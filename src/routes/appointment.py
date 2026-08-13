"""
مسارات API لنظام المواعيد.
يشمل: الحجز، التعديل، الإلغاء، موافقة الطبيب، الإشعارات.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from src.models.user import db, User
from src.models.patient import Patient
from src.models.doctor import Doctor
from src.models.appointment import Appointment, AppointmentHistory
from src.models.notification import Notification
from src.routes.auth import token_required

appointment_bp = Blueprint('appointment', __name__)


# ──────────────────────────────────────────────
# مساعدات
# ──────────────────────────────────────────────

def _notify(user_id, title, message, ref_type='appointment', ref_id=None):
    """إنشاء إشعار داخلي."""
    db.session.add(Notification(
        user_id=user_id,
        title=title,
        message=message,
        type='appointment',
        reference_id=ref_id,
        reference_type=ref_type,
    ))


def _record_history(appointment, new_status, reason, changed_by_id):
    db.session.add(AppointmentHistory(
        appointment_id=appointment.id,
        previous_status=appointment.status,
        new_status=new_status,
        change_reason=reason,
        changed_by=changed_by_id,
    ))
    appointment.status = new_status


def _enrich(appt, include_doctor=True, include_patient=True):
    """أضف بيانات الطبيب/المريض إلى قاموس الموعد."""
    d = appt.to_dict()
    if include_doctor:
        doc = Doctor.query.get(appt.doctor_id)
        d['doctor'] = {
            'id': doc.id,
            'name': f"د. {doc.first_name} {doc.last_name}",
            'specialization': doc.specialization,
            'clinic_name': doc.clinic_name,
            'consultation_fee': doc.consultation_fee,
        } if doc else None
    if include_patient:
        pat = Patient.query.get(appt.patient_id)
        d['patient'] = {
            'id': pat.id,
            'name': f"{pat.first_name} {pat.last_name}",
            'phone': pat.phone,
        } if pat else None
    return d


# ──────────────────────────────────────────────
# قائمة المواعيد
# ──────────────────────────────────────────────

@appointment_bp.route('', methods=['GET'])
@token_required
def list_appointments(current_user):
    """
    المريض يرى مواعيده — الطبيب يرى مواعيده.
    اختياري: ?status=scheduled|confirmed|completed|cancelled
              ?upcoming=1 (قادمة فقط)
    """
    status_filter = request.args.get('status')
    upcoming_only = request.args.get('upcoming') == '1'

    if current_user.user_type == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
        query = Appointment.query.filter_by(patient_id=patient.id)
    elif current_user.user_type == 'doctor':
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if not doctor:
            return jsonify({'message': 'لم يتم العثور على ملف الطبيب'}), 404
        query = Appointment.query.filter_by(doctor_id=doctor.id)
    else:
        return jsonify({'message': 'غير مصرح'}), 403

    if status_filter:
        query = query.filter_by(status=status_filter)
    if upcoming_only:
        query = query.filter(
            Appointment.appointment_date >= datetime.utcnow(),
            Appointment.status.in_(['scheduled', 'confirmed'])
        )

    appointments = query.order_by(Appointment.appointment_date.desc()).all()
    return jsonify({
        'appointments': [_enrich(a) for a in appointments],
        'total': len(appointments)
    }), 200


# ──────────────────────────────────────────────
# إحصائيات
# ──────────────────────────────────────────────

@appointment_bp.route('/stats', methods=['GET'])
@token_required
def get_stats(current_user):
    now = datetime.utcnow()

    if current_user.user_type == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify({'upcoming': 0, 'completed': 0, 'cancelled': 0}), 200
        base = Appointment.query.filter_by(patient_id=patient.id)
    elif current_user.user_type == 'doctor':
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if not doctor:
            return jsonify({'upcoming': 0, 'completed': 0, 'pending': 0}), 200
        base = Appointment.query.filter_by(doctor_id=doctor.id)
    else:
        return jsonify({'message': 'غير مصرح'}), 403

    upcoming   = base.filter(Appointment.appointment_date >= now, Appointment.status.in_(['scheduled', 'confirmed'])).count()
    completed  = base.filter_by(status='completed').count()
    cancelled  = base.filter_by(status='cancelled').count()
    pending    = base.filter_by(status='scheduled').count()

    return jsonify({
        'upcoming':  upcoming,
        'completed': completed,
        'cancelled': cancelled,
        'pending':   pending,
    }), 200


# ──────────────────────────────────────────────
# حجز موعد جديد (المريض)
# ──────────────────────────────────────────────

@appointment_bp.route('', methods=['POST'])
@token_required
def book_appointment(current_user):
    if current_user.user_type != 'patient':
        return jsonify({'message': 'فقط المرضى يمكنهم حجز المواعيد'}), 403

    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404

    data = request.get_json() or {}
    required = ['doctor_id', 'appointment_date', 'appointment_type']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'message': f'الحقول المطلوبة: {", ".join(missing)}'}), 400

    doctor = Doctor.query.get(data['doctor_id'])
    if not doctor or not doctor.is_active:
        return jsonify({'message': 'الطبيب غير موجود أو غير نشط'}), 404

    try:
        appt_date = datetime.fromisoformat(data['appointment_date'])
    except ValueError:
        return jsonify({'message': 'صيغة التاريخ غير صحيحة (ISO 8601)'}), 400

    if appt_date < datetime.utcnow():
        return jsonify({'message': 'لا يمكن حجز موعد في الماضي'}), 400

    # Prevent two patients from reserving the same doctor slot between the
    # availability read and the booking request. The UI also disables booked
    # slots, but this server-side check is the source of truth.
    existing = Appointment.query.filter_by(
        doctor_id=doctor.id,
        appointment_date=appt_date,
    ).filter(Appointment.status.in_(['scheduled', 'confirmed'])).first()
    if existing:
        return jsonify({'message': 'هذا الموعد لم يعد متاحاً، يرجى اختيار وقت آخر'}), 409

    # ── دعم الحجز لفرد من الأسرة ──────────────────────────────────────────────
    for_member_id = data.get('for_family_member_id')
    for_member_name = None

    if for_member_id:
        from src.models.family_health import FamilyMember, FamilyGroup
        member = FamilyMember.query.get(for_member_id)
        if member:
            group = FamilyGroup.query.filter_by(id=member.group_id, owner_user_id=current_user.id).first()
            if group:
                for_member_name = f"{member.first_name} {member.last_name}"
            else:
                for_member_id = None  # لا صلاحية
        else:
            for_member_id = None

    # إذا لم يُحدد فرد من القائمة لكن أرسل اسم يدوي
    if not for_member_id and data.get('for_member_name'):
        for_member_name = data['for_member_name']

    appt = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_date=appt_date,
        appointment_type=data['appointment_type'],
        duration=data.get('duration', doctor.consultation_duration or 30),
        reason=data.get('reason'),
        symptoms=data.get('symptoms'),
        fee=doctor.consultation_fee,
        status='scheduled',
        for_family_member_id=for_member_id,
        for_member_name=for_member_name,
    )
    db.session.add(appt)
    db.session.flush()

    _record_history(appt, 'scheduled', 'حجز جديد من المريض', current_user.id)

    # إشعار الطبيب
    patient_label = (
        f"{patient.first_name} {patient.last_name} (لفرد الأسرة: {for_member_name})"
        if for_member_name else f"{patient.first_name} {patient.last_name}"
    )
    _notify(
        doctor.user_id,
        'طلب موعد جديد',
        f'المريض {patient_label} يطلب موعداً بتاريخ {appt_date.strftime("%Y-%m-%d %H:%M")}',
        ref_id=appt.id,
    )

    # إضافة سجل تلقائي لملف الفرد في الأسرة
    if for_member_id and for_member_name:
        try:
            from src.models.family_health import FamilyMemberHealthRecord
            from datetime import date as _date
            health_rec = FamilyMemberHealthRecord(
                member_id=for_member_id,
                record_type='checkup',
                title=f'موعد طبي — {appt_date.strftime("%Y-%m-%d")}',
                description=data.get('reason', ''),
                date=appt_date.date(),
                doctor_name=f"د. {doctor.first_name} {doctor.last_name}" if doctor else None,
            )
            db.session.add(health_rec)
        except Exception:
            pass

    db.session.commit()
    return jsonify({'message': 'تم حجز الموعد بنجاح', 'appointment': _enrich(appt)}), 201


# ──────────────────────────────────────────────
# تفاصيل موعد
# ──────────────────────────────────────────────

@appointment_bp.route('/<int:appt_id>', methods=['GET'])
@token_required
def get_appointment(current_user, appt_id):
    appt = Appointment.query.get_or_404(appt_id)

    patient = Patient.query.filter_by(user_id=current_user.id).first()
    doctor  = Doctor.query.filter_by(user_id=current_user.id).first()
    is_owner = (
        (patient and appt.patient_id == patient.id) or
        (doctor  and appt.doctor_id  == doctor.id)  or
        current_user.user_type in ('admin', 'super_admin')
    )
    if not is_owner:
        return jsonify({'message': 'غير مصرح'}), 403

    history = AppointmentHistory.query.filter_by(appointment_id=appt_id)\
        .order_by(AppointmentHistory.created_at).all()

    d = _enrich(appt)
    d['history'] = [h.to_dict() for h in history]
    return jsonify({'appointment': d}), 200


# ──────────────────────────────────────────────
# تعديل / إعادة جدولة (المريض)
# ──────────────────────────────────────────────

@appointment_bp.route('/<int:appt_id>', methods=['PUT'])
@token_required
def reschedule_appointment(current_user, appt_id):
    if current_user.user_type != 'patient':
        return jsonify({'message': 'فقط المرضى يمكنهم تعديل مواعيدهم'}), 403

    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404

    appt = Appointment.query.get_or_404(appt_id)
    if appt.patient_id != patient.id:
        return jsonify({'message': 'غير مصرح'}), 403

    if appt.status not in ('scheduled', 'confirmed'):
        return jsonify({'message': 'لا يمكن تعديل موعد بحالته الحالية'}), 400

    data = request.get_json() or {}

    if 'appointment_date' in data:
        try:
            new_date = datetime.fromisoformat(data['appointment_date'])
        except ValueError:
            return jsonify({'message': 'صيغة التاريخ غير صحيحة'}), 400
        if new_date < datetime.utcnow():
            return jsonify({'message': 'لا يمكن تحديد موعد في الماضي'}), 400
        appt.appointment_date = new_date

    if 'appointment_type' in data:
        appt.appointment_type = data['appointment_type']
    if 'reason' in data:
        appt.reason = data['reason']
    if 'symptoms' in data:
        appt.symptoms = data['symptoms']

    prev_status = appt.status
    appt.status = 'scheduled'  # إعادة إلى scheduled بعد التعديل
    _record_history(appt, 'scheduled', f'إعادة جدولة من المريض (كانت: {prev_status})', current_user.id)

    doctor = Doctor.query.get(appt.doctor_id)
    if doctor:
        _notify(
            doctor.user_id,
            'تم تعديل موعد',
            f'قام المريض {patient.first_name} {patient.last_name} بتعديل الموعد إلى {appt.appointment_date.strftime("%Y-%m-%d %H:%M")}',
            ref_id=appt.id,
        )

    db.session.commit()
    return jsonify({'message': 'تم تعديل الموعد', 'appointment': _enrich(appt)}), 200


# ──────────────────────────────────────────────
# إلغاء الموعد
# ──────────────────────────────────────────────

@appointment_bp.route('/<int:appt_id>/cancel', methods=['POST'])
@token_required
def cancel_appointment(current_user, appt_id):
    appt = Appointment.query.get_or_404(appt_id)

    patient = Patient.query.filter_by(user_id=current_user.id).first()
    doctor  = Doctor.query.filter_by(user_id=current_user.id).first()

    is_patient_owner = patient and appt.patient_id == patient.id
    is_doctor_owner  = doctor  and appt.doctor_id  == doctor.id

    if not (is_patient_owner or is_doctor_owner or current_user.user_type in ('admin', 'super_admin')):
        return jsonify({'message': 'غير مصرح'}), 403

    if appt.status in ('completed', 'cancelled'):
        return jsonify({'message': 'لا يمكن إلغاء موعد مكتمل أو ملغى مسبقاً'}), 400

    data   = request.get_json() or {}
    reason = data.get('reason', 'إلغاء بواسطة المستخدم')

    _record_history(appt, 'cancelled', reason, current_user.id)

    # إشعار الطرف الآخر
    if is_patient_owner and doctor:
        _notify(doctor.user_id, 'تم إلغاء موعد',
                f'ألغى المريض {patient.first_name} {patient.last_name} الموعد بتاريخ {appt.appointment_date.strftime("%Y-%m-%d %H:%M")}',
                ref_id=appt.id)
    elif is_doctor_owner and patient:
        _notify(patient.user_id, 'تم إلغاء موعدك',
                f'ألغى الطبيب د. {doctor.first_name} {doctor.last_name} الموعد بتاريخ {appt.appointment_date.strftime("%Y-%m-%d %H:%M")}',
                ref_id=appt.id)

    db.session.commit()
    return jsonify({'message': 'تم إلغاء الموعد', 'appointment': _enrich(appt)}), 200


# ──────────────────────────────────────────────
# تأكيد الموعد (الطبيب)
# ──────────────────────────────────────────────

@appointment_bp.route('/<int:appt_id>/confirm', methods=['POST'])
@token_required
def confirm_appointment(current_user, appt_id):
    if current_user.user_type != 'doctor':
        return jsonify({'message': 'فقط الأطباء يمكنهم تأكيد المواعيد'}), 403

    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        return jsonify({'message': 'لم يتم العثور على ملف الطبيب'}), 404

    appt = Appointment.query.get_or_404(appt_id)
    if appt.doctor_id != doctor.id:
        return jsonify({'message': 'غير مصرح'}), 403

    if appt.status != 'scheduled':
        return jsonify({'message': 'يمكن تأكيد المواعيد المجدولة فقط'}), 400

    data = request.get_json() or {}
    _record_history(appt, 'confirmed', data.get('notes', 'تأكيد من الطبيب'), current_user.id)

    patient = Patient.query.get(appt.patient_id)
    if patient:
        _notify(
            patient.user_id,
            'تم تأكيد موعدك ✅',
            f'أكد الطبيب د. {doctor.first_name} {doctor.last_name} موعدك بتاريخ {appt.appointment_date.strftime("%Y-%m-%d %H:%M")}',
            ref_id=appt.id,
        )

    db.session.commit()
    return jsonify({'message': 'تم تأكيد الموعد', 'appointment': _enrich(appt)}), 200


# ──────────────────────────────────────────────
# إتمام الموعد (الطبيب)
# ──────────────────────────────────────────────

@appointment_bp.route('/<int:appt_id>/complete', methods=['POST'])
@token_required
def complete_appointment(current_user, appt_id):
    if current_user.user_type != 'doctor':
        return jsonify({'message': 'فقط الأطباء يمكنهم إتمام المواعيد'}), 403

    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        return jsonify({'message': 'لم يتم العثور على ملف الطبيب'}), 404

    appt = Appointment.query.get_or_404(appt_id)
    if appt.doctor_id != doctor.id:
        return jsonify({'message': 'غير مصرح'}), 403

    if appt.status not in ('scheduled', 'confirmed'):
        return jsonify({'message': 'لا يمكن إتمام هذا الموعد'}), 400

    data = request.get_json() or {}
    if data.get('notes'):
        appt.notes = data['notes']

    _record_history(appt, 'completed', 'تم الإتمام من قبل الطبيب', current_user.id)

    patient = Patient.query.get(appt.patient_id)
    if patient:
        _notify(
            patient.user_id,
            'اكتمل موعدك',
            f'تم إتمام زيارتك مع د. {doctor.first_name} {doctor.last_name}. يمكنك تقييم التجربة.',
            ref_id=appt.id,
        )

    db.session.commit()
    return jsonify({'message': 'تم إتمام الموعد', 'appointment': _enrich(appt)}), 200


# ──────────────────────────────────────────────
# الإشعارات
# ──────────────────────────────────────────────

@appointment_bp.route('/notifications', methods=['GET'])
@token_required
def get_notifications(current_user):
    notifs = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc()).limit(50).all()
    unread = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({
        'notifications': [n.to_dict() for n in notifs],
        'unread_count':  unread,
    }), 200


@appointment_bp.route('/notifications/mark-read', methods=['POST'])
@token_required
def mark_notifications_read(current_user):
    data = request.get_json() or {}
    ids  = data.get('ids')  # None = mark all
    query = Notification.query.filter_by(user_id=current_user.id, is_read=False)
    if ids:
        query = query.filter(Notification.id.in_(ids))
    query.update({'is_read': True}, synchronize_session=False)
    db.session.commit()
    return jsonify({'message': 'تم التحديث'}), 200
