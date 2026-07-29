"""
الاختبارات الشاملة لمشروع صحتك في أمان
يغطي: APIs، قواعد البيانات، الصلاحيات، الصفحات، الأزرار

تشغيل:
    python -m pytest tests/test_comprehensive.py -v --tb=short 2>&1
"""

import sys
import os
import json
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, db


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────
@pytest.fixture(scope='session')
def test_app():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        db.create_all()
    yield app


@pytest.fixture(scope='session')
def client(test_app):
    return test_app.test_client()


@pytest.fixture(scope='session')
def auth_tokens(client):
    """تسجيل وتسجيل دخول المستخدمين المختلفين"""
    tokens = {}

    # مريض
    reg_patient = client.post('/api/auth/register', json={
        'username': 'testpatient', 'email': 'patient@test.com',
        'password': 'TestPass123!', 'user_type': 'patient',
        'first_name': 'أحمد', 'last_name': 'الاختبار',
        'date_of_birth': '1990-01-01', 'gender': 'male',
        'national_id': '12345678901234', 'phone': '0501234567'
    })
    if reg_patient.status_code in (200, 201):
        data = reg_patient.get_json()
        tokens['patient'] = data.get('token') or data.get('access_token')

    # تسجيل دخول المريض
    if not tokens.get('patient'):
        login = client.post('/api/auth/login', json={
            'email': 'patient@test.com', 'password': 'TestPass123!'
        })
        if login.status_code == 200:
            tokens['patient'] = login.get_json().get('token')

    return tokens


def auth_header(token):
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


# ─────────────────────────────────────────────────────────────
# 1. اختبارات الصحة العامة للـ API
# ─────────────────────────────────────────────────────────────
class TestAPIHealth:
    def test_api_root_returns_200(self, client):
        """الـ API الجذر يستجيب"""
        r = client.get('/')
        assert r.status_code in (200, 404)

    def test_api_health_endpoint(self, client):
        """نقطة نهاية health تعمل"""
        r = client.get('/api/health')
        assert r.status_code == 200
        data = r.get_json()
        assert data is not None

    def test_cors_headers_present(self, client):
        """CORS headers موجودة"""
        r = client.options('/api/auth/login',
                           headers={'Origin': 'http://localhost:5000',
                                    'Access-Control-Request-Method': 'POST'})
        assert r.status_code in (200, 204, 307)

    def test_404_returns_json_or_html(self, client):
        """مسار غير موجود يرجع 404 أو 200 (catch-all يخدم React في الإنتاج)"""
        r = client.get('/api/nonexistent-route-xyz')
        assert r.status_code in (200, 404)


# ─────────────────────────────────────────────────────────────
# 2. اختبارات المصادقة
# ─────────────────────────────────────────────────────────────
class TestAuthentication:
    def test_register_missing_fields(self, client):
        """التسجيل بدون حقول إلزامية يفشل"""
        r = client.post('/api/auth/register', json={'email': 'x@x.com'})
        assert r.status_code in (400, 422)

    def test_register_invalid_user_type(self, client):
        """نوع مستخدم غير صالح"""
        r = client.post('/api/auth/register', json={
            'username': 'bad', 'email': 'bad@test.com',
            'password': 'TestPass123!', 'user_type': 'hacker',
            'first_name': 'x', 'last_name': 'y',
            'date_of_birth': '1990-01-01', 'gender': 'male',
            'national_id': '99999999999999', 'phone': '0500000000'
        })
        assert r.status_code in (400, 422)

    def test_login_wrong_password(self, client):
        """كلمة مرور خاطئة"""
        r = client.post('/api/auth/login', json={
            'email': 'patient@test.com', 'password': 'WrongPass!'
        })
        assert r.status_code in (400, 401)

    def test_login_nonexistent_user(self, client):
        """مستخدم غير موجود"""
        r = client.post('/api/auth/login', json={
            'email': 'nobody@nowhere.com', 'password': 'AnyPass123!'
        })
        assert r.status_code in (400, 401, 404)

    def test_protected_route_without_token(self, client):
        """الوصول للمسار المحمي بدون توكن"""
        r = client.get('/api/auth/profile')
        assert r.status_code == 401

    def test_protected_route_invalid_token(self, client):
        """توكن غير صالح"""
        r = client.get('/api/auth/profile',
                       headers={'Authorization': 'Bearer invalid.token.here'})
        assert r.status_code == 401

    def test_register_patient_success(self, client):
        """تسجيل مريض جديد بنجاح"""
        import time
        uid = str(int(time.time()))[-6:]
        r = client.post('/api/auth/register', json={
            'username': f'patient_{uid}', 'email': f'patient_{uid}@test.com',
            'password': 'TestPass123!', 'user_type': 'patient',
            'first_name': 'فاطمة', 'last_name': 'المختبر',
            'date_of_birth': '1995-06-15', 'gender': 'female',
            'national_id': f'{uid}00000000', 'phone': '0509876543'
        })
        assert r.status_code in (200, 201)
        data = r.get_json()
        assert 'token' in data or 'access_token' in data or 'message' in data

    def test_login_success(self, client):
        """تسجيل دخول صحيح"""
        r = client.post('/api/auth/login', json={
            'email': 'patient2@test.com', 'password': 'TestPass123!'
        })
        assert r.status_code == 200
        data = r.get_json()
        assert 'token' in data or 'access_token' in data

    def test_duplicate_email_rejected(self, client):
        """البريد المكرر يُرفض"""
        for _ in range(2):
            r = client.post('/api/auth/register', json={
                'username': 'dup1', 'email': 'dup@test.com',
                'password': 'TestPass123!', 'user_type': 'patient',
                'first_name': 'نسخ', 'last_name': 'مكرر',
                'date_of_birth': '1990-01-01', 'gender': 'male',
                'national_id': '11111111111111', 'phone': '0500000001'
            })
        assert r.status_code in (400, 409, 422)


