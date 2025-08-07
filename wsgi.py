#!/usr/bin/python3
"""
ملف WSGI لمشروع صحتك في أمان
يستخدم لتشغيل التطبيق على خوادم الإنتاج
"""

import sys
import os
from pathlib import Path

# الحصول على مسار المشروع
project_path = Path(__file__).parent.absolute()
backend_path = project_path / 'sahty_backend'

# إضافة مسارات المشروع إلى Python path
sys.path.insert(0, str(project_path))
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(backend_path / 'src'))

# تفعيل البيئة الافتراضية إذا كانت موجودة
venv_path = backend_path / 'venv' / 'bin' / 'activate_this.py'
if venv_path.exists():
    try:
        with open(venv_path) as file_:
            exec(file_.read(), dict(__file__=str(venv_path)))
    except Exception as e:
        print(f"تحذير: لا يمكن تفعيل البيئة الافتراضية: {e}")

# تحميل متغيرات البيئة
env_file = project_path / '.env'
if env_file.exists():
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    except Exception as e:
        print(f"تحذير: لا يمكن تحميل ملف .env: {e}")

# تعيين متغيرات البيئة الافتراضية
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', 'False')

try:
    # استيراد التطبيق
    from main import app
    
    # إعداد التطبيق للإنتاج
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    # تطبيق Flask
    application = app
    
    # للتوافق مع بعض الخوادم
    app = application
    
except ImportError as e:
    print(f"خطأ في استيراد التطبيق: {e}")
    
    # إنشاء تطبيق بديل في حالة الخطأ
    from flask import Flask, jsonify
    
    application = Flask(__name__)
    
    @application.route('/')
    def error_page():
        return jsonify({
            'error': 'خطأ في تحميل التطبيق',
            'message': 'يرجى التحقق من إعدادات الخادم',
            'details': str(e)
        }), 500
    
    app = application

except Exception as e:
    print(f"خطأ عام في تحميل التطبيق: {e}")
    
    # إنشاء تطبيق بديل في حالة الخطأ
    from flask import Flask, jsonify
    
    application = Flask(__name__)
    
    @application.route('/')
    def error_page():
        return jsonify({
            'error': 'خطأ في تحميل التطبيق',
            'message': 'يرجى التحقق من إعدادات الخادم',
            'details': str(e)
        }), 500
    
    app = application

# دالة للتشغيل المباشر (للاختبار)
if __name__ == "__main__":
    try:
        # تشغيل التطبيق في وضع التطوير
        application.run(
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000)),
            debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        )
    except Exception as e:
        print(f"خطأ في تشغيل التطبيق: {e}")

