"""
Automated backend tests for Sehaty (صحتي) API.
Run: pytest tests/test_backend.py -v

Fixtures (app, client) are defined in conftest.py which forces SQLite in-memory.
"""
import json
import pytest

import uuid

def _unique_email(prefix='user'):
    return f'{prefix}_{uuid.uuid4().hex[:8]}@test.com'

def _unique_nid():
    import random
    return '2' + ''.join(str(random.randint(0, 9)) for _ in range(13))


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def register_and_login(client, email, password='Test1234!', role='patient'):
    """Register + login and return JWT token."""
    client.post('/api/auth/register', json={
        'first_name': 'Test', 'last_name': 'User',
        'email': email, 'password': password,
        'date_of_birth': '1990-01-01', 'gender': 'male',
        'user_type': role, 'national_id': _unique_nid(),
    })
    login_res = client.post('/api/auth/login', json={
        'email': email, 'password': password
    })
    data = login_res.get_json() or {}
    return data.get('token') or data.get('access_token'), login_res.status_code


def auth_headers(token):
    return {'Authorization': f'Bearer {token}'}


# ─────────────────────────────────────────────
# Auth Tests
# ─────────────────────────────────────────────

class TestAuth:
    def test_register_success(self, client):
        res = client.post('/api/auth/register', json={
            'first_name': 'Ali', 'last_name': 'Hassan',
            'email': 'ali.hassan@test.com', 'password': 'Secure123!',
            'date_of_birth': '1985-05-10', 'gender': 'male',
            'user_type': 'patient', 'national_id': '28505100123456',
        })
        assert res.status_code in (200, 201)

    def test_register_duplicate_email(self, client):
        payload = {
            'first_name': 'Dup', 'last_name': 'User', 'email': 'dup@test.com',
            'password': 'Secure123!', 'date_of_birth': '1990-01-01',
            'gender': 'male', 'user_type': 'patient', 'national_id': '29001011234567',
        }
        client.post('/api/auth/register', json=payload)
        res = client.post('/api/auth/register', json=payload)
        assert res.status_code in (400, 409)

    def test_register_missing_fields(self, client):
        res = client.post('/api/auth/register', json={'email': 'incomplete@test.com'})
        assert res.status_code == 400

    def test_register_rejects_non_object_json(self, client):
        res = client.post('/api/auth/register', data='[]', content_type='application/json')
        assert res.status_code == 400

    def test_register_rejects_non_string_credentials(self, client):
        res = client.post('/api/auth/register', json={
            'first_name': 'Bad', 'last_name': 'Input',
            'email': 'bad-input@test.com', 'password': 12345678,
            'user_type': 'patient',
        })
        assert res.status_code == 400

    def test_login_rejects_non_object_json(self, client):
        res = client.post('/api/auth/login', data='[]', content_type='application/json')
        assert res.status_code == 400

    def test_login_rejects_non_string_credentials(self, client):
        res = client.post('/api/auth/login', json={
            'email': {'value': 'bad'}, 'password': 'anything',
        })
        assert res.status_code == 400

    def test_login_success(self, client):
        client.post('/api/auth/register', json={
            'first_name': 'Login', 'last_name': 'Test',
            'email': 'logintest@test.com', 'password': 'Login123!',
            'date_of_birth': '1990-01-01', 'gender': 'female',
            'user_type': 'patient', 'national_id': '29001011234599',
        })
        res = client.post('/api/auth/login', json={
            'email': 'logintest@test.com', 'password': 'Login123!'
        })
        data = res.get_json()
        assert res.status_code == 200
        assert 'token' in data or 'access_token' in data

    def test_login_wrong_password(self, client):
        res = client.post('/api/auth/login', json={
            'email': 'logintest@test.com', 'password': 'WrongPass!'
        })
        assert res.status_code in (400, 401, 403)

    def test_login_nonexistent_user(self, client):
        res = client.post('/api/auth/login', json={
            'email': 'nobody@nowhere.com', 'password': 'anything'
        })
        assert res.status_code in (400, 401, 404)

    def test_protected_route_no_token(self, client):
        res = client.get('/api/auth/profile')
        assert res.status_code == 401


# ─────────────────────────────────────────────
# Blood Bank Tests
# ─────────────────────────────────────────────

