"""Focused regression tests for the Phase 1 security boundaries."""

import uuid

from src.models.blood_bank import BloodDonor
from src.models.lab_radiology import LabRequest, RadiologyRequest
from src.models.patient import Patient
from src.models.professional import Role, UserRole
from src.models.user import User, db
from src.routes.auth import _issue_session


def _registration_payload(email, user_type='patient'):
    suffix = uuid.uuid4().hex[:10]
    payload = {
        'username': f'user_{suffix}',
        'email': email,
        'password': 'Secure123!',
        'user_type': user_type,
        'first_name': 'Security',
        'last_name': 'Test',
        'date_of_birth': '1990-01-01',
        'gender': 'female',
        'national_id': f'2{suffix}000000',
        'phone': f'010{suffix[:8]}',
    }
    if user_type != 'patient':
        payload.update({
            'legal_name': 'Security Provider',
            'license_number': f'LIC-{suffix}',
            'address': 'Test address',
            'city': 'Cairo',
        })
    return payload


def _register_and_login(client, email):
    registration = client.post(
        '/api/auth/register',
        json=_registration_payload(email),
    )
    assert registration.status_code == 201
    login = client.post(
        '/api/auth/login',
        json={'email': email, 'password': 'Secure123!'},
    )
    assert login.status_code == 200
    return login.get_json()['token']


def _headers(token):
    return {'Authorization': f'Bearer {token}'}


def test_registration_cannot_create_administrative_roles(client):
    for role in ('admin', 'super_admin'):
        response = client.post(
            '/api/auth/register',
            json=_registration_payload(
                f'{role}-{uuid.uuid4().hex[:8]}@test.com',
                user_type=role,
            ),
        )
        assert response.status_code == 400


def test_professional_registration_stays_patient_until_activation(client):
    email = f'doctor-{uuid.uuid4().hex[:8]}@test.com'
    response = client.post(
        '/api/auth/register',
        json=_registration_payload(email, user_type='doctor'),
    )
    assert response.status_code == 201
    assert response.get_json()['user']['user_type'] == 'patient'

    login = client.post(
        '/api/auth/login',
        json={'email': email, 'password': 'Secure123!', 'role': 'doctor'},
    )
    assert login.status_code == 200
    assert login.get_json()['user']['user_type'] == 'patient'


def test_signed_token_with_unapproved_role_is_rejected(client):
    email = f'role-tamper-{uuid.uuid4().hex[:8]}@test.com'
    _register_and_login(client, email)
    user = User.query.filter_by(email=email).one()

    token, _ = _issue_session(user, selected_role='doctor')
    db.session.commit()
    response = client.get('/api/auth/profile', headers=_headers(token))

    assert response.status_code == 403


def test_explicit_active_role_allows_role_selected_in_token(client):
    email = f'active-role-{uuid.uuid4().hex[:8]}@test.com'
    _register_and_login(client, email)
    user = User.query.filter_by(email=email).one()
    role = Role.query.filter_by(name='doctor').first()
    if role is None:
        role = Role(name='doctor', label_ar='طبيب')
        db.session.add(role)
        db.session.flush()
    db.session.add(UserRole(user_id=user.id, role_id=role.id, status='ACTIVE'))
    db.session.commit()

    login = client.post(
        '/api/auth/login',
        json={'email': email, 'password': 'Secure123!', 'role': 'doctor'},
    )
    assert login.status_code == 200
    assert login.get_json()['user']['user_type'] == 'doctor'


def test_other_patient_cannot_upload_lab_results(client):
    owner_token = _register_and_login(
        client, f'lab-owner-{uuid.uuid4().hex[:8]}@test.com'
    )
    other_token = _register_and_login(
        client, f'lab-other-{uuid.uuid4().hex[:8]}@test.com'
    )
    owner = User.query.filter(User.email.like('lab-owner-%')).order_by(User.id.desc()).first()
    patient = Patient.query.filter_by(user_id=owner.id).one()
    request = LabRequest(
        patient_id=patient.id,
        requesting_user_id=owner.id,
        test_name='CBC',
        tests_json='[{"name":"CBC"}]',
        status='requested',
    )
    db.session.add(request)
    db.session.commit()

    response = client.post(
        f'/api/lab-requests/{request.id}/results',
        json={'result_value': 'normal'},
        headers=_headers(other_token),
    )

    assert response.status_code == 403
    assert LabRequest.query.get(request.id).result_value is None


def test_other_patient_cannot_upload_radiology_results(client):
    owner_token = _register_and_login(
        client, f'rad-owner-{uuid.uuid4().hex[:8]}@test.com'
    )
    other_token = _register_and_login(
        client, f'rad-other-{uuid.uuid4().hex[:8]}@test.com'
    )
    owner = User.query.filter(User.email.like('rad-owner-%')).order_by(User.id.desc()).first()
    patient = Patient.query.filter_by(user_id=owner.id).one()
    request = RadiologyRequest(
        patient_id=patient.id,
        requesting_user_id=owner.id,
        scan_type='xray',
        body_part='chest',
        status='requested',
    )
    db.session.add(request)
    db.session.commit()

    response = client.post(
        f'/api/radiology-requests/{request.id}/report',
        json={'findings': 'should not be accepted'},
        headers=_headers(other_token),
    )

    assert response.status_code == 403
    assert RadiologyRequest.query.get(request.id).findings is None


def test_public_donor_search_does_not_expose_donor_name(client):
    email = f'donor-{uuid.uuid4().hex[:8]}@test.com'
    _register_and_login(client, email)
    user = User.query.filter_by(email=email).one()
    patient = Patient.query.filter_by(user_id=user.id).one()
    donor = BloodDonor(
        patient_id=patient.id,
        blood_type='O+',
        weight=70,
        age=30,
        city='Cairo',
        is_eligible=True,
        available_for_emergency=True,
        notification_enabled=True,
    )
    db.session.add(donor)
    db.session.commit()

    response = client.get(
        '/api/blood-bank/compatible-donors',
        query_string={'blood_type': 'O+'},
    )

    assert response.status_code == 200
    assert response.get_json()['donors']
    assert all('donor_name' not in item for item in response.get_json()['donors'])