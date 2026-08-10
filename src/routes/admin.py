from datetime import datetime
from functools import wraps

from flask import Blueprint, jsonify, request

from src.models.admin import AuditLog
from src.models.doctor import Doctor
from src.models.provider import PROVIDER_ROLES, ProviderRegistration
from src.models.user import User, db
from src.models.professional import (
    Role, UserRole, ProfessionalRoleRequest, NurseProfile,
)
from src.models.notification import Notification
from src.routes.auth import token_required


admin_bp = Blueprint('admin', __name__)


def admin_only(f):
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if current_user.user_type not in ('admin', 'super_admin'):
            return jsonify({'message': 'هذه الصفحة متاحة للمدير فقط'}), 403
        return f(current_user, *args, **kwargs)
    return decorated


def _write_audit(admin, action, description, resource_id=None):
    try:
        db.session.add(AuditLog(
            user_id=admin.id,
            user_email=admin.email,
            user_type=admin.user_type,
            action=action,
            resource='provider_registrations',
            resource_id=resource_id,
            description=description,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
        ))
        db.session.commit()
    except Exception:
        db.session.rollback()


@admin_bp.route('/providers', methods=['GET'])
@admin_only
def list_providers(current_user):
    status = request.args.get('status')
    provider_type = request.args.get('provider_type')
    query = ProviderRegistration.query.order_by(ProviderRegistration.created_at.desc())
    if status in ('pending', 'approved', 'rejected', 'more_information'):
        query = query.filter_by(status=status)
    if provider_type in PROVIDER_ROLES:
        query = query.filter_by(provider_type=provider_type)
    return jsonify([registration.to_dict() for registration in query.all()])


@admin_bp.route('/providers/<int:registration_id>/review', methods=['PATCH'])
@admin_only
def review_provider(current_user, registration_id):
    registration = db.session.get(ProviderRegistration, registration_id)
    if not registration:
        return jsonify({'message': 'طلب الاعتماد غير موجود'}), 404

    data = request.get_json(silent=True) or {}
    decision = data.get('status')
    if decision not in ('approved', 'rejected', 'more_information'):
        return jsonify({'message': 'حالة الاعتماد غير صالحة'}), 400

    registration.status = decision
    registration.review_note = (data.get('review_note') or '').strip() or None
    registration.reviewed_by = current_user.id
    registration.reviewed_at = datetime.utcnow()
    # Professional approval never disables the base patient account.
    registration.user.is_active = True

    if registration.provider_type == 'doctor':
        doctor = Doctor.query.filter_by(user_id=registration.user_id).first()
        if doctor:
            doctor.is_verified = decision == 'approved'
            doctor.is_active = decision == 'approved'
    if registration.provider_type == 'nurse':
        nurse = NurseProfile.query.filter_by(user_id=registration.user_id).first()
        if nurse:
            nurse.is_active = decision == 'approved'

    role = Role.query.filter_by(name=registration.provider_type).first()
    if not role:
        role = Role(name=registration.provider_type, label_ar=registration.provider_type)
        db.session.add(role)
        db.session.flush()
    user_role = UserRole.query.filter_by(
        user_id=registration.user_id, role_id=role.id
    ).first()
    if not user_role:
        user_role = UserRole(user_id=registration.user_id, role_id=role.id)
        db.session.add(user_role)
    user_role.status = (
        'ACTIVE' if decision == 'approved'
        else 'PENDING_APPROVAL' if decision == 'more_information'
        else 'REJECTED'
    )
    user_role.activated_at = datetime.utcnow() if decision == 'approved' else None
    role_request = ProfessionalRoleRequest.query.filter_by(
        user_id=registration.user_id,
        requested_role=registration.provider_type,
    ).order_by(ProfessionalRoleRequest.submitted_at.desc()).first()
    if role_request:
        role_request.status = (
            'APPROVED' if decision == 'approved'
            else 'MORE_INFORMATION' if decision == 'more_information'
            else 'REJECTED'
        )
        role_request.reviewed_at = datetime.utcnow()
        role_request.reviewed_by = current_user.id
        role_request.rejection_reason = registration.review_note if decision != 'approved' else None
    db.session.add(Notification(
        user_id=registration.user_id,
        title='تم تحديث طلب الدور المهني',
        message=(
            'تم اعتماد طلبك المهني.' if decision == 'approved'
            else 'يرجى استكمال المعلومات المطلوبة لطلبك المهني.' if decision == 'more_information'
            else 'تم رفض طلبك المهني.'
        ),
        type='system',
    ))

    db.session.commit()
    _write_audit(
        current_user,
        f'provider_{decision}',
        f'تم {decision} طلب {registration.legal_name}',
        registration.id,
    )
    return jsonify(registration.to_dict())


@admin_bp.route('/users', methods=['GET'])
@admin_only
def list_users(current_user):
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([{
        **user.to_dict(),
        'provider': user.provider_registration.to_dict() if user.provider_registration else None,
    } for user in users])


@admin_bp.route('/users/<int:user_id>/status', methods=['PATCH'])
@admin_only
def update_user_status(current_user, user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'message': 'المستخدم غير موجود'}), 404
    if user.id == current_user.id:
        return jsonify({'message': 'لا يمكن تعطيل حسابك الحالي'}), 400
    if user.user_type == 'super_admin' and current_user.user_type != 'super_admin':
        return jsonify({'message': 'لا يمكن للمدير العادي تعديل مالك النظام'}), 403
    data = request.get_json(silent=True) or {}
    if not isinstance(data.get('is_active'), bool):
        return jsonify({'message': 'قيمة حالة الحساب غير صالحة'}), 400
    user.is_active = data['is_active']
    db.session.commit()
    _write_audit(current_user, 'user_status_changed', f'تغيير حالة {user.email}', user.id)
    return jsonify(user.to_dict())


@admin_bp.route('/audit-logs', methods=['GET'])
@admin_only
def audit_logs(current_user):
    from src.models.admin import AuditLog
    limit = min(int(request.args.get('limit', 100)), 500)
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    return jsonify([{
        'id': log.id,
        'user_id': log.user_id,
        'user_email': log.user_email,
        'user_type': log.user_type,
        'action': log.action,
        'resource': log.resource,
        'resource_id': log.resource_id,
        'description': log.description,
        'ip_address': log.ip_address,
        'created_at': log.created_at.isoformat() if log.created_at else None,
    } for log in logs])


@admin_bp.route('/stats', methods=['GET'])
@admin_only
def stats(current_user):
    users_by_role = {
        role: User.query.filter_by(user_type=role).count()
        for role in ('patient', 'doctor', *PROVIDER_ROLES.keys(), 'admin', 'super_admin')
    }
    provider_counts = {
        provider_type: {
            'total': ProviderRegistration.query.filter_by(provider_type=provider_type).count(),
            'pending': ProviderRegistration.query.filter_by(provider_type=provider_type, status='pending').count(),
            'approved': ProviderRegistration.query.filter_by(provider_type=provider_type, status='approved').count(),
            'rejected': ProviderRegistration.query.filter_by(provider_type=provider_type, status='rejected').count(),
        }
        for provider_type in ('doctor', *PROVIDER_ROLES.keys())
    }
    return jsonify({
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'pending_approvals': ProviderRegistration.query.filter_by(status='pending').count(),
        'users_by_role': users_by_role,
        'providers': provider_counts,
    })