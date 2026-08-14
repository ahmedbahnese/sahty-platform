from flask import Blueprint, jsonify, request
from src.models.user import User, db
from src.routes.auth import token_required, role_required, current_role, has_active_role, PROFESSIONAL_ROLES
from werkzeug.security import generate_password_hash

user_bp = Blueprint('user', __name__)
ASSIGNABLE_ROLES = {'patient', 'admin', 'super_admin'}

@user_bp.route('/users', methods=['GET'])
@token_required
@role_required('admin', 'super_admin')
def get_users(current_user):
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users', methods=['POST'])
@token_required
@role_required('admin', 'super_admin')
def create_user(current_user):
    data = request.get_json(silent=True) or {}
    if not data.get('email') or not data.get('password'):
        return jsonify({'message': 'البريد الإلكتروني وكلمة المرور مطلوبان'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'البريد الإلكتروني مستخدم بالفعل'}), 400
    requested_role = data.get('user_type', 'patient')
    if requested_role not in ASSIGNABLE_ROLES:
        return jsonify({'message': 'الأدوار المهنية لا تُفعّل من هذا المسار؛ استخدم طلب الاعتماد'}), 400
    if requested_role in ('admin', 'super_admin') and current_role(current_user) != 'super_admin':
        return jsonify({'message': 'لا يمكن للمدير العادي إنشاء مالك للنظام'}), 403
    user = User(
        username=data.get('username'),
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        user_type=requested_role,
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    if current_user.id != user_id and not has_active_role(current_user, 'admin', 'super_admin'):
        return jsonify({'message': 'غير مصرح لك بالوصول'}), 403
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'message': 'المستخدم غير موجود'}), 404
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    if current_user.id != user_id and not has_active_role(current_user, 'admin', 'super_admin'):
        return jsonify({'message': 'غير مصرح لك بالوصول'}), 403
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'message': 'المستخدم غير موجود'}), 404
    if (
        current_role(current_user) == 'admin'
        and user.user_type == 'super_admin'
    ):
        return jsonify({'message': 'لا يمكن للمدير العادي تعديل مالك النظام'}), 403
    data = request.get_json(silent=True) or {}
    user.username = data.get('username', user.username)
    if has_active_role(current_user, 'admin', 'super_admin'):
        user.email = data.get('email', user.email)
        requested_role = data.get('user_type', user.user_type)
        if requested_role in PROFESSIONAL_ROLES:
            return jsonify({'message': 'الأدوار المهنية لا تُفعّل بالتعديل المباشر؛ يجب اعتماد طلب الدور من الإدارة'}), 400
        if requested_role not in ASSIGNABLE_ROLES:
            return jsonify({'message': 'الدور المطلوب غير صالح'}), 400
        if requested_role in ('admin', 'super_admin') and current_role(current_user) != 'super_admin':
            return jsonify({'message': 'لا يمكن للمدير العادي تعيين دور إداري'}), 403
        user.user_type = requested_role
    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
@role_required('super_admin')
def delete_user(current_user, user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'message': 'المستخدم غير موجود'}), 404
    if user.id == current_user.id:
        return jsonify({'message': 'لا يمكن حذف الحساب الحالي'}), 400
    db.session.delete(user)
    db.session.commit()
    return '', 204

@user_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'صحتك في أمان API تعمل بنجاح'}), 200
