"""
مسارات API لنظام طلبات التحاليل المخبرية والأشعة.

التحاليل:
  POST   /api/lab-requests                    — إنشاء طلب
  GET    /api/lab-requests                    — قائمة الطلبات (بحسب الدور)
  GET    /api/lab-requests/<id>               — تفاصيل طلب
  PUT    /api/lab-requests/<id>/approve       — اعتماد الطلب
  PUT    /api/lab-requests/<id>/reject        — رفض الطلب
  POST   /api/lab-requests/<id>/results       — رفع النتائج (multipart)
  POST   /api/lab-requests/<id>/notify        — إرسال الإشعارات

الأشعة:
  POST   /api/radiology-requests              — إنشاء طلب
  GET    /api/radiology-requests              — قائمة الطلبات
  GET    /api/radiology-requests/<id>         — تفاصيل طلب
  PUT    /api/radiology-requests/<id>/reject  — رفض
  POST   /api/radiology-requests/<id>/images  — رفع الصور (multipart)
  POST   /api/radiology-requests/<id>/report  — رفع التقرير
  POST   /api/radiology-requests/<id>/share   — مشاركة النتائج + إشعار
"""
import os
import json
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename

from src.models.user    import db, User
from src.models.patient import Patient
from src.models.notification import Notification
from src.models.lab_radiology import LabRequest, RadiologyRequest
from src.routes.auth import token_required

lab_radiology_bp = Blueprint('lab_radiology', __name__)

# ─────────────────────────────────────────────────────────
# مجلد رفع الملفات
# ─────────────────────────────────────────────────────────
UPLOAD_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif', 'dcm', 'tiff', 'tif'}

def _ensure_upload_dir(subdir=''):
    path = os.path.join(UPLOAD_ROOT, subdir)
    os.makedirs(path, exist_ok=True)
    return path


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _save_uploaded_file(file_storage, subdir):
    """حفظ ملف مرفوع وإعادة (saved_name, relative_url)."""
    if not file_storage or file_storage.filename == '':
        return None, None
    if not _allowed_file(file_storage.filename):
        return None, None
    ext       = file_storage.filename.rsplit('.', 1)[1].lower()
    unique    = f"{uuid.uuid4().hex}.{ext}"
    folder    = _ensure_upload_dir(subdir)
    file_storage.save(os.path.join(folder, unique))
    return unique, f"/api/uploads/{subdir}/{unique}"


def _notify(user_id, title, message, ref_type, ref_id):
    n = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=ref_type,
        reference_id=ref_id,
        reference_type=ref_type,
    )
    db.session.add(n)


def _get_patient_for_user(user):
    """إذا كان المستخدم مريضاً، أعِد سجل المريض. وإلا None."""
    if user.user_type == 'patient':
        return Patient.query.filter_by(user_id=user.id).first()
    return None


# ═══════════════════════════════════════════════════════════
# التحاليل المخبرية — Lab Requests
# ═══════════════════════════════════════════════════════════

@lab_radiology_bp.route('/lab-requests', methods=['POST'])
@token_required
def create_lab_request(current_user):
    """إنشاء طلب تحليل جديد."""
    data = request.get_json(silent=True) or {}

    # تحديد المريض
    if current_user.user_type == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    else:
        # طبيب أو مسؤول يطلب لمريض محدد
        patient_id = data.get('patient_id')
        if not patient_id:
            return jsonify({'message': 'معرّف المريض مطلوب'}), 400
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'message': 'المريض غير موجود'}), 404

    if not data.get('test_name'):
        return jsonify({'message': 'اسم التحليل مطلوب'}), 400

    lab_req = LabRequest(
        patient_id=patient.id,
        requesting_user_id=current_user.id,
        test_name=data['test_name'],
        test_category=data.get('test_category'),
        urgency=data.get('urgency', 'normal'),
        clinical_notes=data.get('clinical_notes'),
        ordering_doctor=data.get('ordering_doctor'),
        status='requested',
    )
    db.session.add(lab_req)
    db.session.commit()
    return jsonify(lab_req.to_dict()), 201


@lab_radiology_bp.route('/lab-requests', methods=['GET'])
@token_required
def list_lab_requests(current_user):
    """قائمة الطلبات — بحسب دور المستخدم."""
    if current_user.user_type == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify([]), 200
        requests_q = LabRequest.query.filter_by(patient_id=patient.id)
    else:
        # طبيب / مختبر / مسؤول — يرى كل الطلبات
        requests_q = LabRequest.query

    status_filter = request.args.get('status')
    if status_filter:
        requests_q = requests_q.filter_by(status=status_filter)

    items = requests_q.order_by(LabRequest.created_at.desc()).all()
    return jsonify([r.to_dict() for r in items]), 200


