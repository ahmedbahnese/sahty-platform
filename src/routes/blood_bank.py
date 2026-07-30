"""
مسارات API لبنك الدم
يشمل: تسجيل المتبرعين، طلبات الدم، الاستجابات، المخزون، الإحصائيات
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from sqlalchemy import or_
from src.models.user import db, User
from src.models.patient import Patient
from src.models.blood_bank import BloodDonor, BloodRequest, BloodRequestResponse, BloodDonation, BloodInventory
from src.models.notification import Notification
from src.routes.auth import token_required

blood_bank_bp = Blueprint('blood_bank', __name__, url_prefix='/api/blood-bank')

COMPATIBLE_DONORS = {
    'A+':  ['A+', 'A-', 'O+', 'O-'],
    'A-':  ['A-', 'O-'],
    'B+':  ['B+', 'B-', 'O+', 'O-'],
    'B-':  ['B-', 'O-'],
    'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
    'AB-': ['A-', 'B-', 'AB-', 'O-'],
    'O+':  ['O+', 'O-'],
    'O-':  ['O-'],
}

# ────────────────────────────────────────────
# الإحصائيات العامة
# ────────────────────────────────────────────

@blood_bank_bp.route('/stats', methods=['GET'])
def get_stats():
    """إحصائيات بنك الدم العامة"""
    total_donors     = BloodDonor.query.filter_by(is_eligible=True).count()
    active_requests  = BloodRequest.query.filter_by(status='active').count()
    total_donations  = BloodDonation.query.filter_by(status='completed').count()
    critical_requests = BloodRequest.query.filter_by(status='active', urgency_level='critical').count()

    # إحصائيات حسب فصيلة الدم
    blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    by_type = {}
    for bt in blood_types:
        donors_count   = BloodDonor.query.filter_by(blood_type=bt, is_eligible=True).count()
        requests_count = BloodRequest.query.filter_by(blood_type=bt, status='active').count()
        by_type[bt] = {'donors': donors_count, 'requests': requests_count}

    return jsonify({
        'total_donors':     total_donors,
        'active_requests':  active_requests,
        'total_donations':  total_donations,
        'critical_requests': critical_requests,
        'by_blood_type':    by_type,
    }), 200


# ────────────────────────────────────────────
# المتبرعون
# ────────────────────────────────────────────

@blood_bank_bp.route('/donors', methods=['GET'])
def list_donors():
    """قائمة المتبرعين (بحث حسب فصيلة الدم والمدينة)"""
    blood_type = request.args.get('blood_type')
    city       = request.args.get('city')
    emergency  = request.args.get('emergency') == '1'

    query = BloodDonor.query.filter_by(is_eligible=True)

    if blood_type:
        query = query.filter_by(blood_type=blood_type)
    if city:
        query = query.filter(BloodDonor.city.ilike(f'%{city}%'))
    if emergency:
        query = query.filter_by(available_for_emergency=True)

    donors = query.order_by(BloodDonor.created_at.desc()).limit(100).all()

    # نُخفي المعلومات الشخصية ونُظهر فقط ما يلزم للتواصل
    result = []
    for d in donors:
        patient = Patient.query.get(d.patient_id)
        result.append({
            'id':           d.id,
            'blood_type':   d.blood_type,
            'city':         d.city,
            'district':     d.district,
            'is_eligible':  d.is_eligible,
            'available_for_emergency': d.available_for_emergency,
            'last_donation_date':  d.last_donation_date.isoformat() if d.last_donation_date else None,
            'next_eligible_date':  d.next_eligible_date.isoformat() if d.next_eligible_date else None,
            'donor_name':   f"{patient.first_name} {patient.last_name[0]}." if patient else 'متبرع',
        })

    return jsonify({'donors': result, 'total': len(result)}), 200


@blood_bank_bp.route('/donors/me', methods=['GET'])
@token_required
def get_my_donor_profile(current_user):
    """ملف المتبرع الخاص بي"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'success': False, 'error': 'ملف المريض غير موجود'}), 404

    donor = BloodDonor.query.filter_by(patient_id=patient.id).first()
    if not donor:
        return jsonify({'success': False, 'donor': None}), 200

    donations = BloodDonation.query.filter_by(donor_id=donor.id)\
        .order_by(BloodDonation.donation_date.desc()).limit(10).all()

    return jsonify({
        'success': True,
        'donor':     donor.to_dict(),
        'donations': [d.to_dict() for d in donations],
    }), 200


