-- Sahty directory geocode — facility coordinates from OpenStreetMap Nominatim.
-- Researched 2026-11-28. Only facilities whose Nominatim result was verified as the
-- actual facility (name/address match) are included. 22 of 155 facilities geocoded;
-- the rest had no reliable Nominatim match and are left NULL (never invented).
-- Safe to re-run: UPDATEs are idempotent.
BEGIN;

UPDATE public.healthcare_directory_records SET latitude = 29.98507, longitude = 31.23094 WHERE name_en = 'As-Salam International Hospital' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 29.98507, longitude = 31.23094 WHERE name_en = 'As-Salam International Hospital';

UPDATE public.healthcare_directory_records SET latitude = 30.09316, longitude = 31.32974 WHERE name_en = 'Cleopatra Hospital' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.09316, longitude = 31.32974 WHERE name_en = 'Cleopatra Hospital';

UPDATE public.healthcare_directory_records SET latitude = 29.9827, longitude = 31.23116 WHERE name_en = 'Nile Badrawi Hospital' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 29.9827, longitude = 31.23116 WHERE name_en = 'Nile Badrawi Hospital';

UPDATE public.healthcare_directory_records SET latitude = 30.09451, longitude = 31.31762 WHERE name_en = 'Cairo Specialized Hospital' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.09451, longitude = 31.31762 WHERE name_en = 'Cairo Specialized Hospital';

UPDATE public.healthcare_directory_records SET latitude = 30.02972, longitude = 31.23206 WHERE name_en = 'Kasr Al Ainy Hospital (Cairo University Hospitals)' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.02972, longitude = 31.23206 WHERE name_en = 'Kasr Al Ainy Hospital (Cairo University Hospitals)';

UPDATE public.healthcare_directory_records SET latitude = 30.0967, longitude = 31.24003 WHERE name_en = 'Nasser Institute Hospital' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.0967, longitude = 31.24003 WHERE name_en = 'Nasser Institute Hospital';

UPDATE public.healthcare_directory_records SET latitude = 30.02318, longitude = 31.23783 WHERE name_en = 'Children''s Cancer Hospital 57357' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.02318, longitude = 31.23783 WHERE name_en = 'Children''s Cancer Hospital 57357';

UPDATE public.healthcare_directory_records SET latitude = 30.13304, longitude = 31.38412 WHERE name_en = 'Saudi German Hospital Cairo' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.13304, longitude = 31.38412 WHERE name_en = 'Saudi German Hospital Cairo';

UPDATE public.healthcare_directory_records SET latitude = 30.06328, longitude = 31.2526 WHERE name_en = 'Coptic Hospital' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.06328, longitude = 31.2526 WHERE name_en = 'Coptic Hospital';

UPDATE public.healthcare_directory_records SET latitude = 30.01625, longitude = 31.43389 WHERE name_en = 'Air Force Specialized Hospital' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.01625, longitude = 31.43389 WHERE name_en = 'Air Force Specialized Hospital';

UPDATE public.healthcare_directory_records SET latitude = 30.04613, longitude = 31.22178 WHERE name_en = 'Anglo-American Hospital' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.04613, longitude = 31.22178 WHERE name_en = 'Anglo-American Hospital';

UPDATE public.healthcare_directory_records SET latitude = 30.06579, longitude = 31.31963 WHERE name_en = 'Dar Al Fouad Hospital – Nasr City' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.06579, longitude = 31.31963 WHERE name_en = 'Dar Al Fouad Hospital – Nasr City';

UPDATE public.healthcare_directory_records SET latitude = 30.11703, longitude = 31.35332 WHERE name_en = 'El Ezaby Pharmacy – Hegaz' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.11703, longitude = 31.35332 WHERE name_en = 'El Ezaby Pharmacy – Hegaz';

UPDATE public.healthcare_directory_records SET latitude = 30.06814, longitude = 31.22189 WHERE name_en = 'Seif Pharmacy – Zamalek' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.06814, longitude = 31.22189 WHERE name_en = 'Seif Pharmacy – Zamalek';

UPDATE public.healthcare_directory_records SET latitude = 30.08407, longitude = 31.32792 WHERE name_en = 'Seif Pharmacy – El Merghany' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.08407, longitude = 31.32792 WHERE name_en = 'Seif Pharmacy – El Merghany';

UPDATE public.healthcare_directory_records SET latitude = 30.04929, longitude = 31.37835 WHERE name_en = 'Alfa Lab – Nasr City' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.04929, longitude = 31.37835 WHERE name_en = 'Alfa Lab – Nasr City';

UPDATE public.healthcare_directory_records SET latitude = 30.06502, longitude = 31.22166 WHERE name_en = 'Al Borg Laboratories – Zamalek' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.06502, longitude = 31.22166 WHERE name_en = 'Al Borg Laboratories – Zamalek';

UPDATE public.healthcare_directory_records SET latitude = 30.11711, longitude = 31.34141 WHERE name_en = 'Cairo Scan – Heliopolis' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.11711, longitude = 31.34141 WHERE name_en = 'Cairo Scan – Heliopolis';

UPDATE public.healthcare_directory_records SET latitude = 29.96005, longitude = 31.26 WHERE name_en = 'Nile Scan & Labs – Maadi' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 29.96005, longitude = 31.26 WHERE name_en = 'Nile Scan & Labs – Maadi';

UPDATE public.healthcare_directory_records SET latitude = 30.08698, longitude = 31.30251 WHERE name_en = 'Misr Radiology Center (MRC) – Heliopolis' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.08698, longitude = 31.30251 WHERE name_en = 'Misr Radiology Center (MRC) – Heliopolis';

UPDATE public.healthcare_directory_records SET latitude = 30.09478, longitude = 31.3319 WHERE name_en = 'Techno Scan – Heliopolis' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.09478, longitude = 31.3319 WHERE name_en = 'Techno Scan – Heliopolis';

UPDATE public.healthcare_directory_records SET latitude = 30.10239, longitude = 31.32308 WHERE name_en = 'Watani Radiology Center – Heliopolis' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.10239, longitude = 31.32308 WHERE name_en = 'Watani Radiology Center – Heliopolis';

COMMIT;