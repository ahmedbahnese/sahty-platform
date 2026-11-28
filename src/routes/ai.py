"""
مسارات API لخدمات الذكاء الاصطناعي
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
import json

from src.routes.auth import token_required, optional_token
from src.models.patient import Patient
from src.models.medication import Medication, MedicationLog
from src.models.user import db
from src.models.ai_usage import AIDailyUsage
from src.services.ai_service import AIService

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

# Lazy singleton — created on first request so missing API key doesn't crash startup
_ai_service = None

def get_ai_service():
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service


@ai_bp.after_request
def _map_provider_limit_to_429(response):
    """A provider free-limit failure surfaces as HTTP 429 (not a 200 with an error body)."""
    if response.is_json:
        body = response.get_json(silent=True) or {}
        if isinstance(body, dict) and body.get('code') == 'ai_provider_limit':
            response.status_code = 429
    return response


# ────────────────────────────────────────────────────
# الحصة اليومية المجانية للذكاء الاصطناعي
# مجانية بالكامل للمستخدم، وتتجدد كل يوم في منتصف الليل
# بتوقيت القاهرة. الحدود: 20 رسالة شات + 5 تحليل صور +
# 10 فحص أعراض يومياً لكل مستخدم (والضيوف بنفس الحدود
# حسب عنوان IP). لا تُحتسب المحاولات الفاشلة.
# ────────────────────────────────────────────────────
CAIRO_TZ = ZoneInfo('Africa/Cairo')

AI_DAILY_LIMITS = {'chat': 20, 'image': 5, 'symptom': 10}
AI_BUCKET_LABELS = {'chat': 'رسائل الشات', 'image': 'تحليل الصور', 'symptom': 'فحص الأعراض'}


def _cairo_today():
    return datetime.now(CAIRO_TZ).date()


def _cairo_next_midnight_iso():
    nxt = datetime.combine(_cairo_today() + timedelta(days=1), time.min, tzinfo=CAIRO_TZ)
    return nxt.isoformat()


def _usage_key(current_user):
    if current_user is not None:
        return {'user_id': current_user.id}
    forwarded = request.headers.get('X-Forwarded-For', '')
    ip = forwarded.split(',')[0].strip() or request.remote_addr or 'unknown'
    return {'guest_key': f'ip:{ip}'}


def _get_or_create_usage(current_user):
    key = _usage_key(current_user)
    today = _cairo_today()
    try:
        row = AIDailyUsage.query.filter_by(usage_date=today, **key).first()
    except Exception:
        # The table may not exist yet if migration 0007 was never applied to
        # this database (the app does not run migrations on Vercel cold start).
        # Create just this table, then retry once instead of failing the request.
        db.session.rollback()
        try:
            AIDailyUsage.__table__.create(db.engine, checkfirst=True)
        except Exception:
            pass
        row = AIDailyUsage.query.filter_by(usage_date=today, **key).first()
    if row is None:
        row = AIDailyUsage(usage_date=today, **key)
        db.session.add(row)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            row = AIDailyUsage.query.filter_by(usage_date=today, **key).first()
    return row


def _usage_payload(current_user):
    row = _get_or_create_usage(current_user)
    out = {}
    for bucket, limit in AI_DAILY_LIMITS.items():
        used = getattr(row, f'{bucket}_count')
        out[bucket] = {'used': used, 'limit': limit, 'remaining': max(0, limit - used)}
    out['resets_at'] = _cairo_next_midnight_iso()
    out['date'] = str(_cairo_today())
    return out


def _require_quota(current_user, bucket):
    """Return a 429 response if today's free quota for the bucket is used up."""
    row = _get_or_create_usage(current_user)
    if getattr(row, f'{bucket}_count') >= AI_DAILY_LIMITS[bucket]:
        return jsonify({
            'success': False,
            'code': 'ai_daily_limit',
            'error': (
                f"وصلت إلى حدك اليومي المجاني من {AI_BUCKET_LABELS[bucket]} "
                f"({AI_DAILY_LIMITS[bucket]} يومياً). تتجدد الحصة غداً في منتصف الليل بتوقيت القاهرة، "
                f"وباقي خدمات التطبيق (الدليل، الحجوزات، الأدوية) تعمل بدون حدود.",
            ),
            'bucket': bucket,
            'limit': AI_DAILY_LIMITS[bucket],
            'used': getattr(row, f'{bucket}_count'),
            'resets_at': _cairo_next_midnight_iso(),
        }), 429
    return None


