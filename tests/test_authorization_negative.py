"""Strict negative authorization coverage for privileged and session-bound APIs."""

import uuid

import jwt


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