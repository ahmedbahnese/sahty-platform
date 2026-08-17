# Sehaty REST API Contract v1

## Contract rules

كل Client يستخدم HTTPS ويمر عبر Flask REST API. لا توجد صلاحية مباشرة إلى PostgreSQL أو Storage. يرسل العميل `Authorization: Bearer <JWT>` للمسارات المحمية، ويرسل `Content-Type: application/json` إلا في multipart uploads. يجب على العميل الاعتماد على HTTP status والحقول المنظمة، لا على نص الرسالة العربي وحده.

| العنصر | القاعدة |
|---|---|
| Authentication | `Authorization: Bearer <JWT>`؛ غيابه أو انتهاء الجلسة يعيد 401 |
| Authorization | يحددها `user_type` والدور النشط server-side، ولا يثق الخادم بدور يرسله العميل وحده |
| Validation | JSON object، حقول مطلوبة، أنواع صحيحة، تواريخ ISO 8601، وقيم enums محددة |
| Ownership | كل مورد طبي أو شخصي يُعاد فقط لمالكه أو للطرف المهني المرتبط به أو لدور إداري مصرح |
| Pagination | `page >= 1` و`per_page` محدود؛ الاستجابة تعرض `total`, `page`, `per_page`, `pages` عند دعم pagination |
| Errors | 400 validation، 401 unauthenticated، 403 forbidden، 404 missing، 409 conflict، 500 server error |
| Transactions | عمليات الإنشاء المرتبطة بإشعارات أو history تُحفظ في transaction واحدة وتُعمل rollback عند الفشل |

## Authentication

| Endpoint | Method | Auth | Authorization | Request | Response |
|---|---|---|---|---|---|
| `/api/auth/register` | POST | Public | التسجيل العام لا يقبل `admin` أو `super_admin` | first_name, last_name, email, password، وحقول الحساب المهني عند الحاجة | 201 مع `token` و`user` |
| `/api/auth/login` | POST | Public | حساب فعال فقط | email/username/phone + password | 200 مع `token` و`user`، أو 401 |
| `/api/auth/profile` | GET/PUT | JWT | المستخدم الحالي فقط | PUT JSON للحقول المسموحة | 200 profile |
| `/api/auth/logout` | POST | JWT | الجلسة الحالية فقط | لا body مطلوب | 200، وإبطال session server-side |
| `/api/auth/switch-role` | POST | JWT | دور معتمد ومربوط بالحساب فقط | `{ "role": "patient" }` | 200 active role |
| `/api/auth/apply-role` | POST | JWT | patient يطلب doctor/nurse؛ الإدارة تعتمد لاحقًا | بيانات الدور المهني | 201 pending request |

## Appointment contract

### POST `/api/appointments`

> **التدفق الملزم:** Authentication → patient authorization → JSON validation → doctor lookup and active check → ISO date parsing → reject past date → slot conflict/availability check → optional family-member ownership check → create appointment/history/notification transaction → PostgreSQL → 201 response.

| البند | العقد |
|---|---|
| Method/Auth | POST، JWT مطلوب |
| Authorization | `current_user.user_type == patient`؛ الطبيب أو الحساب الآخر يحصل على 403 |
| Required request | `doctor_id` integer، `appointment_date` ISO 8601، `appointment_type` أحد `in_person` أو `telemedicine` |
| Optional request | `duration`, `reason`, `symptoms`, `for_family_member_id`, `for_member_name` |
| Validation | الطبيب موجود ونشط؛ التاريخ ليس في الماضي؛ النوع مدعوم؛ فرد الأسرة يجب أن يكون في مجموعة يملكها المستخدم |
| Ownership | `patient_id` مأخوذ من JWT؛ لا يقبل العميل `patient_id` لإنشاء الموعد |
| Availability | يمنع وجود موعد `scheduled` أو `confirmed` للطبيب والتوقيت نفسه ويعيد 409 |
| Success | 201 `{ "message": "...", "appointment": {...} }` |
| Errors | 400 body/fields/date/type، 403 role، 404 patient/doctor، 409 occupied slot، 500 unexpected |

### Appointment reads and transitions

