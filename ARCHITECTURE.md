# SAHTY — Final Architecture

## الهدف

منصة صحتي تتبع بنية متعددة العملاء ذات Backend مركزي. لا يتصل أي Client مباشرة بقاعدة البيانات أو بمفاتيح الخدمات الخارجية؛ كل الاتصالات الحساسة تمر عبر Flask REST API.

```text
                         SAHTY
                           │
             ┌─────────────┴─────────────┐
             │                           │
        Web Client                   Mobile Client
       React / Vite                     Flutter
             │                           │
             └─────────────┬─────────────┘
                           │ HTTPS / JSON REST
                           │
                      Flask Backend
                           │
          ┌────────────────┼────────────────┐
          │                │                │
      PostgreSQL         Storage        External APIs
   transactional data  medical files    maps, AI, SMS, etc.
```

## حدود الطبقات

| الطبقة | التقنية | المسؤولية | ما لا يجوز لها فعله |
|---|---|---|---|
| Web Client | React/Vite/Tailwind | الواجهات، RTL، إدارة حالة العرض، استدعاء REST API، loading/empty/error states | لا تتصل بقاعدة البيانات ولا تحتوي Secrets أو JWT ثابتة |
| Mobile Client | Flutter | شاشات الهاتف، secure session storage، RTL، استدعاء REST API عبر `API_BASE_URL` | لا تستخدم `localhost` في التشغيل الخارجي، ولا تخزن أسرار Backend |
| REST API | Flask Blueprints | العقود العامة، المصادقة، الصلاحيات، التحقق، pagination، ownership/IDOR، serialization | لا يعرض أسرارًا أو بيانات مستخدم آخر |
| Database | PostgreSQL في الإنتاج، SQLite للاختبار والتطوير | المستخدمون، الأدوار، المواعيد، السجلات، الأدلة، العمليات الطبية | لا تُستخدم SQLite كقاعدة إنتاج |
| Storage | S3-compatible أو Storage خدمة النشر | الملفات الطبية والصور والتقارير مع روابط مصرح بها | لا تُحفظ الملفات الحساسة داخل Git أو public assets |
| External APIs | تكاملات Server-side فقط | AI، الخرائط، الرسائل، الخرائط الجغرافية، أو خدمات التحقق عند تفعيلها | لا تُستدعى بمفاتيح سرية من Web أو Mobile |

## مسار الطلب

يصل الطلب من React أو Flutter عبر HTTPS إلى Flask REST API. يتحقق Flask من JWT/session، والدور النشط، وملكية المورد، ثم يقرأ أو يكتب PostgreSQL. الملفات الطبية تمر عبر طبقة Storage مع authorization قبل التنزيل. التكاملات الخارجية تستدعى من Backend فقط، وتُحفظ مفاتيحها في Replit Secrets أو متغيرات البيئة.

## بيئات التشغيل

| البيئة | قاعدة البيانات | التشغيل | الحالة المطلوبة |
|---|---|---|---|
| Development/Test | SQLite | Flask development أو test client | قابلة لإعادة البناء من migrations |
| Replit Production | PostgreSQL مُدار | Gunicorn على `0.0.0.0:$PORT` | `SESSION_SECRET` و`DATABASE_URL` في Secrets، ورفض SQLite |
| Mobile Development | API خارجي عبر `API_BASE_URL` | Flutter toolchain | لا يُفترض `localhost` عند جهاز خارجي |

## قرارات إلزامية

لا يُنشأ Backend ثانٍ ولا تُنقل الأعمال إلى Client. كل feature جديدة يجب أن تمر عبر model أو query، migration، REST endpoint، authorization test، وواجهة مرتبطة بالبيانات الحقيقية. أي تكامل خارجي غير متاح يُصنف `NOT VERIFIED` أو `NOT IMPLEMENTED` ولا يُخفى ببيانات mock.
