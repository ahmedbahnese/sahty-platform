"""Read-only API for the imported, verified Egypt healthcare directory."""

from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from src.models.user import db
from src.models.egypt_healthcare import EgyptFacility

egypt_healthcare_bp = Blueprint(
    "egypt_healthcare", __name__, url_prefix="/api/facilities"
)


@egypt_healthcare_bp.route("", methods=["GET"])
def list_facilities():
    search = request.args.get("search", "").strip()
    governorate = request.args.get("governorate", "").strip()
    city = request.args.get("city", "").strip()
    facility_type = request.args.get("type", "").strip()
    ownership = request.args.get("ownership", "").strip()
    emergency = request.args.get("emergency") == "1"
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 20, type=int), 1), 100)

    query = EgyptFacility.query.join(EgyptFacility.governorate).join(
        EgyptFacility.city
    ).join(EgyptFacility.facility_type).join(EgyptFacility.ownership_type)

    if search:
        query = query.filter(
            or_(
                EgyptFacility.name_ar.ilike(f"%{search}%"),
                EgyptFacility.name_en.ilike(f"%{search}%"),
                EgyptFacility.full_address.ilike(f"%{search}%"),
            )
        )
    if governorate:
        query = query.filter(
            or_(
                EgyptFacility.governorate.has(name_ar=governorate),
                EgyptFacility.governorate.has(name_en=governorate),
            )
        )
    if city:
        query = query.filter(
            or_(
                EgyptFacility.city.has(name_ar=city),
                EgyptFacility.city.has(name_en=city),
            )
        )
    if facility_type:
        query = query.filter(
            or_(
                EgyptFacility.facility_type.has(name_ar=facility_type),
                EgyptFacility.facility_type.has(name_en=facility_type),
            )
        )
    if ownership:
        query = query.filter(
            or_(
                EgyptFacility.ownership_type.has(name_ar=ownership),
                EgyptFacility.ownership_type.has(name_en=ownership),
            )
        )
    if emergency:
        query = query.filter(EgyptFacility.has_emergency_dept.is_(True))

    total = query.count()
    facilities = query.order_by(EgyptFacility.name_ar).offset(
        (page - 1) * per_page
    ).limit(per_page).all()
    return jsonify({
        "facilities": [facility.to_dict() for facility in facilities],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    })


@egypt_healthcare_bp.route("/<int:facility_id>", methods=["GET"])
def get_facility(facility_id):
    facility = db.session.get(EgyptFacility, facility_id)
    if not facility:
        return jsonify({"message": "المنشأة غير موجودة"}), 404
    return jsonify({"facility": facility.to_dict()})