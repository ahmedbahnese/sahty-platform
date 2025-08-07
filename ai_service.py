"""
خدمة الذكاء الاصطناعي لتحليل الصور الطبية والمساعد الصوتي
"""

import os
import base64
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import openai
from PIL import Image
import io
import numpy as np
from flask import current_app

class AIService:
    def __init__(self):
        """تهيئة خدمة الذكاء الاصطناعي"""
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE')
        )
        
    def analyze_medical_image(self, image_data: bytes, image_type: str, patient_info: Dict = None) -> Dict:
        """
        تحليل الصور الطبية باستخدام الذكاء الاصطناعي
        
        Args:
            image_data: بيانات الصورة
            image_type: نوع الصورة (x-ray, ct, mri, ultrasound, etc.)
            patient_info: معلومات المريض الاختيارية
            
        Returns:
            Dict: نتائج التحليل
        """
        try:
            # تحويل الصورة إلى base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # إعداد الرسالة للذكاء الاصطناعي
            messages = [
                {
                    "role": "system",
                    "content": """أنت طبيب أشعة متخصص في تحليل الصور الطبية. 
                    قم بتحليل الصورة المرفقة وقدم تقريراً طبياً مفصلاً باللغة العربية يتضمن:
                    1. وصف الصورة ونوعها
                    2. الملاحظات الطبيعية
                    3. أي تشوهات أو علامات غير طبيعية
                    4. التشخيص المحتمل
                    5. التوصيات للخطوات التالية
                    
                    تذكر أن هذا التحليل للمساعدة فقط ولا يغني عن استشارة طبيب مختص."""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"قم بتحليل هذه الصورة الطبية من نوع: {image_type}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # إضافة معلومات المريض إذا توفرت
            if patient_info:
                patient_context = f"""
                معلومات المريض:
                - العمر: {patient_info.get('age', 'غير محدد')}
                - الجنس: {patient_info.get('gender', 'غير محدد')}
                - الأعراض: {patient_info.get('symptoms', 'غير محددة')}
                - التاريخ المرضي: {patient_info.get('medical_history', 'غير محدد')}
                """
                messages[1]["content"][0]["text"] += f"\n\n{patient_context}"
            
            # استدعاء API
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=1500,
                temperature=0.3
            )
            
            analysis_result = response.choices[0].message.content
            
            # تحليل إضافي للصورة
            image_analysis = self._analyze_image_properties(image_data)
            
            return {
                'success': True,
                'analysis': analysis_result,
                'image_properties': image_analysis,
                'image_type': image_type,
                'timestamp': datetime.now().isoformat(),
                'confidence_score': 0.85,  # يمكن تحسينه لاحقاً
                'recommendations': self._extract_recommendations(analysis_result),
                'urgency_level': self._assess_urgency(analysis_result)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تحليل الصورة الطبية: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _analyze_image_properties(self, image_data: bytes) -> Dict:
        """تحليل خصائص الصورة التقنية"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            return {
                'width': image.width,
                'height': image.height,
                'format': image.format,
                'mode': image.mode,
                'size_kb': len(image_data) / 1024,
                'aspect_ratio': round(image.width / image.height, 2)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _extract_recommendations(self, analysis_text: str) -> List[str]:
        """استخراج التوصيات من نص التحليل"""
        recommendations = []
        
        # البحث عن كلمات مفتاحية للتوصيات
        recommendation_keywords = [
            'يُنصح', 'يُوصى', 'يجب', 'ينبغي', 'من المهم',
            'التوصية', 'الخطوة التالية', 'المتابعة'
        ]
        
        lines = analysis_text.split('\n')
        for line in lines:
            for keyword in recommendation_keywords:
                if keyword in line:
                    recommendations.append(line.strip())
                    break
        
        return recommendations
    
    def _assess_urgency(self, analysis_text: str) -> str:
        """تقييم مستوى الإلحاح من نص التحليل"""
        urgent_keywords = ['عاجل', 'فوري', 'طارئ', 'خطير', 'حرج']
        moderate_keywords = ['متابعة', 'مراقبة', 'فحص إضافي']
        
        text_lower = analysis_text.lower()
        
        for keyword in urgent_keywords:
            if keyword in text_lower:
                return 'عاجل'
        
        for keyword in moderate_keywords:
            if keyword in text_lower:
                return 'متوسط'
        
        return 'عادي'
    
    def voice_assistant(self, user_input: str, context: Dict = None) -> Dict:
        """
        المساعد الصوتي الذكي للاستشارات الطبية
        
        Args:
            user_input: النص المدخل من المستخدم
            context: السياق والمعلومات الإضافية
            
        Returns:
            Dict: الرد والتوصيات
        """
        try:
            # إعداد السياق للمساعد الطبي
            system_prompt = """أنت مساعد طبي ذكي متخصص في تقديم المشورة الطبية الأولية باللغة العربية.
            
            مهامك:
            1. الإجابة على الأسئلة الطبية العامة
            2. تقديم نصائح صحية أولية
            3. توجيه المرضى للتخصص المناسب
            4. تقييم مستوى الإلحاح للحالات
            5. تقديم معلومات عن الأدوية والعلاجات
            
            قواعد مهمة:
            - لا تقدم تشخيصاً نهائياً
            - انصح دائماً بمراجعة طبيب مختص
            - كن حذراً مع الحالات الطارئة
            - استخدم لغة بسيطة ومفهومة
            - اطلب معلومات إضافية عند الحاجة"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            # إضافة السياق إذا توفر
            if context:
                context_text = f"""
                معلومات إضافية:
                - عمر المستخدم: {context.get('age', 'غير محدد')}
                - الجنس: {context.get('gender', 'غير محدد')}
                - التاريخ المرضي: {context.get('medical_history', 'غير محدد')}
                - الأدوية الحالية: {context.get('current_medications', 'لا توجد')}
                """
                messages.append({"role": "system", "content": context_text})
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )
            
            assistant_response = response.choices[0].message.content
            
            # تحليل الرد لاستخراج معلومات إضافية
            analysis = self._analyze_assistant_response(assistant_response)
            
            return {
                'success': True,
                'response': assistant_response,
                'urgency_level': analysis['urgency_level'],
                'recommended_specialty': analysis['recommended_specialty'],
                'follow_up_needed': analysis['follow_up_needed'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في المساعد الصوتي: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'response': 'عذراً، حدث خطأ في النظام. يرجى المحاولة مرة أخرى.',
                'timestamp': datetime.now().isoformat()
            }
    
    def _analyze_assistant_response(self, response_text: str) -> Dict:
        """تحليل رد المساعد لاستخراج معلومات إضافية"""
        analysis = {
            'urgency_level': 'عادي',
            'recommended_specialty': None,
            'follow_up_needed': False
        }
        
        # تحديد مستوى الإلحاح
        urgent_keywords = ['فوري', 'عاجل', 'طوارئ', 'خطير']
        for keyword in urgent_keywords:
            if keyword in response_text:
                analysis['urgency_level'] = 'عاجل'
                break
        
        # تحديد التخصص المطلوب
        specialties = {
            'قلب': ['قلب', 'صدر', 'دورة دموية'],
            'عظام': ['عظام', 'مفاصل', 'كسور'],
            'أطفال': ['أطفال', 'طفل', 'رضيع'],
            'نساء': ['نساء', 'حمل', 'ولادة'],
            'عيون': ['عيون', 'بصر', 'نظر'],
            'أنف وأذن': ['أنف', 'أذن', 'حنجرة'],
            'جلدية': ['جلد', 'حساسية', 'طفح'],
            'نفسية': ['نفسي', 'اكتئاب', 'قلق']
        }
        
        for specialty, keywords in specialties.items():
            for keyword in keywords:
                if keyword in response_text:
                    analysis['recommended_specialty'] = specialty
                    break
        
        # تحديد الحاجة للمتابعة
        follow_up_keywords = ['متابعة', 'مراجعة', 'فحص', 'تحليل']
        for keyword in follow_up_keywords:
            if keyword in response_text:
                analysis['follow_up_needed'] = True
                break
        
        return analysis
    
    def symptom_checker(self, symptoms: List[str], patient_info: Dict = None) -> Dict:
        """
        فحص الأعراض وتقديم تقييم أولي
        
        Args:
            symptoms: قائمة الأعراض
            patient_info: معلومات المريض
            
        Returns:
            Dict: التقييم والتوصيات
        """
        try:
            symptoms_text = "، ".join(symptoms)
            
            prompt = f"""
            قم بتحليل الأعراض التالية وقدم تقييماً أولياً:
            الأعراض: {symptoms_text}
            
            يرجى تقديم:
            1. الحالات المحتملة (مرتبة حسب الاحتمالية)
            2. مستوى الإلحاح
            3. التخصص الطبي المناسب
            4. نصائح أولية
            5. علامات الخطر التي تستدعي التدخل الفوري
            """
            
            if patient_info:
                prompt += f"""
                
                معلومات المريض:
                - العمر: {patient_info.get('age', 'غير محدد')}
                - الجنس: {patient_info.get('gender', 'غير محدد')}
                - التاريخ المرضي: {patient_info.get('medical_history', 'غير محدد')}
                """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "أنت طبيب متخصص في التشخيص الأولي. قدم تحليلاً دقيقاً ومفيداً باللغة العربية."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.5
            )
            
            analysis = response.choices[0].message.content
            
            return {
                'success': True,
                'analysis': analysis,
                'symptoms': symptoms,
                'urgency_assessment': self._assess_urgency(analysis),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في فحص الأعراض: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_medical_report(self, patient_data: Dict, analysis_results: List[Dict]) -> Dict:
        """
        إنتاج تقرير طبي شامل
        
        Args:
            patient_data: بيانات المريض
            analysis_results: نتائج التحاليل والفحوصات
            
        Returns:
            Dict: التقرير الطبي المُنتج
        """
        try:
            # تجميع البيانات
            report_data = {
                'patient_info': patient_data,
                'analysis_results': analysis_results,
                'generated_at': datetime.now().isoformat()
            }
            
            # إنتاج التقرير باستخدام الذكاء الاصطناعي
            prompt = f"""
            قم بإنتاج تقرير طبي شامل باللغة العربية بناءً على البيانات التالية:
            
            بيانات المريض:
            - الاسم: {patient_data.get('name', 'غير محدد')}
            - العمر: {patient_data.get('age', 'غير محدد')}
            - الجنس: {patient_data.get('gender', 'غير محدد')}
            - التاريخ المرضي: {patient_data.get('medical_history', 'غير محدد')}
            
            نتائج الفحوصات:
            {json.dumps(analysis_results, ensure_ascii=False, indent=2)}
            
            يجب أن يتضمن التقرير:
            1. ملخص الحالة
            2. نتائج الفحوصات
            3. التشخيص
            4. خطة العلاج
            5. التوصيات
            6. المتابعة المطلوبة
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "أنت طبيب متخصص في كتابة التقارير الطبية. اكتب تقريراً مهنياً ومفصلاً."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.3
            )
            
            report_content = response.choices[0].message.content
            
            return {
                'success': True,
                'report': report_content,
                'report_data': report_data,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنتاج التقرير الطبي: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

