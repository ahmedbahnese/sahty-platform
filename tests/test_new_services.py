from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from src.models.user import db, User


def _user(email, user_type):
    user = User(
        username=email.split('@')[0],
        email=email,
        password_hash=generate_password_hash('Test1234!'),
        user_type=user_type,
        is_active=True,
    )
    db.session.add(user)
    db.session.flush()
    return user


def _token(user):
    from src.routes.auth import _issue_session
    token, _ = _issue_session(user)
    db.session.commit()
    return token


def test_video_consultation_chat_and_doctor_result(app, client):
    patient = _user('service-patient@test.com', 'patient')
    doctor = _user('service-doctor@test.com', 'doctor')
    patient_token = _token(patient)
    doctor_token = _token(doctor)

    created = client.post('/api/consultations', headers={'Authorization': f'Bearer {patient_token}'}, json={
        'doctor_id': doctor.id,
        'scheduled_at': (datetime.utcnow() + timedelta(days=1)).isoformat(),
    })
    assert created.status_code == 201
    consultation_id = created.get_json()['consultation']['id']
    assert created.get_json()['consultation']['meeting_url']

    sent = client.post(f'/api/consultations/{consultation_id}/messages', headers={'Authorization': f'Bearer {doctor_token}'}, json={'body': 'تمت مراجعة التقارير.'})
    assert sent.status_code == 201

    completed = client.post(f'/api/consultations/{consultation_id}/complete', headers={'Authorization': f'Bearer {doctor_token}'}, json={
        'diagnosis': 'التهاب بسيط',
        'treatment_plan': 'المتابعة حسب تعليمات الطبيب',
        'prescription': {'text': 'روشتة إلكترونية تجريبية محفوظة في الاستشارة'},
        'referral_type': 'follow_up',
    })
    assert completed.status_code == 200
    assert completed.get_json()['consultation']['status'] == 'completed'


def test_doctor_can_request_home_visit_for_patient(app, client):
    patient = _user('home-patient@test.com', 'patient')
    doctor = _user('home-doctor@test.com', 'doctor')
    doctor_token = _token(doctor)

    response = client.post('/api/nursing/requests', headers={'Authorization': f'Bearer {doctor_token}'}, json={
        'patient_id': patient.id,
        'service_type': 'زيارة تمريض منزلية',
        'provider_role': 'nurse',
        'request_type': 'home_visit',
        'address': 'القاهرة - عنوان الاختبار',
        'description': 'متابعة العلامات الحيوية',
    })
    assert response.status_code == 201
    payload = response.get_json()['request']
    assert payload['patient_id'] == patient.id
    assert payload['doctor_id'] == doctor.id
    assert payload['requester_role'] == 'doctor'
