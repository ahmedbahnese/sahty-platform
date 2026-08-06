"""Normalized models for the imported Egypt healthcare facilities directory."""

from datetime import date

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