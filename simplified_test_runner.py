"""
مشغل اختبارات مبسط لمشروع صحتك في أمان
يفحص البنية العامة للمشروع والملفات الأساسية
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import sys

class SimplifiedTestRunner:
    """مشغل اختبارات مبسط للمشروع"""
    
    def __init__(self):
        """تهيئة مشغل الاختبارات"""
        
        self.project_root = '/home/ubuntu'
        self.backend_path = '/home/ubuntu/sahty_backend'
        self.frontend_path = '/home/ubuntu/sahty_frontend'
        
        self.test_results = {
            'structure_tests': {},
            'file_integrity_tests': {},
            'configuration_tests': {},
            'service_architecture_tests': {},
            'frontend_tests': {},
            'documentation_tests': {}
        }
        
        self.test_statistics = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'execution_time': 0
        }
    
    def run_all_tests(self) -> Dict:
        """تشغيل جميع الاختبارات المبسطة"""
        
        print("🚀 بدء تشغيل الاختبارات المبسطة لمشروع صحتك في أمان...")
        start_time = time.time()
        
        # تشغيل مجموعات الاختبارات
        test_groups = [
            ('فحص بنية المشروع', self._test_project_structure),
            ('فحص سلامة الملفات', self._test_file_integrity),
            ('فحص الإعدادات', self._test_configurations),
            ('فحص معمارية الخدمات', self._test_service_architecture),
            ('فحص الواجهة الأمامية', self._test_frontend_structure),
            ('فحص الوثائق', self._test_documentation)
        ]
        
        for group_name, test_function in test_groups:
            print(f"\n📋 تشغيل {group_name}...")
            try:
                group_results = test_function()
                self._update_statistics(group_results)
                print(f"✅ اكتمل {group_name}")
            except Exception as e:
                print(f"❌ خطأ في {group_name}: {str(e)}")
        
        # حساب الإحصائيات النهائية
        end_time = time.time()
        self.test_statistics['execution_time'] = end_time - start_time
        
        # إنتاج التقرير النهائي
        final_report = self._generate_report()
        
        print(f"\n🎯 اكتملت جميع الاختبارات في {self.test_statistics['execution_time']:.2f} ثانية")
        print(f"📊 النتائج: {self.test_statistics['passed_tests']} نجح، {self.test_statistics['failed_tests']} فشل")
        
        return final_report
    
    def _test_project_structure(self) -> Dict:
        """فحص بنية المشروع"""
        
        structure_tests = {}
        
        # فحص المجلدات الأساسية
        required_directories = [
            '/home/ubuntu/sahty_backend',
            '/home/ubuntu/sahty_backend/src',
            '/home/ubuntu/sahty_backend/src/services',
            '/home/ubuntu/sahty_backend/src/models',
            '/home/ubuntu/sahty_backend/src/routes',
            '/home/ubuntu/sahty_frontend',
            '/home/ubuntu/sahty_frontend/src',
            '/home/ubuntu/sahty_frontend/src/components',
            '/home/ubuntu/sahty_frontend/src/pages'
        ]
        
        for directory in required_directories:
            exists = os.path.exists(directory) and os.path.isdir(directory)
            structure_tests[f'directory_{os.path.basename(directory)}'] = {
                'status': 'passed' if exists else 'failed',
                'path': directory,
                'exists': exists
            }
        
        # فحص الملفات الأساسية
        required_files = [
            '/home/ubuntu/sahty_backend/src/main.py',
            '/home/ubuntu/sahty_backend/requirements.txt',
            '/home/ubuntu/sahty_frontend/package.json',
            '/home/ubuntu/sahty_frontend/src/App.jsx',
            '/home/ubuntu/sahty_frontend/src/index.css'
        ]
        
        for file_path in required_files:
            exists = os.path.exists(file_path) and os.path.isfile(file_path)
            structure_tests[f'file_{os.path.basename(file_path)}'] = {
                'status': 'passed' if exists else 'failed',
                'path': file_path,
                'exists': exists
            }
        
        self.test_results['structure_tests'] = structure_tests
        return structure_tests
    
    def _test_file_integrity(self) -> Dict:
        """فحص سلامة الملفات"""
        
        integrity_tests = {}
        
        # فحص ملفات الخدمات
        services_directory = '/home/ubuntu/sahty_backend/src/services'
        if os.path.exists(services_directory):
            service_files = [f for f in os.listdir(services_directory) if f.endswith('.py')]
            
            integrity_tests['services_count'] = {
                'status': 'passed' if len(service_files) >= 20 else 'failed',
                'count': len(service_files),
                'expected_minimum': 20,
                'files': service_files
            }
            
            # فحص محتوى بعض الملفات المهمة
            important_services = [
                'ai_service.py',
                'payment_service.py',
                'notification_service.py',
                'medication_service.py',
                'emergency_service.py'
            ]
            
            for service_file in important_services:
                file_path = os.path.join(services_directory, service_file)
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # فحص أساسي للمحتوى
                        has_class = 'class ' in content
                        has_methods = 'def ' in content
                        has_docstring = '"""' in content or "'''" in content
                        
                        integrity_tests[f'service_{service_file}'] = {
                            'status': 'passed' if has_class and has_methods else 'failed',
                            'has_class': has_class,
                            'has_methods': has_methods,
                            'has_docstring': has_docstring,
                            'file_size': len(content)
                        }
                    except Exception as e:
                        integrity_tests[f'service_{service_file}'] = {
                            'status': 'failed',
                            'error': str(e)
                        }
                else:
                    integrity_tests[f'service_{service_file}'] = {
                        'status': 'failed',
                        'error': 'ملف غير موجود'
                    }
        
        self.test_results['file_integrity_tests'] = integrity_tests
        return integrity_tests
    
    def _test_configurations(self) -> Dict:
        """فحص الإعدادات"""
        
        config_tests = {}
        
        # فحص package.json
        package_json_path = '/home/ubuntu/sahty_frontend/package.json'
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                
                has_dependencies = 'dependencies' in package_data
                has_scripts = 'scripts' in package_data
                has_name = 'name' in package_data
                
                config_tests['package_json'] = {
                    'status': 'passed' if has_dependencies and has_scripts and has_name else 'failed',
                    'has_dependencies': has_dependencies,
                    'has_scripts': has_scripts,
                    'has_name': has_name,
                    'name': package_data.get('name', 'غير محدد')
                }
            except Exception as e:
                config_tests['package_json'] = {
                    'status': 'failed',
                    'error': str(e)
                }
        else:
            config_tests['package_json'] = {
                'status': 'failed',
                'error': 'ملف package.json غير موجود'
            }
        
        # فحص requirements.txt
        requirements_path = '/home/ubuntu/sahty_backend/requirements.txt'
        if os.path.exists(requirements_path):
            try:
                with open(requirements_path, 'r', encoding='utf-8') as f:
                    requirements = f.read().strip().split('\n')
                
                required_packages = ['flask', 'sqlalchemy', 'jwt', 'requests']
                found_packages = []
                
                for req in requirements:
                    for package in required_packages:
                        if package.lower() in req.lower():
                            found_packages.append(package)
                
                config_tests['requirements_txt'] = {
                    'status': 'passed' if len(found_packages) >= 2 else 'failed',
                    'total_requirements': len(requirements),
                    'found_packages': found_packages,
                    'required_packages': required_packages
                }
            except Exception as e:
                config_tests['requirements_txt'] = {
                    'status': 'failed',
                    'error': str(e)
                }
        else:
            config_tests['requirements_txt'] = {
                'status': 'failed',
                'error': 'ملف requirements.txt غير موجود'
            }
        
        self.test_results['configuration_tests'] = config_tests
        return config_tests
    
    def _test_service_architecture(self) -> Dict:
        """فحص معمارية الخدمات"""
        
        architecture_tests = {}
        
        # قائمة الخدمات المطلوبة حسب التقرير
        expected_services = [
            'ai_service.py',
            'payment_service.py',
            'notification_service.py',
            'medication_service.py',
            'mental_health_service.py',
            'vaccination_service.py',
            'nutrition_service.py',
            'diabetes_service.py',
            'lab_analysis_service.py',
            'emergency_service.py',
            'enhanced_auth_service.py',
            'family_network_service.py',
            'digital_health_card_service.py',
            'smart_search_service.py',
            'floating_buttons_service.py',
            'external_integration_service.py',
            'advanced_security_service.py',
            'backup_service.py',
            'low_end_device_support.py',
            'accessibility_service.py',
            'chatbot_service.py',
            'pregnancy_support_service.py',
            'pre_registration_assistant.py',
            'interactive_guide_service.py',
            'personal_center_service.py',
            'rating_system_service.py',
            'welcome_video_service.py',
            'compliance_service.py',
            'government_integration_service.py',
            'offline_mode_service.py',
            'battery_optimization_service.py',
            'advanced_blood_type_service.py',
            'lab_radiology_service.py',
            'private_hospitals_service.py'
        ]
        
        services_directory = '/home/ubuntu/sahty_backend/src/services'
        existing_services = []
        missing_services = []
        
        if os.path.exists(services_directory):
            for service in expected_services:
                service_path = os.path.join(services_directory, service)
                if os.path.exists(service_path):
                    existing_services.append(service)
                else:
                    missing_services.append(service)
        
        coverage_percentage = (len(existing_services) / len(expected_services)) * 100
        
        architecture_tests['service_coverage'] = {
            'status': 'passed' if coverage_percentage >= 90 else 'failed',
            'coverage_percentage': coverage_percentage,
            'total_expected': len(expected_services),
            'existing_services': len(existing_services),
            'missing_services': len(missing_services),
            'missing_list': missing_services[:10]  # أول 10 خدمات مفقودة
        }
        
        # فحص النماذج
        models_directory = '/home/ubuntu/sahty_backend/src/models'
        expected_models = [
            'patient.py',
            'doctor.py',
            'appointment.py',
            'medication.py',
            'blood_bank.py',
            'hospital.py',
            'admin.py'
        ]
        
        existing_models = []
        if os.path.exists(models_directory):
            for model in expected_models:
                model_path = os.path.join(models_directory, model)
                if os.path.exists(model_path):
                    existing_models.append(model)
        
        model_coverage = (len(existing_models) / len(expected_models)) * 100
        
        architecture_tests['model_coverage'] = {
            'status': 'passed' if model_coverage >= 80 else 'failed',
            'coverage_percentage': model_coverage,
            'existing_models': len(existing_models),
            'total_expected': len(expected_models)
        }
        
        self.test_results['service_architecture_tests'] = architecture_tests
        return architecture_tests
    
    def _test_frontend_structure(self) -> Dict:
        """فحص بنية الواجهة الأمامية"""
        
        frontend_tests = {}
        
        # فحص الصفحات المطلوبة
        pages_directory = '/home/ubuntu/sahty_frontend/src/pages'
        expected_pages = [
            'HomePage.jsx',
            'LoginPage.jsx',
            'RegisterPage.jsx',
            'DashboardPage.jsx',
            'DoctorsPage.jsx',
            'ServicesPage.jsx',
            'BloodBankPage.jsx',
            'EmergencyPage.jsx',
            'AIAssistantPage.jsx'
        ]
        
        existing_pages = []
        if os.path.exists(pages_directory):
            for page in expected_pages:
                page_path = os.path.join(pages_directory, page)
                if os.path.exists(page_path):
                    existing_pages.append(page)
        
        page_coverage = (len(existing_pages) / len(expected_pages)) * 100
        
        frontend_tests['pages_coverage'] = {
            'status': 'passed' if page_coverage >= 80 else 'failed',
            'coverage_percentage': page_coverage,
            'existing_pages': len(existing_pages),
            'total_expected': len(expected_pages)
        }
        
        # فحص المكونات
        components_directory = '/home/ubuntu/sahty_frontend/src/components'
        expected_components = [
            'Navbar.jsx',
            'Footer.jsx'
        ]
        
        existing_components = []
        if os.path.exists(components_directory):
            for component in expected_components:
                component_path = os.path.join(components_directory, component)
                if os.path.exists(component_path):
                    existing_components.append(component)
        
        component_coverage = (len(existing_components) / len(expected_components)) * 100
        
        frontend_tests['components_coverage'] = {
            'status': 'passed' if component_coverage >= 80 else 'failed',
            'coverage_percentage': component_coverage,
            'existing_components': len(existing_components),
            'total_expected': len(expected_components)
        }
        
        # فحص ملف App.jsx
        app_file = '/home/ubuntu/sahty_frontend/src/App.jsx'
        if os.path.exists(app_file):
            try:
                with open(app_file, 'r', encoding='utf-8') as f:
                    app_content = f.read()
                
                has_router = 'Router' in app_content or 'BrowserRouter' in app_content
                has_routes = 'Route' in app_content
                has_context = 'Context' in app_content or 'Provider' in app_content
                
                frontend_tests['app_structure'] = {
                    'status': 'passed' if has_router and has_routes else 'failed',
                    'has_router': has_router,
                    'has_routes': has_routes,
                    'has_context': has_context,
                    'file_size': len(app_content)
                }
            except Exception as e:
                frontend_tests['app_structure'] = {
                    'status': 'failed',
                    'error': str(e)
                }
        else:
            frontend_tests['app_structure'] = {
                'status': 'failed',
                'error': 'ملف App.jsx غير موجود'
            }
        
        self.test_results['frontend_tests'] = frontend_tests
        return frontend_tests
    
    def _test_documentation(self) -> Dict:
        """فحص الوثائق"""
        
        documentation_tests = {}
        
        # فحص ملف todo.md
        todo_file = '/home/ubuntu/todo.md'
        if os.path.exists(todo_file):
            try:
                with open(todo_file, 'r', encoding='utf-8') as f:
                    todo_content = f.read()
                
                has_phases = 'المرحلة' in todo_content
                has_checkboxes = '- [x]' in todo_content or '- [ ]' in todo_content
                is_comprehensive = len(todo_content) > 1000
                
                documentation_tests['todo_file'] = {
                    'status': 'passed' if has_phases and has_checkboxes else 'failed',
                    'has_phases': has_phases,
                    'has_checkboxes': has_checkboxes,
                    'is_comprehensive': is_comprehensive,
                    'file_size': len(todo_content)
                }
            except Exception as e:
                documentation_tests['todo_file'] = {
                    'status': 'failed',
                    'error': str(e)
                }
        else:
            documentation_tests['todo_file'] = {
                'status': 'failed',
                'error': 'ملف todo.md غير موجود'
            }
        
        # فحص المخطط المعماري
        architecture_file = '/home/ubuntu/sahty_architecture.png'
        if os.path.exists(architecture_file):
            file_size = os.path.getsize(architecture_file)
            documentation_tests['architecture_diagram'] = {
                'status': 'passed' if file_size > 1000 else 'failed',
                'exists': True,
                'file_size': file_size
            }
        else:
            documentation_tests['architecture_diagram'] = {
                'status': 'failed',
                'exists': False,
                'error': 'مخطط معماري غير موجود'
            }
        
        self.test_results['documentation_tests'] = documentation_tests
        return documentation_tests
    
    def _update_statistics(self, test_results: Dict):
        """تحديث إحصائيات الاختبارات"""
        
        for test_name, test_result in test_results.items():
            self.test_statistics['total_tests'] += 1
            
            if test_result.get('status') == 'passed':
                self.test_statistics['passed_tests'] += 1
            else:
                self.test_statistics['failed_tests'] += 1
    
    def _generate_report(self) -> Dict:
        """إنتاج التقرير النهائي"""
        
        # حساب نسبة النجاح
        if self.test_statistics['total_tests'] > 0:
            success_rate = (self.test_statistics['passed_tests'] / self.test_statistics['total_tests']) * 100
        else:
            success_rate = 0
        
        # تحديد حالة المشروع
        if success_rate >= 90:
            project_status = 'ممتاز - جاهز للنشر'
            status_color = 'green'
        elif success_rate >= 80:
            project_status = 'جيد - يحتاج تحسينات طفيفة'
            status_color = 'yellow'
        elif success_rate >= 70:
            project_status = 'مقبول - يحتاج تحسينات'
            status_color = 'orange'
        else:
            project_status = 'يحتاج عمل إضافي'
            status_color = 'red'
        
        # جمع التوصيات
        recommendations = []
        
        # فحص نتائج الخدمات
        service_tests = self.test_results.get('service_architecture_tests', {})
        service_coverage = service_tests.get('service_coverage', {})
        if service_coverage.get('coverage_percentage', 0) < 90:
            recommendations.append(f"إكمال الخدمات المفقودة ({len(service_coverage.get('missing_services', []))} خدمة)")
        
        # فحص نتائج الواجهة الأمامية
        frontend_tests = self.test_results.get('frontend_tests', {})
        page_coverage = frontend_tests.get('pages_coverage', {})
        if page_coverage.get('coverage_percentage', 0) < 80:
            recommendations.append("إكمال صفحات الواجهة الأمامية المفقودة")
        
        # فحص الوثائق
        doc_tests = self.test_results.get('documentation_tests', {})
        if doc_tests.get('architecture_diagram', {}).get('status') != 'passed':
            recommendations.append("إضافة المخطط المعماري للمشروع")
        
        if success_rate < 85:
            recommendations.append("مراجعة وإصلاح الاختبارات الفاشلة")
        
        # التقرير النهائي
        final_report = {
            'test_summary': {
                'total_tests': self.test_statistics['total_tests'],
                'passed_tests': self.test_statistics['passed_tests'],
                'failed_tests': self.test_statistics['failed_tests'],
                'success_rate': success_rate,
                'execution_time': self.test_statistics['execution_time']
            },
            'project_status': {
                'status': project_status,
                'status_color': status_color,
                'ready_for_deployment': success_rate >= 85
            },
            'detailed_results': self.test_results,
            'recommendations': recommendations,
            'generated_at': datetime.now().isoformat(),
            'project_info': {
                'name': 'صحتك في أمان',
                'owner': 'أحمد حامد أحمد بهنسي',
                'domain': 'sahty.zya.me',
                'features_implemented': self._count_implemented_features()
            }
        }
        
        return final_report
    
    def _count_implemented_features(self) -> Dict:
        """حساب الميزات المطبقة"""
        
        # حساب الخدمات المطبقة
        services_dir = '/home/ubuntu/sahty_backend/src/services'
        service_count = 0
        if os.path.exists(services_dir):
            service_count = len([f for f in os.listdir(services_dir) if f.endswith('.py')])
        
        # حساب الصفحات المطبقة
        pages_dir = '/home/ubuntu/sahty_frontend/src/pages'
        page_count = 0
        if os.path.exists(pages_dir):
            page_count = len([f for f in os.listdir(pages_dir) if f.endswith('.jsx')])
        
        # حساب النماذج المطبقة
        models_dir = '/home/ubuntu/sahty_backend/src/models'
        model_count = 0
        if os.path.exists(models_dir):
            model_count = len([f for f in os.listdir(models_dir) if f.endswith('.py')])
        
        return {
            'backend_services': service_count,
            'frontend_pages': page_count,
            'data_models': model_count,
            'total_files': service_count + page_count + model_count
        }


