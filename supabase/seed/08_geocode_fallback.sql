-- Sahty directory geocode fallback — district centroids (approx. 1-3 km).
-- Run AFTER 07_geocode.sql. Sets lat/lng ONLY where still NULL, so the 22
-- exact facility coordinates from 07 are never overwritten. District centres
-- come from OpenStreetMap Nominatim (19 districts) + known geography for the
-- 8 districts Nominatim returned a wrong feature for (Damanhour, Downtown,
-- Edku, Heliopolis, Itay El-Barud, Sporting, New Cairo, Roushdy).
-- Distances shown for these facilities are therefore approximate — good
-- enough to rank 'nearest to me' by district, never invented as exact.
-- Safe to re-run: UPDATEs only touch NULL coordinates.
BEGIN;

-- Asafra, Alexandria: 31.27646, 30.00297
UPDATE public.healthcare_directory_records SET latitude = 31.27646, longitude = 30.00297 WHERE latitude IS NULL AND city = 'العصافرة' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.27646, longitude = 30.00297 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'Asafra' AND g.name_en = 'Alexandria');

-- Azarita, Alexandria: 31.20755, 29.91428
UPDATE public.healthcare_directory_records SET latitude = 31.20755, longitude = 29.91428 WHERE latitude IS NULL AND city = 'الأزاريطة' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.20755, longitude = 29.91428 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'Azarita' AND g.name_en = 'Alexandria');

-- Damanhour, Beheira: 30.47, 30.47
UPDATE public.healthcare_directory_records SET latitude = 30.47, longitude = 30.47 WHERE latitude IS NULL AND city = 'دمنهور' AND governorate = 'البحيرة';
UPDATE public.egypt_facilities SET latitude = 30.47, longitude = 30.47 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'Damanhour' AND g.name_en = 'Beheira');

-- Downtown, Cairo: 30.0444, 31.2357
UPDATE public.healthcare_directory_records SET latitude = 30.0444, longitude = 31.2357 WHERE latitude IS NULL AND city = 'وسط البلد' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.0444, longitude = 31.2357 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'Downtown' AND g.name_en = 'Cairo');

-- Edku, Beheira: 31.31, 30.3
UPDATE public.healthcare_directory_records SET latitude = 31.31, longitude = 30.3 WHERE latitude IS NULL AND city = 'إدكو' AND governorate = 'البحيرة';
UPDATE public.egypt_facilities SET latitude = 31.31, longitude = 30.3 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'Edku' AND g.name_en = 'Beheira');

-- Heliopolis, Cairo: 30.09, 31.31
UPDATE public.healthcare_directory_records SET latitude = 30.09, longitude = 31.31 WHERE latitude IS NULL AND city = 'مصر الجديدة' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.09, longitude = 31.31 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'Heliopolis' AND g.name_en = 'Cairo');

-- Itay El-Barud, Beheira: 30.89, 30.48
UPDATE public.healthcare_directory_records SET latitude = 30.89, longitude = 30.48 WHERE latitude IS NULL AND city = 'إيتاي البارود' AND governorate = 'البحيرة';
UPDATE public.egypt_facilities SET latitude = 30.89, longitude = 30.48 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'Itay El-Barud' AND g.name_en = 'Beheira');

-- Kafr El-Dawar, Beheira: 31.13391, 30.12919
UPDATE public.healthcare_directory_records SET latitude = 31.13391, longitude = 30.12919 WHERE latitude IS NULL AND city = 'كفر الدوار' AND governorate = 'البحيرة';
UPDATE public.egypt_facilities SET latitude = 31.13391, longitude = 30.12919 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'Kafr El-Dawar' AND g.name_en = 'Beheira');

-- Kom Hamada, Beheira: 30.75891, 30.70035
UPDATE public.healthcare_directory_records SET latitude = 30.75891, longitude = 30.70035 WHERE latitude IS NULL AND city = 'كوم حمادة' AND governorate = 'البحيرة';
UPDATE public.egypt_facilities SET latitude = 30.75891, longitude = 30.70035 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'Kom Hamada' AND g.name_en = 'Beheira');

