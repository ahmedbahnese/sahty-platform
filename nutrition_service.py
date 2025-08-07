"""
خدمة التغذية والنظام الغذائي الصحي
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from flask import current_app
from dataclasses import dataclass
from enum import Enum

class DietType(Enum):
    GENERAL = "عام"
    DIABETIC = "مرضى السكري"
    HYPERTENSION = "ضغط الدم"
    WEIGHT_LOSS = "إنقاص الوزن"
    WEIGHT_GAIN = "زيادة الوزن"
    HEART_HEALTHY = "صحة القلب"
    KIDNEY_FRIENDLY = "صحة الكلى"
    VEGETARIAN = "نباتي"
    GLUTEN_FREE = "خالي من الجلوتين"

class MealType(Enum):
    BREAKFAST = "إفطار"
    LUNCH = "غداء"
    DINNER = "عشاء"
    SNACK = "وجبة خفيفة"

class ActivityLevel(Enum):
    SEDENTARY = "قليل الحركة"
    LIGHT = "نشاط خفيف"
    MODERATE = "نشاط متوسط"
    ACTIVE = "نشط"
    VERY_ACTIVE = "نشط جداً"

@dataclass
class NutritionProfile:
    profile_id: str
    patient_id: str
    age: int
    gender: str
    height: float
    weight: float
    activity_level: str
    health_conditions: List[str]
    allergies: List[str]
    dietary_preferences: List[str]
    daily_calorie_needs: float
    bmr: float
    bmi: float

class NutritionService:
    def __init__(self):
        """تهيئة خدمة التغذية"""
        
        # قاعدة بيانات الأطعمة المصرية
        self.foods_database = {
            # الحبوب والنشويات
            'rice': {
                'name': 'أرز أبيض',
                'category': 'حبوب ونشويات',
                'calories_per_100g': 130,
                'protein': 2.7,
                'carbs': 28,
                'fat': 0.3,
                'fiber': 0.4,
                'vitamins': ['B1', 'B3'],
                'minerals': ['منجنيز', 'سيلينيوم'],
                'glycemic_index': 73,
                'suitable_for': ['عام'],
                'avoid_for': ['مرضى السكري بكميات كبيرة']
            },
            'brown_rice': {
                'name': 'أرز بني',
                'category': 'حبوب ونشويات',
                'calories_per_100g': 111,
                'protein': 2.6,
                'carbs': 23,
                'fat': 0.9,
                'fiber': 1.8,
                'vitamins': ['B1', 'B3', 'B6'],
                'minerals': ['منجنيز', 'سيلينيوم', 'مغنيسيوم'],
                'glycemic_index': 50,
                'suitable_for': ['مرضى السكري', 'إنقاص الوزن'],
                'avoid_for': []
            },
            'bread': {
                'name': 'خبز بلدي',
                'category': 'حبوب ونشويات',
                'calories_per_100g': 265,
                'protein': 8.2,
                'carbs': 49,
                'fat': 3.2,
                'fiber': 4.8,
                'vitamins': ['B1', 'B3', 'حمض الفوليك'],
                'minerals': ['حديد', 'مغنيسيوم'],
                'glycemic_index': 75,
                'suitable_for': ['عام'],
                'avoid_for': ['حساسية الجلوتين']
            },
            # البروتينات
            'chicken_breast': {
                'name': 'صدر دجاج منزوع الجلد',
                'category': 'بروتينات',
                'calories_per_100g': 165,
                'protein': 31,
                'carbs': 0,
                'fat': 3.6,
                'fiber': 0,
                'vitamins': ['B3', 'B6', 'B12'],
                'minerals': ['فوسفور', 'سيلينيوم'],
                'glycemic_index': 0,
                'suitable_for': ['إنقاص الوزن', 'بناء العضلات'],
                'avoid_for': []
            },
            'fish': {
                'name': 'سمك بلطي',
                'category': 'بروتينات',
                'calories_per_100g': 128,
                'protein': 26,
                'carbs': 0,
                'fat': 2.7,
                'fiber': 0,
                'vitamins': ['B12', 'D'],
                'minerals': ['فوسفور', 'سيلينيوم', 'بوتاسيوم'],
                'glycemic_index': 0,
                'suitable_for': ['صحة القلب', 'مرضى السكري'],
                'avoid_for': ['حساسية الأسماك']
            },
            'eggs': {
                'name': 'بيض',
                'category': 'بروتينات',
                'calories_per_100g': 155,
                'protein': 13,
                'carbs': 1.1,
                'fat': 11,
                'fiber': 0,
                'vitamins': ['A', 'D', 'B12', 'حمض الفوليك'],
                'minerals': ['حديد', 'زنك', 'سيلينيوم'],
                'glycemic_index': 0,
                'suitable_for': ['بناء العضلات', 'عام'],
                'avoid_for': ['حساسية البيض']
            },
            # الخضروات
            'tomatoes': {
                'name': 'طماطم',
                'category': 'خضروات',
                'calories_per_100g': 18,
                'protein': 0.9,
                'carbs': 3.9,
                'fat': 0.2,
                'fiber': 1.2,
                'vitamins': ['C', 'K', 'حمض الفوليك'],
                'minerals': ['بوتاسيوم', 'منجنيز'],
                'glycemic_index': 10,
                'suitable_for': ['جميع الأنظمة'],
                'avoid_for': []
            },
            'cucumber': {
                'name': 'خيار',
                'category': 'خضروات',
                'calories_per_100g': 16,
                'protein': 0.7,
                'carbs': 4,
                'fat': 0.1,
                'fiber': 0.5,
                'vitamins': ['C', 'K'],
                'minerals': ['بوتاسيوم', 'مغنيسيوم'],
                'glycemic_index': 15,
                'suitable_for': ['إنقاص الوزن', 'مرضى السكري'],
                'avoid_for': []
            },
            'spinach': {
                'name': 'سبانخ',
                'category': 'خضروات ورقية',
                'calories_per_100g': 23,
                'protein': 2.9,
                'carbs': 3.6,
                'fat': 0.4,
                'fiber': 2.2,
                'vitamins': ['A', 'C', 'K', 'حمض الفوليك'],
                'minerals': ['حديد', 'كالسيوم', 'مغنيسيوم'],
                'glycemic_index': 15,
                'suitable_for': ['جميع الأنظمة'],
                'avoid_for': ['حصوات الكلى (بكميات كبيرة)']
            },
            # الفواكه
            'apple': {
                'name': 'تفاح',
                'category': 'فواكه',
                'calories_per_100g': 52,
                'protein': 0.3,
                'carbs': 14,
                'fat': 0.2,
                'fiber': 2.4,
                'vitamins': ['C'],
                'minerals': ['بوتاسيوم'],
                'glycemic_index': 36,
                'suitable_for': ['مرضى السكري', 'إنقاص الوزن'],
                'avoid_for': []
            },
            'banana': {
                'name': 'موز',
                'category': 'فواكه',
                'calories_per_100g': 89,
                'protein': 1.1,
                'carbs': 23,
                'fat': 0.3,
                'fiber': 2.6,
                'vitamins': ['C', 'B6'],
                'minerals': ['بوتاسيوم', 'مغنيسيوم'],
                'glycemic_index': 51,
                'suitable_for': ['الرياضيين', 'زيادة الوزن'],
                'avoid_for': ['مرضى السكري بكميات كبيرة']
            },
            'orange': {
                'name': 'برتقال',
                'category': 'فواكه حمضية',
                'calories_per_100g': 47,
                'protein': 0.9,
                'carbs': 12,
                'fat': 0.1,
                'fiber': 2.4,
                'vitamins': ['C', 'حمض الفوليك'],
                'minerals': ['كالسيوم', 'بوتاسيوم'],
                'glycemic_index': 45,
                'suitable_for': ['جميع الأنظمة'],
                'avoid_for': []
            },
            # منتجات الألبان
            'milk': {
                'name': 'لبن خالي الدسم',
                'category': 'منتجات ألبان',
                'calories_per_100g': 34,
                'protein': 3.4,
                'carbs': 5,
                'fat': 0.1,
                'fiber': 0,
                'vitamins': ['A', 'D', 'B12'],
                'minerals': ['كالسيوم', 'فوسفور'],
                'glycemic_index': 15,
                'suitable_for': ['إنقاص الوزن', 'صحة العظام'],
                'avoid_for': ['حساسية اللاكتوز']
            },
            'yogurt': {
                'name': 'زبادي طبيعي',
                'category': 'منتجات ألبان',
                'calories_per_100g': 59,
                'protein': 10,
                'carbs': 3.6,
                'fat': 0.4,
                'fiber': 0,
                'vitamins': ['B12', 'ريبوفلافين'],
                'minerals': ['كالسيوم', 'فوسفور'],
                'glycemic_index': 35,
                'suitable_for': ['صحة الهضم', 'بناء العضلات'],
                'avoid_for': ['حساسية اللاكتوز']
            },
            # المكسرات والبذور
            'almonds': {
                'name': 'لوز',
                'category': 'مكسرات',
                'calories_per_100g': 579,
                'protein': 21,
                'carbs': 22,
                'fat': 50,
                'fiber': 12,
                'vitamins': ['E', 'ريبوفلافين'],
                'minerals': ['مغنيسيوم', 'كالسيوم', 'حديد'],
                'glycemic_index': 0,
                'suitable_for': ['صحة القلب', 'مرضى السكري'],
                'avoid_for': ['حساسية المكسرات']
            },
            'walnuts': {
                'name': 'جوز',
                'category': 'مكسرات',
                'calories_per_100g': 654,
                'protein': 15,
                'carbs': 14,
                'fat': 65,
                'fiber': 7,
                'vitamins': ['E', 'B6'],
                'minerals': ['مغنيسيوم', 'فوسفور', 'منجنيز'],
                'glycemic_index': 0,
                'suitable_for': ['صحة الدماغ', 'صحة القلب'],
                'avoid_for': ['حساسية المكسرات']
            }
        }
        
        # الوجبات المقترحة
        self.meal_suggestions = {
            DietType.GENERAL.value: {
                MealType.BREAKFAST.value: [
                    {
                        'name': 'إفطار صحي متوازن',
                        'foods': [
                            {'food': 'eggs', 'quantity': 2, 'unit': 'حبة'},
                            {'food': 'bread', 'quantity': 1, 'unit': 'رغيف صغير'},
                            {'food': 'tomatoes', 'quantity': 1, 'unit': 'حبة متوسطة'},
                            {'food': 'cucumber', 'quantity': 1, 'unit': 'حبة صغيرة'}
                        ],
                        'total_calories': 320,
                        'preparation_time': 15
                    }
                ],
                MealType.LUNCH.value: [
                    {
                        'name': 'غداء متوازن',
                        'foods': [
                            {'food': 'chicken_breast', 'quantity': 150, 'unit': 'جرام'},
                            {'food': 'rice', 'quantity': 100, 'unit': 'جرام مطبوخ'},
                            {'food': 'spinach', 'quantity': 100, 'unit': 'جرام'},
                            {'food': 'tomatoes', 'quantity': 1, 'unit': 'حبة متوسطة'}
                        ],
                        'total_calories': 420,
                        'preparation_time': 30
                    }
                ],
                MealType.DINNER.value: [
                    {
                        'name': 'عشاء خفيف',
                        'foods': [
                            {'food': 'fish', 'quantity': 120, 'unit': 'جرام'},
                            {'food': 'cucumber', 'quantity': 1, 'unit': 'حبة متوسطة'},
                            {'food': 'yogurt', 'quantity': 150, 'unit': 'جرام'}
                        ],
                        'total_calories': 280,
                        'preparation_time': 20
                    }
                ],
                MealType.SNACK.value: [
                    {
                        'name': 'وجبة خفيفة صحية',
                        'foods': [
                            {'food': 'apple', 'quantity': 1, 'unit': 'حبة متوسطة'},
                            {'food': 'almonds', 'quantity': 10, 'unit': 'حبة'}
                        ],
                        'total_calories': 120,
                        'preparation_time': 0
                    }
                ]
            },
            DietType.DIABETIC.value: {
                MealType.BREAKFAST.value: [
                    {
                        'name': 'إفطار لمرضى السكري',
                        'foods': [
                            {'food': 'eggs', 'quantity': 2, 'unit': 'حبة'},
                            {'food': 'spinach', 'quantity': 100, 'unit': 'جرام'},
                            {'food': 'tomatoes', 'quantity': 1, 'unit': 'حبة صغيرة'}
                        ],
                        'total_calories': 210,
                        'preparation_time': 10
                    }
                ],
                MealType.LUNCH.value: [
                    {
                        'name': 'غداء لمرضى السكري',
                        'foods': [
                            {'food': 'fish', 'quantity': 150, 'unit': 'جرام'},
                            {'food': 'brown_rice', 'quantity': 80, 'unit': 'جرام مطبوخ'},
                            {'food': 'cucumber', 'quantity': 1, 'unit': 'حبة متوسطة'},
                            {'food': 'spinach', 'quantity': 100, 'unit': 'جرام'}
                        ],
                        'total_calories': 320,
                        'preparation_time': 25
                    }
                ]
            },
            DietType.WEIGHT_LOSS.value: {
                MealType.BREAKFAST.value: [
                    {
                        'name': 'إفطار لإنقاص الوزن',
                        'foods': [
                            {'food': 'eggs', 'quantity': 1, 'unit': 'حبة'},
                            {'food': 'spinach', 'quantity': 150, 'unit': 'جرام'},
                            {'food': 'tomatoes', 'quantity': 1, 'unit': 'حبة متوسطة'}
                        ],
                        'total_calories': 120,
                        'preparation_time': 8
                    }
                ],
                MealType.LUNCH.value: [
                    {
                        'name': 'غداء لإنقاص الوزن',
                        'foods': [
                            {'food': 'chicken_breast', 'quantity': 120, 'unit': 'جرام'},
                            {'food': 'cucumber', 'quantity': 2, 'unit': 'حبة متوسطة'},
                            {'food': 'tomatoes', 'quantity': 2, 'unit': 'حبة متوسطة'}
                        ],
                        'total_calories': 230,
                        'preparation_time': 15
                    }
                ]
            }
        }
        
        # معاملات حساب الاحتياجات اليومية
        self.bmr_coefficients = {
            'male': {'a': 88.362, 'b': 13.397, 'c': 4.799, 'd': 5.677},
            'female': {'a': 447.593, 'b': 9.247, 'c': 3.098, 'd': 4.330}
        }
        
        self.activity_multipliers = {
            ActivityLevel.SEDENTARY.value: 1.2,
            ActivityLevel.LIGHT.value: 1.375,
            ActivityLevel.MODERATE.value: 1.55,
            ActivityLevel.ACTIVE.value: 1.725,
            ActivityLevel.VERY_ACTIVE.value: 1.9
        }
    
    def create_nutrition_profile(self, patient_id: str, personal_data: Dict,
                               health_data: Dict) -> Dict:
        """
        إنشاء ملف التغذية الشخصي
        
        Args:
            patient_id: معرف المريض
            personal_data: البيانات الشخصية
            health_data: البيانات الصحية
            
        Returns:
            Dict: ملف التغذية
        """
        try:
            profile_id = str(uuid.uuid4())
            
            # حساب BMR (معدل الأيض الأساسي)
            bmr = self._calculate_bmr(
                personal_data['gender'],
                personal_data['weight'],
                personal_data['height'],
                personal_data['age']
            )
            
            # حساب الاحتياجات اليومية من السعرات
            daily_calories = self._calculate_daily_calories(
                bmr, personal_data['activity_level']
            )
            
            # حساب BMI
            bmi = self._calculate_bmi(personal_data['weight'], personal_data['height'])
            
            # إنشاء الملف الشخصي
            nutrition_profile = NutritionProfile(
                profile_id=profile_id,
                patient_id=patient_id,
                age=personal_data['age'],
                gender=personal_data['gender'],
                height=personal_data['height'],
                weight=personal_data['weight'],
                activity_level=personal_data['activity_level'],
                health_conditions=health_data.get('conditions', []),
                allergies=health_data.get('allergies', []),
                dietary_preferences=health_data.get('preferences', []),
                daily_calorie_needs=daily_calories,
                bmr=bmr,
                bmi=bmi
            )
            
            # تحديد نوع النظام الغذائي المناسب
            recommended_diet = self._recommend_diet_type(nutrition_profile)
            
            # إنشاء خطة غذائية أولية
            meal_plan = self._create_initial_meal_plan(nutrition_profile, recommended_diet)
            
            return {
                'success': True,
                'nutrition_profile': nutrition_profile.__dict__,
                'recommended_diet': recommended_diet,
                'meal_plan': meal_plan,
                'health_assessment': self._assess_nutritional_health(nutrition_profile)
            }
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء ملف التغذية: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_bmr(self, gender: str, weight: float, height: float, age: int) -> float:
        """حساب معدل الأيض الأساسي باستخدام معادلة Harris-Benedict"""
        coeffs = self.bmr_coefficients[gender.lower()]
        bmr = (coeffs['a'] + 
               coeffs['b'] * weight + 
               coeffs['c'] * height - 
               coeffs['d'] * age)
        return round(bmr, 1)
    
    def _calculate_daily_calories(self, bmr: float, activity_level: str) -> float:
        """حساب الاحتياجات اليومية من السعرات"""
        multiplier = self.activity_multipliers.get(activity_level, 1.2)
        return round(bmr * multiplier, 0)
    
    def _calculate_bmi(self, weight: float, height: float) -> float:
        """حساب مؤشر كتلة الجسم"""
        height_m = height / 100  # تحويل من سم إلى متر
        bmi = weight / (height_m ** 2)
        return round(bmi, 1)
    
    def _recommend_diet_type(self, profile: NutritionProfile) -> str:
        """توصية نوع النظام الغذائي المناسب"""
        # فحص الحالات الصحية
        conditions = [c.lower() for c in profile.health_conditions]
        
        if 'diabetes' in conditions or 'سكري' in conditions:
            return DietType.DIABETIC.value
        elif 'hypertension' in conditions or 'ضغط' in conditions:
            return DietType.HYPERTENSION.value
        elif 'heart' in conditions or 'قلب' in conditions:
            return DietType.HEART_HEALTHY.value
        elif profile.bmi > 30:
            return DietType.WEIGHT_LOSS.value
        elif profile.bmi < 18.5:
            return DietType.WEIGHT_GAIN.value
        else:
            return DietType.GENERAL.value
    
    def _create_initial_meal_plan(self, profile: NutritionProfile, diet_type: str) -> Dict:
        """إنشاء خطة غذائية أولية"""
        meal_plan = {
            'plan_id': str(uuid.uuid4()),
            'patient_id': profile.patient_id,
            'diet_type': diet_type,
            'daily_calories_target': profile.daily_calorie_needs,
            'created_at': datetime.now().isoformat(),
            'duration_days': 7,
            'meals': {}
        }
        
        # إنشاء وجبات لأسبوع واحد
        for day in range(1, 8):
            day_meals = {}
            daily_calories = 0
            
            # توزيع السعرات على الوجبات
            calorie_distribution = {
                MealType.BREAKFAST.value: 0.25,
                MealType.LUNCH.value: 0.35,
                MealType.DINNER.value: 0.30,
                MealType.SNACK.value: 0.10
            }
            
            for meal_type, percentage in calorie_distribution.items():
                target_calories = profile.daily_calorie_needs * percentage
                
                # اختيار وجبة مناسبة
                meal = self._select_appropriate_meal(
                    diet_type, meal_type, target_calories, profile
                )
                
                if meal:
                    day_meals[meal_type] = meal
                    daily_calories += meal['total_calories']
            
            meal_plan['meals'][f'day_{day}'] = {
                'meals': day_meals,
                'total_calories': daily_calories,
                'date': (datetime.now() + timedelta(days=day-1)).date().isoformat()
            }
        
        return meal_plan
    
    def _select_appropriate_meal(self, diet_type: str, meal_type: str, 
                               target_calories: float, profile: NutritionProfile) -> Optional[Dict]:
        """اختيار وجبة مناسبة"""
        if diet_type not in self.meal_suggestions:
            diet_type = DietType.GENERAL.value
        
        if meal_type not in self.meal_suggestions[diet_type]:
            return None
        
        available_meals = self.meal_suggestions[diet_type][meal_type]
        
        # فلترة الوجبات حسب الحساسية
        suitable_meals = []
        for meal in available_meals:
            is_suitable = True
            for food_item in meal['foods']:
                food_data = self.foods_database.get(food_item['food'])
                if food_data:
                    # فحص الحساسية
                    for allergy in profile.allergies:
                        if allergy.lower() in food_data['name'].lower():
                            is_suitable = False
                            break
                    
                    # فحص موانع الاستعمال
                    for condition in profile.health_conditions:
                        if condition.lower() in [avoid.lower() for avoid in food_data.get('avoid_for', [])]:
                            is_suitable = False
                            break
                
                if not is_suitable:
                    break
            
            if is_suitable:
                suitable_meals.append(meal)
        
        # اختيار أقرب وجبة للسعرات المطلوبة
        if suitable_meals:
            return min(suitable_meals, 
                      key=lambda x: abs(x['total_calories'] - target_calories))
        
        return None
    
    def _assess_nutritional_health(self, profile: NutritionProfile) -> Dict:
        """تقييم الحالة التغذوية"""
        assessment = {
            'bmi_status': self._get_bmi_status(profile.bmi),
            'calorie_needs': profile.daily_calorie_needs,
            'health_risks': [],
            'recommendations': []
        }
        
        # تقييم BMI
        if profile.bmi < 18.5:
            assessment['health_risks'].append('نقص الوزن')
            assessment['recommendations'].append('زيادة السعرات الحرارية وبناء العضلات')
        elif profile.bmi > 30:
            assessment['health_risks'].append('السمنة')
            assessment['recommendations'].append('تقليل السعرات وزيادة النشاط البدني')
        elif profile.bmi > 25:
            assessment['health_risks'].append('زيادة الوزن')
            assessment['recommendations'].append('اتباع نظام غذائي متوازن')
        
        # تقييم الحالات الصحية
        for condition in profile.health_conditions:
            if 'diabetes' in condition.lower() or 'سكري' in condition:
                assessment['recommendations'].append('تجنب السكريات البسيطة والتركيز على الألياف')
            elif 'hypertension' in condition.lower() or 'ضغط' in condition:
                assessment['recommendations'].append('تقليل الصوديوم وزيادة البوتاسيوم')
        
        return assessment
    
    def _get_bmi_status(self, bmi: float) -> str:
        """تحديد حالة BMI"""
        if bmi < 18.5:
            return 'نقص الوزن'
        elif bmi < 25:
            return 'وزن طبيعي'
        elif bmi < 30:
            return 'زيادة الوزن'
        else:
            return 'سمنة'
    
    def track_food_intake(self, patient_id: str, meal_data: Dict) -> Dict:
        """
        تتبع تناول الطعام
        
        Args:
            patient_id: معرف المريض
            meal_data: بيانات الوجبة
            
        Returns:
            Dict: سجل الوجبة
        """
        try:
            intake_id = str(uuid.uuid4())
            
            # حساب القيم الغذائية
            nutritional_values = self._calculate_meal_nutrition(meal_data['foods'])
            
            # إنشاء سجل الوجبة
            food_intake = {
                'intake_id': intake_id,
                'patient_id': patient_id,
                'date': datetime.now().date().isoformat(),
                'time': datetime.now().time().isoformat(),
                'meal_type': meal_data['meal_type'],
                'foods': meal_data['foods'],
                'nutritional_values': nutritional_values,
                'notes': meal_data.get('notes', ''),
                'mood_before': meal_data.get('mood_before'),
                'mood_after': meal_data.get('mood_after'),
                'hunger_level': meal_data.get('hunger_level'),
                'satisfaction_level': meal_data.get('satisfaction_level')
            }
            
            # تحليل التقدم اليومي
            daily_progress = self._analyze_daily_progress(patient_id, food_intake)
            
            # توصيات فورية
            immediate_recommendations = self._get_immediate_recommendations(
                nutritional_values, daily_progress
            )
            
            return {
                'success': True,
                'food_intake': food_intake,
                'daily_progress': daily_progress,
                'recommendations': immediate_recommendations
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_meal_nutrition(self, foods: List[Dict]) -> Dict:
        """حساب القيم الغذائية للوجبة"""
        total_nutrition = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0,
            'fiber': 0,
            'vitamins': set(),
            'minerals': set()
        }
        
        for food_item in foods:
            food_code = food_item['food']
            quantity = food_item['quantity']
            
            if food_code in self.foods_database:
                food_data = self.foods_database[food_code]
                
                # تحويل الكمية إلى 100 جرام
                factor = quantity / 100
                
                total_nutrition['calories'] += food_data['calories_per_100g'] * factor
                total_nutrition['protein'] += food_data['protein'] * factor
                total_nutrition['carbs'] += food_data['carbs'] * factor
                total_nutrition['fat'] += food_data['fat'] * factor
                total_nutrition['fiber'] += food_data['fiber'] * factor
                
                # إضافة الفيتامينات والمعادن
                total_nutrition['vitamins'].update(food_data.get('vitamins', []))
                total_nutrition['minerals'].update(food_data.get('minerals', []))
        
        # تحويل المجموعات إلى قوائم
        total_nutrition['vitamins'] = list(total_nutrition['vitamins'])
        total_nutrition['minerals'] = list(total_nutrition['minerals'])
        
        # تقريب الأرقام
        for key in ['calories', 'protein', 'carbs', 'fat', 'fiber']:
            total_nutrition[key] = round(total_nutrition[key], 1)
        
        return total_nutrition
    
    def _analyze_daily_progress(self, patient_id: str, current_intake: Dict) -> Dict:
        """تحليل التقدم اليومي"""
        # في التطبيق الحقيقي، سيتم الحصول على البيانات من قاعدة البيانات
        # هنا محاكاة للتحليل
        
        daily_target = 2000  # افتراضي
        consumed_today = current_intake['nutritional_values']['calories']
        
        progress = {
            'date': current_intake['date'],
            'calories_target': daily_target,
            'calories_consumed': consumed_today,
            'calories_remaining': daily_target - consumed_today,
            'progress_percentage': round((consumed_today / daily_target) * 100, 1),
            'meals_logged': 1,  # افتراضي
            'water_intake': 0,  # يمكن إضافتها لاحقاً
            'macronutrient_balance': {
                'protein_percentage': 20,
                'carbs_percentage': 50,
                'fat_percentage': 30
            }
        }
        
        return progress
    
    def _get_immediate_recommendations(self, nutrition: Dict, progress: Dict) -> List[str]:
        """الحصول على توصيات فورية"""
        recommendations = []
        
        # توصيات بناءً على السعرات
        if progress['calories_remaining'] > 500:
            recommendations.append('تحتاج لتناول وجبة أخرى لتحقيق هدفك اليومي')
        elif progress['calories_remaining'] < -200:
            recommendations.append('تجاوزت هدفك اليومي، تجنب الوجبات الإضافية')
        
        # توصيات بناءً على البروتين
        if nutrition['protein'] < 20:
            recommendations.append('أضف مصدر بروتين لوجبتك القادمة')
        
        # توصيات بناءً على الألياف
        if nutrition['fiber'] < 5:
            recommendations.append('أضف المزيد من الخضروات والفواكه')
        
        return recommendations
    
    def generate_meal_plan(self, patient_id: str, preferences: Dict, 
                          duration_days: int = 7) -> Dict:
        """
        إنتاج خطة غذائية مخصصة
        
        Args:
            patient_id: معرف المريض
            preferences: التفضيلات الغذائية
            duration_days: مدة الخطة بالأيام
            
        Returns:
            Dict: الخطة الغذائية
        """
        try:
            # الحصول على ملف التغذية
            # في التطبيق الحقيقي، سيتم الحصول على البيانات من قاعدة البيانات
            
            plan_id = str(uuid.uuid4())
            diet_type = preferences.get('diet_type', DietType.GENERAL.value)
            calorie_target = preferences.get('calorie_target', 2000)
            
            meal_plan = {
                'plan_id': plan_id,
                'patient_id': patient_id,
                'diet_type': diet_type,
                'calorie_target': calorie_target,
                'duration_days': duration_days,
                'created_at': datetime.now().isoformat(),
                'preferences': preferences,
                'daily_plans': {}
            }
            
            # إنشاء خطة يومية لكل يوم
            for day in range(1, duration_days + 1):
                daily_plan = self._create_daily_meal_plan(
                    diet_type, calorie_target, preferences, day
                )
                meal_plan['daily_plans'][f'day_{day}'] = daily_plan
            
            # إنشاء قائمة التسوق
            shopping_list = self._generate_shopping_list(meal_plan)
            
            # حساب التكلفة المتوقعة
            estimated_cost = self._estimate_meal_plan_cost(meal_plan)
            
            return {
                'success': True,
                'meal_plan': meal_plan,
                'shopping_list': shopping_list,
                'estimated_cost': estimated_cost,
                'nutritional_summary': self._summarize_plan_nutrition(meal_plan)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_daily_meal_plan(self, diet_type: str, calorie_target: float,
                              preferences: Dict, day_number: int) -> Dict:
        """إنشاء خطة يومية"""
        daily_plan = {
            'day': day_number,
            'date': (datetime.now() + timedelta(days=day_number-1)).date().isoformat(),
            'meals': {},
            'total_calories': 0,
            'total_protein': 0,
            'total_carbs': 0,
            'total_fat': 0
        }
        
        # توزيع السعرات على الوجبات
        calorie_distribution = {
            MealType.BREAKFAST.value: 0.25,
            MealType.LUNCH.value: 0.35,
            MealType.DINNER.value: 0.30,
            MealType.SNACK.value: 0.10
        }
        
        for meal_type, percentage in calorie_distribution.items():
            target_calories = calorie_target * percentage
            
            # إنشاء وجبة مخصصة
            meal = self._create_custom_meal(
                diet_type, meal_type, target_calories, preferences, day_number
            )
            
            if meal:
                daily_plan['meals'][meal_type] = meal
                daily_plan['total_calories'] += meal['calories']
                daily_plan['total_protein'] += meal['protein']
                daily_plan['total_carbs'] += meal['carbs']
                daily_plan['total_fat'] += meal['fat']
        
        return daily_plan
    
    def _create_custom_meal(self, diet_type: str, meal_type: str, 
                          target_calories: float, preferences: Dict, day: int) -> Dict:
        """إنشاء وجبة مخصصة"""
        # اختيار أطعمة مناسبة
        suitable_foods = self._filter_suitable_foods(diet_type, preferences)
        
        # بناء الوجبة
        meal_foods = []
        current_calories = 0
        
        # منطق بسيط لبناء الوجبة
        if meal_type == MealType.BREAKFAST.value:
            # إضافة بروتين
            protein_foods = [f for f in suitable_foods if self.foods_database[f]['category'] == 'بروتينات']
            if protein_foods:
                selected_protein = protein_foods[day % len(protein_foods)]
                meal_foods.append({'food': selected_protein, 'quantity': 100, 'unit': 'جرام'})
                current_calories += self.foods_database[selected_protein]['calories_per_100g']
            
            # إضافة خضروات
            vegetable_foods = [f for f in suitable_foods if 'خضروات' in self.foods_database[f]['category']]
            if vegetable_foods:
                selected_vegetable = vegetable_foods[day % len(vegetable_foods)]
                meal_foods.append({'food': selected_vegetable, 'quantity': 150, 'unit': 'جرام'})
                current_calories += self.foods_database[selected_vegetable]['calories_per_100g'] * 1.5
        
        # حساب القيم الغذائية
        nutrition = self._calculate_meal_nutrition(meal_foods)
        
        return {
            'name': f'{meal_type} - اليوم {day}',
            'foods': meal_foods,
            'calories': nutrition['calories'],
            'protein': nutrition['protein'],
            'carbs': nutrition['carbs'],
            'fat': nutrition['fat'],
            'fiber': nutrition['fiber'],
            'preparation_time': 20,
            'instructions': ['تحضير الطعام حسب التعليمات المعتادة']
        }
    
    def _filter_suitable_foods(self, diet_type: str, preferences: Dict) -> List[str]:
        """فلترة الأطعمة المناسبة"""
        suitable_foods = []
        allergies = preferences.get('allergies', [])
        dislikes = preferences.get('dislikes', [])
        
        for food_code, food_data in self.foods_database.items():
            # فحص الحساسية
            is_allergic = any(allergy.lower() in food_data['name'].lower() 
                            for allergy in allergies)
            
            # فحص عدم التفضيل
            is_disliked = any(dislike.lower() in food_data['name'].lower() 
                            for dislike in dislikes)
            
            # فحص مناسبة النظام الغذائي
            is_suitable_for_diet = diet_type in food_data.get('suitable_for', [])
            
            if not is_allergic and not is_disliked and (is_suitable_for_diet or diet_type == DietType.GENERAL.value):
                suitable_foods.append(food_code)
        
        return suitable_foods
    
    def _generate_shopping_list(self, meal_plan: Dict) -> Dict:
        """إنتاج قائمة التسوق"""
        shopping_list = {}
        
        # جمع جميع الأطعمة من الخطة
        for day_key, daily_plan in meal_plan['daily_plans'].items():
            for meal_type, meal in daily_plan['meals'].items():
                for food_item in meal['foods']:
                    food_code = food_item['food']
                    quantity = food_item['quantity']
                    
                    if food_code in shopping_list:
                        shopping_list[food_code]['total_quantity'] += quantity
                    else:
                        food_data = self.foods_database.get(food_code, {})
                        shopping_list[food_code] = {
                            'name': food_data.get('name', food_code),
                            'category': food_data.get('category', 'أخرى'),
                            'total_quantity': quantity,
                            'unit': food_item['unit'],
                            'estimated_price': self._estimate_food_price(food_code, quantity)
                        }
        
        # تنظيم القائمة حسب الفئات
        organized_list = {}
        for food_code, item in shopping_list.items():
            category = item['category']
            if category not in organized_list:
                organized_list[category] = []
            organized_list[category].append(item)
        
        return {
            'shopping_list': organized_list,
            'total_items': len(shopping_list),
            'estimated_total_cost': sum(item['estimated_price'] for item in shopping_list.values())
        }
    
    def _estimate_food_price(self, food_code: str, quantity: float) -> float:
        """تقدير سعر الطعام"""
        # أسعار تقديرية للأطعمة (بالجنيه المصري)
        price_per_kg = {
            'rice': 15,
            'brown_rice': 25,
            'bread': 5,
            'chicken_breast': 80,
            'fish': 60,
            'eggs': 50,  # للكيلو
            'tomatoes': 8,
            'cucumber': 6,
            'spinach': 10,
            'apple': 20,
            'banana': 12,
            'orange': 15,
            'milk': 20,
            'yogurt': 25,
            'almonds': 200,
            'walnuts': 250
        }
        
        price_per_kg_value = price_per_kg.get(food_code, 20)  # سعر افتراضي
        return round((quantity / 1000) * price_per_kg_value, 2)
    
    def _estimate_meal_plan_cost(self, meal_plan: Dict) -> Dict:
        """تقدير تكلفة الخطة الغذائية"""
        total_cost = 0
        daily_costs = []
        
        for day_key, daily_plan in meal_plan['daily_plans'].items():
            daily_cost = 0
            for meal_type, meal in daily_plan['meals'].items():
                for food_item in meal['foods']:
                    food_cost = self._estimate_food_price(
                        food_item['food'], food_item['quantity']
                    )
                    daily_cost += food_cost
            
            daily_costs.append(daily_cost)
            total_cost += daily_cost
        
        return {
            'total_cost': round(total_cost, 2),
            'average_daily_cost': round(total_cost / len(daily_costs), 2),
            'daily_costs': daily_costs,
            'currency': 'EGP'
        }
    
    def _summarize_plan_nutrition(self, meal_plan: Dict) -> Dict:
        """ملخص التغذية للخطة"""
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        days_count = len(meal_plan['daily_plans'])
        
        for daily_plan in meal_plan['daily_plans'].values():
            total_calories += daily_plan['total_calories']
            total_protein += daily_plan['total_protein']
            total_carbs += daily_plan['total_carbs']
            total_fat += daily_plan['total_fat']
        
        return {
            'average_daily_calories': round(total_calories / days_count, 0),
            'average_daily_protein': round(total_protein / days_count, 1),
            'average_daily_carbs': round(total_carbs / days_count, 1),
            'average_daily_fat': round(total_fat / days_count, 1),
            'protein_percentage': round((total_protein * 4 / total_calories) * 100, 1),
            'carbs_percentage': round((total_carbs * 4 / total_calories) * 100, 1),
            'fat_percentage': round((total_fat * 9 / total_calories) * 100, 1)
        }
    
    def get_nutrition_advice(self, patient_id: str, question: str) -> Dict:
        """
        الحصول على نصائح تغذوية
        
        Args:
            patient_id: معرف المريض
            question: السؤال التغذوي
            
        Returns:
            Dict: النصيحة التغذوية
        """
        try:
            # قاعدة بيانات النصائح التغذوية
            nutrition_advice = {
                'weight_loss': {
                    'keywords': ['إنقاص', 'تخسيس', 'وزن', 'رجيم'],
                    'advice': [
                        'قلل من السعرات الحرارية بمقدار 500-750 سعرة يومياً',
                        'اشرب الماء قبل الوجبات',
                        'تناول البروتين في كل وجبة',
                        'أكثر من الخضروات والألياف',
                        'تجنب المشروبات السكرية',
                        'مارس الرياضة بانتظام'
                    ]
                },
                'diabetes': {
                    'keywords': ['سكري', 'سكر', 'جلوكوز'],
                    'advice': [
                        'اختر الكربوهيدرات المعقدة',
                        'تجنب السكريات البسيطة',
                        'تناول وجبات صغيرة متكررة',
                        'أكثر من الألياف',
                        'راقب مؤشر السكر في الأطعمة',
                        'حافظ على وزن صحي'
                    ]
                },
                'heart_health': {
                    'keywords': ['قلب', 'كولسترول', 'ضغط'],
                    'advice': [
                        'قلل من الدهون المشبعة',
                        'أكثر من أوميجا 3',
                        'تناول المكسرات والبذور',
                        'قلل من الصوديوم',
                        'أكثر من الفواكه والخضروات',
                        'تجنب الأطعمة المصنعة'
                    ]
                },
                'general': {
                    'keywords': ['عام', 'صحة', 'تغذية'],
                    'advice': [
                        'تناول 5 حصص من الفواكه والخضروات يومياً',
                        'اشرب 8 أكواب ماء يومياً',
                        'تناول البروتين الخالي من الدهون',
                        'اختر الحبوب الكاملة',
                        'قلل من السكر المضاف',
                        'تناول الطعام ببطء'
                    ]
                }
            }
            
            # تحديد نوع النصيحة المطلوبة
            advice_type = 'general'
            question_lower = question.lower()
            
            for category, data in nutrition_advice.items():
                if any(keyword in question_lower for keyword in data['keywords']):
                    advice_type = category
                    break
            
            selected_advice = nutrition_advice[advice_type]['advice']
            
            # إضافة نصائح مخصصة بناءً على ملف المريض
            # في التطبيق الحقيقي، سيتم الحصول على بيانات المريض
            
            return {
                'success': True,
                'question': question,
                'advice_category': advice_type,
                'recommendations': selected_advice,
                'additional_resources': [
                    'دليل التغذية الصحية',
                    'جدول السعرات الحرارية',
                    'وصفات صحية'
                ],
                'follow_up_questions': [
                    'هل تحتاج لخطة غذائية مخصصة؟',
                    'هل لديك حساسية من أطعمة معينة؟',
                    'ما هو مستوى نشاطك البدني؟'
                ]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_nutrition_trends(self, patient_id: str, period_days: int = 30) -> Dict:
        """
        تحليل اتجاهات التغذية
        
        Args:
            patient_id: معرف المريض
            period_days: فترة التحليل بالأيام
            
        Returns:
            Dict: تحليل الاتجاهات
        """
        try:
            # في التطبيق الحقيقي، سيتم الحصول على البيانات من قاعدة البيانات
            # هنا محاكاة للتحليل
            
            trends_analysis = {
                'patient_id': patient_id,
                'analysis_period': {
                    'start_date': (datetime.now() - timedelta(days=period_days)).date().isoformat(),
                    'end_date': datetime.now().date().isoformat(),
                    'days': period_days
                },
                'calorie_trends': {
                    'average_daily_calories': 1850,
                    'target_calories': 2000,
                    'trend_direction': 'stable',
                    'highest_day': 2200,
                    'lowest_day': 1600
                },
                'macronutrient_balance': {
                    'protein_average': 18,  # نسبة مئوية
                    'carbs_average': 52,
                    'fat_average': 30,
                    'fiber_average': 25  # جرام
                },
                'meal_patterns': {
                    'most_skipped_meal': 'إفطار',
                    'largest_meal': 'غداء',
                    'eating_frequency': 3.2,  # وجبات في اليوم
                    'late_night_eating': 15  # نسبة الأيام
                },
                'food_variety': {
                    'unique_foods_consumed': 45,
                    'most_consumed_category': 'بروتينات',
                    'least_consumed_category': 'فواكه',
                    'variety_score': 7.5  # من 10
                },
                'hydration': {
                    'average_water_intake': 6.5,  # أكواب
                    'target_water_intake': 8,
                    'hydration_consistency': 70  # نسبة الأيام التي تم تحقيق الهدف
                },
                'recommendations': [
                    'زيادة تناول الفواكه إلى 3 حصص يومياً',
                    'عدم تفويت وجبة الإفطار',
                    'زيادة شرب الماء',
                    'تقليل الأكل المتأخر'
                ],
                'progress_indicators': {
                    'weight_change': -1.2,  # كيلوجرام
                    'energy_levels': 'محسن',
                    'sleep_quality': 'مستقر',
                    'mood_stability': 'محسن'
                }
            }
            
            return {
                'success': True,
                'trends_analysis': trends_analysis,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

