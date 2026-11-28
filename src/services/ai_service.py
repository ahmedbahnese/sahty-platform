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


# ──────────────────────────────────────────────
# مزوّدو الذكاء الاصطناعي (مجانيون، متوافقون مع OpenAI)
# ──────────────────────────────────────────────
# Gemini أساسي (شات + صور + أعراض) وGroq احتياطي + صوت (Whisper).
# OpenAI يبقى خياراً للتوافق مع الإعداد القديم.
# اختيار المزوّد من متغيرات البيئة:
#   AI_PRIMARY_PROVIDER  (الافتراضي: gemini)
#   AI_FALLBACK_PROVIDER (الافتراضي: groq)
# المفاتيح: GEMINI_API_KEY / GROQ_API_KEY / OPENAI_API_KEY.
# المزوّد الذي ليس له مفتاح يُتخطَّى بصمت.
PROVIDERS = {
    'gemini': {
        'base_url': 'https://generativelanguage.googleapis.com/v1beta/openai/',
        'key_env': 'GEMINI_API_KEY',
        'chat_model': 'gemini-2.0-flash',
        'vision_model': 'gemini-2.0-flash',
        'voice_model': None,  # واجهة OpenAI المتوافقة من Gemini لا تدعم تحويل الصوت إلى نص
    },
    'groq': {
        'base_url': 'https://api.groq.com/openai/v1',
        'key_env': 'GROQ_API_KEY',
        'chat_model': 'llama-3.3-70b-versatile',
        'vision_model': 'meta-llama/llama-4-scout-17b-16e-instruct',
        'voice_model': 'whisper-large-v3-turbo',
    },
    'openai': {
        'base_url': None,  # يُؤخذ من OPENAI_API_BASE أو الافتراضي لدى OpenAI
        'key_env': 'OPENAI_API_KEY',
        'chat_model': 'gpt-4o',
        'vision_model': 'gpt-4o',
        'voice_model': 'whisper-1',
    },
}

_MODEL_KEY = {'chat': 'chat_model', 'vision': 'vision_model', 'voice': 'voice_model'}
_FREE_LIMIT_MESSAGE = (
    'انتهت الحصة المجانية لدى مزوّد الذكاء الاصطناعي. '
    'حاول غداً بعد تجدد الحد المجاني.'
)


class _AIProviderLimitError(Exception):
    """Raised when a provider reports its free quota/rate limit is exhausted."""


def _is_rate_limit_error(exc: BaseException) -> bool:
    """True when an exception looks like a provider rate-limit/quota failure."""
    if isinstance(exc, getattr(openai, 'RateLimitError', ())):
        return True
    if getattr(exc, 'status_code', None) == 429:
        return True
    text = str(exc).lower()
    return any(
        marker in text
        for marker in (
            '429', 'rate limit', 'rate_limit', 'ratelimit', 'too many requests',
            'quota', 'insufficient_quota', 'exceeded your current quota',
        )
    )


def _failure_dict(exc: BaseException, **extra) -> Dict:
    """Public failure dict for a provider error, preserving the old return shapes."""
    if isinstance(exc, _AIProviderLimitError):
        result = {
            'success': False,
            'code': 'ai_provider_limit',
            'error': _FREE_LIMIT_MESSAGE,
            'timestamp': datetime.now().isoformat(),
        }
    else:
        result = {
            'success': False,
            'error': str(exc),
            'timestamp': datetime.now().isoformat(),
        }
    result.update(extra)
    return result


