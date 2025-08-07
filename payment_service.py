"""
خدمة أنظمة الدفع المتكاملة
"""

import os
import json
import hashlib
import hmac
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app
from decimal import Decimal
import uuid

class PaymentService:
    def __init__(self):
        """تهيئة خدمة الدفع"""
        # إعدادات بوابات الدفع المختلفة
        self.fawry_config = {
            'merchant_code': os.getenv('FAWRY_MERCHANT_CODE', 'TEST_MERCHANT'),
            'security_key': os.getenv('FAWRY_SECURITY_KEY', 'TEST_KEY'),
            'base_url': os.getenv('FAWRY_BASE_URL', 'https://atfawry.fawrystaging.com/ECommerceWeb/Fawry/')
        }
        
        self.paymob_config = {
            'api_key': os.getenv('PAYMOB_API_KEY', 'TEST_API_KEY'),
            'integration_id': os.getenv('PAYMOB_INTEGRATION_ID', 'TEST_INTEGRATION'),
            'base_url': os.getenv('PAYMOB_BASE_URL', 'https://accept.paymob.com/api/')
        }
        
        self.vodafone_cash_config = {
            'merchant_id': os.getenv('VODAFONE_MERCHANT_ID', 'TEST_MERCHANT'),
            'api_key': os.getenv('VODAFONE_API_KEY', 'TEST_KEY'),
            'base_url': os.getenv('VODAFONE_BASE_URL', 'https://api-preprod.vodafone.com.eg/')
        }
    
    def create_payment_intent(self, amount: float, currency: str = 'EGP', 
                            payment_method: str = 'card', customer_info: Dict = None,
                            service_details: Dict = None) -> Dict:
        """
        إنشاء نية دفع جديدة
        
        Args:
            amount: المبلغ
            currency: العملة
            payment_method: طريقة الدفع (card, wallet, cash, bank_transfer)
            customer_info: معلومات العميل
            service_details: تفاصيل الخدمة
            
        Returns:
            Dict: تفاصيل نية الدفع
        """
        try:
            payment_id = str(uuid.uuid4())
            
            payment_intent = {
                'payment_id': payment_id,
                'amount': float(amount),
                'currency': currency,
                'payment_method': payment_method,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=1)).isoformat(),
                'customer_info': customer_info or {},
                'service_details': service_details or {},
                'metadata': {
                    'source': 'sahty_app',
                    'version': '1.0'
                }
            }
            
            # اختيار بوابة الدفع المناسبة
            if payment_method == 'card':
                payment_intent['payment_url'] = self._create_card_payment(payment_intent)
            elif payment_method == 'wallet':
                payment_intent['payment_url'] = self._create_wallet_payment(payment_intent)
            elif payment_method == 'fawry':
                payment_intent['payment_code'] = self._create_fawry_payment(payment_intent)
            elif payment_method == 'bank_transfer':
                payment_intent['bank_details'] = self._get_bank_transfer_details()
            
            return {
                'success': True,
                'payment_intent': payment_intent
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء نية الدفع: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_card_payment(self, payment_intent: Dict) -> str:
        """إنشاء رابط دفع بالبطاقة عبر Paymob"""
        try:
            # الحصول على رمز المصادقة
            auth_response = requests.post(
                f"{self.paymob_config['base_url']}auth/tokens",
                json={'api_key': self.paymob_config['api_key']}
            )
            
            if auth_response.status_code != 201:
                raise Exception("فشل في المصادقة مع Paymob")
            
            auth_token = auth_response.json()['token']
            
            # إنشاء طلب دفع
            order_data = {
                'auth_token': auth_token,
                'delivery_needed': False,
                'amount_cents': int(payment_intent['amount'] * 100),
                'currency': payment_intent['currency'],
                'merchant_order_id': payment_intent['payment_id'],
                'items': [{
                    'name': payment_intent['service_details'].get('name', 'خدمة طبية'),
                    'amount_cents': int(payment_intent['amount'] * 100),
                    'description': payment_intent['service_details'].get('description', ''),
                    'quantity': 1
                }]
            }
            
            order_response = requests.post(
                f"{self.paymob_config['base_url']}ecommerce/orders",
                json=order_data
            )
            
            if order_response.status_code != 201:
                raise Exception("فشل في إنشاء طلب الدفع")
            
            order_id = order_response.json()['id']
            
            # إنشاء مفتاح الدفع
            payment_key_data = {
                'auth_token': auth_token,
                'amount_cents': int(payment_intent['amount'] * 100),
                'expiration': 3600,
                'order_id': order_id,
                'billing_data': {
                    'apartment': 'NA',
                    'email': payment_intent['customer_info'].get('email', ''),
                    'floor': 'NA',
                    'first_name': payment_intent['customer_info'].get('first_name', ''),
                    'street': 'NA',
                    'building': 'NA',
                    'phone_number': payment_intent['customer_info'].get('phone', ''),
                    'shipping_method': 'NA',
                    'postal_code': 'NA',
                    'city': payment_intent['customer_info'].get('city', ''),
                    'country': 'EG',
                    'last_name': payment_intent['customer_info'].get('last_name', ''),
                    'state': 'NA'
                },
                'currency': payment_intent['currency'],
                'integration_id': self.paymob_config['integration_id']
            }
            
            payment_key_response = requests.post(
                f"{self.paymob_config['base_url']}acceptance/payment_keys",
                json=payment_key_data
            )
            
            if payment_key_response.status_code != 201:
                raise Exception("فشل في إنشاء مفتاح الدفع")
            
            payment_token = payment_key_response.json()['token']
            
            return f"https://accept.paymob.com/api/acceptance/iframes/YOUR_IFRAME_ID?payment_token={payment_token}"
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء دفع البطاقة: {str(e)}")
            return None
    
    def _create_wallet_payment(self, payment_intent: Dict) -> str:
        """إنشاء دفع عبر المحفظة الإلكترونية"""
        try:
            # محاكاة إنشاء رابط دفع المحفظة
            wallet_data = {
                'payment_id': payment_intent['payment_id'],
                'amount': payment_intent['amount'],
                'phone': payment_intent['customer_info'].get('phone', ''),
                'service': payment_intent['service_details'].get('name', 'خدمة طبية')
            }
            
            # في التطبيق الحقيقي، سيتم استدعاء API المحفظة الإلكترونية
            return f"https://wallet.example.com/pay?ref={payment_intent['payment_id']}"
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء دفع المحفظة: {str(e)}")
            return None
    
    def _create_fawry_payment(self, payment_intent: Dict) -> str:
        """إنشاء كود دفع فوري"""
        try:
            # إعداد بيانات الدفع
            merchant_ref_num = payment_intent['payment_id']
            customer_mobile = payment_intent['customer_info'].get('phone', '')
            amount = payment_intent['amount']
            
            # إنشاء التوقيع
            signature_string = (
                f"{self.fawry_config['merchant_code']}"
                f"{merchant_ref_num}"
                f"{customer_mobile}"
                f"{amount:.2f}"
                f"{self.fawry_config['security_key']}"
            )
            
            signature = hashlib.sha256(signature_string.encode()).hexdigest()
            
            # بيانات الطلب
            request_data = {
                'merchantCode': self.fawry_config['merchant_code'],
                'merchantRefNum': merchant_ref_num,
                'customerMobile': customer_mobile,
                'customerEmail': payment_intent['customer_info'].get('email', ''),
                'paymentAmount': amount,
                'currencyCode': payment_intent['currency'],
                'paymentMethod': 'PAYATFAWRY',
                'signature': signature,
                'chargeItems': [{
                    'itemId': '1',
                    'description': payment_intent['service_details'].get('name', 'خدمة طبية'),
                    'price': amount,
                    'quantity': 1
                }]
            }
            
            # إرسال الطلب
            response = requests.post(
                f"{self.fawry_config['base_url']}payments/charge",
                json=request_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('statusCode') == 200:
                    return result.get('referenceNumber')
            
            raise Exception("فشل في إنشاء كود فوري")
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء دفع فوري: {str(e)}")
            return None
    
    def _get_bank_transfer_details(self) -> Dict:
        """الحصول على تفاصيل التحويل البنكي"""
        return {
            'bank_name': 'البنك الأهلي المصري',
            'account_number': '1234567890123456',
            'account_name': 'صحتك في أمان',
            'swift_code': 'NBEAEGCX',
            'iban': 'EG380003001234567890123456789',
            'branch': 'فرع مدينة نصر',
            'instructions': [
                'يرجى كتابة رقم الطلب في خانة البيان',
                'إرسال صورة من إيصال التحويل عبر الواتساب',
                'سيتم تفعيل الخدمة خلال 24 ساعة من التحويل'
            ]
        }
    
    def verify_payment(self, payment_id: str, verification_data: Dict = None) -> Dict:
        """
        التحقق من حالة الدفع
        
        Args:
            payment_id: معرف الدفع
            verification_data: بيانات التحقق الإضافية
            
        Returns:
            Dict: حالة الدفع
        """
        try:
            # في التطبيق الحقيقي، سيتم الاستعلام من قاعدة البيانات
            # والتحقق من بوابة الدفع
            
            # محاكاة التحقق
            payment_status = {
                'payment_id': payment_id,
                'status': 'completed',  # pending, completed, failed, cancelled
                'amount': 100.0,
                'currency': 'EGP',
                'transaction_id': f"TXN_{payment_id[:8]}",
                'verified_at': datetime.now().isoformat(),
                'payment_method': 'card',
                'fees': 5.0,
                'net_amount': 95.0
            }
            
            return {
                'success': True,
                'payment_status': payment_status
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في التحقق من الدفع: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_refund(self, payment_id: str, amount: float = None, reason: str = None) -> Dict:
        """
        معالجة استرداد المبلغ
        
        Args:
            payment_id: معرف الدفع
            amount: المبلغ المراد استرداده (None للاسترداد الكامل)
            reason: سبب الاسترداد
            
        Returns:
            Dict: تفاصيل الاسترداد
        """
        try:
            refund_id = str(uuid.uuid4())
            
            # في التطبيق الحقيقي، سيتم استدعاء API بوابة الدفع
            refund_details = {
                'refund_id': refund_id,
                'payment_id': payment_id,
                'amount': amount or 100.0,
                'reason': reason or 'طلب العميل',
                'status': 'processing',
                'created_at': datetime.now().isoformat(),
                'estimated_completion': (datetime.now() + timedelta(days=7)).isoformat()
            }
            
            return {
                'success': True,
                'refund_details': refund_details
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في معالجة الاسترداد: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_payment_methods(self, amount: float = None, customer_location: str = None) -> List[Dict]:
        """
        الحصول على طرق الدفع المتاحة
        
        Args:
            amount: المبلغ (لتحديد الطرق المناسبة)
            customer_location: موقع العميل
            
        Returns:
            List[Dict]: قائمة طرق الدفع المتاحة
        """
        payment_methods = [
            {
                'id': 'card',
                'name': 'بطاقة ائتمان/خصم',
                'description': 'فيزا، ماستركارد، أو بطاقات محلية',
                'icon': 'credit-card',
                'fees': '2.9% + 2 جنيه',
                'processing_time': 'فوري',
                'min_amount': 10,
                'max_amount': 50000,
                'available': True
            },
            {
                'id': 'wallet',
                'name': 'محفظة إلكترونية',
                'description': 'فودافون كاش، أورانج موني، إتصالات كاش',
                'icon': 'smartphone',
                'fees': '1.5%',
                'processing_time': 'فوري',
                'min_amount': 5,
                'max_amount': 10000,
                'available': True
            },
            {
                'id': 'fawry',
                'name': 'فوري',
                'description': 'ادفع في أي فرع فوري أو ماكينة',
                'icon': 'map-pin',
                'fees': '5 جنيه',
                'processing_time': 'فوري',
                'min_amount': 10,
                'max_amount': 5000,
                'available': True
            },
            {
                'id': 'bank_transfer',
                'name': 'تحويل بنكي',
                'description': 'تحويل مباشر من حسابك البنكي',
                'icon': 'building',
                'fees': 'مجاني',
                'processing_time': '1-3 أيام عمل',
                'min_amount': 50,
                'max_amount': 100000,
                'available': True
            },
            {
                'id': 'installments',
                'name': 'تقسيط',
                'description': 'قسط المبلغ على 3، 6، أو 12 شهر',
                'icon': 'calendar',
                'fees': 'حسب البنك',
                'processing_time': 'فوري',
                'min_amount': 500,
                'max_amount': 50000,
                'available': amount and amount >= 500
            }
        ]
        
        # فلترة الطرق المتاحة حسب المبلغ
        if amount:
            available_methods = []
            for method in payment_methods:
                if (method['min_amount'] <= amount <= method['max_amount'] and 
                    method['available']):
                    available_methods.append(method)
            return available_methods
        
        return [method for method in payment_methods if method['available']]
    
    def calculate_fees(self, amount: float, payment_method: str) -> Dict:
        """
        حساب رسوم الدفع
        
        Args:
            amount: المبلغ
            payment_method: طريقة الدفع
            
        Returns:
            Dict: تفاصيل الرسوم
        """
        fee_structures = {
            'card': {'percentage': 2.9, 'fixed': 2.0},
            'wallet': {'percentage': 1.5, 'fixed': 0.0},
            'fawry': {'percentage': 0.0, 'fixed': 5.0},
            'bank_transfer': {'percentage': 0.0, 'fixed': 0.0},
            'installments': {'percentage': 3.5, 'fixed': 0.0}
        }
        
        if payment_method not in fee_structures:
            return {'error': 'طريقة دفع غير مدعومة'}
        
        structure = fee_structures[payment_method]
        percentage_fee = amount * (structure['percentage'] / 100)
        fixed_fee = structure['fixed']
        total_fees = percentage_fee + fixed_fee
        
        return {
            'amount': amount,
            'percentage_fee': percentage_fee,
            'fixed_fee': fixed_fee,
            'total_fees': total_fees,
            'net_amount': amount - total_fees,
            'customer_pays': amount + total_fees if payment_method == 'card' else amount
        }
    
    def create_subscription(self, customer_id: str, plan_id: str, payment_method: str) -> Dict:
        """
        إنشاء اشتراك دوري
        
        Args:
            customer_id: معرف العميل
            plan_id: معرف الخطة
            payment_method: طريقة الدفع
            
        Returns:
            Dict: تفاصيل الاشتراك
        """
        try:
            subscription_id = str(uuid.uuid4())
            
            # خطط الاشتراك المتاحة
            plans = {
                'basic': {
                    'name': 'الخطة الأساسية',
                    'price': 99.0,
                    'billing_cycle': 'monthly',
                    'features': ['استشارات محدودة', 'تحليل أساسي للصور']
                },
                'premium': {
                    'name': 'الخطة المميزة',
                    'price': 199.0,
                    'billing_cycle': 'monthly',
                    'features': ['استشارات غير محدودة', 'تحليل متقدم', 'تقارير مفصلة']
                },
                'family': {
                    'name': 'خطة العائلة',
                    'price': 299.0,
                    'billing_cycle': 'monthly',
                    'features': ['حتى 6 أفراد', 'جميع الميزات', 'دعم أولوية']
                }
            }
            
            if plan_id not in plans:
                raise Exception('خطة غير موجودة')
            
            plan = plans[plan_id]
            
            subscription = {
                'subscription_id': subscription_id,
                'customer_id': customer_id,
                'plan_id': plan_id,
                'plan_details': plan,
                'payment_method': payment_method,
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'next_billing_date': (datetime.now() + timedelta(days=30)).isoformat(),
                'trial_end_date': (datetime.now() + timedelta(days=7)).isoformat()
            }
            
            return {
                'success': True,
                'subscription': subscription
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء الاشتراك: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

