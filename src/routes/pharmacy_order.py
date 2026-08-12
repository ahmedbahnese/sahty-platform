"""
مسارات طلبات الأدوية من الصيدلية — Sprint X Feature 3

POST   /api/pharmacy-orders                      — إنشاء طلب (multipart يدعم رفع صورة وصفة)
GET    /api/pharmacy-orders                      — قائمة طلبات المريض
GET    /api/pharmacy-orders/<id>                 — تفاصيل طلب
PUT    /api/pharmacy-orders/<id>/confirm         — الصيدلية تؤكد الطلب
PUT    /api/pharmacy-orders/<id>/dispense        — الصيدلية تؤكد الصرف
PUT    /api/pharmacy-orders/<id>/cancel          — إلغاء الطلب
"""
import os
import json
import uuid
from datetime import datetime

from flask import Blueprint, request, jsonify, send_from_directory, g
from werkzeug.utils import secure_filename

from src.models.user import db
from src.models.patient import Patient
from src.models.medication import PharmacyOrder
from src.models.notification import Notification
from src.routes.auth import token_required

pharmacy_order_bp = Blueprint('pharmacy_order', __name__)

UPLOAD_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'static', 'uploads')
ALLOWED_IMG = {'pdf', 'jpg', 'jpeg', 'png', 'gif', 'webp'}


def _ensure_dir(subdir):
    path = os.path.join(UPLOAD_ROOT, subdir)
    os.makedirs(path, exist_ok=True)
    return path


def _save_file(file_storage, subdir):
    if not file_storage or file_storage.filename == '':
        return None, None
    ext = file_storage.filename.rsplit('.', 1)[-1].lower() if '.' in file_storage.filename else ''
    if ext not in ALLOWED_IMG:
        return None, None
    unique = f"{uuid.uuid4().hex}.{ext}"
    file_storage.save(os.path.join(_ensure_dir(subdir), unique))
    return unique, f"/api/uploads/{subdir}/{unique}"


def _notify(user_id, title, message, ref_id=None):
    db.session.add(Notification(
        user_id=user_id, title=title, message=message,
        type='pharmacy_order', reference_id=ref_id, reference_type='pharmacy_order',
    ))


# ─────────────────────────────────────────
# إنشاء طلب
# ─────────────────────────────────────────

@pharmacy_order_bp.route('/pharmacy-orders', methods=['POST'])
@token_required
def create_pharmacy_order(current_user):
    """
    يقبل multipart/form-data أو JSON.
    order_type: paper_prescription | manual | from_prescription
    """
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'ملف المريض غير موجود'}), 404

    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()

    order_type = data.get('order_type', 'manual')
    if order_type not in ('paper_prescription', 'manual', 'from_prescription'):
        return jsonify({'message': 'نوع الطلب غير صالح'}), 400

    # الأدوية (JSON string)
    meds_raw = data.get('medications_json', '[]')
    if isinstance(meds_raw, str):
        try:
            meds = json.loads(meds_raw)
        except Exception:
            meds = []
    else:
        meds = meds_raw if isinstance(meds_raw, list) else []

    # وصفة المنصة
    source_rx_id = int(data['source_prescription_id']) if data.get('source_prescription_id') else None
    if order_type == 'from_prescription' and source_rx_id:
        # اسحب الأدوية من الوصفة
        from src.models.prescription import Prescription, PrescriptionItem
        rx = Prescription.query.get(source_rx_id)
        if rx and rx.patient_id == patient.id:
            items = PrescriptionItem.query.filter_by(prescription_id=rx.id).all()
            if not meds:   # استخدم أدوية الوصفة إذا لم تُدخَل يدوياً
                meds = [{'name': i.drug_name, 'dosage': i.dosage, 'quantity': '', 'notes': i.instructions or ''} for i in items]

    if not meds and order_type != 'paper_prescription':
        return jsonify({'message': 'يجب تحديد دواء واحد على الأقل'}), 400

    order = PharmacyOrder(
        patient_id=patient.id,
        order_type=order_type,
        source_prescription_id=source_rx_id,
        medications_json=json.dumps(meds, ensure_ascii=False),
        preferred_pharmacy_name=data.get('preferred_pharmacy_name'),
        preferred_pharmacy_id=int(data['preferred_pharmacy_id']) if data.get('preferred_pharmacy_id') else None,
        fulfillment_method=data.get('fulfillment_method', 'pickup'),
        delivery_address=data.get('delivery_address'),
        notes=data.get('notes'),
        status='pending',
    )
    db.session.add(order)
    db.session.flush()

    # رفع صورة الوصفة الورقية
    if order_type == 'paper_prescription' and 'prescription_image' in request.files:
        saved_name, _ = _save_file(request.files['prescription_image'], 'prescription_images')
        if saved_name:
            order.prescription_image_path = saved_name
            order.prescription_image_name = request.files['prescription_image'].filename
    elif order_type == 'paper_prescription' and not data.get('prescription_image_path'):
        pass   # الصورة اختيارية لكن يُفضَّل

    db.session.commit()

    # إشعار المريض
    _notify(
        patient.user_id,
        'تم إرسال طلب الدواء',
        f'تم إرسال طلب الدواء إلى الصيدلية. سنخطرك عند التأكيد.',
        order.id,
    )
    db.session.commit()
    return jsonify(order.to_dict()), 201


