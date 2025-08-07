import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Droplets, 
  Search, 
  MapPin, 
  Phone, 
  Clock, 
  Heart,
  User,
  Calendar,
  Filter,
  Plus,
  AlertCircle,
  CheckCircle,
  Star
} from 'lucide-react'

export default function BloodBankPage() {
  const [activeTab, setActiveTab] = useState('search')
  const [searchFilters, setSearchFilters] = useState({
    bloodType: '',
    city: '',
    urgency: ''
  })
  const [donationForm, setDonationForm] = useState({
    name: '',
    phone: '',
    bloodType: '',
    city: '',
    lastDonation: '',
    medicalConditions: '',
    available: true
  })
  const [requests, setRequests] = useState([])
  const [donors, setDonors] = useState([])
  const [loading, setLoading] = useState(false)

  // بيانات وهمية لطلبات الدم
  const mockRequests = [
    {
      id: 1,
      patientName: 'أحمد محمد علي',
      bloodType: 'O+',
      unitsNeeded: 3,
      hospital: 'مستشفى القاهرة الجديدة',
      city: 'القاهرة',
      urgency: 'عاجل',
      contactPhone: '01234567890',
      requestDate: '2024-01-15',
      description: 'حالة طوارئ - حادث سير',
      status: 'نشط'
    },
    {
      id: 2,
      patientName: 'فاطمة أحمد حسن',
      bloodType: 'A+',
      unitsNeeded: 2,
      hospital: 'مستشفى الإسكندرية الدولي',
      city: 'الإسكندرية',
      urgency: 'متوسط',
      contactPhone: '01234567891',
      requestDate: '2024-01-14',
      description: 'عملية جراحية مجدولة',
      status: 'نشط'
    },
    {
      id: 3,
      patientName: 'محمد حسام الدين',
      bloodType: 'B-',
      unitsNeeded: 1,
      hospital: 'مستشفى الجيزة التخصصي',
      city: 'الجيزة',
      urgency: 'عاجل جداً',
      contactPhone: '01234567892',
      requestDate: '2024-01-15',
      description: 'حالة طوارئ - نزيف داخلي',
      status: 'نشط'
    }
  ]

  // بيانات وهمية للمتبرعين
  const mockDonors = [
    {
      id: 1,
      name: 'سارة محمد إبراهيم',
      bloodType: 'O+',
      city: 'القاهرة',
      phone: '01234567893',
      lastDonation: '2023-10-15',
      totalDonations: 8,
      rating: 4.9,
      available: true,
      verified: true
    },
    {
      id: 2,
      name: 'عمر عبد الرحمن',
      bloodType: 'A+',
      city: 'الإسكندرية',
      phone: '01234567894',
      lastDonation: '2023-11-20',
      totalDonations: 5,
      rating: 4.7,
      available: true,
      verified: true
    },
    {
      id: 3,
      name: 'نورا أحمد سالم',
      bloodType: 'B-',
      city: 'الجيزة',
      phone: '01234567895',
      lastDonation: '2023-09-10',
      totalDonations: 12,
      rating: 5.0,
      available: true,
      verified: true
    }
  ]

  const bloodTypes = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
  const cities = ['القاهرة', 'الإسكندرية', 'الجيزة', 'الشرقية', 'البحيرة', 'المنوفية']
  const urgencyLevels = ['عاجل جداً', 'عاجل', 'متوسط', 'غير عاجل']

  useEffect(() => {
    setRequests(mockRequests)
    setDonors(mockDonors)
  }, [])

  const handleSearchFilterChange = (field, value) => {
    setSearchFilters(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleDonationFormChange = (field, value) => {
    setDonationForm(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleDonationSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    // محاكاة إرسال البيانات
    setTimeout(() => {
      setLoading(false)
      alert('تم تسجيلك كمتبرع بنجاح!')
      setDonationForm({
        name: '',
        phone: '',
        bloodType: '',
        city: '',
        lastDonation: '',
        medicalConditions: '',
        available: true
      })
    }, 2000)
  }

  const handleContactDonor = (donorId) => {
    console.log('التواصل مع المتبرع:', donorId)
  }

  const handleRequestHelp = (requestId) => {
    console.log('المساعدة في الطلب:', requestId)
  }

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'عاجل جداً': return 'text-red-600 bg-red-100'
      case 'عاجل': return 'text-orange-600 bg-orange-100'
      case 'متوسط': return 'text-yellow-600 bg-yellow-100'
      default: return 'text-green-600 bg-green-100'
    }
  }

  const getBloodTypeColor = (bloodType) => {
    const colors = {
      'O+': 'bg-red-100 text-red-800',
      'O-': 'bg-red-200 text-red-900',
      'A+': 'bg-blue-100 text-blue-800',
      'A-': 'bg-blue-200 text-blue-900',
      'B+': 'bg-green-100 text-green-800',
      'B-': 'bg-green-200 text-green-900',
      'AB+': 'bg-purple-100 text-purple-800',
      'AB-': 'bg-purple-200 text-purple-900'
    }
    return colors[bloodType] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* الرأس */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-4">
            <div className="bg-red-100 p-4 rounded-full">
              <Droplets className="h-12 w-12 text-red-600" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            بنك الدم الرقمي
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            منصة شاملة للتبرع بالدم والبحث عن متبرعين في حالات الطوارئ
          </p>
        </div>

        {/* إحصائيات سريعة */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 text-center">
            <div className="text-3xl font-bold text-red-600 mb-2">1,250</div>
            <div className="text-gray-600">متبرع نشط</div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">89</div>
            <div className="text-gray-600">طلب نشط</div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">3,420</div>
            <div className="text-gray-600">عملية تبرع</div>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 text-center">
            <div className="text-3xl font-bold text-purple-600 mb-2">24/7</div>
            <div className="text-gray-600">خدمة متواصلة</div>
          </div>
        </div>

        {/* التبويبات */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 mb-8">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 rtl:space-x-reverse px-6">
              <button
                onClick={() => setActiveTab('search')}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === 'search'
                    ? 'border-red-500 text-red-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                البحث عن متبرعين
              </button>
              <button
                onClick={() => setActiveTab('requests')}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === 'requests'
                    ? 'border-red-500 text-red-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                طلبات الدم
              </button>
              <button
                onClick={() => setActiveTab('donate')}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === 'donate'
                    ? 'border-red-500 text-red-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                سجل كمتبرع
              </button>
            </nav>
          </div>

          <div className="p-6">
            {/* تبويب البحث عن متبرعين */}
            {activeTab === 'search' && (
              <div className="space-y-6">
                {/* فلاتر البحث */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
                  <div>
                    <Label>فصيلة الدم</Label>
                    <select
                      value={searchFilters.bloodType}
                      onChange={(e) => handleSearchFilterChange('bloodType', e.target.value)}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
                    >
                      <option value="">جميع الفصائل</option>
                      {bloodTypes.map(type => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <Label>المدينة</Label>
                    <select
                      value={searchFilters.city}
                      onChange={(e) => handleSearchFilterChange('city', e.target.value)}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
                    >
                      <option value="">جميع المدن</option>
                      {cities.map(city => (
                        <option key={city} value={city}>{city}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <Label>مستوى الإلحاح</Label>
                    <select
                      value={searchFilters.urgency}
                      onChange={(e) => handleSearchFilterChange('urgency', e.target.value)}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
                    >
                      <option value="">جميع المستويات</option>
                      {urgencyLevels.map(level => (
                        <option key={level} value={level}>{level}</option>
                      ))}
                    </select>
                  </div>
                  <div className="flex items-end">
                    <Button className="w-full bg-red-600 hover:bg-red-700">
                      <Search className="h-4 w-4 ml-2" />
                      بحث
                    </Button>
                  </div>
                </div>

                {/* قائمة المتبرعين */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {donors.map(donor => (
                    <div key={donor.id} className="bg-white p-6 rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center">
                          <div className="bg-red-100 p-2 rounded-full">
                            <User className="h-5 w-5 text-red-600" />
                          </div>
                          <div className="mr-3">
                            <h3 className="font-semibold text-gray-900">{donor.name}</h3>
                            <div className="flex items-center mt-1">
                              <span className={`px-2 py-1 text-xs font-medium rounded-full ${getBloodTypeColor(donor.bloodType)}`}>
                                {donor.bloodType}
                              </span>
                              {donor.verified && (
                                <CheckCircle className="h-4 w-4 text-green-500 mr-1" />
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center">
                          <Star className="h-4 w-4 text-yellow-400 fill-current" />
                          <span className="text-sm text-gray-600 mr-1">{donor.rating}</span>
                        </div>
                      </div>

                      <div className="space-y-2 text-sm text-gray-600 mb-4">
                        <div className="flex items-center">
                          <MapPin className="h-4 w-4 ml-1" />
                          <span>{donor.city}</span>
                        </div>
                        <div className="flex items-center">
                          <Droplets className="h-4 w-4 ml-1" />
                          <span>{donor.totalDonations} تبرع سابق</span>
                        </div>
                        <div className="flex items-center">
                          <Calendar className="h-4 w-4 ml-1" />
                          <span>آخر تبرع: {donor.lastDonation}</span>
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          donor.available ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {donor.available ? 'متاح' : 'غير متاح'}
                        </span>
                        <Button
                          size="sm"
                          onClick={() => handleContactDonor(donor.id)}
                          disabled={!donor.available}
                          className="bg-red-600 hover:bg-red-700"
                        >
                          <Phone className="h-4 w-4 ml-1" />
                          تواصل
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* تبويب طلبات الدم */}
            {activeTab === 'requests' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">طلبات الدم النشطة</h3>
                  <Button className="bg-red-600 hover:bg-red-700">
                    <Plus className="h-4 w-4 ml-2" />
                    إضافة طلب جديد
                  </Button>
                </div>

                <div className="space-y-4">
                  {requests.map(request => (
                    <div key={request.id} className="bg-white p-6 rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center mb-2">
                            <h3 className="text-lg font-semibold text-gray-900 ml-3">
                              {request.patientName}
                            </h3>
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${getBloodTypeColor(request.bloodType)}`}>
                              {request.bloodType}
                            </span>
                            <span className={`px-2 py-1 text-xs font-medium rounded-full mr-2 ${getUrgencyColor(request.urgency)}`}>
                              {request.urgency}
                            </span>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600 mb-4">
                            <div className="space-y-1">
                              <div className="flex items-center">
                                <Droplets className="h-4 w-4 ml-1" />
                                <span>عدد الوحدات: {request.unitsNeeded}</span>
                              </div>
                              <div className="flex items-center">
                                <MapPin className="h-4 w-4 ml-1" />
                                <span>{request.hospital} - {request.city}</span>
                              </div>
                            </div>
                            <div className="space-y-1">
                              <div className="flex items-center">
                                <Phone className="h-4 w-4 ml-1" />
                                <span>{request.contactPhone}</span>
                              </div>
                              <div className="flex items-center">
                                <Calendar className="h-4 w-4 ml-1" />
                                <span>{request.requestDate}</span>
                              </div>
                            </div>
                          </div>

                          <p className="text-gray-700 mb-4">{request.description}</p>
                        </div>

                        <div className="flex flex-col space-y-2">
                          <Button
                            size="sm"
                            onClick={() => handleRequestHelp(request.id)}
                            className="bg-red-600 hover:bg-red-700"
                          >
                            <Heart className="h-4 w-4 ml-1" />
                            ساعد الآن
                          </Button>
                          <Button size="sm" variant="outline">
                            مشاركة
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* تبويب التسجيل كمتبرع */}
            {activeTab === 'donate' && (
              <div className="max-w-2xl mx-auto">
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">
                    سجل كمتبرع بالدم
                  </h3>
                  <p className="text-gray-600">
                    انضم إلى شبكة المتبرعين وساعد في إنقاذ الأرواح
                  </p>
                </div>

                <form onSubmit={handleDonationSubmit} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <Label htmlFor="name">الاسم الكامل *</Label>
                      <Input
                        id="name"
                        type="text"
                        required
                        value={donationForm.name}
                        onChange={(e) => handleDonationFormChange('name', e.target.value)}
                        placeholder="أدخل اسمك الكامل"
                      />
                    </div>
                    <div>
                      <Label htmlFor="phone">رقم الهاتف *</Label>
                      <Input
                        id="phone"
                        type="tel"
                        required
                        value={donationForm.phone}
                        onChange={(e) => handleDonationFormChange('phone', e.target.value)}
                        placeholder="01xxxxxxxxx"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <Label htmlFor="bloodType">فصيلة الدم *</Label>
                      <select
                        id="bloodType"
                        required
                        value={donationForm.bloodType}
                        onChange={(e) => handleDonationFormChange('bloodType', e.target.value)}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
                      >
                        <option value="">اختر فصيلة الدم</option>
                        {bloodTypes.map(type => (
                          <option key={type} value={type}>{type}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <Label htmlFor="city">المدينة *</Label>
                      <select
                        id="city"
                        required
                        value={donationForm.city}
                        onChange={(e) => handleDonationFormChange('city', e.target.value)}
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
                      >
                        <option value="">اختر المدينة</option>
                        {cities.map(city => (
                          <option key={city} value={city}>{city}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="lastDonation">تاريخ آخر تبرع</Label>
                    <Input
                      id="lastDonation"
                      type="date"
                      value={donationForm.lastDonation}
                      onChange={(e) => handleDonationFormChange('lastDonation', e.target.value)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="medicalConditions">الحالات الطبية (اختياري)</Label>
                    <textarea
                      id="medicalConditions"
                      rows={3}
                      value={donationForm.medicalConditions}
                      onChange={(e) => handleDonationFormChange('medicalConditions', e.target.value)}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
                      placeholder="اذكر أي حالات طبية أو أدوية تتناولها"
                    />
                  </div>

                  <div className="flex items-center">
                    <input
                      id="available"
                      type="checkbox"
                      checked={donationForm.available}
                      onChange={(e) => handleDonationFormChange('available', e.target.checked)}
                      className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
                    />
                    <label htmlFor="available" className="mr-2 block text-sm text-gray-700">
                      متاح للتبرع حالياً
                    </label>
                  </div>

                  <Alert className="border-blue-200 bg-blue-50">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="text-blue-700">
                      سيتم التواصل معك عند وجود حالات تحتاج لفصيلة دمك. يمكنك تحديث حالة التوفر في أي وقت.
                    </AlertDescription>
                  </Alert>

                  <Button
                    type="submit"
                    className="w-full bg-red-600 hover:bg-red-700"
                    disabled={loading}
                  >
                    {loading ? 'جاري التسجيل...' : 'سجل كمتبرع'}
                  </Button>
                </form>
              </div>
            )}
          </div>
        </div>

        {/* معلومات مهمة */}
        <div className="bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-red-800 mb-4">معلومات مهمة عن التبرع بالدم</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-red-700">
            <div>
              <h4 className="font-medium mb-2">شروط التبرع:</h4>
              <ul className="space-y-1">
                <li>• العمر من 18 إلى 65 سنة</li>
                <li>• الوزن أكثر من 50 كيلو</li>
                <li>• عدم التبرع خلال آخر 3 أشهر</li>
                <li>• عدم وجود أمراض معدية</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">فوائد التبرع:</h4>
              <ul className="space-y-1">
                <li>• تجديد خلايا الدم</li>
                <li>• تحسين الدورة الدموية</li>
                <li>• فحص طبي مجاني</li>
                <li>• إنقاذ حياة الآخرين</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

