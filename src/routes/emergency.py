"""
مسارات API لنظام الطوارئ الطبية.

GET    /api/emergency/qr                  — QR بيانات طوارئ المريض
GET    /api/emergency/patient-card/<tok>  — صفحة عامة لبطاقة الطوارئ
POST   /api/emergency/sos                 — تفعيل SOS
POST   /api/emergency/ambulance           — طلب إسعاف
GET    /api/emergency/alerts              — سجل التنبيهات
PUT    /api/emergency/alerts/<id>/resolve — إغلاق تنبيه
GET    /api/emergency/family-contacts     — قائمة جهات العائلة
POST   /api/emergency/family-contacts     — إضافة جهة عائلة
DELETE /api/emergency/family-contacts/<id>— حذف جهة عائلة
POST   /api/emergency/notify-family/<id>  — إشعار العائلة لتنبيه معين
"""
import io, base64, json, os
from datetime import datetime

import qrcode
from flask import Blueprint, request, jsonify

from src.models.user       import db, User
from src.models.patient    import Patient, Allergy
from src.models.medication import Medication
from src.models.notification import Notification
from src.models.emergency  import EmergencyAlert, FamilyContact
from src.routes.auth       import token_required

emergency_bp = Blueprint('emergency', __name__)


# ─────────────────────────────────────────────────────────
# مساعدات داخلية
# ─────────────────────────────────────────────────────────

def _make_notification(user_id, title, message, ref_type, ref_id):
    n = Notification(user_id=user_id, title=title, message=message,
                     type=ref_type, reference_id=ref_id, reference_type=ref_type)
    db.session.add(n)


def _patient_emergency_info(patient: Patient) -> dict:
    """بناء قاموس المعلومات الطارئة للمريض."""
    allergies = [a.allergen for a in Allergy.query.filter_by(patient_id=patient.id).all()]
    meds = [m.name for m in
            Medication.query.filter_by(patient_id=patient.id, is_active=True).all()]
    return {
        'name':        f"{patient.first_name} {patient.last_name}",
        'blood_type':  patient.blood_type or '—',
        'dob':         patient.date_of_birth.isoformat() if patient.date_of_birth else '—',
        'phone':       patient.phone,
        'allergies':   allergies[:5],
        'medications': meds[:5],
        'ec_name':     patient.emergency_contact_name  or '—',
        'ec_phone':    patient.emergency_contact_phone or '—',
        'national_id': patient.national_id,
    }


def _qr_base64(data: str) -> str:
    """توليد QR وإعادته كـ base64 PNG."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#c0392b", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode()


# ─────────────────────────────────────────────────────────
# QR — بطاقة الطوارئ
# ─────────────────────────────────────────────────────────

@emergency_bp.route('/emergency/qr', methods=['GET'])
@token_required
def get_emergency_qr(current_user):
    """يُولّد QR يحتوي بيانات الطوارئ الأساسية للمريض."""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404

    info = _patient_emergency_info(patient)

    # النص المشفّر في QR — ملخص نصي يمكن قراءته بأي هاتف
    qr_text = (
        f"🆘 بطاقة طوارئ طبية\n"
        f"الاسم: {info['name']}\n"
        f"فصيلة الدم: {info['blood_type']}\n"
        f"تاريخ الميلاد: {info['dob']}\n"
        f"الهاتف: {info['phone']}\n"
        f"الحساسية: {', '.join(info['allergies']) if info['allergies'] else 'لا يوجد'}\n"
        f"الأدوية: {', '.join(info['medications']) if info['medications'] else 'لا يوجد'}\n"
        f"اتصال الطوارئ: {info['ec_name']} — {info['ec_phone']}"
    )

    return jsonify({
        'qr_base64': _qr_base64(qr_text),
        'card':      info,
    }), 200


# ─────────────────────────────────────────────────────────
# SOS
# ─────────────────────────────────────────────────────────

@emergency_bp.route('/emergency/sos', methods=['POST'])
@token_required
def trigger_sos(current_user):
    """تفعيل SOS — يحفظ التنبيه ويُشعر جهات الاتصال الأسرية."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'message': 'بيانات SOS يجب أن تكون JSON صحيحة'}), 400
    patient = Patient.query.filter_by(user_id=current_user.id).first()

    alert = EmergencyAlert(
        user_id       = current_user.id,
        patient_id    = patient.id if patient else None,
        alert_type    = 'sos',
        latitude      = data.get('latitude'),
        longitude     = data.get('longitude'),
        location_text = data.get('location_text', ''),
        emergency_type= data.get('emergency_type', 'SOS'),
        severity      = data.get('severity', 'critical'),
        description   = data.get('description', 'طلب مساعدة طارئة'),
        caller_name   = data.get('caller_name', current_user.email),
        caller_phone  = data.get('caller_phone', ''),
        status        = 'active',
    )
    db.session.add(alert)
    db.session.flush()   # نحتاج alert.id للإشعارات

    # إشعار جهات الاتصال الأسرية بإشعار داخلي
    contacts  = FamilyContact.query.filter_by(user_id=current_user.id).all()
    loc_label = alert.location_text or (
        f"{alert.latitude:.5f}, {alert.longitude:.5f}"
        if alert.latitude else 'غير محدد'
    )
    patient_name = f"{patient.first_name} {patient.last_name}" if patient else current_user.email

    notified = 0
    for fc in contacts:
        # البحث عن مستخدم بنفس رقم الهاتف
        user_match = User.query.filter_by(phone=fc.phone).first() if hasattr(User, 'phone') else None
        if user_match:
            _make_notification(
                user_match.id,
                f'🆘 SOS من {patient_name}',
                f'تم إرسال نداء استغاثة.\nالموقع: {loc_label}\nالحالة: {alert.emergency_type}',
                'emergency', alert.id,
            )
            notified += 1

    alert.family_notified = notified > 0
    alert.notified_at     = datetime.utcnow() if notified > 0 else None
    db.session.commit()

    return jsonify({
        'message':      'تم إرسال SOS بنجاح',
        'alert':        alert.to_dict(),
        'notified':     notified,
        'contacts_count': len(contacts),
    }), 201


