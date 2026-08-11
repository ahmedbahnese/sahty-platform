"""
مسارات API للملف الطبي الإلكتروني الكامل.
يشمل: الأمراض، العمليات، الحساسية، الأدوية، التطعيمات، التحاليل، الأشعة، التاريخ المرضي.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, date
from src.models.user import db
from src.models.patient import Patient, Allergy
from src.models.medication import Medication
from src.models.medical_record import (
    Disease, Surgery, Vaccination, LabTest, Radiology, MedicalHistory,
    BloodGasReading, ECGRecord
)
from src.routes.auth import token_required

medical_record_bp = Blueprint('medical_record', __name__)


def _get_patient(current_user):
    """استرجاع ملف المريض للمستخدم الحالي."""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return None, jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    return patient, None, None


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


# ──────────────────────────────────────────────
# ملخص الملف الطبي الكامل
# ──────────────────────────────────────────────
@medical_record_bp.route('/summary', methods=['GET'])
@token_required
def get_full_summary(current_user):
    """جلب كامل الملف الطبي دفعة واحدة."""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404

    history = MedicalHistory.query.filter_by(patient_id=patient.id).first()

    return jsonify({
        'patient': patient.to_dict(),
        'diseases': [d.to_dict() for d in Disease.query.filter_by(patient_id=patient.id).order_by(Disease.diagnosis_date.desc()).all()],
        'surgeries': [s.to_dict() for s in Surgery.query.filter_by(patient_id=patient.id).order_by(Surgery.surgery_date.desc()).all()],
        'allergies': [a.to_dict() for a in Allergy.query.filter_by(patient_id=patient.id).all()],
        'medications': [m.to_dict() for m in Medication.query.filter_by(patient_id=patient.id).order_by(Medication.start_date.desc()).all()],
        'vaccinations': [v.to_dict() for v in Vaccination.query.filter_by(patient_id=patient.id).order_by(Vaccination.date_given.desc()).all()],
        'lab_tests': [l.to_dict() for l in LabTest.query.filter_by(patient_id=patient.id).order_by(LabTest.test_date.desc()).all()],
        'radiology': [r.to_dict() for r in Radiology.query.filter_by(patient_id=patient.id).order_by(Radiology.scan_date.desc()).all()],
        'medical_history': history.to_dict() if history else None,
    }), 200


# ──────────────────────────────────────────────
# الأمراض
# ──────────────────────────────────────────────
@medical_record_bp.route('/diseases', methods=['GET'])
@token_required
def get_diseases(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    diseases = Disease.query.filter_by(patient_id=patient.id).order_by(Disease.diagnosis_date.desc()).all()
    return jsonify([d.to_dict() for d in diseases]), 200


@medical_record_bp.route('/diseases', methods=['POST'])
@token_required
def add_disease(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    data = request.get_json(silent=True) or {}
    if not data.get('name'):
        return jsonify({'message': 'اسم المرض مطلوب'}), 400
    disease = Disease(
        patient_id=patient.id,
        name=data['name'],
        icd_code=data.get('icd_code'),
        status=data.get('status', 'active'),
        severity=data.get('severity'),
        diagnosis_date=_parse_date(data.get('diagnosis_date')),
        resolution_date=_parse_date(data.get('resolution_date')),
        treating_doctor=data.get('treating_doctor'),
        hospital=data.get('hospital'),
        treatment_summary=data.get('treatment_summary'),
        notes=data.get('notes'),
        attachment_data=data.get('attachment_data'),
    )
    db.session.add(disease)
    db.session.commit()
    return jsonify(disease.to_dict()), 201


@medical_record_bp.route('/diseases/<int:disease_id>', methods=['PUT'])
@token_required
def update_disease(current_user, disease_id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    disease = Disease.query.filter_by(id=disease_id, patient_id=patient.id).first()
    if not disease:
        return jsonify({'message': 'لم يتم العثور على المرض'}), 404
    data = request.get_json(silent=True) or {}
    for field in ('name', 'icd_code', 'status', 'severity', 'treating_doctor', 'hospital', 'treatment_summary', 'notes', 'attachment_data'):
        if field in data:
            setattr(disease, field, data[field])
    for date_field in ('diagnosis_date', 'resolution_date'):
        if date_field in data:
            setattr(disease, date_field, _parse_date(data[date_field]))
    db.session.commit()
    return jsonify(disease.to_dict()), 200


@medical_record_bp.route('/diseases/<int:disease_id>', methods=['DELETE'])
@token_required
def delete_disease(current_user, disease_id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    disease = Disease.query.filter_by(id=disease_id, patient_id=patient.id).first()
    if not disease:
        return jsonify({'message': 'لم يتم العثور على المرض'}), 404
    db.session.delete(disease)
    db.session.commit()
    return jsonify({'message': 'تم الحذف بنجاح'}), 200


# ──────────────────────────────────────────────
# العمليات الجراحية
# ──────────────────────────────────────────────
@medical_record_bp.route('/surgeries', methods=['GET'])
@token_required
def get_surgeries(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    surgeries = Surgery.query.filter_by(patient_id=patient.id).order_by(Surgery.surgery_date.desc()).all()
    return jsonify([s.to_dict() for s in surgeries]), 200


@medical_record_bp.route('/surgeries', methods=['POST'])
@token_required
def add_surgery(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    data = request.get_json(silent=True) or {}
    if not data.get('name'):
        return jsonify({'message': 'اسم العملية مطلوب'}), 400
    surgery = Surgery(
        patient_id=patient.id,
        name=data['name'],
        surgery_type=data.get('surgery_type'),
        surgery_date=_parse_date(data.get('surgery_date')),
        hospital=data.get('hospital'),
        surgeon=data.get('surgeon'),
        anesthesia_type=data.get('anesthesia_type'),
        duration_minutes=data.get('duration_minutes'),
        outcome=data.get('outcome'),
        complications=data.get('complications'),
        post_op_notes=data.get('post_op_notes'),
        follow_up_date=_parse_date(data.get('follow_up_date')),
        notes=data.get('notes'),
    )
    db.session.add(surgery)
    db.session.commit()
    return jsonify(surgery.to_dict()), 201


@medical_record_bp.route('/surgeries/<int:surgery_id>', methods=['PUT'])
@token_required
def update_surgery(current_user, surgery_id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    surgery = Surgery.query.filter_by(id=surgery_id, patient_id=patient.id).first()
    if not surgery:
        return jsonify({'message': 'لم يتم العثور على العملية'}), 404
    data = request.get_json(silent=True) or {}
    for field in ('name', 'surgery_type', 'hospital', 'surgeon', 'anesthesia_type',
                  'duration_minutes', 'outcome', 'complications', 'post_op_notes', 'notes'):
        if field in data:
            setattr(surgery, field, data[field])
    for date_field in ('surgery_date', 'follow_up_date'):
        if date_field in data:
            setattr(surgery, date_field, _parse_date(data[date_field]))
    db.session.commit()
    return jsonify(surgery.to_dict()), 200


@medical_record_bp.route('/surgeries/<int:surgery_id>', methods=['DELETE'])
@token_required
def delete_surgery(current_user, surgery_id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    surgery = Surgery.query.filter_by(id=surgery_id, patient_id=patient.id).first()
    if not surgery:
        return jsonify({'message': 'لم يتم العثور على العملية'}), 404
    db.session.delete(surgery)
    db.session.commit()
    return jsonify({'message': 'تم الحذف بنجاح'}), 200


# ──────────────────────────────────────────────
# الحساسية
# ──────────────────────────────────────────────
@medical_record_bp.route('/allergies', methods=['GET'])
@token_required
def get_allergies(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    allergies = Allergy.query.filter_by(patient_id=patient.id).all()
    return jsonify([a.to_dict() for a in allergies]), 200


@medical_record_bp.route('/allergies', methods=['POST'])
@token_required
def add_allergy(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    data = request.get_json(silent=True) or {}
    if not data.get('allergen'):
        return jsonify({'message': 'اسم المسبب للحساسية مطلوب'}), 400
    allergy = Allergy(
        patient_id=patient.id,
        allergen=data['allergen'],
        severity=data.get('severity'),
        reaction=data.get('reaction'),
        notes=data.get('notes'),
    )
    db.session.add(allergy)
    db.session.commit()
    return jsonify(allergy.to_dict()), 201


@medical_record_bp.route('/allergies/<int:allergy_id>', methods=['PUT'])
@token_required
def update_allergy(current_user, allergy_id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    allergy = Allergy.query.filter_by(id=allergy_id, patient_id=patient.id).first()
    if not allergy:
        return jsonify({'message': 'لم يتم العثور على سجل الحساسية'}), 404
    data = request.get_json(silent=True) or {}
    for field in ('allergen', 'severity', 'reaction', 'notes'):
        if field in data:
            setattr(allergy, field, data[field])
    db.session.commit()
    return jsonify(allergy.to_dict()), 200


@medical_record_bp.route('/allergies/<int:allergy_id>', methods=['DELETE'])
@token_required
def delete_allergy(current_user, allergy_id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    allergy = Allergy.query.filter_by(id=allergy_id, patient_id=patient.id).first()
    if not allergy:
        return jsonify({'message': 'لم يتم العثور على سجل الحساسية'}), 404
    db.session.delete(allergy)
    db.session.commit()
    return jsonify({'message': 'تم الحذف بنجاح'}), 200


# ──────────────────────────────────────────────
# الأدوية
# ──────────────────────────────────────────────
@medical_record_bp.route('/medications', methods=['GET'])
@token_required
def get_medications(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    meds = Medication.query.filter_by(patient_id=patient.id).order_by(Medication.start_date.desc()).all()
    return jsonify([m.to_dict() for m in meds]), 200


@medical_record_bp.route('/medications', methods=['POST'])
@token_required
def add_medication(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    data = request.get_json(silent=True) or {}
    if not data.get('name') or not data.get('dosage') or not data.get('frequency'):
        return jsonify({'message': 'اسم الدواء والجرعة والتكرار مطلوبة'}), 400
    med = Medication(
        patient_id=patient.id,
        name=data['name'],
        generic_name=data.get('generic_name'),
        dosage=data['dosage'],
        form=data.get('form'),
        frequency=data['frequency'],
        duration=data.get('duration'),
        instructions=data.get('instructions'),
        start_date=_parse_date(data.get('start_date')) or date.today(),
        end_date=_parse_date(data.get('end_date')),
        is_active=data.get('is_active', True),
        side_effects=data.get('side_effects'),
        warnings=data.get('warnings'),
        attachment_data=data.get('attachment_data'),
    )
    db.session.add(med)
    db.session.commit()
    return jsonify(med.to_dict()), 201


@medical_record_bp.route('/medications/<int:med_id>', methods=['PUT'])
@token_required
def update_medication(current_user, med_id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    med = Medication.query.filter_by(id=med_id, patient_id=patient.id).first()
    if not med:
        return jsonify({'message': 'لم يتم العثور على الدواء'}), 404
    data = request.get_json(silent=True) or {}
    for field in ('name', 'generic_name', 'dosage', 'form', 'frequency', 'duration',
                  'instructions', 'is_active', 'is_completed', 'side_effects', 'warnings', 'attachment_data'):
        if field in data:
            setattr(med, field, data[field])
    for date_field in ('start_date', 'end_date'):
        if date_field in data:
            setattr(med, date_field, _parse_date(data[date_field]))
    db.session.commit()
    return jsonify(med.to_dict()), 200


@medical_record_bp.route('/medications/<int:med_id>', methods=['DELETE'])
@token_required
def delete_medication(current_user, med_id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    med = Medication.query.filter_by(id=med_id, patient_id=patient.id).first()
    if not med:
        return jsonify({'message': 'لم يتم العثور على الدواء'}), 404
    db.session.delete(med)
    db.session.commit()
    return jsonify({'message': 'تم الحذف بنجاح'}), 200


# ──────────────────────────────────────────────
# التطعيمات
# ──────────────────────────────────────────────
@medical_record_bp.route('/vaccinations', methods=['GET'])
@token_required
def get_vaccinations(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    vaccinations = Vaccination.query.filter_by(patient_id=patient.id).order_by(Vaccination.date_given.desc()).all()
    return jsonify([v.to_dict() for v in vaccinations]), 200


@medical_record_bp.route('/vaccinations', methods=['POST'])
@token_required
def add_vaccination(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    data = request.get_json(silent=True) or {}
    if not data.get('vaccine_name'):
        return jsonify({'message': 'اسم التطعيم مطلوب'}), 400
    vaccination = Vaccination(
        patient_id=patient.id,
        vaccine_name=data['vaccine_name'],
        disease_prevented=data.get('disease_prevented'),
        dose_number=data.get('dose_number', 1),
        total_doses=data.get('total_doses'),
        date_given=_parse_date(data.get('date_given')),
        next_due_date=_parse_date(data.get('next_due_date')),
        provider=data.get('provider'),
        batch_number=data.get('batch_number'),
        administration_site=data.get('administration_site'),
        reaction=data.get('reaction'),
        notes=data.get('notes'),
        attachment_data=data.get('attachment_data'),
    )
    db.session.add(vaccination)
    db.session.commit()
    return jsonify(vaccination.to_dict()), 201


@medical_record_bp.route('/vaccinations/<int:vacc_id>', methods=['PUT'])
@token_required
def update_vaccination(current_user, vacc_id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    vaccination = Vaccination.query.filter_by(id=vacc_id, patient_id=patient.id).first()
    if not vaccination:
        return jsonify({'message': 'لم يتم العثور على التطعيم'}), 404
    data = request.get_json(silent=True) or {}
    for field in ('vaccine_name', 'disease_prevented', 'dose_number', 'total_doses',
                  'provider', 'batch_number', 'administration_site', 'reaction', 'notes', 'attachment_data'):
        if field in data:
            setattr(vaccination, field, data[field])
    for date_field in ('date_given', 'next_due_date'):
        if date_field in data:
            setattr(vaccination, date_field, _parse_date(data[date_field]))
    db.session.commit()
    return jsonify(vaccination.to_dict()), 200


@medical_record_bp.route('/vaccinations/<int:vacc_id>', methods=['DELETE'])
@token_required
def delete_vaccination(current_user, vacc_id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    vaccination = Vaccination.query.filter_by(id=vacc_id, patient_id=patient.id).first()
    if not vaccination:
        return jsonify({'message': 'لم يتم العثور على التطعيم'}), 404
    db.session.delete(vaccination)
    db.session.commit()
    return jsonify({'message': 'تم الحذف بنجاح'}), 200


# ──────────────────────────────────────────────
# التحاليل المخبرية
# ──────────────────────────────────────────────
@medical_record_bp.route('/lab-tests', methods=['GET'])
@token_required
def get_lab_tests(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    tests = LabTest.query.filter_by(patient_id=patient.id).order_by(LabTest.test_date.desc()).all()
    return jsonify([t.to_dict() for t in tests]), 200


@medical_record_bp.route('/lab-tests', methods=['POST'])
@token_required
def add_lab_test(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    data = request.get_json(silent=True) or {}
    if not data.get('test_name'):
        return jsonify({'message': 'اسم التحليل مطلوب'}), 400
    test = LabTest(
        patient_id=patient.id,
        test_name=data['test_name'],
        test_category=data.get('test_category'),
        test_date=_parse_date(data.get('test_date')),
        lab_name=data.get('lab_name'),
        ordering_doctor=data.get('ordering_doctor'),
        result_value=data.get('result_value'),
        unit=data.get('unit'),
        reference_range=data.get('reference_range'),
        status=data.get('status', 'normal'),
        interpretation=data.get('interpretation'),
        notes=data.get('notes'),
        attachment_data=data.get('attachment_data'),
    )
    db.session.add(test)
    db.session.commit()
    # Auto-detect blood type from lab test name/result
    blood_type_val = data.get('result_value', '')
    if blood_type_val and any(k in data.get('test_name', '').lower() for k in ('blood type', 'فصيلة', 'blood group', 'abo')):
        valid_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        for bt in valid_types:
            if bt.lower() in blood_type_val.lower() or bt in blood_type_val:
                patient.blood_type = bt
                db.session.commit()
                break
    return jsonify(test.to_dict()), 201


@medical_record_bp.route('/lab-tests/<int:test_id>', methods=['PUT'])
@token_required
def update_lab_test(current_user, test_id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    test = LabTest.query.filter_by(id=test_id, patient_id=patient.id).first()
    if not test:
        return jsonify({'message': 'لم يتم العثور على التحليل'}), 404
    data = request.get_json(silent=True) or {}
    for field in ('test_name', 'test_category', 'lab_name', 'ordering_doctor',
                  'result_value', 'unit', 'reference_range', 'status', 'interpretation', 'notes', 'attachment_data'):
        if field in data:
            setattr(test, field, data[field])
    if 'test_date' in data:
        test.test_date = _parse_date(data['test_date'])
    db.session.commit()
    return jsonify(test.to_dict()), 200


@medical_record_bp.route('/lab-tests/<int:test_id>', methods=['DELETE'])
@token_required
def delete_lab_test(current_user, test_id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    test = LabTest.query.filter_by(id=test_id, patient_id=patient.id).first()
    if not test:
        return jsonify({'message': 'لم يتم العثور على التحليل'}), 404
    db.session.delete(test)
    db.session.commit()
    return jsonify({'message': 'تم الحذف بنجاح'}), 200


# ──────────────────────────────────────────────
# الأشعة والتصوير الطبي
# ──────────────────────────────────────────────
@medical_record_bp.route('/radiology', methods=['GET'])
@token_required
def get_radiology(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    scans = Radiology.query.filter_by(patient_id=patient.id).order_by(Radiology.scan_date.desc()).all()
    return jsonify([r.to_dict() for r in scans]), 200


@medical_record_bp.route('/radiology', methods=['POST'])
@token_required
def add_radiology(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    data = request.get_json(silent=True) or {}
    if not data.get('scan_type') or not data.get('body_part'):
        return jsonify({'message': 'نوع الأشعة والجزء المصوَّر مطلوبان'}), 400
    scan = Radiology(
        patient_id=patient.id,
        scan_type=data['scan_type'],
        body_part=data['body_part'],
        scan_date=_parse_date(data.get('scan_date')),
        facility=data.get('facility'),
        radiologist=data.get('radiologist'),
        ordering_doctor=data.get('ordering_doctor'),
        reason=data.get('reason'),
        findings=data.get('findings'),
        impression=data.get('impression'),
        recommendation=data.get('recommendation'),
        notes=data.get('notes'),
        attachment_data=data.get('attachment_data'),
        report_data=data.get('report_data'),
    )
    db.session.add(scan)
    db.session.commit()
    return jsonify(scan.to_dict()), 201


@medical_record_bp.route('/radiology/<int:scan_id>', methods=['PUT'])
@token_required
def update_radiology(current_user, scan_id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    scan = Radiology.query.filter_by(id=scan_id, patient_id=patient.id).first()
    if not scan:
        return jsonify({'message': 'لم يتم العثور على الأشعة'}), 404
    data = request.get_json(silent=True) or {}
    for field in ('scan_type', 'body_part', 'facility', 'radiologist', 'ordering_doctor',
                  'reason', 'findings', 'impression', 'recommendation', 'notes',
                  'attachment_data', 'report_data'):
        if field in data:
            setattr(scan, field, data[field])
    if 'scan_date' in data:
        scan.scan_date = _parse_date(data['scan_date'])
    db.session.commit()
    return jsonify(scan.to_dict()), 200


@medical_record_bp.route('/radiology/<int:scan_id>', methods=['DELETE'])
@token_required
def delete_radiology(current_user, scan_id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    scan = Radiology.query.filter_by(id=scan_id, patient_id=patient.id).first()
    if not scan:
        return jsonify({'message': 'لم يتم العثور على الأشعة'}), 404
    db.session.delete(scan)
    db.session.commit()
    return jsonify({'message': 'تم الحذف بنجاح'}), 200


# ──────────────────────────────────────────────
# التاريخ المرضي
# ──────────────────────────────────────────────
@medical_record_bp.route('/history', methods=['GET'])
@token_required
def get_medical_history(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    history = MedicalHistory.query.filter_by(patient_id=patient.id).first()
    return jsonify(history.to_dict() if history else {}), 200


@medical_record_bp.route('/history', methods=['PUT'])
@token_required
def upsert_medical_history(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    data = request.get_json(silent=True) or {}
    history = MedicalHistory.query.filter_by(patient_id=patient.id).first()
    if not history:
        history = MedicalHistory(patient_id=patient.id)
        db.session.add(history)
    for field in ('smoking_status', 'smoking_years', 'alcohol_use', 'physical_activity',
                  'diet_type', 'family_history', 'chronic_conditions', 'genetic_conditions', 'general_notes'):
        if field in data:
            setattr(history, field, data[field])
    db.session.commit()
    return jsonify(history.to_dict()), 200


# ──────────────────────────────────────────────
# بيانات المريض الحيوية (وزن، طول، فصيلة الدم)
# ──────────────────────────────────────────────
@medical_record_bp.route('/patient-profile', methods=['GET'])
@token_required
def get_patient_profile(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    allergies = [a.to_dict() for a in Allergy.query.filter_by(patient_id=patient.id).all()]
    return jsonify({
        'id': patient.id,
        'first_name': patient.first_name,
        'last_name': patient.last_name,
        'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
        'gender': patient.gender,
        'blood_type': patient.blood_type,
        'height': patient.height,
        'weight': patient.weight,
        'allergies': allergies,
    }), 200


@medical_record_bp.route('/patient-vitals', methods=['PUT'])
@token_required
def update_patient_vitals(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    data = request.get_json(silent=True) or {}
    if 'height' in data and data['height'] is not None:
        patient.height = float(data['height'])
    if 'weight' in data and data['weight'] is not None:
        patient.weight = float(data['weight'])
    if 'blood_type' in data and data['blood_type']:
        patient.blood_type = data['blood_type']
    db.session.commit()
    return jsonify({'height': patient.height, 'weight': patient.weight, 'blood_type': patient.blood_type}), 200


# ──────────────────────────────────────────────
# تقرير طبي شامل (JSON)
# ──────────────────────────────────────────────
@medical_record_bp.route('/report', methods=['GET'])
@token_required
def get_medical_report(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    allergies = [a.to_dict() for a in Allergy.query.filter_by(patient_id=patient.id).all()]
    diseases = [d.to_dict() for d in Disease.query.filter_by(patient_id=patient.id).all()]
    medications = [m.to_dict() for m in Medication.query.filter_by(patient_id=patient.id, is_active=True).all()]
    vaccinations = [v.to_dict() for v in Vaccination.query.filter_by(patient_id=patient.id).all()]
    lab_tests = [l.to_dict() for l in LabTest.query.filter_by(patient_id=patient.id).order_by(LabTest.test_date.desc()).limit(20).all()]
    radiology = [r.to_dict() for r in Radiology.query.filter_by(patient_id=patient.id).order_by(Radiology.scan_date.desc()).limit(10).all()]
    history = MedicalHistory.query.filter_by(patient_id=patient.id).first()
    from datetime import date as dt_date
    today = dt_date.today()
    age = None
    if patient.date_of_birth:
        age = today.year - patient.date_of_birth.year - (
            (today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day)
        )
    return jsonify({
        'generated_at': datetime.utcnow().isoformat(),
        'patient': {
            'name': f'{patient.first_name} {patient.last_name}',
            'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
            'age': age,
            'gender': patient.gender,
            'blood_type': patient.blood_type,
            'height': patient.height,
            'weight': patient.weight,
            'bmi': round(patient.weight / ((patient.height / 100) ** 2), 1) if patient.height and patient.weight else None,
        },
        'allergies': allergies,
        'active_diseases': [d for d in diseases if d.get('status') in ('active', 'chronic')],
        'current_medications': medications,
        'vaccinations': vaccinations,
        'recent_lab_tests': lab_tests,
        'recent_radiology': radiology,
        'medical_history': history.to_dict() if history else {},
    }), 200


# ──────────────────────────────────────────────
# الملخص السريري الشامل (Patient Clinical Summary)
# ──────────────────────────────────────────────
@medical_record_bp.route('/clinical-summary', methods=['GET'])
@token_required
def get_clinical_summary(current_user):
    """
    ملخص سريري شامل يشمل:
    - بيانات المريض
    - الأمراض والتاريخ الجراحي والحساسية
    - الأدوية الحالية
    - التحاليل المكتملة فقط (لها نتائج)
    - الأشعة المكتملة فقط (لها تقارير)
    - زيارات الطبيب المكتملة (مع بيانات الطبيب)
    """
    from src.models.appointment import Appointment
    from src.models.doctor import Doctor
    from datetime import date as dt_date

    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404

    # ── حساب العمر ──
    today = dt_date.today()
    age = None
    if patient.date_of_birth:
        age = today.year - patient.date_of_birth.year - (
            (today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day)
        )

    # ── التحاليل المكتملة فقط (لها قيمة نتيجة) ──
    completed_labs = LabTest.query.filter(
        LabTest.patient_id == patient.id,
        LabTest.result_value.isnot(None),
        LabTest.result_value != ''
    ).order_by(LabTest.test_date.asc()).all()

    # ── الأشعة المكتملة فقط (لها نتائج أو تقرير — وليست فارغة) ──
    completed_radiology = Radiology.query.filter(
        Radiology.patient_id == patient.id,
        db.or_(
            db.and_(Radiology.findings.isnot(None), Radiology.findings != ''),
            db.and_(Radiology.impression.isnot(None), Radiology.impression != ''),
            db.and_(Radiology.report_data.isnot(None), Radiology.report_data != '')
        )
    ).order_by(Radiology.scan_date.asc()).all()

    # ── زيارات الطبيب المكتملة ──
    completed_visits = Appointment.query.filter_by(
        patient_id=patient.id,
        status='completed'
    ).order_by(Appointment.appointment_date.asc()).all()

    visits_data = []
    for appt in completed_visits:
        doc = db.session.get(Doctor, appt.doctor_id)
        d = appt.to_dict()
        d['doctor'] = {
            'id': doc.id,
            'name': f"د. {doc.first_name} {doc.last_name}",
            'specialization': doc.specialization,
            'clinic_name': doc.clinic_name,
        } if doc else None
        visits_data.append(d)

    # ── الأدوية الحالية (نشطة) ──
    current_meds = Medication.query.filter_by(
        patient_id=patient.id,
        is_active=True
    ).order_by(Medication.start_date.desc()).all()

    patient_dict = patient.to_dict()
    patient_dict['age'] = age

    return jsonify({
        'patient': patient_dict,
        'diseases': [d.to_dict() for d in Disease.query.filter_by(patient_id=patient.id).order_by(Disease.diagnosis_date.desc()).all()],
        'surgeries': [s.to_dict() for s in Surgery.query.filter_by(patient_id=patient.id).order_by(Surgery.surgery_date.desc()).all()],
        'allergies': [a.to_dict() for a in Allergy.query.filter_by(patient_id=patient.id).all()],
        'current_medications': [m.to_dict() for m in current_meds],
        'lab_tests': [l.to_dict() for l in completed_labs],
        'radiology': [r.to_dict() for r in completed_radiology],
        'visits': visits_data,
    }), 200


# ──────────────────────────────────────────────
# غازات الدم (ABG)
# ──────────────────────────────────────────────
@medical_record_bp.route('/blood-gas', methods=['GET'])
@token_required
def get_blood_gas(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    readings = BloodGasReading.query.filter_by(patient_id=patient.id).order_by(
        BloodGasReading.reading_date.desc(), BloodGasReading.created_at.desc()).all()
    return jsonify([r.to_dict() for r in readings]), 200


@medical_record_bp.route('/blood-gas', methods=['POST'])
@token_required
def add_blood_gas(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    data = request.get_json(silent=True) or {}
    reading = BloodGasReading(
        patient_id=patient.id,
        reading_date=_parse_date(data.get('reading_date')),
        reading_time=data.get('reading_time'),
        mode=data.get('mode'),
        ph=data.get('ph'),
        pco2=data.get('pco2'),
        hco3=data.get('hco3'),
        o2=data.get('o2'),
        spo2=data.get('spo2'),
        k=data.get('k'),
        lactate=data.get('lactate'),
        notes=data.get('notes'),
        attachment_data=data.get('attachment_data'),
    )
    db.session.add(reading)
    db.session.commit()
    return jsonify(reading.to_dict()), 201


@medical_record_bp.route('/blood-gas/<int:rid>', methods=['PUT'])
@token_required
def update_blood_gas(current_user, rid):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    reading = BloodGasReading.query.filter_by(id=rid, patient_id=patient.id).first()
    if not reading:
        return jsonify({'message': 'لم يتم العثور على القراءة'}), 404
    data = request.get_json(silent=True) or {}
    for f in ('reading_time', 'mode', 'ph', 'pco2', 'hco3', 'o2', 'spo2', 'k', 'lactate', 'notes', 'attachment_data'):
        if f in data:
            setattr(reading, f, data[f])
    if 'reading_date' in data:
        reading.reading_date = _parse_date(data['reading_date'])
    db.session.commit()
    return jsonify(reading.to_dict()), 200


@medical_record_bp.route('/blood-gas/<int:rid>', methods=['DELETE'])
@token_required
def delete_blood_gas(current_user, rid):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    reading = BloodGasReading.query.filter_by(id=rid, patient_id=patient.id).first()
    if not reading:
        return jsonify({'message': 'لم يتم العثور على القراءة'}), 404
    db.session.delete(reading)
    db.session.commit()
    return jsonify({'message': 'تم الحذف'}), 200


# ──────────────────────────────────────────────
# رسومات القلب (ECG)
# ──────────────────────────────────────────────
@medical_record_bp.route('/ecg', methods=['GET'])
@token_required
def get_ecg(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    records = ECGRecord.query.filter_by(patient_id=patient.id).order_by(ECGRecord.ecg_date.desc()).all()
    return jsonify([r.to_dict() for r in records]), 200


@medical_record_bp.route('/ecg', methods=['POST'])
@token_required
def add_ecg(current_user):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    data = request.get_json(silent=True) or {}
    record = ECGRecord(
        patient_id=patient.id,
        ecg_date=_parse_date(data.get('ecg_date')),
        facility=data.get('facility'),
        ordering_doctor=data.get('ordering_doctor'),
        findings=data.get('findings'),
        notes=data.get('notes'),
        attachment_data=data.get('attachment_data'),
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201


@medical_record_bp.route('/ecg/<int:rid>', methods=['PUT'])
@token_required
def update_ecg(current_user, rid):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    record = ECGRecord.query.filter_by(id=rid, patient_id=patient.id).first()
    if not record:
        return jsonify({'message': 'لم يتم العثور على السجل'}), 404
    data = request.get_json(silent=True) or {}
    for f in ('facility', 'ordering_doctor', 'findings', 'notes', 'attachment_data'):
        if f in data:
            setattr(record, f, data[f])
    if 'ecg_date' in data:
        record.ecg_date = _parse_date(data['ecg_date'])
    db.session.commit()
    return jsonify(record.to_dict()), 200


@medical_record_bp.route('/ecg/<int:rid>', methods=['DELETE'])
@token_required
def delete_ecg(current_user, rid):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    record = ECGRecord.query.filter_by(id=rid, patient_id=patient.id).first()
    if not record:
        return jsonify({'message': 'لم يتم العثور على السجل'}), 404
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': 'تم الحذف'}), 200


# ──────────────────────────────────────────────
# تقرير طبي عام (public - للـ QR code)
# ──────────────────────────────────────────────
@medical_record_bp.route('/public/<string:token>', methods=['GET'])
def get_public_report(token):
    """تقرير طبي للقراءة فقط عبر رمز QR — بدون تسجيل دخول."""
    import hmac, hashlib, os
    secret = os.environ.get('SESSION_SECRET', 'sehaty-secret')
    # token = patient_id:signature
    try:
        parts = token.split(':')
        if len(parts) != 2:
            return jsonify({'message': 'رابط غير صالح'}), 400
        pid_str, sig = parts
        expected = hmac.new(secret.encode(), pid_str.encode(), hashlib.sha256).hexdigest()[:16]
        if not hmac.compare_digest(sig, expected):
            return jsonify({'message': 'رابط غير صالح'}), 403
        patient_id = int(pid_str)
    except Exception:
        return jsonify({'message': 'رابط غير صالح'}), 400

    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'message': 'لم يتم العثور على الملف'}), 404

    # رمز QR عام محدود عمداً: لا يعرض أي تشخيص أو دواء أو نتيجة طبية.
    return jsonify({
        'generated_at': datetime.utcnow().isoformat(),
        'patient': {
            'name': f'{patient.first_name} {patient.last_name}',
        },
    }), 200


@medical_record_bp.route('/public-token', methods=['GET'])
@token_required
def get_public_token(current_user):
    """توليد رمز عام للـ QR code."""
    import hmac, hashlib, os
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404
    secret = os.environ.get('SESSION_SECRET', 'sehaty-secret')
    sig = hmac.new(secret.encode(), str(patient.id).encode(), hashlib.sha256).hexdigest()[:16]
    token = f'{patient.id}:{sig}'
    return jsonify({'token': token, 'patient_id': patient.id}), 200


@medical_record_bp.route('/visits/<int:appointment_id>', methods=['GET'])
@token_required
def get_visit_encounter(current_user, appointment_id):
    """تفاصيل الزيارة الكاملة (Encounter) عند النقر على زيارة محددة."""
    from src.models.appointment import Appointment
    from src.models.doctor import Doctor
    from src.models.patient import MedicalRecord
    from datetime import timedelta

    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        return jsonify({'message': 'لم يتم العثور على ملف المريض'}), 404

    appt = Appointment.query.filter_by(id=appointment_id, patient_id=patient.id).first()
    if not appt:
        return jsonify({'message': 'لم يتم العثور على الموعد'}), 404

    doc = db.session.get(Doctor, appt.doctor_id)

    # ── البحث عن السجل الطبي المرتبط (أقرب تاريخ) ──
    medical_record = None
    if doc and appt.appointment_date:
        appt_date = appt.appointment_date
        medical_record = MedicalRecord.query.filter(
            MedicalRecord.patient_id == patient.id,
            MedicalRecord.doctor_id == appt.doctor_id,
            MedicalRecord.visit_date >= appt_date - timedelta(days=2),
            MedicalRecord.visit_date <= appt_date + timedelta(days=2),
        ).order_by(MedicalRecord.visit_date.asc()).first()

    result = appt.to_dict()
    result['doctor'] = {
        'id': doc.id,
        'name': f"د. {doc.first_name} {doc.last_name}",
        'specialization': doc.specialization,
        'sub_specialization': doc.sub_specialization,
        'clinic_name': doc.clinic_name,
        'hospital_affiliation': doc.hospital_affiliation,
        'license_number': doc.license_number,
    } if doc else None
    result['medical_record'] = medical_record.to_dict() if medical_record else None

    return jsonify(result), 200
