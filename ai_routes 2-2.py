"""
مسارات API لخدمات الذكاء الاصطناعي
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from ..services.ai_service import AIService
from ..models.patient import Patient
from ..models.doctor import Doctor
from ..auth import token_required
import json

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

# تهيئة خدمة الذكاء الاصطناعي
ai_service = AIService()

# أنواع الملفات المسموحة للصور الطبية
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'dicom'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB

def allowed_file(filename):
    """فحص امتداد الملف"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ai_bp.route('/analyze-image', methods=['POST'])
@token_required
def analyze_medical_image(current_user):
    """تحليل الصور الطبية"""
    try:
        # فحص وجود الملف
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'لم يتم رفع أي صورة'
            }), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'لم يتم اختيار ملف'
            }), 400
        
        # فحص نوع الملف
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'نوع الملف غير مدعوم'
            }), 400
        
        # فحص حجم الملف
        file_data = file.read()
        if len(file_data) > MAX_FILE_SIZE:
            return jsonify({
                'success': False,
                'error': 'حجم الملف كبير جداً'
            }), 400
        
        # الحصول على معلومات إضافية
        image_type = request.form.get('image_type', 'unknown')
        patient_id = request.form.get('patient_id')
        
        # معلومات المريض (اختيارية)
        patient_info = None
        if patient_id:
            patient = Patient.query.get(patient_id)
            if patient:
                patient_info = {
                    'age': patient.age,
                    'gender': patient.gender,
                    'medical_history': patient.medical_history,
                    'symptoms': request.form.get('symptoms', '')
                }
        
        # تحليل الصورة
        result = ai_service.analyze_medical_image(
            image_data=file_data,
            image_type=image_type,
            patient_info=patient_info
        )
        
        # حفظ النتيجة في قاعدة البيانات (يمكن إضافة نموذج للتحليلات لاحقاً)
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"خطأ في تحليل الصورة: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'حدث خطأ في النظام'
        }), 500

