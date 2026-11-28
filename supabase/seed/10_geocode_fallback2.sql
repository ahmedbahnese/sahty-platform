-- Sahty directory geocode fallback, part 2 — remaining districts (approx. 1-3 km).
-- Run AFTER 08_geocode_fallback.sql. Sets lat/lng ONLY where still NULL, so
-- the 22 exact facility coordinates from 07 and the 08 fallbacks are never
-- overwritten. Covers the 26 city/governorate combinations that were still
-- NULL after 08 (45 rows in healthcare_directory_records, 41 in
-- egypt_facilities), found by GROUP BY on 2026-11-28.
-- Two fixes vs 08: (1) New Cairo is matched with the EXACT string stored in
-- the flat table, 'القاهرة الجديدة – التجمع الخامس' (en dash U+2013) — 08 used
-- a slash and matched nothing; (2) egypt_facilities is matched by city
-- name_ar (Arabic) instead of name_en — 08's name_en 'Smouha' missed one
-- Smouha row whose city row carries a different name_en.
-- District centres come from OpenStreetMap Nominatim (place/suburb, railway
-- station, park, or street points inside the district) + known geography for
-- the 4 districts Nominatim returned nothing useful for (El Hadra, El Hadra
-- Bahariya, El Delengat, generic 'Cairo'/'Greater Cairo' = Downtown).
-- The Cairo-Ismailia desert-road row is the International Medical Center
-- itself (Nominatim amenity=hospital 30.19325, 31.65821), so its point is
-- the facility's own location. Distances for these facilities are therefore
-- approximate — good enough to rank 'nearest to me' by district, never
-- invented as exact.
-- Safe to re-run: UPDATEs only touch NULL coordinates.
BEGIN;

-- Abbassia (العباسية), Cairo: 30.071, 31.285 — Nominatim Abbassia metro station / Police Stadium
UPDATE public.healthcare_directory_records SET latitude = 30.071, longitude = 31.285 WHERE latitude IS NULL AND city = 'العباسية' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.071, longitude = 31.285 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'العباسية' AND g.name_ar = 'القاهرة');

-- New Cairo / 5th Settlement (القاهرة الجديدة – التجمع الخامس), Cairo: 30.02, 31.46 — same centroid as 08, exact en-dash string this time
UPDATE public.healthcare_directory_records SET latitude = 30.02, longitude = 31.46 WHERE latitude IS NULL AND city = 'القاهرة الجديدة – التجمع الخامس' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.02, longitude = 31.46 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'القاهرة الجديدة – التجمع الخامس' AND g.name_ar = 'القاهرة');

-- El Hadra (الحضرة), Alexandria: 31.20, 29.935 — known geography (south of Smouha / Moharram Bey)
UPDATE public.healthcare_directory_records SET latitude = 31.20, longitude = 29.935 WHERE latitude IS NULL AND city = 'الحضرة' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.20, longitude = 29.935 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'الحضرة' AND g.name_ar = 'الإسكندرية');

-- Zamalek (الزمالك), Cairo: 30.06299, 31.21963 — Nominatim place=suburb
UPDATE public.healthcare_directory_records SET latitude = 30.06299, longitude = 31.21963 WHERE latitude IS NULL AND city = 'الزمالك' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.06299, longitude = 31.21963 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'الزمالك' AND g.name_ar = 'القاهرة');

-- Kasr Al Ainy (القصر العيني), Cairo: 30.03, 31.23 — Nominatim hospital-area points
UPDATE public.healthcare_directory_records SET latitude = 30.03, longitude = 31.23 WHERE latitude IS NULL AND city = 'القصر العيني' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.03, longitude = 31.23 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'القصر العيني' AND g.name_ar = 'القاهرة');

-- Al-Manial (المنيل), Cairo: 30.025, 31.226 — Nominatim المنيل الغربي / الشرقي neighbourhoods
UPDATE public.healthcare_directory_records SET latitude = 30.025, longitude = 31.226 WHERE latitude IS NULL AND city = 'المنيل' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.025, longitude = 31.226 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'المنيل' AND g.name_ar = 'القاهرة');