@lab_radiology_bp.route('/lab-requests/<int:req_id>', methods=['GET'])
@token_required
def get_lab_request(current_user, req_id):
    lab_req = LabRequest.query.get_or_404(req_id)
    if current_user.user_type == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient or lab_req.patient_id != patient.id:
            return jsonify({'message': 'غير مصرح'}), 403
    return jsonify(lab_req.to_dict()), 200


@lab_radiology_bp.route('/lab-requests/<int:req_id>/approve', methods=['PUT'])
@token_required
def approve_lab_request(current_user, req_id):
    """اعتماد طلب التحليل — للمختبر أو المسؤول."""
    if current_user.user_type not in ('admin', 'super_admin', 'laboratory', 'lab'):
        return jsonify({'message': 'غير مصرح لك بالاعتماد'}), 403
    lab_req = LabRequest.query.get_or_404(req_id)
    if lab_req.status != 'requested':
        return jsonify({'message': f'الطلب بحالة "{lab_req.status}" ولا يمكن اعتماده'}), 400
    data = request.get_json(silent=True) or {}
    lab_req.status              = 'approved'
    lab_req.approved_by_user_id = current_user.id
    lab_req.approved_at         = datetime.utcnow()
    lab_req.approval_notes      = data.get('approval_notes', '')
    db.session.commit()

    # إشعار صاحب الطلب
    _notify(
        lab_req.requesting_user_id,
        'تم اعتماد طلب التحليل',
        f'تم اعتماد طلبك للتحليل "{lab_req.test_name}".',
        'lab_request', lab_req.id,
    )
    db.session.commit()
    return jsonify(lab_req.to_dict()), 200


@lab_radiology_bp.route('/lab-requests/<int:req_id>/reject', methods=['PUT'])
@token_required
def reject_lab_request(current_user, req_id):
    """رفض طلب التحليل."""
    if current_user.user_type not in ('admin', 'super_admin', 'laboratory', 'lab'):
        return jsonify({'message': 'غير مصرح لك بالرفض'}), 403
    lab_req = LabRequest.query.get_or_404(req_id)
    if lab_req.status not in ('requested',):
        return jsonify({'message': 'الطلب لا يمكن رفضه في حالته الحالية'}), 400
    data = request.get_json(silent=True) or {}
    lab_req.status           = 'rejected'
    lab_req.rejection_reason = data.get('rejection_reason', '')
    db.session.commit()

    _notify(
        lab_req.requesting_user_id,
        'تم رفض طلب التحليل',
        f'تم رفض طلبك للتحليل "{lab_req.test_name}". السبب: {lab_req.rejection_reason}',
        'lab_request', lab_req.id,
    )
    db.session.commit()
    return jsonify(lab_req.to_dict()), 200


@lab_radiology_bp.route('/lab-requests/<int:req_id>/results', methods=['POST'])
@token_required
def upload_lab_results(current_user, req_id):
    """رفع نتائج التحليل — نص + ملف اختياري."""
    lab_req = LabRequest.query.get_or_404(req_id)
    if lab_req.status == 'rejected':
        return jsonify({'message': 'لا يمكن رفع نتائج لطلب مرفوض'}), 400

    # نص النتائج (JSON أو form-data)
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()

    lab_req.lab_name              = data.get('lab_name', lab_req.lab_name)
    lab_req.result_value          = data.get('result_value')
    lab_req.result_unit           = data.get('result_unit')
    lab_req.reference_range       = data.get('reference_range')
    lab_req.result_status         = data.get('result_status', 'normal')
    lab_req.result_interpretation = data.get('result_interpretation')
    lab_req.result_uploaded_at    = datetime.utcnow()
    lab_req.result_uploaded_by    = current_user.id
    lab_req.status                = 'results_uploaded'

    # ملف اختياري
    if 'result_file' in request.files:
        saved_name, _ = _save_uploaded_file(request.files['result_file'], 'lab_results')
        if saved_name:
            lab_req.result_file_path = saved_name
            lab_req.result_file_name = request.files['result_file'].filename

    db.session.commit()
    return jsonify(lab_req.to_dict()), 200


