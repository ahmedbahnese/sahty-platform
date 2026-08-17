# Data source notes

## HDX Egypt Health Facilities

Source page: https://data.humdata.org/dataset/hotosm_egy_health_facilities

The page identifies the dataset as “Egypt Health Facilities (OpenStreetMap Export)”, sourced from OpenStreetMap contributors. The export includes features matching healthcare tags or amenities such as doctors, dentists, clinics, hospitals, and pharmacies. Listed fields include name, name:en, amenity, building, healthcare, healthcare:speciality, operator:type, capacity:persons, addr:full, and address fields. The page exposes GeoJSON ZIP, SHP, KML, and Geopackage downloads for points and polygons. The page showed a 6 May 2026 modification date during verification.

This is a real public geospatial source for facilities, but it is not an official Egyptian licensing registry, does not guarantee complete coverage, does not inherently provide 1,200 unique records per facility category per governorate, and does not provide a verified directory of 1,200 individual doctors per governorate. It can be used as a sourced facility layer only after filtering, deduplication, governorate assignment, and explicit source attribution.

## HDX Egypt administrative boundaries

Source page: https://data.humdata.org/dataset/cod-ab-egy

The HDX page exposes Egypt administrative boundary downloads including `egy_admin_boundaries.geojson.zip` and `egy_admin_boundaries.shp.zip`, and states the dataset covers administrative levels including ADM1 governorates. This source can support spatial assignment of facility coordinates to Cairo, Alexandria, and Beheira, subject to checking the boundary names and coordinate reference system before import.

## Verified extract result

Using the downloaded HDX point GeoJSON and HDX ADM1 boundaries, spatial matching assigned 589 named, unique source records to the target governorates: Cairo 368, Alexandria 203, Beheira 18. The raw Egypt points dataset contained 1,576 features total, 1,219 named features, and 18 spatially unmatched points.

The processed CSV currently contains these normalized facility types: pharmacy 263, hospital 141, clinic 87, doctor 51, health_center 10, laboratory 9, healthcare_facility 5, and dentist 23. All 589 rows have unique source external IDs in the prepared extract. This is a verified public facility extract, not a complete official licensing registry and not evidence that 1,200 records exist for each category.

## Official-source integration findings

The official Egypt Healthcare Authority page states that EHA is a public healthcare services provider established under Law No. 2 of 2018 and describes a tiered network of family medicine units, centers, hospitals, diagnostic and laboratory services, with accreditation and registration processes. URL: https://eha.gov.eg/en/about-eha/

The official Ministry of Health and Population website is active and publishes health-sector announcements and institutional information, but the public page reviewed did not expose a downloadable nationwide directory for physicians and all facility categories. URL: https://www.mohp.gov.eg/

These institutions should be approached for an official data-sharing or API/export request rather than scraped aggressively. Public pages may be used for source verification, while licensed registries should be imported only under explicit permission and with field-level privacy minimization.
