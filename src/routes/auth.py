from flask import Blueprint, request, jsonify, g
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import jwt
import datetime
import hashlib
import secrets
from src.models.user import db, User, UserSession
from src.models.patient import Patient
from src.models.doctor import Doctor
from src.models.admin import Admin, AuditLog
from src.models.provider import PROVIDER_ROLES, ProviderRegistration
import os

auth_bp = Blueprint('auth', __name__)

# JWT Secret Key
JWT_SECRET = os.environ.get('JWT_SECRET', os.environ.get('SESSION_SECRET'))
if not JWT_SECRET:
    raise RuntimeError('SESSION_SECRET or JWT_SECRET must be configured before starting the API')
SESSION_TTL = datetime.timedelta(hours=24)
PUBLIC_ROLES = {'patient', 'doctor', *PROVIDER_ROLES.keys()}
ROLE_LABELS = {
    'patient': 'مستخدم',
    'doctor': 'طبيب',
    **PROVIDER_ROLES,
}


def _hash_token(token):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def _issue_session(user):
    """Create a signed token and a server-side session record."""
    session_id = secrets.token_urlsafe(32)
    expires_at = datetime.datetime.utcnow() + SESSION_TTL
    token_payload = {
        'user_id': user.id,
        'email': user.email,
        'user_type': user.user_type,
        'jti': session_id,
        'exp': expires_at,
    }
    token = jwt.encode(token_payload, JWT_SECRET, algorithm='HS256')
    user_session = UserSession(
        user_id=user.id,
        jwt_id=session_id,
        token_hash=_hash_token(token),
        expires_at=expires_at,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
    )
    db.session.add(user_session)
    return token, user_session

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token مفقود'}), 401
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user_id = data['user_id']
            current_user = db.session.get(User, current_user_id)
            current_session = UserSession.query.filter_by(
                token_hash=_hash_token(token),
                user_id=current_user_id,
            ).first()
            if not current_user or not current_session or not current_session.is_valid:
                return jsonify({'message': 'مستخدم غير صالح'}), 401
            if data.get('jti') != current_session.jwt_id:
                return jsonify({'message': 'جلسة غير صالحة'}), 401
            if not current_user.is_active:
                return jsonify({'message': 'الحساب غير مفعل'}), 401
            current_session.last_seen_at = datetime.datetime.utcnow()
            g.current_session = current_session
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'انتهت صلاحية الجلسة'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token غير صالح'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.user_type not in ['admin', 'super_admin']:
            return jsonify({'message': 'غير مصرح لك بالوصول'}), 403
        return f(current_user, *args, **kwargs)
    return decorated


