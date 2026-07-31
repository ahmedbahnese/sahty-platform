"""
مسارات متابعة الأدوية — Sprint X Enhancement
يشمل: الاستيراد من الوصفة، إحصائيات الالتزام، إشعار الطبيب عند تكرار التفويت.
"""

from datetime import datetime, date, time, timedelta
import json

from flask import Blueprint, request, jsonify
from src.routes.auth import token_required
from src.models.user import db
from src.models.medication import Medication, MedicationSchedule, MedicationLog
from src.models.patient import Patient
from src.models.notification import Notification

medication_bp = Blueprint('medication', __name__, url_prefix='/api/medications')


# ─────────────────────────────────────────
# مساعدات
# ─────────────────────────────────────────

def _notify_user(user_id, title, message, ref_type='medication', ref_id=None):
    db.session.add(Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=ref_type,
        reference_id=ref_id,
        reference_type=ref_type,
    ))


def _check_and_notify_missed(med, patient):
    """إشعار الطبيب إذا تكررت الجرعات الفائتة أكثر من الحد المسموح."""
    if not med.notify_doctor_on_missed or not med.doctor_id:
        return

    threshold = med.missed_dose_threshold or 3
    # عدد الجرعات الفائتة في آخر 7 أيام
    since = datetime.utcnow() - timedelta(days=7)
    missed_count = MedicationLog.query.filter(
        MedicationLog.medication_id == med.id,
        MedicationLog.status.in_(['missed']),
        MedicationLog.created_at >= since,
    ).count()

    if missed_count >= threshold:
        from src.models.doctor import Doctor
        doctor = Doctor.query.get(med.doctor_id)
        if doctor:
            _notify_user(
                doctor.user_id,
                f'تنبيه: المريض يتغيب عن دواء {med.name}',
                f'المريض {patient.first_name} {patient.last_name} فوّت {missed_count} جرعات '
                f'من دواء "{med.name}" خلال آخر 7 أيام. يُرجى المتابعة.',
                'medication', med.id,
            )


def _notify_family_missed(med, patient):
    """إشعار أفراد الأسرة عند تفويت جرعة."""
    if not med.notify_family:
        return
    try:
        from src.models.family_health import FamilyMember
        members = FamilyMember.query.filter_by(patient_id=patient.id).all()
        for m in members:
            if m.user_id:
                _notify_user(
                    m.user_id,
                    f'تنبيه: {patient.first_name} فوّت جرعة دواء',
                    f'فوّت {patient.first_name} جرعة دواء "{med.name}". يرجى المتابعة.',
                    'medication', med.id,
                )
    except Exception:
        pass


# ─────────────────────────────────────────
# الأدوية
# ─────────────────────────────────────────
@medication_bp.route('/', methods=['GET'])
@token_required
def get_medications(current_user):
    """جلب أدوية المريض"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'success': False, 'error': 'ملف المريض غير موجود'}), 404

    status = request.args.get('status', 'active')  # active, all, completed
    query = Medication.query.filter_by(patient_id=patient.id)
    if status == 'active':
        query = query.filter_by(is_active=True, is_completed=False)
    elif status == 'completed':
        query = query.filter_by(is_completed=True)

    medications = query.order_by(Medication.created_at.desc()).all()

    result = []
    for med in medications:
        med_dict = med.to_dict()
        schedules = MedicationSchedule.query.filter_by(medication_id=med.id, is_active=True).all()
        med_dict['schedules'] = [s.to_dict() for s in schedules]

        # حساب نسبة الالتزام
        total_logs = MedicationLog.query.filter_by(medication_id=med.id).count()
        taken_logs = MedicationLog.query.filter_by(medication_id=med.id, status='taken').count()
        med_dict['adherence_rate'] = round((taken_logs / total_logs * 100) if total_logs > 0 else 0, 1)
        result.append(med_dict)

    return jsonify({'success': True, 'medications': result})


@medication_bp.route('/', methods=['POST'])
@token_required
def add_medication(current_user):
    """إضافة دواء جديد"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'success': False, 'error': 'ملف المريض غير موجود'}), 404

    data = request.get_json()
    required = ['name', 'dosage', 'frequency', 'start_date']
    for field in required:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'الحقل {field} مطلوب'}), 400

    try:
        start = date.fromisoformat(data['start_date'])
        end = date.fromisoformat(data['end_date']) if data.get('end_date') else None
    except ValueError:
        return jsonify({'success': False, 'error': 'تنسيق التاريخ غير صحيح'}), 400

    med = Medication(
        patient_id=patient.id,
        name=data['name'],
        generic_name=data.get('generic_name'),
        dosage=data['dosage'],
        form=data.get('form', 'tablet'),
        frequency=data['frequency'],
        duration=data.get('duration'),
        instructions=data.get('instructions'),
        start_date=start,
        end_date=end,
        side_effects=data.get('side_effects'),
        warnings=data.get('warnings'),
        is_active=True,
        notify_family=data.get('notify_family', False),
        notify_doctor_on_missed=data.get('notify_doctor_on_missed', False),
        missed_dose_threshold=data.get('missed_dose_threshold', 3),
        source=data.get('source', 'manual'),
        prescription_id=data.get('prescription_id'),
    )
    db.session.add(med)
    db.session.flush()

    # إضافة جداول التذكير
    if data.get('schedule_times'):
        for t_str in data['schedule_times']:
            try:
                h, m = map(int, t_str.split(':'))
                schedule = MedicationSchedule(
                    medication_id=med.id,
                    time_of_day=time(h, m),
                    reminder_enabled=True
                )
                db.session.add(schedule)
            except Exception:
                pass

    db.session.commit()
    return jsonify({'success': True, 'medication': med.to_dict()}), 201


