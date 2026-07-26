from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class SystemOwner(db.Model):
    __tablename__ = 'system_owners'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # معلومات المالك
    full_name = db.Column(db.String(200), nullable=False, default='أحمد حامد أحمد بهنسي')
    phone = db.Column(db.String(20), nullable=False, default='01063299450')
    email = db.Column(db.String(120), nullable=False, default='Ahmedbahnese@yahoo.com')
    location = db.Column(db.String(200), default='الإسكندرية، مصر')
    facebook_profile = db.Column(db.String(500), default='https://www.facebook.com/share/1Ei7ZKXFi6/?mibextid=wwXIfr')
    
    # معلومات النظام
    system_name = db.Column(db.String(100), default='صحتك في أمان')
    system_version = db.Column(db.String(20), default='1.0.0')
    
    # صلاحيات المالك
    has_full_access = db.Column(db.Boolean, default=True)
    can_manage_admins = db.Column(db.Boolean, default=True)
    can_manage_system = db.Column(db.Boolean, default=True)
    can_view_analytics = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'phone': self.phone,
            'email': self.email,
            'location': self.location,
            'facebook_profile': self.facebook_profile,
            'system_name': self.system_name,
            'system_version': self.system_version,
            'has_full_access': self.has_full_access,
            'can_manage_admins': self.can_manage_admins,
            'can_manage_system': self.can_manage_system,
            'can_view_analytics': self.can_view_analytics,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # معلومات شخصية
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    
    # نوع المدير
    admin_type = db.Column(db.String(50), nullable=False)  # super_admin, system_admin, content_admin, support_admin
    department = db.Column(db.String(100))
    
    # الصلاحيات
    permissions = db.Column(db.JSON)  # JSON object with detailed permissions
    
    # معلومات الوصول
    can_access_dashboard = db.Column(db.Boolean, default=True)
    can_manage_users = db.Column(db.Boolean, default=False)
    can_manage_doctors = db.Column(db.Boolean, default=False)
    can_manage_hospitals = db.Column(db.Boolean, default=False)
    can_manage_content = db.Column(db.Boolean, default=False)
    can_view_reports = db.Column(db.Boolean, default=False)
    can_manage_system_settings = db.Column(db.Boolean, default=False)
    
    # حالة الحساب
    is_active = db.Column(db.Boolean, default=True)
    is_super_admin = db.Column(db.Boolean, default=False)
    
    # معلومات الجلسة
    last_login = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'email': self.email,
            'admin_type': self.admin_type,
            'department': self.department,
            'permissions': self.permissions,
            'can_access_dashboard': self.can_access_dashboard,
            'can_manage_users': self.can_manage_users,
            'can_manage_doctors': self.can_manage_doctors,
            'can_manage_hospitals': self.can_manage_hospitals,
            'can_manage_content': self.can_manage_content,
            'can_view_reports': self.can_view_reports,
            'can_manage_system_settings': self.can_manage_system_settings,
            'is_active': self.is_active,
            'is_super_admin': self.is_super_admin,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'login_count': self.login_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SystemSettings(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # إعدادات عامة
    site_name = db.Column(db.String(100), default='صحتك في أمان')
    site_description = db.Column(db.Text, default='منصة طبية شاملة للرعاية الصحية')
    site_logo = db.Column(db.String(500))
    site_favicon = db.Column(db.String(500))
    
    # معلومات الاتصال
    contact_email = db.Column(db.String(120), default='Ahmedbahnese@yahoo.com')
    contact_phone = db.Column(db.String(20), default='01063299450')
    support_email = db.Column(db.String(120))
    support_phone = db.Column(db.String(20))
    
    # إعدادات الأمان
    enable_two_factor = db.Column(db.Boolean, default=True)
    session_timeout = db.Column(db.Integer, default=3600)  # seconds
    max_login_attempts = db.Column(db.Integer, default=5)
    password_min_length = db.Column(db.Integer, default=8)
    
    # إعدادات التنبيهات
    enable_email_notifications = db.Column(db.Boolean, default=True)
    enable_sms_notifications = db.Column(db.Boolean, default=True)
    enable_push_notifications = db.Column(db.Boolean, default=True)
    
    # إعدادات الدفع
    payment_currency = db.Column(db.String(10), default='EGP')
    tax_rate = db.Column(db.Float, default=0.14)  # 14% VAT in Egypt
    
    # إعدادات اللغة
    default_language = db.Column(db.String(10), default='ar')
    supported_languages = db.Column(db.String(100), default='ar,en')
    
    # إعدادات الصيانة
    maintenance_mode = db.Column(db.Boolean, default=False)
    maintenance_message = db.Column(db.Text)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('admins.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'site_name': self.site_name,
            'site_description': self.site_description,
            'site_logo': self.site_logo,
            'site_favicon': self.site_favicon,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'support_email': self.support_email,
            'support_phone': self.support_phone,
            'enable_two_factor': self.enable_two_factor,
            'session_timeout': self.session_timeout,
            'max_login_attempts': self.max_login_attempts,
            'password_min_length': self.password_min_length,
            'enable_email_notifications': self.enable_email_notifications,
            'enable_sms_notifications': self.enable_sms_notifications,
            'enable_push_notifications': self.enable_push_notifications,
            'payment_currency': self.payment_currency,
            'tax_rate': self.tax_rate,
            'default_language': self.default_language,
            'supported_languages': self.supported_languages,
            'maintenance_mode': self.maintenance_mode,
            'maintenance_message': self.maintenance_message,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by
        }

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # معلومات المستخدم
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_email = db.Column(db.String(120))
    user_type = db.Column(db.String(50))  # patient, doctor, admin, system
    
    # تفاصيل العملية
    action = db.Column(db.String(100), nullable=False)
    resource = db.Column(db.String(100))  # table/model name
    resource_id = db.Column(db.Integer)
    
    # تفاصيل إضافية
    description = db.Column(db.Text)
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    
    # معلومات الجلسة
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    session_id = db.Column(db.String(100))
    
    # النتيجة
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_email': self.user_email,
            'user_type': self.user_type,
            'action': self.action,
            'resource': self.resource,
            'resource_id': self.resource_id,
            'description': self.description,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'session_id': self.session_id,
            'success': self.success,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

