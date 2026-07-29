from flask import Blueprint, request, jsonify
from src.models.user import db
from src.routes.auth import token_required, admin_required
import datetime

feedback_bp = Blueprint('feedback', __name__)


class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150))
    phone = db.Column(db.String(30))
    type = db.Column(db.String(30), nullable=False)  # complaint | suggestion | inquiry
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='new')  # new | reviewed | resolved
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'type': self.type,
            'subject': self.subject,
            'message': self.message,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


TYPE_LABELS = {
    'complaint': 'شكوى',
    'suggestion': 'اقتراح',
    'inquiry': 'استفسار',
}


@feedback_bp.route('/api/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json(silent=True) or {}
        required = ['name', 'type', 'subject', 'message']
        for field in required:
            if not data.get(field, '').strip():
                return jsonify({'message': f'حقل {field} مطلوب'}), 400
        if data['type'] not in TYPE_LABELS:
            return jsonify({'message': 'نوع غير صالح'}), 400

        # Attach logged-in user if token provided
        user_id = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            try:
                import jwt, os, hashlib
                from src.models.user import UserSession, User
                raw_token = auth_header[7:]
                secret = os.environ.get('JWT_SECRET') or os.environ.get('SESSION_SECRET')
                payload = jwt.decode(raw_token, secret, algorithms=['HS256'])
                token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
                session = UserSession.query.filter_by(
                    token_hash=token_hash, user_id=payload['user_id']
                ).first()
                if session and session.is_valid:
                    user_id = payload['user_id']
            except Exception:
                pass

        fb = Feedback(
            name=data['name'].strip(),
            email=data.get('email', '').strip() or None,
            phone=data.get('phone', '').strip() or None,
            type=data['type'],
            subject=data['subject'].strip(),
            message=data['message'].strip(),
            user_id=user_id,
        )
        db.session.add(fb)
        db.session.commit()
        return jsonify({'message': 'تم إرسال رسالتك بنجاح، سنتواصل معك قريباً', 'id': fb.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'خطأ في الإرسال: {str(e)}'}), 500


@feedback_bp.route('/api/feedback', methods=['GET'])
@token_required
@admin_required
def list_feedback(current_user):
    """للمؤسس والمشرفين فقط — عرض جميع الرسائل"""
    try:
        status_filter = request.args.get('status')
        type_filter = request.args.get('type')
        query = Feedback.query.order_by(Feedback.created_at.desc())
        if status_filter:
            query = query.filter_by(status=status_filter)
        if type_filter:
            query = query.filter_by(type=type_filter)
        items = query.limit(200).all()
        return jsonify({'feedback': [f.to_dict() for f in items], 'total': len(items)}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@feedback_bp.route('/api/feedback/<int:feedback_id>', methods=['PATCH'])
@token_required
@admin_required
def update_feedback(current_user, feedback_id):
    """تحديث حالة الرسالة أو إضافة ملاحظة"""
    try:
        fb = db.session.get(Feedback, feedback_id)
        if not fb:
            return jsonify({'message': 'الرسالة غير موجودة'}), 404
        data = request.get_json(silent=True) or {}
        if 'status' in data:
            fb.status = data['status']
        if 'admin_notes' in data:
            fb.admin_notes = data['admin_notes']
        db.session.commit()
        return jsonify({'message': 'تم التحديث', 'feedback': fb.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500