@blood_bank_bp.route('/donors/register', methods=['POST'])
@token_required
def register_donor(current_user):
    """تسجيل كمتبرع بالدم"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'success': False, 'error': 'يجب أن يكون لديك ملف مريض'}), 404

    # هل هو مسجل مسبقاً؟
    existing = BloodDonor.query.filter_by(patient_id=patient.id).first()
    if existing:
        return jsonify({'success': False, 'error': 'أنت مسجل مسبقاً كمتبرع'}), 409

    data = request.get_json() or {}
    required = ['blood_type', 'weight', 'age', 'city']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'success': False, 'error': f'الحقول المطلوبة: {", ".join(missing)}'}), 400

    # التحقق من الأهلية الأساسية
    weight = float(data['weight'])
    age    = int(data['age'])
    if weight < 50:
        return jsonify({'success': False, 'error': 'الوزن يجب ألا يقل عن 50 كيلوجرام'}), 400
    if age < 18 or age > 65:
        return jsonify({'success': False, 'error': 'يجب أن يكون العمر بين 18 و 65 سنة'}), 400

    donor = BloodDonor(
        patient_id=patient.id,
        blood_type=data['blood_type'],
        weight=weight,
        age=age,
        city=data['city'],
        district=data.get('district'),
        has_chronic_diseases=data.get('has_chronic_diseases', False),
        chronic_diseases_list=data.get('chronic_diseases_list'),
        current_medications=data.get('current_medications'),
        available_for_emergency=data.get('available_for_emergency', True),
        notification_enabled=data.get('notification_enabled', True),
        emergency_notification=data.get('emergency_notification', True),
        is_eligible=True,
    )
    db.session.add(donor)
    db.session.commit()
    return jsonify({'success': True, 'message': 'تم التسجيل كمتبرع بنجاح', 'donor': donor.to_dict()}), 201


@blood_bank_bp.route('/donors/me', methods=['PUT'])
@token_required
def update_donor_profile(current_user):
    """تحديث ملف المتبرع"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'success': False, 'error': 'ملف المريض غير موجود'}), 404

    donor = BloodDonor.query.filter_by(patient_id=patient.id).first()
    if not donor:
        return jsonify({'success': False, 'error': 'لم يتم التسجيل كمتبرع'}), 404

    data = request.get_json() or {}
    updatable = [
        'weight', 'age', 'city', 'district', 'has_chronic_diseases',
        'chronic_diseases_list', 'current_medications', 'available_for_emergency',
        'notification_enabled', 'emergency_notification',
    ]
    for field in updatable:
        if field in data:
            setattr(donor, field, data[field])

    db.session.commit()
    return jsonify({'success': True, 'donor': donor.to_dict()}), 200


# ────────────────────────────────────────────
# طلبات الدم
# ────────────────────────────────────────────

@blood_bank_bp.route('/requests', methods=['GET'])
def list_requests():
    """قائمة طلبات الدم النشطة"""
    blood_type = request.args.get('blood_type')
    city       = request.args.get('city')
    urgency    = request.args.get('urgency')

    query = BloodRequest.query.filter_by(status='active')
    if blood_type:
        query = query.filter_by(blood_type=blood_type)
    if city:
        query = query.filter(BloodRequest.city.ilike(f'%{city}%'))
    if urgency:
        query = query.filter_by(urgency_level=urgency)

    requests = query.order_by(
        BloodRequest.urgency_level.desc(),
        BloodRequest.created_at.desc()
    ).limit(100).all()

    return jsonify({'requests': [r.to_dict() for r in requests], 'total': len(requests)}), 200