@lab_radiology_bp.route('/lab-requests/<int:req_id>/notify', methods=['POST'])
@token_required
def notify_lab_results(current_user, req_id):
    """إرسال إشعار بنتائج التحليل للطبيب والمريض."""
    lab_req = LabRequest.query.get_or_404(req_id)
    if lab_req.status != 'results_uploaded':
        return jsonify({'message': 'لا توجد نتائج لإرسال إشعار عنها'}), 400

    patient    = Patient.query.get(lab_req.patient_id)
    msg_result = f'نتيجة: {lab_req.result_value} {lab_req.result_unit or ""} ({lab_req.result_status or ""})'

    # إشعار المريض
    if patient:
        _notify(
            patient.user_id,
            f'نتائج تحليل "{lab_req.test_name}" جاهزة',
            f'{msg_result}. يرجى مراجعة طبيبك لمناقشة النتائج.',
            'lab_request', lab_req.id,
        )

    # إشعار صاحب الطلب (إذا كان طبيباً أو مختلفاً عن المريض)
    if lab_req.requesting_user_id != (patient.user_id if patient else None):
        _notify(
            lab_req.requesting_user_id,
            f'نتائج التحليل "{lab_req.test_name}" جاهزة',
            f'المريض: {patient.first_name} {patient.last_name if patient else ""}. {msg_result}.',
            'lab_request', lab_req.id,
        )

    lab_req.notified_at = datetime.utcnow()
    lab_req.status      = 'completed'
    db.session.commit()
    return jsonify({'message': 'تم إرسال الإشعارات بنجاح', 'request': lab_req.to_dict()}), 200


# ═══════════════════════════════════════════════════════════
# الأشعة والتصوير الطبي — Radiology Requests
# ═══════════════════════════════════════════════════════════

@lab_radiology_bp.route('/radiology-requests', methods=['POST'])
@token_required
def create_radiology_request(current_user):
    """إنشاء طلب أشعة جديد."""
    data = request.get_json(silent=True) or {}

    if current_user.user_type == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    else:
        patient_id = data.get('patient_id')
        if not patient_id:
            return jsonify({'message': 'معرّف المريض مطلوب'}), 400
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'message': 'المريض غير موجود'}), 404

    if not data.get('scan_type') or not data.get('body_part'):
        return jsonify({'message': 'نوع الأشعة والجزء المصوَّر مطلوبان'}), 400

    rad_req = RadiologyRequest(
        patient_id=patient.id,
        requesting_user_id=current_user.id,
        scan_type=data['scan_type'],
        body_part=data['body_part'],
        urgency=data.get('urgency', 'normal'),
        clinical_reason=data.get('clinical_reason'),
        ordering_doctor=data.get('ordering_doctor'),
        status='requested',
    )
    db.session.add(rad_req)
    db.session.commit()
    return jsonify(rad_req.to_dict()), 201


@lab_radiology_bp.route('/radiology-requests', methods=['GET'])
@token_required
def list_radiology_requests(current_user):
    if current_user.user_type == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify([]), 200
        q = RadiologyRequest.query.filter_by(patient_id=patient.id)
    else:
        q = RadiologyRequest.query

    status_filter = request.args.get('status')
    if status_filter:
        q = q.filter_by(status=status_filter)

    items = q.order_by(RadiologyRequest.created_at.desc()).all()
    return jsonify([r.to_dict() for r in items]), 200


@lab_radiology_bp.route('/radiology-requests/<int:req_id>', methods=['GET'])
@token_required
def get_radiology_request(current_user, req_id):
    rad_req = RadiologyRequest.query.get_or_404(req_id)
    if current_user.user_type == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient or rad_req.patient_id != patient.id:
            return jsonify({'message': 'غير مصرح'}), 403
    return jsonify(rad_req.to_dict()), 200


@lab_radiology_bp.route('/radiology-requests/<int:req_id>/reject', methods=['PUT'])
@token_required
def reject_radiology_request(current_user, req_id):
    if current_user.user_type not in ('admin', 'super_admin', 'radiology_center'):
        return jsonify({'message': 'غير مصرح لك بالرفض'}), 403
    rad_req = RadiologyRequest.query.get_or_404(req_id)
    if rad_req.status != 'requested':
        return jsonify({'message': 'الطلب لا يمكن رفضه في حالته الحالية'}), 400
    data = request.get_json(silent=True) or {}
    rad_req.status           = 'rejected'
    rad_req.rejection_reason = data.get('rejection_reason', '')
    db.session.commit()

    _notify(
        rad_req.requesting_user_id,
        'تم رفض طلب الأشعة',
        f'تم رفض طلب الأشعة "{rad_req.scan_type} - {rad_req.body_part}". السبب: {rad_req.rejection_reason}',
        'radiology_request', rad_req.id,
    )
    db.session.commit()
    return jsonify(rad_req.to_dict()), 200


