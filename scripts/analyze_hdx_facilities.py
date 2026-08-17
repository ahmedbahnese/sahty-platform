import json
from collections import Counter
from pathlib import Path

path = Path('data/raw/egy_health_facilities_points/hotosm_egy_health_facilities_points_geojson.geojson')
data = json.loads(path.read_text(encoding='utf-8'))
features = data.get('features', [])
print(f'total_features={len(features)}')

keys = Counter()
amenity = Counter()
healthcare = Counter()
operator_type = Counter()
city = Counter()
source = Counter()
for feature in features:
    props = feature.get('properties') or {}
    keys.update(props.keys())
    for field, counter in [('amenity', amenity), ('healthcare', healthcare), ('operator:type', operator_type)]:
        value = props.get(field)
        if value not in (None, ''):
            counter[str(value)] += 1
    for field, counter in [('addr:city', city), ('source', source)]:
        value = props.get(field)
        if value not in (None, ''):
            counter[str(value)] += 1

print('property_keys=' + ','.join(sorted(keys)))
for label, counter in [('amenity', amenity), ('healthcare', healthcare), ('operator_type', operator_type), ('addr_city', city), ('source', source)]:
    print(f'{label}:')
    for value, count in counter.most_common():
        print(f'  {count}\t{value}')

coords = 0
named = 0
for feature in features:
    props = feature.get('properties') or {}
    geometry = feature.get('geometry') or {}
    if props.get('name') or props.get('name:en'):
        named += 1
    if geometry.get('coordinates'):
        coords += 1
print(f'named_features={named}')
print(f'features_with_coordinates={coords}')