-- Maadi, Cairo: 29.95971, 31.25808
UPDATE public.healthcare_directory_records SET latitude = 29.95971, longitude = 31.25808 WHERE latitude IS NULL AND city = 'المعادي' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 29.95971, longitude = 31.25808 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'Maadi' AND g.name_en = 'Cairo');

-- Miami, Alexandria: 31.26583, 29.9943
UPDATE public.healthcare_directory_records SET latitude = 31.26583, longitude = 29.9943 WHERE latitude IS NULL AND city = 'ميامي' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.26583, longitude = 29.9943 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'Miami' AND g.name_en = 'Alexandria');

-- Moharram Bey, Alexandria: 31.18609, 29.92615
UPDATE public.healthcare_directory_records SET latitude = 31.18609, longitude = 29.92615 WHERE latitude IS NULL AND city = 'محرم بك' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.18609, longitude = 29.92615 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'Moharram Bey' AND g.name_en = 'Alexandria');

-- Mostafa Kamel, Alexandria: 31.22573, 29.9408
UPDATE public.healthcare_directory_records SET latitude = 31.22573, longitude = 29.9408 WHERE latitude IS NULL AND city = 'مصطفى كامل' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.22573, longitude = 29.9408 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'Mostafa Kamel' AND g.name_en = 'Alexandria');

-- Nasr City, Cairo: 30.05212, 31.3422
UPDATE public.healthcare_directory_records SET latitude = 30.05212, longitude = 31.3422 WHERE latitude IS NULL AND city = 'مدينة نصر' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.05212, longitude = 31.3422 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'Nasr City' AND g.name_en = 'Cairo');

-- New Cairo / 5th Settlement, Cairo: 30.02, 31.46
UPDATE public.healthcare_directory_records SET latitude = 30.02, longitude = 31.46 WHERE latitude IS NULL AND city = 'القاهرة الجديدة / التجمع الخامس' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.02, longitude = 31.46 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'New Cairo / 5th Settlement' AND g.name_en = 'Cairo');

-- Raml Station, Alexandria: 31.20141, 29.90112
UPDATE public.healthcare_directory_records SET latitude = 31.20141, longitude = 29.90112 WHERE latitude IS NULL AND city = 'محطة الرمل' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.20141, longitude = 29.90112 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'Raml Station' AND g.name_en = 'Alexandria');

-- Roushdy, Alexandria: 31.22, 29.94
UPDATE public.healthcare_directory_records SET latitude = 31.22, longitude = 29.94 WHERE latitude IS NULL AND city = 'رشدي' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.22, longitude = 29.94 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'Roushdy' AND g.name_en = 'Alexandria');

-- Sayeda Zeinab, Cairo: 30.03244, 31.24162
UPDATE public.healthcare_directory_records SET latitude = 30.03244, longitude = 31.24162 WHERE latitude IS NULL AND city = 'السيدة زينب' AND governorate = 'القاهرة';
UPDATE public.egypt_facilities SET latitude = 30.03244, longitude = 31.24162 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'Sayeda Zeinab' AND g.name_en = 'Cairo');

-- Shatby, Alexandria: 31.2, 29.91667
UPDATE public.healthcare_directory_records SET latitude = 31.2, longitude = 29.91667 WHERE latitude IS NULL AND city = 'الشاطبي' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.2, longitude = 29.91667 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'Shatby' AND g.name_en = 'Alexandria');

-- Smouha, Alexandria: 31.21542, 29.94477
UPDATE public.healthcare_directory_records SET latitude = 31.21542, longitude = 29.94477 WHERE latitude IS NULL AND city = 'سموحة' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.21542, longitude = 29.94477 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'Smouha' AND g.name_en = 'Alexandria');

-- Sporting, Alexandria: 31.22, 29.94
UPDATE public.healthcare_directory_records SET latitude = 31.22, longitude = 29.94 WHERE latitude IS NULL AND city = 'سبورتنج' AND governorate = 'الإسكندرية';
UPDATE public.egypt_facilities SET latitude = 31.22, longitude = 29.94 WHERE latitude IS NULL AND city_id IN (SELECT c.id FROM public.egypt_cities c JOIN public.egypt_governorates g ON g.id = c.governorate_id WHERE c.name_en = 'Sporting' AND g.name_en = 'Alexandria');

COMMIT;