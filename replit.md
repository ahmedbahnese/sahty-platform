# صحتك في أمان (Sahty)

## تشغيل المشروع

المشروع عبارة عن تطبيق React/Vite مع API مبني باستخدام Flask وSQLAlchemy.

- تثبيت التبعيات: `npm install` و`pip install -r requirements.txt`
- بناء الواجهة: `npm run build`
- ترقية قاعدة البيانات قبل التشغيل: `DATABASE_URL=sqlite:///src/database/app.db SESSION_SECRET=... flask --app main db upgrade`
- تشغيل التطبيق بعد الترقية: `PORT=5000 python main.py`
- الاختبارات: `pytest -q`

## التشغيل على Replit

يُشغّل workflow التطبيق بعد بناء الواجهة وترقية قاعدة البيانات:

```bash
npm run build && flask --app main db upgrade && PORT=5000 gunicorn --bind 0.0.0.0:5000 wsgi:application
```

يستخدم التشغيل الافتراضي SQLite. يجب أن يكون `SESSION_SECRET` مضبوطاً في Secrets؛
أما `OPENAI_API_KEY` وخدمات التخزين السحابي فهي اختيارية للميزات المرتبطة بها.

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

يطبق `python main.py` الترقية تلقائيًا قبل زرع البيانات المرجعية وبدء Flask.
يمكن لبيئات Gunicorn تنفيذ `flask --app main db upgrade` كخطوة نشر منفصلة قبل
بدء الخادم، وسيبقى تطبيق الترقية عند بدء التطبيق آمنًا لأنه idempotent.

يخدم Flask ملفات `dist` عند التشغيل الإنتاجي، ويشغل واجهة التطبيق وAPI على نفس المنفذ.

## الدليل الطبي

يتم استيراد قاعدة البيانات المرفقة من `attached_assets/Egypt_Healthcare_Full_Database_6000_1786271157551.zip` عند بدء التطبيق إذا كان جدول `healthcare_directory_records` فارغًا. الاستيراد آمن عند إعادة التشغيل ولا يستبدل الجداول القديمة.

## مسار Flutter المحمول على Replit

ملف `replit.nix` يطلب حزمة Flutter من بيئة Nix، لكن يجب التحقق من النسخة التي توفرها Replit بدل افتراض أنها مطابقة لـFlutter 3.32.0. شغّل الفحص القابل لإعادة الإنتاج التالي:

```bash
bash scripts/replit-mobile-check.sh
```

ينفذ الفحص `flutter --version` و`dart --version` و`flutter doctor -v` ثم `flutter pub get` و`flutter analyze` و`flutter test`. إذا لم تكن الأدوات متاحة، يفشل بوضوح ولا يعتبر mobile جاهزًا.

لتشغيل Flask ليستعمله تطبيق Flutter، يجب أن يستمع الخادم على `0.0.0.0` والمنفذ الذي توفره Replit، مع ضبط `SESSION_SECRET` في Secrets:

```bash
npm run build
flask --app main db upgrade
PORT=5000 gunicorn --bind 0.0.0.0:5000 wsgi:application
```

بعد نشر الـRepl أو إتاحة منفذه العام، استخدم عنوان HTTPS العام الذي توفره Replit. إذا كان متغير `REPLIT_DEV_DOMAIN` متاحًا في البيئة، يصبح عنوان API:

```bash
https://${REPLIT_DEV_DOMAIN}/api
```

وشغّل Flutter مع تمريره وقت البناء أو التشغيل:

```bash
cd mobile
flutter run --dart-define=API_BASE_URL=https://<REPLIT_PUBLIC_DOMAIN>/api
```

لا تستخدم `localhost` أو `127.0.0.1` من جهاز خارجي، ولا تستخدم `10.0.2.2` إلا من Android emulator للوصول إلى جهاز المضيف. يجب أن تكون `CORS_ORIGINS` مضبوطة على أصل الواجهة أو النطاق الذي يستدعي API، وأن تكون الخدمة العامة عبر HTTPS. لا تضع `SESSION_SECRET` أو JWT أو أي رمز إنتاج في Flutter أو Git.

## User preferences

- الحفاظ على بنية المشروع الحالية وتعديلها تدريجيًا بدل إعادة البناء من الصفر.
- إبقاء حساب المريض أساسيًا عند إضافة دور مهني، مع اعتماد الدور المهني بشكل منفصل.