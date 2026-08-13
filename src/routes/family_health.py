"""
مسارات Family Health Manager
"""

import json
from datetime import datetime, date

from flask import Blueprint, request, jsonify
from src.routes.auth import token_required
from src.models.user import db
from src.models.family_health import FamilyGroup, FamilyMember, FamilyMemberHealthRecord, FamilyHealthGoal
from src.services.ai_service import AIService

family_bp = Blueprint('family', __name__, url_prefix='/api/family')

_ai_service = None
def get_ai_service():
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service


# ─────────────────────────────────────────
# مجموعات الأسرة
# ─────────────────────────────────────────
@family_bp.route('/groups', methods=['GET'])
@token_required
def get_groups(current_user):
    """جلب مجموعات الأسرة للمستخدم"""
    groups = FamilyGroup.query.filter_by(owner_user_id=current_user.id).all()
    return jsonify({'success': True, 'groups': [g.to_dict() for g in groups]})


@family_bp.route('/groups', methods=['POST'])
@token_required
def create_group(current_user):
    """إنشاء مجموعة أسرة جديدة"""
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'success': False, 'error': 'اسم المجموعة مطلوب'}), 400

    group = FamilyGroup(
        name=data['name'],
        owner_user_id=current_user.id,
        description=data.get('description', '')
    )
    db.session.add(group)
    db.session.commit()
    return jsonify({'success': True, 'group': group.to_dict()}), 201


@family_bp.route('/groups/<int:group_id>', methods=['GET'])
@token_required
def get_group(current_user, group_id):
    group = FamilyGroup.query.filter_by(id=group_id, owner_user_id=current_user.id).first()
    if not group:
        return jsonify({'success': False, 'error': 'المجموعة غير موجودة'}), 404
    members = [m.to_dict() for m in FamilyMember.query.filter_by(group_id=group_id, is_active=True).all()]
    goals = [g.to_dict() for g in FamilyHealthGoal.query.filter_by(group_id=group_id).all()]
    return jsonify({'success': True, 'group': group.to_dict(), 'members': members, 'goals': goals})


@family_bp.route('/groups/<int:group_id>', methods=['PUT'])
@token_required
def update_group(current_user, group_id):
    group = FamilyGroup.query.filter_by(id=group_id, owner_user_id=current_user.id).first()
    if not group:
        return jsonify({'success': False, 'error': 'المجموعة غير موجودة'}), 404
    data = request.get_json()
    if data.get('name'):
        group.name = data['name']
    if 'description' in data:
        group.description = data['description']
    group.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'group': group.to_dict()})


@family_bp.route('/groups/<int:group_id>', methods=['DELETE'])
@token_required
def delete_group(current_user, group_id):
    group = FamilyGroup.query.filter_by(id=group_id, owner_user_id=current_user.id).first()
    if not group:
        return jsonify({'success': False, 'error': 'المجموعة غير موجودة'}), 404
    db.session.delete(group)
    db.session.commit()
    return jsonify({'success': True, 'message': 'تم حذف المجموعة'})


# ─────────────────────────────────────────
# أفراد الأسرة
# ─────────────────────────────────────────
@family_bp.route('/groups/<int:group_id>/members', methods=['GET'])
@token_required
def get_members(current_user, group_id):
    group = FamilyGroup.query.filter_by(id=group_id, owner_user_id=current_user.id).first()
    if not group:
        return jsonify({'success': False, 'error': 'المجموعة غير موجودة'}), 404
    members = FamilyMember.query.filter_by(group_id=group_id, is_active=True).all()
    return jsonify({'success': True, 'members': [m.to_dict() for m in members]})


@family_bp.route('/groups/<int:group_id>/members', methods=['POST'])
@token_required
def add_member(current_user, group_id):
    group = FamilyGroup.query.filter_by(id=group_id, owner_user_id=current_user.id).first()
    if not group:
        return jsonify({'success': False, 'error': 'المجموعة غير موجودة'}), 404

    data = request.get_json()
    required = ['first_name', 'last_name', 'relationship']
    for field in required:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'الحقل {field} مطلوب'}), 400

    dob = None
    if data.get('date_of_birth'):
        try:
            dob = date.fromisoformat(data['date_of_birth'])
        except ValueError:
            pass

    member = FamilyMember(
        group_id=group_id,
        first_name=data['first_name'],
        last_name=data['last_name'],
        relationship=data['relationship'],
        date_of_birth=dob,
        gender=data.get('gender'),
        blood_type=data.get('blood_type'),
        phone=data.get('phone'),
        chronic_diseases=json.dumps(data.get('chronic_diseases', []), ensure_ascii=False),
        allergies=json.dumps(data.get('allergies', []), ensure_ascii=False),
        current_medications=json.dumps(data.get('current_medications', []), ensure_ascii=False),
        notes=data.get('notes', '')
    )
    db.session.add(member)
    db.session.commit()
    return jsonify({'success': True, 'member': member.to_dict()}), 201


