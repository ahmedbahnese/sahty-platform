"""
مسارات API لنظام طلبات التحاليل المخبرية والأشعة.

التحاليل:
  POST   /api/lab-requests                    — إنشاء طلب (يدعم تحاليل متعددة + رفع وثيقة + تحصيل منزلي)
  GET    /api/lab-requests                    — قائمة الطلبات (بحسب الدور)
  GET    /api/lab-requests/<id>               — تفاصيل طلب
  PUT    /api/lab-requests/<id>/approve       — اعتماد الطلب
  PUT    /api/lab-requests/<id>/reject        — رفض الطلب
  POST   /api/lab-requests/<id>/results       — رفع النتائج (multipart)
  POST   /api/lab-requests/<id>/notify        — إرسال الإشعارات + حفظ في السجل الطبي

الأشعة:
  POST   /api/radiology-requests              — إنشاء طلب (يدعم رفع وثيقة + مركز + موعد)
  GET    /api/radiology-requests              — قائمة الطلبات
  GET    /api/radiology-requests/<id>         — تفاصيل طلب
  PUT    /api/radiology-requests/<id>/reject  — رفض
  POST   /api/radiology-requests/<id>/images  — رفع الصور (multipart)
  POST   /api/radiology-requests/<id>/report  — رفع التقرير
  POST   /api/radiology-requests/<id>/share   — مشاركة النتائج + إشعار + حفظ في السجل الطبي
"""
import os
import json
import uuid
from datetime import datetime, date
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename

from src.models.user    import db, User
from src.models.patient import Patient
from src.models.notification import Notification
from src.models.lab_radiology import LabRequest, RadiologyRequest
from src.models.medical_record import LabTest, Radiology
from src.models.egypt_healthcare import HealthcareDirectoryRecord
from src.routes.auth import token_required, current_role, has_active_role

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
    if current_role(user) == 'patient':
        return Patient.query.filter_by(user_id=user.id).first()
    return None


def _parse_bool(value):
    return value in (True, 'true', '1', 'yes', 'on')


def _parse_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except (TypeError, ValueError):
        return None


def _validate_directory_center(name, facility_type):
    """لا تسمح الطلبات بمراكز مكتوبة عشوائياً إذا كان الدليل المستورد متاحاً."""
    name = (name or '').strip()
    if not name:
        return None
    record = HealthcareDirectoryRecord.query.filter(
        HealthcareDirectoryRecord.facility_type == facility_type,
        HealthcareDirectoryRecord.name_ar == name,
    ).first()
    if record:
        return record.name_ar
    # قواعد البيانات القديمة قد لا تحتوي على الاسم العربي نفسه؛ نقبل المطابقة الجزئية
    record = HealthcareDirectoryRecord.query.filter(
        HealthcareDirectoryRecord.facility_type == facility_type,
        db.or_(
            HealthcareDirectoryRecord.name_ar.ilike(f'%{name}%'),
            HealthcareDirectoryRecord.name_en.ilike(f'%{name}%'),
        ),
    ).first()
    return record.name_ar if record else None


# تعليمات التحضير لكل نوع تحليل
LAB_PREPARATION = {
    'فصم الدم': 'صيام 8 ساعات قبل التحليل.',
    'سكر صيام': 'صيام 8-12 ساعة كاملة قبل التحليل.',
    'سكر تحمّل': 'صيام 12 ساعة. الامتناع عن أي طعام أو شراب عدا الماء.',
    'كولسترول': 'صيام 12 ساعة قبل التحليل.',
    'دهون ثلاثية': 'صيام 12 ساعة. تجنّب الدهون 24 ساعة قبل التحليل.',
    'وظائف الكبد': 'صيام 8 ساعات. تجنّب الكحول 24 ساعة قبل التحليل.',
    'وظائف الكلى': 'شرب كميات وفيرة من الماء قبل التحليل.',
    'تحليل البول': 'جمع عينة البول الأولى صباحاً.',
    'كورتيزول': 'جمع العينة في الصباح الباكر (8-9 صباحاً).',
    'هرمونات': 'صيام 8 ساعات. ذكر الأدوية الحالية للطبيب.',
    'بروتين': 'صيام 8 ساعات.',
    'فيتامين': 'صيام 8 ساعات قبل التحليل.',
    'مزرعة': 'جمع العينة قبل أخذ المضادات الحيوية.',
}