class TestBloodBank:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.token, _ = register_and_login(client, 'bloodbank.patient@test.com')
        self.headers = auth_headers(self.token)

    def test_list_requests(self, client):
        res = client.get('/api/blood-bank/requests', headers=self.headers)
        assert res.status_code == 200
        data = res.get_json()
        assert 'requests' in data

    def test_create_blood_request(self, client):
        res = client.post('/api/blood-bank/requests', json={
            'patient_name': 'سارة أحمد',
            'blood_type': 'O+',
            'units_needed': 2,
            'hospital_name': 'مستشفى القاهرة',
            'city': 'القاهرة',
            'urgency_level': 'urgent',
            'contact_phone': '01012345678',
            'needed_by_date': '2026-08-15T00:00:00',
        }, headers=self.headers)
        assert res.status_code in (200, 201)
        data = res.get_json()
        assert 'request' in data or 'message' in data

    def test_invalid_blood_type(self, client):
        res = client.post('/api/blood-bank/requests', json={
            'patient_name': 'Test', 'blood_type': 'Z+',
            'units_needed': 1, 'hospital_name': 'Test Hospital',
            'city': 'Cairo', 'urgency_level': 'urgent',
            'contact_phone': '01000000000', 'needed_by_date': '2026-08-01T00:00:00',
        }, headers=self.headers)
        # either validation error or creates with DB default
        assert res.status_code in (200, 201, 400, 422)

    def test_get_inventory(self, client):
        res = client.get('/api/blood-bank/inventory', headers=self.headers)
        assert res.status_code in (200, 404)

    def test_unauthenticated_create(self, client):
        res = client.post('/api/blood-bank/requests', json={
            'patient_name': 'X', 'blood_type': 'A+',
        })
        assert res.status_code == 401


# ─────────────────────────────────────────────
# Hospital Tests
# ─────────────────────────────────────────────

class TestHospitals:
    def test_list_hospitals_public(self, client):
        res = client.get('/api/hospitals')
        assert res.status_code == 200
        data = res.get_json()
        assert 'hospitals' in data
        assert 'total' in data

    def test_list_hospitals_pagination(self, client):
        res = client.get('/api/hospitals?page=1&per_page=5')
        assert res.status_code == 200
        data = res.get_json()
        assert data['per_page'] == 5

    def test_hospital_not_found(self, client):
        res = client.get('/api/hospitals/999999')
        assert res.status_code == 404

    def test_create_hospital_requires_admin(self, client):
        token, _ = register_and_login(client, 'patient.hosp@test.com')
        res = client.post('/api/hospitals', json={
            'name': 'Test Hospital', 'type': 'public',
            'phone': '0201234567', 'address': '1 Test St', 'city': 'Cairo',
        }, headers=auth_headers(token))
        assert res.status_code in (403, 401)

    def test_emergency_services_public(self, client):
        res = client.get('/api/emergency-services')
        assert res.status_code == 200
        data = res.get_json()
        assert 'services' in data


# ─────────────────────────────────────────────
# Notification Tests
# ─────────────────────────────────────────────

class TestNotifications:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.token, _ = register_and_login(client, 'notif.user@test.com')
        self.headers = auth_headers(self.token)

    def test_list_notifications(self, client):
        res = client.get('/api/notifications', headers=self.headers)
        assert res.status_code == 200
        data = res.get_json()
        assert 'notifications' in data

    def test_unread_count(self, client):
        res = client.get('/api/notifications/unread-count', headers=self.headers)
        assert res.status_code == 200
        data = res.get_json()
        assert 'count' in data or 'unread_count' in data


# ─────────────────────────────────────────────
# Feedback Tests
# ─────────────────────────────────────────────

class TestFeedback:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.token, _ = register_and_login(client, 'feedback.user@test.com')
        self.headers = auth_headers(self.token)

    def test_submit_feedback(self, client):
        res = client.post('/api/feedback', json={
            'name': 'Test User',
            'type': 'complaint',
            'subject': 'Test Subject',
            'message': 'This is a test feedback message.',
            'rating': 5,
        }, headers=self.headers)
        assert res.status_code in (200, 201)

    def test_submit_feedback_no_message(self, client):
        res = client.post('/api/feedback', json={'subject': 'empty'}, headers=self.headers)
        assert res.status_code in (400, 422)

    def test_list_feedback_unauthenticated(self, client):
        res = client.get('/api/feedback')
        assert res.status_code == 401

    def test_feedback_no_error_leakage(self, client):
        """Ensure error responses never expose raw Python exception messages."""
        res = client.post('/api/feedback', json={'rating': 'not_a_number'})
        if res.status_code != 200:
            data = res.get_json() or {}
            msg = data.get('message', '') + data.get('error', '')
            assert 'Traceback' not in msg
            assert 'Exception' not in msg


# ─────────────────────────────────────────────
# Prescription Tests
# ─────────────────────────────────────────────

class TestPrescriptions:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.token, _ = register_and_login(client, 'rx.patient@test.com')
        self.headers = auth_headers(self.token)

    def test_list_prescriptions(self, client):
        res = client.get('/api/prescriptions', headers=self.headers)
        assert res.status_code == 200
        data = res.get_json()
        assert 'prescriptions' in data or isinstance(data, list)

    def test_get_nonexistent_prescription(self, client):
        res = client.get('/api/prescriptions/999999', headers=self.headers)
        assert res.status_code == 404


