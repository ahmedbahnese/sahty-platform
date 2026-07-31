"""
مسارات API لإدارة التطعيمات للبالغين والأطفال
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from src.routes.auth import token_required
from src.models.user import db
from src.models.medical_record import Vaccination
from src.models.patient import Patient
from src.models.family_health import FamilyGroup, FamilyMember, FamilyMemberHealthRecord
from src.models.notification import Notification

vaccination_bp = Blueprint('vaccination', __name__, url_prefix='/api/vaccinations')


# ── جدول اللقاحات الموصى بها للبالغين (حسب العمر) ─────────────────────────────
ADULT_SCHEDULE = [
    {
        'vaccine_name': 'لقاح الإنفلونزا الموسمي',
        'disease_prevented': 'الإنفلونزا',
        'frequency': 'yearly',
        'recommended_ages': 'جميع الأعمار (سنوياً)',
        'notes': 'يُوصى بأخذه كل عام في الخريف'
    },
    {
        'vaccine_name': 'لقاح Tdap (الكزاز + الدفتيريا + السعال الديكي)',
        'disease_prevented': 'الكزاز والدفتيريا والسعال الديكي',
        'frequency': 'every_10_years',
        'recommended_ages': 'البالغون (تعزيز كل 10 سنوات)',
        'notes': 'جرعة تعزيز واحدة ثم Td كل 10 سنوات'
    },
    {
        'vaccine_name': 'لقاح التهاب الكبد B',
        'disease_prevented': 'التهاب الكبد B',
        'frequency': 'series',
        'recommended_ages': 'البالغون غير الملقحين',
        'notes': '3 جرعات: 0 و 1 و 6 أشهر'
    },
    {
        'vaccine_name': 'لقاح التهاب الكبد A',
        'disease_prevented': 'التهاب الكبد A',
        'frequency': 'series',
        'recommended_ages': 'البالغون غير الملقحين',
        'notes': 'جرعتان بفارق 6-12 شهراً'
    },
    {
        'vaccine_name': 'لقاح الحصبة والنكاف والحصبة الألمانية (MMR)',
        'disease_prevented': 'الحصبة والنكاف والحصبة الألمانية',
        'frequency': 'once',
        'recommended_ages': 'البالغون المولودون بعد 1957 وغير الملقحين',
        'notes': 'جرعة واحدة أو جرعتان للفئات المعرضة للخطر'
    },
    {
        'vaccine_name': 'لقاح جدري الماء (Varicella)',
        'disease_prevented': 'جدري الماء',
        'frequency': 'series',
        'recommended_ages': 'البالغون غير الملقحين وغير المصابين سابقاً',
        'notes': 'جرعتان بفارق 4-8 أسابيع'
    },
    {
        'vaccine_name': 'لقاح الحمى التيفية',
        'disease_prevented': 'الحمى التيفية',
        'frequency': 'every_2_years',
        'recommended_ages': 'المسافرون إلى مناطق موبوءة',
        'notes': 'تعزيز كل عامين للمسافرين'
    },
    {
        'vaccine_name': 'لقاح الرئة / المكورات الرئوية (Pneumococcal)',
        'disease_prevented': 'الالتهاب الرئوي',
        'frequency': 'once',
        'recommended_ages': '65 سنة فأكثر أو من لديهم حالات طبية مزمنة',
        'notes': 'PCV15 أو PCV20 لكبار السن'
    },
    {
        'vaccine_name': 'لقاح الهربس النطاقي (Shingrix)',
        'disease_prevented': 'الهربس النطاقي',
        'frequency': 'series',
        'recommended_ages': '50 سنة فأكثر',
        'notes': 'جرعتان بفارق 2-6 أشهر'
    },
    {
        'vaccine_name': 'لقاح كوفيد-19',
        'disease_prevented': 'كوفيد-19',
        'frequency': 'yearly',
        'recommended_ages': 'جميع الأعمار',
        'notes': 'الجرعة الأولية + جرعات تعزيز دورية حسب التوصيات الحديثة'
    },
]

# ── جدول اللقاحات للأطفال (حسب العمر بالأشهر) ─────────────────────────────────
CHILD_SCHEDULE = [
    {'age_months': 0,   'vaccine_name': 'لقاح التهاب الكبد B (الجرعة الأولى)', 'disease_prevented': 'التهاب الكبد B', 'notes': 'عند الولادة'},
    {'age_months': 1,   'vaccine_name': 'لقاح التهاب الكبد B (الجرعة الثانية)', 'disease_prevented': 'التهاب الكبد B', 'notes': 'الشهر الأول'},
    {'age_months': 2,   'vaccine_name': 'DTaP (الجرعة الأولى)', 'disease_prevented': 'الدفتيريا والكزاز والسعال الديكي', 'notes': 'الشهر الثاني'},
    {'age_months': 2,   'vaccine_name': 'IPV (الجرعة الأولى) - شلل الأطفال', 'disease_prevented': 'شلل الأطفال', 'notes': 'الشهر الثاني'},
    {'age_months': 2,   'vaccine_name': 'Hib (الجرعة الأولى)', 'disease_prevented': 'المستدمية النزلية ب', 'notes': 'الشهر الثاني'},
    {'age_months': 2,   'vaccine_name': 'PCV13 (الجرعة الأولى) - الرئة', 'disease_prevented': 'الالتهاب الرئوي', 'notes': 'الشهر الثاني'},
    {'age_months': 2,   'vaccine_name': 'RV (الجرعة الأولى) - الروتا', 'disease_prevented': 'الفيروس العجلي', 'notes': 'الشهر الثاني'},
    {'age_months': 4,   'vaccine_name': 'DTaP (الجرعة الثانية)', 'disease_prevented': 'الدفتيريا والكزاز والسعال الديكي', 'notes': 'الشهر الرابع'},
    {'age_months': 4,   'vaccine_name': 'IPV (الجرعة الثانية) - شلل الأطفال', 'disease_prevented': 'شلل الأطفال', 'notes': 'الشهر الرابع'},
    {'age_months': 4,   'vaccine_name': 'Hib (الجرعة الثانية)', 'disease_prevented': 'المستدمية النزلية ب', 'notes': 'الشهر الرابع'},
    {'age_months': 4,   'vaccine_name': 'PCV13 (الجرعة الثانية) - الرئة', 'disease_prevented': 'الالتهاب الرئوي', 'notes': 'الشهر الرابع'},
    {'age_months': 4,   'vaccine_name': 'RV (الجرعة الثانية) - الروتا', 'disease_prevented': 'الفيروس العجلي', 'notes': 'الشهر الرابع'},
    {'age_months': 6,   'vaccine_name': 'DTaP (الجرعة الثالثة)', 'disease_prevented': 'الدفتيريا والكزاز والسعال الديكي', 'notes': 'الشهر السادس'},
    {'age_months': 6,   'vaccine_name': 'Hib (الجرعة الثالثة)', 'disease_prevented': 'المستدمية النزلية ب', 'notes': 'الشهر السادس'},
    {'age_months': 6,   'vaccine_name': 'PCV13 (الجرعة الثالثة) - الرئة', 'disease_prevented': 'الالتهاب الرئوي', 'notes': 'الشهر السادس'},
    {'age_months': 6,   'vaccine_name': 'لقاح التهاب الكبد B (الجرعة الثالثة)', 'disease_prevented': 'التهاب الكبد B', 'notes': 'بين الشهر 6-18'},
    {'age_months': 6,   'vaccine_name': 'لقاح الإنفلونزا (الأول)', 'disease_prevented': 'الإنفلونزا', 'notes': 'من 6 أشهر فصاعداً سنوياً'},
    {'age_months': 12,  'vaccine_name': 'MMR (الجرعة الأولى)', 'disease_prevented': 'الحصبة والنكاف والحصبة الألمانية', 'notes': '12-15 شهراً'},
    {'age_months': 12,  'vaccine_name': 'Varicella (الجرعة الأولى)', 'disease_prevented': 'جدري الماء', 'notes': '12-15 شهراً'},
    {'age_months': 12,  'vaccine_name': 'PCV13 (الجرعة الرابعة) - الرئة', 'disease_prevented': 'الالتهاب الرئوي', 'notes': '12-15 شهراً'},
    {'age_months': 12,  'vaccine_name': 'Hib (الجرعة الرابعة)', 'disease_prevented': 'المستدمية النزلية ب', 'notes': '12-15 شهراً'},
    {'age_months': 12,  'vaccine_name': 'لقاح التهاب الكبد A (الجرعة الأولى)', 'disease_prevented': 'التهاب الكبد A', 'notes': '12-23 شهراً'},
    {'age_months': 18,  'vaccine_name': 'DTaP (الجرعة الرابعة)', 'disease_prevented': 'الدفتيريا والكزاز والسعال الديكي', 'notes': '15-18 شهراً'},
    {'age_months': 18,  'vaccine_name': 'لقاح التهاب الكبد A (الجرعة الثانية)', 'disease_prevented': 'التهاب الكبد A', 'notes': '6 أشهر بعد الجرعة الأولى'},
    {'age_months': 48,  'vaccine_name': 'DTaP (الجرعة الخامسة)', 'disease_prevented': 'الدفتيريا والكزاز والسعال الديكي', 'notes': '4-6 سنوات'},
    {'age_months': 48,  'vaccine_name': 'IPV (الجرعة الرابعة) - شلل الأطفال', 'disease_prevented': 'شلل الأطفال', 'notes': '4-6 سنوات'},
    {'age_months': 48,  'vaccine_name': 'MMR (الجرعة الثانية)', 'disease_prevented': 'الحصبة والنكاف والحصبة الألمانية', 'notes': '4-6 سنوات'},
    {'age_months': 48,  'vaccine_name': 'Varicella (الجرعة الثانية)', 'disease_prevented': 'جدري الماء', 'notes': '4-6 سنوات'},
    {'age_months': 132, 'vaccine_name': 'Tdap (المراهقين)', 'disease_prevented': 'الكزاز والدفتيريا والسعال الديكي', 'notes': '11-12 سنة'},
    {'age_months': 132, 'vaccine_name': 'لقاح HPV (الجرعة الأولى)', 'disease_prevented': 'فيروس الورم الحليمي البشري', 'notes': '11-12 سنة (سلسلة جرعتين أو ثلاثة)'},
    {'age_months': 132, 'vaccine_name': 'لقاح المكورات السحائية (MCV4)', 'disease_prevented': 'التهاب السحايا البكتيري', 'notes': '11-12 سنة'},
]


def _get_patient_or_404(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return None, jsonify({'success': False, 'error': 'ملف المريض غير موجود'}), 404
    return patient, None, None


# ── تطعيمات البالغ (المريض نفسه) ────────────────────────────────────────────────

@vaccination_bp.route('/', methods=['GET'])
@token_required
def list_vaccinations(current_user):
    """قائمة تطعيمات المريض"""
    patient, err, code = _get_patient_or_404(current_user)
    if err:
        return err, code

    vaccinations = Vaccination.query.filter_by(patient_id=patient.id).order_by(
        Vaccination.date_given.desc().nullslast()
    ).all()
    return jsonify({'success': True, 'vaccinations': [v.to_dict() for v in vaccinations]})


@vaccination_bp.route('/', methods=['POST'])
@token_required
def add_vaccination(current_user):
    """إضافة تطعيم للمريض"""
    patient, err, code = _get_patient_or_404(current_user)
    if err:
        return err, code

    data = request.get_json()
    if not data or not data.get('vaccine_name'):
        return jsonify({'success': False, 'error': 'اسم اللقاح مطلوب'}), 400

    vac = Vaccination(
        patient_id=patient.id,
        vaccine_name=data['vaccine_name'],
        disease_prevented=data.get('disease_prevented'),
        dose_number=data.get('dose_number', 1),
        total_doses=data.get('total_doses'),
        date_given=_parse_date(data.get('date_given')),
        next_due_date=_parse_date(data.get('next_due_date')),
        provider=data.get('provider'),
        batch_number=data.get('batch_number'),
        administration_site=data.get('administration_site'),
        reaction=data.get('reaction'),
        notes=data.get('notes'),
    )
    db.session.add(vac)
    db.session.commit()

    # إشعار بالموعد التالي
    if vac.next_due_date:
        db.session.add(Notification(
            user_id=current_user.id,
            title='تطعيم جديد مسجّل',
            message=f'تم تسجيل لقاح {vac.vaccine_name}. الموعد التالي: {vac.next_due_date.strftime("%Y-%m-%d")}',
            type='vaccination',
        ))
        db.session.commit()

    return jsonify({'success': True, 'vaccination': vac.to_dict()}), 201


@vaccination_bp.route('/<int:vac_id>', methods=['PUT'])
@token_required
def update_vaccination(current_user, vac_id):
    """تحديث تطعيم"""
    patient, err, code = _get_patient_or_404(current_user)
    if err:
        return err, code

    vac = Vaccination.query.filter_by(id=vac_id, patient_id=patient.id).first()
    if not vac:
        return jsonify({'success': False, 'error': 'التطعيم غير موجود'}), 404

    data = request.get_json()
    for field in ['vaccine_name', 'disease_prevented', 'dose_number', 'total_doses',
                  'provider', 'batch_number', 'administration_site', 'reaction', 'notes']:
        if field in data:
            setattr(vac, field, data[field])
    if 'date_given' in data:
        vac.date_given = _parse_date(data['date_given'])
    if 'next_due_date' in data:
        vac.next_due_date = _parse_date(data['next_due_date'])

    db.session.commit()
    return jsonify({'success': True, 'vaccination': vac.to_dict()})


@vaccination_bp.route('/<int:vac_id>', methods=['DELETE'])
@token_required
def delete_vaccination(current_user, vac_id):
    patient, err, code = _get_patient_or_404(current_user)
    if err:
        return err, code

    vac = Vaccination.query.filter_by(id=vac_id, patient_id=patient.id).first()
    if not vac:
        return jsonify({'success': False, 'error': 'التطعيم غير موجود'}), 404

    db.session.delete(vac)
    db.session.commit()
    return jsonify({'success': True, 'message': 'تم حذف التطعيم'})


@vaccination_bp.route('/schedule', methods=['GET'])
@token_required
def get_recommended_schedule(current_user):
    """جدول التطعيمات الموصى بها للبالغ"""
    patient, err, code = _get_patient_or_404(current_user)
    if err:
        return err, code

    # احسب العمر
    age_years = None
    if patient.date_of_birth:
        age_years = (date.today() - patient.date_of_birth).days // 365

    # حدد التطعيمات المأخوذة فعلاً
    taken_names = {v.vaccine_name for v in
                   Vaccination.query.filter_by(patient_id=patient.id).all()}

    schedule = []
    for vac in ADULT_SCHEDULE:
        status = 'taken' if vac['vaccine_name'] in taken_names else 'recommended'
        schedule.append({**vac, 'status': status})

    return jsonify({
        'success': True,
        'patient_age': age_years,
        'schedule': schedule,
    })


@vaccination_bp.route('/upcoming', methods=['GET'])
@token_required
def upcoming_vaccinations(current_user):
    """التطعيمات القادمة والمتأخرة"""
    patient, err, code = _get_patient_or_404(current_user)
    if err:
        return err, code

    today = date.today()
    in_30 = today + timedelta(days=30)

    all_vacs = Vaccination.query.filter_by(patient_id=patient.id).all()

    upcoming = []
    overdue = []

    for v in all_vacs:
        if v.next_due_date:
            d = v.to_dict()
            if v.next_due_date < today:
                overdue.append(d)
            elif v.next_due_date <= in_30:
                upcoming.append(d)

    return jsonify({
        'success': True,
        'overdue': sorted(overdue, key=lambda x: x['next_due_date']),
        'upcoming': sorted(upcoming, key=lambda x: x['next_due_date']),
    })


# ── تطعيمات أفراد الأسرة (الأطفال) ─────────────────────────────────────────────

@vaccination_bp.route('/family-member/<int:member_id>', methods=['GET'])
@token_required
def list_member_vaccinations(current_user, member_id):
    """جلب تطعيمات فرد من الأسرة"""
    member = _check_member_access(current_user, member_id)
    if isinstance(member, tuple):
        return member

    records = FamilyMemberHealthRecord.query.filter_by(
        member_id=member_id, record_type='vaccination'
    ).order_by(FamilyMemberHealthRecord.date.desc()).all()

    # حدد الجدول المقترح للطفل
    schedule = _get_child_schedule(member)

    return jsonify({
        'success': True,
        'member': member.to_dict(),
        'vaccinations': [r.to_dict() for r in records],
        'schedule': schedule,
    })


@vaccination_bp.route('/family-member/<int:member_id>', methods=['POST'])
@token_required
def add_member_vaccination(current_user, member_id):
    """إضافة تطعيم لفرد من الأسرة"""
    member = _check_member_access(current_user, member_id)
    if isinstance(member, tuple):
        return member

    data = request.get_json()
    if not data or not data.get('vaccine_name') or not data.get('date'):
        return jsonify({'success': False, 'error': 'اسم اللقاح والتاريخ مطلوبان'}), 400

    rec = FamilyMemberHealthRecord(
        member_id=member_id,
        record_type='vaccination',
        title=data['vaccine_name'],
        description=data.get('disease_prevented', ''),
        date=_parse_date(data['date']),
        next_due_date=_parse_date(data.get('next_due_date')),
        result=data.get('reaction'),
        doctor_name=data.get('provider'),
        hospital_name=data.get('hospital_name'),
    )
    db.session.add(rec)
    db.session.commit()

    if rec.next_due_date:
        db.session.add(Notification(
            user_id=current_user.id,
            title=f'تطعيم {member.first_name} القادم',
            message=f'موعد لقاح {data["vaccine_name"]} لـ{member.first_name}: {rec.next_due_date.strftime("%Y-%m-%d")}',
            type='vaccination',
        ))
        db.session.commit()

    return jsonify({'success': True, 'record': rec.to_dict()}), 201


@vaccination_bp.route('/child-schedule/<int:member_id>', methods=['GET'])
@token_required
def get_child_schedule(current_user, member_id):
    """جدول تطعيمات الطفل المقترح"""
    member = _check_member_access(current_user, member_id)
    if isinstance(member, tuple):
        return member

    schedule = _get_child_schedule(member)
    return jsonify({'success': True, 'member': member.to_dict(), 'schedule': schedule})


# ── Helpers ──────────────────────────────────────────────────────────────────────

def _parse_date(val):
    if not val:
        return None
    try:
        return date.fromisoformat(str(val)[:10])
    except (ValueError, TypeError):
        return None


def _check_member_access(current_user, member_id):
    member = FamilyMember.query.get(member_id)
    if not member:
        return jsonify({'success': False, 'error': 'الفرد غير موجود'}), 404
    group = FamilyGroup.query.filter_by(id=member.group_id, owner_user_id=current_user.id).first()
    if not group:
        return jsonify({'success': False, 'error': 'غير مصرح'}), 403
    return member


def _get_child_schedule(member):
    """احسب جدول التطعيمات للطفل مع الحالة"""
    today = date.today()
    age_months = None
    if member.date_of_birth:
        delta = today - member.date_of_birth
        age_months = delta.days // 30

    # التطعيمات المأخوذة فعلاً (من سجلات الأسرة)
    taken_records = FamilyMemberHealthRecord.query.filter_by(
        member_id=member.id, record_type='vaccination'
    ).all()
    taken_names = {r.title for r in taken_records}

    schedule = []
    for item in CHILD_SCHEDULE:
        if age_months is None or item['age_months'] <= age_months + 3:
            status = 'taken' if item['vaccine_name'] in taken_names else (
                'overdue' if age_months and item['age_months'] < age_months - 1 else 'upcoming'
            )
            due_date = None
            if member.date_of_birth:
                due_date = (member.date_of_birth + timedelta(days=item['age_months'] * 30)).isoformat()
            schedule.append({
                **item,
                'status': status,
                'due_date': due_date,
            })

    return schedule