-- Hanoville / Agami (الهانوفيل، العجمي), Alexandria: 31.105, 29.765 — Nominatim Hanoville street points
UPDATE public.healthcare_directory_records SET latitude = 31.105, longitude = 29.765 WHERE latitude IS NULL AND city = 'الهانوفيل، العجمي' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.105, longitude = 29.765 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'الهانوفيل، العجمي' AND g.name_ar = 'الإسكندرية');

-- Saba Pasha (سابا باشا), Alexandria: 31.239, 29.954 — Nominatim Saba Pasha points
UPDATE public.healthcare_directory_records SET latitude = 31.239, longitude = 29.954 WHERE latitude IS NULL AND city = 'سابا باشا' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.239, longitude = 29.954 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'سابا باشا' AND g.name_ar = 'الإسكندرية');

-- Sidi Gaber (سيدي جابر), Alexandria: 31.22384, 29.93724 — Nominatim administrative boundary
UPDATE public.healthcare_directory_records SET latitude = 31.22384, longitude = 29.93724 WHERE latitude IS NULL AND city = 'سيدي جابر' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.22384, longitude = 29.93724 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'سيدي جابر' AND g.name_ar = 'الإسكندرية');

-- Kom El Dikka (كوم الدكة), Alexandria: 31.19508, 29.90397 — Nominatim park
UPDATE public.healthcare_directory_records SET latitude = 31.19508, longitude = 29.90397 WHERE latitude IS NULL AND city = 'كوم الدكة' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.19508, longitude = 29.90397 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'كوم الدكة' AND g.name_ar = 'الإسكندرية');

-- Ibrahimia (الإبراهيمية), Alexandria: 31.2145, 29.9268 — Nominatim church / office / tram-stop points
UPDATE public.healthcare_directory_records SET latitude = 31.2145, longitude = 29.9268 WHERE latitude IS NULL AND city = 'الإبراهيمية' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.2145, longitude = 29.9268 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'الإبراهيمية' AND g.name_ar = 'الإسكندرية');

-- El Hadra Bahariya (الحضرة البحرية), Alexandria: 31.21, 29.93 — known geography (northern El Hadra)
UPDATE public.healthcare_directory_records SET latitude = 31.21, longitude = 29.93 WHERE latitude IS NULL AND city = 'الحضرة البحرية' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.21, longitude = 29.93 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'الحضرة البحرية' AND g.name_ar = 'الإسكندرية');

-- El Delengat (الدلنجات), Beheira: 30.82, 30.53 — known geography (no Nominatim result)
UPDATE public.healthcare_directory_records SET latitude = 30.82, longitude = 30.53 WHERE latitude IS NULL AND city = 'الدلنجات' AND governorate = 'البحيرة';
UPDATE public.egypt_facilities SET latitude = 30.82, longitude = 30.53 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'الدلنجات' AND g.name_ar = 'البحيرة');

-- Generic 'Cairo' (القاهرة), Cairo: 30.0444, 31.2357 — Downtown
UPDATE public.healthcare_directory_records SET latitude = 30.0444, longitude = 31.2357 WHERE latitude IS NULL AND city = 'القاهرة' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.0444, longitude = 31.2357 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'القاهرة' AND g.name_ar = 'القاهرة');

-- Greater Cairo (القاهرة الكبرى), Cairo: 30.0444, 31.2357 — Downtown
UPDATE public.healthcare_directory_records SET latitude = 30.0444, longitude = 31.2357 WHERE latitude IS NULL AND city = 'القاهرة الكبرى' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.0444, longitude = 31.2357 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'القاهرة الكبرى' AND g.name_ar = 'القاهرة');

-- New Maadi (المعادي الجديدة), Cairo: 29.978, 31.32 — Nominatim area points (Malvern College 29.9791, 31.3512 is the eastern edge)
UPDATE public.healthcare_directory_records SET latitude = 29.978, longitude = 31.32 WHERE latitude IS NULL AND city = 'المعادي الجديدة' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 29.978, longitude = 31.32 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'المعادي الجديدة' AND g.name_ar = 'القاهرة');

-- Bakos (باكوس), Alexandria: 31.23376, 29.96857 — Nominatim place=neighbourhood
UPDATE public.healthcare_directory_records SET latitude = 31.23376, longitude = 29.96857 WHERE latitude IS NULL AND city = 'باكوس' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.23376, longitude = 29.96857 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'باكوس' AND g.name_ar = 'الإسكندرية');

