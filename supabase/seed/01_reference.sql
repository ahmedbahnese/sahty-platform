-- Sahty directory seed — reference data + ai_daily_usage table (migration 0007).
-- Run first, then 02_cairo.sql, 03_alexandria.sql, 04_beheira.sql.
-- Safe to re-run: all inserts are guarded (ON CONFLICT / NOT EXISTS).
BEGIN;

CREATE TABLE IF NOT EXISTS public.ai_daily_usage (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES public.users(id),
  guest_key VARCHAR(120),
  usage_date DATE NOT NULL,
  chat_count INTEGER NOT NULL DEFAULT 0,
  image_count INTEGER NOT NULL DEFAULT 0,
  symptom_count INTEGER NOT NULL DEFAULT 0,
  CONSTRAINT uq_ai_usage_user_date UNIQUE (user_id, usage_date),
  CONSTRAINT uq_ai_usage_guest_date UNIQUE (guest_key, usage_date)
);

INSERT INTO public.egypt_governorates (name_ar, name_en) VALUES ('القاهرة', 'Cairo') ON CONFLICT (name_en) DO NOTHING;
INSERT INTO public.egypt_governorates (name_ar, name_en) VALUES ('الإسكندرية', 'Alexandria') ON CONFLICT (name_en) DO NOTHING;
INSERT INTO public.egypt_governorates (name_ar, name_en) VALUES ('البحيرة', 'Beheira') ON CONFLICT (name_en) DO NOTHING;

INSERT INTO public.egypt_facility_types (name_ar, name_en) VALUES ('مستشفى', 'Hospital') ON CONFLICT (name_en) DO NOTHING;
INSERT INTO public.egypt_facility_types (name_ar, name_en) VALUES ('صيدلية', 'Pharmacy') ON CONFLICT (name_en) DO NOTHING;
INSERT INTO public.egypt_facility_types (name_ar, name_en) VALUES ('معمل تحاليل', 'Laboratory') ON CONFLICT (name_en) DO NOTHING;
INSERT INTO public.egypt_facility_types (name_ar, name_en) VALUES ('مركز أشعة', 'Radiology Center') ON CONFLICT (name_en) DO NOTHING;
INSERT INTO public.egypt_facility_types (name_ar, name_en) VALUES ('بنك دم', 'Blood Bank') ON CONFLICT (name_en) DO NOTHING;
INSERT INTO public.egypt_facility_types (name_ar, name_en) VALUES ('مركز إسعاف', 'Ambulance Center') ON CONFLICT (name_en) DO NOTHING;

INSERT INTO public.egypt_ownership_types (name_ar, name_en) VALUES ('حكومي', 'Government') ON CONFLICT (name_en) DO NOTHING;
INSERT INTO public.egypt_ownership_types (name_ar, name_en) VALUES ('جامعي', 'University') ON CONFLICT (name_en) DO NOTHING;
INSERT INTO public.egypt_ownership_types (name_ar, name_en) VALUES ('خاص', 'Private') ON CONFLICT (name_en) DO NOTHING;
INSERT INTO public.egypt_ownership_types (name_ar, name_en) VALUES ('عسكري', 'Military') ON CONFLICT (name_en) DO NOTHING;
INSERT INTO public.egypt_ownership_types (name_ar, name_en) VALUES ('خيري / غير ربحي', 'Non-profit') ON CONFLICT (name_en) DO NOTHING;

INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'الأزاريطة', 'Azarita' FROM public.egypt_governorates g WHERE g.name_en = 'Alexandria' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Azarita');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'الإبراهيمية', 'El Ibrahimeya' FROM public.egypt_governorates g WHERE g.name_en = 'Alexandria' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'El Ibrahimeya');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'الحضرة', 'El Hadra' FROM public.egypt_governorates g WHERE g.name_en = 'Alexandria' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'El Hadra');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'الحضرة البحرية', 'El Hadara Bahary' FROM public.egypt_governorates g WHERE g.name_en = 'Alexandria' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'El Hadara Bahary');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'الهانوفيل، العجمي', 'Hanovil, Agami' FROM public.egypt_governorates g WHERE g.name_en = 'Alexandria' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Hanovil, Agami');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'باكوس', 'Bacchus' FROM public.egypt_governorates g WHERE g.name_en = 'Alexandria' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Bacchus');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'رأس التين / الأنفوشي', 'Ras El Tin / Anfushi' FROM public.egypt_governorates g WHERE g.name_en = 'Alexandria' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Ras El Tin / Anfushi');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'رشدي', 'Roushdy' FROM public.egypt_governorates g WHERE g.name_en = 'Alexandria' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Roushdy');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'زيزينيا', 'Zizinia' FROM public.egypt_governorates g WHERE g.name_en = 'Alexandria' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Zizinia');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'سابا باشا', 'Saba Pacha' FROM public.egypt_governorates g WHERE g.name_en = 'Alexandria' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Saba Pacha');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'سابا باشا', 'Saba Pasha' FROM public.egypt_governorates g WHERE g.name_en = 'Alexandria' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Saba Pasha');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'سان ستيفانو', 'San Stefano' FROM public.egypt_governorates g WHERE g.name_en = 'Alexandria' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'San Stefano');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'سموحة', 'Semouha' FROM public.egypt_governorates g WHERE g.name_en = 'Alexandria' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Semouha');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'سموحة', 'Smouha' FROM public.egypt_governorates g WHERE g.name_en = 'Alexandria' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Smouha');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'سيدي بشر بحري', 'Sidi Beshr Bahary' FROM public.egypt_governorates g WHERE g.name_en = 'Alexandria' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Sidi Beshr Bahary');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'سيدي جابر', 'Sidi Gaber' FROM public.egypt_governorates g WHERE g.name_en = 'Alexandria' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Sidi Gaber');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'كوم الدكة', 'Kom el-Dekka' FROM public.egypt_governorates g WHERE g.name_en = 'Alexandria' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Kom el-Dekka');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'محطة الرمل', 'Raml Station' FROM public.egypt_governorates g WHERE g.name_en = 'Alexandria' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Raml Station');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'إيتاي البارود', 'Itay El-Barud' FROM public.egypt_governorates g WHERE g.name_en = 'Beheira' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Itay El-Barud');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'الدلنجات', 'El Delengat' FROM public.egypt_governorates g WHERE g.name_en = 'Beheira' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'El Delengat');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'دمنهور', 'Damanhour' FROM public.egypt_governorates g WHERE g.name_en = 'Beheira' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Damanhour');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'رشيد', 'Rashid' FROM public.egypt_governorates g WHERE g.name_en = 'Beheira' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Rashid');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'كفر الدوار', 'Kafr El-Dawar' FROM public.egypt_governorates g WHERE g.name_en = 'Beheira' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Kafr El-Dawar');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'كوم حمادة', 'Kom Hamada' FROM public.egypt_governorates g WHERE g.name_en = 'Beheira' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Kom Hamada');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'الزمالك', 'Zamalek' FROM public.egypt_governorates g WHERE g.name_en = 'Cairo' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Zamalek');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'السيدة زينب', 'Sayeda Zeinab' FROM public.egypt_governorates g WHERE g.name_en = 'Cairo' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Sayeda Zeinab');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'العباسية', 'Abbassia' FROM public.egypt_governorates g WHERE g.name_en = 'Cairo' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Abbassia');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'القاهرة', 'Cairo' FROM public.egypt_governorates g WHERE g.name_en = 'Cairo' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Cairo');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'القاهرة الجديدة – التجمع الخامس', 'New Cairo / 5th Settlement' FROM public.egypt_governorates g WHERE g.name_en = 'Cairo' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'New Cairo / 5th Settlement');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'القاهرة الكبرى', 'Greater Cairo' FROM public.egypt_governorates g WHERE g.name_en = 'Cairo' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Greater Cairo');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'القصر العيني', 'Kasr Al Ainy' FROM public.egypt_governorates g WHERE g.name_en = 'Cairo' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Kasr Al Ainy');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'المعادي', 'Maadi' FROM public.egypt_governorates g WHERE g.name_en = 'Cairo' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Maadi');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'المعادي الجديدة', 'New Maadi' FROM public.egypt_governorates g WHERE g.name_en = 'Cairo' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'New Maadi');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'المنيل', 'Manial' FROM public.egypt_governorates g WHERE g.name_en = 'Cairo' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Manial');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'النزهة الجديدة', 'New Nozha' FROM public.egypt_governorates g WHERE g.name_en = 'Cairo' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'New Nozha');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'دار السلام', 'Dar El Salam' FROM public.egypt_governorates g WHERE g.name_en = 'Cairo' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Dar El Salam');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'رمسيس', 'Ramses' FROM public.egypt_governorates g WHERE g.name_en = 'Cairo' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Ramses');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'شبرا', 'Shubra' FROM public.egypt_governorates g WHERE g.name_en = 'Cairo' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Shubra');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'طريق القاهرة – الإسماعيلية الصحراوي', 'Cairo–Ismailia Desert Rd' FROM public.egypt_governorates g WHERE g.name_en = 'Cairo' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Cairo–Ismailia Desert Rd');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'عابدين', 'Abdeen' FROM public.egypt_governorates g WHERE g.name_en = 'Cairo' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Abdeen');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'عين شمس / ألف مسكن', 'Ain Shams / Alf Maskan' FROM public.egypt_governorates g WHERE g.name_en = 'Cairo' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Ain Shams / Alf Maskan');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'مدينة نصر', 'Nasr City' FROM public.egypt_governorates g WHERE g.name_en = 'Cairo' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Nasr City');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'مصر الجديدة', 'Heliopolis' FROM public.egypt_governorates g WHERE g.name_en = 'Cairo' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Heliopolis');
INSERT INTO public.egypt_cities (governorate_id, name_ar, name_en) SELECT g.id, 'وسط البلد', 'Downtown' FROM public.egypt_governorates g WHERE g.name_en = 'Cairo' AND NOT EXISTS (SELECT 1 FROM public.egypt_cities c WHERE c.governorate_id = g.id AND c.name_en = 'Downtown');

COMMIT;
