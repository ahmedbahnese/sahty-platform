import os
import sys
# DON\'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
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

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """
    دالة لتقديم الملفات الثابتة (الواجهة الأمامية).

    تخدم ملفات الواجهة الأمامية (React build) من مجلد 'static'.
    إذا كان المسار غير موجود، تعيد توجيه الطلب إلى index.html.

    Args:
        path (str): المسار المطلوب للملف.

    Returns:
        Response: الملف المطلوب أو index.html أو رسالة خطأ 404.
    """
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    """
    نقطة الدخول الرئيسية لتشغيل تطبيق Flask.

    يقوم بتشغيل الخادم على العنوان 0.0.0.0 والمنفذ 5000 في وضع التصحيح.
    """
    app.run(host='0.0.0.0', port=5000, debug=True)