def main():
    """تشغيل الاختبارات المبسطة"""
    
    print("=" * 80)
    print("🏥 اختبارات مبسطة لمشروع صحتك في أمان")
    print("=" * 80)
    
    # إنشاء مشغل الاختبارات
    test_runner = SimplifiedTestRunner()
    
    # تشغيل الاختبارات
    final_report = test_runner.run_all_tests()
    
    # طباعة التقرير النهائي
    print("\n" + "=" * 80)
    print("📊 التقرير النهائي")
    print("=" * 80)
    
    print(f"📈 إجمالي الاختبارات: {final_report['test_summary']['total_tests']}")
    print(f"✅ اختبارات ناجحة: {final_report['test_summary']['passed_tests']}")
    print(f"❌ اختبارات فاشلة: {final_report['test_summary']['failed_tests']}")
    print(f"📊 نسبة النجاح: {final_report['test_summary']['success_rate']:.1f}%")
    print(f"⏱️ وقت التنفيذ: {final_report['test_summary']['execution_time']:.2f} ثانية")
    
    print(f"\n🎯 حالة المشروع: {final_report['project_status']['status']}")
    print(f"🚀 جاهز للنشر: {'نعم' if final_report['project_status']['ready_for_deployment'] else 'لا'}")
    
    print(f"\n📁 الميزات المطبقة:")
    features = final_report['project_info']['features_implemented']
    print(f"   - خدمات الواجهة الخلفية: {features['backend_services']}")
    print(f"   - صفحات الواجهة الأمامية: {features['frontend_pages']}")
    print(f"   - نماذج البيانات: {features['data_models']}")
    print(f"   - إجمالي الملفات: {features['total_files']}")
    
    if final_report['recommendations']:
        print(f"\n💡 توصيات التحسين:")
        for recommendation in final_report['recommendations']:
            print(f"   - {recommendation}")
    
    print("\n" + "=" * 80)
    print("🎉 اكتملت جميع الاختبارات!")
    print("=" * 80)
    
    return final_report


if __name__ == "__main__":
    main()

