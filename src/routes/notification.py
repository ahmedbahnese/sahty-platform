"""
مسارات API لنظام الإشعارات
"""
from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.notification import Notification
from src.models.push_subscription import PushSubscription
from src.routes.auth import token_required

notification_bp = Blueprint('notification', __name__, url_prefix='/api/notifications')


@notification_bp.route('', methods=['GET'])
@token_required
def list_notifications(current_user):
    """جلب إشعارات المستخدم الحالي"""
    page      = max(request.args.get('page', 1, type=int) or 1, 1)
    per_page  = min(max(request.args.get('per_page', 20, type=int) or 20, 1), 50)
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
    data = request.get_json(silent=True)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return jsonify({'success': False, 'error': 'بيانات الإشعارات يجب أن تكون JSON صحيحة'}), 400
    ids = data.get('ids')
    if ids is not None:
        if not isinstance(ids, list) or not all(isinstance(item, int) and item > 0 for item in ids):
            return jsonify({'success': False, 'error': 'قائمة معرفات الإشعارات غير صالحة'}), 400

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

def _ensure_push_table():
    """Create push_subscriptions on first use (the app does not run migrations on Vercel)."""
    from sqlalchemy import text
    try:
        db.session.execute(text("SELECT 1 FROM push_subscriptions LIMIT 1"))
    except Exception:
        db.session.rollback()
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS push_subscriptions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                endpoint TEXT NOT NULL UNIQUE,
                p256dh VARCHAR(200) NOT NULL,
                auth VARCHAR(200) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """))
        db.session.commit()


def _optional_user_id():
    """User id from a Bearer token when one is sent; None for guests."""
    import jwt
    import os
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header[7:]
    for secret in (os.environ.get('JWT_SECRET'), os.environ.get('SESSION_SECRET')):
        if not secret:
            continue
        try:
            payload = jwt.decode(token, secret, algorithms=['HS256'])
            return payload.get('user_id')
        except Exception:
            continue
    return None


@notification_bp.route('/push-subscribe', methods=['POST'])
def push_subscribe():
    """Store a Web Push subscription so the device receives emergency alerts.
    Works for guests too; links to the user when a valid token is sent."""
    _ensure_push_table()
    data = request.get_json(silent=True) or {}
    sub = data.get('subscription') or {}
    endpoint = (sub.get('endpoint') or '').strip()
    keys = sub.get('keys') or {}
    p256dh = (keys.get('p256dh') or '').strip()
    auth = (keys.get('auth') or '').strip()
    if not endpoint or not p256dh or not auth:
        return jsonify({'message': 'بيانات الاشتراك غير كاملة'}), 400
    user_id = _optional_user_id()
    existing = PushSubscription.query.filter_by(endpoint=endpoint).first()
    if existing:
        existing.user_id = user_id or existing.user_id
        existing.p256dh = p256dh
        existing.auth = auth
    else:
        db.session.add(PushSubscription(
            user_id=user_id, endpoint=endpoint, p256dh=p256dh, auth=auth,
        ))
    db.session.commit()
    return jsonify({'success': True}), 200


@notification_bp.route('/push-subscribe', methods=['DELETE'])
def push_unsubscribe():
    """Remove a Web Push subscription (stop emergency alerts on this device)."""
    _ensure_push_table()
    data = request.get_json(silent=True) or {}
    endpoint = (data.get('endpoint') or '').strip()
    if not endpoint:
        return jsonify({'message': 'الاشتراك غير محدد'}), 400
    PushSubscription.query.filter_by(endpoint=endpoint).delete()
    db.session.commit()
    return jsonify({'success': True}), 200
