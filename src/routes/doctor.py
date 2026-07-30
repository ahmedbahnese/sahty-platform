"""
مسارات API للأطباء
يشمل: قائمة الأطباء، البحث، الملف الشخصي، الأوقات المتاحة، إدارة الملف
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta, time
from sqlalchemy import or_, and_
from src.models.user import db, User
from src.models.doctor import Doctor, DoctorAvailability
from src.models.appointment import Appointment, AppointmentRating
from src.routes.auth import token_required

doctor_bp = Blueprint('doctor', __name__, url_prefix='/api/doctors')

DAYS_AR = {0: 'الاثنين', 1: 'الثلاثاء', 2: 'الأربعاء',
           3: 'الخميس', 4: 'الجمعة', 5: 'السبت', 6: 'الأحد'}


# ────────────────────────────────────────────
# قائمة الأطباء / البحث
# ────────────────────────────────────────────

@doctor_bp.route('', methods=['GET'])
def list_doctors():
    """
    البحث عن أطباء.
    ?search=اسم  ?specialization=تخصص  ?city=مدينة
    ?telemedicine=1  ?verified=1  ?page=1  ?per_page=20
    """
    search         = request.args.get('search', '').strip()
    specialization = request.args.get('specialization', '').strip()
    city           = request.args.get('city', '').strip()
    telemedicine   = request.args.get('telemedicine') == '1'
    verified_only  = request.args.get('verified') == '1'
    page           = request.args.get('page', 1, type=int)
    per_page       = min(request.args.get('per_page', 20, type=int), 50)

    query = Doctor.query.filter_by(is_active=True)

    if search:
        query = query.filter(or_(
            Doctor.first_name.ilike(f'%{search}%'),
            Doctor.last_name.ilike(f'%{search}%'),
            Doctor.specialization.ilike(f'%{search}%'),
            Doctor.clinic_name.ilike(f'%{search}%'),
        ))
    if specialization:
        query = query.filter(Doctor.specialization.ilike(f'%{specialization}%'))
    if city:
        query = query.filter(or_(
            Doctor.clinic_address.ilike(f'%{city}%'),
            Doctor.hospital_affiliation.ilike(f'%{city}%'),
        ))
    if telemedicine:
        query = query.filter_by(available_for_telemedicine=True)
    if verified_only:
        query = query.filter_by(is_verified=True)

    total = query.count()
    doctors = query.order_by(Doctor.rating.desc(), Doctor.is_verified.desc())\
        .offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        'doctors':  [_doctor_summary(d) for d in doctors],
        'total':    total,
        'page':     page,
        'per_page': per_page,
        'pages':    (total + per_page - 1) // per_page,
    }), 200


def _doctor_summary(doctor):
    """ملخص بيانات الطبيب لقوائم البحث"""
    d = doctor.to_dict()
    # حساب عدد المواعيد المكتملة
    d['appointments_count'] = Appointment.query.filter_by(
        doctor_id=doctor.id, status='completed'
    ).count()
    d['availability_days'] = _get_availability_days(doctor.id)
    return d


def _get_availability_days(doctor_id):
    """أيام العمل المتاحة"""
    avail = DoctorAvailability.query.filter_by(doctor_id=doctor_id, is_available=True).all()
    return [{'day': DAYS_AR.get(a.day_of_week, ''), 'day_num': a.day_of_week,
             'start': a.start_time.strftime('%H:%M') if a.start_time else None,
             'end':   a.end_time.strftime('%H:%M')   if a.end_time   else None}
            for a in avail]


# ────────────────────────────────────────────
# ملف طبيب مفصل
# ────────────────────────────────────────────

@doctor_bp.route('/<int:doctor_id>', methods=['GET'])
def get_doctor(doctor_id):
    """الملف الشخصي الكامل للطبيب"""
    doctor = Doctor.query.get_or_404(doctor_id)
    if not doctor.is_active:
        return jsonify({'error': 'الطبيب غير متاح'}), 404

    # آخر تقييمات
    ratings = AppointmentRating.query.join(Appointment)\
        .filter(Appointment.doctor_id == doctor_id)\
        .order_by(AppointmentRating.created_at.desc()).limit(5).all()

    data = doctor.to_dict()
    data['availability']  = _get_availability_days(doctor_id)
    data['appointments_count'] = Appointment.query.filter_by(
        doctor_id=doctor_id, status='completed'
    ).count()
    data['reviews'] = [_format_rating(r) for r in ratings]

    return jsonify({'doctor': data}), 200


def _format_rating(rating):
    from src.models.patient import Patient
    from src.models.user import User
    patient = Patient.query.get(
        Appointment.query.get(rating.appointment_id).patient_id
    ) if rating.appointment_id else None
    return {
        'id':         rating.id,
        'rating':     rating.rating,
        'review':     rating.review,
        'created_at': rating.created_at.isoformat() if rating.created_at else None,
        'patient_name': f"{patient.first_name} {patient.last_name[0]}." if patient else 'مريض',
    }


# ────────────────────────────────────────────
# الأوقات المتاحة للحجز
# ────────────────────────────────────────────

@doctor_bp.route('/<int:doctor_id>/available-slots', methods=['GET'])
def get_available_slots(doctor_id):
    """
    الأوقات الشاغرة للحجز خلال الأيام القادمة.
    ?days=7  (عدد الأيام للأمام، افتراضياً 7)
    """
    doctor = Doctor.query.get_or_404(doctor_id)
    if not doctor.is_active:
        return jsonify({'slots': []}), 200

    days_ahead = min(request.args.get('days', 7, type=int), 30)
    duration   = doctor.consultation_duration or 30  # دقيقة

    # جدول التوفر المتكرر
    availability = DoctorAvailability.query.filter_by(
        doctor_id=doctor_id, is_available=True
    ).all()
    avail_by_day = {a.day_of_week: a for a in availability}

    # المواعيد المحجوزة خلال الفترة
    start_dt = datetime.utcnow()
    end_dt   = start_dt + timedelta(days=days_ahead)
    booked   = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date >= start_dt,
        Appointment.appointment_date < end_dt,
        Appointment.status.in_(['scheduled', 'confirmed']),
    ).all()
    booked_times = {a.appointment_date.replace(second=0, microsecond=0) for a in booked}

    slots = []
    for day_offset in range(days_ahead):
        day_date = (start_dt + timedelta(days=day_offset)).date()
        weekday  = day_date.weekday()  # 0=Monday … 6=Sunday

        if weekday not in avail_by_day:
            continue

        avail = avail_by_day[weekday]
        slot_time = datetime.combine(day_date, avail.start_time)
        end_time  = datetime.combine(day_date, avail.end_time)

        while slot_time + timedelta(minutes=duration) <= end_time:
            # تجاوز الأوقات الماضية
            if slot_time > start_dt:
                is_booked = slot_time.replace(second=0, microsecond=0) in booked_times
                if not is_booked:
                    slots.append({
                        'datetime':  slot_time.isoformat(),
                        'date':      day_date.isoformat(),
                        'time':      slot_time.strftime('%H:%M'),
                        'day':       DAYS_AR.get(weekday, ''),
                        'duration':  duration,
                        'available': True,
                    })
            slot_time += timedelta(minutes=duration)

    return jsonify({
        'slots':    slots,
        'total':    len(slots),
        'doctor_id': doctor_id,
        'duration': duration,
    }), 200


# ────────────────────────────────────────────
# إدارة ملف الطبيب (الطبيب نفسه)
# ────────────────────────────────────────────

@doctor_bp.route('/me', methods=['GET'])
@token_required
def get_my_profile(current_user):
    """الملف الشخصي للطبيب المسجل دخوله"""
    if current_user.user_type != 'doctor':
        return jsonify({'error': 'غير مصرح — فقط الأطباء'}), 403

    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        return jsonify({'error': 'لم يتم العثور على ملف الطبيب'}), 404

    data = doctor.to_dict()
    data['availability'] = [a.to_dict() for a in doctor.availability]
    # إحصائيات سريعة
    data['stats'] = {
        'total_appointments': Appointment.query.filter_by(doctor_id=doctor.id).count(),
        'completed':          Appointment.query.filter_by(doctor_id=doctor.id, status='completed').count(),
        'upcoming':           Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date >= datetime.utcnow(),
            Appointment.status.in_(['scheduled', 'confirmed']),
        ).count(),
    }
    return jsonify({'doctor': data}), 200


@doctor_bp.route('/me', methods=['PUT'])
@token_required
def update_my_profile(current_user):
    """تحديث الملف الشخصي للطبيب"""
    if current_user.user_type != 'doctor':
        return jsonify({'error': 'غير مصرح'}), 403

    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        return jsonify({'error': 'لم يتم العثور على ملف الطبيب'}), 404

    data = request.get_json() or {}
    updatable = [
        'first_name', 'last_name', 'phone',
        'specialization', 'sub_specialization', 'years_of_experience',
        'clinic_name', 'clinic_address', 'hospital_affiliation',
        'consultation_fee', 'consultation_duration', 'available_for_telemedicine',
    ]
    for field in updatable:
        if field in data:
            setattr(doctor, field, data[field])

    db.session.commit()
    return jsonify({'success': True, 'doctor': doctor.to_dict()}), 200


@doctor_bp.route('/me/availability', methods=['POST'])
@token_required
def set_availability(current_user):
    """
    تحديث أوقات العمل للطبيب.
    يستقبل قائمة: [{ day_of_week, start_time, end_time, is_available }]
    يستبدل جدول العمل الحالي بالكامل.
    """
    if current_user.user_type != 'doctor':
        return jsonify({'error': 'غير مصرح'}), 403

    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        return jsonify({'error': 'لم يتم العثور على ملف الطبيب'}), 404

    data = request.get_json() or {}
    slots = data.get('availability', [])
    if not isinstance(slots, list):
        return jsonify({'error': 'يجب إرسال قائمة بأوقات العمل'}), 400

    # احذف القديم وأضف الجديد
    DoctorAvailability.query.filter_by(doctor_id=doctor.id).delete()

    for slot in slots:
        try:
            start = time.fromisoformat(slot['start_time'])
            end   = time.fromisoformat(slot['end_time'])
        except (KeyError, ValueError):
            continue

        db.session.add(DoctorAvailability(
            doctor_id=doctor.id,
            day_of_week=int(slot['day_of_week']),
            start_time=start,
            end_time=end,
            is_available=slot.get('is_available', True),
        ))

    db.session.commit()
    return jsonify({
        'success': True,
        'availability': [a.to_dict() for a in DoctorAvailability.query.filter_by(doctor_id=doctor.id).all()],
    }), 200


# ────────────────────────────────────────────
# تقييم الطبيب
# ────────────────────────────────────────────

@doctor_bp.route('/<int:doctor_id>/rate', methods=['POST'])
@token_required
def rate_doctor(current_user, doctor_id):
    """تقييم الطبيب بعد اكتمال الموعد"""
    from src.models.patient import Patient
    from src.models.appointment import AppointmentRating

    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'error': 'ملف المريض غير موجود'}), 404

    data = request.get_json() or {}
    appointment_id = data.get('appointment_id')
    rating_val     = data.get('rating')

    if not appointment_id or rating_val is None:
        return jsonify({'error': 'appointment_id و rating مطلوبان'}), 400

    rating_val = float(rating_val)
    if not (1 <= rating_val <= 5):
        return jsonify({'error': 'التقييم يجب أن يكون بين 1 و 5'}), 400

    appt = Appointment.query.get_or_404(appointment_id)
    if appt.patient_id != patient.id or appt.doctor_id != doctor_id:
        return jsonify({'error': 'غير مصرح'}), 403
    if appt.status != 'completed':
        return jsonify({'error': 'يمكن التقييم فقط بعد اكتمال الموعد'}), 400

    existing = AppointmentRating.query.filter_by(appointment_id=appointment_id).first()
    if existing:
        existing.rating = rating_val
        existing.review = data.get('review')
    else:
        db.session.add(AppointmentRating(
            appointment_id=appointment_id,
            user_id=current_user.id,
            rating=rating_val,
            review=data.get('review'),
        ))

    # تحديث متوسط تقييم الطبيب
    doctor = Doctor.query.get(doctor_id)
    if doctor:
        all_ratings = AppointmentRating.query.join(Appointment)\
            .filter(Appointment.doctor_id == doctor_id).all()
        all_vals = [r.rating for r in all_ratings]
        doctor.rating        = round(sum(all_vals) / len(all_vals), 1)
        doctor.total_reviews = len(all_vals)

    db.session.commit()
    return jsonify({'success': True, 'message': 'شكراً على تقييمك'}), 200