| Endpoint | Method/Auth | Authorization/ownership | Success |
|---|---|---|---|
| `/api/appointments` | GET/JWT | المريض يرى مواعيده، والطبيب يرى مواعيده؛ غيرهما 403 | `{ appointments, total }` |
| `/api/appointments/stats` | GET/JWT | إحصاءات المستخدم الحالي فقط | counts by status |
| `/api/appointments/{id}` | GET/JWT | المريض المالك أو الطبيب المعني أو admin | appointment + history |
| `/api/appointments/{id}` | PUT/JWT | المريض المالك فقط، والحالة scheduled/confirmed | updated appointment |
| `/api/appointments/{id}/confirm` | POST/JWT | الطبيب المرتبط بالموعد فقط | status `confirmed` |
| `/api/appointments/{id}/complete` | POST/JWT | الطبيب المرتبط بالموعد فقط | status `completed` |
| `/api/appointments/{id}/cancel` | POST/JWT | المريض المالك أو الطبيب المرتبط أو الإدارة | status `cancelled` |

## Directory contract

| Endpoint | Method/Auth | Request/query | Ownership/validation | Response |
|---|---|---|---|---|
| `/api/facilities` | GET/Public | search, governorate, city, type, specialty, page, per_page, nearest | بيانات دليل عامة؛ pagination وحدود النوع | `{ facilities, total, page, per_page, pages }` |
| `/api/facilities/metadata` | GET/Public | لا body | يعرض الأنواع والمحافظات والمدن الموجودة فعليًا | metadata arrays |
| `/api/doctors` | GET/Public | specialty, city, name, page, per_page | يعرض الأطباء النشطين/المعتمدين وفق تنفيذ route | `{ doctors }` |
| `/api/doctors/{id}` | GET/Public | path id | الطبيب موجود ونشط | doctor + availability + rating |
| `/api/doctors/{id}/available-slots` | GET/JWT | `date=YYYY-MM-DD` | قراءة availability وحالة الحجز | slots |

## Prescriptions and medical data

| Endpoint family | Auth | Ownership/authorization contract |
|---|---|---|
| `/api/prescriptions` | JWT | الإنشاء للطبيب المرتبط، القراءة للمريض أو الطبيب المرتبط أو دور الصيدلية في نطاق الصرف، ولا يسمح بتغيير وصفة خارج النطاق |
| `/api/medical-record/*` | JWT | السجل للمريض المالك، والطبيب فقط ضمن علاقة علاجية/صلاحية route؛ يمنع IDOR ويعيد 403 |
| `/api/lab-requests/*` | JWT | المريض يرى طلباته، الطبيب يعتمد ضمن نطاقه، المعمل يضيف النتائج لطلب مرتبط؛ الملفات multipart ويجب فحص النوع والملكية |
| `/api/radiology-requests/*` | JWT | نفس مبدأ الملكية؛ الصور والتقارير لا تُعرض إلا للطرف المصرح |
| `/api/uploads/*` | JWT | لا يكفي معرفة filename؛ endpoint يجب أن يتحقق من ملكية سجل الملف قبل التنزيل |

## Error examples

```json
{ "message": "بيانات الحجز يجب أن تكون JSON صحيحة" }
```

```json
{ "error": "Not Found", "message": "المسار غير موجود", "status": 404 }
```

```json
{ "message": "هذا الموعد لم يعد متاحاً، يرجى اختيار وقت آخر" }
```

## Mobile rule

لا يبدأ Flutter بإنشاء workflow جديد قبل تثبيت endpoint في هذا العقد وإضافة اختبار API له. يجب تعريف `API_BASE_URL` عبر build configuration، واستخدام DTOs مطابقة لأسماء الحقول الحالية، ومعالجة 401 بتجديد/تسجيل خروج، و403 برسالة صلاحية، و409 بإعادة اختيار المورد، و422/400 بعرض أخطاء التحقق.

## Verification requirement

كل endpoint حرج يحتاج اختبارًا واحدًا على الأقل للحالة الناجحة، و401، و403/ownership، و400 validation، و404، و409 عند وجود تعارض. يجب تشغيل الاختبارات ضد SQLite النظيفة، ثم إعادة smoke tests ضد PostgreSQL Replit عند توفير `DATABASE_URL` الإنتاجية.
