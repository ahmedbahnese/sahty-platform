from datetime import datetime

from flask import Blueprint, jsonify, request

from src.models.user import db, User
from src.models.notification import Notification
from src.models.professional import (
    NurseProfile,
    NursingRequestStatusHistory,
    NursingServiceRequest,
    ProfessionalRoleRequest,
)
from src.routes.auth import role_required, token_required

nursing_bp = Blueprint("nursing", __name__, url_prefix="/api/nursing")


def _notify(user_id, title, message, reference_id=None):
    db.session.add(Notification(
        user_id=user_id, title=title, message=message, type="nursing",
        reference_id=reference_id, reference_type="nursing_request",
    ))


def _change_status(item, status, user_id, note=None):
    item.status = status
    db.session.add(NursingRequestStatusHistory(
        request_id=item.id, status=status, changed_by=user_id, note=note,
    ))


@nursing_bp.route("/role-request", methods=["POST"])
@token_required
def request_nurse_role(current_user):
    data = request.get_json(silent=True) or {}
    required = ("full_name", "qualification", "license_number")
    if any(not data.get(field) for field in required):
        return jsonify({"message": "الاسم والمؤهل ورقم ترخيص التمريض مطلوبة"}), 400
    existing = ProfessionalRoleRequest.query.filter_by(
        user_id=current_user.id, requested_role="nurse", status="PENDING_APPROVAL"
    ).first()
    if existing:
        return jsonify({"message": "يوجد طلب تمريض قيد المراجعة", "request": existing.to_dict()}), 409
    request_row = ProfessionalRoleRequest(
        user_id=current_user.id,
        requested_role="nurse",
        documents={"id_document": data.get("id_document")},
        credentials={
            "full_name": data["full_name"],
            "qualification": data["qualification"],
            "license_number": data["license_number"],
            "additional": data.get("additional"),
        },
    )
    db.session.add(request_row)
    db.session.flush()
    nurse_profile = NurseProfile.query.filter_by(user_id=current_user.id).first()
    if nurse_profile:
        nurse_profile.full_name = data["full_name"]
        nurse_profile.qualification = data["qualification"]
        nurse_profile.license_number = data["license_number"]
        nurse_profile.credentials = data.get("additional") or {}
        nurse_profile.is_active = False
    else:
        db.session.add(NurseProfile(
            user_id=current_user.id, full_name=data["full_name"],
            qualification=data["qualification"], license_number=data["license_number"],
            credentials=data.get("additional") or {}, is_active=False,
        ))
    _notify(current_user.id, "تم إرسال طلب التسجيل كممرض", "سيتم مراجعة مؤهلاتك وإخطارك بالنتيجة.")
    db.session.commit()
    return jsonify({"message": "تم إرسال طلب التسجيل كممرض بنجاح", "request": request_row.to_dict()}), 201


@nursing_bp.route("/requests", methods=["GET", "POST"])
@token_required
def nursing_requests(current_user):
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        if not data.get("service_type") or not data.get("address"):
            return jsonify({"message": "نوع الخدمة والعنوان مطلوبان"}), 400
        scheduled_at = None
        if data.get("scheduled_at"):
            try:
                scheduled_at = datetime.fromisoformat(data["scheduled_at"].replace("Z", "+00:00"))
            except ValueError:
                return jsonify({"message": "موعد الزيارة غير صالح"}), 400
        item = NursingServiceRequest(
            patient_id=current_user.id, service_type=data["service_type"],
            description=data.get("description"), address=data["address"],
            scheduled_at=scheduled_at,
        )
        db.session.add(item)
        db.session.flush()
        _change_status(item, "PENDING", current_user.id)
        db.session.commit()
        return jsonify({"message": "تم إرسال طلب التمريض", "request": item.to_dict()}), 201

    if current_user.user_type == "nurse":
        rows = NursingServiceRequest.query.filter(
            (NursingServiceRequest.patient_id == current_user.id) |
            (NursingServiceRequest.nurse_id == current_user.id) |
            (NursingServiceRequest.status.in_(("PENDING", "UNDER_REVIEW")))
        ).order_by(NursingServiceRequest.created_at.desc()).all()
    else:
        rows = NursingServiceRequest.query.filter_by(
            patient_id=current_user.id
        ).order_by(NursingServiceRequest.created_at.desc()).all()
    return jsonify({"requests": [row.to_dict() for row in rows]})


@nursing_bp.route("/requests/<int:request_id>/accept", methods=["POST"])
@token_required
@role_required("nurse")
def accept_request(current_user, request_id):
    nurse = NurseProfile.query.filter_by(user_id=current_user.id, is_active=True).first()
    if not nurse:
        return jsonify({"message": "لا يمكن إلا للممرض المعتمد قبول الطلبات"}), 403
    item = db.session.get(NursingServiceRequest, request_id)
    if not item or item.status not in ("PENDING", "UNDER_REVIEW"):
        return jsonify({"message": "الطلب غير متاح للقبول"}), 404
    item.nurse_id = current_user.id
    _change_status(item, "ACCEPTED", current_user.id)
    _notify(item.patient_id, "تم قبول طلب التمريض", "تم قبول طلبك وسيتم جدولة الزيارة.", item.id)
    db.session.commit()
    return jsonify({"request": item.to_dict()})


@nursing_bp.route("/requests/<int:request_id>/reject", methods=["POST"])
@token_required
@role_required("nurse")
def reject_request(current_user, request_id):
    nurse = NurseProfile.query.filter_by(user_id=current_user.id, is_active=True).first()
    if not nurse:
        return jsonify({"message": "الممرض غير معتمد"}), 403
    item = db.session.get(NursingServiceRequest, request_id)
    if not item or item.status not in ("PENDING", "UNDER_REVIEW"):
        return jsonify({"message": "الطلب غير متاح للرفض"}), 404
    note = (request.get_json(silent=True) or {}).get("reason")
    _change_status(item, "REJECTED", current_user.id, note)
    item.rejection_reason = note
    _notify(item.patient_id, "تم رفض طلب التمريض", note or "تعذر قبول الطلب حالياً.", item.id)
    db.session.commit()
    return jsonify({"request": item.to_dict()})


@nursing_bp.route("/requests/<int:request_id>/complete", methods=["POST"])
@token_required
@role_required("nurse")
def complete_request(current_user, request_id):
    item = db.session.get(NursingServiceRequest, request_id)
    if not item or item.nurse_id != current_user.id:
        return jsonify({"message": "الطلب غير موجود أو غير مسند إليك"}), 404
    item.visit_notes = (request.get_json(silent=True) or {}).get("visit_notes")
    _change_status(item, "COMPLETED", current_user.id, item.visit_notes)
    _notify(item.patient_id, "اكتملت زيارة التمريض", "تم توثيق زيارة التمريض بنجاح.", item.id)
    db.session.commit()
    return jsonify({"request": item.to_dict()})