class AIService:
    def __init__(self):
        """تهيئة خدمة الذكاء الاصطناعي (lazy — client created on first use)"""
        self._clients = {}

    # ── المزوّدون ──────────────────────────────────────
    def _provider_chain(self, kind: str) -> List[str]:
        """Ordered providers to try for a kind ('chat'/'vision'/'voice')."""
        primary = os.getenv('AI_PRIMARY_PROVIDER', 'gemini').strip().lower()
        fallback = os.getenv('AI_FALLBACK_PROVIDER', 'groq').strip().lower()
        model_key = _MODEL_KEY[kind]
        chain = []
        for name in (primary, fallback):
            if name not in PROVIDERS or name in chain:
                continue
            if PROVIDERS[name].get(model_key) is None:
                continue
            if not os.getenv(PROVIDERS[name]['key_env']):
                continue
            chain.append(name)
        return chain

    def _voice_chain(self) -> List[str]:
        """Voice: Groq first (Whisper), then OpenAI if configured. Gemini has no audio transcription."""
        chain = []
        for name in ('groq', 'openai'):
            if PROVIDERS[name].get('voice_model') is None:
                continue
            if not os.getenv(PROVIDERS[name]['key_env']):
                continue
            chain.append(name)
        return chain

    def _get_client(self, provider_name: str):
        if provider_name not in self._clients:
            cfg = PROVIDERS[provider_name]
            api_key = os.getenv(cfg['key_env'])
            if not api_key:
                raise ValueError(
                    f"{cfg['key_env']} غير محدد. "
                    'يرجى إضافة مفتاح المزوّد في الإعدادات لاستخدام ميزات الذكاء الاصطناعي.'
                )
            kwargs = {'api_key': api_key}
            base_url = cfg['base_url'] or os.getenv('OPENAI_API_BASE')
            if base_url:
                kwargs['base_url'] = base_url
            self._clients[provider_name] = openai.OpenAI(**kwargs)
        return self._clients[provider_name]

    @property
    def client(self):
        """Primary provider's client (backward compat for the old single-client use)."""
        chain = self._provider_chain('chat') or self._provider_chain('vision')
        if not chain:
            raise ValueError(
                'لم يتم إعداد أي مزوّد ذكاء اصطناعي. '
                'أضف GEMINI_API_KEY أو GROQ_API_KEY في الإعدادات.'
            )
        return self._get_client(chain[0])

    def _chat_complete(self, kind: str, messages: List[Dict], **kwargs) -> str:
        """Chat/vision completion: primary once, then fallback once. Returns the response text."""
        chain = self._provider_chain(kind)
        if not chain:
            raise ValueError(
                'لم يتم إعداد أي مزوّد ذكاء اصطناعي. '
                'أضف GEMINI_API_KEY أو GROQ_API_KEY في الإعدادات.'
            )
        model_key = _MODEL_KEY[kind]
        last_error = None
        saw_rate_limit = False
        for name in chain:
            try:
                response = self._get_client(name).chat.completions.create(
                    model=PROVIDERS[name][model_key],
                    messages=messages,
                    **kwargs,
                )
                return response.choices[0].message.content
            except Exception as exc:  # noqa: BLE001 — any provider failure triggers one fallback attempt
                last_error = exc
                if _is_rate_limit_error(exc):
                    saw_rate_limit = True
        if saw_rate_limit:
            raise _AIProviderLimitError(str(last_error))
        raise last_error

    def _transcribe(self, audio_file, language: str = 'ar') -> str:
        """Audio transcription: Groq (Whisper) first, then OpenAI. Gemini has no transcription."""
        chain = self._voice_chain()
        if not chain:
            raise ValueError(
                'لا يوجد مزوّد صوت مُهيَّأ. أضف GROQ_API_KEY أو OPENAI_API_KEY لاستخدام المساعد الصوتي.'
            )
        last_error = None
        saw_rate_limit = False
        for name in chain:
            try:
                try:
                    audio_file.seek(0)
                except Exception:
                    pass
                response = self._get_client(name).audio.transcriptions.create(
                    model=PROVIDERS[name]['voice_model'],
                    file=audio_file,
                    language=language,
                )
                return response.text
            except Exception as exc:  # noqa: BLE001 — any provider failure triggers one fallback attempt
                last_error = exc
                if _is_rate_limit_error(exc):
                    saw_rate_limit = True
        if saw_rate_limit:
            raise _AIProviderLimitError(str(last_error))
        raise last_error

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

            analysis_result = self._chat_complete(
                'vision', messages, max_tokens=1500, temperature=0.3
            )
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
            return _failure_dict(e)

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

            assistant_response = self._chat_complete(
                'chat', messages, max_tokens=800, temperature=0.7
            )
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
            return _failure_dict(
                e, response='عذراً، حدث خطأ في النظام. يرجى المحاولة مرة أخرى.'
            )

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

            analysis = self._chat_complete(
                'chat',
                messages=[
                    {"role": "system", "content": "أنت طبيب متخصص في التشخيص الأولي. قدم تحليلاً دقيقاً ومفيداً باللغة العربية."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,
                temperature=0.5
            )

            return {
                'success': True,
                'analysis': analysis,
                'symptoms': symptoms,
                'urgency_assessment': self._assess_urgency(analysis),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return _failure_dict(e)

    # ──────────────────────────────────────────────
    # تحليل الصوت
    # ──────────────────────────────────────────────
    def analyze_voice(self, audio_data: bytes, context: Dict = None) -> Dict:
        """تحليل الصوت وتحويله إلى نص ثم معالجته طبياً"""
        try:
            # تحويل الصوت إلى نص باستخدام Whisper
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.webm"

            transcribed_text = self._transcribe(audio_file, language="ar")

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
            return _failure_dict(e)

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

            analysis = self._chat_complete(
                'chat',
                messages=[
                    {"role": "system", "content": "أنت صيدلاني ومتخصص في إدارة الأدوية. قدم تقييماً دقيقاً باللغة العربية."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.4
            )

            return {
                'success': True,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return _failure_dict(e)

    def check_drug_interactions(self, medications: List[str]) -> Dict:
        """فحص تفاعلات الأدوية"""
        try:
            meds_text = "، ".join(medications)

            analysis = self._chat_complete(
                'chat',
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

            return {
                'success': True,
                'analysis': analysis,
                'medications': medications,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return _failure_dict(e)

    # ──────────────────────────────────────────────
    # Family Health Manager - تحليل صحة الأسرة
    # ──────────────────────────────────────────────
    def analyze_family_health(self, family_members: List[Dict]) -> Dict:
        """تحليل الصحة العامة للأسرة وتقديم توصيات"""
        try:
            family_data = json.dumps(family_members, ensure_ascii=False, indent=2)

            analysis = self._chat_complete(
                'chat',
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

            return {
                'success': True,
                'analysis': analysis,
                'members_count': len(family_members),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return _failure_dict(e)

    def generate_health_report(self, patient_data: Dict) -> Dict:
        """إنتاج تقرير صحي شامل"""
        try:
            report_text = self._chat_complete(
                'chat',
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
                'report': report_text,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return _failure_dict(e)

    # ──────────────────────────────────────────────
    # تحليل المستندات الطبية (تقارير، وصفات، نتائج)
    # ──────────────────────────────────────────────
    def analyze_medical_document(self, image_data: bytes, doc_type: str = 'general',
                                  patient_info: dict = None) -> dict:
        """تحليل مستند طبي بلغة مبسطة"""
        try:
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            doc_prompts = {
                'lab': (
                    "أنت متخصص في تفسير نتائج التحاليل المخبرية. حلل هذه النتيجة وقدم:\n"
                    "1. ملخص النتائج بلغة بسيطة\n"
                    "2. القيم الطبيعية والقيم الشاذة مع التمييز الواضح\n"
                    "3. ماذا تعني هذه النتائج للمريض\n"
                    "4. التوصيات العامة\n"
                    "5. هل يحتاج المريض استشارة طبيب فوراً؟\n\n"
                    "⚠️ لا تقدم تشخيصاً نهائياً."
                ),
                'radiology': (
                    "أنت متخصص في قراءة تقارير الأشعة. حلل هذا التقرير وقدم:\n"
                    "1. ملخص ما تم تصويره\n"
                    "2. الملاحظات الرئيسية بلغة مبسطة\n"
                    "3. النتائج غير الطبيعية إن وجدت\n"
                    "4. الخطوات المقترحة التالية\n\n"
                    "⚠️ لا تقدم تشخيصاً نهائياً."
                ),
                'prescription': (
                    "أنت صيدلاني متخصص. حلل هذه الوصفة وقدم:\n"
                    "1. قائمة الأدوية واستخداماتها\n"
                    "2. الجرعة وطريقة الاستخدام\n"
                    "3. التحذيرات والتفاعلات الدوائية\n"
                    "4. نصائح للمريض\n"
                    "5. متى يجب مراجعة الطبيب\n\n"
                    "⚠️ لا تقدم نصائح تغيير الجرعة."
                ),
                'general': (
                    "أنت طبيب متخصص. حلل هذا المستند الطبي وقدم:\n"
                    "1. ملخص المحتوى بلغة مبسطة\n"
                    "2. النقاط الرئيسية والمعلومات المهمة\n"
                    "3. القيم أو النتائج غير الطبيعية إن وجدت\n"
                    "4. التوصيات العامة\n"
                    "5. هل يحتاج متابعة عاجلة؟\n\n"
                    "⚠️ هذا للتوعية فقط ولا يغني عن استشارة الطبيب."
                ),
            }
            system_prompt = doc_prompts.get(doc_type, doc_prompts['general'])
            user_text = f"قم بتحليل هذا المستند الطبي من نوع: {doc_type}"
            if patient_info:
                user_text += (
                    f"\n\nمعلومات المريض:\n"
                    f"- العمر: {patient_info.get('age', 'غير محدد')}\n"
                    f"- الجنس: {patient_info.get('gender', 'غير محدد')}\n"
                )
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": user_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]}
            ]
            result_text = self._chat_complete(
                'vision', messages, max_tokens=1500, temperature=0.3,
            )
            return {
                'success': True,
                'analysis': result_text,
                'doc_type': doc_type,
                'urgency_level': self._assess_urgency(result_text),
                'recommendations': self._extract_recommendations(result_text),
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            return _failure_dict(e)

    def symptom_checker_with_followup(self, symptoms: list, patient_info: dict = None,
                                       conversation_history: list = None,
                                       image_data: bytes = None) -> dict:
        """فحص الأعراض مع أسئلة متابعة ودعم الصور"""
        try:
            system_prompt = (
                "أنت طبيب متخصص في فحص الأعراض. دورك:\n"
                "1. تقييم الأعراض المذكورة بدقة\n"
                "2. طرح أسئلة متابعة دقيقة لتحسين التقييم\n"
                "3. تقدير مستوى الإلحاح: عاجل / متوسط / عادي\n"
                "4. اقتراح التخصص الطبي المناسب\n"
                "5. اقتراح الخطوات التالية الواضحة\n\n"
                "قواعد:\n"
                "- لا تقدم تشخيصاً نهائياً قاطعاً\n"
                "- اعرض دائماً: 'هذا تقييم أولي — يجب مراجعة طبيب مختص'\n"
                "- في حالات الطوارئ: وجّه فوراً لاستدعاء الإسعاف (920)\n"
                "- اطرح سؤالاً أو سؤالين في نهاية كل رد لتوضيح الصورة"
            )
            messages = [{"role": "system", "content": system_prompt}]
            if patient_info:
                ctx = (
                    f"معلومات المريض: عمر={patient_info.get('age','غير محدد')}, "
                    f"جنس={patient_info.get('gender','غير محدد')}, "
                    f"تاريخ مرضي={patient_info.get('medical_history','غير محدد')}"
                )
                messages.append({"role": "system", "content": ctx})
            if conversation_history:
                for msg in conversation_history[-8:]:
                    role = msg.get('role')
                    content = msg.get('content', '')
                    if role in ('user', 'assistant') and content:
                        messages.append({"role": role, "content": content})
            symptom_text = "الأعراض التي أشعر بها:\n" + "\n".join(f"- {s}" for s in symptoms if s)
            if image_data:
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                messages.append({"role": "user", "content": [
                    {"type": "text", "text": symptom_text + "\n\nأرفقت صورة للمنطقة المصابة."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]})
            else:
                messages.append({"role": "user", "content": symptom_text})
            result_text = self._chat_complete(
                'vision' if image_data else 'chat', messages,
                max_tokens=1000, temperature=0.5,
            )
            analysis = self._analyze_assistant_response(result_text)
            return {
                'success': True,
                'analysis': result_text,
                'urgency_assessment': analysis['urgency_level'],
                'recommended_specialty': analysis['recommended_specialty'],
                'follow_up_needed': analysis['follow_up_needed'],
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            return _failure_dict(e)

