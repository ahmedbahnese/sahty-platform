"""
مسارات API لنظام الإشعارات
"""
from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.notification import Notification
from src.routes.auth import token_required

notification_bp = Blueprint('notification', __name__, url_prefix='/api/notifications')


@notification_bp.route('', methods=['GET'])
@token_required
def list_notifications(current_user):
    """جلب إشعارات المستخدم الحالي"""
    page      = request.args.get('page', 1, type=int)
    per_page  = min(request.args.get('per_page', 20, type=int), 50)
    unread_only = request.args.get('unread') == '1'

    query = Notification.query.filter_by(user_id=current_user.id)
    if unread_only:
        query = query.filter_by(is_read=False)

    total  = query.count()
    unread = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    items  = query.order_by(Notification.created_at.desc())\
        .offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        'notifications': [n.to_dict() for n in items],
        'total':         total,
        'unread_count':  unread,
        'page':          page,
        'per_page':      per_page,
    }), 200


@notification_bp.route('/unread-count', methods=['GET'])
@token_required
def unread_count(current_user):
    """عدد الإشعارات غير المقروءة فقط (للـ polling)"""
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'unread_count': count}), 200


@notification_bp.route('/mark-read', methods=['POST'])
@token_required
def mark_read(current_user):
    """تعيين إشعارات كمقروءة. body: { ids: [1,2,3] } أو {} لتعيين الكل"""
    data = request.get_json() or {}
    ids  = data.get('ids')

    query = Notification.query.filter_by(user_id=current_user.id, is_read=False)
    if ids:
        query = query.filter(Notification.id.in_(ids))

    updated = query.update({'is_read': True}, synchronize_session=False)
    db.session.commit()
    return jsonify({'success': True, 'updated': updated}), 200


@notification_bp.route('/<int:notif_id>', methods=['DELETE'])
@token_required
def delete_notification(current_user, notif_id):
    """حذف إشعار"""
    notif = Notification.query.filter_by(id=notif_id, user_id=current_user.id).first_or_404()
    db.session.delete(notif)
    db.session.commit()
    return jsonify({'success': True}), 200


@notification_bp.route('/clear', methods=['DELETE'])
@token_required
def clear_all(current_user):
    """حذف جميع الإشعارات المقروءة"""
    deleted = Notification.query.filter_by(user_id=current_user.id, is_read=True).delete()
    db.session.commit()
    return jsonify({'success': True, 'deleted': deleted}), 200
