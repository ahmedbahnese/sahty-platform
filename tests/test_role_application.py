"""Regression coverage for professional role applications."""

import uuid

from src.models.notification import Notification
from src.models.professional import ProfessionalRoleRequest, Role, UserRole
from src.models.provider import ProviderRegistration
from src.models.user import User


def _register_patient(client):
    email = f"role-application-{uuid.uuid4().hex}@test.com"
    response = client.post(
        "/api/auth/register",
        json={
            "first_name": "Role",
            "last_name": "Applicant",
            "email": email,
            "password": "Secure123!",
            "date_of_birth": "1990-01-01",
            "gender": "other",
            "national_id": f"9{uuid.uuid4().int % 10**13:013d}",
            "user_type": "patient",
        },
    )
    assert response.status_code == 201
    return response.get_json()["token"], User.query.filter_by(email=email).one()


def _role_application_payload():
    return {
        "role": "doctor",
        "full_name": "Role Applicant",
        "license_number": "DOC-12345",
        "qualification": "MBBS",
        "specialization": "Internal Medicine",
        "id_document": "id-document.png",
        "professional_license": "license.png",
        "address": "1 Test Street",
        "city": "Cairo",
    }


def test_apply_role_creates_pending_workflow_and_system_notification(client):
    token, user = _register_patient(client)

    response = client.post(
        "/api/auth/apply-role",
        json=_role_application_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["message"] == "تم إرسال طلبك بنجاح. سيظل حساب المريض متاحاً حتى اعتماد الدور."
    assert body["request"]["requested_role"] == "doctor"
    assert body["request"]["status"] == "PENDING_APPROVAL"

    role = Role.query.filter_by(name="doctor").one()
    user_role = UserRole.query.filter_by(user_id=user.id, role_id=role.id).one()
    assert user_role.status == "PENDING_APPROVAL"

    request_row = ProfessionalRoleRequest.query.filter_by(
        user_id=user.id, requested_role="doctor"
    ).one()
    assert request_row.credentials["license_number"] == "DOC-12345"
    assert request_row.documents["professional_license"] == "license.png"

    provider = ProviderRegistration.query.filter_by(user_id=user.id).one()
    assert provider.provider_type == "doctor"
    assert provider.status == "pending"

    notification = Notification.query.filter_by(user_id=user.id).one()
    assert notification.title == "تم استلام طلب الدور المهني"
    assert notification.type == "system"
    assert notification.reference_id is None
    assert notification.reference_type is None

    notifications_response = client.get(
        "/api/notifications",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert notifications_response.status_code == 200
    assert notifications_response.get_json()["notifications"] == [notification.to_dict()]


def test_apply_role_rejects_duplicate_pending_request(client):
    token, user = _register_patient(client)
    headers = {"Authorization": f"Bearer {token}"}

    first_response = client.post(
        "/api/auth/apply-role",
        json=_role_application_payload(),
        headers=headers,
    )
    assert first_response.status_code == 201

    duplicate_response = client.post(
        "/api/auth/apply-role",
        json=_role_application_payload(),
        headers=headers,
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.get_json()["message"] == "يوجد طلب قيد المراجعة لهذا الدور"
    assert ProfessionalRoleRequest.query.filter_by(
        user_id=user.id, requested_role="doctor"
    ).count() == 1
    assert Notification.query.filter_by(user_id=user.id).count() == 1