def _consume_quota(current_user, bucket):
    row = _get_or_create_usage(current_user)
    setattr(row, f'{bucket}_count', getattr(row, f'{bucket}_count') + 1)
    db.session.commit()

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
ALLOWED_AUDIO_EXTENSIONS = {'webm', 'mp3', 'wav', 'ogg', 'm4a', 'flac'}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


def _allowed(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set


@ai_bp.before_request
def require_clinical_ai_review():
    """Do not expose unvalidated clinical AI workflows by default."""
    if request.path == '/api/ai/usage':
        return None
    if (
        current_app.config.get('SAHTY_PRODUCTION_LIKE', False)
        and not current_app.config.get('SAHTY_CLINICAL_AI_ENABLED', False)
    ):
        return jsonify({
            'success': False,
            'code': 'clinical_ai_unavailable',
            'error': 'خدمات الذكاء الاصطناعي الطبي غير متاحة حالياً حتى استكمال مراجعة السلامة والخصوصية.',
        }), 503


@ai_bp.route('/usage', methods=['GET'])
@optional_token
def ai_usage(current_user):
    """الحصة اليومية المجانية المتبقية — تتجدد في منتصف الليل بتوقيت القاهرة."""
    return jsonify({'success': True, 'usage': _usage_payload(current_user)})


# ────────────────────────────────────────────────────
# المساعد الذكي (نصي)
# ────────────────────────────────────────────────────
def _build_chat_context(current_user):
    """Build patient context dict for AI calls. Safe to call with current_user=None."""
    if current_user is None:
        return {'user_id': None, 'user_type': 'guest'}
    context = {'user_id': current_user.id, 'user_type': current_user.user_type}
    if current_user.user_type == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if patient:
            from datetime import date
            age = (date.today() - patient.date_of_birth).days // 365 if patient.date_of_birth else None
            context.update({'age': age, 'gender': patient.gender, 'blood_type': patient.blood_type})
    return context


@ai_bp.route('/chat', methods=['POST'])
@token_required
def ai_chat(current_user):
    """المساعد الطبي الذكي - نصي مع دعم سياق المحادثة"""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': 'الرسالة مطلوبة'}), 400

    # history: [{'role': 'user'|'assistant', 'content': '...'}] — اختياري
    history = data.get('history', [])
    if not isinstance(history, list):
        history = []

    quota_error = _require_quota(current_user, 'chat')
    if quota_error:
        return quota_error
    result = get_ai_service().voice_assistant(
        data['message'],
        _build_chat_context(current_user),
        history=history,
    )
    if result.get('success'):
        _consume_quota(current_user, 'chat')
    return jsonify(result)


# backward-compat alias — works with or without login
@ai_bp.route('/voice-assistant', methods=['POST'])
@optional_token
def voice_assistant(current_user):
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': 'الرسالة مطلوبة'}), 400
    history = data.get('history', [])
    if not isinstance(history, list):
        history = []
    quota_error = _require_quota(current_user, 'chat')
    if quota_error:
        return quota_error
    result = get_ai_service().voice_assistant(
        data['message'],
        _build_chat_context(current_user),
        history=history,
    )
    if result.get('success'):
        _consume_quota(current_user, 'chat')
    return jsonify(result)


# ────────────────────────────────────────────────────
# تحليل الصور الطبية
# ────────────────────────────────────────────────────
@ai_bp.route('/analyze-image', methods=['POST'])
@token_required
def analyze_medical_image(current_user):
    """تحليل الصور الطبية"""
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'لم يتم رفع أي صورة'}), 400

    file = request.files['image']
    if not file.filename or not _allowed(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        return jsonify({'success': False, 'error': 'نوع الملف غير مدعوم'}), 400

    file_data = file.read()
    if len(file_data) > MAX_FILE_SIZE:
        return jsonify({'success': False, 'error': 'حجم الملف كبير جداً (الحد 20 MB)'}), 400

    image_type = request.form.get('image_type', 'general')
    patient_info = None

    if current_user.user_type == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if patient:
            from datetime import date
            age = (date.today() - patient.date_of_birth).days // 365 if patient.date_of_birth else None
            patient_info = {
                'age': age,
                'gender': patient.gender,
                'symptoms': request.form.get('symptoms', '')
            }

    quota_error = _require_quota(current_user, 'image')
    if quota_error:
        return quota_error
    result = get_ai_service().analyze_medical_image(file_data, image_type, patient_info)
    if result.get('success'):
        _consume_quota(current_user, 'image')
    return jsonify(result)


# ────────────────────────────────────────────────────
# تحليل الصوت
# ────────────────────────────────────────────────────
@ai_bp.route('/analyze-voice', methods=['POST'])
@token_required
def analyze_voice(current_user):
    """تحليل الصوت وتحويله إلى نص ثم معالجته طبياً"""
    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': 'لم يتم رفع أي ملف صوتي'}), 400

    file = request.files['audio']
    if not file.filename or not _allowed(file.filename, ALLOWED_AUDIO_EXTENSIONS):
        return jsonify({'success': False, 'error': 'صيغة الصوت غير مدعومة'}), 400

    audio_data = file.read()
    if len(audio_data) > MAX_FILE_SIZE:
        return jsonify({'success': False, 'error': 'حجم الملف كبير جداً'}), 400

    context = {}
    if current_user.user_type == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if patient:
            from datetime import date
            age = (date.today() - patient.date_of_birth).days // 365 if patient.date_of_birth else None
            context = {'age': age, 'gender': patient.gender}

    quota_error = _require_quota(current_user, 'chat')
    if quota_error:
        return quota_error
    result = get_ai_service().analyze_voice(audio_data, context)
    if result.get('success'):
        _consume_quota(current_user, 'chat')
    return jsonify(result)


# ────────────────────────────────────────────────────
# اقتراح التشخيص (فحص الأعراض)
# ────────────────────────────────────────────────────
@ai_bp.route('/symptom-checker', methods=['POST'])
@token_required
def symptom_checker(current_user):
    """فحص الأعراض واقتراح التشخيص — متاح للضيوف أيضاً"""
    data = request.get_json()
    if not data or 'symptoms' not in data:
        return jsonify({'success': False, 'error': 'الأعراض مطلوبة'}), 400

    symptoms = data['symptoms']
    if isinstance(symptoms, str):
        symptoms = [s.strip() for s in symptoms.split('،') if s.strip()]

    patient_info = None
    if current_user and current_user.user_type == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if patient:
            from datetime import date
            age = (date.today() - patient.date_of_birth).days // 365 if patient.date_of_birth else None
            patient_info = {
                'age': age,
                'gender': patient.gender,
                'medical_history': data.get('medical_history', '')
            }

    quota_error = _require_quota(current_user, 'symptom')
    if quota_error:
        return quota_error
    result = get_ai_service().symptom_checker(symptoms, patient_info)
    if result.get('success'):
        _consume_quota(current_user, 'symptom')
    return jsonify(result)


# ────────────────────────────────────────────────────
# متابعة الأدوية - تحليل ذكي
# ────────────────────────────────────────────────────
@ai_bp.route('/medication-adherence', methods=['GET'])
@token_required
def medication_adherence(current_user):
    """تحليل التزام المريض بالأدوية"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'success': False, 'error': 'ملف المريض غير موجود'}), 404

    medications = Medication.query.filter_by(patient_id=patient.id, is_active=True).all()
    logs = MedicationLog.query.filter_by(patient_id=patient.id).order_by(
        MedicationLog.scheduled_time.desc()
    ).limit(50).all()

    meds_data = [m.to_dict() for m in medications]
    logs_data = [l.to_dict() for l in logs]

    quota_error = _require_quota(current_user, 'symptom')
    if quota_error:
        return quota_error
    result = get_ai_service().analyze_medication_adherence(logs_data, meds_data)
    if result.get('success'):
        _consume_quota(current_user, 'symptom')
    return jsonify(result)


@ai_bp.route('/drug-interaction', methods=['POST'])
@optional_token
def drug_interaction(current_user):
    """فحص تفاعلات الأدوية — متاح للضيوف أيضاً"""
    data = request.get_json()
    if not data or 'medications' not in data:
        return jsonify({'success': False, 'error': 'قائمة الأدوية مطلوبة'}), 400

    quota_error = _require_quota(current_user, 'symptom')
    if quota_error:
        return quota_error
    result = get_ai_service().check_drug_interactions(data['medications'])
    if result.get('success'):
        _consume_quota(current_user, 'symptom')
    return jsonify(result)


# ────────────────────────────────────────────────────
# تقرير صحي شامل
# ────────────────────────────────────────────────────
@ai_bp.route('/health-report', methods=['GET'])
@token_required
def health_report(current_user):
    """إنتاج تقرير صحي شامل"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'success': False, 'error': 'ملف المريض غير موجود'}), 404

    from datetime import date
    age = (date.today() - patient.date_of_birth).days // 365 if patient.date_of_birth else None

    meds = Medication.query.filter_by(patient_id=patient.id, is_active=True).all()
    med_names = [m.name for m in meds]

    patient_data = {
        'name': f"{patient.first_name} {patient.last_name}",
        'age': age,
        'gender': 'ذكر' if patient.gender == 'male' else 'أنثى',
        'blood_type': patient.blood_type,
        'medications': '، '.join(med_names) if med_names else 'لا توجد',
    }

    quota_error = _require_quota(current_user, 'symptom')
    if quota_error:
        return quota_error
    result = get_ai_service().generate_health_report(patient_data)
    if result.get('success'):
        _consume_quota(current_user, 'symptom')
    return jsonify(result)


# ────────────────────────────────────────────────────
# تحليل المستندات الطبية (تقارير، وصفات، نتائج)
# ────────────────────────────────────────────────────
@ai_bp.route('/analyze-document', methods=['POST'])
@optional_token
def analyze_medical_document(current_user):
    """
    تحليل مستند طبي مرفوع كصورة: تقرير مخبري، أشعة، وصفة، تقرير عام.
    يشرح المحتوى بلغة مبسطة ويبرز القيم غير الطبيعية.
    doc_type: lab | radiology | prescription | general
    """
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'لم يتم رفع أي ملف'}), 400

    file = request.files['file']
    if not file.filename or not _allowed(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        return jsonify({'success': False, 'error': 'نوع الملف غير مدعوم (PNG, JPG, JPEG, WEBP)'}), 400

    file_data = file.read()
    if len(file_data) > MAX_FILE_SIZE:
        return jsonify({'success': False, 'error': 'حجم الملف كبير جداً (الحد 20 MB)'}), 400

    doc_type = request.form.get('doc_type', 'general')
    patient_info = None
    if current_user and current_user.user_type == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if patient:
            from datetime import date
            age = (date.today() - patient.date_of_birth).days // 365 if patient.date_of_birth else None
            patient_info = {'age': age, 'gender': patient.gender}

    quota_error = _require_quota(current_user, 'image')
    if quota_error:
        return quota_error
    result = get_ai_service().analyze_medical_document(file_data, doc_type, patient_info)
    if result.get('success'):
        _consume_quota(current_user, 'image')
    return jsonify(result)


# ────────────────────────────────────────────────────
# فحص الأعراض المتطور مع أسئلة متابعة وصور
# ────────────────────────────────────────────────────
@ai_bp.route('/symptom-checker-v2', methods=['POST'])
@optional_token
def symptom_checker_v2(current_user):
    """
    فحص الأعراض المتطور: يدعم الصور + محادثة متعددة الأدوار + أسئلة متابعة.
    """
    # يمكن إرسال بيانات كـ multipart (مع صورة) أو JSON (بدون صورة)
    image_data = None
    if 'image' in request.files:
        img_file = request.files['image']
        if img_file and _allowed(img_file.filename or '', ALLOWED_IMAGE_EXTENSIONS):
            image_data = img_file.read()
            if len(image_data) > MAX_FILE_SIZE:
                image_data = None

    if request.content_type and 'multipart' in request.content_type:
        symptoms_raw = request.form.get('symptoms', '[]')
        history_raw = request.form.get('history', '[]')
        medical_history = request.form.get('medical_history', '')
        try:
            import json as _json
            symptoms = _json.loads(symptoms_raw) if symptoms_raw.startswith('[') else [symptoms_raw]
            history = _json.loads(history_raw) if history_raw.startswith('[') else []
        except Exception:
            symptoms = [symptoms_raw] if symptoms_raw else []
            history = []
    else:
        data = request.get_json() or {}
        symptoms = data.get('symptoms', [])
        if isinstance(symptoms, str):
            symptoms = [s.strip() for s in symptoms.split('،') if s.strip()]
        history = data.get('history', [])
        medical_history = data.get('medical_history', '')

    if not symptoms:
        return jsonify({'success': False, 'error': 'الأعراض مطلوبة'}), 400

    patient_info = None
    if current_user and current_user.user_type == 'patient':
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if patient:
            from datetime import date
            age = (date.today() - patient.date_of_birth).days // 365 if patient.date_of_birth else None
            patient_info = {'age': age, 'gender': patient.gender, 'medical_history': medical_history}

    quota_error = _require_quota(current_user, 'symptom')
    if quota_error:
        return quota_error
    if image_data:
        quota_error = _require_quota(current_user, 'image')
        if quota_error:
            return quota_error
    result = get_ai_service().symptom_checker_with_followup(
        symptoms=symptoms,
        patient_info=patient_info,
        conversation_history=history,
        image_data=image_data,
    )
    if result.get('success'):
        _consume_quota(current_user, 'symptom')
        if image_data:
            _consume_quota(current_user, 'image')
    return jsonify(result)


# ────────────────────────────────────────────────────
# نصائح صحية عامة
# ────────────────────────────────────────────────────
@ai_bp.route('/health-tips', methods=['GET'])
@token_required
def health_tips(current_user):
    """نصائح صحية مخصصة"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()

    context = {}
    if patient:
        from datetime import date
        age = (date.today() - patient.date_of_birth).days // 365 if patient.date_of_birth else None
        context = {'age': age, 'gender': patient.gender, 'blood_type': patient.blood_type}

    gender_txt = 'ذكر' if context.get('gender') == 'male' else 'أنثى'
    prompt = (
        f"قدم 5 نصائح صحية مخصصة لشخص عمره {context.get('age','غير محدد')} سنة "
        f"جنسه {gender_txt}. النصائح يجب أن تكون عملية وقابلة للتطبيق اليومي."
    )

    quota_error = _require_quota(current_user, 'chat')
    if quota_error:
        return quota_error
    result = get_ai_service().voice_assistant(prompt, context)
    if result.get('response'):
        _consume_quota(current_user, 'chat')
    return jsonify({
        'success': True,
        'tips': result.get('response', ''),
        'timestamp': datetime.now().isoformat()
    })