def _get_preparation_instructions(tests):
    """استخراج تعليمات التحضير بناءً على قائمة التحاليل."""
    instructions = set()
    for t in tests:
        name = t.get('name', '') if isinstance(t, dict) else str(t)
        for keyword, instr in LAB_PREPARATION.items():
            if keyword in name:
                instructions.add(instr)
    if not instructions:
        instructions.add('اتبع تعليمات طبيبك. أبلغ المختبر بأي أدوية تتناولها.')
    return list(instructions)


# ═══════════════════════════════════════════════════════════
# التحاليل المخبرية — Lab Requests
# ═══════════════════════════════════════════════════════════

@lab_radiology_bp.route('/lab-requests', methods=['POST'])
@token_required
def create_lab_request(current_user):
    """إنشاء طلب تحليل جديد — يدعم multipart لرفع وثيقة الطلب."""
    # يقبل JSON أو form-data
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()

    # تحديد المريض
    if current_role(current_user) == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    else:
        return jsonify({'message': 'يجب إنشاء طلب التحليل من حساب المريض'}), 403

    # التحاليل — قائمة JSON أو اسم واحد
    tests_raw = data.get('tests_json') or data.get('tests', '[]')
    if isinstance(tests_raw, str):
        try:
            tests = json.loads(tests_raw)
        except Exception:
            tests = []
    else:
        tests = tests_raw if isinstance(tests_raw, list) else []

    # اسم التحليل (للتوافق العكسي)
    test_name = data.get('test_name') or (tests[0].get('name') if tests else None)
    if not test_name:
        return jsonify({'message': 'اسم التحليل مطلوب'}), 400

    if data.get('lab_center_name'):
        center = _validate_directory_center(data.get('lab_center_name'), 'Laboratory')
        if HealthcareDirectoryRecord.query.filter_by(facility_type='Laboratory').first() and not center:
            return jsonify({'message': 'اختر مركز تحاليل من الدليل الطبي الفعلي'}), 400
        data['lab_center_name'] = center or data.get('lab_center_name')

    # تعليمات التحضير
    prep_instructions = _get_preparation_instructions(tests or [{'name': test_name}])

    # التحصيل المنزلي
    home_collection = data.get('home_collection') in (True, 'true', '1', 'yes')
    collection_date = None
    if data.get('collection_date'):
        try:
            collection_date = date.fromisoformat(data['collection_date'])
        except Exception:
            pass

    scheduled_dt = None
    if data.get('scheduled_datetime'):
        try:
            scheduled_dt = datetime.fromisoformat(data['scheduled_datetime'])
        except Exception:
            pass

    lab_req = LabRequest(
        patient_id=patient.id,
        requesting_user_id=current_user.id,
        test_name=test_name,
        tests_json=json.dumps(tests, ensure_ascii=False),
        test_category=data.get('test_category'),
        urgency=data.get('urgency', 'routine'),
        clinical_notes=data.get('clinical_notes'),
        ordering_doctor=data.get('ordering_doctor'),
        lab_center_name=data.get('lab_center_name'),
        preparation_instructions=json.dumps(prep_instructions, ensure_ascii=False),
        preparation_notes=data.get('preparation_notes'),
        scheduled_datetime=scheduled_dt,
        home_collection=home_collection,
        collection_address=data.get('collection_address'),
        collection_lat=float(data['collection_lat']) if data.get('collection_lat') else None,
        collection_lng=float(data['collection_lng']) if data.get('collection_lng') else None,
        collection_date=collection_date,
        collection_time=data.get('collection_time'),
        collection_staff_name=data.get('collection_staff_name'),
        status='requested',
    )
    db.session.add(lab_req)
    db.session.flush()

    # رفع وثيقة الطلب الأصلي
    if 'request_doc' in request.files:
        saved_name, _ = _save_uploaded_file(request.files['request_doc'], 'lab_request_docs')
        if saved_name:
            lab_req.request_doc_path = saved_name
            lab_req.request_doc_name = request.files['request_doc'].filename

    db.session.commit()

    # إشعار المريض بتأكيد الطلب
    _notify(
        patient.user_id,
        'تم إرسال طلب التحليل',
        f'تم إرسال طلب تحليل "{test_name}" بنجاح. ستتلقى إشعاراً عند الاعتماد.',
        'lab_request', lab_req.id,
    )
    db.session.commit()
    return jsonify(lab_req.to_dict()), 201


def _owned_request(current_user, model, req_id):
    item = model.query.get_or_404(req_id)
    role = current_role(current_user)
    if role == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient or item.patient_id != patient.id:
            return None
    elif role not in ('admin', 'super_admin') and item.requesting_user_id != current_user.id:
        return None
    return item


