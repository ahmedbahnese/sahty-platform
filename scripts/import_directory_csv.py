import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from main import app, db
from src.models.egypt_healthcare import HealthcareDirectoryRecord


def as_float(value):
    return float(value) if value not in (None, '') else None


def as_bool(value):
    return str(value).lower() in {'1', 'true', 'yes'}


def run(path):
    created = 0
    updated = 0
    with app.app_context(), Path(path).open(encoding='utf-8-sig', newline='') as handle:
        for row in csv.DictReader(handle):
            external_id = (row.get('external_id') or '').strip() or None
            existing = None
            if external_id:
                existing = HealthcareDirectoryRecord.query.filter_by(external_id=external_id).first()
            if existing is None:
                existing = HealthcareDirectoryRecord.query.filter_by(
                    name_en=row['name_en'],
                    governorate=row['governorate'],
                    latitude=as_float(row.get('latitude')),
                    longitude=as_float(row.get('longitude')),
                ).first()
            if existing is None:
                existing = HealthcareDirectoryRecord()
                db.session.add(existing)
                created += 1
            else:
                updated += 1
            existing.external_id = external_id
            existing.name_ar = row['name_ar']
            existing.name_en = row['name_en']
            existing.facility_type = row['facility_type']
            existing.governorate = row['governorate']
            existing.city = row.get('city') or row['governorate']
            existing.address = row.get('address') or None
            existing.phone = row.get('phone') or None
            existing.specialty = row.get('specialty') or None
            existing.source = row.get('source') or None
            existing.latitude = as_float(row.get('latitude'))
            existing.longitude = as_float(row.get('longitude'))
            existing.working_hours = row.get('working_hours') or None
            existing.home_services = as_bool(row.get('home_services'))
            existing.emergency_24_7 = as_bool(row.get('emergency_24_7'))
            existing.imported_at = datetime.utcnow()
        db.session.commit()
    print(f'created={created}')
    print(f'updated={updated}')
    print(f'total_rows={created + updated}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_path')
    args = parser.parse_args()
    run(args.csv_path)
