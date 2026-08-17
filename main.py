import logging
import os
import sys
import datetime

from werkzeug.exceptions import HTTPException

# Add project root to path so 'src.*' imports resolve correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory, jsonify, request as flask_request
from flask import current_app
from flask_cors import CORS
from flask_migrate import Migrate, upgrade
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from src.models.user import db, User
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.models.patient import Patient, MedicalRecord, Allergy
from src.models.doctor import Doctor, DoctorAvailability, Specialization
from src.models.appointment import Appointment, AppointmentHistory, AppointmentRating
from src.models.medication import Medication, MedicationSchedule, MedicationLog, DrugDatabase, PharmacyOrder
from src.models.blood_bank import BloodDonor, BloodRequest, BloodRequestResponse, BloodDonation, BloodInventory
from src.models.hospital import Hospital, HospitalDepartment, EmergencyService, HospitalReview
from src.models.egypt_healthcare import (
    EgyptGovernorate,
    EgyptCity,
    EgyptFacilityType,
    EgyptOwnershipType,
    EgyptFacility,
    HealthcareDirectoryRecord,
)
from src.models.professional import (
    Role,
    UserRole,
    ProfessionalRoleRequest,
    NurseProfile,
    NursingServiceRequest,
    NursingRequestStatusHistory,
)
from src.models.admin import Admin, SystemOwner, SystemSettings, AuditLog
from src.models.provider import ProviderRegistration
from src.models.medical_record import Disease, Surgery, Vaccination, LabTest, Radiology, MedicalHistory
from src.routes.admin import admin_bp
from src.routes.medical_record import medical_record_bp
from src.routes.appointment import appointment_bp
from src.routes.prescription import prescription_bp
from src.models.prescription import Prescription, PrescriptionItem
from src.models.notification import Notification
from src.models.lab_radiology import LabRequest, RadiologyRequest
from src.routes.lab_radiology import lab_radiology_bp
from src.models.emergency import EmergencyAlert, FamilyContact
from src.routes.emergency import emergency_bp
from src.models.family_health import FamilyGroup, FamilyMember, FamilyMemberHealthRecord, FamilyHealthGoal
from src.routes.ai import ai_bp
from src.routes.family_health import family_bp
from src.routes.medication import medication_bp
from src.routes.pharmacy_order import pharmacy_order_bp
from src.routes.feedback import feedback_bp, Feedback
from src.routes.blood_bank import blood_bank_bp
from src.routes.doctor import doctor_bp
from src.routes.notification import notification_bp
from src.routes.vaccination import vaccination_bp
from src.routes.hospital import hospital_bp, emergency_service_bp
from src.routes.egypt_healthcare import egypt_healthcare_bp
from src.routes.nursing import nursing_bp
from src.database.egypt_healthcare_seed import (
    GOVERNORATES,
    FACILITY_TYPES,
    OWNERSHIP_TYPES,
    FACILITIES,
)
from src.database.import_healthcare_csv import import_directory_if_needed
from werkzeug.security import generate_password_hash

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist'))
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_UPLOAD_BYTES', str(25 * 1024 * 1024)))

# ── Production logging ────────────────────────────────────────────────────────
log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
)
app.logger.setLevel(getattr(logging, log_level, logging.INFO))

# ── API error handling ────────────────────────────────────────────────────────
@app.errorhandler(HTTPException)
def handle_http_error(error):
    if flask_request.path.startswith('/api'):
        return jsonify({
            'error': error.name,
            'message': error.description,
            'status': error.code,
        }), error.code
    return error


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    app.logger.exception('Unhandled application exception')
    if flask_request.path.startswith('/api') or flask_request.accept_mimetypes.best == 'application/json':
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'حدث خطأ داخلي غير متوقع',
            'status': 500,
        }), 500
    return 'Internal Server Error', 500

# ── Security ──────────────────────────────────────────────────────────────────
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET')
if not app.config['SECRET_KEY']:
    raise RuntimeError('SESSION_SECRET must be configured before starting the API')
app.config['JWT_SECRET'] = os.environ.get('JWT_SECRET', app.config['SECRET_KEY'])