@lab_radiology_bp.route('/lab-requests/<int:req_id>', methods=['PUT'])
@token_required
def update_lab_request(current_user, req_id):
    item = _owned_request(current_user, LabRequest, req_id)
    if not item:
        return jsonify({'message': 'غير مصرح'}), 403
    if item.status not in ('requested', 'approved'):
        return jsonify({'message': 'لا يمكن تعديل طلب مكتمل أو مرفوض'}), 400
    data = request.get_json(silent=True) or {}
    tests = data.get('tests', item.tests)
    if not isinstance(tests, list) or not tests or any(not isinstance(t, dict) or not t.get('name') for t in tests):
        return jsonify({'message': 'يجب إدخال تحليل واحد على الأقل'}), 400
    item.tests_json = json.dumps(tests, ensure_ascii=False)
    item.test_name = tests[0]['name']
    item.test_category = tests[0].get('category', item.test_category)
    item.preparation_instructions = json.dumps(
        _get_preparation_instructions(tests), ensure_ascii=False
    )
    for field in ('urgency', 'clinical_notes', 'ordering_doctor', 'lab_center_name',
                  'preparation_notes', 'collection_address', 'collection_time',
                  'collection_staff_name'):
        if field in data:
            setattr(item, field, data[field])
    if 'home_collection' in data:
        item.home_collection = bool(data['home_collection'])
    if 'scheduled_datetime' in data:
        item.scheduled_datetime = _parse_datetime(data['scheduled_datetime'])
    if 'collection_date' in data:
        try:
            item.collection_date = date.fromisoformat(data['collection_date']) if data['collection_date'] else None
        except ValueError:
            return jsonify({'message': 'تاريخ السحب غير صالح'}), 400
    db.session.commit()
    return jsonify(item.to_dict())


@lab_radiology_bp.route('/lab-requests/<int:req_id>', methods=['DELETE'])
@token_required
def delete_lab_request(current_user, req_id):
    item = _owned_request(current_user, LabRequest, req_id)
    if not item:
        return jsonify({'message': 'غير مصرح'}), 403
    if item.status not in ('requested', 'rejected'):
        return jsonify({'message': 'لا يمكن حذف طلب تمت معالجته'}), 400
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'تم حذف الطلب'})


@lab_radiology_bp.route('/lab-requests', methods=['GET'])
@token_required
def list_lab_requests(current_user):
    """قائمة الطلبات — بحسب دور المستخدم."""
    if current_role(current_user) == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify([]), 200
        requests_q = LabRequest.query.filter_by(patient_id=patient.id)
    elif current_role(current_user) in ('admin', 'super_admin'):
        requests_q = LabRequest.query
    else:
        requests_q = LabRequest.query.filter_by(requesting_user_id=current_user.id)

    status_filter = request.args.get('status')
    if status_filter:
        requests_q = requests_q.filter_by(status=status_filter)

    items = requests_q.order_by(LabRequest.created_at.desc()).all()
    return jsonify([r.to_dict() for r in items]), 200


@lab_radiology_bp.route('/lab-requests/<int:req_id>', methods=['GET'])
@token_required
def get_lab_request(current_user, req_id):
    lab_req = LabRequest.query.get_or_404(req_id)
    if current_role(current_user) == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient or lab_req.patient_id != patient.id:
            return jsonify({'message': 'غير مصرح'}), 403
    elif current_role(current_user) not in ('admin', 'super_admin') and lab_req.requesting_user_id != current_user.id:
        return jsonify({'message': 'غير مصرح'}), 403
    return jsonify(lab_req.to_dict()), 200