@family_bp.route('/members/<int:member_id>', methods=['GET'])
@token_required
def get_member(current_user, member_id):
    member = _get_member_or_404(current_user, member_id)
    if isinstance(member, tuple):
        return member
    records = [r.to_dict() for r in FamilyMemberHealthRecord.query.filter_by(member_id=member_id).order_by(
        FamilyMemberHealthRecord.date.desc()).all()]
    return jsonify({'success': True, 'member': member.to_dict(), 'records': records})


@family_bp.route('/members/<int:member_id>', methods=['PUT'])
@token_required
def update_member(current_user, member_id):
    member = _get_member_or_404(current_user, member_id)
    if isinstance(member, tuple):
        return member

    data = request.get_json()
    for field in ['first_name', 'last_name', 'relationship', 'gender', 'blood_type', 'phone', 'notes']:
        if field in data:
            setattr(member, field, data[field])

    if 'date_of_birth' in data and data['date_of_birth']:
        try:
            member.date_of_birth = date.fromisoformat(data['date_of_birth'])
        except ValueError:
            pass

    for json_field in ['chronic_diseases', 'allergies', 'current_medications']:
        if json_field in data:
            setattr(member, json_field, json.dumps(data[json_field], ensure_ascii=False))

    member.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'member': member.to_dict()})


@family_bp.route('/members/<int:member_id>', methods=['DELETE'])
@token_required
def delete_member(current_user, member_id):
    member = _get_member_or_404(current_user, member_id)
    if isinstance(member, tuple):
        return member
    member.is_active = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'تم حذف الفرد'})


# ─────────────────────────────────────────
# سجلات صحية لأفراد الأسرة
# ─────────────────────────────────────────
@family_bp.route('/members/<int:member_id>/records', methods=['GET'])
@token_required
def get_member_records(current_user, member_id):
    member = _get_member_or_404(current_user, member_id)
    if isinstance(member, tuple):
        return member
    records = FamilyMemberHealthRecord.query.filter_by(member_id=member_id).order_by(
        FamilyMemberHealthRecord.date.desc()).all()
    return jsonify({'success': True, 'records': [r.to_dict() for r in records]})


