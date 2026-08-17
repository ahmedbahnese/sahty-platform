import csv
import json
from pathlib import Path

from shapely.geometry import Point, shape

FACILITIES = Path('data/raw/egy_health_facilities_points/hotosm_egy_health_facilities_points_geojson.geojson')
BOUNDARIES = Path('data/raw/egy_boundaries/egy_admin1.geojson')
OUTPUT = Path('data/processed/egypt_directory_hdx_target.csv')
TARGETS = {'Cairo', 'Alexandria', 'Behera'}
SOURCE = 'HDX HOTOSM Egypt Health Facilities / OpenStreetMap contributors (modified 2026-05-06)'

TYPE_MAP = {
    'pharmacy': 'pharmacy',
    'hospital': 'hospital',
    'clinic': 'clinic',
    'doctor': 'doctor',
    'doctors': 'doctor',
    'dentist': 'dentist',
    'laboratory': 'laboratory',
    'centre': 'health_center',
    'center': 'health_center',
    'مركز_صحي': 'health_center',
    'radiology': 'radiology_center',
    'blood_bank': 'blood_bank',
}


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def resolve_province(point, boundaries):
    for boundary in boundaries:
        polygon = shape(boundary['geometry'])
        if polygon.contains(point) or polygon.touches(point):
            props = boundary.get('properties') or {}
            return props.get('adm1_name'), props.get('adm1_name1')
    return None, None


def normalize_type(props):
    for key in ('healthcare', 'amenity'):
        value = props.get(key)
        if value in TYPE_MAP:
            return TYPE_MAP[value]
    return 'healthcare_facility'


def main():
    facilities = load_json(FACILITIES)['features']
    boundaries = load_json(BOUNDARIES)['features']
    rows = []
    seen = set()
    for feature in facilities:
        geometry = feature.get('geometry') or {}
        coordinates = geometry.get('coordinates')
        if geometry.get('type') != 'Point' or not coordinates:
            continue
        lon, lat = coordinates[:2]
        province_en, province_ar = resolve_province(Point(lon, lat), boundaries)
        if province_en not in TARGETS:
            continue
        props = feature.get('properties') or {}
        name_ar = (props.get('name:ar') or props.get('name') or '').strip()
        name_en = (props.get('name:en') or props.get('name') or name_ar).strip()
        if not name_ar and not name_en:
            continue
        osm_id = str(props.get('osm_type', 'node')) + ':' + str(props.get('osm_id', ''))
        dedupe_key = osm_id if osm_id.endswith(':') is False else f'{name_en.lower()}|{round(float(lat), 6)}|{round(float(lon), 6)}'
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        rows.append({
            'external_id': osm_id,
            'name_ar': name_ar or name_en,
            'name_en': name_en or name_ar,
            'facility_type': normalize_type(props),
            'governorate': province_en,
            'governorate_ar': province_ar or province_en,
            'city': (props.get('addr:city') or '').strip(),
            'address': (props.get('addr:full') or '').strip(),
            'phone': '',
            'specialty': (props.get('healthcare:speciality') or '').strip(),
            'source': SOURCE,
            'latitude': lat,
            'longitude': lon,
            'working_hours': '',
            'home_services': '0',
            'emergency_24_7': '0',
        })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys()) if rows else []
    with OUTPUT.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: (row['governorate'], row['facility_type'], row['name_en'])))
    print(f'rows={len(rows)}')
    for province in sorted(TARGETS):
        print(province, sum(row['governorate'] == province for row in rows))


if __name__ == '__main__':
    main()
