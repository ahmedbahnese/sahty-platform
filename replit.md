# صحتك في أمان — Sahty Health Platform

## نظرة عامة
منصة طبية شاملة باللغة العربية تجمع المرضى والأطباء والمستشفيات في مكان واحد.

**Stack:** Flask (Python 3.12) + React 19 / Vite + SQLite (dev) / PostgreSQL (prod)

---

## كيفية التشغيل

| الخدمة | الأمر | المنفذ |
|--------|-------|--------|
| Flask API | `python main.py` | 5001 |
| React Frontend | `npm run dev` | 5000 |

Vite يعمل كـ proxy — كل طلبات `/api/*` تُحوَّل تلقائياً إلى `:5001`.

---

## بنية المشروع

```
.
├── main.py                  # نقطة دخول Flask
├── src/
│   ├── models/              # نماذج قاعدة البيانات (SQLAlchemy)
│   │   ├── user.py          # المستخدمون والجلسات
│   │   ├── patient.py       # المرضى
│   │   ├── doctor.py        # الأطباء
│   │   ├── appointment.py   # المواعيد
│   │   ├── medication.py    # الأدوية والجداول
│   │   ├── family_health.py # Family Health Manager (جديد)
│   │   └── ...
│   ├── routes/              # مسارات Flask Blueprint
│   │   ├── auth.py          # المصادقة + token_required
│   │   ├── ai.py            # الذكاء الاصطناعي (جديد)
│   │   ├── medication.py    # متابعة الأدوية (جديد)
│   │   ├── family_health.py # Family Health (جديد)
│   │   └── ...
│   ├── services/
│   │   └── ai_service.py    # OpenAI integration (lazy init)
│   ├── pages/               # صفحات React
│   │   ├── AIAssistantPage.jsx
│   │   ├── MedicationTrackingPage.jsx  (جديد)
│   │   ├── FamilyHealthPage.jsx        (جديد)
│   │   └── ...
│   ├── components/          # مكونات React المشتركة
│   └── contexts/
│       └── AuthContext.jsx  # JWT + role flags
├── tests/
│   └── test_comprehensive.py  # اختبارات شاملة (Phase 12)
├── package.json
└── requirements.txt
```

---

## المتغيرات البيئية المطلوبة

| المتغير | الوصف | إلزامي |
|---------|-------|--------|
| `SESSION_SECRET` | مفتاح تشفير الجلسات والـ JWT | ✅ |
| `OPENAI_API_KEY` | مفتاح OpenAI لميزات الذكاء الاصطناعي | لميزات AI فقط |
| `DATABASE_URL` | رابط PostgreSQL للإنتاج | اختياري (SQLite افتراضي) |
| `ADMIN_EMAIL` | إيميل مدير النظام الأول | اختياري |
| `ADMIN_PASSWORD` | كلمة مرور المدير الأول | اختياري |

---

## الميزات الرئيسية

### المرحلة 11 — الذكاء الاصطناعي
- **المساعد الذكي** — محادثة طبية مع GPT-4o (`/ai-assistant`)
- **تحليل الصور** — تحليل الصور الطبية (X-Ray, MRI...) (`POST /api/ai/analyze-image`)
- **تحليل الصوت** — تحويل صوت → نص → معالجة طبية (`POST /api/ai/analyze-voice`)
- **اقتراح التشخيص** — فحص الأعراض (`POST /api/ai/symptom-checker`)
- **متابعة الأدوية** — تتبع وتحليل الالتزام بالأدوية (`/medications`)
- **Family Health Manager** — إدارة صحة الأسرة بالكامل (`/family-health`)

### المرحلة 12 — الاختبارات
- **`tests/test_comprehensive.py`** — 40+ اختبار يغطي APIs، قاعدة البيانات، الصلاحيات، التحقق من المدخلات
- التشغيل: `python -m pytest tests/ -v`

---

## نقاط نهاية API الرئيسية

```
POST /api/auth/register          — تسجيل
POST /api/auth/login             — دخول
GET  /api/auth/profile           — الملف الشخصي

GET  /api/medications/           — قائمة الأدوية
POST /api/medications/           — إضافة دواء
POST /api/medications/:id/log    — تسجيل تناول
GET  /api/medications/today-summary

GET  /api/family/groups          — مجموعات الأسرة
POST /api/family/groups          — إنشاء مجموعة
POST /api/family/groups/:id/members
GET  /api/family/groups/:id/ai-analysis

POST /api/ai/chat                — المساعد الذكي
POST /api/ai/analyze-image       — تحليل الصور
POST /api/ai/analyze-voice       — تحليل الصوت
POST /api/ai/symptom-checker     — اقتراح التشخيص
GET  /api/ai/medication-adherence
GET  /api/ai/health-tips
```

---

## تفضيلات المستخدم
- اللغة الرئيسية: العربية (RTL)
- الاتجاه: `dir="rtl"`
- Stack ثابت: Flask + React/Vite (لا ترقية أو تغيير)