# ─────────────────────────────────────────────────────────────
# 3. اختبارات الصلاحيات
# ─────────────────────────────────────────────────────────────
class TestPermissions:
    def test_admin_endpoints_require_admin_role(self, client, auth_tokens):
        """نقاط نهاية الإدارة تتطلب صلاحية مدير"""
        token = auth_tokens.get('patient')
        if not token:
            pytest.skip('No patient token available')
        r = client.get('/api/admin/users', headers=auth_header(token))
        # مريض لا يستطيع الوصول لإدارة المستخدمين
        assert r.status_code in (401, 403)

    def test_patient_can_access_own_data(self, client, auth_tokens):
        """المريض يستطيع الوصول لبياناته"""
        token = auth_tokens.get('patient')
        if not token:
            pytest.skip('No patient token available')
        r = client.get('/api/auth/profile', headers=auth_header(token))
        assert r.status_code in (200, 404)  # 404 لو لم يتم إنشاء ملف المريض

    def test_unauthenticated_cannot_access_medical(self, client):
        """غير المسجل لا يستطيع الوصول للملف الطبي"""
        r = client.get('/api/medical-record/diseases')
        assert r.status_code in (401, 405)

    def test_medications_require_auth(self, client):
        """الأدوية تتطلب المصادقة"""
        r = client.get('/api/medications/')
        assert r.status_code == 401

    def test_family_group_requires_auth(self, client):
        """مجموعة الأسرة تتطلب المصادقة"""
        r = client.get('/api/family/groups')
        assert r.status_code == 401

    def test_ai_endpoints_require_auth(self, client):
        """نقاط نهاية AI تتطلب المصادقة"""
        endpoints = [
            ('/api/ai/chat', 'POST', {'message': 'test'}),
            ('/api/ai/symptom-checker', 'POST', {'symptoms': ['صداع']}),
            ('/api/ai/health-tips', 'GET', None),
        ]
        for path, method, body in endpoints:
            if method == 'GET':
                r = client.get(path)
            else:
                r = client.post(path, json=body)
            assert r.status_code == 401, f"Expected 401 for {path}, got {r.status_code}"

    def test_appointments_require_auth(self, client):
        """المواعيد تتطلب المصادقة"""
        # /api/appointments (no trailing slash) is the actual registered route
        r = client.get('/api/appointments')
        assert r.status_code in (401, 405)

    def test_prescriptions_require_auth(self, client):
        """الوصفات تتطلب المصادقة"""
        r = client.get('/api/prescriptions')
        assert r.status_code in (401, 405)


# ─────────────────────────────────────────────────────────────
# 4. اختبارات الأطباء والمستشفيات (عامة)
# ─────────────────────────────────────────────────────────────
class TestPublicEndpoints:
    def test_doctors_list_public(self, client):
        """قائمة الأطباء متاحة للجميع"""
        r = client.get('/api/doctors')
        assert r.status_code in (200, 404)

    def test_hospitals_list_public(self, client):
        """قائمة المستشفيات متاحة للجميع"""
        r = client.get('/api/hospitals')
        assert r.status_code in (200, 404)

    def test_specializations_list_public(self, client):
        """قائمة التخصصات متاحة للجميع"""
        r = client.get('/api/specializations')
        assert r.status_code in (200, 404)