@ai_bp.route('/voice-assistant', methods=['POST'])
@token_required
def voice_assistant(current_user):
    """المساعد الصوتي الذكي"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'الرسالة مطلوبة'
            }), 400
        
        user_message = data['message']
        
        # إعداد السياق
        context = {
            'user_id': current_user.id,
            'user_type': current_user.user_type
        }
        
        # إضافة معلومات المريض إذا كان المستخدم مريضاً
        if current_user.user_type == 'patient':
            patient = Patient.query.filter_by(user_id=current_user.id).first()
            if patient:
                context.update({
                    'age': patient.age,
                    'gender': patient.gender,
                    'medical_history': patient.medical_history,
                    'current_medications': patient.current_medications
                })
        
        # استدعاء المساعد الصوتي
        result = ai_service.voice_assistant(
            user_input=user_message,
            context=context
        )
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"خطأ في المساعد الصوتي: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'حدث خطأ في النظام'
        }), 500

@ai_bp.route('/symptom-checker', methods=['POST'])
@token_required
def symptom_checker(current_user):
    """فحص الأعراض"""
    try:
        data = request.get_json()
        
        if not data or 'symptoms' not in data:
            return jsonify({
                'success': False,
                'error': 'قائمة الأعراض مطلوبة'
            }), 400
        
        symptoms = data['symptoms']
        if not isinstance(symptoms, list) or len(symptoms) == 0:
            return jsonify({
                'success': False,
                'error': 'يجب تقديم قائمة بالأعراض'
            }), 400
        
        # معلومات المريض
        patient_info = None
        if current_user.user_type == 'patient':
            patient = Patient.query.filter_by(user_id=current_user.id).first()
            if patient:
                patient_info = {
                    'age': patient.age,
                    'gender': patient.gender,
                    'medical_history': patient.medical_history
                }
        
        # فحص الأعراض
        result = ai_service.symptom_checker(
            symptoms=symptoms,
            patient_info=patient_info
        )
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"خطأ في فحص الأعراض: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'حدث خطأ في النظام'
        }), 500

@ai_bp.route('/generate-report', methods=['POST'])
@token_required
def generate_medical_report(current_user):
    """إنتاج تقرير طبي"""
    try:
        # فحص صلاحيات الطبيب
        if current_user.user_type != 'doctor':
            return jsonify({
                'success': False,
                'error': 'هذه الخدمة متاحة للأطباء فقط'
            }), 403
        
        data = request.get_json()
        
        if not data or 'patient_id' not in data:
            return jsonify({
                'success': False,
                'error': 'معرف المريض مطلوب'
            }), 400
        
        patient_id = data['patient_id']
        patient = Patient.query.get(patient_id)
        
        if not patient:
            return jsonify({
                'success': False,
                'error': 'المريض غير موجود'
            }), 404
        
        # بيانات المريض
        patient_data = {
            'name': patient.full_name,
            'age': patient.age,
            'gender': patient.gender,
            'medical_history': patient.medical_history,
            'current_medications': patient.current_medications
        }
        
        # نتائج التحاليل (من البيانات المرسلة)
        analysis_results = data.get('analysis_results', [])
        
        # إنتاج التقرير
        result = ai_service.generate_medical_report(
            patient_data=patient_data,
            analysis_results=analysis_results
        )
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"خطأ في إنتاج التقرير: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'حدث خطأ في النظام'
        }), 500

@ai_bp.route('/health-tips', methods=['GET'])
@token_required
def get_health_tips(current_user):
    """الحصول على نصائح صحية مخصصة"""
    try:
        # معلومات المستخدم
        user_info = {}
        if current_user.user_type == 'patient':
            patient = Patient.query.filter_by(user_id=current_user.id).first()
            if patient:
                user_info = {
                    'age': patient.age,
                    'gender': patient.gender,
                    'medical_history': patient.medical_history,
                    'chronic_conditions': patient.chronic_conditions
                }
        
        # إنتاج نصائح مخصصة
        prompt = f"""
        قدم 5 نصائح صحية مخصصة للمستخدم التالي:
        
        معلومات المستخدم:
        - العمر: {user_info.get('age', 'غير محدد')}
        - الجنس: {user_info.get('gender', 'غير محدد')}
        - التاريخ المرضي: {user_info.get('medical_history', 'غير محدد')}
        - الحالات المزمنة: {user_info.get('chronic_conditions', 'لا توجد')}
        
        النصائح يجب أن تكون:
        - عملية وقابلة للتطبيق
        - مناسبة للعمر والحالة الصحية
        - باللغة العربية
        - مختصرة ومفيدة
        """
        
        response = ai_service.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "أنت مستشار صحي متخصص في تقديم نصائح صحية مخصصة."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=600,
            temperature=0.7
        )
        
        tips = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'tips': tips,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"خطأ في الحصول على النصائح: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'حدث خطأ في النظام'
        }), 500

@ai_bp.route('/drug-interaction', methods=['POST'])
@token_required
def check_drug_interaction(current_user):
    """فحص تفاعل الأدوية"""
    try:
        data = request.get_json()
        
        if not data or 'medications' not in data:
            return jsonify({
                'success': False,
                'error': 'قائمة الأدوية مطلوبة'
            }), 400
        
        medications = data['medications']
        if not isinstance(medications, list) or len(medications) < 2:
            return jsonify({
                'success': False,
                'error': 'يجب تقديم دوائين على الأقل للفحص'
            }), 400
        
        # فحص تفاعل الأدوية
        medications_text = "، ".join(medications)
        
        prompt = f"""
        قم بفحص التفاعلات المحتملة بين الأدوية التالية:
        {medications_text}
        
        يرجى تقديم:
        1. التفاعلات المحتملة
        2. مستوى الخطورة لكل تفاعل
        3. الأعراض الجانبية المحتملة
        4. التوصيات والاحتياطات
        5. بدائل آمنة إن وجدت
        
        استخدم اللغة العربية وكن دقيقاً في المعلومات الطبية.
        """
        
        response = ai_service.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "أنت صيدلي متخصص في تفاعلات الأدوية. قدم معلومات دقيقة وموثوقة."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        interaction_analysis = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'analysis': interaction_analysis,
            'medications': medications,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"خطأ في فحص تفاعل الأدوية: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'حدث خطأ في النظام'
        }), 500

@ai_bp.route('/nutrition-advice', methods=['POST'])
@token_required
def get_nutrition_advice(current_user):
    """الحصول على نصائح غذائية مخصصة"""
    try:
        data = request.get_json()
        
        # معلومات المستخدم
        user_info = {}
        if current_user.user_type == 'patient':
            patient = Patient.query.filter_by(user_id=current_user.id).first()
            if patient:
                user_info = {
                    'age': patient.age,
                    'gender': patient.gender,
                    'weight': patient.weight,
                    'height': patient.height,
                    'medical_history': patient.medical_history,
                    'chronic_conditions': patient.chronic_conditions
                }
        
        # معلومات إضافية من الطلب
        goal = data.get('goal', 'تحسين الصحة العامة')  # هدف التغذية
        dietary_restrictions = data.get('dietary_restrictions', [])  # قيود غذائية
        activity_level = data.get('activity_level', 'متوسط')  # مستوى النشاط
        
        prompt = f"""
        قدم خطة غذائية مخصصة للمستخدم التالي:
        
        معلومات المستخدم:
        - العمر: {user_info.get('age', 'غير محدد')}
        - الجنس: {user_info.get('gender', 'غير محدد')}
        - الوزن: {user_info.get('weight', 'غير محدد')} كجم
        - الطول: {user_info.get('height', 'غير محدد')} سم
        - الحالات المزمنة: {user_info.get('chronic_conditions', 'لا توجد')}
        
        الهدف: {goal}
        القيود الغذائية: {', '.join(dietary_restrictions) if dietary_restrictions else 'لا توجد'}
        مستوى النشاط: {activity_level}
        
        يرجى تقديم:
        1. خطة غذائية يومية
        2. الأطعمة المفيدة والمضرة
        3. نصائح للطبخ الصحي
        4. مكملات غذائية مقترحة
        5. نصائح للحفاظ على الوزن المثالي
        """
        
        response = ai_service.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "أنت أخصائي تغذية متخصص في وضع خطط غذائية مخصصة."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1200,
            temperature=0.6
        )
        
        nutrition_advice = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'advice': nutrition_advice,
            'goal': goal,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"خطأ في النصائح الغذائية: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'حدث خطأ في النظام'
        }), 500

