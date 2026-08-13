# صحتك في أمان (Sahty)

## تشغيل المشروع

المشروع عبارة عن تطبيق React/Vite مع API مبني باستخدام Flask وSQLAlchemy.

- تثبيت التبعيات: `npm install` و`pip install -r requirements.txt`
- بناء الواجهة: `npm run build`
- ترقية قاعدة البيانات قبل التشغيل: `DATABASE_URL=sqlite:///src/database/app.db SESSION_SECRET=... flask --app main db upgrade`
- تشغيل التطبيق بعد الترقية: `PORT=5000 python main.py`
- الاختبارات: `pytest -q`

## ترحيلات قاعدة البيانات

يتم إنشاء الجداول وترقيتها حصراً عبر Flask-Migrate/Alembic. لا يستدعي التطبيق
`db.create_all()` ولا ينفذ أوامر `ALTER TABLE` أثناء التشغيل.

لبيئة جديدة أو قاعدة بيانات مستوردة، شغّل:

```bash
flask --app main db upgrade
```

بعد تعديل نماذج SQLAlchemy، أنشئ revision جديدة ثم راجعها قبل تطبيقها:

```bash
flask --app main db migrate -m "describe schema change"
flask --app main db upgrade
```

يجب تشغيل أمر الترقية كخطوة نشر منفصلة قبل بدء Gunicorn أو `python main.py`.

يخدم Flask ملفات `dist` عند التشغيل الإنتاجي، ويشغل واجهة التطبيق وAPI على نفس المنفذ.

## الدليل الطبي

يتم استيراد قاعدة البيانات المرفقة من `attached_assets/Egypt_Healthcare_Full_Database_6000_1786271157551.zip` عند بدء التطبيق إذا كان جدول `healthcare_directory_records` فارغًا. الاستيراد آمن عند إعادة التشغيل ولا يستبدل الجداول القديمة.

## User preferences

- الحفاظ على بنية المشروع الحالية وتعديلها تدريجيًا بدل إعادة البناء من الصفر.
- إبقاء حساب المريض أساسيًا عند إضافة دور مهني، مع اعتماد الدور المهني بشكل منفصل.