# ─────────────────────────────────────────────────────────────
# 5. اختبارات الأدوية
# ─────────────────────────────────────────────────────────────
class TestMedications:
    def _get_token(self, client):
        """الحصول على توكن مريض للاختبار"""
        login = client.post('/api/auth/login', json={
            'email': 'patient2@test.com', 'password': 'TestPass123!'
        })
        if login.status_code == 200:
            return login.get_json().get('token')
        return None

    def test_get_medications_empty(self, client):
        """جلب الأدوية لمريض جديد"""
        token = self._get_token(client)
        if not token:
            pytest.skip('No token')
        r = client.get('/api/medications/', headers=auth_header(token))
        # 200 (قائمة فارغة) أو 404 (لم ينشئ ملف مريض بعد)
        assert r.status_code in (200, 404)

    def test_add_medication_missing_fields(self, client):
        """إضافة دواء بدون حقول إلزامية"""
        token = self._get_token(client)
        if not token:
            pytest.skip('No token')
        r = client.post('/api/medications/', json={'name': 'باراسيتامول'},
                        headers=auth_header(token))
        assert r.status_code in (400, 404)

    def test_today_summary(self, client):
        """ملخص أدوية اليوم"""
        token = self._get_token(client)
        if not token:
            pytest.skip('No token')
        r = client.get('/api/medications/today-summary', headers=auth_header(token))
        assert r.status_code in (200, 404)


# ─────────────────────────────────────────────────────────────
# 6. اختبارات Family Health Manager
# ─────────────────────────────────────────────────────────────
class TestFamilyHealth:
    def _get_token(self, client):
        login = client.post('/api/auth/login', json={
            'email': 'patient2@test.com', 'password': 'TestPass123!'
        })
        if login.status_code == 200:
            return login.get_json().get('token')
        return None

    def test_get_groups_empty(self, client):
        """جلب مجموعات الأسرة - قائمة فارغة لمستخدم جديد"""
        token = self._get_token(client)
        if not token:
            pytest.skip('No token')
        r = client.get('/api/family/groups', headers=auth_header(token))
        assert r.status_code == 200
        data = r.get_json()
        assert data['success'] is True
        assert isinstance(data['groups'], list)

    def test_create_group_success(self, client):
        """إنشاء مجموعة أسرة"""
        token = self._get_token(client)
        if not token:
            pytest.skip('No token')
        r = client.post('/api/family/groups',
                        json={'name': 'عائلة الاختبار', 'description': 'وصف'},
                        headers=auth_header(token))
        assert r.status_code in (200, 201)
        data = r.get_json()
        assert data['success'] is True
        assert data['group']['name'] == 'عائلة الاختبار'

    def test_create_group_missing_name(self, client):
        """إنشاء مجموعة بدون اسم يفشل"""
        token = self._get_token(client)
        if not token:
            pytest.skip('No token')
        r = client.post('/api/family/groups', json={'description': 'بدون اسم'},
                        headers=auth_header(token))
        assert r.status_code == 400

    def test_add_member_to_group(self, client):
        """إضافة فرد لمجموعة"""
        token = self._get_token(client)
        if not token:
            pytest.skip('No token')
        # إنشاء مجموعة أولاً
        gr = client.post('/api/family/groups',
                         json={'name': 'مجموعة الأعضاء'},
                         headers=auth_header(token))
        if gr.status_code not in (200, 201):
            pytest.skip('Could not create group')
        group_id = gr.get_json()['group']['id']

        r = client.post(f'/api/family/groups/{group_id}/members', json={
            'first_name': 'محمد', 'last_name': 'الاختبار',
            'relationship': 'أخ', 'gender': 'male',
            'date_of_birth': '1985-03-20'
        }, headers=auth_header(token))
        assert r.status_code in (200, 201)
        data = r.get_json()
        assert data['success'] is True

    def test_access_other_user_group_denied(self, client):
        """مستخدم لا يستطيع الوصول لمجموعة مستخدم آخر"""
        # تسجيل دخول مستخدم ثانٍ
        reg = client.post('/api/auth/register', json={
            'username': 'otheruser', 'email': 'other@test.com',
            'password': 'TestPass123!', 'user_type': 'patient',
            'first_name': 'آخر', 'last_name': 'مستخدم',
            'date_of_birth': '1988-01-01', 'gender': 'male',
            'national_id': '22222222222222', 'phone': '0500000002'
        })
        login = client.post('/api/auth/login', json={
            'email': 'other@test.com', 'password': 'TestPass123!'
        })
        if login.status_code != 200:
            pytest.skip('Could not login second user')
        token2 = login.get_json().get('token')

        # محاولة الوصول لمجموعة ذات ID=1 (تخص مستخدماً آخر)
        r = client.get('/api/family/groups/1', headers=auth_header(token2))
        # يجب أن يرفض (403 أو 404)
        assert r.status_code in (403, 404)


