"""
مسارات API للوصفات الطبية.
يشمل: الإنشاء، الإرسال للصيدلية، تأكيد الصرف، التاريخ.
"""
from flask import Blueprint, request, jsonify, g
from datetime import datetime, date, timedelta
from src.models.user import db, User
from src.models.patient import Patient
from src.models.doctor import Doctor
from src.models.prescription import Prescription, PrescriptionItem
from src.models.notification import Notification
from src.routes.auth import token_required, current_role

prescription_bp = Blueprint('prescription', __name__)


# ──────────────────────────────────────────────
# مساعدات
# ──────────────────────────────────────────────

def _notify(user_id, title, message, ref_id=None):
    db.session.add(Notification(
        user_id=user_id,
        title=title,
        message=message,
        type='prescription',
        reference_id=ref_id,
        reference_type='prescription',
    ))


def _enrich(rx):
    d = rx.to_dict()
    doctor  = Doctor.query.get(rx.doctor_id)
    patient = Patient.query.get(rx.patient_id)
    d['doctor']  = {'id': doctor.id,  'name': f"د. {doctor.first_name} {doctor.last_name}",  'specialization': doctor.specialization}  if doctor  else None
    d['patient'] = {'id': patient.id, 'name': f"{patient.first_name} {patient.last_name}", 'phone': patient.phone} if patient else None
    return d


# ──────────────────────────────────────────────
# قائمة الوصفات
# ──────────────────────────────────────────────

@prescription_bp.route('', methods=['GET'])
@token_required
def list_prescriptions(current_user):
    """
    المريض → وصفاته  |  الطبيب → ما أصدره  |  الصيدلية → ما أُرسل إليها
    اختياري: ?status=active|sent_to_pharmacy|dispensed|cancelled
    """
    status_filter = request.args.get('status')

    role = current_role(current_user)
    if role == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
        query = Prescription.query.filter_by(patient_id=patient.id)

    elif role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if not doctor:
            return jsonify({'message': 'لم يتم العثور على ملف الطبيب'}), 404
        query = Prescription.query.filter_by(doctor_id=doctor.id)

    elif role == 'pharmacy':
        query = Prescription.query.filter_by(pharmacy_user_id=current_user.id)

    else:
        return jsonify({'message': 'غير مصرح'}), 403

    if status_filter:
        query = query.filter_by(status=status_filter)

    prescriptions = query.order_by(Prescription.created_at.desc()).all()
    return jsonify({
        'prescriptions': [_enrich(rx) for rx in prescriptions],
        'total': len(prescriptions),
    }), 200


# ──────────────────────────────────────────────
# إنشاء وصفة (الطبيب)
# ──────────────────────────────────────────────

@prescription_bp.route('', methods=['POST'])
@token_required
def create_prescription(current_user):
    if current_role(current_user) != 'doctor':
        return jsonify({'message': 'فقط الأطباء يمكنهم إنشاء وصفات'}), 403

    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        return jsonify({'message': 'لم يتم العثور على ملف الطبيب'}), 404

    data = request.get_json() or {}
    if not data.get('patient_id'):
        return jsonify({'message': 'patient_id مطلوب'}), 400
    if not data.get('items') or not isinstance(data['items'], list) or len(data['items']) == 0:
        return jsonify({'message': 'يجب أن تحتوي الوصفة على دواء واحد على الأقل'}), 400

    patient = Patient.query.get(data['patient_id'])
    if not patient:
        return jsonify({'message': 'المريض غير موجود'}), 404

    # يجب أن يكون للطبيب علاقة موعد مع المريض
    from src.models.appointment import Appointment
    has_relationship = Appointment.query.filter_by(
        doctor_id=doctor.id,
        patient_id=patient.id,
    ).first()
    if not has_relationship:
        return jsonify({'message': 'لا يمكنك إنشاء وصفة لمريض ليس من مرضاك'}), 403

    valid_until = None
    if data.get('valid_until'):
        try:
            valid_until = datetime.strptime(data['valid_until'], '%Y-%m-%d').date()
        except ValueError:
            pass
    if not valid_until:
        valid_until = (datetime.utcnow() + timedelta(days=30)).date()

    rx = Prescription(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_id=data.get('appointment_id'),
        diagnosis=data.get('diagnosis'),
        notes=data.get('notes'),
        valid_until=valid_until,
        status='active',
    )
    db.session.add(rx)
    db.session.flush()

    for item_data in data['items']:
        if not item_data.get('drug_name') or not item_data.get('dosage') or not item_data.get('frequency'):
            return jsonify({'message': 'كل دواء يجب أن يحتوي على: drug_name, dosage, frequency'}), 400
        db.session.add(PrescriptionItem(
            prescription_id=rx.id,
            drug_name=item_data['drug_name'],
            generic_name=item_data.get('generic_name'),
            dosage=item_data['dosage'],
            form=item_data.get('form'),
            frequency=item_data['frequency'],
            duration=item_data.get('duration'),
            quantity=item_data.get('quantity'),
            instructions=item_data.get('instructions'),
        ))

    # إشعار المريض
    _notify(
        patient.user_id,
        'وصفة طبية جديدة 📋',
        f'أصدر د. {doctor.first_name} {doctor.last_name} وصفة طبية جديدة لك.',
        ref_id=rx.id,
    )

    db.session.commit()
    return jsonify({'message': 'تم إنشاء الوصفة', 'prescription': _enrich(rx)}), 201


# ──────────────────────────────────────────────
# تفاصيل وصفة
# ──────────────────────────────────────────────

