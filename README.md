# صحتك في أمان — Sehaty Healthcare Platform

منصة رعاية صحية عربية تعمل كتطبيق ويب مستقل، وتتكون من واجهة React وخادم Flask.

## المتطلبات

- Python 3.11 أو أحدث
- Node.js 18 أو أحدث
- SQLite للتطوير، أو PostgreSQL عند الحاجة للإنتاج

## التشغيل المحلي

1. أنشئ بيئة Python وثبّت التبعيات:

   ```bash
   python -m venv .venv
   source .venv/bin/activate       # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. ثبّت تبعيات الواجهة:

   ```bash
   npm install
   ```

3. انسخ `.env.example` إلى `.env` وضع قيمة عشوائية طويلة في `SESSION_SECRET`.

4. شغّل الخادم والواجهة في نافذتين:

   ```bash
   python main.py
   npm run dev
   ```

   افتح الواجهة على `http://localhost:5173`. يعمل API على `http://localhost:5001`.

## بناء نسخة الإنتاج

```bash
npm run build
FLASK_ENV=production gunicorn --bind 0.0.0.0:5001 wsgi:application
```

بعد البناء يستطيع Flask تقديم ملفات الواجهة من مجلد `dist`.

## بنية المشروع

- `src/`: كود الواجهة وصفحاتها، ونماذج Flask ومسارات API.
- `src/database/app.db`: قاعدة SQLite المحلية الافتراضية.
- `migrations/`: ترحيلات قاعدة البيانات.
- `scripts/`: أدوات اختيارية لبيانات العرض والتقارير.
- `tests/`: اختبارات الخادم.

## إعدادات اختيارية

- `DATABASE_URL`: تغيير قاعدة البيانات من SQLite إلى PostgreSQL.
- `OPENAI_API_KEY`: تفعيل ميزات المساعد الذكي.
- `CORS_ORIGINS`: قائمة بعناوين الواجهة المسموح لها باستدعاء API، مفصولة بفواصل.

لا تعتمد عملية التشغيل على أي منصة أو خدمة استضافة بعينها.