@medication_bp.route('/import-from-prescription/<int:prescription_id>', methods=['POST'])
@token_required
def import_from_prescription(current_user, prescription_id):
    """استيراد الأدوية تلقائياً من وصفة طبيب الى متابعة الأدوية."""
    from src.models.prescription import Prescription, PrescriptionItem

    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'success': False, 'error': 'ملف المريض غير موجود'}), 404

    rx = Prescription.query.get(prescription_id)
    if not rx:
        return jsonify({'success': False, 'error': 'الوصفة غير موجودة'}), 404
    if rx.patient_id != patient.id:
        return jsonify({'success': False, 'error': 'غير مصرح'}), 403

    items = PrescriptionItem.query.filter_by(prescription_id=rx.id).all()
    if not items:
        return jsonify({'success': False, 'error': 'الوصفة لا تحتوي على أدوية'}), 400

    data_body = request.get_json(silent=True) or {}
    notify_family = data_body.get('notify_family', False)
    notify_doctor = data_body.get('notify_doctor_on_missed', False)

    created = []
    today = date.today()
    for item in items:
        # تجنّب الاستيراد المكرر
        existing = Medication.query.filter_by(
            patient_id=patient.id, prescription_id=rx.id, name=item.drug_name
        ).first()
        if existing:
            continue

        # احسب تاريخ الانتهاء من المدة
        end_date = None
        if item.duration_days:
            end_date = today + timedelta(days=item.duration_days)

        med = Medication(
            patient_id=patient.id,
            doctor_id=rx.doctor_id,
            prescription_id=rx.id,
            source='prescription',
            name=item.drug_name,
            dosage=item.dosage or '',
            form=item.dosage_form or 'tablet',
            frequency=item.frequency or 'مرة يومياً',
            duration=f'{item.duration_days} يوماً' if item.duration_days else None,
            instructions=item.instructions,
            start_date=today,
            end_date=end_date,
            is_active=True,
            notify_family=notify_family,
            notify_doctor_on_missed=notify_doctor,
        )
        db.session.add(med)
        db.session.flush()

        # جدول افتراضي: مرة صباحاً
        schedule = MedicationSchedule(
            medication_id=med.id,
            time_of_day=time(8, 0),
            reminder_enabled=True,
        )
        db.session.add(schedule)
        created.append(med.to_dict())

    db.session.commit()
    return jsonify({'success': True, 'imported': len(created), 'medications': created}), 201


@medication_bp.route('/adherence-stats', methods=['GET'])
@token_required
def adherence_stats(current_user):
    """إحصائيات الالتزام الشاملة للمريض."""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'success': False, 'error': 'ملف المريض غير موجود'}), 404

    days = request.args.get('days', 30, type=int)
    since = datetime.utcnow() - timedelta(days=days)

    meds = Medication.query.filter_by(patient_id=patient.id).all()
    stats = []
    overall_taken = 0
    overall_total = 0

    for med in meds:
        logs = MedicationLog.query.filter(
            MedicationLog.medication_id == med.id,
            MedicationLog.created_at >= since,
        ).all()
        total = len(logs)
        taken = sum(1 for l in logs if l.status == 'taken')
        missed = sum(1 for l in logs if l.status == 'missed')
        skipped = sum(1 for l in logs if l.status == 'skipped')
        overall_taken += taken
        overall_total += total

        stats.append({
            'medication_id': med.id,
            'medication_name': med.name,
            'dosage': med.dosage,
            'frequency': med.frequency,
            'total_logs': total,
            'taken': taken,
            'missed': missed,
            'skipped': skipped,
            'adherence_rate': round((taken / total * 100) if total else 0, 1),
        })

    overall_rate = round((overall_taken / overall_total * 100) if overall_total else 0, 1)
    return jsonify({
        'success': True,
        'period_days': days,
        'overall_adherence_rate': overall_rate,
        'medications': stats,
    })


@medication_bp.route('/<int:med_id>', methods=['GET'])
@token_required
def get_medication(current_user, med_id):
    med = _get_med_or_403(current_user, med_id)
    if isinstance(med, tuple):
        return med
    med_dict = med.to_dict()
    schedules = MedicationSchedule.query.filter_by(medication_id=med_id).all()
    logs = MedicationLog.query.filter_by(medication_id=med_id).order_by(
        MedicationLog.scheduled_time.desc()).limit(30).all()
    med_dict['schedules'] = [s.to_dict() for s in schedules]
    med_dict['recent_logs'] = [l.to_dict() for l in logs]
    return jsonify({'success': True, 'medication': med_dict})


