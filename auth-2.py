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

auth_bp = Blueprint(\'auth\', __name__)

# JWT Secret Key (في الإنتاج يجب أن يكون في متغير بيئة)
JWT_SECRET = os.environ.get(\'JWT_SECRET\', \'your-secret-key-here\')

def token_required(f):
    """
    Decorator للتحقق من صحة JWT Token.

    يتطلب وجود Token صالح في رأس الطلب (Authorization: Bearer <token>).
    إذا كان Token غير صالح أو منتهي الصلاحية، يعيد استجابة خطأ 401.

    Args:
        f (function): الدالة التي سيتم تطبيق الـ decorator عليها.

    Returns:
        function: الدالة المزينة التي تتحقق من Token قبل التنفيذ.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get(\'Authorization\')
        
        if not token:
            return jsonify({\'message\': \'Token مفقود\'}), 401
        
        try:
            if token.startswith(\'Bearer \'):
                token = token[7:]
            
            data = jwt.decode(token, JWT_SECRET, algorithms=[\'HS256\'])
            current_user_id = data[\'user_id\']
            current_user = User.query.get(current_user_id)
            
            if not current_user:
                return jsonify({\'message\': \'مستخدم غير صالح\'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({\'message\': \'انتهت صلاحية الجلسة\'}), 401
        except jwt.InvalidTokenError:
            return jsonify({\'message\': \'Token غير صالح\'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """
    Decorator للتحقق من صلاحيات المدير.

    يتطلب أن يكون المستخدم الحالي من نوع \'admin\' أو \'super_admin\'.
    إذا لم يكن كذلك، يعيد استجابة خطأ 403.

    Args:
        f (function): الدالة التي سيتم تطبيق الـ decorator عليها.

    Returns:
        function: الدالة المزينة التي تتحقق من صلاحيات المدير قبل التنفيذ.
    """
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.user_type not in [\'admin\', \'super_admin\']:
            return jsonify({\'message\': \'غير مصرح لك بالوصول\'}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route(\'/register\', methods=[\'POST\'])
def register():
    """
    تسجيل مستخدم جديد في النظام.

    تتطلب البيانات التالية في جسم الطلب (JSON):
    - email (str): البريد الإلكتروني للمستخدم (يجب أن يكون فريدًا).
    - password (str): كلمة المرور للمستخدم.
    - user_type (str): نوع المستخدم (مثال: \'patient\', \'doctor\', \'admin\').
    - first_name (str): الاسم الأول للمستخدم.
    - last_name (str): الاسم الأخير للمستخدم.
    - (اختياري) phone (str): رقم هاتف المستخدم.
    - (اختياري) date_of_birth (str): تاريخ ميلاد المريض (بصيغة YYYY-MM-DD).
    - (اختياري) gender (str): جنس المريض.
    - (اختياري) national_id (str): الرقم القومي للمريض.
    - (اختياري) license_number (str): رقم ترخيص الطبيب.
    - (اختياري) specialization (str): تخصص الطبيب.
    - (اختياري) admin_type (str): نوع المدير (مثال: \'system_admin\').

    Returns:
        Response: استجابة JSON تحتوي على رسالة نجاح ومعرف المستخدم ونوعه، أو رسالة خطأ.
    """
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = [\'email\', \'password\', \'user_type\', \'first_name\', \'last_name\']
        for field in required_fields:
            if field not in data:
                return jsonify({\'message\': f\'حقل {field} مطلوب\'}), 400
        
        # التحقق من وجود المستخدم
        if User.query.filter_by(email=data[\'email\']).first():
            return jsonify({\'message\': \'البريد الإلكتروني مستخدم بالفعل\'}), 400
        
        # إنشاء المستخدم الجديد
        hashed_password = generate_password_hash(data[\'password\'])
        
        new_user = User(
            email=data[\'email\'],
            password_hash=hashed_password,
            user_type=data[\'user_type\'],
            is_active=True
        )
        
        db.session.add(new_user)
        db.session.flush()  # للحصول على user_id
        
        # إنشاء الملف الشخصي حسب نوع المستخدم
        if data[\'user_type\'] == \'patient\':
            patient = Patient(
                user_id=new_user.id,
                first_name=data[\'first_name\'],
                last_name=data[\'last_name\'],
                email=data[\'email\'],
                phone=data.get(\'phone\', \'\'),
                date_of_birth=datetime.datetime.strptime(data[\'date_of_birth\'], \'%Y-%m-%d\').date() if data.get(\'date_of_birth\') else None,
                gender=data.get(\'gender\', \'\'),
                national_id=data.get(\'national_id\', \'\')
            )
            db.session.add(patient)
            
        elif data[\'user_type\'] == \'doctor\':
            doctor = Doctor(
                user_id=new_user.id,
                first_name=data[\'first_name\'],
                last_name=data[\'last_name\'],
                email=data[\'email\'],
                phone=data.get(\'phone\', \'\'),
                license_number=data.get(\'license_number\', \'\'),
                specialization=data.get(\'specialization\', \'\')
            )
            db.session.add(doctor)
            
        elif data[\'user_type\'] == \'admin\':
            admin = Admin(
                user_id=new_user.id,
                first_name=data[\'first_name\'],
                last_name=data[\'last_name\'],
                email=data[\'email\'],
                phone=data.get(\'phone\', \'\'),
                admin_type=data.get(\'admin_type\', \'system_admin\')
            )
            db.session.add(admin)
        
        db.session.commit()
        
        # تسجيل العملية في سجل المراجعة
        audit_log = AuditLog(
            user_id=new_user.id,
            user_email=new_user.email,
            user_type=new_user.user_type,
            action=\'user_registration\',
            description=f\'تسجيل مستخدم جديد: {data[\"first_name\"]} {data[\"last_name\"]}\\',
            ip_address=request.remote_addr,
            user_agent=request.headers.get(\'User-Agent\')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            \'message\': \'تم التسجيل بنجاح\',
            \'user_id\': new_user.id,
            \'user_type\': new_user.user_type
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({\'message\': f\'خطأ في التسجيل: {str(e)}\'}), 500

@auth_bp.route(\'/login\', methods=[\'POST\'])
def login():
    """
    تسجيل دخول المستخدم إلى النظام.

    تتطلب البيانات التالية في جسم الطلب (JSON):
    - email (str): البريد الإلكتروني للمستخدم.
    - password (str): كلمة المرور للمستخدم.

    Returns:
        Response: استجابة JSON تحتوي على رسالة نجاح وToken و معلومات المستخدم، أو رسالة خطأ.
    """
    try:
        data = request.get_json()
        
        if not data.get(\'email\') or not data.get(\'password\'):
            return jsonify({\'message\': \'البريد الإلكتروني وكلمة المرور مطلوبان\'}), 400
        
        # البحث عن المستخدم
        user = User.query.filter_by(email=data[\'email\']).first()
        
        if not user or not check_password_hash(user.password_hash, data[\'password\']):
            return jsonify({\'message\': \'بيانات الدخول غير صحيحة\'}), 401
        
        if not user.is_active:
            return jsonify({\'message\': \'الحساب غير مفعل\'}), 401
        
        # إنشاء JWT Token
        token_payload = {
            \'user_id\': user.id,
            \'email\': user.email,
            \'user_type\': user.user_type,
            \'exp\': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        
        token = jwt.encode(token_payload, JWT_SECRET, algorithm=\'HS256\')
        
        # تحديث معلومات آخر دخول
        user.last_login = datetime.datetime.utcnow()
        user.login_count = (user.login_count or 0) + 1
        
        # تحديث معلومات المدير إذا كان مدير
        if user.user_type in [\'admin\', \'super_admin\']:
            admin = Admin.query.filter_by(user_id=user.id).first()
            if admin:
                admin.last_login = datetime.datetime.utcnow()
                admin.login_count = (admin.login_count or 0) + 1
        
        db.session.commit()
        
        # تسجيل العملية في سجل المراجعة
        audit_log = AuditLog(
            user_id=user.id,
            user_email=user.email,
            user_type=user.user_type,
            action=\'user_login\',
            description=f\'تسجيل دخول ناجح\',
            ip_address=request.remote_addr,
            user_agent=request.headers.get(\'User-Agent\')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        # الحصول على معلومات إضافية حسب نوع المستخدم
        profile_data = {}
        if user.user_type == \'patient\':
            patient = Patient.query.filter_by(user_id=user.id).first()
            if patient:
                profile_data = patient.to_dict()
        elif user.user_type == \'doctor\':
            doctor = Doctor.query.filter_by(user_id=user.id).first()
            if doctor:
                profile_data = doctor.to_dict()
        elif user.user_type in [\'admin\', \'super_admin\']:
            admin = Admin.query.filter_by(user_id=user.id).first()
            if admin:
                profile_data = admin.to_dict()
        
        return jsonify({
            \'message\': \'تم تسجيل الدخول بنجاح\',
            \'token\': token,
            \'user\': {
                \'id\': user.id,
                \'email\': user.email,
                \'user_type\': user.user_type,
                \'is_active\': user.is_active,
                \'profile\': profile_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({\'message\': f\'خطأ في تسجيل الدخول: {str(e)}\'}), 500

@auth_bp.route(\'/owner-login\', methods=[\'POST\'])
def owner_login():
    """
    تسجيل دخول المالك (أحمد بهنسي) إلى النظام.

    تتطلب البيانات التالية في جسم الطلب (JSON):
    - email (str): البريد الإلكتروني للمالك (Ahmedbahnese@yahoo.com).
    - password (str): كلمة المرور للمالك (Bahnasy123).

    إذا لم يكن حساب المالك موجودًا، يتم إنشاؤه تلقائيًا.

    Returns:
        Response: استجابة JSON تحتوي على رسالة نجاح وToken ومعلومات المالك، أو رسالة خطأ.
    """
    try:
        data = request.get_json()
        
        # التحقق من بيانات المالك
        if (data.get(\'email\') == \'Ahmedbahnese@yahoo.com\' and 
            data.get(\'password\') == \'Bahnasy123\'):
            
            # البحث عن حساب المالك أو إنشاؤه
            owner = SystemOwner.query.first()
            if not owner:
                owner = SystemOwner()
                db.session.add(owner)
                db.session.commit()
            
            # البحث عن المستخدم أو إنشاؤه
            user = User.query.filter_by(email=\'Ahmedbahnese@yahoo.com\').first()
            if not user:
                user = User(
                    email=\'Ahmedbahnese@yahoo.com\',
                    password_hash=generate_password_hash(\'Bahnasy123\'),
                    user_type=\'super_admin\',
                    is_active=True
                )
                db.session.add(user)
                db.session.flush()
                
                # إنشاء ملف المدير
                admin = Admin(
                    user_id=user.id,
                    first_name=\'أحمد حامد\',
                    last_name=\'أحمد بهنسي\',
                    email=\'Ahmedbahnese@yahoo.com\',
                    phone=\'01063299450\',
                    admin_type=\'super_admin\',
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
            
            # إنشاء JWT Token
            token_payload = {
                \'user_id\': user.id,
                \'email\': user.email,
                \'user_type\': \'super_admin\',
                \'is_owner\': True,
                \'exp\': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }
            
            token = jwt.encode(token_payload, JWT_SECRET, algorithm=\'HS256\')
            
            # تحديث معلومات آخر دخول
            user.last_login = datetime.datetime.utcnow()
            user.login_count = (user.login_count or 0) + 1
            db.session.commit()
            
            # تسجيل العملية
            audit_log = AuditLog(
                user_id=user.id,
                user_email=user.email,
                user_type=\'super_admin\',
                action=\'owner_login\',
                description=\'تسجيل دخول المالك - أحمد بهنسي\',
                ip_address=request.remote_addr,
                user_agent=request.headers.get(\'User-Agent\')
            )
            db.session.add(audit_log)
            db.session.commit()
            
            return jsonify({
                \'message\': \'مرحباً بك أحمد بهنسي - مالك النظام\',
                \'token\': token,
                \'user\': {
                    \'id\': user.id,
                    \'email\': user.email,
                    \'user_type\': \'super_admin\',
                    \'is_owner\': True,
                    \'owner_info\': owner.to_dict()
                }
            }), 200
        else:
            return jsonify({\'message\': \'بيانات الدخول غير صحيحة\'}), 401
            
    except Exception as e:
        return jsonify({\'message\': f\'خطأ في تسجيل الدخول: {str(e)}\'}), 500

@auth_bp.route(\'/profile\', methods=[\'GET\'])
@token_required
def get_profile(current_user):
    """
    الحصول على الملف الشخصي للمستخدم الحالي.

    تتطلب Token صالح في رأس الطلب.

    Args:
        current_user (User): كائن المستخدم الحالي الذي تم استخراجه من Token.

    Returns:
        Response: استجابة JSON تحتوي على معلومات الملف الشخصي للمستخدم، أو رسالة خطأ.
    """
    try:
        profile_data = {}
        
        if current_user.user_type == \'patient\':
            patient = Patient.query.filter_by(user_id=current_user.id).first()
            if patient:
                profile_data = patient.to_dict()
        elif current_user.user_type == \'doctor\':
            doctor = Doctor.query.filter_by(user_id=current_user.id).first()
            if doctor:
                profile_data = doctor.to_dict()
        elif current_user.user_type in [\'admin\', \'super_admin\']:
            admin = Admin.query.filter_by(user_id=current_user.id).first()
            if admin:
                profile_data = admin.to_dict()
        
        return jsonify({
            \'user\': {
                \'id\': current_user.id,
                \'email\': current_user.email,
                \'user_type\': current_user.user_type,
                \'is_active\': current_user.is_active,
                \'last_login\': current_user.last_login.isoformat() if current_user.last_login else None,
                \'profile\': profile_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({\'message\': f\'خطأ في جلب الملف الشخصي: {str(e)}\'}), 500

@auth_bp.route(\'/logout\', methods=[\'POST\'])
@token_required
def logout(current_user):
    """
    تسجيل خروج المستخدم من النظام.

    تتطلب Token صالح في رأس الطلب.

    Args:
        current_user (User): كائن المستخدم الحالي الذي تم استخراجه من Token.

    Returns:
        Response: استجابة JSON تحتوي على رسالة نجاح، أو رسالة خطأ.
    """
    try:
        # تسجيل العملية في سجل المراجعة
        audit_log = AuditLog(
            user_id=current_user.id,
            user_email=current_user.email,
            user_type=current_user.user_type,
            action=\'user_logout\',
            description=\'تسجيل خروج\',
            ip_address=request.remote_addr,
            user_agent=request.headers.get(\'User-Agent\')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({\'message\': \'تم تسجيل الخروج بنجاح\'}), 200
        
    except Exception as e:
        return jsonify({\'message\': f\'خطأ في تسجيل الخروج: {str(e)}\'}), 500

@auth_bp.route(\'/change-password\', methods=[\'POST\'])
@token_required
def change_password(current_user):
    """
    تغيير كلمة المرور للمستخدم الحالي.

    تتطلب Token صالح في رأس الطلب والبيانات التالية في جسم الطلب (JSON):
    - current_password (str): كلمة المرور الحالية للمستخدم.
    - new_password (str): كلمة المرور الجديدة للمستخدم.

    Args:
        current_user (User): كائن المستخدم الحالي الذي تم استخراجه من Token.

    Returns:
        Response: استجابة JSON تحتوي على رسالة نجاح، أو رسالة خطأ.
    """
    try:
        data = request.get_json()
        
        if not data.get(\'current_password\') or not data.get(\'new_password\'):
            return jsonify({\'message\': \'كلمة المرور الحالية والجديدة مطلوبتان\'}), 400
        
        # التحقق من كلمة المرور الحالية
        if not check_password_hash(current_user.password_hash, data[\'current_password\']):
            return jsonify({\'message\': \'كلمة المرور الحالية غير صحيحة\'}), 400
        
        # تحديث كلمة المرور
        current_user.password_hash = generate_password_hash(data[\'new_password\'])
        db.session.commit()
        
        # تسجيل العملية
        audit_log = AuditLog(
            user_id=current_user.id,
            user_email=current_user.email,
            user_type=current_user.user_type,
            action=\'password_change\',
            description=\'تغيير كلمة المرور\',
            ip_address=request.remote_addr,
            user_agent=request.headers.get(\'User-Agent\')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({\'message\': \'تم تغيير كلمة المرور بنجاح\'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({\'message\': f\'خطأ في تغيير كلمة المرور: {str(e)}\'}), 500



