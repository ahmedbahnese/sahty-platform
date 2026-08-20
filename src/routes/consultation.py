import os
import uuid
from datetime import datetime

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from src.models.user import db, User
from src.models.consultation import Consultation, ConsultationMessage, ConsultationAttachment
from src.models.notification import Notification
from src.routes.auth import token_required, role_required

consultation_bp = Blueprint("consultation", __name__, url_prefix="/api/consultations")

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "webp", "dcm", "tif", "tiff"}
MAX_ATTACHMENT_BYTES = 25 * 1024 * 1024


def _is_participant(item, user):
    return user.user_type in ("admin", "super_admin") or user.id in (item.patient_id, item.doctor_id)


def _meeting_url(room):
    base = os.environ.get("VIDEO_MEETING_BASE_URL", "https://meet.jit.si").rstrip("/")
    return f"{base}/{room}"


def _notify(user_id, title, message, consultation_id):
    db.session.add(Notification(
        user_id=user_id,
        title=title,
        message=message,
        type="consultation",
        reference_id=consultation_id,
        reference_type="consultation",
    ))


def _save_attachment(file_storage, consultation_id):
    original = secure_filename(file_storage.filename or "")
    if not original or "." not in original:
        return None, "اسم الملف غير صالح"
    extension = original.rsplit(".", 1)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        return None, "نوع الملف غير مدعوم"
    content = file_storage.read()
    if len(content) > MAX_ATTACHMENT_BYTES:
        return None, "حجم الملف يتجاوز 25 ميجابايت"
    folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "static", "uploads", "consultations"))
    os.makedirs(folder, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}.{extension}"
    file_storage.save(os.path.join(folder, stored_name))
    return (stored_name, original, file_storage.mimetype, len(content)), None


@consultation_bp.route("", methods=["GET", "POST"])
@token_required
def consultations(current_user):
    if request.method == "GET":
        rows = Consultation.query.filter(
            (Consultation.patient_id == current_user.id) |
            (Consultation.doctor_id == current_user.id)
        ).order_by(Consultation.created_at.desc()).all()
        if current_user.user_type in ("admin", "super_admin"):
            rows = Consultation.query.order_by(Consultation.created_at.desc()).limit(100).all()
        return jsonify({"consultations": [row.to_dict() for row in rows]})

    data = request.get_json(silent=True) or {}
    doctor_id = data.get("doctor_id")
    if not doctor_id or not data.get("scheduled_at"):
        return jsonify({"message": "الطبيب وموعد الاستشارة مطلوبان"}), 400
    doctor = db.session.get(User, doctor_id)
    if not doctor or doctor.user_type != "doctor" or not doctor.is_active:
        return jsonify({"message": "الطبيب غير متاح"}), 400
    try:
        scheduled_at = datetime.fromisoformat(str(data["scheduled_at"]).replace("Z", "+00:00"))
    except ValueError:
        return jsonify({"message": "موعد الاستشارة غير صالح"}), 400

    room = f"sehaty-consultation-{uuid.uuid4().hex}"
    row = Consultation(
        patient_id=current_user.id,
        doctor_id=doctor.id,
        status="requested",
        scheduled_at=scheduled_at,
        meeting_provider=os.environ.get("VIDEO_MEETING_PROVIDER", "jitsi"),
        meeting_room=room,
        meeting_url=_meeting_url(room),
    )
    db.session.add(row)
    db.session.flush()
    _notify(doctor.id, "طلب استشارة مرئية جديد", "لديك طلب استشارة مرئية جديد من مريض.", row.id)
    db.session.commit()
    return jsonify({"message": "تم إرسال طلب الاستشارة", "consultation": row.to_dict()}), 201


@consultation_bp.route("/<int:consultation_id>", methods=["GET"])
@token_required
def get_consultation(current_user, consultation_id):
    row = db.session.get(Consultation, consultation_id)
    if not row or not _is_participant(row, current_user):
        return jsonify({"message": "الاستشارة غير موجودة أو غير مصرح بها"}), 404
    return jsonify({"consultation": row.to_dict()})


@consultation_bp.route("/<int:consultation_id>/messages", methods=["POST"])
@token_required
def send_message(current_user, consultation_id):
    row = db.session.get(Consultation, consultation_id)
    if not row or not _is_participant(row, current_user):
        return jsonify({"message": "غير مصرح"}), 403
    body = (request.get_json(silent=True) or {}).get("body", "").strip()
    if not body or len(body) > 5000:
        return jsonify({"message": "نص الرسالة مطلوب وبحد أقصى 5000 حرف"}), 400
    message = ConsultationMessage(consultation_id=row.id, sender_user_id=current_user.id, body=body)
    db.session.add(message)
    target_id = row.doctor_id if current_user.id == row.patient_id else row.patient_id
    _notify(target_id, "رسالة جديدة في الاستشارة", "لديك رسالة جديدة من الطرف الآخر.", row.id)
    db.session.commit()
    return jsonify({"message": message.to_dict()}), 201


@consultation_bp.route("/<int:consultation_id>/attachments", methods=["POST"])
@token_required
def upload_attachment(current_user, consultation_id):
    row = db.session.get(Consultation, consultation_id)
    if not row or not _is_participant(row, current_user):
        return jsonify({"message": "غير مصرح"}), 403
    file_storage = request.files.get("file")
    if not file_storage:
        return jsonify({"message": "الملف الطبي مطلوب"}), 400
    saved, error = _save_attachment(file_storage, row.id)
    if error:
        return jsonify({"message": error}), 400
    stored_name, original, mimetype, size = saved
    attachment = ConsultationAttachment(
        consultation_id=row.id,
        uploaded_by_user_id=current_user.id,
        file_path=f"/api/uploads/consultations/{stored_name}",
        file_name=original,
        mime_type=mimetype,
        file_size=size,
        kind=request.form.get("kind", "medical_report"),
    )
    db.session.add(attachment)
    db.session.commit()
    return jsonify({"attachment": attachment.to_dict()}), 201


@consultation_bp.route("/<int:consultation_id>/complete", methods=["POST"])
@token_required
@role_required("doctor")
def complete_consultation(current_user, consultation_id):
    row = db.session.get(Consultation, consultation_id)
    if not row or row.doctor_id != current_user.id:
        return jsonify({"message": "الاستشارة غير موجودة أو غير مسندة إليك"}), 404
    data = request.get_json(silent=True) or {}
    row.status = "completed"
    row.diagnosis = data.get("diagnosis")
    row.treatment_plan = data.get("treatment_plan")
    row.prescription_data = data.get("prescription") or {}
    row.referral_type = data.get("referral_type")
    row.referral_note = data.get("referral_note")
    row.emergency_requested = bool(data.get("emergency_requested", False))
    _notify(row.patient_id, "اكتملت الاستشارة الطبية", "تمت إضافة التشخيص وخطة العلاج إلى الاستشارة.", row.id)
    db.session.commit()
    return jsonify({"consultation": row.to_dict()}), 200
