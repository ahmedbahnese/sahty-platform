import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from main import app


def main():
    with app.test_client() as client:
        all_response = client.get('/api/facilities?per_page=1')
        cairo_response = client.get('/api/facilities?governorate=Cairo&per_page=100')
        pharmacy_response = client.get('/api/facilities?type=pharmacy&governorate=Cairo&per_page=100')
        for response in (all_response, cairo_response, pharmacy_response):
            assert response.status_code == 200, response.data
        all_payload = all_response.get_json()
        cairo_payload = cairo_response.get_json()
        pharmacy_payload = pharmacy_response.get_json()
        print('all_total=', all_payload['total'])
        print('cairo_total=', cairo_payload['total'])
        print('cairo_pharmacy_total=', pharmacy_payload['total'])
        assert all_payload['total'] == 589
        assert cairo_payload['total'] == 368
        assert pharmacy_payload['total'] == 124


if __name__ == '__main__':
    main()
