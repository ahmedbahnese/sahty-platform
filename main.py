import os
import sys

# Add project root to path so 'src.*' imports resolve correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory, jsonify, request as flask_request
from flask_cors import CORS
from flask_migrate import Migrate
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
from werkzeug.security import generate_password_hash

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'))

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
    response.headers['Permissions-Policy']        = 'camera=(), microphone=(), geolocation=()'
    # Only set HSTS in production (avoids breaking local http dev)
    if os.environ.get('FLASK_ENV') == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS(app,
     origins=['http://localhost:5000', 'http://localhost:5173',
               'https://*.replit.dev', 'https://*.repl.co'],
     supports_credentials=True)

# ── Rate Limiting ─────────────────────────────────────────────────────────────
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=['200 per hour', '30 per minute'],
    storage_uri='memory://',
)
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
app.register_blueprint(pharmacy_order_bp, url_prefix='/api')

# ── Database ──────────────────────────────────────────────────────────────────
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'database', 'app.db')

# Support both postgresql:// (Render/Heroku) and postgresql+psycopg2:// styles
database_url = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
# Heroku/Render use postgres:// — SQLAlchemy 2.x needs postgresql://
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI']        = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS']      = {
    'pool_pre_ping': True,   # detect stale connections
    'pool_recycle':  300,    # recycle connections every 5 minutes
}

db.init_app(app)
migrate = Migrate(app, db)  # Flask-Migrate — run `flask db init/migrate/upgrade`

with app.app_context():
    db.create_all()

    # ── Safe column migrations (won't fail on existing dbs) ──────────────────
    from sqlalchemy import text
    migrations = [
        # Existing safe migrations
        "ALTER TABLE diseases ADD COLUMN IF NOT EXISTS attachment_data TEXT",
        "ALTER TABLE vaccinations ADD COLUMN IF NOT EXISTS attachment_data TEXT",
        "ALTER TABLE lab_tests ADD COLUMN IF NOT EXISTS attachment_data TEXT",
        "ALTER TABLE radiology_scans ADD COLUMN IF NOT EXISTS attachment_data TEXT",
        "ALTER TABLE radiology_scans ADD COLUMN IF NOT EXISTS report_data TEXT",
        "ALTER TABLE medications ADD COLUMN IF NOT EXISTS attachment_data TEXT",

        # Sprint X — Lab Requests: multiple tests, center, home collection, scheduling, doc upload
        "ALTER TABLE lab_requests ADD COLUMN IF NOT EXISTS tests_json TEXT DEFAULT '[]'",
        "ALTER TABLE lab_requests ADD COLUMN IF NOT EXISTS lab_center_name VARCHAR(200)",
        "ALTER TABLE lab_requests ADD COLUMN IF NOT EXISTS preparation_instructions TEXT",
        "ALTER TABLE lab_requests ADD COLUMN IF NOT EXISTS request_doc_path VARCHAR(500)",
        "ALTER TABLE lab_requests ADD COLUMN IF NOT EXISTS request_doc_name VARCHAR(200)",
        "ALTER TABLE lab_requests ADD COLUMN IF NOT EXISTS scheduled_datetime DATETIME",
        "ALTER TABLE lab_requests ADD COLUMN IF NOT EXISTS home_collection BOOLEAN DEFAULT 0",
        "ALTER TABLE lab_requests ADD COLUMN IF NOT EXISTS collection_address TEXT",
        "ALTER TABLE lab_requests ADD COLUMN IF NOT EXISTS collection_lat REAL",
        "ALTER TABLE lab_requests ADD COLUMN IF NOT EXISTS collection_lng REAL",
        "ALTER TABLE lab_requests ADD COLUMN IF NOT EXISTS collection_date DATE",
        "ALTER TABLE lab_requests ADD COLUMN IF NOT EXISTS collection_time VARCHAR(10)",
        "ALTER TABLE lab_requests ADD COLUMN IF NOT EXISTS collection_staff_name VARCHAR(200)",

        # Sprint X — Radiology Requests: center, scheduling, doc upload
        "ALTER TABLE radiology_requests ADD COLUMN IF NOT EXISTS radiology_center_name VARCHAR(200)",
        "ALTER TABLE radiology_requests ADD COLUMN IF NOT EXISTS request_doc_path VARCHAR(500)",
        "ALTER TABLE radiology_requests ADD COLUMN IF NOT EXISTS request_doc_name VARCHAR(200)",
        "ALTER TABLE radiology_requests ADD COLUMN IF NOT EXISTS scheduled_datetime DATETIME",

        # Sprint X — Medications: prescription source, notification settings
        "ALTER TABLE medications ADD COLUMN IF NOT EXISTS prescription_id INTEGER REFERENCES prescriptions(id)",
        "ALTER TABLE medications ADD COLUMN IF NOT EXISTS source VARCHAR(30) DEFAULT 'manual'",
        "ALTER TABLE medications ADD COLUMN IF NOT EXISTS notify_family BOOLEAN DEFAULT 0",
        "ALTER TABLE medications ADD COLUMN IF NOT EXISTS notify_doctor_on_missed BOOLEAN DEFAULT 0",
        "ALTER TABLE medications ADD COLUMN IF NOT EXISTS missed_dose_threshold INTEGER DEFAULT 3",

        # Sprint 5-8 — Family member in appointments, vaccination tracking
        "ALTER TABLE appointments ADD COLUMN IF NOT EXISTS for_family_member_id INTEGER REFERENCES family_members(id)",
        "ALTER TABLE appointments ADD COLUMN IF NOT EXISTS for_member_name VARCHAR(200)",
    ]
    with db.engine.connect() as conn:
        for stmt in migrations:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception:
                conn.rollback()

    # ── Bootstrap first super-admin ───────────────────────────────────────────
    bootstrap_email    = os.environ.get('ADMIN_EMAIL', 'admin@sehaty.com')
    bootstrap_password = os.environ.get('ADMIN_PASSWORD')
    if bootstrap_password:
        bootstrap_user = User.query.filter_by(email=bootstrap_email).first()
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

# ── SPA fallback ──────────────────────────────────────────────────────────────
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
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
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