@lab_radiology_bp.route('/lab-requests/<int:req_id>/approve', methods=['PUT'])
@token_required
def approve_lab_request(current_user, req_id):
    """اعتماد طلب التحليل — للمختبر أو المسؤول."""
    if current_role(current_user) not in ('admin', 'super_admin', 'laboratory', 'lab'):
        return jsonify({'message': 'غير مصرح لك بالاعتماد'}), 403
    lab_req = _owned_request(current_user, LabRequest, req_id)
    if not lab_req or (
        current_role(current_user) not in ('admin', 'super_admin', 'laboratory', 'lab')
        and lab_req.requesting_user_id != current_user.id
    ):
        return jsonify({'message': 'غير مصرح'}), 403
    if lab_req.status != 'requested':
        return jsonify({'message': f'الطلب بحالة "{lab_req.status}" ولا يمكن اعتماده'}), 400
    data = request.get_json(silent=True) or {}
    lab_req.status              = 'approved'
    lab_req.approved_by_user_id = current_user.id
    lab_req.approved_at         = datetime.utcnow()
    lab_req.approval_notes      = data.get('approval_notes', '')
    if data.get('collection_staff_name'):
        lab_req.collection_staff_name = data['collection_staff_name']
    db.session.commit()

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
    if not (
        has_active_role(current_user, 'admin', 'super_admin', 'laboratory', 'lab')
    ):
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
    lab_req = _owned_request(current_user, LabRequest, req_id)
    if not lab_req:
        return jsonify({'message': 'غير مصرح'}), 403
    if lab_req.status == 'rejected':
        return jsonify({'message': 'لا يمكن رفع نتائج لطلب مرفوض'}), 400

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
    """إرسال إشعار بنتائج التحليل للطبيب والمريض + حفظ في السجل الطبي."""
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

    # ── حفظ في السجل الطبي تلقائياً ──────────────────────
    if patient:
        try:
            lab_test = LabTest(
                patient_id=patient.id,
                test_name=lab_req.test_name,
                test_category=lab_req.test_category,
                test_date=date.today(),
                lab_name=lab_req.lab_name or lab_req.lab_center_name,
                ordering_doctor=lab_req.ordering_doctor,
                result_value=lab_req.result_value,
                unit=lab_req.result_unit,
                reference_range=lab_req.reference_range,
                status=lab_req.result_status or 'normal',
                interpretation=lab_req.result_interpretation,
                notes=f'مرجع طلب التحليل: #{lab_req.id}',
            )
            db.session.add(lab_test)
        except Exception:
            pass   # لا تفشل الإشعار بسبب خطأ في السجل الطبي

    db.session.commit()
    return jsonify({'message': 'تم إرسال الإشعارات بنجاح', 'request': lab_req.to_dict()}), 200


# ═══════════════════════════════════════════════════════════
# الأشعة والتصوير الطبي — Radiology Requests
# ═══════════════════════════════════════════════════════════

@lab_radiology_bp.route('/radiology-requests', methods=['POST'])
@token_required
def create_radiology_request(current_user):
    """إنشاء طلب أشعة جديد — يدعم رفع وثيقة الطلب + مركز + موعد."""
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()

    if current_role(current_user) == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    else:
        return jsonify({'message': 'يجب إنشاء طلب الأشعة من حساب المريض'}), 403

    if not data.get('scan_type') or not data.get('body_part'):
        return jsonify({'message': 'نوع الأشعة والجزء المصوَّر مطلوبان'}), 400

    if data.get('radiology_center_name'):
        center = _validate_directory_center(data.get('radiology_center_name'), 'Radiology Center')
        if HealthcareDirectoryRecord.query.filter_by(facility_type='Radiology Center').first() and not center:
            return jsonify({'message': 'اختر مركز أشعة من الدليل الطبي الفعلي'}), 400
        data['radiology_center_name'] = center or data.get('radiology_center_name')

    try:
        patient_weight = float(data['patient_weight']) if data.get('patient_weight') else None
    except (TypeError, ValueError):
        return jsonify({'message': 'وزن المريض غير صالح'}), 400
    checklist = data.get('preparation_checklist', [])
    if isinstance(checklist, str):
        try:
            checklist = json.loads(checklist)
        except Exception:
            checklist = [checklist] if checklist else []
    if not isinstance(checklist, list):
        checklist = []

    scheduled_dt = None
    if data.get('scheduled_datetime'):
        try:
            scheduled_dt = datetime.fromisoformat(data['scheduled_datetime'])
        except Exception:
            pass

    rad_req = RadiologyRequest(
        patient_id=patient.id,
        requesting_user_id=current_user.id,
        scan_type=data['scan_type'],
        body_part=data['body_part'],
        urgency=data.get('urgency', 'routine'),
        clinical_reason=data.get('clinical_reason'),
        ordering_doctor=data.get('ordering_doctor'),
        radiology_center_name=data.get('radiology_center_name'),
        scheduled_datetime=scheduled_dt,
        body_part_code=data.get('body_part_code'),
        patient_weight=patient_weight,
        requires_sedation=_parse_bool(data.get('requires_sedation')),
        uses_contrast=_parse_bool(data.get('uses_contrast')),
        preparation_required=_parse_bool(data.get('preparation_required')),
        preparation_checklist_json=json.dumps(checklist, ensure_ascii=False),
        status='requested',
    )
    db.session.add(rad_req)
    db.session.flush()

    # رفع وثيقة الطلب الأصلي (PDF/صورة)
    if 'request_doc' in request.files:
        saved_name, _ = _save_uploaded_file(request.files['request_doc'], 'radiology_request_docs')
        if saved_name:
            rad_req.request_doc_path = saved_name
            rad_req.request_doc_name = request.files['request_doc'].filename

    db.session.commit()

    # إشعار المريض بتأكيد الطلب
    _notify(
        patient.user_id,
        'تم إرسال طلب الأشعة',
        f'تم إرسال طلب أشعة "{data["scan_type"]} — {data["body_part"]}" بنجاح.',
        'radiology_request', rad_req.id,
    )
    db.session.commit()
    return jsonify(rad_req.to_dict()), 201


