"""
مسارات API لخدمات الذكاء الاصطناعي
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
import json

from src.routes.auth import token_required, optional_token
from src.models.patient import Patient
from src.models.medication import Medication, MedicationLog
from src.models.user import db
from src.services.ai_service import AIService

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

# Lazy singleton — created on first request so missing API key doesn't crash startup
_ai_service = None

def get_ai_service():
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
ALLOWED_AUDIO_EXTENSIONS = {'webm', 'mp3', 'wav', 'ogg', 'm4a', 'flac'}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


def _allowed(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set


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
@optional_token
def ai_chat(current_user):
    """المساعد الطبي الذكي - نصي مع دعم سياق المحادثة"""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': 'الرسالة مطلوبة'}), 400

    # history: [{'role': 'user'|'assistant', 'content': '...'}] — اختياري
    history = data.get('history', [])
    if not isinstance(history, list):
        history = []

    result = get_ai_service().voice_assistant(
        data['message'],
        _build_chat_context(current_user),
        history=history,
    )
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
    result = get_ai_service().voice_assistant(
        data['message'],
        _build_chat_context(current_user),
        history=history,
    )
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

    result = get_ai_service().analyze_medical_image(file_data, image_type, patient_info)
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

    result = get_ai_service().analyze_voice(audio_data, context)
    return jsonify(result)


# ────────────────────────────────────────────────────
# اقتراح التشخيص (فحص الأعراض)
# ────────────────────────────────────────────────────
@ai_bp.route('/symptom-checker', methods=['POST'])
@optional_token
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

    result = get_ai_service().symptom_checker(symptoms, patient_info)
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

    result = get_ai_service().analyze_medication_adherence(logs_data, meds_data)
    return jsonify(result)


@ai_bp.route('/drug-interaction', methods=['POST'])
@optional_token
def drug_interaction(current_user):
    """فحص تفاعلات الأدوية — متاح للضيوف أيضاً"""
    data = request.get_json()
    if not data or 'medications' not in data:
        return jsonify({'success': False, 'error': 'قائمة الأدوية مطلوبة'}), 400

    result = get_ai_service().check_drug_interactions(data['medications'])
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

    result = get_ai_service().generate_health_report(patient_data)
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

    result = get_ai_service().analyze_medical_document(file_data, doc_type, patient_info)
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

    result = get_ai_service().symptom_checker_with_followup(
        symptoms=symptoms,
        patient_info=patient_info,
        conversation_history=history,
        image_data=image_data,
    )
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

    result = get_ai_service().voice_assistant(prompt, context)
    return jsonify({
        'success': True,
        'tips': result.get('response', ''),
        'timestamp': datetime.now().isoformat()
    })
