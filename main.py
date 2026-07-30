import os
import sys

# Add project root to path so 'src.*' imports resolve correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.user import db, User
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.models.patient import Patient, MedicalRecord, Allergy
from src.models.doctor import Doctor, DoctorAvailability, Specialization
from src.models.appointment import Appointment, AppointmentHistory, AppointmentRating
from src.models.medication import Medication, MedicationSchedule, MedicationLog, DrugDatabase
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
from src.routes.feedback import feedback_bp, Feedback
from werkzeug.security import generate_password_hash

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'))

# Security — use environment secret if available
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET')
if not app.config['SECRET_KEY']:
    raise RuntimeError('SESSION_SECRET must be configured before starting the API')
app.config['JWT_SECRET'] = os.environ.get('JWT_SECRET', app.config['SECRET_KEY'])

# CORS — allow Vite dev server to call the API
CORS(app, origins=['http://localhost:5000', 'http://localhost:5173', 'https://*.replit.dev', 'https://*.repl.co'],
     supports_credentials=True)

# Blueprints
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

# Database
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'database', 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    f'sqlite:///{db_path}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

    # ── ترحيل الأعمدة الجديدة (آمن على قواعد البيانات الموجودة) ──
    from sqlalchemy import text
    migrations = [
        "ALTER TABLE diseases ADD COLUMN IF NOT EXISTS attachment_data TEXT",
        "ALTER TABLE vaccinations ADD COLUMN IF NOT EXISTS attachment_data TEXT",
        "ALTER TABLE lab_tests ADD COLUMN IF NOT EXISTS attachment_data TEXT",
        "ALTER TABLE radiology_scans ADD COLUMN IF NOT EXISTS attachment_data TEXT",
        "ALTER TABLE radiology_scans ADD COLUMN IF NOT EXISTS report_data TEXT",
        "ALTER TABLE medications ADD COLUMN IF NOT EXISTS attachment_data TEXT",
    ]
    with db.engine.connect() as conn:
        for stmt in migrations:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception:
                conn.rollback()  # reset transaction state on any failure

    # Bootstrap the first system administrator only when explicitly configured.
    # This keeps admin creation out of the public registration flow.
    bootstrap_email = os.environ.get('ADMIN_EMAIL')
    bootstrap_password = os.environ.get('ADMIN_PASSWORD')
    if bootstrap_email and bootstrap_password:
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
            # Always sync the password from the env secret so a changed ADMIN_PASSWORD takes effect.
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

# Serve React build (production)
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
                'endpoints': {
                    'auth': '/api/auth/',
                    'users': '/api/users',
                    'health': '/api/health'
                }
            }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