@lab_radiology_bp.route('/radiology-requests/<int:req_id>', methods=['PUT'])
@token_required
def update_radiology_request(current_user, req_id):
    item = _owned_request(current_user, RadiologyRequest, req_id)
    if not item:
        return jsonify({'message': 'غير مصرح'}), 403
    if item.status not in ('requested',):
        return jsonify({'message': 'لا يمكن تعديل طلب تمت معالجته'}), 400
    data = request.get_json(silent=True) or {}
    for field in ('scan_type', 'body_part', 'body_part_code', 'urgency', 'clinical_reason',
                  'ordering_doctor', 'radiology_center_name'):
        if field in data and data[field] is not None:
            setattr(item, field, data[field])
    if 'patient_weight' in data:
        try:
            item.patient_weight = float(data['patient_weight']) if data['patient_weight'] else None
        except (TypeError, ValueError):
            return jsonify({'message': 'وزن المريض غير صالح'}), 400
    for field in ('requires_sedation', 'uses_contrast', 'preparation_required'):
        if field in data:
            setattr(item, field, _parse_bool(data[field]))
    if 'preparation_checklist' in data:
        item.preparation_checklist_json = json.dumps(data['preparation_checklist'] or [], ensure_ascii=False)
    if 'scheduled_datetime' in data:
        item.scheduled_datetime = _parse_datetime(data['scheduled_datetime'])
    db.session.commit()
    return jsonify(item.to_dict())


@lab_radiology_bp.route('/radiology-requests/<int:req_id>', methods=['DELETE'])
@token_required
def delete_radiology_request(current_user, req_id):
    item = _owned_request(current_user, RadiologyRequest, req_id)
    if not item:
        return jsonify({'message': 'غير مصرح'}), 403
    if item.status not in ('requested', 'rejected'):
        return jsonify({'message': 'لا يمكن حذف طلب تمت معالجته'}), 400
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'تم حذف الطلب'})


@lab_radiology_bp.route('/radiology-requests', methods=['GET'])
@token_required
def list_radiology_requests(current_user):
    if current_role(current_user) == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify([]), 200
        q = RadiologyRequest.query.filter_by(patient_id=patient.id)
    elif current_role(current_user) in ('admin', 'super_admin'):
        q = RadiologyRequest.query
    else:
        q = RadiologyRequest.query.filter_by(requesting_user_id=current_user.id)

    status_filter = request.args.get('status')
    if status_filter:
        q = q.filter_by(status=status_filter)

    items = q.order_by(RadiologyRequest.created_at.desc()).all()
    return jsonify([r.to_dict() for r in items]), 200


@lab_radiology_bp.route('/radiology-requests/<int:req_id>', methods=['GET'])
@token_required
def get_radiology_request(current_user, req_id):
    rad_req = RadiologyRequest.query.get_or_404(req_id)
    if current_role(current_user) == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient or rad_req.patient_id != patient.id:
            return jsonify({'message': 'غير مصرح'}), 403
    elif current_role(current_user) not in ('admin', 'super_admin') and rad_req.requesting_user_id != current_user.id:
        return jsonify({'message': 'غير مصرح'}), 403
    return jsonify(rad_req.to_dict()), 200