-- Dar El Salam (دار السلام), Cairo: 29.982, 31.242 — Nominatim Dar El Salam metro station
UPDATE public.healthcare_directory_records SET latitude = 29.982, longitude = 31.242 WHERE latitude IS NULL AND city = 'دار السلام' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 29.982, longitude = 31.242 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'دار السلام' AND g.name_ar = 'القاهرة');

-- Ras El Tin / Anfushi (رأس التين / الأنفوشي), Alexandria: 31.20251, 29.874 — Nominatim tram stop
UPDATE public.healthcare_directory_records SET latitude = 31.20251, longitude = 29.874 WHERE latitude IS NULL AND city = 'رأس التين / الأنفوشي' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.20251, longitude = 29.874 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'رأس التين / الأنفوشي' AND g.name_ar = 'الإسكندرية');

-- Rosetta (رشيد), Beheira: 31.40138, 30.41843 — Nominatim place=city
UPDATE public.healthcare_directory_records SET latitude = 31.40138, longitude = 30.41843 WHERE latitude IS NULL AND city = 'رشيد' AND governorate = 'البحيرة';
UPDATE public.egypt_facilities SET latitude = 31.40138, longitude = 30.41843 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'رشيد' AND g.name_ar = 'البحيرة');

-- Ramses (رمسيس), Cairo: 30.0618, 31.246 — Nominatim El Shohadaa metro station (Ramses Square)
UPDATE public.healthcare_directory_records SET latitude = 30.0618, longitude = 31.246 WHERE latitude IS NULL AND city = 'رمسيس' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.0618, longitude = 31.246 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'رمسيس' AND g.name_ar = 'القاهرة');

-- Sidi Bishr Bahari (سيدي بشر بحري), Alexandria: 31.253, 29.977 — Nominatim Sidi Bishr tram stop, seaside side
UPDATE public.healthcare_directory_records SET latitude = 31.253, longitude = 29.977 WHERE latitude IS NULL AND city = 'سيدي بشر بحري' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.253, longitude = 29.977 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'سيدي بشر بحري' AND g.name_ar = 'الإسكندرية');

-- Shubra (شبرا), Cairo: 30.08, 31.245 — Nominatim subway-line points through Shubra
UPDATE public.healthcare_directory_records SET latitude = 30.08, longitude = 31.245 WHERE latitude IS NULL AND city = 'شبرا' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.08, longitude = 31.245 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'شبرا' AND g.name_ar = 'القاهرة');

-- Cairo–Ismailia Desert Road (طريق القاهرة – الإسماعيلية الصحراوي), Cairo: 30.19325, 31.65821 — Nominatim International Medical Center hospital itself
UPDATE public.healthcare_directory_records SET latitude = 30.19325, longitude = 31.65821 WHERE latitude IS NULL AND city = 'طريق القاهرة – الإسماعيلية الصحراوي' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.19325, longitude = 31.65821 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'طريق القاهرة – الإسماعيلية الصحراوي' AND g.name_ar = 'القاهرة');

-- Abdeen (عابدين), Cairo: 30.043, 31.246 — Nominatim Abdeen Garden / Palace
UPDATE public.healthcare_directory_records SET latitude = 30.043, longitude = 31.246 WHERE latitude IS NULL AND city = 'عابدين' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.043, longitude = 31.246 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'عابدين' AND g.name_ar = 'القاهرة');

-- Ain Shams / Alf Maskan (عين شمس / ألف مسكن), Cairo: 30.13048, 31.31675 — Nominatim place=suburb
UPDATE public.healthcare_directory_records SET latitude = 30.13048, longitude = 31.31675 WHERE latitude IS NULL AND city = 'عين شمس / ألف مسكن' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.13048, longitude = 31.31675 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'عين شمس / ألف مسكن' AND g.name_ar = 'القاهرة');

-- Smouha (سموحة), Alexandria: 31.21542, 29.94477 — same centroid as 08, matched by name_ar this time (one egypt_facilities row was missed by 08's name_en match)
UPDATE public.healthcare_directory_records SET latitude = 31.21542, longitude = 29.94477 WHERE latitude IS NULL AND city = 'سموحة' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.21542, longitude = 29.94477 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_ar = 'سموحة' AND g.name_ar = 'الإسكندرية');

COMMIT;