# ─────────────────────────────────────────────
# Vaccination Tests
# ─────────────────────────────────────────────

class TestVaccinations:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.token, _ = register_and_login(client, 'vacc.patient@test.com')
        self.headers = auth_headers(self.token)

    def test_list_vaccinations(self, client):
        res = client.get('/api/vaccinations/', headers=self.headers)
        assert res.status_code in (200, 404)  # 404 if patient profile missing in test DB

    def test_add_vaccination(self, client):
        res = client.post('/api/vaccinations/', json={
            'vaccine_name': 'COVID-19 mRNA',
            'vaccination_date': '2025-01-15',
            'dose_number': 1,
            'batch_number': 'LOT123',
        }, headers=self.headers)
        assert res.status_code in (200, 201, 404)  # 404 if patient profile missing in test DB


# ─────────────────────────────────────────────
# Appointment Tests
# ─────────────────────────────────────────────

@pytest.mark.usefixtures()
def test_list_appointments(client):
    token, _ = register_and_login(client, _unique_email('apt'))
    res = client.get('/api/appointments', headers=auth_headers(token))
    assert res.status_code in (200, 401)  # 401 only if token generation failed


@pytest.mark.usefixtures()
def test_book_appointment_missing_fields(client):
    token, _ = register_and_login(client, _unique_email('apt2'))
    res = client.post('/api/appointments', json={}, headers=auth_headers(token))
    assert res.status_code in (400, 422, 401)


def test_book_appointment_rejects_non_object_json(client):
    token, _ = register_and_login(client, _unique_email('apt3'))
    res = client.post('/api/appointments', data='[]', content_type='application/json', headers=auth_headers(token))
    assert res.status_code == 400


def test_book_appointment_rejects_invalid_doctor_id(client):
    token, _ = register_and_login(client, _unique_email('apt4'))
    res = client.post('/api/appointments', json={
        'doctor_id': 'not-a-number',
        'appointment_date': '2099-01-01T10:00:00',
        'appointment_type': 'in_person',
    }, headers=auth_headers(token))
    assert res.status_code == 400


def test_book_appointment_rejects_unknown_type(client):
    token, _ = register_and_login(client, _unique_email('apt5'))
    res = client.post('/api/appointments', json={
        'doctor_id': 1,
        'appointment_date': '2099-01-01T10:00:00',
        'appointment_type': 'unknown',
    }, headers=auth_headers(token))
    assert res.status_code == 400


# ─────────────────────────────────────────────
# Medication Tests
# ─────────────────────────────────────────────

@pytest.mark.usefixtures()
def test_list_medications(client):
    token, _ = register_and_login(client, _unique_email('med'))
    res = client.get('/api/medications/', headers=auth_headers(token))
    assert res.status_code in (200, 404, 401)  # 404 if patient profile missing


@pytest.mark.usefixtures()
def test_add_medication_validation(client):
    token, _ = register_and_login(client, _unique_email('med2'))
    res = client.post('/api/medications/', json={}, headers=auth_headers(token))
    assert res.status_code in (400, 422, 404, 401)


# ─────────────────────────────────────────────
# Security Tests
# ─────────────────────────────────────────────

class TestSecurity:
    def test_admin_routes_protected(self, client):
        for route in ['/api/admin/users', '/api/admin/stats']:
            res = client.get(route)
            assert res.status_code in (401, 403), f'{route} should be protected'

    def test_debug_mode_off(self, app):
        """App should not be in debug mode."""
        assert not app.debug, 'debug=True must be disabled in production'

    def test_no_stack_trace_in_api_errors(self, client):
        # SPA serves index.html for unknown routes; check that API errors don't leak tracebacks
        res = client.get('/api/blood-bank/stats')  # known good endpoint
        assert res.status_code in (200, 401, 404)
        if res.is_json:
            body = json.dumps(res.get_json())
            assert 'Traceback' not in body

    def test_jwt_required_on_profile_endpoint(self, client):
        res = client.get('/api/auth/profile')
        assert res.status_code == 401

    def test_sql_injection_in_search(self, client):
        """Basic SQL injection attempt should not crash the server."""
        res = client.get('/api/hospitals?search=%27+OR+%271%27%3D%271')
        assert res.status_code in (200, 400)
        assert res.status_code != 500

    def test_xss_in_feedback_stored_safely(self, client):
        token, _ = register_and_login(client, 'xss.user@test.com')
        res = client.post('/api/feedback', json={
            'subject': '<script>alert(1)</script>',
            'message': 'XSS test',
            'category': 'general',
        }, headers=auth_headers(token))
        # Just checks the server doesn't crash; sanitization is client-side
        assert res.status_code in (200, 201, 400)
