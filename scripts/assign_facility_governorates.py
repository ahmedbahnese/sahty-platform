import json
from collections import Counter
from pathlib import Path

from shapely.geometry import Point, shape

facilities_path = Path('data/raw/egy_health_facilities_points/hotosm_egy_health_facilities_points_geojson.geojson')
boundaries_path = Path('data/raw/egy_boundaries/egy_admin1.geojson')
facilities = json.loads(facilities_path.read_text(encoding='utf-8'))['features']
boundaries = json.loads(boundaries_path.read_text(encoding='utf-8'))['features']

print('boundary_count=', len(boundaries))
for boundary in boundaries[:3]:
    print('boundary_properties=', boundary.get('properties'))

province_counts = Counter()
category_counts = Counter()
unmatched = 0
for feature in facilities:
    geometry = feature.get('geometry') or {}
    coords = geometry.get('coordinates')
    if geometry.get('type') != 'Point' or not coords:
        unmatched += 1
        continue
    point = Point(coords[0], coords[1])
    matched_name = None
    for boundary in boundaries:
        polygon = shape(boundary['geometry'])
        if polygon.contains(point) or polygon.touches(point):
            props = boundary.get('properties') or {}
            matched_name = props.get('adm1_name') or props.get('adm1_name1') or props.get('ADM1_EN') or props.get('NAME_1') or props.get('name') or props.get('admin1Name')
            break
    if not matched_name:
        unmatched += 1
        continue
    props = feature.get('properties') or {}
    province_counts[matched_name] += 1
    category = props.get('healthcare') or props.get('amenity') or 'unknown'
    category_counts[(matched_name, category)] += 1

print('unmatched=', unmatched)
print('province_counts:')
for key, count in province_counts.most_common():
    print(f'  {count}\t{key}')
print('selected_category_counts:')
for (province, category), count in sorted(category_counts.items()):
    if any(token in province.lower() for token in ('cairo', 'alex', 'behera', 'behira')):
        print(f'  {count}\t{province}\t{category}')
