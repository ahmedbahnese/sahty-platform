"""Normalized models for the imported Egypt healthcare facilities directory."""

from datetime import date, datetime, time

from src.models.user import db


class EgyptGovernorate(db.Model):
    __tablename__ = "egypt_governorates"

    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(100), nullable=False, unique=True)
    name_en = db.Column(db.String(100), nullable=False, unique=True)


class EgyptCity(db.Model):
    __tablename__ = "egypt_cities"

    id = db.Column(db.Integer, primary_key=True)
    governorate_id = db.Column(
        db.Integer, db.ForeignKey("egypt_governorates.id"), nullable=False
    )
    name_ar = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)

    governorate = db.relationship("EgyptGovernorate", backref="cities")
    __table_args__ = (
        db.UniqueConstraint("governorate_id", "name_en", name="uq_egypt_city_name"),
    )


class EgyptFacilityType(db.Model):
    __tablename__ = "egypt_facility_types"

    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(100), nullable=False, unique=True)
    name_en = db.Column(db.String(100), nullable=False, unique=True)


class EgyptOwnershipType(db.Model):
    __tablename__ = "egypt_ownership_types"

    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(100), nullable=False, unique=True)
    name_en = db.Column(db.String(100), nullable=False, unique=True)


class EgyptFacility(db.Model):
    __tablename__ = "egypt_facilities"

    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(250), nullable=False)
    name_en = db.Column(db.String(250), nullable=False, unique=True)
    governorate_id = db.Column(
        db.Integer, db.ForeignKey("egypt_governorates.id"), nullable=False
    )
    city_id = db.Column(db.Integer, db.ForeignKey("egypt_cities.id"), nullable=False)
    facility_type_id = db.Column(
        db.Integer, db.ForeignKey("egypt_facility_types.id"), nullable=False
    )
    ownership_type_id = db.Column(
        db.Integer, db.ForeignKey("egypt_ownership_types.id"), nullable=False
    )
    district = db.Column(db.String(150))
    full_address = db.Column(db.Text)
    google_maps_url = db.Column(db.String(500))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    phone_numbers = db.Column(db.String(250))
    is_24_hours = db.Column(db.Boolean, nullable=False, default=False)
    has_emergency_dept = db.Column(db.Boolean, nullable=False, default=False)
    has_icu = db.Column(db.Boolean, nullable=False, default=False)
    data_source = db.Column(db.String(250))
    date_verified = db.Column(db.Date, default=date.today)

    governorate = db.relationship("EgyptGovernorate", backref="facilities")
    city = db.relationship("EgyptCity", backref="facilities")
    facility_type = db.relationship("EgyptFacilityType", backref="facilities")
    ownership_type = db.relationship("EgyptOwnershipType", backref="facilities")

    def to_dict(self):
        return {
            "id": self.id,
            "name_ar": self.name_ar,
            "name_en": self.name_en,
            "governorate": {
                "id": self.governorate.id,
                "name_ar": self.governorate.name_ar,
                "name_en": self.governorate.name_en,
            },
            "city": {
                "id": self.city.id,
                "name_ar": self.city.name_ar,
                "name_en": self.city.name_en,
            },
            "district": self.district,
            "full_address": self.full_address,
            "google_maps_url": self.google_maps_url,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "phone_numbers": self.phone_numbers,
            "is_24_hours": self.is_24_hours,
            "has_emergency_dept": self.has_emergency_dept,
            "has_icu": self.has_icu,
            "data_source": self.data_source,
            "date_verified": self.date_verified.isoformat() if self.date_verified else None,
            "facility_type": {
                "id": self.facility_type.id,
                "name_ar": self.facility_type.name_ar,
                "name_en": self.facility_type.name_en,
            },
            "ownership": {
                "id": self.ownership_type.id,
                "name_ar": self.ownership_type.name_ar,
                "name_en": self.ownership_type.name_en,
            },
        }


class HealthcareDirectoryRecord(db.Model):
    """Flat imported directory rows.

    The supplied database intentionally contains repeated provider names for
    different branches.  Keeping the import in its own table preserves every
    row without changing the older normalized directory used by the app.
    """

    __tablename__ = "healthcare_directory_records"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(120), index=True)
    name_ar = db.Column(db.String(250), nullable=False)
    name_en = db.Column(db.String(250), nullable=False)
    facility_type = db.Column(db.String(80), nullable=False, index=True)
    governorate = db.Column(db.String(100), nullable=False, index=True)
    city = db.Column(db.String(150), nullable=False, index=True)
    address = db.Column(db.Text)
    phone = db.Column(db.String(250))
    specialty = db.Column(db.Text)
    source = db.Column(db.String(250))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    working_hours = db.Column(db.String(250))
    home_services = db.Column(db.Boolean, nullable=False, default=False)
    emergency_24_7 = db.Column(db.Boolean, nullable=False, default=False)
    imported_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def _is_open_now(self, now=None):
        """Calculate opening status from stored hours; unknown stays unknown."""
        if not self.working_hours:
            return None
        raw = self.working_hours.strip().lower().replace(" ", "")
        if raw in {"24hours", "24/7", "24ساعة"}:
            return True
        if not now:
            now = datetime.now().time()
        try:
            start_raw, end_raw = raw.replace("–", "-").split("-", 1)
            def parse(value):
                suffix = None
                if value.endswith(("am", "pm")):
                    suffix, value = value[-2:], value[:-2]
                hour, minute = (value.split(":") + ["0"])[:2]
                hour, minute = int(hour), int(minute)
                if suffix == "pm" and hour < 12:
                    hour += 12
                if suffix == "am" and hour == 12:
                    hour = 0
                return time(hour, minute)
            start, end = parse(start_raw), parse(end_raw)
            return start <= now <= end if start <= end else now >= start or now <= end
        except (ValueError, TypeError):
            return None

    def to_dict(self, user_lat=None, user_lng=None):
        distance_km = None
        if user_lat is not None and user_lng is not None and self.latitude is not None and self.longitude is not None:
            from math import atan2, cos, radians, sin, sqrt
            radius = 6371.0
            d_lat = radians(self.latitude - user_lat)
            d_lng = radians(self.longitude - user_lng)
            a = sin(d_lat / 2) ** 2 + cos(radians(user_lat)) * cos(radians(self.latitude)) * sin(d_lng / 2) ** 2
            distance_km = round(radius * 2 * atan2(sqrt(a), sqrt(1 - a)), 1)
        return {
            "id": self.id,
            "external_id": self.external_id,
            "name_ar": self.name_ar,
            "name_en": self.name_en,
            "facility_type": self.facility_type,
            "governorate": self.governorate,
            "city": self.city,
            "full_address": self.address,
            "phone_numbers": self.phone,
            "specialty": self.specialty,
            "services": self.specialty,
            "data_source": self.source,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "working_hours": self.working_hours,
            "is_open": self._is_open_now(),
            "home_services": self.home_services,
            "has_emergency_dept": self.emergency_24_7,
            "is_24_hours": self.emergency_24_7,
            "distance_km": distance_km,
            "google_maps_url": f"https://www.google.com/maps/search/?api=1&query={self.latitude},{self.longitude}"
                if self.latitude is not None and self.longitude is not None
                else f"https://www.google.com/maps/search/?api=1&query={self.name_en} {self.address or ''}",
        }