@family_bp.route('/members/<int:member_id>/records', methods=['POST'])
@token_required
def add_member_record(current_user, member_id):
    member = _get_member_or_404(current_user, member_id)
    if isinstance(member, tuple):
        return member

    data = request.get_json()
    if not data.get('record_type') or not data.get('title') or not data.get('date'):
        return jsonify({'success': False, 'error': 'النوع والعنوان والتاريخ مطلوبة'}), 400

    try:
        rec_date = date.fromisoformat(data['date'])
    except ValueError:
        return jsonify({'success': False, 'error': 'تنسيق التاريخ غير صحيح'}), 400

    next_due = None
    if data.get('next_due_date'):
        try:
            next_due = date.fromisoformat(data['next_due_date'])
        except ValueError:
            pass

    record = FamilyMemberHealthRecord(
        member_id=member_id,
        record_type=data['record_type'],
        title=data['title'],
        description=data.get('description'),
        date=rec_date,
        next_due_date=next_due,
        result=data.get('result'),
        doctor_name=data.get('doctor_name'),
        hospital_name=data.get('hospital_name')
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({'success': True, 'record': record.to_dict()}), 201


@family_bp.route('/members/<int:member_id>/records/<int:record_id>', methods=['PUT'])
@token_required
def update_member_record(current_user, member_id, record_id):
    member = _get_member_or_404(current_user, member_id)
    if isinstance(member, tuple):
        return member
    record = FamilyMemberHealthRecord.query.filter_by(
        id=record_id, member_id=member_id
    ).first()
    if not record:
        return jsonify({'success': False, 'error': 'السجل غير موجود'}), 404

    data = request.get_json() or {}
    for field in ('record_type', 'title', 'description', 'result', 'doctor_name', 'hospital_name'):
        if field in data:
            setattr(record, field, data[field])
    for field in ('date', 'next_due_date'):
        if field in data:
            value = data[field]
            if value:
                try:
                    setattr(record, field, date.fromisoformat(value))
                except ValueError:
                    return jsonify({'success': False, 'error': 'تنسيق التاريخ غير صحيح'}), 400
            elif field == 'next_due_date':
                record.next_due_date = None
    db.session.commit()
    return jsonify({'success': True, 'record': record.to_dict()})


@family_bp.route('/members/<int:member_id>/records/<int:record_id>', methods=['DELETE'])
@token_required
def delete_member_record(current_user, member_id, record_id):
    member = _get_member_or_404(current_user, member_id)
    if isinstance(member, tuple):
        return member
    record = FamilyMemberHealthRecord.query.filter_by(
        id=record_id, member_id=member_id
    ).first()
    if not record:
        return jsonify({'success': False, 'error': 'السجل غير موجود'}), 404
    db.session.delete(record)
    db.session.commit()
    return jsonify({'success': True, 'message': 'تم حذف السجل'})


@family_bp.route('/members/<int:member_id>/report', methods=['GET'])
@token_required
def get_member_report(current_user, member_id):
    """تقرير شامل مبسط لفرد الأسرة، مع التحقق من ملكية المجموعة."""
    member = _get_member_or_404(current_user, member_id)
    if isinstance(member, tuple):
        return member
    records = FamilyMemberHealthRecord.query.filter_by(
        member_id=member_id
    ).order_by(FamilyMemberHealthRecord.date.desc()).all()
    return jsonify({
        'success': True,
        'member': member.to_dict(),
        'records': [record.to_dict() for record in records],
        'generated_at': datetime.utcnow().isoformat(),
    })


# ─────────────────────────────────────────
# أهداف صحية
# ─────────────────────────────────────────
@family_bp.route('/groups/<int:group_id>/goals', methods=['GET'])
@token_required
def get_goals(current_user, group_id):
    group = FamilyGroup.query.filter_by(id=group_id, owner_user_id=current_user.id).first()
    if not group:
        return jsonify({'success': False, 'error': 'المجموعة غير موجودة'}), 404
    goals = FamilyHealthGoal.query.filter_by(group_id=group_id).all()
    return jsonify({'success': True, 'goals': [g.to_dict() for g in goals]})


@family_bp.route('/groups/<int:group_id>/goals', methods=['POST'])
@token_required
def add_goal(current_user, group_id):
    group = FamilyGroup.query.filter_by(id=group_id, owner_user_id=current_user.id).first()
    if not group:
        return jsonify({'success': False, 'error': 'المجموعة غير موجودة'}), 404

    data = request.get_json()
    if not data.get('title'):
        return jsonify({'success': False, 'error': 'العنوان مطلوب'}), 400

    target_date = None
    if data.get('target_date'):
        try:
            target_date = date.fromisoformat(data['target_date'])
        except ValueError:
            pass

    goal = FamilyHealthGoal(
        group_id=group_id,
        member_id=data.get('member_id'),
        title=data['title'],
        description=data.get('description'),
        target_date=target_date
    )
    db.session.add(goal)
    db.session.commit()
    return jsonify({'success': True, 'goal': goal.to_dict()}), 201


@family_bp.route('/goals/<int:goal_id>/progress', methods=['PUT'])
@token_required
def update_goal_progress(current_user, goal_id):
    goal = FamilyHealthGoal.query.get(goal_id)
    if not goal:
        return jsonify({'success': False, 'error': 'الهدف غير موجود'}), 404

    # تحقق من الملكية
    group = FamilyGroup.query.filter_by(id=goal.group_id, owner_user_id=current_user.id).first()
    if not group:
        return jsonify({'success': False, 'error': 'غير مصرح'}), 403

    data = request.get_json()
    if 'progress' in data:
        goal.progress = max(0, min(100, int(data['progress'])))
    if 'status' in data:
        goal.status = data['status']
    goal.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'goal': goal.to_dict()})


# ─────────────────────────────────────────
# تحليل AI لصحة الأسرة
# ─────────────────────────────────────────
@family_bp.route('/groups/<int:group_id>/ai-analysis', methods=['GET'])
@token_required
def family_ai_analysis(current_user, group_id):
    """تحليل ذكي لصحة الأسرة"""
    group = FamilyGroup.query.filter_by(id=group_id, owner_user_id=current_user.id).first()
    if not group:
        return jsonify({'success': False, 'error': 'المجموعة غير موجودة'}), 404

    members = FamilyMember.query.filter_by(group_id=group_id, is_active=True).all()
    if not members:
        return jsonify({'success': False, 'error': 'لا يوجد أفراد في المجموعة'}), 400

    family_data = [m.to_dict() for m in members]
    result = get_ai_service().analyze_family_health(family_data)
    return jsonify(result)


# ─────────────────────────────────────────
# helper
# ─────────────────────────────────────────
def _get_member_or_404(current_user, member_id):
    member = FamilyMember.query.get(member_id)
    if not member:
        return jsonify({'success': False, 'error': 'الفرد غير موجود'}), 404
    group = FamilyGroup.query.filter_by(id=member.group_id, owner_user_id=current_user.id).first()
    if not group:
        return jsonify({'success': False, 'error': 'غير مصرح'}), 403
    return member
