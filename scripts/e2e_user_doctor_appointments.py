"""Executable end-to-end smoke test for the user/doctor/appointment journey.

This uses an isolated test database supplied through DATABASE_URL. It never runs
against production because the script requires FLASK_ENV=development.
"""
from datetime import date, datetime, time, timedelta
import os
import sys
from pathlib import Path

if os.environ.get('FLASK_ENV') != 'development':
    raise SystemExit('Refusing E2E smoke test unless FLASK_ENV=development')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from werkzeug.security import generate_password_hash
from main import app, db
from src.models.user import User
from src.models.doctor import Doctor, DoctorAvailability


def expect(response, status, label):
    if response.status_code != status:
        raise AssertionError(f'{label}: expected {status}, got {response.status_code}: {response.get_data(as_text=True)[:300]}')
    return response.get_json(silent=True) or {}


def main():
    with app.app_context():
        db.drop_all()
        db.create_all()
        client = app.test_client()

        register = expect(client.post('/api/auth/register', json={
            'first_name': 'مريض', 'last_name': 'اختبار',
            'email': 'e2e.patient@example.com', 'password': 'Patient123',
            'user_type': 'patient', 'date_of_birth': '1990-01-01',
            'gender': 'male', 'national_id': '29901010000001',
        }), 201, 'register patient')
        patient_token = register['token']
        patient_headers = {'Authorization': f'Bearer {patient_token}'}

        profile = expect(client.get('/api/auth/profile', headers=patient_headers), 200, 'patient profile')
        assert profile.get('user') or profile.get('profile')
        expect(client.post('/api/auth/switch-role', json={'role': 'admin'}, headers=patient_headers), 403, 'reject unassigned role')

        doctor_user = User(
            username='e2e.doctor', email='e2e.doctor@example.com',
            password_hash=generate_password_hash('Doctor123'),
            user_type='doctor', is_active=True,
        )
        db.session.add(doctor_user)
        db.session.flush()
        doctor = Doctor(
            user_id=doctor_user.id, first_name='طبيب', last_name='اختبار',
            phone='01000000001', email=doctor_user.email, license_number='E2E-LICENSE-1',
            specialization='باطنة', clinic_name='عيادة الاختبار', consultation_fee=100,
            consultation_duration=30, is_active=True, is_verified=True,
        )
        db.session.add(doctor)
        db.session.flush()
        db.session.add(DoctorAvailability(
            doctor_id=doctor.id, day_of_week=(date.today().weekday() + 1) % 7,
            start_time=time(9, 0), end_time=time(17, 0), is_available=True,
        ))
        db.session.commit()

        doctors = expect(client.get('/api/doctors?specialty=باطنة&per_page=20'), 200, 'doctor search')
        assert any(item.get('id') == doctor.id for item in doctors.get('doctors', []))
        future = datetime.utcnow() + timedelta(days=2)
        slots = expect(client.get(f'/api/doctors/{doctor.id}/available-slots?date={future.date().isoformat()}', headers=patient_headers), 200, 'availability')
        assert isinstance(slots, dict)

        appointment = expect(client.post('/api/appointments', json={
            'doctor_id': doctor.id,
            'appointment_date': future.replace(hour=10, minute=0, second=0, microsecond=0).isoformat(),
            'appointment_type': 'in_person',
            'reason': 'فحص دوري',
        }, headers=patient_headers), 201, 'book appointment')
        appointment_id = appointment['appointment']['id']

        doctor_login = expect(client.post('/api/auth/login', json={
            'email': doctor_user.email, 'password': 'Doctor123',
        }), 200, 'doctor login')
        doctor_headers = {'Authorization': f"Bearer {doctor_login['token']}"}
        expect(client.post(f'/api/appointments/{appointment_id}/confirm', headers=doctor_headers, json={'notes': 'تم التأكيد'}), 200, 'confirm appointment')
        expect(client.post(f'/api/appointments/{appointment_id}/complete', headers=doctor_headers, json={'notes': 'تمت الزيارة'}), 200, 'complete appointment')

        final = expect(client.get(f'/api/appointments/{appointment_id}', headers=patient_headers), 200, 'patient reads final appointment')
        assert final['appointment']['status'] == 'completed'
        print('E2E_USER_DOCTOR_APPOINTMENT=PASS')
        print(f"patient_id={register['user']['id']} doctor_id={doctor.id} appointment_id={appointment_id}")


if __name__ == '__main__':
    main()