@lab_radiology_bp.route('/radiology-requests/<int:req_id>/reject', methods=['PUT'])
@token_required
def reject_radiology_request(current_user, req_id):
    if current_role(current_user) not in ('admin', 'super_admin', 'radiology_center'):
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
    rad_req = _owned_request(current_user, RadiologyRequest, req_id)
    if not rad_req:
        return jsonify({'message': 'غير مصرح'}), 403
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

    if request.form.get('facility'):
        rad_req.facility = request.form.get('facility')

    db.session.commit()
    return jsonify(rad_req.to_dict()), 200


@lab_radiology_bp.route('/radiology-requests/<int:req_id>/report', methods=['POST'])
@token_required
def upload_radiology_report(current_user, req_id):
    """رفع تقرير الأشعة (نص + ملف اختياري)."""
    rad_req = _owned_request(current_user, RadiologyRequest, req_id)
    if not rad_req:
        return jsonify({'message': 'غير مصرح'}), 403
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
    """مشاركة نتائج الأشعة مع الطبيب والمريض + حفظ في السجل الطبي."""
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
            'نتائج أشعة المريض جاهزة',
            f'أشعة "{scan_label}" للمريض {patient.first_name if patient else ""} {patient.last_name if patient else ""}. '
            f'الخلاصة: {rad_req.impression or rad_req.findings or "—"}',
            'radiology_request', rad_req.id,
        )

    rad_req.shared_at = datetime.utcnow()
    rad_req.status    = 'shared'

    # ── حفظ في السجل الطبي تلقائياً ──────────────────────
    if patient:
        try:
            radiology_record = Radiology(
                patient_id=patient.id,
                scan_type=rad_req.scan_type,
                body_part=rad_req.body_part,
                scan_date=date.today(),
                facility=rad_req.facility or rad_req.radiology_center_name,
                ordering_doctor=rad_req.ordering_doctor,
                radiologist=rad_req.radiologist_name,
                findings=rad_req.findings,
                impression=rad_req.impression,
                recommendation=rad_req.recommendation,
                notes=f'مرجع طلب الأشعة: #{rad_req.id}',
            )
            db.session.add(radiology_record)
        except Exception:
            pass

    db.session.commit()
    return jsonify({'message': 'تم مشاركة النتائج بنجاح', 'request': rad_req.to_dict()}), 200


# ─────────────────────────────────────────────────────────
# تقديم ملفات مرفوعة
# ─────────────────────────────────────────────────────────
@lab_radiology_bp.route('/uploads/<path:filepath>', methods=['GET'])
@token_required
def serve_upload(current_user, filepath):
    # Upload URLs are not capabilities. Resolve the stored path back to its
    # owning object before serving anything from disk.
    normalized = os.path.normpath(filepath)
    if normalized.startswith('..') or os.path.isabs(normalized):
        return jsonify({'message': 'الملف غير موجود'}), 404

    authorized = False
    for model in (LabRequest, RadiologyRequest):
        for item in model.query.all():
            paths = []
            if isinstance(item, LabRequest):
                for field, folder in (
                    ('request_doc_path', 'lab_request_docs'),
                    ('result_file_path', 'lab_results'),
                ):
                    value = getattr(item, field, None)
                    if value:
                        paths.append(f'{folder}/{value}')
            else:
                for field, folder in (
                    ('request_doc_path', 'radiology_request_docs'),
                    ('report_file_path', 'radiology_reports'),
                ):
                    value = getattr(item, field, None)
                    if value:
                        paths.append(f'{folder}/{value}')
                paths.extend(
                    f"radiology_images/{image.get('path')}"
                    for image in item.image_paths
                    if isinstance(image, dict) and image.get('path')
                )
            if normalized in [p for p in paths if p]:
                patient = Patient.query.get(item.patient_id)
                authorized = bool(
                    current_role(current_user) in ('admin', 'super_admin')
                    or (patient and patient.user_id == current_user.id)
                    or item.requesting_user_id == current_user.id
                )
                break
        if authorized:
            break

    if not authorized:
        from src.models.medication import PharmacyOrder
        order = next((
            item for item in PharmacyOrder.query.all()
            if item.prescription_image_path
            and normalized == f"prescription_images/{item.prescription_image_path}"
        ), None)
        if order:
            patient = Patient.query.get(order.patient_id)
            authorized = bool(
                current_role(current_user) in ('admin', 'super_admin')
                or (patient and patient.user_id == current_user.id)
                or (current_role(current_user) == 'pharmacy'
                    and order.preferred_pharmacy_id in (None, current_user.id))
            )

    if not authorized:
        return jsonify({'message': 'غير مصرح بالوصول إلى الملف'}), 403
    return send_from_directory(UPLOAD_ROOT, filepath)
