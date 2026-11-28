"""Regression coverage for high-risk privacy and upload regressions."""

import io
from datetime import datetime
from types import SimpleNamespace

from werkzeug.datastructures import FileStorage


def test_public_medical_share_is_disabled(client):
    response = client.get('/api/medical-record/public/1:invalid')
    assert response.status_code == 410
    assert 'patient' not in (response.get_json() or {})


def test_public_token_minting_is_disabled(client):
    response = client.get('/api/medical-record/public-token')
    # The route still requires an authenticated user; the public surface itself
    # must not issue any permanent share token.
    assert response.status_code == 401


def test_doctor_profile_image_requires_authentication(client):
    response = client.get('/api/doctors/profile-images/not-a-real-image.png')
    assert response.status_code == 401


def test_public_blood_request_projection_excludes_private_fields():
    from src.routes.blood_bank import _public_request_dict

    row = SimpleNamespace(
        id=7,
        blood_type='O+',
        units_needed=2,
        component_type='whole_blood',
        is_irradiated=False,
        urgency_level='urgent',
        hospital_name='مستشفى اختباري',
        city='القاهرة',
        status='active',
        needed_by_date=datetime(2026, 11, 28),
        document_status='document_required',
        created_at=datetime(2026, 11, 27),
        patient_id=111,
        patient_name='بيانات سرية',
        medical_condition='بيانات سرية',
        contact_phone='01000000000',
        hospital_address='عنوان خاص',
        transfusion_request_file_path='private/file.pdf',
    )

    result = _public_request_dict(row)

    assert result['blood_type'] == 'O+'
    assert not ({'patient_id', 'patient_name', 'medical_condition', 'contact_phone',
                 'hospital_address', 'transfusion_request_file_path'} & result.keys())


def test_blood_document_is_saved_byte_for_byte(monkeypatch, tmp_path):
    from src.routes import blood_bank

    monkeypatch.setattr(blood_bank, 'UPLOAD_ROOT', str(tmp_path))
    payload = b'%PDF-1.7\nmedical-document-bytes\n%%EOF'
    upload = FileStorage(stream=io.BytesIO(payload), filename='request.pdf', content_type='application/pdf')

    saved, error = blood_bank._save_transfusion_document(upload)

    assert error is None
    relative_path, original_name = saved
    stored_path = tmp_path / relative_path.split('/', 1)[1]
    assert original_name == 'request.pdf'
    assert stored_path.read_bytes() == payload


def test_consultation_attachment_is_saved_byte_for_byte(monkeypatch, tmp_path):
    from src.routes import consultation

    monkeypatch.setattr(consultation, 'CONSULTATION_UPLOAD_DIR', str(tmp_path))
    payload = b'\x89PNG\r\n\x1a\nfixture-image-data'
    upload = FileStorage(stream=io.BytesIO(payload), filename='attachment.png', content_type='image/png')

    saved, error = consultation._save_attachment(upload, 123)

    assert error is None
    stored_name, original_name, mime_type, size = saved
    assert (tmp_path / stored_name).read_bytes() == payload
    assert original_name == 'attachment.png'
    assert mime_type == 'image/png'
    assert size == len(payload)


def test_vercel_database_limiter_uses_shared_counter(client, app, monkeypatch):
    import main
    from src.models.rate_limit import RequestRateLimit
    from src.models.user import db

    monkeypatch.setattr(main, "use_vercel_database_limiter", True)
    app.config["TESTING"] = False
    try:
        response = client.get(
            "/api/blood-bank/stats",
            headers={"X-Real-IP": "203.0.113.41"},
        )
        assert response.status_code == 200
        counters = RequestRateLimit.query.order_by(RequestRateLimit.key).all()
        assert len(counters) == 2
        assert all(item.request_count == 1 for item in counters)
    finally:
        app.config["TESTING"] = True
        db.session.remove()