# ─────────────────────────────────────────
# قائمة الطلبات
# ─────────────────────────────────────────

@pharmacy_order_bp.route('/pharmacy-orders', methods=['GET'])
@token_required
def list_pharmacy_orders(current_user):
    role = getattr(g, 'current_role', current_user.user_type)
    if role == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify([]), 200
        q = PharmacyOrder.query.filter_by(patient_id=patient.id)
    elif role == 'pharmacy':
        # A pharmacy only sees orders explicitly addressed to it. Legacy orders
        # without a selected pharmacy remain visible to admins, not every store.
        provider_id = request.args.get('pharmacy_id', type=int)
        q = PharmacyOrder.query.filter(
            PharmacyOrder.preferred_pharmacy_id == provider_id
        ) if provider_id else PharmacyOrder.query.filter_by(preferred_pharmacy_id=None)
    else:
        q = PharmacyOrder.query

    status_filter = request.args.get('status')
    if status_filter:
        q = q.filter_by(status=status_filter)

    orders = q.order_by(PharmacyOrder.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders]), 200


@pharmacy_order_bp.route('/pharmacy-orders/<int:order_id>', methods=['GET'])
@token_required
def get_pharmacy_order(current_user, order_id):
    order = PharmacyOrder.query.get_or_404(order_id)
    if getattr(g, 'current_role', current_user.user_type) == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient or order.patient_id != patient.id:
            return jsonify({'message': 'غير مصرح'}), 403
    return jsonify(order.to_dict()), 200


# ─────────────────────────────────────────
# إجراءات الصيدلية
# ─────────────────────────────────────────

@pharmacy_order_bp.route('/pharmacy-orders/<int:order_id>/confirm', methods=['PUT'])
@token_required
def confirm_pharmacy_order(current_user, order_id):
    if getattr(g, 'current_role', current_user.user_type) not in ('admin', 'super_admin', 'pharmacy'):
        return jsonify({'message': 'غير مصرح'}), 403
    order = PharmacyOrder.query.get_or_404(order_id)
    if order.status != 'pending':
        return jsonify({'message': 'الطلب ليس في حالة انتظار'}), 400
    order.status = 'confirmed'
    order.updated_at = datetime.utcnow()
    db.session.commit()

    patient = Patient.query.get(order.patient_id)
    if patient:
        _notify(patient.user_id, 'تأكيد طلب الدواء', 'تم تأكيد طلب الدواء من الصيدلية. سيتم التحضير قريباً.', order.id)
        db.session.commit()
    return jsonify(order.to_dict()), 200


@pharmacy_order_bp.route('/pharmacy-orders/<int:order_id>/dispense', methods=['PUT'])
@token_required
def dispense_pharmacy_order(current_user, order_id):
    if getattr(g, 'current_role', current_user.user_type) not in ('admin', 'super_admin', 'pharmacy'):
        return jsonify({'message': 'غير مصرح'}), 403
    order = PharmacyOrder.query.get_or_404(order_id)
    if order.status not in ('pending', 'confirmed'):
        return jsonify({'message': 'لا يمكن صرف هذا الطلب في حالته الحالية'}), 400
    order.status = 'dispensed'
    order.dispensed_at = datetime.utcnow()
    order.updated_at = datetime.utcnow()
    db.session.commit()

    patient = Patient.query.get(order.patient_id)
    if patient:
        _notify(patient.user_id, 'تم صرف الدواء', 'تم صرف طلب الدواء بنجاح. يمكنك استلامه من الصيدلية.', order.id)
        db.session.commit()
    return jsonify(order.to_dict()), 200


@pharmacy_order_bp.route('/pharmacy-orders/<int:order_id>/cancel', methods=['PUT'])
@token_required
def cancel_pharmacy_order(current_user, order_id):
    order = PharmacyOrder.query.get_or_404(order_id)
    if current_user.user_type == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient or order.patient_id != patient.id:
            return jsonify({'message': 'غير مصرح'}), 403
    data = request.get_json(silent=True) or {}
    order.status = 'cancelled'
    order.cancelled_reason = data.get('reason', '')
    order.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(order.to_dict()), 200
