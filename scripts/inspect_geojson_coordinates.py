import json
from pathlib import Path

facility = json.loads(Path('data/raw/egy_health_facilities_points/hotosm_egy_health_facilities_points_geojson.geojson').read_text())
boundary = json.loads(Path('data/raw/egy_boundaries/egy_admin1.geojson').read_text())
print('facility_first=', facility['features'][0].get('geometry'), facility['features'][0].get('properties'))
print('boundary_first_geometry_type=', boundary['features'][0].get('geometry', {}).get('type'))
print('boundary_first_bbox=', boundary['features'][0].get('bbox'))
print('facility_crs=', facility.get('crs'))
print('boundary_crs=', boundary.get('crs'))