@lab_radiology_bp.route('/radiology-requests/<int:req_id>/images', methods=['POST'])
@token_required
def upload_radiology_images(current_user, req_id):
    """رفع صور الأشعة — يقبل ملفاً واحداً أو أكثر."""
    rad_req = RadiologyRequest.query.get_or_404(req_id)
    if rad_req.status == 'rejected':
        return jsonify({'message': 'لا يمكن رفع صور لطلب مرفوض'}), 400

    saved_files = []
    files = request.files.getlist('images') or []
    for f in files:
        saved_name, _ = _save_uploaded_file(f, 'radiology_images')
        if saved_name:
            saved_files.append({'name': f.filename, 'path': saved_name})

    existing = rad_req.image_paths
    existing.extend(saved_files)
    rad_req.image_paths_json   = json.dumps(existing)
    rad_req.images_uploaded_at = datetime.utcnow()
    rad_req.images_uploaded_by = current_user.id
    if rad_req.status == 'requested':
        rad_req.status = 'images_uploaded'

    # معلومات إضافية اختيارية
    if request.form.get('facility'):
        rad_req.facility = request.form.get('facility')

    db.session.commit()
    return jsonify(rad_req.to_dict()), 200


@lab_radiology_bp.route('/radiology-requests/<int:req_id>/report', methods=['POST'])
@token_required
def upload_radiology_report(current_user, req_id):
    """رفع تقرير الأشعة (نص + ملف اختياري)."""
    rad_req = RadiologyRequest.query.get_or_404(req_id)
    if rad_req.status == 'rejected':
        return jsonify({'message': 'لا يمكن رفع تقرير لطلب مرفوض'}), 400

    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()

    rad_req.facility          = data.get('facility', rad_req.facility)
    rad_req.radiologist_name  = data.get('radiologist_name')
    rad_req.findings          = data.get('findings')
    rad_req.impression        = data.get('impression')
    rad_req.recommendation    = data.get('recommendation')
    rad_req.report_uploaded_at = datetime.utcnow()
    rad_req.report_uploaded_by = current_user.id
    rad_req.status             = 'report_uploaded'

    if 'report_file' in request.files:
        saved_name, _ = _save_uploaded_file(request.files['report_file'], 'radiology_reports')
        if saved_name:
            rad_req.report_file_path = saved_name
            rad_req.report_file_name = request.files['report_file'].filename

    db.session.commit()
    return jsonify(rad_req.to_dict()), 200


@lab_radiology_bp.route('/radiology-requests/<int:req_id>/share', methods=['POST'])
@token_required
def share_radiology_results(current_user, req_id):
    """مشاركة نتائج الأشعة مع الطبيب والمريض."""
    rad_req = RadiologyRequest.query.get_or_404(req_id)
    if rad_req.status != 'report_uploaded':
        return jsonify({'message': 'لا يوجد تقرير لمشاركته'}), 400

    patient = Patient.query.get(rad_req.patient_id)
    scan_label = f'{rad_req.scan_type} — {rad_req.body_part}'

    if patient:
        _notify(
            patient.user_id,
            f'نتائج أشعة "{scan_label}" جاهزة',
            f'تم رفع تقرير أشعتك. الخلاصة: {rad_req.impression or rad_req.findings or "يرجى المراجعة"}',
            'radiology_request', rad_req.id,
        )

    if rad_req.requesting_user_id != (patient.user_id if patient else None):
        _notify(
            rad_req.requesting_user_id,
            f'نتائج أشعة المريض جاهزة',
            f'أشعة "{scan_label}" للمريض {patient.first_name if patient else ""} {patient.last_name if patient else ""}. '
            f'الخلاصة: {rad_req.impression or rad_req.findings or "—"}',
            'radiology_request', rad_req.id,
        )

    rad_req.shared_at = datetime.utcnow()
    rad_req.status    = 'shared'
    db.session.commit()
    return jsonify({'message': 'تم مشاركة النتائج بنجاح', 'request': rad_req.to_dict()}), 200


# ─────────────────────────────────────────────────────────
# تقديم ملفات مرفوعة
# ─────────────────────────────────────────────────────────
@lab_radiology_bp.route('/uploads/<path:filepath>', methods=['GET'])
@token_required
def serve_upload(current_user, filepath):
    return send_from_directory(UPLOAD_ROOT, filepath)
