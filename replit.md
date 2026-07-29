# صحتك في أمان — Sahty Healthcare Platform

## نظرة عامة
منصة رعاية صحية متكاملة تجمع بين:
- **الواجهة الأمامية**: React 19 + Vite + Tailwind CSS 4
- **الواجهة الخلفية**: Flask (Python) + SQLAlchemy + JWT

## كيفية التشغيل

### الخادمان:
| الخادم | الأمر | المنفذ |
|--------|-------|--------|
| Flask API | `python main.py` | 5001 |
| Vite (React) | `npm run dev` | 5000 |

الواجهة الأمامية (5000) تُحيل طلبات `/api/*` تلقائياً إلى Flask (5001) عبر Vite proxy.

## المتغيرات والأسرار المطلوبة

| المفتاح | النوع | الوصف |
|---------|-------|-------|
| `SESSION_SECRET` | Secret | مفتاح تشفير الجلسات والـ JWT |
| `ADMIN_EMAIL` | EnvVar | بريد حساب المؤسس |
| `ADMIN_PASSWORD` | Secret | كلمة مرور المؤسس — يُحدَّث تلقائياً عند كل إعادة تشغيل |
| `ADMIN_FIRST_NAME` | EnvVar | الاسم الأول للمؤسس |
| `ADMIN_LAST_NAME` | EnvVar | الاسم الأخير للمؤسس |
| `OPENAI_API_KEY` | Secret | مطلوب لميزات المساعد الذكي |

## البنية الأساسية
```
/
├── main.py              # Flask entry point (port 5001)
├── src/
│   ├── models/          # SQLAlchemy models
│   ├── routes/          # Flask blueprints (API)
│   ├── services/        # AI service, etc.
│   ├── pages/           # React pages
│   ├── components/      # React components
│   └── contexts/        # React contexts (Auth)
├── App.jsx              # React router + FloatingAIChat
└── main.jsx             # React entry point
```

## ميزات رئيسية
- ✅ تسجيل دخول JWT مع جلسات خادمية
- ✅ أنواع مستخدمين: مريض، طبيب، صيدلية، معمل، مستشفى، مشرف
- ✅ مساعد ذكي عائم قابل للسحب على جميع الصفحات
- ✅ لوحة إدارة للمشرف (super_admin)
- ✅ بنك الدم، الطوارئ، التحاليل، الأشعة، الوصفات

## ملاحظات تقنية
- كلمة مرور المؤسس تُحدَّث تلقائياً من `ADMIN_PASSWORD` عند كل بدء تشغيل Flask
- قاعدة البيانات: PostgreSQL (Replit-managed) أو SQLite كبديل
- المساعد الذكي يحتاج `OPENAI_API_KEY` — بدونه يُظهر رسالة خطأ واضحة

## تفضيلات المستخدم
- اللغة العربية للواجهة (RTL)
- ألوان: أبيض + كحلي داكن (`#0f2444`) + أزرق (`#2563eb`)
- المساعد الذكي عائم ويمكن سحبه في كل صفحة
