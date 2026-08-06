"""
إنشاء مريض تجريبي بكامل البيانات لعرض الملخص السريري.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from src.models.user import db, User
from src.models.patient import Patient, MedicalRecord, Allergy
from src.models.medical_record import Disease, Surgery, Vaccination, LabTest, Radiology
from src.models.medication import Medication
from src.models.doctor import Doctor
from src.models.appointment import Appointment
from werkzeug.security import generate_password_hash
from datetime import date, datetime, timedelta

DEMO_EMAIL = 'demo.patient@sehaty.com'
DEMO_PASS  = 'Demo@12345'

with app.app_context():
    # ── حذف إن وُجد ──
    old_user = User.query.filter_by(email=DEMO_EMAIL).first()
    if old_user:
        old_pat = Patient.query.filter_by(user_id=old_user.id).first()
        if old_pat:
            for m in [Disease, Surgery, Allergy, Medication, LabTest, Radiology, Vaccination, MedicalRecord]:
                m.query.filter_by(patient_id=old_pat.id).delete()
            Appointment.query.filter_by(patient_id=old_pat.id).delete()
            db.session.delete(old_pat)
        db.session.delete(old_user)
        db.session.commit()

    # ── مستخدم ──
    user = User(
        username='demo_patient',
        email=DEMO_EMAIL,
        password_hash=generate_password_hash(DEMO_PASS),
        user_type='patient',
        is_active=True,
    )
    db.session.add(user)
    db.session.flush()

    # ── ملف المريض ──
    patient = Patient(
        user_id=user.id,
        first_name='محمد',
        last_name='الأحمدي',
        date_of_birth=date(1985, 3, 15),
        gender='male',
        national_id='1085432167',
        phone='0501234567',
        email=DEMO_EMAIL,
        address='الرياض، حي النزهة، شارع الأمير سلطان',
        blood_type='A+',
        height=175.0,
        weight=82.0,
        emergency_contact_name='أحمد الأحمدي',
        emergency_contact_phone='0509876543',
        insurance_number='INS-2024-88921',
        insurance_provider='شركة التعاونية للتأمين',
    )
    db.session.add(patient)
    db.session.flush()

    pid = patient.id

    # ── الأمراض ──
    diseases = [
        Disease(patient_id=pid, name='داء السكري من النوع الثاني', icd_code='E11',
                status='chronic', severity='moderate',
                diagnosis_date=date(2018, 6, 10), treating_doctor='د. خالد العمري',
                hospital='مستشفى الملك فهد', treatment_summary='ميتفورمين 500 ملغ مرتين يومياً'),
        Disease(patient_id=pid, name='ارتفاع ضغط الدم', icd_code='I10',
                status='chronic', severity='moderate',
                diagnosis_date=date(2019, 2, 20), treating_doctor='د. سارة المالكي',
                hospital='مستشفى الملك عبدالعزيز', treatment_summary='أملوديبين 5 ملغ يومياً'),
        Disease(patient_id=pid, name='التهاب المفاصل التنكسي', icd_code='M17.1',
                status='active', severity='mild',
                diagnosis_date=date(2022, 9, 5), treating_doctor='د. فيصل الزهراني',
                notes='يؤثر على الركبة اليمنى بشكل رئيسي'),
        Disease(patient_id=pid, name='التهاب الزائدة الدودية الحاد', icd_code='K37',
                status='resolved', severity='severe',
                diagnosis_date=date(2015, 4, 2), resolution_date=date(2015, 4, 8),
                hospital='مستشفى الملك فيصل', treating_doctor='د. محمد القحطاني'),
    ]
    for d in diseases:
        db.session.add(d)

    # ── العمليات الجراحية ──
    surgeries = [
        Surgery(patient_id=pid, name='استئصال الزائدة الدودية',
                surgery_type='استئصال', surgery_date=date(2015, 4, 3),
                hospital='مستشفى الملك فيصل', surgeon='د. محمد القحطاني',
                anesthesia_type='general', duration_minutes=75,
                outcome='successful', post_op_notes='تعافٍ ممتاز دون مضاعفات',
                follow_up_date=date(2015, 4, 17)),
        Surgery(patient_id=pid, name='إصلاح الغضروف الهلالي للركبة اليمنى',
                surgery_type='تنظير مفصل', surgery_date=date(2023, 1, 18),
                hospital='المركز الطبي السعودي الألماني', surgeon='د. عبدالرحمن السلمي',
                anesthesia_type='spinal', duration_minutes=90,
                outcome='successful', complications='تورم خفيف لأسبوعين',
                post_op_notes='العلاج الطبيعي لمدة 6 أسابيع'),
    ]
    for s in surgeries:
        db.session.add(s)

    # ── الحساسية ──
    allergies = [
        Allergy(patient_id=pid, allergen='البنسلين', severity='severe',
                reaction='طفح جلدي وضيق في التنفس', notes='تحسس دوائي موثق'),
        Allergy(patient_id=pid, allergen='الأسبرين', severity='moderate',
                reaction='غثيان وآلام في المعدة'),
        Allergy(patient_id=pid, allergen='المكسرات (الفول السوداني)', severity='severe',
                reaction='حساسية فورية — يحمل حقنة إيبي نفرين'),
        Allergy(patient_id=pid, allergen='الغبار والعفن', severity='mild',
                reaction='عطس وسيلان الأنف'),
    ]
    for a in allergies:
        db.session.add(a)

    # ── الأدوية الحالية ──
    meds = [
        Medication(patient_id=pid, name='ميتفورمين', generic_name='Metformin',
                   dosage='500 ملغ', form='أقراص', frequency='مرتين يومياً',
                   start_date=date(2018, 6, 15), is_active=True,
                   instructions='مع الطعام لتقليل الأعراض الجانبية'),
        Medication(patient_id=pid, name='أملوديبين', generic_name='Amlodipine',
                   dosage='5 ملغ', form='أقراص', frequency='مرة يومياً صباحاً',
                   start_date=date(2019, 3, 1), is_active=True),
        Medication(patient_id=pid, name='أتورفاستاتين', generic_name='Atorvastatin',
                   dosage='20 ملغ', form='أقراص', frequency='مرة يومياً ليلاً',
                   start_date=date(2020, 1, 10), is_active=True,
                   instructions='تجنب عصير الجريب فروت'),
        Medication(patient_id=pid, name='أوميبرازول', generic_name='Omeprazole',
                   dosage='20 ملغ', form='كبسولات', frequency='مرة يومياً قبل الإفطار',
                   start_date=date(2021, 5, 20), is_active=True),
    ]
    for m in meds:
        db.session.add(m)

    # ── التحاليل المخبرية (مكتملة — لها نتائج) ──
    labs = [
        LabTest(patient_id=pid, test_name='سكر الدم الصيامي', test_category='الغدد الصماء',
                test_date=date(2024, 1, 15), lab_name='مختبرات الدقة',
                ordering_doctor='د. خالد العمري',
                result_value='128', unit='mg/dL', reference_range='70-100',
                status='abnormal', interpretation='مرتفع قليلاً — متابعة النظام الغذائي'),
        LabTest(patient_id=pid, test_name='هيموغلوبين السكري (HbA1c)', test_category='الغدد الصماء',
                test_date=date(2024, 1, 15), lab_name='مختبرات الدقة',
                ordering_doctor='د. خالد العمري',
                result_value='7.2', unit='%', reference_range='< 6.5',
                status='abnormal', interpretation='ضبط متوسط للسكري'),
        LabTest(patient_id=pid, test_name='الكوليسترول الكلي', test_category='الدهون',
                test_date=date(2024, 1, 15), lab_name='مختبرات الدقة',
                ordering_doctor='د. سارة المالكي',
                result_value='195', unit='mg/dL', reference_range='< 200',
                status='normal', interpretation='ضمن الحدود الطبيعية'),
        LabTest(patient_id=pid, test_name='LDL الكوليسترول الضار', test_category='الدهون',
                test_date=date(2024, 1, 15), lab_name='مختبرات الدقة',
                ordering_doctor='د. سارة المالكي',
                result_value='118', unit='mg/dL', reference_range='< 100',
                status='abnormal', interpretation='مرتفع — الاستمرار في الأتورفاستاتين'),
        LabTest(patient_id=pid, test_name='صورة دم كاملة (CBC)', test_category='الدم',
                test_date=date(2024, 3, 5), lab_name='مختبرات الرعاية',
                ordering_doctor='د. خالد العمري',
                result_value='خضاب الدم: 14.2 g/dL، كريات بيضاء: 7.1 K/μL، صفائح: 245 K/μL',
                unit='', reference_range='طبيعي',
                status='normal'),
        LabTest(patient_id=pid, test_name='وظائف الكلى (Creatinine)', test_category='وظائف الكلى',
                test_date=date(2024, 3, 5), lab_name='مختبرات الرعاية',
                ordering_doctor='د. خالد العمري',
                result_value='0.95', unit='mg/dL', reference_range='0.7-1.2',
                status='normal'),
        LabTest(patient_id=pid, test_name='وظائف الكبد (ALT/AST)', test_category='وظائف الكبد',
                test_date=date(2024, 3, 5), lab_name='مختبرات الرعاية',
                ordering_doctor='د. خالد العمري',
                result_value='ALT: 32 U/L، AST: 28 U/L',
                unit='', reference_range='< 56 / < 40',
                status='normal'),
    ]
    for l in labs:
        db.session.add(l)

    # ── الأشعة (مكتملة — لها تقارير) ──
    radiology_list = [
        Radiology(patient_id=pid, scan_type='xray', body_part='الصدر',
                  scan_date=date(2023, 11, 10), facility='مركز التصوير الطبي المتقدم',
                  radiologist='د. نورة الحربي', ordering_doctor='د. سارة المالكي',
                  reason='تقييم دوري لارتفاع ضغط الدم',
                  findings='القلب طبيعي الحجم. الرئتان صافيتان. لا تضخم في القلب.',
                  impression='أشعة صدر طبيعية دون مستجدات'),
        Radiology(patient_id=pid, scan_type='mri', body_part='الركبة اليمنى',
                  scan_date=date(2022, 12, 5), facility='مركز التصوير الطبي المتقدم',
                  radiologist='د. عمر الشهراني', ordering_doctor='د. فيصل الزهراني',
                  reason='ألم مزمن وتقييم ما قبل الجراحة',
                  findings='تمزق جزئي في الغضروف الهلالي الداخلي. وجود انصباب مفصلي خفيف. الأربطة سليمة.',
                  impression='تمزق جزئي للغضروف الهلالي الداخلي — يُنصح بالتدخل الجراحي',
                  recommendation='مراجعة جراح العظام لتقييم إمكانية التنظير المفصلي'),
        Radiology(patient_id=pid, scan_type='ultrasound', body_part='البطن والحوض',
                  scan_date=date(2024, 2, 20), facility='مستشفى الملك فهد',
                  radiologist='د. هنا القرشي', ordering_doctor='د. خالد العمري',
                  reason='متابعة دورية لمريض السكري',
                  findings='الكبد طبيعي الحجم وبنيته. المرارة طبيعية بلا حصوات. البنكرياس طبيعي. الكليتان طبيعيتا الحجم والبنية.',
                  impression='فحص بالموجات الصوتية للبطن طبيعي'),
    ]
    for r in radiology_list:
        db.session.add(r)

    # ── طبيب تجريبي ──
    demo_doc = Doctor.query.filter_by(license_number='DR-DEMO-0001').first()
    if not demo_doc:
        doc_user = User.query.filter_by(email='demo.doctor@sehaty.com').first()
        if not doc_user:
            doc_user = User(username='demo_doctor', email='demo.doctor@sehaty.com',
                            password_hash=generate_password_hash('Doctor@123'),
                            user_type='doctor', is_active=True)
            db.session.add(doc_user)
            db.session.flush()
        demo_doc = Doctor(
            user_id=doc_user.id,
            first_name='خالد', last_name='العمري',
            phone='0551111111', email='demo.doctor@sehaty.com',
            license_number='DR-DEMO-0001',
            specialization='الباطنية وأمراض السكري',
            sub_specialization='السكري والغدد الصماء',
            years_of_experience=15,
            clinic_name='عيادة العمري للباطنية',
            hospital_affiliation='مستشفى الملك فهد',
            is_verified=True, is_active=True,
        )
        db.session.add(demo_doc)
        db.session.flush()

    # ── زيارات مكتملة ──
    visits_data = [
        dict(date=datetime(2023, 9, 12, 10, 0), reason='متابعة داء السكري وارتفاع ضغط الدم',
             symptoms='دوار خفيف وزيادة العطش', notes='تعديل جرعة ميتفورمين'),
        dict(date=datetime(2024, 1, 15, 9, 30), reason='مراجعة دورية ونتائج التحاليل',
             symptoms='ألم خفيف في القدمين', notes='طلب تحاليل دم شاملة ومتابعة بعد شهر'),
        dict(date=datetime(2024, 3, 5, 11, 0), reason='متابعة نتائج التحاليل والأشعة',
             symptoms='لا شكاوى جديدة', notes='الحالة مستقرة — استمرار الأدوية الحالية'),
    ]
    for v in visits_data:
        appt = Appointment(
            patient_id=pid, doctor_id=demo_doc.id,
            appointment_date=v['date'], duration=30,
            appointment_type='in_person', status='completed',
            reason=v['reason'], symptoms=v['symptoms'],
            fee=200.0, payment_status='paid', payment_method='card',
        )
        db.session.add(appt)
        db.session.flush()

        record = MedicalRecord(
            patient_id=pid, doctor_id=demo_doc.id,
            visit_date=v['date'],
            symptoms=v['symptoms'],
            diagnosis='داء السكري من النوع الثاني تحت السيطرة — ارتفاع ضغط الدم مضبوط',
            treatment=v['notes'],
            notes='المريض ملتزم بالأدوية والنظام الغذائي. يُنصح بالمشي 30 دقيقة يومياً.',
            vital_signs={
                'ضغط الدم': '138/88 mmHg',
                'النبض': '76 نبضة/دقيقة',
                'الحرارة': '36.8°C',
                'التشبع بالأكسجين': '98%',
                'الوزن': '82 كغ',
            },
        )
        db.session.add(record)

    db.session.commit()
    print(f'✅ تم إنشاء مريض تجريبي')
    print(f'   البريد: {DEMO_EMAIL}')
    print(f'   كلمة المرور: {DEMO_PASS}')
    print(f'   patient_id: {pid}')