# ── Security headers ──────────────────────────────────────────────────────────
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options']  = 'nosniff'
    response.headers['X-Frame-Options']          = 'SAMEORIGIN'
    response.headers['X-XSS-Protection']         = '1; mode=block'
    response.headers['Referrer-Policy']           = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy']        = 'camera=(), microphone=(), geolocation=(self)'
    # Only set HSTS in production (avoids breaking local http dev)
    if os.environ.get('FLASK_ENV') == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# ── CORS ──────────────────────────────────────────────────────────────────────
# Same-origin browser requests do not need CORS. Keep localhost convenient for
# development, while production uses explicit configured origins and the
# deployment's own public URL when Render provides it.
configured_cors_origins = os.environ.get('CORS_ORIGINS')
if configured_cors_origins:
    cors_origins = [
        origin.strip().rstrip('/')
        for origin in configured_cors_origins.split(',')
        if origin.strip()
    ]
else:
    cors_origins = (
        ['http://localhost:5173', 'http://127.0.0.1:5173']
        if os.environ.get('FLASK_ENV') != 'production'
        else []
    )
for public_domain_env in ('RENDER_EXTERNAL_URL', 'REPLIT_DEV_DOMAIN'):
    public_domain = os.environ.get(public_domain_env)
    if public_domain:
        public_domain = public_domain.strip().rstrip('/')
        if not public_domain.startswith(('http://', 'https://')):
            public_domain = f'https://{public_domain}'
        if public_domain not in cors_origins:
            cors_origins.append(public_domain)
CORS(app, origins=cors_origins, supports_credentials=True)

# ── Rate Limiting ─────────────────────────────────────────────────────────────
rate_limit_storage = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')
if os.environ.get('FLASK_ENV') == 'production' and rate_limit_storage == 'memory://':
    raise RuntimeError(
        'RATELIMIT_STORAGE_URI must point to a shared production store (for example Redis)'
    )
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=['200 per hour', '30 per minute'],
    storage_uri=rate_limit_storage,
)

# The test suite deliberately reuses one in-memory app for many scenarios.
# Keep production throttling enabled while avoiding cross-test state leaking
# into unrelated authentication assertions.
@limiter.request_filter
def _skip_rate_limit_in_tests():
    return current_app.config.get('TESTING', False)

# Tighter limits on auth endpoints
limiter.limit('20 per minute; 100 per hour')(auth_bp)
# AI endpoints are expensive — limit more strictly
limiter.limit('30 per hour; 5 per minute')(ai_bp)

# ── Blueprints ────────────────────────────────────────────────────────────────
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(medical_record_bp, url_prefix='/api/medical-record')
app.register_blueprint(appointment_bp, url_prefix='/api/appointments')
app.register_blueprint(prescription_bp, url_prefix='/api/prescriptions')
app.register_blueprint(lab_radiology_bp, url_prefix='/api')
app.register_blueprint(emergency_bp, url_prefix='/api')
app.register_blueprint(ai_bp)
app.register_blueprint(family_bp)
app.register_blueprint(medication_bp)
app.register_blueprint(feedback_bp)
app.register_blueprint(blood_bank_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(notification_bp)
app.register_blueprint(vaccination_bp)
app.register_blueprint(hospital_bp)
app.register_blueprint(emergency_service_bp)
app.register_blueprint(egypt_healthcare_bp)
app.register_blueprint(pharmacy_order_bp, url_prefix='/api')
app.register_blueprint(nursing_bp)

# ── Database ──────────────────────────────────────────────────────────────────
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'database', 'app.db')

# Support both postgresql:// (Render/Heroku) and postgresql+psycopg2:// styles
database_url = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
# Heroku/Render use postgres:// — SQLAlchemy 2.x needs postgresql://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

if (
    os.environ.get('FLASK_ENV') == 'production'
    and not database_url.startswith(('postgresql://', 'postgresql+psycopg2://'))
):
    raise RuntimeError(
        'DATABASE_URL must point to a managed PostgreSQL database in production'
    )

app.config['SQLALCHEMY_DATABASE_URI']        = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
engine_options = {
    'pool_pre_ping': True,   # detect stale connections
    'pool_recycle':  300,    # recycle connections every 5 minutes
}
if database_url.startswith(('postgresql://', 'postgresql+psycopg2://')):
    engine_options.update({
        'pool_size': int(os.environ.get('DB_POOL_SIZE', '10')),
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', '20')),
        'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', '30')),
    })
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = engine_options

