"""
مسارات API للمستشفيات وخدمات الطوارئ.
GET    /api/hospitals                    — قائمة / بحث
GET    /api/hospitals/<id>              — تفاصيل مستشفى
POST   /api/hospitals                   — إضافة (admin)
PUT    /api/hospitals/<id>              — تحديث (admin)
DELETE /api/hospitals/<id>              — حذف ناعم (admin)
GET    /api/hospitals/<id>/departments  — أقسام مستشفى
GET    /api/emergency-services          — خدمات الطوارئ
POST   /api/hospitals/<id>/review       — إضافة تقييم (patient)
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from src.models.user import db
from src.models.hospital import Hospital, HospitalDepartment, EmergencyService, HospitalReview
from src.models.egypt_healthcare import EgyptFacility
from src.models.patient import Patient
from src.routes.auth import token_required

hospital_bp = Blueprint('hospital', __name__, url_prefix='/api/hospitals')
emergency_service_bp = Blueprint('emergency_service', __name__, url_prefix='/api/emergency-services')


# ────────────────────────────────────────────
# قائمة المستشفيات / بحث
# ────────────────────────────────────────────

@hospital_bp.route('', methods=['GET'])
def list_hospitals():
    """
    بحث عن مستشفيات.
    ?search=اسم  ?city=مدينة  ?type=public|private|specialized
    ?emergency=1  ?verified=1  ?page=1  ?per_page=20
    """
    search    = request.args.get('search', '').strip()
    city      = request.args.get('city', '').strip()
    h_type    = request.args.get('type', '').strip()
    emergency = request.args.get('emergency') == '1'
    verified  = request.args.get('verified') == '1'
    page      = request.args.get('page', 1, type=int)
    per_page  = min(request.args.get('per_page', 20, type=int), 50)

    query = Hospital.query.filter_by(is_active=True)

    if search:
        query = query.filter(or_(
            Hospital.name.ilike(f'%{search}%'),
            Hospital.name_en.ilike(f'%{search}%'),
        ))
    if city:
        query = query.filter(Hospital.city.ilike(f'%{city}%'))
    if h_type:
        query = query.filter_by(type=h_type)
    if emergency:
        query = query.filter_by(has_emergency=True)
    if verified:
        query = query.filter_by(is_verified=True)

    # Include the imported Egyptian directory without changing the existing
    # hospital table. Both sources are normalized to the response shape used
    # by the current frontend.
    legacy_hospitals = query.order_by(Hospital.rating.desc()).all()
    facility_query = EgyptFacility.query
    if search:
        facility_query = facility_query.filter(or_(
            EgyptFacility.name_ar.ilike(f'%{search}%'),
            EgyptFacility.name_en.ilike(f'%{search}%'),
            EgyptFacility.full_address.ilike(f'%{search}%'),
        ))
    if city:
        facility_query = facility_query.filter(or_(
            EgyptFacility.city.has(name_ar=city),
            EgyptFacility.city.has(name_en=city),
            EgyptFacility.governorate.has(name_ar=city),
            EgyptFacility.governorate.has(name_en=city),
        ))
    if h_type == 'private':
        facility_query = facility_query.filter(
            EgyptFacility.ownership_type.has(name_en='Private')
        )
    elif h_type == 'public':
        facility_query = facility_query.filter(
            or_(
                EgyptFacility.ownership_type.has(name_en='Government'),
                EgyptFacility.ownership_type.has(name_en='University'),
            )
        )
    if emergency:
        facility_query = facility_query.filter(EgyptFacility.has_emergency_dept.is_(True))

    imported_hospitals = []
    for facility in facility_query.order_by(EgyptFacility.name_ar).all():
        imported_hospitals.append({
            'id': -facility.id,
            'name': facility.name_ar,
            'name_en': facility.name_en,
            'type': 'private' if facility.ownership_type.name_en == 'Private' else 'public',
            'facility_type': facility.facility_type.name_ar,
            'phone': facility.phone_numbers or '',
            'email': None,
            'website': facility.google_maps_url,
            'address': facility.full_address or '',
            'city': facility.city.name_ar,
            'district': facility.district,
            'latitude': facility.latitude,
            'longitude': facility.longitude,
            'has_emergency': facility.has_emergency_dept,
            'emergency_phone': facility.phone_numbers if facility.has_emergency_dept else None,
            'is_24_hours': facility.is_24_hours,
            'is_verified': True,
            'is_imported': True,
            'data_source': facility.data_source,
            'google_maps_url': facility.google_maps_url,
            'rating': 0,
            'total_reviews': 0,
            'specializations': None,
            'services': None,
            'facilities': None,
            'total_beds': None,
            'available_beds': None,
            'icu_beds': None,
            'available_icu_beds': None,
            'accepted_insurance': None,
            'working_hours': None,
        })

    all_hospitals = [h.to_dict() for h in legacy_hospitals] + imported_hospitals
    total = len(all_hospitals)
    start = (page - 1) * per_page
    hospitals = all_hospitals[start:start + per_page]

    return jsonify({
        'hospitals': hospitals,
        'total':     total,
        'page':      page,
        'per_page':  per_page,
        'pages':     (total + per_page - 1) // per_page,
    }), 200


# ────────────────────────────────────────────
# تفاصيل مستشفى
# ────────────────────────────────────────────

@hospital_bp.route('/<int:hospital_id>', methods=['GET'])
def get_hospital(hospital_id):
    hospital = db.session.get(Hospital, hospital_id)
    if not hospital or not hospital.is_active:
        return jsonify({'message': 'المستشفى غير موجود'}), 404

    data = hospital.to_dict()
    data['departments'] = [d.to_dict() for d in
                           HospitalDepartment.query.filter_by(hospital_id=hospital_id, is_active=True).all()]
    # آخر 5 تقييمات معتمدة
    reviews = HospitalReview.query.filter_by(hospital_id=hospital_id, is_approved=True)\
        .order_by(HospitalReview.created_at.desc()).limit(5).all()
    data['reviews'] = [r.to_dict() for r in reviews]
    return jsonify({'hospital': data}), 200


# ────────────────────────────────────────────
# إضافة مستشفى (admin فقط)
# ────────────────────────────────────────────

@hospital_bp.route('', methods=['POST'])
@token_required
def create_hospital(current_user):
    if current_user.user_type not in ('admin', 'super_admin'):
        return jsonify({'message': 'غير مصرح'}), 403

    data = request.get_json(silent=True) or {}
    required = ['name', 'type', 'phone', 'address', 'city']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'message': f'الحقول المطلوبة: {", ".join(missing)}'}), 400

    hospital = Hospital(
        name=data['name'],
        name_en=data.get('name_en'),
        type=data['type'],
        phone=data['phone'],
        email=data.get('email'),
        website=data.get('website'),
        address=data['address'],
        city=data['city'],
        district=data.get('district'),
        postal_code=data.get('postal_code'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        specializations=data.get('specializations'),
        services=data.get('services'),
        facilities=data.get('facilities'),
        has_emergency=data.get('has_emergency', False),
        emergency_phone=data.get('emergency_phone'),
        is_24_hours=data.get('is_24_hours', False),
        total_beds=data.get('total_beds'),
        available_beds=data.get('available_beds'),
        icu_beds=data.get('icu_beds'),
        available_icu_beds=data.get('available_icu_beds'),
        accepted_insurance=data.get('accepted_insurance'),
        working_hours=data.get('working_hours'),
        is_active=True,
        is_verified=data.get('is_verified', False),
    )
    db.session.add(hospital)
    db.session.commit()
    return jsonify({'hospital': hospital.to_dict()}), 201


# ────────────────────────────────────────────
# تحديث مستشفى (admin)
# ────────────────────────────────────────────

@hospital_bp.route('/<int:hospital_id>', methods=['PUT'])
@token_required
def update_hospital(current_user, hospital_id):
    if current_user.user_type not in ('admin', 'super_admin'):
        return jsonify({'message': 'غير مصرح'}), 403

    hospital = db.session.get(Hospital, hospital_id)
    if not hospital:
        return jsonify({'message': 'المستشفى غير موجود'}), 404

    data = request.get_json(silent=True) or {}
    updatable = [
        'name', 'name_en', 'type', 'phone', 'email', 'website',
        'address', 'city', 'district', 'postal_code', 'latitude', 'longitude',
        'specializations', 'services', 'facilities', 'has_emergency',
        'emergency_phone', 'is_24_hours', 'total_beds', 'available_beds',
        'icu_beds', 'available_icu_beds', 'accepted_insurance', 'working_hours',
        'is_active', 'is_verified',
    ]
    for field in updatable:
        if field in data:
            setattr(hospital, field, data[field])

    db.session.commit()
    return jsonify({'hospital': hospital.to_dict()}), 200


# ────────────────────────────────────────────
# حذف ناعم (admin)
# ────────────────────────────────────────────

@hospital_bp.route('/<int:hospital_id>', methods=['DELETE'])
@token_required
def delete_hospital(current_user, hospital_id):
    if current_user.user_type not in ('admin', 'super_admin'):
        return jsonify({'message': 'غير مصرح'}), 403

    hospital = db.session.get(Hospital, hospital_id)
    if not hospital:
        return jsonify({'message': 'المستشفى غير موجود'}), 404

    hospital.is_active = False
    db.session.commit()
    return jsonify({'message': 'تم حذف المستشفى'}), 200


# ────────────────────────────────────────────
# أقسام المستشفى
# ────────────────────────────────────────────

@hospital_bp.route('/<int:hospital_id>/departments', methods=['GET'])
def list_departments(hospital_id):
    hospital = db.session.get(Hospital, hospital_id)
    if not hospital:
        return jsonify({'message': 'المستشفى غير موجود'}), 404
    depts = HospitalDepartment.query.filter_by(hospital_id=hospital_id, is_active=True).all()
    return jsonify({'departments': [d.to_dict() for d in depts]}), 200


@hospital_bp.route('/<int:hospital_id>/departments', methods=['POST'])
@token_required
def create_department(current_user, hospital_id):
    if current_user.user_type not in ('admin', 'super_admin'):
        return jsonify({'message': 'غير مصرح'}), 403

    hospital = db.session.get(Hospital, hospital_id)
    if not hospital:
        return jsonify({'message': 'المستشفى غير موجود'}), 404

    data = request.get_json(silent=True) or {}
    if not data.get('name'):
        return jsonify({'message': 'اسم القسم مطلوب'}), 400

    dept = HospitalDepartment(
        hospital_id=hospital_id,
        name=data['name'],
        name_en=data.get('name_en'),
        description=data.get('description'),
        phone=data.get('phone'),
        extension=data.get('extension'),
        floor=data.get('floor'),
        wing=data.get('wing'),
        services=data.get('services'),
        equipment=data.get('equipment'),
        head_of_department=data.get('head_of_department'),
        total_doctors=data.get('total_doctors', 0),
        total_nurses=data.get('total_nurses', 0),
        working_hours=data.get('working_hours'),
    )
    db.session.add(dept)
    db.session.commit()
    return jsonify({'department': dept.to_dict()}), 201


# ────────────────────────────────────────────
# تقييم مستشفى (patients)
# ────────────────────────────────────────────

@hospital_bp.route('/<int:hospital_id>/review', methods=['POST'])
@token_required
def review_hospital(current_user, hospital_id):
    if current_user.user_type != 'patient':
        return jsonify({'message': 'التقييم متاح للمرضى فقط'}), 403

    hospital = db.session.get(Hospital, hospital_id)
    if not hospital:
        return jsonify({'message': 'المستشفى غير موجود'}), 404

    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'ملف المريض غير موجود'}), 404

    data = request.get_json(silent=True) or {}
    overall = data.get('overall_rating')
    if not overall or not isinstance(overall, int) or not (1 <= overall <= 5):
        return jsonify({'message': 'التقييم العام مطلوب (1-5)'}), 400

    # منع التقييم المكرر
    existing = HospitalReview.query.filter_by(hospital_id=hospital_id, patient_id=patient.id).first()
    if existing:
        # تحديث التقييم الموجود
        existing.overall_rating = overall
        existing.cleanliness_rating = data.get('cleanliness_rating')
        existing.staff_rating = data.get('staff_rating')
        existing.facilities_rating = data.get('facilities_rating')
        existing.waiting_time_rating = data.get('waiting_time_rating')
        existing.review_title = data.get('review_title')
        existing.review_text = data.get('review_text')
        existing.would_recommend = data.get('would_recommend')
        review = existing
    else:
        review = HospitalReview(
            hospital_id=hospital_id,
            patient_id=patient.id,
            overall_rating=overall,
            cleanliness_rating=data.get('cleanliness_rating'),
            staff_rating=data.get('staff_rating'),
            facilities_rating=data.get('facilities_rating'),
            waiting_time_rating=data.get('waiting_time_rating'),
            review_title=data.get('review_title'),
            review_text=data.get('review_text'),
            would_recommend=data.get('would_recommend'),
        )
        db.session.add(review)

    # إعادة حساب متوسط التقييم
    db.session.flush()
    all_reviews = HospitalReview.query.filter_by(hospital_id=hospital_id, is_approved=True).all()
    if all_reviews:
        hospital.rating = round(sum(r.overall_rating for r in all_reviews) / len(all_reviews), 1)
        hospital.total_reviews = len(all_reviews)

    db.session.commit()
    return jsonify({'message': 'شكراً على تقييمك', 'review': review.to_dict()}), 200 if existing else 201


# ────────────────────────────────────────────
# خدمات الطوارئ
# ────────────────────────────────────────────

@emergency_service_bp.route('', methods=['GET'])
def list_emergency_services():
    city = request.args.get('city', '').strip()
    svc_type = request.args.get('type', '').strip()

    query = EmergencyService.query.filter_by(is_active=True)
    if city:
        query = query.filter(EmergencyService.city.ilike(f'%{city}%'))
    if svc_type:
        query = query.filter_by(type=svc_type)

    services = query.order_by(EmergencyService.type).all()
    return jsonify({'services': [s.to_dict() for s in services]}), 200