# ─────────────────────────────────────────────────────────
# طلب إسعاف
# ─────────────────────────────────────────────────────────

@emergency_bp.route('/emergency/ambulance', methods=['POST'])
@token_required
def request_ambulance(current_user):
    """تسجيل طلب إسعاف."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'message': 'بيانات طلب الإسعاف يجب أن تكون JSON صحيحة'}), 400
    patient = Patient.query.filter_by(user_id=current_user.id).first()

    if not data.get('location_text') and not (data.get('latitude') and data.get('longitude')):
        return jsonify({'message': 'الموقع مطلوب'}), 400

    alert = EmergencyAlert(
        user_id        = current_user.id,
        patient_id     = patient.id if patient else None,
        alert_type     = 'ambulance_request',
        latitude       = data.get('latitude'),
        longitude      = data.get('longitude'),
        location_text  = data.get('location_text', ''),
        emergency_type = data.get('emergency_type', 'غير محدد'),
        severity       = data.get('severity', 'urgent'),
        description    = data.get('description', ''),
        caller_name    = data.get('caller_name', ''),
        caller_phone   = data.get('caller_phone', ''),
        status         = 'active',
    )
    db.session.add(alert)
    db.session.commit()

    return jsonify({
        'message': 'تم إرسال طلب الإسعاف',
        'alert':   alert.to_dict(),
        'ref_number': f"EMG-{alert.id:05d}",
    }), 201


# ─────────────────────────────────────────────────────────
# سجل التنبيهات
# ─────────────────────────────────────────────────────────

@emergency_bp.route('/emergency/alerts', methods=['GET'])
@token_required
def list_alerts(current_user):
    alerts = EmergencyAlert.query.filter_by(user_id=current_user.id)\
                                 .order_by(EmergencyAlert.created_at.desc()).limit(20).all()
    return jsonify([a.to_dict() for a in alerts]), 200


@emergency_bp.route('/emergency/alerts/<int:alert_id>/resolve', methods=['PUT'])
@token_required
def resolve_alert(current_user, alert_id):
    alert = EmergencyAlert.query.filter_by(id=alert_id, user_id=current_user.id).first_or_404()
    alert.status = 'resolved'
    db.session.commit()
    return jsonify(alert.to_dict()), 200


@emergency_bp.route('/emergency/alerts/<int:alert_id>', methods=['PUT'])
@token_required
def update_alert(current_user, alert_id):
    """تحديث ملاحظات وموقع وبيانات تنبيه الطوارئ قبل إغلاقه."""
    alert = EmergencyAlert.query.filter_by(
        id=alert_id, user_id=current_user.id
    ).first()
    if not alert:
        return jsonify({'message': 'التنبيه غير موجود'}), 404
    if alert.status == 'resolved':
        return jsonify({'message': 'لا يمكن تعديل تنبيه مغلق'}), 400

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'message': 'بيانات التنبيه يجب أن تكون JSON صحيحة'}), 400
    for field in (
        'emergency_type', 'severity', 'description', 'location_text',
        'caller_name', 'caller_phone',
    ):
        if field in data:
            setattr(alert, field, data[field])
    for field in ('latitude', 'longitude'):
        if field in data:
            try:
                setattr(
                    alert,
                    field,
                    float(data[field]) if data[field] not in (None, '') else None,
                )
            except (TypeError, ValueError):
                return jsonify({'message': 'إحداثيات الموقع غير صالحة'}), 400
    db.session.commit()
    return jsonify({'message': 'تم تحديث بيانات الطوارئ', 'alert': alert.to_dict()}), 200


# ─────────────────────────────────────────────────────────
# جهات الاتصال الأسرية
# ─────────────────────────────────────────────────────────

@emergency_bp.route('/emergency/family-contacts', methods=['GET'])
@token_required
def list_family_contacts(current_user):
    contacts = FamilyContact.query.filter_by(user_id=current_user.id).all()
    return jsonify([c.to_dict() for c in contacts]), 200


@emergency_bp.route('/emergency/family-contacts', methods=['POST'])
@token_required
def add_family_contact(current_user):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'message': 'بيانات جهة الاتصال يجب أن تكون JSON صحيحة'}), 400
    if not isinstance(data.get('name'), str) or not isinstance(data.get('phone'), str) or not data.get('name').strip() or not data.get('phone').strip():
        return jsonify({'message': 'الاسم والهاتف مطلوبان'}), 400

    # حد أقصى 5 جهات
    if FamilyContact.query.filter_by(user_id=current_user.id).count() >= 5:
        return jsonify({'message': 'الحد الأقصى 5 جهات أسرية'}), 400

    # إذا طلب الجعلها أساسية، احذف التأشير من الأخريات
    if data.get('is_primary'):
        FamilyContact.query.filter_by(user_id=current_user.id, is_primary=True)\
                           .update({'is_primary': False})

    contact = FamilyContact(
        user_id      = current_user.id,
        name         = data['name'],
        phone        = data['phone'],
        relationship = data.get('relationship', ''),
        is_primary   = bool(data.get('is_primary', False)),
    )
    db.session.add(contact)
    db.session.commit()
    return jsonify(contact.to_dict()), 201


@emergency_bp.route('/emergency/family-contacts/<int:contact_id>', methods=['DELETE'])
@token_required
def delete_family_contact(current_user, contact_id):
    contact = FamilyContact.query.filter_by(id=contact_id, user_id=current_user.id).first_or_404()
    db.session.delete(contact)
    db.session.commit()
    return jsonify({'message': 'تم الحذف'}), 200


@emergency_bp.route('/emergency/notify-family/<int:alert_id>', methods=['POST'])
@token_required
def notify_family(current_user, alert_id):
    """إرسال إشعار داخلي لجهات العائلة المسجلة بالتطبيق."""
    alert   = EmergencyAlert.query.filter_by(id=alert_id, user_id=current_user.id).first_or_404()
    patient = Patient.query.filter_by(user_id=current_user.id).first()

    contacts  = FamilyContact.query.filter_by(user_id=current_user.id).all()
    if not contacts:
        return jsonify({'message': 'لا توجد جهات عائلة مضافة'}), 400

    loc_label    = alert.location_text or (
        f"{alert.latitude:.5f}, {alert.longitude:.5f}" if alert.latitude else 'غير محدد'
    )
    patient_name = f"{patient.first_name} {patient.last_name}" if patient else current_user.email
    notified = 0

    for fc in contacts:
        user_match = User.query.filter(User.email == fc.phone).first()  # fallback email match
        if not user_match:
            user_match = User.query.filter(getattr(User, 'phone', None) == fc.phone).first() \
                         if hasattr(User, 'phone') else None
        if user_match:
            _make_notification(
                user_match.id,
                f'🆘 طوارئ: {patient_name}',
                f'تنبيه طوارئ صادر.\nالنوع: {alert.emergency_type}\nالموقع: {loc_label}',
                'emergency', alert.id,
            )
            notified += 1

    alert.family_notified = True
    alert.notified_at     = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message':  f'تم إرسال الإشعار لـ {notified} من {len(contacts)} جهة',
        'notified': notified,
        'total':    len(contacts),
        'note':     'يُرسَل الإشعار فقط لجهات مسجلة في التطبيق بنفس رقم الهاتف',
    }), 200
