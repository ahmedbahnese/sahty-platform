"""Strict negative authorization coverage for privileged and session-bound APIs."""

import io
import json
import os
import uuid

import jwt
from src.models.lab_radiology import LabRequest, RadiologyRequest
from src.models.patient import Patient
from src.models.user import User, db


def _register_and_login(client):
    email = f"negative-auth-{uuid.uuid4().hex}@test.com"
    response = client.post(
        "/api/auth/register",
        json={
            "first_name": "Negative",
            "last_name": "Authorization",
            "email": email,
            "password": "Secure123!",
            "date_of_birth": "1990-01-01",
            "gender": "other",
            "user_type": "patient",
            "national_id": f"9{uuid.uuid4().int % 10**13:013d}",
        },
    )
    assert response.status_code == 201
    token = response.get_json()["token"]
    return token


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_admin_endpoint_rejects_anonymous_request(client):
    response = client.get("/api/admin/users")

    assert response.status_code == 401


def test_admin_endpoint_rejects_authenticated_patient(client):
    token = _register_and_login(client)

    response = client.get("/api/admin/users", headers=_auth_header(token))

    assert response.status_code == 403


def test_role_switch_rejects_unassigned_admin_role(client):
    token = _register_and_login(client)

    response = client.post(
        "/api/auth/switch-role",
        json={"role": "admin"},
        headers=_auth_header(token),
    )

    assert response.status_code == 403


def test_signed_token_with_wrong_secret_is_rejected(client):
    token = jwt.encode(
        {"user_id": 1, "user_type": "admin"},
        "wrong-secret",
        algorithm="HS256",
    )

    response = client.get("/api/admin/users", headers=_auth_header(token))

    assert response.status_code == 401


def test_revoked_session_cannot_access_protected_endpoint(client):
    token = _register_and_login(client)
    headers = _auth_header(token)

    logout = client.post("/api/auth/logout", headers=headers)
    assert logout.status_code == 200

    response = client.get("/api/auth/profile", headers=headers)

    assert response.status_code == 401


def test_patient_file_access_is_scoped_to_the_owning_patient(client):
    def register(email, first_name):
        response = client.post(
            "/api/auth/register",
            json={
                "first_name": first_name,
                "last_name": "File",
                "email": email,
                "password": "Secure123!",
                "date_of_birth": "1990-01-01",
                "gender": "other",
                "national_id": f"{first_name}-{uuid.uuid4().hex}",
                "user_type": "patient",
            },
        )
        assert response.status_code == 201
        return response.get_json()["token"]

    email_a = f"file-a-{uuid.uuid4().hex}@test.com"
    email_b = f"file-b-{uuid.uuid4().hex}@test.com"
    token_a = register(email_a, "FileA")
    token_b = register(email_b, "FileB")

    patient_a = Patient.query.filter_by(email=email_a).first()
    patient_b = Patient.query.filter_by(email=email_b).first()
    user_a = User.query.filter_by(email=email_a).first()
    user_b = User.query.filter_by(email=email_b).first()

    file_a = f"{uuid.uuid4().hex}.png"
    file_b = f"{uuid.uuid4().hex}.png"
    upload_dir = os.path.join("static", "uploads", "radiology_images")
    os.makedirs(upload_dir, exist_ok=True)
    paths = [
        os.path.join(upload_dir, file_a),
        os.path.join(upload_dir, file_b),
    ]
    for path, contents in zip(paths, (b"FILE_A", b"FILE_B")):
        with open(path, "wb") as handle:
            handle.write(contents)

    try:
        request_a = RadiologyRequest(
            patient_id=patient_a.id,
            requesting_user_id=user_a.id,
            scan_type="xray",
            body_part="chest",
            image_paths_json=json.dumps([{"name": "a.png", "path": file_a}]),
        )
        request_b = RadiologyRequest(
            patient_id=patient_b.id,
            requesting_user_id=user_b.id,
            scan_type="xray",
            body_part="chest",
            image_paths_json=json.dumps([{"name": "b.png", "path": file_b}]),
        )
        db.session.add_all([request_a, request_b])
        db.session.commit()

        own_file = client.get(
            f"/api/uploads/radiology_images/{file_a}",
            headers=_auth_header(token_a),
        )
        other_file_a = client.get(
            f"/api/uploads/radiology_images/{file_b}",
            headers=_auth_header(token_a),
        )
        other_file_b = client.get(
            f"/api/uploads/radiology_images/{file_a}",
            headers=_auth_header(token_b),
        )

        assert own_file.status_code == 200
        assert own_file.data == b"FILE_A"
        assert other_file_a.status_code == 403
        assert other_file_b.status_code == 403

        cross_patient_upload = client.post(
            f"/api/radiology-requests/{request_b.id}/images",
            headers=_auth_header(token_a),
            data={"images": (io.BytesIO(b"EVIL"), "cross-patient.png")},
            content_type="multipart/form-data",
        )
        assert cross_patient_upload.status_code == 403
    finally:
        for path in paths:
            if os.path.exists(path):
                os.remove(path)


def test_patient_cannot_read_another_patient_lab_request(client):
    email_a = f"lab-owner-a-{uuid.uuid4().hex}@test.com"
    email_b = f"lab-owner-b-{uuid.uuid4().hex}@test.com"
    response_a = client.post(
        "/api/auth/register",
        json={
            "first_name": "Lab",
            "last_name": "Owner A",
            "email": email_a,
            "password": "Secure123!",
            "date_of_birth": "1990-01-01",
            "gender": "other",
            "user_type": "patient",
            "national_id": f"7{uuid.uuid4().int % 10**13:013d}",
        },
    )
    response_b = client.post(
        "/api/auth/register",
        json={
            "first_name": "Lab",
            "last_name": "Owner B",
            "email": email_b,
            "password": "Secure123!",
            "date_of_birth": "1990-01-01",
            "gender": "other",
            "user_type": "patient",
            "national_id": f"8{uuid.uuid4().int % 10**13:013d}",
        },
    )
    token_a = response_a.get_json()["token"]
    user_a = User.query.filter_by(email=email_a).one()
    user_b = User.query.filter_by(email=email_b).one()
    patient_b = Patient.query.filter_by(user_id=user_b.id).one()
    request_b = LabRequest(
        patient_id=patient_b.id,
        requesting_user_id=user_b.id,
        test_name="CBC",
        tests_json='[{"name":"CBC"}]',
        status="requested",
    )
    db.session.add(request_b)
    db.session.commit()

    listing = client.get('/api/lab-requests', headers=_auth_header(token_a))
    detail = client.get(f'/api/lab-requests/{request_b.id}', headers=_auth_header(token_a))

    assert listing.status_code == 200
    assert request_b.id not in {item['id'] for item in listing.get_json()}
    assert detail.status_code == 403


def test_patient_token_cannot_activate_unassigned_professional_role(client):
    token = _register_and_login(client)

    response = client.get('/api/auth/profile', headers=_auth_header(token))

    assert response.status_code == 200
    profile = response.get_json()['user']
    assert profile['user_type'] == 'patient'
    assert 'doctor' not in profile['active_roles']

    switch = client.post(
        '/api/auth/switch-role',
        json={'role': 'doctor'},
        headers=_auth_header(token),
    )
    assert switch.status_code == 403