@prescription_bp.route('/<int:rx_id>', methods=['GET'])
@token_required
def get_prescription(current_user, rx_id):
    rx = Prescription.query.get_or_404(rx_id)

    patient  = Patient.query.filter_by(user_id=current_user.id).first()
    doctor   = Doctor.query.filter_by(user_id=current_user.id).first()
    is_owner = (
        (patient and rx.patient_id == patient.id) or
        (doctor  and rx.doctor_id  == doctor.id)  or
        (current_role(current_user) == 'pharmacy' and rx.pharmacy_user_id == current_user.id) or
        current_role(current_user) in ('admin', 'super_admin')
    )
    if not is_owner:
        return jsonify({'message': 'غير مصرح'}), 403

    return jsonify({'prescription': _enrich(rx)}), 200


# ──────────────────────────────────────────────
# إرسال إلى الصيدلية (الطبيب أو المريض)
# ──────────────────────────────────────────────

@prescription_bp.route('/<int:rx_id>/send-pharmacy', methods=['POST'])
@token_required
def send_to_pharmacy(current_user, rx_id):
    rx = Prescription.query.get_or_404(rx_id)

    doctor  = Doctor.query.filter_by(user_id=current_user.id).first()
    patient = Patient.query.filter_by(user_id=current_user.id).first()

    is_doctor_owner  = doctor  and rx.doctor_id  == doctor.id
    is_patient_owner = patient and rx.patient_id == patient.id

    if not (is_doctor_owner or is_patient_owner):
        return jsonify({'message': 'غير مصرح'}), 403

    if rx.status not in ('active',):
        return jsonify({'message': 'يمكن إرسال الوصفات النشطة فقط'}), 400

    data = request.get_json() or {}
    pharmacy_name    = data.get('pharmacy_name', 'الصيدلية')
    pharmacy_user_id = data.get('pharmacy_user_id')

    # التحقق من صيدلية محددة
    if pharmacy_user_id:
        pharm_user = User.query.get(pharmacy_user_id)
        if not pharm_user or pharm_user.user_type != 'pharmacy':
            return jsonify({'message': 'الصيدلية المحددة غير صالحة'}), 400
        rx.pharmacy_user_id = pharmacy_user_id
        pharmacy_name = pharm_user.email

    rx.pharmacy_name       = pharmacy_name
    rx.status              = 'sent_to_pharmacy'
    rx.sent_to_pharmacy_at = datetime.utcnow()

    # إشعار الصيدلية إن كانت محددة
    if rx.pharmacy_user_id:
        _notify(
            rx.pharmacy_user_id,
            'وصفة طبية جديدة للصرف',
            f'وصلت وصفة طبية جديدة من د. {doctor.first_name if doctor else ""} {doctor.last_name if doctor else ""} للصرف.',
            ref_id=rx.id,
        )

    # إشعار المريض إذا أرسلها الطبيب
    if is_doctor_owner:
        _notify(
            Patient.query.get(rx.patient_id).user_id,
            'تم إرسال وصفتك للصيدلية',
            f'أرسل الطبيب وصفتك إلى {pharmacy_name}.',
            ref_id=rx.id,
        )

    db.session.commit()
    return jsonify({'message': 'تم إرسال الوصفة إلى الصيدلية', 'prescription': _enrich(rx)}), 200


# ──────────────────────────────────────────────
# تأكيد الصرف (الصيدلية أو الطبيب)
# ──────────────────────────────────────────────

@prescription_bp.route('/<int:rx_id>/dispense', methods=['POST'])
@token_required
def dispense_prescription(current_user, rx_id):
    rx = Prescription.query.get_or_404(rx_id)

    is_pharmacy = current_role(current_user) == 'pharmacy' and rx.pharmacy_user_id == current_user.id
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    is_doctor = doctor and rx.doctor_id == doctor.id

    if not (is_pharmacy or is_doctor or current_role(current_user) in ('admin', 'super_admin')):
        return jsonify({'message': 'غير مصرح'}), 403

    if rx.status not in ('sent_to_pharmacy', 'active'):
        return jsonify({'message': 'لا يمكن تأكيد صرف هذه الوصفة'}), 400

    data = request.get_json() or {}
    rx.status       = 'dispensed'
    rx.dispensed_at = datetime.utcnow()
    rx.dispensed_by = data.get('dispensed_by', 'الصيدلية')

    patient = Patient.query.get(rx.patient_id)
    if patient:
        _notify(
            patient.user_id,
            'تم صرف وصفتك ✅',
            f'تم صرف وصفتك الطبية من {rx.dispensed_by}.',
            ref_id=rx.id,
        )

    db.session.commit()
    return jsonify({'message': 'تم تأكيد صرف الوصفة', 'prescription': _enrich(rx)}), 200


# ──────────────────────────────────────────────
# إلغاء وصفة (الطبيب فقط)
# ──────────────────────────────────────────────

@prescription_bp.route('/<int:rx_id>/cancel', methods=['POST'])
@token_required
def cancel_prescription(current_user, rx_id):
    if current_role(current_user) != 'doctor':
        return jsonify({'message': 'فقط الطبيب يمكنه إلغاء الوصفة'}), 403

    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    rx = Prescription.query.get_or_404(rx_id)
    if not doctor or rx.doctor_id != doctor.id:
        return jsonify({'message': 'غير مصرح'}), 403

    if rx.status == 'dispensed':
        return jsonify({'message': 'لا يمكن إلغاء وصفة تم صرفها'}), 400

    rx.status = 'cancelled'

    patient = Patient.query.get(rx.patient_id)
    if patient:
        _notify(patient.user_id, 'تم إلغاء وصفتك', 'تم إلغاء الوصفة الطبية من قِبل الطبيب.', ref_id=rx.id)

    db.session.commit()
    return jsonify({'message': 'تم إلغاء الوصفة'}), 200