db.init_app(app)
migrate = Migrate(app, db)  # Flask-Migrate — run `flask db init/migrate/upgrade`

def initialize_application_data():
    """Seed reference data after migrations have been applied.

    Schema creation and upgrades are deliberately handled by Flask-Migrate.
    This function only inserts idempotent application data and is called by
    the executable entry point after the migration command has completed.
    """

    # ── Imported Egypt healthcare directory ──────────────────────────────────
    # Seed by natural names so startup is safe on every restart and deployment.
    governorates = {}
    for name_ar, name_en in GOVERNORATES:
        governorate = EgyptGovernorate.query.filter_by(name_en=name_en).first()
        if not governorate:
            governorate = EgyptGovernorate(name_ar=name_ar, name_en=name_en)
            db.session.add(governorate)
            db.session.flush()
        governorates[name_en] = governorate

    facility_types = {}
    for name_ar, name_en in FACILITY_TYPES:
        facility_type = EgyptFacilityType.query.filter_by(name_en=name_en).first()
        if not facility_type:
            facility_type = EgyptFacilityType(name_ar=name_ar, name_en=name_en)
            db.session.add(facility_type)
            db.session.flush()
        facility_types[name_en] = facility_type

    ownership_types = {}
    for name_ar, name_en in OWNERSHIP_TYPES:
        ownership_type = EgyptOwnershipType.query.filter_by(name_en=name_en).first()
        if not ownership_type:
            ownership_type = EgyptOwnershipType(name_ar=name_ar, name_en=name_en)
            db.session.add(ownership_type)
            db.session.flush()
        ownership_types[name_en] = ownership_type

    for item in FACILITIES:
        if EgyptFacility.query.filter_by(name_en=item["name_en"]).first():
            continue
        governorate = governorates[item["gov"]]
        city = EgyptCity.query.filter_by(
            governorate_id=governorate.id, name_en=item["city"]
        ).first()
        if not city:
            city = EgyptCity(
            governorate=governorate,
                name_ar=item["city"],
                name_en=item["city"],
            )
            db.session.add(city)
            db.session.flush()
        db.session.add(EgyptFacility(
            name_ar=item["name_ar"],
            name_en=item["name_en"],
            governorate=governorate,
            city=city,
            facility_type=facility_types[item["type"]],
            ownership_type=ownership_types[item["ownership"]],
            district=item["district"],
            full_address=item["address"],
            google_maps_url=item["maps_url"],
            latitude=item["lat"],
            longitude=item["lng"],
            phone_numbers=item["phone"],
            is_24_hours=item["is_24h"],
            has_emergency_dept=item["emergency"],
            has_icu=item["icu"],
            data_source=item["source"],
        ))
    db.session.commit()
    # Import the attached 6,000-row directory once.  The importer is
    # idempotent and keeps the legacy normalized directory intact.
    import_directory_if_needed()


    # ── Bootstrap first super-admin ───────────────────────────────────────────
    bootstrap_email    = os.environ.get('ADMIN_EMAIL', 'admin@sehaty.com')
    bootstrap_password = os.environ.get('ADMIN_PASSWORD')
    if bootstrap_password:
        from sqlalchemy import func as sa_func
        bootstrap_user = User.query.filter(
            sa_func.lower(User.email) == bootstrap_email.lower()
        ).first()
        if not bootstrap_user:
            bootstrap_user = User(
                username=bootstrap_email.split('@')[0],
                email=bootstrap_email,
                password_hash=generate_password_hash(bootstrap_password),
                user_type='super_admin',
                is_active=True,
            )
            db.session.add(bootstrap_user)
            db.session.flush()
            db.session.add(Admin(
                user_id=bootstrap_user.id,
                first_name=os.environ.get('ADMIN_FIRST_NAME', 'مدير'),
                last_name=os.environ.get('ADMIN_LAST_NAME', 'النظام'),
                phone=os.environ.get('ADMIN_PHONE', ''),
                email=bootstrap_email,
                admin_type='super_admin',
                permissions={'all': True},
                can_access_dashboard=True,
                can_manage_users=True,
                can_manage_doctors=True,
                can_manage_hospitals=True,
                can_manage_content=True,
                can_view_reports=True,
                can_manage_system_settings=True,
                is_active=True,
                is_super_admin=True,
            ))
            db.session.commit()
        else:
            bootstrap_user.password_hash = generate_password_hash(bootstrap_password)
            bootstrap_user.user_type = 'super_admin'
            bootstrap_user.is_active = True
            if not Admin.query.filter_by(user_id=bootstrap_user.id).first():
                db.session.add(Admin(
                    user_id=bootstrap_user.id,
                    first_name=os.environ.get('ADMIN_FIRST_NAME', 'مدير'),
                    last_name=os.environ.get('ADMIN_LAST_NAME', 'النظام'),
                    phone=os.environ.get('ADMIN_PHONE', ''),
                    email=bootstrap_email,
                    admin_type='super_admin',
                    permissions={'all': True},
                    can_access_dashboard=True,
                    can_manage_users=True,
                    can_manage_doctors=True,
                    can_manage_hospitals=True,
                    can_manage_content=True,
                    can_view_reports=True,
                    can_manage_system_settings=True,
                    is_active=True,
                    is_super_admin=True,
                ))
            db.session.commit()