@blood_bank_bp.route('/requests', methods=['POST'])
@token_required
def create_request(current_user):
    """إنشاء طلب دم جديد"""
    data = request.get_json() or {}
    required = ['blood_type', 'units_needed', 'urgency_level', 'patient_name',
                'hospital_name', 'contact_phone', 'needed_by_date']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'success': False, 'error': f'الحقول المطلوبة: {", ".join(missing)}'}), 400

    try:
        needed_by = datetime.fromisoformat(data['needed_by_date'])
    except ValueError:
        return jsonify({'success': False, 'error': 'صيغة التاريخ غير صحيحة (ISO 8601)'}), 400

    patient = Patient.query.filter_by(user_id=current_user.id).first()
    blood_request = BloodRequest(
        patient_id=patient.id if patient else None,
        blood_type=data['blood_type'],
        units_needed=int(data['units_needed']),
        urgency_level=data['urgency_level'],
        patient_name=data['patient_name'],
        patient_age=data.get('patient_age'),
        medical_condition=data.get('medical_condition'),
        hospital_name=data['hospital_name'],
        hospital_address=data.get('hospital_address'),
        contact_person=data.get('contact_person'),
        contact_phone=data['contact_phone'],
        city=data.get('city'),
        district=data.get('district'),
        needed_by_date=needed_by,
        description=data.get('description'),
        special_requirements=data.get('special_requirements'),
        status='active',
    )
    db.session.add(blood_request)
    db.session.flush()

    # إشعار المتبرعين المتوافقين في نفس المدينة
    compatible = COMPATIBLE_DONORS.get(data['blood_type'], [data['blood_type']])
    matching_donors = BloodDonor.query.filter(
        BloodDonor.blood_type.in_(compatible),
        BloodDonor.is_eligible == True,
        BloodDonor.notification_enabled == True,
    )
    if data.get('city'):
        matching_donors = matching_donors.filter(BloodDonor.city.ilike(f"%{data['city']}%"))

    urgency_label = {'critical': 'حرج جداً', 'urgent': 'عاجل', 'routine': 'عادي'}.get(data['urgency_level'], '')
    for donor in matching_donors.limit(50).all():
        donor_patient = Patient.query.get(donor.patient_id)
        if donor_patient:
            db.session.add(Notification(
                user_id=donor_patient.user_id,
                title=f'طلب دم {urgency_label} - {data["blood_type"]}',
                message=f'مريض في {data["hospital_name"]} يحتاج دم فصيلة {data["blood_type"]}. تواصل: {data["contact_phone"]}',
                type='blood_bank',
                reference_id=blood_request.id,
                reference_type='blood_request',
            ))

    db.session.commit()
    return jsonify({'success': True, 'message': 'تم إنشاء الطلب', 'request': blood_request.to_dict()}), 201


@blood_bank_bp.route('/requests/<int:request_id>', methods=['GET'])
def get_request(request_id):
    """تفاصيل طلب دم"""
    blood_request = BloodRequest.query.get_or_404(request_id)
    data = blood_request.to_dict()
    data['responses_count'] = BloodRequestResponse.query.filter_by(request_id=request_id).count()
    return jsonify({'request': data}), 200


