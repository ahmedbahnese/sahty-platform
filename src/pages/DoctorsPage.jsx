import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  Search, 
  Star, 
  MapPin, 
  Clock, 
  Phone, 
  Calendar,
  Filter,
  Stethoscope,
  Heart,
  Brain,
  Eye,
  Bone,
  Baby
} from 'lucide-react'

export default function DoctorsPage() {
  const [doctors, setDoctors] = useState([])
  const [filteredDoctors, setFilteredDoctors] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedSpecialization, setSelectedSpecialization] = useState('')
  const [selectedCity, setSelectedCity] = useState('')
  const [loading, setLoading] = useState(true)

  // بيانات وهمية للأطباء
  const mockDoctors = [
    {
      id: 1,
      name: 'د. أحمد محمد علي',
      specialization: 'طب القلب',
      rating: 4.8,
      reviews: 156,
      experience: 15,
      city: 'القاهرة',
      district: 'مصر الجديدة',
      consultationFee: 300,
      image: '/api/placeholder/150/150',
      availableToday: true,
      nextAvailable: 'اليوم 2:00 م',
      hospital: 'مستشفى القاهرة الجديدة',
      phone: '01234567890',
      languages: ['العربية', 'الإنجليزية']
    },
    {
      id: 2,
      name: 'د. فاطمة أحمد حسن',
      specialization: 'طب الأطفال',
      rating: 4.9,
      reviews: 203,
      experience: 12,
      city: 'الإسكندرية',
      district: 'سموحة',
      consultationFee: 250,
      image: '/api/placeholder/150/150',
      availableToday: false,
      nextAvailable: 'غداً 10:00 ص',
      hospital: 'مستشفى الإسكندرية الدولي',
      phone: '01234567891',
      languages: ['العربية', 'الفرنسية']
    },
    {
      id: 3,
      name: 'د. محمد حسام الدين',
      specialization: 'طب العظام',
      rating: 4.7,
      reviews: 89,
      experience: 18,
      city: 'الجيزة',
      district: 'المهندسين',
      consultationFee: 350,
      image: '/api/placeholder/150/150',
      availableToday: true,
      nextAvailable: 'اليوم 4:00 م',
      hospital: 'مستشفى الجيزة التخصصي',
      phone: '01234567892',
      languages: ['العربية', 'الإنجليزية', 'الألمانية']
    },
    {
      id: 4,
      name: 'د. سارة محمد إبراهيم',
      specialization: 'طب النساء والتوليد',
      rating: 4.9,
      reviews: 178,
      experience: 14,
      city: 'القاهرة',
      district: 'الزمالك',
      consultationFee: 400,
      image: '/api/placeholder/150/150',
      availableToday: true,
      nextAvailable: 'اليوم 6:00 م',
      hospital: 'مستشفى الزمالك النسائي',
      phone: '01234567893',
      languages: ['العربية', 'الإنجليزية']
    },
    {
      id: 5,
      name: 'د. عمر عبد الرحمن',
      specialization: 'طب العيون',
      rating: 4.6,
      reviews: 134,
      experience: 10,
      city: 'الإسكندرية',
      district: 'العطارين',
      consultationFee: 280,
      image: '/api/placeholder/150/150',
      availableToday: false,
      nextAvailable: 'الأحد 11:00 ص',
      hospital: 'مستشفى العيون التخصصي',
      phone: '01234567894',
      languages: ['العربية', 'الإنجليزية']
    },
    {
      id: 6,
      name: 'د. نورا أحمد سالم',
      specialization: 'طب الأعصاب',
      rating: 4.8,
      reviews: 92,
      experience: 16,
      city: 'القاهرة',
      district: 'مدينة نصر',
      consultationFee: 450,
      image: '/api/placeholder/150/150',
      availableToday: true,
      nextAvailable: 'اليوم 3:30 م',
      hospital: 'مستشفى مدينة نصر للأعصاب',
      phone: '01234567895',
      languages: ['العربية', 'الإنجليزية', 'الفرنسية']
    }
  ]

  const specializations = [
    { name: 'طب القلب', icon: Heart },
    { name: 'طب الأطفال', icon: Baby },
    { name: 'طب العظام', icon: Bone },
    { name: 'طب النساء والتوليد', icon: Stethoscope },
    { name: 'طب العيون', icon: Eye },
    { name: 'طب الأعصاب', icon: Brain },
    { name: 'طب عام', icon: Stethoscope },
    { name: 'طب الأسنان', icon: Stethoscope }
  ]

  const cities = ['القاهرة', 'الإسكندرية', 'الجيزة', 'الشرقية', 'البحيرة', 'المنوفية']

  useEffect(() => {
    setDoctors(mockDoctors)
    setFilteredDoctors(mockDoctors)
    setLoading(false)
  }, [])

  useEffect(() => {
    // تطبيق الفلاتر
    let filtered = doctors

    if (searchTerm) {
      filtered = filtered.filter(doctor => 
        doctor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doctor.specialization.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doctor.hospital.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    if (selectedSpecialization) {
      filtered = filtered.filter(doctor => doctor.specialization === selectedSpecialization)
    }

    if (selectedCity) {
      filtered = filtered.filter(doctor => doctor.city === selectedCity)
    }

    setFilteredDoctors(filtered)
  }, [searchTerm, selectedSpecialization, selectedCity, doctors])

  const handleBookAppointment = (doctorId) => {
    // هنا سيتم التوجيه لصفحة حجز الموعد
    console.log('حجز موعد مع الطبيب:', doctorId)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* الرأس */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            أطباؤنا المعتمدون
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            اختر من بين أفضل الأطباء المعتمدين في مختلف التخصصات واحجز موعدك بسهولة
          </p>
        </div>

        {/* شريط البحث والفلاتر */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* البحث */}
            <div className="relative">
              <Search className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              <Input
                type="text"
                placeholder="ابحث عن طبيب أو تخصص..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* التخصص */}
            <select
              value={selectedSpecialization}
              onChange={(e) => setSelectedSpecialization(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">جميع التخصصات</option>
              {specializations.map((spec, index) => (
                <option key={index} value={spec.name}>{spec.name}</option>
              ))}
            </select>

            {/* المدينة */}
            <select
              value={selectedCity}
              onChange={(e) => setSelectedCity(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">جميع المدن</option>
              {cities.map((city, index) => (
                <option key={index} value={city}>{city}</option>
              ))}
            </select>

            {/* زر الفلترة */}
            <Button variant="outline" className="flex items-center">
              <Filter className="h-4 w-4 ml-2" />
              فلاتر متقدمة
            </Button>
          </div>
        </div>

        {/* التخصصات السريعة */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">التخصصات الشائعة</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
            {specializations.slice(0, 8).map((spec, index) => {
              const IconComponent = spec.icon
              return (
                <button
                  key={index}
                  onClick={() => setSelectedSpecialization(spec.name)}
                  className={`flex flex-col items-center p-4 rounded-lg border transition-colors ${
                    selectedSpecialization === spec.name
                      ? 'border-blue-500 bg-blue-50 text-blue-600'
                      : 'border-gray-200 hover:border-gray-300 text-gray-700'
                  }`}
                >
                  <IconComponent className="h-6 w-6 mb-2" />
                  <span className="text-sm font-medium text-center">{spec.name}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* نتائج البحث */}
        <div className="mb-6">
          <p className="text-gray-600">
            تم العثور على {filteredDoctors.length} طبيب
          </p>
        </div>

        {/* قائمة الأطباء */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredDoctors.map((doctor) => (
            <div key={doctor.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
              <div className="flex items-start space-x-4 rtl:space-x-reverse">
                {/* صورة الطبيب */}
                <div className="flex-shrink-0">
                  <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center">
                    <Stethoscope className="h-10 w-10 text-blue-600" />
                  </div>
                </div>

                {/* معلومات الطبيب */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">
                        {doctor.name}
                      </h3>
                      <p className="text-blue-600 font-medium mb-2">
                        {doctor.specialization}
                      </p>
                      
                      {/* التقييم */}
                      <div className="flex items-center mb-2">
                        <div className="flex items-center">
                          {[...Array(5)].map((_, i) => (
                            <Star
                              key={i}
                              className={`h-4 w-4 ${
                                i < Math.floor(doctor.rating)
                                  ? 'text-yellow-400 fill-current'
                                  : 'text-gray-300'
                              }`}
                            />
                          ))}
                        </div>
                        <span className="text-sm text-gray-600 mr-2">
                          {doctor.rating} ({doctor.reviews} تقييم)
                        </span>
                      </div>

                      {/* المعلومات الإضافية */}
                      <div className="space-y-1 text-sm text-gray-600">
                        <div className="flex items-center">
                          <MapPin className="h-4 w-4 ml-1" />
                          <span>{doctor.city} - {doctor.district}</span>
                        </div>
                        <div className="flex items-center">
                          <Stethoscope className="h-4 w-4 ml-1" />
                          <span>{doctor.hospital}</span>
                        </div>
                        <div className="flex items-center">
                          <Clock className="h-4 w-4 ml-1" />
                          <span>{doctor.experience} سنة خبرة</span>
                        </div>
                      </div>
                    </div>

                    {/* السعر والحالة */}
                    <div className="text-left">
                      <div className="text-lg font-bold text-gray-900 mb-1">
                        {doctor.consultationFee} جنيه
                      </div>
                      <div className={`text-sm font-medium ${
                        doctor.availableToday ? 'text-green-600' : 'text-orange-600'
                      }`}>
                        {doctor.nextAvailable}
                      </div>
                    </div>
                  </div>

                  {/* الأزرار */}
                  <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
                    <div className="flex items-center space-x-2 rtl:space-x-reverse">
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex items-center"
                      >
                        <Phone className="h-4 w-4 ml-1" />
                        اتصال
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                      >
                        عرض الملف
                      </Button>
                    </div>
                    
                    <Button
                      onClick={() => handleBookAppointment(doctor.id)}
                      className="flex items-center"
                    >
                      <Calendar className="h-4 w-4 ml-1" />
                      احجز موعد
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* رسالة عدم وجود نتائج */}
        {filteredDoctors.length === 0 && (
          <div className="text-center py-12">
            <Stethoscope className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              لم يتم العثور على أطباء
            </h3>
            <p className="text-gray-600">
              جرب تغيير معايير البحث أو الفلاتر
            </p>
          </div>
        )}

        {/* دعوة للعمل */}
        <div className="mt-12 bg-blue-600 text-white p-8 rounded-xl text-center">
          <h3 className="text-2xl font-bold mb-4">
            هل أنت طبيب وتريد الانضمام إلينا؟
          </h3>
          <p className="text-blue-100 mb-6">
            انضم إلى شبكة أطبائنا المعتمدين واحصل على المزيد من المرضى
          </p>
          <Button className="bg-white text-blue-600 hover:bg-gray-100">
            سجل كطبيب
          </Button>
        </div>
      </div>
    </div>
  )
}

