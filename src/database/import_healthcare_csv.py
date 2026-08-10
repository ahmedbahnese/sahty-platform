"""Import the supplied Egypt healthcare CSV database into SQLite safely."""

import csv
import io
import os
import zipfile

from src.models.egypt_healthcare import HealthcareDirectoryRecord
from src.models.user import db


ZIP_NAME = "Egypt_Healthcare_Full_Database_6000_1786271157551.zip"
CSV_NAMES = {
    "Egypt_Hospitals.csv": "Hospital",
    "Egypt_Pharmacies.csv": "Pharmacy",
    "Egypt_Laboratories.csv": "Laboratory",
    "Egypt_Radiology_Centers.csv": "Radiology Center",
    "Egypt_Blood_Banks.csv": "Blood Bank",
}


def _zip_path():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    candidates = [
        os.path.join(root, "attached_assets", ZIP_NAME),
        os.path.join(root, ZIP_NAME),
    ]
    return next((path for path in candidates if os.path.exists(path)), None)


def import_directory_if_needed():
    path = _zip_path()
    if not path:
        return 0
    imported = 0
    with zipfile.ZipFile(path) as archive:
        for filename, expected_type in CSV_NAMES.items():
            # Import each facility type independently so adding a new CSV to
            # an already-seeded deployment remains safe and complete.
            if HealthcareDirectoryRecord.query.filter_by(
                facility_type=expected_type
            ).first():
                continue
            member = next((n for n in archive.namelist() if n.endswith("/" + filename)), None)
            if not member:
                continue
            stream = io.TextIOWrapper(archive.open(member), encoding="utf-8-sig", newline="")
            for row in csv.DictReader(stream):
                def value(key):
                    raw = (row.get(key) or "").strip()
                    return None if raw.lower() in {"nan", "none", ""} else raw
                db.session.add(HealthcareDirectoryRecord(
                    name_ar=value("Arabic Name") or value("English Name") or "منشأة صحية",
                    name_en=value("English Name") or value("Arabic Name") or "Healthcare facility",
                    facility_type=value("Facility Type") or expected_type,
                    governorate=value("Governorate") or "Unknown",
                    city=value("City") or "Unknown",
                    address=value("Full Address"),
                    phone=value("Phone Number"),
                    specialty=value("Specialty"),
                    source=value("Source"),
                ))
                imported += 1
                if imported % 500 == 0:
                    db.session.flush()
            stream.close()
    db.session.commit()
    return imported