def role_required(*roles):
    """Restrict an endpoint to one or more user roles."""
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            if current_user.user_type not in roles:
                return jsonify({'message': 'غير مصرح لك بالوصول'}), 403
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json(silent=True) or {}
        required_fields = ['email', 'password', 'user_type', 'first_name', 'last_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'حقل {field} مطلوب'}), 400
        user_type = data['user_type']
        if user_type not in PUBLIC_ROLES:
            return jsonify({'message': 'نوع الحساب المطلوب غير متاح للتسجيل العام'}), 400
        if len(data['password']) < 8:
            return jsonify({'message': 'كلمة المرور يجب أن تكون 8 أحرف على الأقل'}), 400
        if user_type != 'patient':
            for field in ('legal_name', 'license_number', 'address', 'city'):
                if not data.get(field):
                    return jsonify({'message': f'حقل {field} مطلوب للحساب المهني'}), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'البريد الإلكتروني مستخدم بالفعل'}), 400
        username = (data.get('username') or data['email'].split('@')[0]).strip()
        if User.query.filter_by(username=username).first():
            return jsonify({'message': 'اسم المستخدم مستخدم بالفعل، اختر اسماً آخر'}), 400
        hashed_password = generate_password_hash(data['password'])
        new_user = User(
            username=username,
            email=data['email'],
            password_hash=hashed_password,
            user_type=user_type,
            is_active=user_type == 'patient'
        )
        db.session.add(new_user)
        db.session.flush()
        if user_type == 'patient':
            patient = Patient(
                user_id=new_user.id,
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone=data.get('phone', ''),
                date_of_birth=datetime.datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get('date_of_birth') else datetime.date.today(),
                gender=data.get('gender', ''),
                national_id=data.get('national_id', str(new_user.id))
            )
            db.session.add(patient)
        elif user_type == 'doctor':
            doctor = Doctor(
                user_id=new_user.id,
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone=data.get('phone', ''),
                license_number=data.get('license_number', f'LIC-{new_user.id}'),
                specialization=data.get('specialization', '')
            )
            db.session.add(doctor)
        if user_type != 'patient':
            provider = ProviderRegistration(
                user_id=new_user.id,
                provider_type=user_type,
                legal_name=data.get('legal_name') or f'{data["first_name"]} {data["last_name"]}',
                license_number=data['license_number'],
                phone=data.get('phone', ''),
                address=data['address'],
                city=data.get('city', ''),
                details={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'specialization': data.get('specialization'),
                    'website': data.get('website'),
                    'services': data.get('services'),
                    'id_card_image': data.get('id_card_image'),
                    'practice_license_image': data.get('practice_license_image'),
                },
            )
            db.session.add(provider)
        db.session.commit()
        try:
            audit_log = AuditLog(
                user_id=new_user.id,
                user_email=new_user.email,
                user_type=new_user.user_type,
                action='user_registration',
                description=f'تسجيل مستخدم جديد: {data["first_name"]} {data["last_name"]}',
                new_values={
                    'user_type': user_type,
                    'license_number': data.get('license_number'),
                    'legal_name': data.get('legal_name'),
                } if user_type != 'patient' else None,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(audit_log)
            db.session.commit()
        except Exception:
            pass
        response_data = {
            'message': (
                'تم استلام طلبك بنجاح، وستتمكن من تسجيل الدخول بعد اعتماد الإدارة '
                f'لحساب {ROLE_LABELS[user_type]}'
            ) if user_type != 'patient' else 'تم التسجيل بنجاح',
            'user_id': new_user.id,
            'user_type': new_user.user_type,
            'pending_review': user_type != 'patient'
        }
        if user_type == 'patient':
            response_data['token'], _ = _issue_session(new_user)
            db.session.commit()
            response_data['user'] = {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'user_type': new_user.user_type,
                'is_active': new_user.is_active,
                'profile': Patient.query.filter_by(user_id=new_user.id).first().to_dict()
            }
        return jsonify({
            **response_data
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'خطأ في التسجيل: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        identifier = data.get('identifier') or data.get('email')
        if not identifier or not data.get('password'):
            return jsonify({'message': 'اسم المستخدم أو الهاتف أو البريد الإلكتروني وكلمة المرور مطلوبة'}), 400
        user = User.query.filter(
            (User.email == identifier) |
            (User.username == identifier)
        ).first()
        if not user:
            patient = Patient.query.filter_by(phone=identifier).first()
            doctor = Doctor.query.filter_by(phone=identifier).first()
            related = patient or doctor
            user = User.query.get(related.user_id) if related else None
        if not user or not check_password_hash(user.password_hash, data['password']):
            return jsonify({'message': 'بيانات الدخول غير صحيحة'}), 401
        if not user.is_active:
            if user.user_type in PUBLIC_ROLES - {'patient'}:
                return jsonify({'message': 'الحساب بانتظار اعتماد الإدارة قبل تسجيل الدخول'}), 403
            return jsonify({'message': 'الحساب غير مفعل'}), 403
        token, _ = _issue_session(user)
        user.last_login = datetime.datetime.utcnow()
        user.login_count = (user.login_count or 0) + 1
        if user.user_type in ['admin', 'super_admin']:
            admin = Admin.query.filter_by(user_id=user.id).first()
            if admin:
                admin.last_login = datetime.datetime.utcnow()
                admin.login_count = (admin.login_count or 0) + 1
        db.session.commit()
        profile_data = {}
        if user.user_type == 'patient':
            patient = Patient.query.filter_by(user_id=user.id).first()
            if patient:
                profile_data = patient.to_dict()
        elif user.user_type == 'doctor':
            doctor = Doctor.query.filter_by(user_id=user.id).first()
            if doctor:
                profile_data = doctor.to_dict()
        elif user.user_type in ['admin', 'super_admin']:
            admin = Admin.query.filter_by(user_id=user.id).first()
            if admin:
                profile_data = admin.to_dict()
        elif user.user_type in PUBLIC_ROLES - {'patient', 'doctor'}:
            provider = ProviderRegistration.query.filter_by(user_id=user.id).first()
            if provider:
                profile_data = provider.to_dict()
        return jsonify({
            'message': 'تم تسجيل الدخول بنجاح',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
                'is_active': user.is_active,
                'profile': profile_data
            }
        }), 200
    except Exception as e:
        return jsonify({'message': f'خطأ في تسجيل الدخول: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    try:
        profile_data = {}
        if current_user.user_type == 'patient':
            patient = Patient.query.filter_by(user_id=current_user.id).first()
            if patient:
                profile_data = patient.to_dict()
        elif current_user.user_type == 'doctor':
            doctor = Doctor.query.filter_by(user_id=current_user.id).first()
            if doctor:
                profile_data = doctor.to_dict()
        elif current_user.user_type in ['admin', 'super_admin']:
            admin = Admin.query.filter_by(user_id=current_user.id).first()
            if admin:
                profile_data = admin.to_dict()
        elif current_user.user_type in PUBLIC_ROLES - {'patient', 'doctor'}:
            provider = ProviderRegistration.query.filter_by(user_id=current_user.id).first()
            if provider:
                profile_data = provider.to_dict()
        return jsonify({
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'email': current_user.email,
                'user_type': current_user.user_type,
                'is_active': current_user.is_active,
                'last_login': current_user.last_login.isoformat() if current_user.last_login else None,
                'profile': profile_data
            }
        }), 200
    except Exception as e:
        return jsonify({'message': f'خطأ في جلب الملف الشخصي: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    try:
        current_session = getattr(g, 'current_session', None)
        if current_session:
            current_session.revoked_at = datetime.datetime.utcnow()
            db.session.commit()

        # Session invalidation is durable even if audit logging is unavailable.
        try:
            audit_log = AuditLog(
                user_id=current_user.id,
                user_email=current_user.email,
                user_type=current_user.user_type,
                action='user_logout',
                description='تسجيل خروج',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(audit_log)
            db.session.commit()
        except Exception:
            db.session.rollback()
        return jsonify({'message': 'تم تسجيل الخروج بنجاح'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'خطأ في تسجيل الخروج: {str(e)}'}), 500

@auth_bp.route('/doctors', methods=['GET'])
@token_required
def list_doctors(current_user):
    """
    قائمة الأطباء النشطين — للمرضى عند حجز المواعيد.
    يُرجع فقط الحقول الضرورية لواجهة الحجز (لا بيانات حساسة).
    """
    from src.models.doctor import Doctor
    doctors = Doctor.query.filter_by(is_active=True).all()
    safe = [
        {
            'id':                   d.id,
            'first_name':           d.first_name,
            'last_name':            d.last_name,
            'specialization':       d.specialization,
            'sub_specialization':   d.sub_specialization,
            'clinic_name':          d.clinic_name,
            'clinic_address':       d.clinic_address,
            'consultation_fee':     d.consultation_fee,
            'consultation_duration': d.consultation_duration,
            'available_for_telemedicine': d.available_for_telemedicine,
            'rating':               d.rating,
            'total_reviews':        d.total_reviews,
            'is_verified':          d.is_verified,
        }
        for d in doctors
    ]
    return jsonify({'doctors': safe}), 200


@auth_bp.route('/patients', methods=['GET'])
@token_required
def list_patients(current_user):
    """
    قائمة المرضى — للأطباء عند إنشاء الوصفات.
    يُرجع فقط الحقول الضرورية لتعريف المريض (لا رقم هوية ولا بيانات حساسة).
    مقيد بالأطباء والمديرين فقط.
    """
    if current_user.user_type not in ('doctor', 'admin', 'super_admin'):
        return jsonify({'message': 'غير مصرح'}), 403
    from src.models.patient import Patient
    from src.models.appointment import Appointment
    from src.models.doctor import Doctor

    # الأطباء يرون مرضاهم فقط (من لديهم موعد سابق أو حالي معهم)
    if current_user.user_type == 'doctor':
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if not doctor:
            return jsonify({'patients': []}), 200
        patient_ids = db.session.query(Appointment.patient_id)\
            .filter_by(doctor_id=doctor.id).distinct().all()
        patient_ids = [pid for (pid,) in patient_ids]
        patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()
    else:
        patients = Patient.query.all()

    safe = [
        {
            'id':         p.id,
            'first_name': p.first_name,
            'last_name':  p.last_name,
            'phone':      p.phone,
            'gender':     p.gender,
        }
        for p in patients
    ]
    return jsonify({'patients': safe}), 200


@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    try:
        data = request.get_json()
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'message': 'كلمة المرور الحالية والجديدة مطلوبتان'}), 400
        if not check_password_hash(current_user.password_hash, data['current_password']):
            return jsonify({'message': 'كلمة المرور الحالية غير صحيحة'}), 400
        current_user.password_hash = generate_password_hash(data['new_password'])
        UserSession.query.filter(
            UserSession.user_id == current_user.id,
            UserSession.revoked_at.is_(None),
        ).update({'revoked_at': datetime.datetime.utcnow()})
        db.session.commit()
        return jsonify({'message': 'تم تغيير كلمة المرور بنجاح'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'خطأ في تغيير كلمة المرور: {str(e)}'}), 500