@blood_bank_bp.route('/requests/<int:request_id>/respond', methods=['POST'])
@token_required
def respond_to_request(current_user, request_id):
    """الاستجابة لطلب دم (كمتبرع)"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'success': False, 'error': 'ملف المريض غير موجود'}), 404

    donor = BloodDonor.query.filter_by(patient_id=patient.id).first()
    if not donor:
        return jsonify({'success': False, 'error': 'يجب التسجيل أولاً كمتبرع'}), 403

    blood_request = BloodRequest.query.get_or_404(request_id)
    if blood_request.status != 'active':
        return jsonify({'success': False, 'error': 'الطلب لم يعد نشطاً'}), 400

    # هل استجاب مسبقاً؟
    existing = BloodRequestResponse.query.filter_by(
        request_id=request_id, donor_id=donor.id
    ).first()
    if existing:
        return jsonify({'success': False, 'error': 'لقد استجبت على هذا الطلب مسبقاً'}), 409

    data = request.get_json() or {}
    if not data.get('response_type'):
        return jsonify({'success': False, 'error': 'نوع الاستجابة مطلوب (willing/maybe/not_available)'}), 400

    response = BloodRequestResponse(
        request_id=request_id,
        donor_id=donor.id,
        response_type=data['response_type'],
        available_date=datetime.fromisoformat(data['available_date']) if data.get('available_date') else None,
        message=data.get('message'),
        status='pending',
    )
    db.session.add(response)

    # إشعار مقدم الطلب إن كان مستخدماً مسجلاً
    if blood_request.patient_id:
        req_patient = Patient.query.get(blood_request.patient_id)
        if req_patient:
            db.session.add(Notification(
                user_id=req_patient.user_id,
                title='استجابة لطلب الدم',
                message=f'متبرع بفصيلة {donor.blood_type} استجاب على طلبك. تواصل معه عبر الطلب.',
                type='blood_bank',
                reference_id=request_id,
                reference_type='blood_request',
            ))

    db.session.commit()
    return jsonify({'success': True, 'message': 'تم تسجيل استجابتك', 'response': response.to_dict()}), 201


@blood_bank_bp.route('/requests/<int:request_id>/close', methods=['POST'])
@token_required
def close_request(current_user, request_id):
    """إغلاق طلب الدم (من قِبل صاحبه أو المدير)"""
    blood_request = BloodRequest.query.get_or_404(request_id)

    patient = Patient.query.filter_by(user_id=current_user.id).first()
    is_owner = patient and blood_request.patient_id == patient.id
    is_admin = current_user.user_type in ('admin', 'super_admin')

    if not (is_owner or is_admin):
        return jsonify({'success': False, 'error': 'غير مصرح'}), 403

    data = request.get_json() or {}
    blood_request.status = data.get('status', 'fulfilled')
    db.session.commit()
    return jsonify({'success': True, 'message': 'تم إغلاق الطلب'}), 200


# ────────────────────────────────────────────
# المخزون
# ────────────────────────────────────────────

@blood_bank_bp.route('/inventory', methods=['GET'])
def get_inventory():
    """مخزون الدم في المستشفيات"""
    hospital_id = request.args.get('hospital_id', type=int)
    blood_type  = request.args.get('blood_type')

    query = BloodInventory.query
    if hospital_id:
        query = query.filter_by(hospital_id=hospital_id)
    if blood_type:
        query = query.filter_by(blood_type=blood_type)

    inventory = query.all()
    return jsonify({'inventory': [i.to_dict() for i in inventory], 'total': len(inventory)}), 200


# ────────────────────────────────────────────
# سجل تبرعاتي
# ────────────────────────────────────────────

@blood_bank_bp.route('/my-donations', methods=['GET'])
@token_required
def my_donations(current_user):
    """سجل التبرعات الخاص بي"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'donations': []}), 200

    donor = BloodDonor.query.filter_by(patient_id=patient.id).first()
    if not donor:
        return jsonify({'donations': []}), 200

    donations = BloodDonation.query.filter_by(donor_id=donor.id)\
        .order_by(BloodDonation.donation_date.desc()).all()

    return jsonify({'donations': [d.to_dict() for d in donations], 'total': len(donations)}), 200


@blood_bank_bp.route('/compatible-donors', methods=['GET'])
def compatible_donors():
    """البحث عن متبرعين متوافقين مع فصيلة معينة"""
    blood_type = request.args.get('blood_type', '')
    city       = request.args.get('city', '')

    compatible = COMPATIBLE_DONORS.get(blood_type, [blood_type])

    query = BloodDonor.query.filter(
        BloodDonor.blood_type.in_(compatible),
        BloodDonor.is_eligible == True,
        BloodDonor.available_for_emergency == True,
    )
    if city:
        query = query.filter(BloodDonor.city.ilike(f'%{city}%'))

    donors = query.limit(50).all()
    result = []
    for d in donors:
        patient = Patient.query.get(d.patient_id)
        result.append({
            'id':         d.id,
            'blood_type': d.blood_type,
            'city':       d.city,
            'district':   d.district,
            'donor_name': f"{patient.first_name} {patient.last_name[0]}." if patient else 'متبرع',
        })

    return jsonify({'donors': result, 'total': len(result), 'compatible_types': compatible}), 200
