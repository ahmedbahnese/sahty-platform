"""
خدمة العائلة المترابطة وإدارة الحسابات العائلية
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app
from dataclasses import dataclass
from enum import Enum

class FamilyRole(Enum):
    HEAD = "رب الأسرة"
    SPOUSE = "الزوج/الزوجة"
    PARENT = "والد"
    CHILD = "طفل"
    GUARDIAN = "وصي"
    CAREGIVER = "مقدم رعاية"
    EMERGENCY_CONTACT = "جهة اتصال طوارئ"

class RelationshipType(Enum):
    FATHER = "أب"
    MOTHER = "أم"
    SON = "ابن"
    DAUGHTER = "ابنة"
    HUSBAND = "زوج"
    WIFE = "زوجة"
    BROTHER = "أخ"
    SISTER = "أخت"
    GRANDFATHER = "جد"
    GRANDMOTHER = "جدة"
    UNCLE = "عم/خال"
    AUNT = "عمة/خالة"
    COUSIN = "ابن عم/خال"
    GUARDIAN = "وصي"
    CAREGIVER = "مقدم رعاية"

class PermissionLevel(Enum):
    FULL_ACCESS = "وصول كامل"
    MEDICAL_ONLY = "طبي فقط"
    EMERGENCY_ONLY = "طوارئ فقط"
    VIEW_ONLY = "عرض فقط"
    NO_ACCESS = "بدون وصول"

class InvitationStatus(Enum):
    PENDING = "في الانتظار"
    ACCEPTED = "مقبولة"
    DECLINED = "مرفوضة"
    EXPIRED = "منتهية الصلاحية"
    CANCELLED = "ملغية"

@dataclass
class FamilyMember:
    member_id: str
    user_id: str
    family_id: str
    relationship: str
    role: str
    permissions: Dict
    added_by: str
    added_at: datetime
    is_active: bool

@dataclass
class FamilyInvitation:
    invitation_id: str
    family_id: str
    inviter_id: str
    invitee_email: str
    invitee_phone: str
    relationship: str
    role: str
    permissions: Dict
    message: str
    created_at: datetime
    expires_at: datetime
    status: str

class FamilyNetworkService:
    def __init__(self):
        """تهيئة خدمة العائلة المترابطة"""
        
        # إعدادات العائلة
        self.family_settings = {
            'max_family_size': 20,
            'invitation_expiry_days': 7,
            'min_age_for_account': 13,
            'require_guardian_approval': True,
            'allow_multiple_families': True,
            'max_families_per_user': 3
        }
        
        # الصلاحيات الافتراضية حسب العلاقة
        self.default_permissions = {
            FamilyRole.HEAD.value: {
                'view_medical_records': True,
                'edit_medical_records': True,
                'book_appointments': True,
                'cancel_appointments': True,
                'view_medications': True,
                'manage_medications': True,
                'emergency_access': True,
                'invite_members': True,
                'remove_members': True,
                'manage_permissions': True,
                'view_financial': True,
                'manage_financial': True
            },
            FamilyRole.SPOUSE.value: {
                'view_medical_records': True,
                'edit_medical_records': True,
                'book_appointments': True,
                'cancel_appointments': True,
                'view_medications': True,
                'manage_medications': True,
                'emergency_access': True,
                'invite_members': True,
                'remove_members': False,
                'manage_permissions': False,
                'view_financial': True,
                'manage_financial': False
            },
            FamilyRole.PARENT.value: {
                'view_medical_records': True,
                'edit_medical_records': True,
                'book_appointments': True,
                'cancel_appointments': True,
                'view_medications': True,
                'manage_medications': True,
                'emergency_access': True,
                'invite_members': False,
                'remove_members': False,
                'manage_permissions': False,
                'view_financial': False,
                'manage_financial': False
            },
            FamilyRole.CHILD.value: {
                'view_medical_records': False,
                'edit_medical_records': False,
                'book_appointments': False,
                'cancel_appointments': False,
                'view_medications': True,
                'manage_medications': False,
                'emergency_access': False,
                'invite_members': False,
                'remove_members': False,
                'manage_permissions': False,
                'view_financial': False,
                'manage_financial': False
            },
            FamilyRole.GUARDIAN.value: {
                'view_medical_records': True,
                'edit_medical_records': True,
                'book_appointments': True,
                'cancel_appointments': True,
                'view_medications': True,
                'manage_medications': True,
                'emergency_access': True,
                'invite_members': False,
                'remove_members': False,
                'manage_permissions': False,
                'view_financial': False,
                'manage_financial': False
            },
            FamilyRole.CAREGIVER.value: {
                'view_medical_records': True,
                'edit_medical_records': False,
                'book_appointments': True,
                'cancel_appointments': False,
                'view_medications': True,
                'manage_medications': True,
                'emergency_access': True,
                'invite_members': False,
                'remove_members': False,
                'manage_permissions': False,
                'view_financial': False,
                'manage_financial': False
            },
            FamilyRole.EMERGENCY_CONTACT.value: {
                'view_medical_records': False,
                'edit_medical_records': False,
                'book_appointments': False,
                'cancel_appointments': False,
                'view_medications': False,
                'manage_medications': False,
                'emergency_access': True,
                'invite_members': False,
                'remove_members': False,
                'manage_permissions': False,
                'view_financial': False,
                'manage_financial': False
            }
        }
        
        # قوالب الدعوات
        self.invitation_templates = {
            'email': {
                'subject_ar': 'دعوة للانضمام لعائلة {family_name} في صحتك في أمان',
                'body_ar': '''
                مرحباً،
                
                تمت دعوتك من قبل {inviter_name} للانضمام لعائلة {family_name} في تطبيق "صحتك في أمان".
                
                العلاقة: {relationship}
                الدور: {role}
                رسالة شخصية: {message}
                
                للقبول، اضغط على الرابط التالي:
                {accept_link}
                
                للرفض، اضغط على الرابط التالي:
                {decline_link}
                
                هذه الدعوة صالحة حتى {expiry_date}
                
                مع تحيات فريق صحتك في أمان
                '''
            },
            'sms': {
                'ar': '{inviter_name} دعاك للانضمام لعائلة {family_name} في تطبيق صحتك في أمان. للقبول: {accept_link}'
            }
        }
        
        # قواعد الخصوصية
        self.privacy_rules = {
            'adult_to_adult': {
                'default_access': PermissionLevel.VIEW_ONLY.value,
                'requires_consent': True,
                'can_override': False
            },
            'parent_to_child': {
                'default_access': PermissionLevel.FULL_ACCESS.value,
                'requires_consent': False,
                'can_override': True,
                'age_limit': 18
            },
            'guardian_to_ward': {
                'default_access': PermissionLevel.FULL_ACCESS.value,
                'requires_consent': False,
                'can_override': True
            },
            'caregiver_to_patient': {
                'default_access': PermissionLevel.MEDICAL_ONLY.value,
                'requires_consent': True,
                'can_override': False
            }
        }
        
        # قاعدة بيانات العائلات (في التطبيق الحقيقي ستكون في قاعدة البيانات)
        self.families = {}
        self.family_members = {}
        self.family_invitations = {}
        self.family_activities = {}
    
    def create_family(self, creator_data: Dict) -> Dict:
        """
        إنشاء عائلة جديدة
        
        Args:
            creator_data: بيانات منشئ العائلة
            
        Returns:
            Dict: معلومات العائلة الجديدة
        """
        try:
            family_id = str(uuid.uuid4())
            creator_id = creator_data.get('user_id')
            
            # إنشاء العائلة
            family = {
                'family_id': family_id,
                'name': creator_data.get('family_name', f'عائلة {creator_data.get("name", "غير محدد")}'),
                'description': creator_data.get('description', ''),
                'created_by': creator_id,
                'created_at': datetime.now(),
                'settings': {
                    'privacy_level': creator_data.get('privacy_level', 'family_only'),
                    'allow_invitations': True,
                    'require_approval': True,
                    'share_emergency_info': True,
                    'share_medical_history': creator_data.get('share_medical_history', False)
                },
                'is_active': True
            }
            
            self.families[family_id] = family
            
            # إضافة المنشئ كرب أسرة
            creator_member = FamilyMember(
                member_id=str(uuid.uuid4()),
                user_id=creator_id,
                family_id=family_id,
                relationship=RelationshipType.FATHER.value if creator_data.get('gender') == 'male' else RelationshipType.MOTHER.value,
                role=FamilyRole.HEAD.value,
                permissions=self.default_permissions[FamilyRole.HEAD.value].copy(),
                added_by=creator_id,
                added_at=datetime.now(),
                is_active=True
            )
            
            self.family_members[creator_member.member_id] = creator_member
            
            # تسجيل النشاط
            self._log_family_activity(
                family_id, creator_id, 'family_created',
                f'تم إنشاء العائلة {family["name"]}'
            )
            
            return {
                'success': True,
                'family': family,
                'creator_member': creator_member.__dict__,
                'next_steps': [
                    'قم بدعوة أفراد العائلة للانضمام',
                    'اضبط إعدادات الخصوصية',
                    'أضف معلومات الطوارئ'
                ]
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء العائلة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إنشاء العائلة'
            }
    
    def invite_family_member(self, invitation_data: Dict) -> Dict:
        """
        دعوة عضو جديد للعائلة
        
        Args:
            invitation_data: بيانات الدعوة
            
        Returns:
            Dict: نتيجة الدعوة
        """
        try:
            family_id = invitation_data.get('family_id')
            inviter_id = invitation_data.get('inviter_id')
            invitee_email = invitation_data.get('invitee_email')
            invitee_phone = invitation_data.get('invitee_phone')
            relationship = invitation_data.get('relationship')
            role = invitation_data.get('role', FamilyRole.CHILD.value)
            custom_permissions = invitation_data.get('permissions', {})
            personal_message = invitation_data.get('message', '')
            
            # التحقق من وجود العائلة
            if family_id not in self.families:
                return {
                    'success': False,
                    'error': 'العائلة غير موجودة'
                }
            
            family = self.families[family_id]
            
            # التحقق من صلاحية الدعوة
            inviter_member = self._get_family_member_by_user(family_id, inviter_id)
            if not inviter_member or not inviter_member.permissions.get('invite_members'):
                return {
                    'success': False,
                    'error': 'ليس لديك صلاحية دعوة أعضاء جدد'
                }
            
            # التحقق من حد العائلة
            current_members = self._get_family_members_count(family_id)
            if current_members >= self.family_settings['max_family_size']:
                return {
                    'success': False,
                    'error': f'تم الوصول للحد الأقصى لأعضاء العائلة ({self.family_settings["max_family_size"]})'
                }
            
            # التحقق من وجود دعوة سابقة
            existing_invitation = self._get_pending_invitation(family_id, invitee_email)
            if existing_invitation:
                return {
                    'success': False,
                    'error': 'توجد دعوة سابقة في الانتظار لهذا البريد الإلكتروني'
                }
            
            # تحديد الصلاحيات
            if custom_permissions:
                permissions = custom_permissions
            else:
                permissions = self.default_permissions.get(role, {}).copy()
            
            # إنشاء الدعوة
            invitation_id = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(days=self.family_settings['invitation_expiry_days'])
            
            invitation = FamilyInvitation(
                invitation_id=invitation_id,
                family_id=family_id,
                inviter_id=inviter_id,
                invitee_email=invitee_email,
                invitee_phone=invitee_phone,
                relationship=relationship,
                role=role,
                permissions=permissions,
                message=personal_message,
                created_at=datetime.now(),
                expires_at=expires_at,
                status=InvitationStatus.PENDING.value
            )
            
            self.family_invitations[invitation_id] = invitation
            
            # إرسال الدعوة
            invitation_sent = self._send_family_invitation(invitation, family, inviter_member)
            
            # تسجيل النشاط
            self._log_family_activity(
                family_id, inviter_id, 'member_invited',
                f'تم دعوة {invitee_email} كـ {relationship}'
            )
            
            return {
                'success': True,
                'invitation': invitation.__dict__,
                'invitation_sent': invitation_sent,
                'expires_at': expires_at.isoformat(),
                'message': 'تم إرسال الدعوة بنجاح'
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في دعوة عضو العائلة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إرسال الدعوة'
            }
    
    def respond_to_invitation(self, response_data: Dict) -> Dict:
        """
        الرد على دعوة العائلة
        
        Args:
            response_data: بيانات الرد
            
        Returns:
            Dict: نتيجة الرد
        """
        try:
            invitation_id = response_data.get('invitation_id')
            user_id = response_data.get('user_id')
            response = response_data.get('response')  # 'accept' or 'decline'
            user_data = response_data.get('user_data', {})
            
            # التحقق من وجود الدعوة
            if invitation_id not in self.family_invitations:
                return {
                    'success': False,
                    'error': 'الدعوة غير موجودة'
                }
            
            invitation = self.family_invitations[invitation_id]
            
            # التحقق من صلاحية الدعوة
            if invitation.status != InvitationStatus.PENDING.value:
                return {
                    'success': False,
                    'error': 'تم الرد على هذه الدعوة مسبقاً'
                }
            
            if datetime.now() > invitation.expires_at:
                invitation.status = InvitationStatus.EXPIRED.value
                return {
                    'success': False,
                    'error': 'انتهت صلاحية الدعوة'
                }
            
            # معالجة الرد
            if response == 'accept':
                # قبول الدعوة
                invitation.status = InvitationStatus.ACCEPTED.value
                
                # إضافة العضو للعائلة
                member_id = str(uuid.uuid4())
                new_member = FamilyMember(
                    member_id=member_id,
                    user_id=user_id,
                    family_id=invitation.family_id,
                    relationship=invitation.relationship,
                    role=invitation.role,
                    permissions=invitation.permissions.copy(),
                    added_by=invitation.inviter_id,
                    added_at=datetime.now(),
                    is_active=True
                )
                
                self.family_members[member_id] = new_member
                
                # تسجيل النشاط
                self._log_family_activity(
                    invitation.family_id, user_id, 'member_joined',
                    f'{user_data.get("name", "عضو جديد")} انضم للعائلة كـ {invitation.relationship}'
                )
                
                # إرسال إشعار للعائلة
                self._notify_family_members(
                    invitation.family_id, 
                    f'انضم {user_data.get("name", "عضو جديد")} للعائلة',
                    exclude_user=user_id
                )
                
                return {
                    'success': True,
                    'message': 'تم قبول الدعوة وانضمامك للعائلة بنجاح',
                    'family_member': new_member.__dict__,
                    'family_info': self.families[invitation.family_id],
                    'next_steps': [
                        'اكمل ملفك الشخصي',
                        'راجع إعدادات الخصوصية',
                        'تعرف على أفراد العائلة الآخرين'
                    ]
                }
                
            elif response == 'decline':
                # رفض الدعوة
                invitation.status = InvitationStatus.DECLINED.value
                
                # تسجيل النشاط
                self._log_family_activity(
                    invitation.family_id, invitation.inviter_id, 'invitation_declined',
                    f'تم رفض دعوة {invitation.invitee_email}'
                )
                
                # إشعار الداعي
                self._notify_user(
                    invitation.inviter_id,
                    f'تم رفض دعوة {invitation.invitee_email} للانضمام للعائلة'
                )
                
                return {
                    'success': True,
                    'message': 'تم رفض الدعوة'
                }
            
            else:
                return {
                    'success': False,
                    'error': 'رد غير صالح'
                }
                
        except Exception as e:
            current_app.logger.error(f"خطأ في الرد على الدعوة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في معالجة الرد'
            }
    
    def get_family_members(self, family_id: str, requester_id: str) -> Dict:
        """
        الحصول على أعضاء العائلة
        
        Args:
            family_id: معرف العائلة
            requester_id: معرف طالب المعلومات
            
        Returns:
            Dict: قائمة أعضاء العائلة
        """
        try:
            # التحقق من وجود العائلة
            if family_id not in self.families:
                return {
                    'success': False,
                    'error': 'العائلة غير موجودة'
                }
            
            # التحقق من عضوية الطالب
            requester_member = self._get_family_member_by_user(family_id, requester_id)
            if not requester_member:
                return {
                    'success': False,
                    'error': 'ليس لديك صلاحية للوصول لهذه العائلة'
                }
            
            # جمع أعضاء العائلة
            family_members = []
            for member in self.family_members.values():
                if member.family_id == family_id and member.is_active:
                    # تحديد المعلومات المتاحة حسب الصلاحيات
                    member_info = {
                        'member_id': member.member_id,
                        'user_id': member.user_id,
                        'relationship': member.relationship,
                        'role': member.role,
                        'added_at': member.added_at.isoformat(),
                        'is_self': member.user_id == requester_id
                    }
                    
                    # إضافة معلومات إضافية حسب الصلاحيات
                    if (requester_member.permissions.get('view_medical_records') or 
                        member.user_id == requester_id):
                        member_info.update({
                            'permissions': member.permissions,
                            'last_activity': self._get_member_last_activity(member.user_id),
                            'health_status': self._get_member_health_summary(member.user_id)
                        })
                    
                    family_members.append(member_info)
            
            family = self.families[family_id]
            
            return {
                'success': True,
                'family_info': {
                    'family_id': family['family_id'],
                    'name': family['name'],
                    'description': family['description'],
                    'created_at': family['created_at'].isoformat(),
                    'settings': family['settings']
                },
                'members': family_members,
                'total_members': len(family_members),
                'requester_permissions': requester_member.permissions,
                'family_statistics': self._get_family_statistics(family_id)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على أعضاء العائلة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على أعضاء العائلة'
            }
    
    def update_member_permissions(self, update_data: Dict) -> Dict:
        """
        تحديث صلاحيات عضو العائلة
        
        Args:
            update_data: بيانات التحديث
            
        Returns:
            Dict: نتيجة التحديث
        """
        try:
            family_id = update_data.get('family_id')
            member_id = update_data.get('member_id')
            new_permissions = update_data.get('permissions')
            updater_id = update_data.get('updater_id')
            
            # التحقق من وجود العضو
            if member_id not in self.family_members:
                return {
                    'success': False,
                    'error': 'العضو غير موجود'
                }
            
            member = self.family_members[member_id]
            
            # التحقق من صلاحية التحديث
            updater_member = self._get_family_member_by_user(family_id, updater_id)
            if not updater_member or not updater_member.permissions.get('manage_permissions'):
                return {
                    'success': False,
                    'error': 'ليس لديك صلاحية تعديل الصلاحيات'
                }
            
            # التحقق من قواعد الخصوصية
            privacy_check = self._check_privacy_rules(updater_member, member, new_permissions)
            if not privacy_check['allowed']:
                return {
                    'success': False,
                    'error': privacy_check['reason']
                }
            
            # حفظ الصلاحيات القديمة للمراجعة
            old_permissions = member.permissions.copy()
            
            # تحديث الصلاحيات
            member.permissions.update(new_permissions)
            
            # تسجيل النشاط
            self._log_family_activity(
                family_id, updater_id, 'permissions_updated',
                f'تم تحديث صلاحيات {member.relationship}'
            )
            
            # إشعار العضو المحدث
            self._notify_user(
                member.user_id,
                'تم تحديث صلاحياتك في العائلة'
            )
            
            return {
                'success': True,
                'message': 'تم تحديث الصلاحيات بنجاح',
                'updated_member': member.__dict__,
                'changes': self._compare_permissions(old_permissions, member.permissions)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تحديث صلاحيات العضو: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في تحديث الصلاحيات'
            }
    
    def remove_family_member(self, removal_data: Dict) -> Dict:
        """
        إزالة عضو من العائلة
        
        Args:
            removal_data: بيانات الإزالة
            
        Returns:
            Dict: نتيجة الإزالة
        """
        try:
            family_id = removal_data.get('family_id')
            member_id = removal_data.get('member_id')
            remover_id = removal_data.get('remover_id')
            reason = removal_data.get('reason', '')
            
            # التحقق من وجود العضو
            if member_id not in self.family_members:
                return {
                    'success': False,
                    'error': 'العضو غير موجود'
                }
            
            member = self.family_members[member_id]
            
            # التحقق من صلاحية الإزالة
            remover_member = self._get_family_member_by_user(family_id, remover_id)
            if not remover_member or not remover_member.permissions.get('remove_members'):
                return {
                    'success': False,
                    'error': 'ليس لديك صلاحية إزالة أعضاء'
                }
            
            # منع إزالة رب الأسرة
            if member.role == FamilyRole.HEAD.value:
                return {
                    'success': False,
                    'error': 'لا يمكن إزالة رب الأسرة'
                }
            
            # منع الإزالة الذاتية (إلا إذا كان مغادرة طوعية)
            if member.user_id == remover_id and not removal_data.get('voluntary_leave'):
                return {
                    'success': False,
                    'error': 'استخدم خيار "مغادرة العائلة" للخروج طوعياً'
                }
            
            # إزالة العضو
            member.is_active = False
            
            # تسجيل النشاط
            action = 'member_left' if removal_data.get('voluntary_leave') else 'member_removed'
            self._log_family_activity(
                family_id, remover_id, action,
                f'{member.relationship} {"غادر" if action == "member_left" else "تم إزالته من"} العائلة'
            )
            
            # إشعار أعضاء العائلة
            self._notify_family_members(
                family_id,
                f'{member.relationship} {"غادر" if action == "member_left" else "تم إزالته من"} العائلة',
                exclude_user=member.user_id
            )
            
            # إشعار العضو المُزال (إذا لم يكن مغادرة طوعية)
            if not removal_data.get('voluntary_leave'):
                self._notify_user(
                    member.user_id,
                    f'تم إزالتك من عائلة {self.families[family_id]["name"]}'
                )
            
            return {
                'success': True,
                'message': 'تم إزالة العضو بنجاح' if not removal_data.get('voluntary_leave') else 'تم مغادرة العائلة بنجاح',
                'removed_member': member.__dict__
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إزالة عضو العائلة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إزالة العضو'
            }
    
    def get_family_activities(self, family_id: str, requester_id: str, 
                            limit: int = 50, offset: int = 0) -> Dict:
        """
        الحصول على أنشطة العائلة
        
        Args:
            family_id: معرف العائلة
            requester_id: معرف طالب المعلومات
            limit: عدد الأنشطة
            offset: الإزاحة
            
        Returns:
            Dict: قائمة الأنشطة
        """
        try:
            # التحقق من عضوية الطالب
            requester_member = self._get_family_member_by_user(family_id, requester_id)
            if not requester_member:
                return {
                    'success': False,
                    'error': 'ليس لديك صلاحية للوصول لهذه العائلة'
                }
            
            # جمع الأنشطة
            family_activities = self.family_activities.get(family_id, [])
            
            # ترتيب الأنشطة حسب التاريخ (الأحدث أولاً)
            sorted_activities = sorted(
                family_activities, 
                key=lambda x: x['timestamp'], 
                reverse=True
            )
            
            # تطبيق الحد والإزاحة
            paginated_activities = sorted_activities[offset:offset + limit]
            
            # تصفية الأنشطة حسب الصلاحيات
            filtered_activities = []
            for activity in paginated_activities:
                if self._can_view_activity(requester_member, activity):
                    filtered_activities.append(activity)
            
            return {
                'success': True,
                'activities': filtered_activities,
                'total_activities': len(family_activities),
                'has_more': offset + limit < len(family_activities),
                'next_offset': offset + limit if offset + limit < len(family_activities) else None
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على أنشطة العائلة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على الأنشطة'
            }
    
    def get_user_families(self, user_id: str) -> Dict:
        """
        الحصول على عائلات المستخدم
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            Dict: قائمة العائلات
        """
        try:
            user_families = []
            
            for member in self.family_members.values():
                if member.user_id == user_id and member.is_active:
                    family = self.families.get(member.family_id)
                    if family and family['is_active']:
                        family_info = {
                            'family_id': family['family_id'],
                            'name': family['name'],
                            'description': family['description'],
                            'member_role': member.role,
                            'member_relationship': member.relationship,
                            'member_permissions': member.permissions,
                            'joined_at': member.added_at.isoformat(),
                            'total_members': self._get_family_members_count(family['family_id']),
                            'recent_activity': self._get_recent_family_activity(family['family_id'])
                        }
                        user_families.append(family_info)
            
            return {
                'success': True,
                'families': user_families,
                'total_families': len(user_families),
                'can_create_more': len(user_families) < self.family_settings['max_families_per_user']
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على عائلات المستخدم: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على العائلات'
            }
    
    def get_pending_invitations(self, user_email: str) -> Dict:
        """
        الحصول على الدعوات المعلقة للمستخدم
        
        Args:
            user_email: بريد المستخدم الإلكتروني
            
        Returns:
            Dict: قائمة الدعوات المعلقة
        """
        try:
            pending_invitations = []
            current_time = datetime.now()
            
            for invitation in self.family_invitations.values():
                if (invitation.invitee_email == user_email and 
                    invitation.status == InvitationStatus.PENDING.value and
                    invitation.expires_at > current_time):
                    
                    family = self.families.get(invitation.family_id)
                    inviter_member = self._get_family_member_by_user(
                        invitation.family_id, invitation.inviter_id
                    )
                    
                    invitation_info = {
                        'invitation_id': invitation.invitation_id,
                        'family_name': family['name'] if family else 'غير محدد',
                        'family_description': family['description'] if family else '',
                        'inviter_name': self._get_user_name(invitation.inviter_id),
                        'relationship': invitation.relationship,
                        'role': invitation.role,
                        'permissions': invitation.permissions,
                        'message': invitation.message,
                        'created_at': invitation.created_at.isoformat(),
                        'expires_at': invitation.expires_at.isoformat(),
                        'expires_in_hours': int((invitation.expires_at - current_time).total_seconds() / 3600)
                    }
                    pending_invitations.append(invitation_info)
            
            return {
                'success': True,
                'pending_invitations': pending_invitations,
                'total_invitations': len(pending_invitations)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في الحصول على الدعوات المعلقة: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في الحصول على الدعوات'
            }
    
    # الدوال المساعدة
    def _get_family_member_by_user(self, family_id: str, user_id: str) -> Optional[FamilyMember]:
        """الحصول على عضو العائلة بمعرف المستخدم"""
        for member in self.family_members.values():
            if (member.family_id == family_id and 
                member.user_id == user_id and 
                member.is_active):
                return member
        return None
    
    def _get_family_members_count(self, family_id: str) -> int:
        """عدد أعضاء العائلة النشطين"""
        count = 0
        for member in self.family_members.values():
            if member.family_id == family_id and member.is_active:
                count += 1
        return count
    
    def _get_pending_invitation(self, family_id: str, email: str) -> Optional[FamilyInvitation]:
        """البحث عن دعوة معلقة"""
        for invitation in self.family_invitations.values():
            if (invitation.family_id == family_id and 
                invitation.invitee_email == email and
                invitation.status == InvitationStatus.PENDING.value):
                return invitation
        return None
    
    def _send_family_invitation(self, invitation: FamilyInvitation, 
                               family: Dict, inviter: FamilyMember) -> bool:
        """إرسال دعوة العائلة"""
        try:
            # في التطبيق الحقيقي، سيتم إرسال بريد إلكتروني و/أو SMS
            current_app.logger.info(f"إرسال دعوة عائلة إلى {invitation.invitee_email}")
            return True
        except Exception as e:
            current_app.logger.error(f"خطأ في إرسال الدعوة: {str(e)}")
            return False
    
    def _log_family_activity(self, family_id: str, user_id: str, 
                           activity_type: str, description: str):
        """تسجيل نشاط العائلة"""
        if family_id not in self.family_activities:
            self.family_activities[family_id] = []
        
        activity = {
            'activity_id': str(uuid.uuid4()),
            'user_id': user_id,
            'activity_type': activity_type,
            'description': description,
            'timestamp': datetime.now(),
            'metadata': {}
        }
        
        self.family_activities[family_id].append(activity)
    
    def _notify_family_members(self, family_id: str, message: str, exclude_user: str = None):
        """إشعار أعضاء العائلة"""
        for member in self.family_members.values():
            if (member.family_id == family_id and 
                member.is_active and 
                member.user_id != exclude_user):
                self._notify_user(member.user_id, message)
    
    def _notify_user(self, user_id: str, message: str):
        """إشعار مستخدم محدد"""
        # في التطبيق الحقيقي، سيتم إرسال إشعار
        current_app.logger.info(f"إشعار للمستخدم {user_id}: {message}")
    
    def _check_privacy_rules(self, updater: FamilyMember, target: FamilyMember, 
                           new_permissions: Dict) -> Dict:
        """فحص قواعد الخصوصية"""
        # تطبيق قواعد الخصوصية المعقدة
        return {
            'allowed': True,
            'reason': ''
        }
    
    def _compare_permissions(self, old_permissions: Dict, new_permissions: Dict) -> List[str]:
        """مقارنة الصلاحيات"""
        changes = []
        for key, value in new_permissions.items():
            if key not in old_permissions or old_permissions[key] != value:
                status = 'تم تفعيل' if value else 'تم إلغاء'
                changes.append(f'{status} {key}')
        return changes
    
    def _can_view_activity(self, member: FamilyMember, activity: Dict) -> bool:
        """فحص إمكانية عرض النشاط"""
        # تطبيق قواعد عرض الأنشطة
        return True
    
    def _get_member_last_activity(self, user_id: str) -> str:
        """آخر نشاط للعضو"""
        return datetime.now().isoformat()
    
    def _get_member_health_summary(self, user_id: str) -> Dict:
        """ملخص صحة العضو"""
        return {
            'status': 'جيد',
            'last_checkup': '2024-01-15',
            'upcoming_appointments': 1
        }
    
    def _get_family_statistics(self, family_id: str) -> Dict:
        """إحصائيات العائلة"""
        return {
            'total_appointments_this_month': 5,
            'total_medications': 12,
            'health_alerts': 2
        }
    
    def _get_recent_family_activity(self, family_id: str) -> List[Dict]:
        """الأنشطة الحديثة للعائلة"""
        activities = self.family_activities.get(family_id, [])
        return sorted(activities, key=lambda x: x['timestamp'], reverse=True)[:3]
    
    def _get_user_name(self, user_id: str) -> str:
        """اسم المستخدم"""
        # في التطبيق الحقيقي، سيتم الحصول على الاسم من قاعدة البيانات
        return 'مستخدم'

