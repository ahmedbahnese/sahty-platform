"""
خدمة الذكاء الاصطناعي لتحليل الصور الطبية والمساعد الذكي
"""

import os
import base64
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import openai
from PIL import Image
import io
from flask import current_app


class AIService:
    def __init__(self):
        """تهيئة خدمة الذكاء الاصطناعي (lazy — client created on first use)"""
        self._client = None

    @property
    def client(self):
        if self._client is None:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError(
                    'OPENAI_API_KEY غير محدد. '
                    'يرجى إضافة مفتاح OpenAI في الإعدادات لاستخدام ميزات الذكاء الاصطناعي.'
                )
            base_url = os.getenv('OPENAI_API_BASE')
            kwargs = {'api_key': api_key}
            if base_url:
                kwargs['base_url'] = base_url
            self._client = openai.OpenAI(**kwargs)
        return self._client

    # ──────────────────────────────────────────────
    # تحليل الصور الطبية
    # ──────────────────────────────────────────────
    def analyze_medical_image(self, image_data: bytes, image_type: str, patient_info: Dict = None) -> Dict:
        """تحليل الصور الطبية باستخدام الذكاء الاصطناعي"""
        try:
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            messages = [
                {
                    "role": "system",
                    "content": (
                        "أنت طبيب أشعة متخصص في تحليل الصور الطبية. "
                        "قم بتحليل الصورة المرفقة وقدم تقريراً طبياً مفصلاً باللغة العربية يتضمن:\n"
                        "1. وصف الصورة ونوعها\n"
                        "2. الملاحظات الطبيعية\n"
                        "3. أي تشوهات أو علامات غير طبيعية\n"
                        "4. التشخيص المحتمل\n"
                        "5. التوصيات للخطوات التالية\n\n"
                        "تذكر أن هذا التحليل للمساعدة فقط ولا يغني عن استشارة طبيب مختص."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"قم بتحليل هذه الصورة الطبية من نوع: {image_type}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ]

            if patient_info:
                patient_context = (
                    f"\n\nمعلومات المريض:\n"
                    f"- العمر: {patient_info.get('age', 'غير محدد')}\n"
                    f"- الجنس: {patient_info.get('gender', 'غير محدد')}\n"
                    f"- الأعراض: {patient_info.get('symptoms', 'غير محددة')}\n"
                    f"- التاريخ المرضي: {patient_info.get('medical_history', 'غير محدد')}"
                )
                messages[1]["content"][0]["text"] += patient_context

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1500,
                temperature=0.3
            )

            analysis_result = response.choices[0].message.content
            image_analysis = self._analyze_image_properties(image_data)

            return {
                'success': True,
                'analysis': analysis_result,
                'image_properties': image_analysis,
                'image_type': image_type,
                'timestamp': datetime.now().isoformat(),
                'confidence_score': 0.85,
                'recommendations': self._extract_recommendations(analysis_result),
                'urgency_level': self._assess_urgency(analysis_result)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _analyze_image_properties(self, image_data: bytes) -> Dict:
        try:
            image = Image.open(io.BytesIO(image_data))
            return {
                'width': image.width,
                'height': image.height,
                'format': image.format,
                'mode': image.mode,
                'size_kb': round(len(image_data) / 1024, 2),
                'aspect_ratio': round(image.width / image.height, 2)
            }
        except Exception as e:
            return {'error': str(e)}

    def _extract_recommendations(self, analysis_text: str) -> List[str]:
        recommendations = []
        keywords = ['يُنصح', 'يُوصى', 'يجب', 'ينبغي', 'من المهم', 'التوصية', 'الخطوة التالية', 'المتابعة']
        for line in analysis_text.split('\n'):
            for kw in keywords:
                if kw in line:
                    recommendations.append(line.strip())
                    break
        return recommendations

    def _assess_urgency(self, analysis_text: str) -> str:
        urgent = ['عاجل', 'فوري', 'طارئ', 'خطير', 'حرج']
        moderate = ['متابعة', 'مراقبة', 'فحص إضافي']
        for kw in urgent:
            if kw in analysis_text:
                return 'عاجل'
        for kw in moderate:
            if kw in analysis_text:
                return 'متوسط'
        return 'عادي'

    # ──────────────────────────────────────────────
    # المساعد الذكي
    # ──────────────────────────────────────────────
    def voice_assistant(self, user_input: str, context: Dict = None,
                        history: List[Dict] = None) -> Dict:
        """
        المساعد الذكي للاستشارات الطبية مع دعم سياق المحادثة متعددة الأدوار.
        history: قائمة رسائل سابقة بصيغة [{'role': 'user'|'assistant', 'content': '...'}]
        """
        try:
            system_prompt = (
                "أنت مساعد طبي ذكي متخصص في تقديم المشورة الطبية الأولية باللغة العربية.\n\n"
                "مهامك:\n"
                "1. الإجابة على الأسئلة الطبية العامة\n"
                "2. تقديم نصائح صحية أولية\n"
                "3. توجيه المرضى للتخصص المناسب\n"
                "4. تقييم مستوى الإلحاح للحالات\n"
                "5. تقديم معلومات عن الأدوية والعلاجات\n\n"
                "قواعد: لا تقدم تشخيصاً نهائياً، انصح دائماً بمراجعة طبيب مختص."
            )

            messages = [{"role": "system", "content": system_prompt}]

            if context:
                ctx = (
                    f"معلومات المستخدم: عمر={context.get('age','غير محدد')}, "
                    f"جنس={context.get('gender','غير محدد')}, "
                    f"تاريخ مرضي={context.get('medical_history','غير محدد')}, "
                    f"أدوية حالية={context.get('current_medications','لا توجد')}"
                )
                messages.append({"role": "system", "content": ctx})

            # إضافة سياق المحادثة السابقة (حتى 10 رسائل للتوازن بين السياق والتكلفة)
            if history:
                for msg in history[-10:]:
                    role = msg.get('role')
                    content = msg.get('content', '')
                    if role in ('user', 'assistant') and content:
                        messages.append({"role": role, "content": content})

            messages.append({"role": "user", "content": user_input})

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )

            assistant_response = response.choices[0].message.content
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
            return {
                'success': False,
                'error': str(e),
                'response': 'عذراً، حدث خطأ في النظام. يرجى المحاولة مرة أخرى.',
                'timestamp': datetime.now().isoformat()
            }

    def _analyze_assistant_response(self, response_text: str) -> Dict:
        analysis = {'urgency_level': 'عادي', 'recommended_specialty': None, 'follow_up_needed': False}
        for kw in ['فوري', 'عاجل', 'طوارئ', 'خطير']:
            if kw in response_text:
                analysis['urgency_level'] = 'عاجل'
                break
        specialties = {
            'قلب': ['قلب', 'صدر', 'دورة دموية'],
            'عظام': ['عظام', 'مفاصل', 'كسور'],
            'أطفال': ['أطفال', 'طفل', 'رضيع'],
            'نساء': ['نساء', 'حمل', 'ولادة'],
            'عيون': ['عيون', 'بصر'],
            'جلدية': ['جلد', 'حساسية', 'طفح'],
            'نفسية': ['نفسي', 'اكتئاب', 'قلق'],
            'باطنية': ['سكر', 'ضغط', 'كلى', 'كبد']
        }
        for specialty, keywords in specialties.items():
            for kw in keywords:
                if kw in response_text:
                    analysis['recommended_specialty'] = specialty
                    break
        for kw in ['متابعة', 'مراجعة', 'فحص', 'تحليل']:
            if kw in response_text:
                analysis['follow_up_needed'] = True
                break
        return analysis

    # ──────────────────────────────────────────────
    # فحص الأعراض واقتراح التشخيص
    # ──────────────────────────────────────────────
    def symptom_checker(self, symptoms: List[str], patient_info: Dict = None) -> Dict:
        """فحص الأعراض وتقديم تقييم أولي مع اقتراح التشخيص"""
        try:
            symptoms_text = "، ".join(symptoms)

            prompt = (
                f"قم بتحليل الأعراض التالية وقدم تقييماً أولياً:\n"
                f"الأعراض: {symptoms_text}\n\n"
                "يرجى تقديم:\n"
                "1. الحالات المحتملة مرتبة حسب الاحتمالية مع نسبة مئوية\n"
                "2. مستوى الإلحاح (عاجل/متوسط/عادي)\n"
                "3. التخصص الطبي المناسب\n"
                "4. نصائح أولية يمكن اتباعها الآن\n"
                "5. علامات الخطر التي تستدعي التدخل الفوري"
            )

            if patient_info:
                prompt += (
                    f"\n\nمعلومات المريض:\n"
                    f"- العمر: {patient_info.get('age', 'غير محدد')}\n"
                    f"- الجنس: {patient_info.get('gender', 'غير محدد')}\n"
                    f"- التاريخ المرضي: {patient_info.get('medical_history', 'غير محدد')}"
                )

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "أنت طبيب متخصص في التشخيص الأولي. قدم تحليلاً دقيقاً ومفيداً باللغة العربية."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,
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
            return {'success': False, 'error': str(e), 'timestamp': datetime.now().isoformat()}

    # ──────────────────────────────────────────────
    # تحليل الصوت
    # ──────────────────────────────────────────────
    def analyze_voice(self, audio_data: bytes, context: Dict = None) -> Dict:
        """تحليل الصوت وتحويله إلى نص ثم معالجته طبياً"""
        try:
            # تحويل الصوت إلى نص باستخدام Whisper
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.webm"

            transcript_response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ar"
            )

            transcribed_text = transcript_response.text

            # معالجة النص المُحوَّل كمحادثة طبية
            assistant_result = self.voice_assistant(transcribed_text, context)

            return {
                'success': True,
                'transcribed_text': transcribed_text,
                'response': assistant_result.get('response', ''),
                'urgency_level': assistant_result.get('urgency_level', 'عادي'),
                'recommended_specialty': assistant_result.get('recommended_specialty'),
                'follow_up_needed': assistant_result.get('follow_up_needed', False),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'timestamp': datetime.now().isoformat()}

    # ──────────────────────────────────────────────
    # متابعة الأدوية بالذكاء الاصطناعي
    # ──────────────────────────────────────────────
    def analyze_medication_adherence(self, medication_logs: List[Dict], medications: List[Dict]) -> Dict:
        """تحليل التزام المريض بالأدوية وتقديم توصيات"""
        try:
            meds_summary = json.dumps(medications, ensure_ascii=False, indent=2)
            logs_summary = json.dumps(medication_logs[-20:] if len(medication_logs) > 20 else medication_logs,
                                      ensure_ascii=False, indent=2)

            prompt = (
                f"قم بتحليل التزام المريض بالأدوية بناءً على البيانات التالية:\n\n"
                f"الأدوية الموصوفة:\n{meds_summary}\n\n"
                f"سجل التناول الأخير:\n{logs_summary}\n\n"
                "قدم:\n"
                "1. نسبة الالتزام الإجمالية\n"
                "2. الأدوية التي يُفوِّتها المريض بشكل متكرر\n"
                "3. أسباب محتملة للتقصير\n"
                "4. توصيات عملية لتحسين الالتزام\n"
                "5. تحذيرات صحية إذا وُجدت"
            )

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "أنت صيدلاني ومتخصص في إدارة الأدوية. قدم تقييماً دقيقاً باللغة العربية."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.4
            )

            analysis = response.choices[0].message.content

            return {
                'success': True,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'timestamp': datetime.now().isoformat()}

    def check_drug_interactions(self, medications: List[str]) -> Dict:
        """فحص تفاعلات الأدوية"""
        try:
            meds_text = "، ".join(medications)

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "أنت صيدلاني متخصص في فحص تفاعلات الأدوية. قدم تحليلاً دقيقاً باللغة العربية."},
                    {"role": "user", "content": (
                        f"قم بفحص التفاعلات بين الأدوية التالية: {meds_text}\n\n"
                        "قدم:\n1. التفاعلات الخطيرة إن وجدت\n"
                        "2. التفاعلات المتوسطة\n3. توصيات التعامل\n4. بدائل مقترحة إذا لزم"
                    )}
                ],
                max_tokens=800,
                temperature=0.3
            )

            analysis = response.choices[0].message.content

            return {
                'success': True,
                'analysis': analysis,
                'medications': medications,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'timestamp': datetime.now().isoformat()}

    # ──────────────────────────────────────────────
    # Family Health Manager - تحليل صحة الأسرة
    # ──────────────────────────────────────────────
    def analyze_family_health(self, family_members: List[Dict]) -> Dict:
        """تحليل الصحة العامة للأسرة وتقديم توصيات"""
        try:
            family_data = json.dumps(family_members, ensure_ascii=False, indent=2)

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "أنت طبيب أسرة متخصص في الرعاية الصحية الشاملة. قدم تحليلاً دقيقاً باللغة العربية."},
                    {"role": "user", "content": (
                        f"قم بتحليل الوضع الصحي للأسرة بناءً على البيانات التالية:\n{family_data}\n\n"
                        "قدم:\n"
                        "1. ملخص الوضع الصحي لكل فرد\n"
                        "2. الأمراض المشتركة في الأسرة (الوراثية المحتملة)\n"
                        "3. التوصيات الوقائية لكل فرد حسب عمره\n"
                        "4. الفحوصات الدورية المقترحة\n"
                        "5. نمط الحياة الصحي المناسب للأسرة"
                    )}
                ],
                max_tokens=1500,
                temperature=0.5
            )

            analysis = response.choices[0].message.content

            return {
                'success': True,
                'analysis': analysis,
                'members_count': len(family_members),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'timestamp': datetime.now().isoformat()}

    def generate_health_report(self, patient_data: Dict) -> Dict:
        """إنتاج تقرير صحي شامل"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "أنت طبيب متخصص في كتابة التقارير الطبية الشاملة باللغة العربية."},
                    {"role": "user", "content": (
                        f"أنتج تقريراً صحياً شاملاً للمريض:\n"
                        f"الاسم: {patient_data.get('name','غير محدد')}\n"
                        f"العمر: {patient_data.get('age','غير محدد')}\n"
                        f"الجنس: {patient_data.get('gender','غير محدد')}\n"
                        f"الأمراض المزمنة: {patient_data.get('chronic_diseases','لا توجد')}\n"
                        f"الأدوية الحالية: {patient_data.get('medications','لا توجد')}\n"
                        f"آخر فحص: {patient_data.get('last_checkup','غير معروف')}\n\n"
                        "التقرير يشمل: ملخص الحالة، التوصيات، الفحوصات المطلوبة، نمط الحياة المقترح."
                    )}
                ],
                max_tokens=1200,
                temperature=0.3
            )

            return {
                'success': True,
                'report': response.choices[0].message.content,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'timestamp': datetime.now().isoformat()}
