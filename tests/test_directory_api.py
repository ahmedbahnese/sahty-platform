"""Regression tests for the database-backed healthcare directory."""

from src.models.egypt_healthcare import HealthcareDirectoryRecord
from src.models.user import db


def test_directory_filters_laboratories_and_home_services(client):
    db.session.add_all([
        HealthcareDirectoryRecord(
            name_ar='معمل منزلي',
            name_en='Home Lab',
            facility_type='Laboratory',
            governorate='القاهرة',
            city='مدينة نصر',
            address='شارع مثال',
            phone='01000000000',
            specialty='تحاليل دم',
            home_services=True,
            working_hours='24/7',
        ),
        HealthcareDirectoryRecord(
            name_ar='معمل عادي',
            name_en='Regular Lab',
            facility_type='Laboratory',
            governorate='القاهرة',
            city='المعادي',
            address='شارع آخر',
            specialty='تحاليل دم',
            home_services=False,
            working_hours='08:00-16:00',
        ),
    ])
    db.session.commit()

    response = client.get('/api/facilities?type=Laboratory&home_services=1')

    assert response.status_code == 200
    facilities = response.get_json()['facilities']
    assert [facility['name_ar'] for facility in facilities] == ['معمل منزلي']
