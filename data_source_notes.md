# Data source notes

## HDX Egypt Health Facilities

Source page: https://data.humdata.org/dataset/hotosm_egy_health_facilities

The page identifies the dataset as “Egypt Health Facilities (OpenStreetMap Export)”, sourced from OpenStreetMap contributors. The export includes features matching healthcare tags or amenities such as doctors, dentists, clinics, hospitals, and pharmacies. Listed fields include name, name:en, amenity, building, healthcare, healthcare:speciality, operator:type, capacity:persons, addr:full, and address fields. The page exposes GeoJSON ZIP, SHP, KML, and Geopackage downloads for points and polygons. The page showed a 6 May 2026 modification date during verification.

This is a real public geospatial source for facilities, but it is not an official Egyptian licensing registry, does not guarantee complete coverage, does not inherently provide 1,200 unique records per facility category per governorate, and does not provide a verified directory of 1,200 individual doctors per governorate. It can be used as a sourced facility layer only after filtering, deduplication, governorate assignment, and explicit source attribution.

## HDX Egypt administrative boundaries

Source page: https://data.humdata.org/dataset/cod-ab-egy

The HDX page exposes Egypt administrative boundary downloads including `egy_admin_boundaries.geojson.zip` and `egy_admin_boundaries.shp.zip`, and states the dataset covers administrative levels including ADM1 governorates. This source can support spatial assignment of facility coordinates to Cairo, Alexandria, and Beheira, subject to checking the boundary names and coordinate reference system before import.