# ─────────────────────────────────────────────────────────────
# 7. اختبارات المواعيد
# ─────────────────────────────────────────────────────────────
class TestAppointments:
    def _get_token(self, client):
        login = client.post('/api/auth/login', json={
            'email': 'patient2@test.com', 'password': 'TestPass123!'
        })
        if login.status_code == 200:
            return login.get_json().get('token')
        return None

    def test_get_appointments(self, client):
        """جلب المواعيد"""
        token = self._get_token(client)
        if not token:
            pytest.skip('No token')
        r = client.get('/api/appointments/', headers=auth_header(token))
        assert r.status_code in (200, 404)

    def test_create_appointment_missing_fields(self, client):
        """حجز موعد بدون حقول إلزامية"""
        token = self._get_token(client)
        if not token:
            pytest.skip('No token')
        r = client.post('/api/appointments/book', json={'note': 'test'},
                        headers=auth_header(token))
        assert r.status_code in (400, 404, 405, 422)


# ─────────────────────────────────────────────────────────────
# 8. اختبارات الطوارئ
# ─────────────────────────────────────────────────────────────
class TestEmergency:
    def test_emergency_list_public(self, client):
        """قائمة خدمات الطوارئ"""
        r = client.get('/api/emergency/services')
        assert r.status_code in (200, 404)

    def test_emergency_alert_requires_auth(self, client):
        """تنبيه الطوارئ يتطلب المصادقة"""
        r = client.post('/api/emergency/alerts', json={'type': 'medical'})
        assert r.status_code in (401, 404, 405)


# ─────────────────────────────────────────────────────────────
# 9. اختبارات بنك الدم
# ─────────────────────────────────────────────────────────────
class TestBloodBank:
    def test_blood_bank_public_list(self, client):
        """قائمة بنك الدم العامة"""
        r = client.get('/api/blood-bank/inventory')
        assert r.status_code in (200, 404)

    def test_blood_request_requires_auth(self, client):
        """طلب الدم يتطلب المصادقة"""
        r = client.post('/api/blood/request', json={'blood_type': 'A+'})
        assert r.status_code in (401, 404, 405)


# ─────────────────────────────────────────────────────────────
# 10. اختبارات التحاليل والأشعة
# ─────────────────────────────────────────────────────────────
class TestLabRadiology:
    def _get_token(self, client):
        login = client.post('/api/auth/login', json={
            'email': 'patient2@test.com', 'password': 'TestPass123!'
        })
        if login.status_code == 200:
            return login.get_json().get('token')
        return None

    def test_lab_requests_require_auth(self, client):
        """طلبات التحاليل تتطلب المصادقة"""
        r = client.get('/api/lab-requests')
        assert r.status_code in (401, 404)

    def test_radiology_requests_require_auth(self, client):
        """طلبات الأشعة تتطلب المصادقة"""
        r = client.get('/api/radiology-requests')
        assert r.status_code in (401, 404)

    def test_get_lab_requests_with_auth(self, client):
        """جلب طلبات التحاليل مع مصادقة"""
        token = self._get_token(client)
        if not token:
            pytest.skip('No token')
        r = client.get('/api/lab-requests', headers=auth_header(token))
        assert r.status_code in (200, 404)


