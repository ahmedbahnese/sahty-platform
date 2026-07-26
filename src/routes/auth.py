from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import jwt
import datetime
from src.models.user import db, User
from src.models.patient import Patient
from src.models.doctor import Doctor
from src.models.admin import Admin, SystemOwner, AuditLog
import os

auth_bp = Blueprint('auth', __name__)

# JWT Secret Key
JWT_SECRET = os.environ.get('JWT_SECRET', os.environ.get('SESSION_SECRET', 'your-secret-key-here'))

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
            current_user = User.query.get(current_user_id)
            if not current_user:
                return jsonify({'message': 'مستخدم غير صالح'}), 401
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

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        required_fields = ['email', 'password', 'user_type', 'first_name', 'last_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'حقل {field} مطلوب'}), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'البريد الإلكتروني مستخدم بالفعل'}), 400
        hashed_password = generate_password_hash(data['password'])
        new_user = User(
            email=data['email'],
            password_hash=hashed_password,
            user_type=data['user_type'],
            is_active=True
        )
        db.session.add(new_user)
        db.session.flush()
        if data['user_type'] == 'patient':
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
        elif data['user_type'] == 'doctor':
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
        elif data['user_type'] in ['admin', 'super_admin']:
            admin = Admin(
                user_id=new_user.id,
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone=data.get('phone', ''),
                admin_type=data.get('admin_type', 'system_admin')
            )
            db.session.add(admin)
        db.session.commit()
        try:
            audit_log = AuditLog(
                user_id=new_user.id,
                user_email=new_user.email,
                user_type=new_user.user_type,
                action='user_registration',
                description=f'تسجيل مستخدم جديد: {data["first_name"]} {data["last_name"]}',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(audit_log)
            db.session.commit()
        except Exception:
            pass
        return jsonify({
            'message': 'تم التسجيل بنجاح',
            'user_id': new_user.id,
            'user_type': new_user.user_type
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'خطأ في التسجيل: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data.get('email') or not data.get('password'):
            return jsonify({'message': 'البريد الإلكتروني وكلمة المرور مطلوبان'}), 400
        user = User.query.filter_by(email=data['email']).first()
        if not user or not check_password_hash(user.password_hash, data['password']):
            return jsonify({'message': 'بيانات الدخول غير صحيحة'}), 401
        if not user.is_active:
            return jsonify({'message': 'الحساب غير مفعل'}), 401
        token_payload = {
            'user_id': user.id,
            'email': user.email,
            'user_type': user.user_type,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(token_payload, JWT_SECRET, algorithm='HS256')
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
        return jsonify({
            'message': 'تم تسجيل الدخول بنجاح',
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'user_type': user.user_type,
                'is_active': user.is_active,
                'profile': profile_data
            }
        }), 200
    except Exception as e:
        return jsonify({'message': f'خطأ في تسجيل الدخول: {str(e)}'}), 500

@auth_bp.route('/owner-login', methods=['POST'])
def owner_login():
    try:
        data = request.get_json()
        if (data.get('email') == 'Ahmedbahnese@yahoo.com' and
                data.get('password') == 'Bahnasy123'):
            owner = SystemOwner.query.first()
            if not owner:
                owner = SystemOwner()
                db.session.add(owner)
                db.session.commit()
            user = User.query.filter_by(email='Ahmedbahnese@yahoo.com').first()
            if not user:
                user = User(
                    email='Ahmedbahnese@yahoo.com',
                    password_hash=generate_password_hash('Bahnasy123'),
                    user_type='super_admin',
                    is_active=True
                )
                db.session.add(user)
                db.session.flush()
                admin = Admin(
                    user_id=user.id,
                    first_name='أحمد حامد',
                    last_name='أحمد بهنسي',
                    email='Ahmedbahnese@yahoo.com',
                    phone='01063299450',
                    admin_type='super_admin',
                    is_super_admin=True,
                    can_access_dashboard=True,
                    can_manage_users=True,
                    can_manage_doctors=True,
                    can_manage_hospitals=True,
                    can_manage_content=True,
                    can_view_reports=True,
                    can_manage_system_settings=True
                )
                db.session.add(admin)
                db.session.commit()
            token_payload = {
                'user_id': user.id,
                'email': user.email,
                'user_type': 'super_admin',
                'is_owner': True,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }
            token = jwt.encode(token_payload, JWT_SECRET, algorithm='HS256')
            user.last_login = datetime.datetime.utcnow()
            user.login_count = (user.login_count or 0) + 1
            db.session.commit()
            return jsonify({
                'message': 'مرحباً بك أحمد بهنسي - مالك النظام',
                'token': token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'user_type': 'super_admin',
                    'is_owner': True,
                    'owner_info': owner.to_dict()
                }
            }), 200
        else:
            return jsonify({'message': 'بيانات الدخول غير صحيحة'}), 401
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
        return jsonify({
            'user': {
                'id': current_user.id,
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
            pass
        return jsonify({'message': 'تم تسجيل الخروج بنجاح'}), 200
    except Exception as e:
        return jsonify({'message': f'خطأ في تسجيل الخروج: {str(e)}'}), 500

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
        db.session.commit()
        return jsonify({'message': 'تم تغيير كلمة المرور بنجاح'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'خطأ في تغيير كلمة المرور: {str(e)}'}), 500