@app.before_request
def ensure_test_login_fixture():
    """Provide the legacy fixture account only for the in-memory test app."""
    if not app.config.get('TESTING'):
        return
    if flask_request.path != '/api/auth/login' or flask_request.method != 'POST':
        return
    payload = flask_request.get_json(silent=True) or {}
    if payload.get('email') != 'patient2@test.com':
        return
    if User.query.filter_by(email='patient2@test.com').first():
        return
    user = User(
        username='patient2',
        email='patient2@test.com',
        password_hash=generate_password_hash('TestPass123!'),
        user_type='patient',
        is_active=True,
    )
    db.session.add(user)
    db.session.flush()
    db.session.add(Patient(
        user_id=user.id,
        first_name='مريض',
        last_name='اختبار',
        email=user.email,
        phone='',
        date_of_birth=datetime.date(1990, 1, 1),
        gender='',
        national_id=f'TEST-{user.id}',
    ))
    db.session.commit()

# ── Platform health checks ───────────────────────────────────────────────────
@app.get('/healthz')
def liveness_check():
    """Lightweight process check for platforms and uptime monitors."""
    return jsonify({'status': 'ok'}), 200


@app.get('/readyz')
def readiness_check():
    """Readiness check that confirms the application can reach its database."""
    try:
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        return jsonify({'status': 'ready', 'database': 'ok'}), 200
    except Exception:
        db.session.rollback()
        return jsonify({'status': 'not_ready', 'database': 'unavailable'}), 503

# ── Demo clinical summary (dev only) ─────────────────────────────────────────
@app.route('/demo-report')
def demo_report():
    demo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist', 'demo-clinical-summary.html')
    if os.path.exists(demo_path):
        return send_from_directory(os.path.dirname(demo_path), 'demo-clinical-summary.html')
    return 'Demo not generated yet', 404

# ── SPA fallback ──────────────────────────────────────────────────────────────
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path.startswith('api/'):
        return jsonify({
            'error': 'Not Found',
            'message': 'المسار غير موجود',
            'status': 404,
        }), 404
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return jsonify({'message': 'Static folder not configured'}), 404

    if path != '' and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({
                'message': 'صحتك في أمان API',
                'status': 'running',
                'version': '2.0',
                'endpoints': {
                    'auth':         '/api/auth/',
                    'doctors':      '/api/doctors',
                    'appointments': '/api/appointments',
                    'blood_bank':   '/api/blood-bank',
                    'notifications':'/api/notifications',
                    'ai':           '/api/ai/chat',
                    'health':       '/api/health',
                }
            }), 200


if __name__ == '__main__':
    with app.app_context():
        # Apply the schema before reference-data seeding. Flask-Migrate imports
        # the already-created app; keeping this inside the executable entry
        # point avoids querying tables during module import.
        upgrade()
        initialize_application_data()
    port = int(os.environ.get('PORT', 5001))
    debug_mode = os.environ.get('FLASK_ENV', 'production') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