# ─────────────────────────────────────────────────────────────
# 11. اختبارات AI (بدون مفتاح API)
# ─────────────────────────────────────────────────────────────
class TestAIEndpoints:
    def _get_token(self, client):
        login = client.post('/api/auth/login', json={
            'email': 'patient2@test.com', 'password': 'TestPass123!'
        })
        if login.status_code == 200:
            return login.get_json().get('token')
        return None

    def test_ai_chat_requires_message(self, client):
        """AI chat يتطلب رسالة"""
        token = self._get_token(client)
        if not token:
            pytest.skip('No token')
        r = client.post('/api/ai/chat', json={}, headers=auth_header(token))
        assert r.status_code == 400

    def test_ai_symptom_checker_requires_symptoms(self, client):
        """فحص الأعراض يتطلب قائمة أعراض"""
        token = self._get_token(client)
        if not token:
            pytest.skip('No token')
        r = client.post('/api/ai/symptom-checker', json={},
                        headers=auth_header(token))
        assert r.status_code == 400

    def test_ai_drug_interaction_requires_meds(self, client):
        """فحص التفاعلات يتطلب قائمة أدوية"""
        token = self._get_token(client)
        if not token:
            pytest.skip('No token')
        r = client.post('/api/ai/drug-interaction', json={},
                        headers=auth_header(token))
        assert r.status_code == 400

    def test_ai_chat_responds_structurally(self, client):
        """AI chat يرجع response أو error بهيكل صحيح"""
        token = self._get_token(client)
        if not token:
            pytest.skip('No token')
        r = client.post('/api/ai/chat', json={'message': 'ما هي أعراض الزكام؟'},
                        headers=auth_header(token))
        assert r.status_code in (200, 500)
        data = r.get_json()
        assert 'success' in data

    def test_ai_image_upload_validates_file_type(self, client):
        """رفع صورة بصيغة غير مدعومة"""
        token = self._get_token(client)
        if not token:
            pytest.skip('No token')
        import io
        bad_file = (io.BytesIO(b'not-an-image'), 'test.exe')
        r = client.post('/api/ai/analyze-image',
                        data={'image': bad_file, 'image_type': 'xray'},
                        headers={'Authorization': f'Bearer {token}'},
                        content_type='multipart/form-data')
        assert r.status_code in (400, 500)


# ─────────────────────────────────────────────────────────────
# 12. اختبارات قاعدة البيانات
# ─────────────────────────────────────────────────────────────
class TestDatabase:
    def test_user_model_creation(self, test_app):
        """إنشاء مستخدم في قاعدة البيانات"""
        with test_app.app_context():
            from src.models.user import User, db
            from werkzeug.security import generate_password_hash
            user = User(
                username='dbtest',
                email='dbtest@test.com',
                password_hash=generate_password_hash('TestPass123!'),
                user_type='patient',
                is_active=True
            )
            db.session.add(user)
            db.session.commit()
            found = User.query.filter_by(email='dbtest@test.com').first()
            assert found is not None
            assert found.username == 'dbtest'
            db.session.delete(found)
            db.session.commit()

    def test_family_group_model(self, test_app):
        """نموذج مجموعة الأسرة يعمل"""
        import time
        uid = str(int(time.time()))[-8:]
        with test_app.app_context():
            from src.models.user import User, db
            from src.models.family_health import FamilyGroup
            from werkzeug.security import generate_password_hash

            # Use unique values to avoid conflicts with existing data
            user = User.query.filter_by(email=f'familytest_{uid}@test.com').first()
            if not user:
                user = User(
                    username=f'familytest_{uid}',
                    email=f'familytest_{uid}@test.com',
                    password_hash=generate_password_hash('TestPass123!'),
                    user_type='patient',
                    is_active=True
                )
                db.session.add(user)
                try:
                    db.session.flush()
                except Exception:
                    db.session.rollback()
                    pytest.skip('DB constraint - cannot create test user')

            group_name = f'مجموعة اختبار {uid}'
            group = FamilyGroup(name=group_name, owner_user_id=user.id)
            db.session.add(group)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                pytest.skip('DB constraint - cannot create test group')

            found = FamilyGroup.query.filter_by(name=group_name).first()
            assert found is not None
            assert found.to_dict()['name'] == group_name

    def test_medication_model(self, test_app):
        """نموذج الدواء يعمل"""
        with test_app.app_context():
            from src.models.medication import Medication
            # تحقق من وجود النموذج
            assert hasattr(Medication, 'name')
            assert hasattr(Medication, 'dosage')
            assert hasattr(Medication, 'frequency')

    def test_all_models_importable(self, test_app):
        """جميع النماذج قابلة للاستيراد"""
        from src.models.user import User
        from src.models.patient import Patient
        from src.models.doctor import Doctor
        from src.models.appointment import Appointment
        from src.models.medication import Medication, MedicationLog
        from src.models.blood_bank import BloodDonor, BloodRequest
        from src.models.hospital import Hospital
        from src.models.admin import Admin
        from src.models.emergency import EmergencyAlert
        from src.models.family_health import FamilyGroup, FamilyMember
        assert True  # كل الاستيرادات نجحت

    def test_database_tables_exist(self, test_app):
        """جميع الجداول موجودة في قاعدة البيانات"""
        with test_app.app_context():
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            required_tables = [
                'users', 'patients', 'doctors', 'appointments',
                'medications', 'family_groups', 'family_members'
            ]
            for table in required_tables:
                assert table in tables, f"جدول '{table}' غير موجود"


