import os
import sys

# Add project root to path so 'src.*' imports resolve correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.models.patient import Patient, MedicalRecord, Allergy
from src.models.doctor import Doctor, DoctorAvailability, Specialization
from src.models.appointment import Appointment, AppointmentHistory, AppointmentRating
from src.models.medication import Medication, MedicationSchedule, MedicationLog, DrugDatabase
from src.models.blood_bank import BloodDonor, BloodRequest, BloodRequestResponse, BloodDonation, BloodInventory
from src.models.hospital import Hospital, HospitalDepartment, EmergencyService, HospitalReview
from src.models.admin import Admin, SystemOwner, SystemSettings, AuditLog

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'))

# Security — use environment secret if available
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'sahty-dev-secret-2024')

# CORS — allow Vite dev server to call the API
CORS(app, origins=['http://localhost:5000', 'http://localhost:5173', 'https://*.replit.dev', 'https://*.repl.co'],
     supports_credentials=True)

# Blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Database
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'database', 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

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