@medication_bp.route('/<int:med_id>', methods=['PUT'])
@token_required
def update_medication(current_user, med_id):
    med = _get_med_or_403(current_user, med_id)
    if isinstance(med, tuple):
        return med

    data = request.get_json()
    updatable = ['name', 'generic_name', 'dosage', 'form', 'frequency', 'duration',
                 'instructions', 'side_effects', 'warnings', 'is_active', 'is_completed',
                 'notify_family', 'notify_doctor_on_missed', 'missed_dose_threshold']
    for field in updatable:
        if field in data:
            setattr(med, field, data[field])

    if 'end_date' in data and data['end_date']:
        try:
            med.end_date = date.fromisoformat(data['end_date'])
        except ValueError:
            pass

    med.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'medication': med.to_dict()})


@medication_bp.route('/<int:med_id>', methods=['DELETE'])
@token_required
def delete_medication(current_user, med_id):
    med = _get_med_or_403(current_user, med_id)
    if isinstance(med, tuple):
        return med
    med.is_active = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'تم إلغاء تفعيل الدواء'})


# ─────────────────────────────────────────
# سجلات التناول (Logs)
# ─────────────────────────────────────────
@medication_bp.route('/<int:med_id>/log', methods=['POST'])
@token_required
def log_medication(current_user, med_id):
    """تسجيل تناول / تفويت دواء — مع إشعار الأسرة والطبيب."""
    med = _get_med_or_403(current_user, med_id)
    if isinstance(med, tuple):
        return med

    patient = Patient.query.filter_by(user_id=current_user.id).first()
    data = request.get_json()

    if not data.get('status') or data['status'] not in ('taken', 'missed', 'skipped', 'delayed'):
        return jsonify({'success': False, 'error': 'الحالة يجب أن تكون: taken, missed, skipped, delayed'}), 400

    scheduled_time = datetime.utcnow()
    if data.get('scheduled_time'):
        try:
            scheduled_time = datetime.fromisoformat(data['scheduled_time'])
        except ValueError:
            pass

    actual_time = None
    if data['status'] == 'taken':
        actual_time = datetime.utcnow()
        if data.get('actual_time'):
            try:
                actual_time = datetime.fromisoformat(data['actual_time'])
            except ValueError:
                pass

    log = MedicationLog(
        medication_id=med_id,
        patient_id=patient.id,
        scheduled_time=scheduled_time,
        actual_time=actual_time,
        status=data['status'],
        notes=data.get('notes'),
        side_effects_experienced=data.get('side_effects_experienced')
    )
    db.session.add(log)
    db.session.commit()

    # إشعارات عند التفويت
    if data['status'] == 'missed' and patient:
        _notify_family_missed(med, patient)
        _check_and_notify_missed(med, patient)
        db.session.commit()

    return jsonify({'success': True, 'log': log.to_dict()}), 201


@medication_bp.route('/<int:med_id>/logs', methods=['GET'])
@token_required
def get_medication_logs(current_user, med_id):
    med = _get_med_or_403(current_user, med_id)
    if isinstance(med, tuple):
        return med

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    logs = MedicationLog.query.filter_by(medication_id=med_id).order_by(
        MedicationLog.scheduled_time.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'logs': [l.to_dict() for l in logs.items],
        'total': logs.total,
        'pages': logs.pages,
        'current_page': page
    })


# ─────────────────────────────────────────
# ملخص اليوم
# ─────────────────────────────────────────
@medication_bp.route('/today-summary', methods=['GET'])
@token_required
def today_summary(current_user):
    """ملخص أدوية اليوم"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'success': False, 'error': 'ملف المريض غير موجود'}), 404

    active_meds = Medication.query.filter_by(patient_id=patient.id, is_active=True, is_completed=False).all()

    today = date.today()
    summary = []
    for med in active_meds:
        if med.start_date and med.start_date > today:
            continue
        if med.end_date and med.end_date < today:
            continue

        schedules = MedicationSchedule.query.filter_by(medication_id=med.id, is_active=True).all()
        taken_today = MedicationLog.query.filter(
            MedicationLog.medication_id == med.id,
            MedicationLog.status == 'taken',
            MedicationLog.scheduled_time >= datetime.combine(today, time.min),
            MedicationLog.scheduled_time <= datetime.combine(today, time.max)
        ).count()

        summary.append({
            'medication': med.to_dict(),
            'schedules': [s.to_dict() for s in schedules],
            'taken_today': taken_today,
            'total_doses_today': len(schedules),
            'is_complete': taken_today >= len(schedules)
        })

    return jsonify({'success': True, 'summary': summary, 'date': today.isoformat()})


# ─────────────────────────────────────────
# helper
# ─────────────────────────────────────────
def _get_med_or_403(current_user, med_id):
    med = Medication.query.get(med_id)
    if not med:
        return jsonify({'success': False, 'error': 'الدواء غير موجود'}), 404
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient or med.patient_id != patient.id:
        return jsonify({'success': False, 'error': 'غير مصرح'}), 403
    return med
