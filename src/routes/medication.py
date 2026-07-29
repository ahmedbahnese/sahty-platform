"""
مسارات متابعة الأدوية
"""

from datetime import datetime, date, time
import json

from flask import Blueprint, request, jsonify
from src.routes.auth import token_required
from src.models.user import db
from src.models.medication import Medication, MedicationSchedule, MedicationLog
from src.models.patient import Patient

medication_bp = Blueprint('medication', __name__, url_prefix='/api/medications')


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
        is_active=True
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
                 'instructions', 'side_effects', 'warnings', 'is_active', 'is_completed']
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
    """تسجيل تناول / تفويت دواء"""
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
