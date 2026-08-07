# دليل تشغيل ونشر منصة صحتك في أمان

## مكونات التطبيق

- **الخادم:** Flask وPython 3.11 أو أحدث، ويعمل افتراضياً على المنفذ 5001.
- **الواجهة:** React وVite، وتعمل أثناء التطوير على المنفذ 5173.
- **قاعدة البيانات:** SQLite للتطوير، أو PostgreSQL للإنتاج.

## إعداد البيئة

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
npm install
cp .env.example .env
```

ضع قيمة عشوائية طويلة في `SESSION_SECRET` قبل تشغيل الخادم. لا تضع الأسرار داخل Git.

## التشغيل أثناء التطوير

شغّل كل أمر في نافذة طرفية مستقلة:

```bash
python main.py
npm run dev
```

العناوين الافتراضية:

- الواجهة: `http://localhost:5173`
- API: `http://localhost:5001`

يمكن تغيير عنوان API الذي تستخدمه Vite عبر `API_URL`. ويمكن تغيير قائمة أصول CORS عبر
`CORS_ORIGINS`.

## بناء وتشغيل الإنتاج

```bash
npm run build
FLASK_ENV=production gunicorn --bind 0.0.0.0:5001 wsgi:application
```

بعد تنفيذ `npm run build` يستطيع Flask تقديم الواجهة من مجلد `dist` عند استخدام
إعداد خادم واحد مناسب.

## قاعدة البيانات

للتطوير تستخدم المنصة SQLite في `src/database/app.db`. لتشغيل PostgreSQL:

```bash
export DATABASE_URL='postgresql://user:password@host/database'
flask --app main db upgrade
```

أنشئ النسخ الاحتياطية وفق سياسة مزود قاعدة البيانات، ولا تضع ملفات النسخ الاحتياطية
أو بيانات المرضى في المستودع.

## ميزات الذكاء الاصطناعي

يتطلب المساعد الذكي `OPENAI_API_KEY`. إذا لم تُضبط القيمة، تبقى بقية ميزات المنصة
متاحة وتعيد واجهة الذكاء الاصطناعي رسالة خطأ واضحة عند طلبها.

## فحص سريع

```bash
npm run build
npm run lint
pytest
```