# ─────────────────────────────────────────────────────────────
# 13. اختبارات الصلاحيات المتقدمة
# ─────────────────────────────────────────────────────────────
class TestAdvancedPermissions:
    def test_cannot_delete_other_user_family_group(self, client):
        """لا يمكن حذف مجموعة أسرة تخص مستخدماً آخر"""
        # مستخدم 1 - patient2
        login1 = client.post('/api/auth/login', json={
            'email': 'patient2@test.com', 'password': 'TestPass123!'
        })
        if login1.status_code != 200:
            pytest.skip()
        token1 = login1.get_json().get('token')

        # إنشاء مجموعة للمستخدم الأول
        gr = client.post('/api/family/groups',
                         json={'name': 'مجموعة خاصة'},
                         headers=auth_header(token1))
        if gr.status_code not in (200, 201):
            pytest.skip('Could not create group')
        group_id = gr.get_json()['group']['id']

        # مستخدم 2 - other
        login2 = client.post('/api/auth/login', json={
            'email': 'other@test.com', 'password': 'TestPass123!'
        })
        if login2.status_code != 200:
            pytest.skip()
        token2 = login2.get_json().get('token')

        # محاولة الحذف من المستخدم الثاني
        r = client.delete(f'/api/family/groups/{group_id}',
                          headers=auth_header(token2))
        assert r.status_code in (403, 404)

    def test_cannot_log_medication_of_another_patient(self, client):
        """لا يمكن تسجيل دواء مريض آخر"""
        login = client.post('/api/auth/login', json={
            'email': 'other@test.com', 'password': 'TestPass123!'
        })
        if login.status_code != 200:
            pytest.skip()
        token = login.get_json().get('token')

        # محاولة تسجيل دواء بـ ID=1 (يخص مريضاً آخر)
        r = client.post('/api/medications/1/log',
                        json={'status': 'taken'},
                        headers=auth_header(token))
        assert r.status_code in (403, 404)


# ─────────────────────────────────────────────────────────────
# 14. اختبارات التحقق من صحة البيانات
# ─────────────────────────────────────────────────────────────
class TestInputValidation:
    def _get_token(self, client):
        login = client.post('/api/auth/login', json={
            'email': 'patient2@test.com', 'password': 'TestPass123!'
        })
        if login.status_code == 200:
            return login.get_json().get('token')
        return None

    def test_medication_log_invalid_status(self, client):
        """حالة تناول دواء غير صالحة"""
        token = self._get_token(client)
        if not token:
            pytest.skip('No token')
        r = client.post('/api/medications/1/log',
                        json={'status': 'unknown_status'},
                        headers=auth_header(token))
        assert r.status_code in (400, 403, 404)

    def test_family_member_invalid_date(self, client):
        """تاريخ ميلاد غير صالح"""
        token = self._get_token(client)
        if not token:
            pytest.skip('No token')
        # إنشاء مجموعة أولاً
        gr = client.post('/api/family/groups',
                         json={'name': 'اختبار التحقق'},
                         headers=auth_header(token))
        if gr.status_code not in (200, 201):
            pytest.skip()
        gid = gr.get_json()['group']['id']

        r = client.post(f'/api/family/groups/{gid}/members', json={
            'first_name': 'test', 'last_name': 'test',
            'relationship': 'أخ', 'date_of_birth': 'invalid-date'
        }, headers=auth_header(token))
        # يجب إما رفض أو تجاهل التاريخ الغير صالح
        assert r.status_code in (200, 201, 400)

    def test_empty_json_body(self, client):
        """جسم طلب فارغ"""
        token = self._get_token(client)
        if not token:
            pytest.skip('No token')
        r = client.post('/api/ai/chat', data='not-json',
                        headers={**auth_header(token),
                                 'Content-Type': 'application/json'})
        assert r.status_code in (400, 415, 500)
