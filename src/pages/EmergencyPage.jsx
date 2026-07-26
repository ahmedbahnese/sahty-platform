import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Phone, 
  MapPin, 
  Clock, 
  AlertTriangle,
  Ambulance,
  Heart,
  Shield,
  Navigation,
  User,
  Calendar,
  FileText,
  Zap,
  Activity,
  Stethoscope
} from 'lucide-react'

export default function EmergencyPage() {
  const [emergencyForm, setEmergencyForm] = useState({
    name: '',
    phone: '',
    location: '',
    emergencyType: '',
    description: '',
    severity: ''
  })
  const [isEmergencyActive, setIsEmergencyActive] = useState(false)
  const [nearbyHospitals, setNearbyHospitals] = useState([])
  const [emergencyContacts, setEmergencyContacts] = useState([])

  // أرقام الطوارئ
  const emergencyNumbers = [
    { name: 'الإسعاف', number: '123', icon: Ambulance, color: 'bg-red-500' },
    { name: 'الشرطة', number: '122', icon: Shield, color: 'bg-blue-500' },
    { name: 'الإطفاء', number: '180', icon: Zap, color: 'bg-orange-500' },
    { name: 'الغاز الطبيعي', number: '129', icon: AlertTriangle, color: 'bg-yellow-500' }
  ]

  // أنواع الطوارئ
  const emergencyTypes = [
    'حادث سير',
    'نوبة قلبية',
    'صعوبة في التنفس',
    'نزيف شديد',
    'كسور',
    'حروق',
    'تسمم',
    'فقدان الوعي',
    'ألم شديد',
    'أخرى'
  ]

  // مستويات الخطورة
  const severityLevels = [
    { value: 'critical', label: 'حرج - يهدد الحياة', color: 'text-red-600' },
    { value: 'urgent', label: 'عاجل - يحتاج تدخل سريع', color: 'text-orange-600' },
    { value: 'moderate', label: 'متوسط - يحتاج رعاية طبية', color: 'text-yellow-600' },
    { value: 'minor', label: 'بسيط - غير عاجل', color: 'text-green-600' }
  ]

  // المستشفيات القريبة (بيانات وهمية)
  const mockHospitals = [
    {
      id: 1,
      name: 'مستشفى القاهرة الجديدة',
      address: 'التجمع الأول، القاهرة الجديدة',
      distance: '2.5 كم',
      phone: '0227584000',
      emergencyAvailable: true,
      estimatedTime: '8 دقائق',
      specialties: ['طوارئ', 'قلب', 'جراحة']
    },
    {
      id: 2,
      name: 'مستشفى دار الفؤاد',
      address: 'مدينة نصر، القاهرة',
      distance: '4.2 كم',
      phone: '0225555555',
      emergencyAvailable: true,
      estimatedTime: '12 دقيقة',
      specialties: ['طوارئ', 'أعصاب', 'عظام']
    },
    {
      id: 3,
      name: 'مستشفى الشروق',
      address: 'مدينة الشروق',
      distance: '6.8 كم',
      phone: '0244444444',
      emergencyAvailable: true,
      estimatedTime: '18 دقيقة',
      specialties: ['طوارئ', 'أطفال', 'نساء وتوليد']
    }
  ]

  useEffect(() => {
    setNearbyHospitals(mockHospitals)
  }, [])

  const handleFormChange = (field, value) => {
    setEmergencyForm(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleEmergencyCall = (number) => {
    window.location.href = `tel:${number}`
  }

  const handleEmergencySubmit = async (e) => {
    e.preventDefault()
    setIsEmergencyActive(true)
    
    // محاكاة إرسال طلب الطوارئ
    setTimeout(() => {
      alert('تم إرسال طلب الطوارئ بنجاح! سيتم التواصل معك قريباً')
    }, 1000)
  }

  const handleHospitalCall = (phone) => {
    window.location.href = `tel:${phone}`
  }

  const handleGetDirections = (hospitalName) => {
    // فتح خرائط جوجل للتوجيه
    const query = encodeURIComponent(hospitalName)
    window.open(`https://www.google.com/maps/search/${query}`, '_blank')
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* الرأس */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-4">
            <div className="bg-red-100 p-4 rounded-full">
              <AlertTriangle className="h-12 w-12 text-red-600" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            خدمات الطوارئ الطبية
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            خدمة طوارئ متاحة على مدار الساعة للحالات العاجلة والطارئة
          </p>
        </div>

        {/* أرقام الطوارئ السريعة */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            أرقام الطوارئ السريعة
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {emergencyNumbers.map((emergency, index) => {
              const IconComponent = emergency.icon
              return (
                <button
                  key={index}
                  onClick={() => handleEmergencyCall(emergency.number)}
                  className={`${emergency.color} text-white p-6 rounded-xl hover:opacity-90 transition-opacity`}
                >
                  <div className="text-center">
                    <IconComponent className="h-8 w-8 mx-auto mb-2" />
                    <div className="font-bold text-lg">{emergency.number}</div>
                    <div className="text-sm">{emergency.name}</div>
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* نموذج طلب الطوارئ */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
              <Phone className="h-6 w-6 text-red-600 ml-2" />
              طلب مساعدة طارئة
            </h3>

            {isEmergencyActive && (
              <Alert className="mb-6 border-red-200 bg-red-50">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription className="text-red-700">
                  تم تفعيل حالة الطوارئ. سيتم التواصل معك خلال دقائق.
                </AlertDescription>
              </Alert>
            )}

            <form onSubmit={handleEmergencySubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="name">الاسم *</Label>
                  <Input
                    id="name"
                    type="text"
                    required
                    value={emergencyForm.name}
                    onChange={(e) => handleFormChange('name', e.target.value)}
                    placeholder="اسمك الكامل"
                  />
                </div>
                <div>
                  <Label htmlFor="phone">رقم الهاتف *</Label>
                  <Input
                    id="phone"
                    type="tel"
                    required
                    value={emergencyForm.phone}
                    onChange={(e) => handleFormChange('phone', e.target.value)}
                    placeholder="01xxxxxxxxx"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="location">الموقع الحالي *</Label>
                <Input
                  id="location"
                  type="text"
                  required
                  value={emergencyForm.location}
                  onChange={(e) => handleFormChange('location', e.target.value)}
                  placeholder="العنوان التفصيلي أو أقرب معلم"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="emergencyType">نوع الطارئ *</Label>
                  <select
                    id="emergencyType"
                    required
                    value={emergencyForm.emergencyType}
                    onChange={(e) => handleFormChange('emergencyType', e.target.value)}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
                  >
                    <option value="">اختر نوع الطارئ</option>
                    {emergencyTypes.map((type, index) => (
                      <option key={index} value={type}>{type}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label htmlFor="severity">مستوى الخطورة *</Label>
                  <select
                    id="severity"
                    required
                    value={emergencyForm.severity}
                    onChange={(e) => handleFormChange('severity', e.target.value)}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
                  >
                    <option value="">اختر مستوى الخطورة</option>
                    {severityLevels.map((level, index) => (
                      <option key={index} value={level.value}>{level.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <Label htmlFor="description">وصف الحالة *</Label>
                <textarea
                  id="description"
                  required
                  rows={3}
                  value={emergencyForm.description}
                  onChange={(e) => handleFormChange('description', e.target.value)}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
                  placeholder="اشرح الحالة بالتفصيل..."
                />
              </div>

              <Button
                type="submit"
                className="w-full bg-red-600 hover:bg-red-700 text-lg py-3"
                disabled={isEmergencyActive}
              >
                <AlertTriangle className="h-5 w-5 ml-2" />
                {isEmergencyActive ? 'تم إرسال الطلب' : 'إرسال طلب طوارئ'}
              </Button>
            </form>
          </div>

          {/* المستشفيات القريبة */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
              <MapPin className="h-6 w-6 text-blue-600 ml-2" />
              المستشفيات القريبة
            </h3>

            <div className="space-y-4">
              {nearbyHospitals.map(hospital => (
                <div key={hospital.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="font-semibold text-gray-900">{hospital.name}</h4>
                      <p className="text-sm text-gray-600 flex items-center mt-1">
                        <MapPin className="h-4 w-4 ml-1" />
                        {hospital.address}
                      </p>
                    </div>
                    <div className="text-left">
                      <div className="text-sm font-medium text-blue-600">{hospital.distance}</div>
                      <div className="text-xs text-gray-500">{hospital.estimatedTime}</div>
                    </div>
                  </div>

                  <div className="flex items-center mb-3">
                    <div className="flex items-center text-sm text-gray-600">
                      <Phone className="h-4 w-4 ml-1" />
                      <span>{hospital.phone}</span>
                    </div>
                    {hospital.emergencyAvailable && (
                      <span className="bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded-full mr-3">
                        طوارئ متاح
                      </span>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-1 mb-3">
                    {hospital.specialties.map((specialty, index) => (
                      <span key={index} className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded">
                        {specialty}
                      </span>
                    ))}
                  </div>

                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      onClick={() => handleHospitalCall(hospital.phone)}
                      className="bg-red-600 hover:bg-red-700 flex-1"
                    >
                      <Phone className="h-4 w-4 ml-1" />
                      اتصال
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleGetDirections(hospital.name)}
                      className="flex-1"
                    >
                      <Navigation className="h-4 w-4 ml-1" />
                      الاتجاهات
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* نصائح الإسعافات الأولية */}
        <div className="mt-8 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <Heart className="h-6 w-6 text-red-600 ml-2" />
            نصائح الإسعافات الأولية
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-red-50 p-4 rounded-lg">
              <h4 className="font-semibold text-red-800 mb-2">النزيف الشديد</h4>
              <ul className="text-sm text-red-700 space-y-1">
                <li>• اضغط مباشرة على الجرح</li>
                <li>• ارفع العضو المصاب</li>
                <li>• لا تزيل الضمادة المشبعة</li>
                <li>• اطلب المساعدة فوراً</li>
              </ul>
            </div>

            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-semibold text-blue-800 mb-2">صعوبة التنفس</h4>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• اجعل المريض يجلس منتصباً</li>
                <li>• فك الملابس الضيقة</li>
                <li>• تأكد من وضوح مجرى الهواء</li>
                <li>• ابق هادئاً وطمئن المريض</li>
              </ul>
            </div>

            <div className="bg-green-50 p-4 rounded-lg">
              <h4 className="font-semibold text-green-800 mb-2">فقدان الوعي</h4>
              <ul className="text-sm text-green-700 space-y-1">
                <li>• تحقق من الاستجابة</li>
                <li>• ضع المريض في وضع الإفاقة</li>
                <li>• تأكد من التنفس</li>
                <li>• لا تترك المريض وحده</li>
              </ul>
            </div>
          </div>
        </div>

        {/* معلومات مهمة */}
        <div className="mt-8 bg-gradient-to-r from-red-50 to-orange-50 border border-red-200 rounded-xl p-6">
          <div className="flex items-start">
            <AlertTriangle className="h-6 w-6 text-red-600 ml-3 mt-1 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-semibold text-red-800 mb-2">معلومات مهمة</h3>
              <div className="text-red-700 space-y-2">
                <p>• في حالات الطوارئ الحرجة، اتصل بالإسعاف (123) مباشرة</p>
                <p>• احتفظ بهدوئك وتحدث بوضوح عند الاتصال</p>
                <p>• اذكر موقعك بدقة ونوع الطارئ</p>
                <p>• لا تنقل المصاب إلا إذا كان في خطر إضافي</p>
                <p>• ابق مع المصاب حتى وصول المساعدة</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

