"""Read-only API for the imported, verified Egypt healthcare directory."""

from flask import Blueprint, jsonify, request
from sqlalchemy import func, or_

from src.models.user import db
from src.models.egypt_healthcare import EgyptFacility, HealthcareDirectoryRecord

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
    open_now = request.args.get("open_now") == "1"
    home_services = request.args.get("home_services") == "1"
    nearest = request.args.get("nearest") == "1"
    specialty = request.args.get("specialty", "").strip()
    user_lat = request.args.get("lat", type=float)
    user_lng = request.args.get("lng", type=float)
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 20, type=int), 1), 100)

    flat_query = HealthcareDirectoryRecord.query
    type_map = {
        "hospital": "hospital", "pharmacy": "pharmacy",
        "laboratory": "laboratory", "lab": "laboratory",
        "radiology": "radiology_center", "radiology_center": "radiology_center",
        "radiology center": "radiology_center",
        "ambulance": "ambulance", "ambulance center": "ambulance",
        "ambulance station": "ambulance",
        "blood bank": "blood_bank", "blood_bank": "blood_bank",
        "clinic": "clinic", "doctor": "doctor", "dentist": "dentist",
        "health center": "health_center", "health_center": "health_center",
    }
    requested_type = type_map.get(facility_type.lower(), facility_type.lower())
    if requested_type:
        flat_query = flat_query.filter(
            func.lower(HealthcareDirectoryRecord.facility_type) == requested_type
        )
    if search:
        flat_query = flat_query.filter(or_(
            HealthcareDirectoryRecord.name_ar.ilike(f"%{search}%"),
            HealthcareDirectoryRecord.name_en.ilike(f"%{search}%"),
            HealthcareDirectoryRecord.address.ilike(f"%{search}%"),
        ))
    if governorate:
        flat_query = flat_query.filter(HealthcareDirectoryRecord.governorate.ilike(f"%{governorate}%"))
    if city:
        flat_query = flat_query.filter(HealthcareDirectoryRecord.city.ilike(f"%{city}%"))
    if specialty:
        flat_query = flat_query.filter(HealthcareDirectoryRecord.specialty.ilike(f"%{specialty}%"))
    if home_services:
        flat_query = flat_query.filter(HealthcareDirectoryRecord.home_services.is_(True))
    if emergency:
        flat_query = flat_query.filter(HealthcareDirectoryRecord.emergency_24_7.is_(True))
    imported_directory_available = HealthcareDirectoryRecord.query.first() is not None
    records = flat_query.all()
    serialized = [
        record.to_dict(user_lat, user_lng)
        for record in records
        if not open_now or record._is_open_now() is True
    ]
    if nearest and user_lat is not None and user_lng is not None:
        # Nearest mode shows the nearest places only (with real coordinates),
        # not the whole directory merely re-sorted.
        serialized = [item for item in serialized if item["distance_km"] is not None]
        serialized.sort(key=lambda item: item["distance_km"])
        serialized = serialized[:20]
    else:
        serialized.sort(key=lambda item: item["name_ar"])
    if imported_directory_available:
        total = len(serialized)
        start = (page - 1) * per_page
        return jsonify({
            "facilities": serialized[start:start + per_page],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        })

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


@egypt_healthcare_bp.route("/metadata", methods=["GET"])
def directory_metadata():
    from src.models.egypt_healthcare import EgyptCity, EgyptGovernorate

    rows = HealthcareDirectoryRecord.query.with_entities(
        HealthcareDirectoryRecord.facility_type,
        HealthcareDirectoryRecord.governorate,
        HealthcareDirectoryRecord.city,
    ).all()
    # Cities grouped by governorate, from the reference table (complete
    # district lists), so the city filter only offers the selected
    # governorate's own cities/districts.
    grouped = {}
    city_rows = (
        db.session.query(EgyptCity.name_ar, EgyptGovernorate.name_ar)
        .join(EgyptGovernorate, EgyptCity.governorate_id == EgyptGovernorate.id)
        .all()
    )
    for city_ar, gov_ar in city_rows:
        grouped.setdefault(gov_ar, []).append(city_ar)
    # Any city used by directory records but missing from the reference
    # table still appears under its governorate.
    for _type, gov_ar, city_ar in rows:
        if gov_ar and city_ar:
            grouped.setdefault(gov_ar, [])
            if city_ar not in grouped[gov_ar]:
                grouped[gov_ar].append(city_ar)
    for gov in grouped:
        grouped[gov] = sorted(set(grouped[gov]))
    all_cities = sorted({c for cities in grouped.values() for c in cities})
    return jsonify({
        "facility_types": sorted({row[0] for row in rows}),
        "governorates": sorted({row[1] for row in rows}),
        "cities": all_cities,
        "cities_by_governorate": grouped,
    })


@egypt_healthcare_bp.route("/<int:facility_id>", methods=["GET"])
def get_facility(facility_id):
    facility = db.session.get(EgyptFacility, facility_id)
    if not facility:
        return jsonify({"message": "المنشأة غير موجودة"}), 404
    return jsonify({"facility": facility.to_dict()})
