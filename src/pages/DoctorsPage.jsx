import { useState, useEffect } from 'react'
import { Input } from '@/components/ui/input'
import {
  Search,
  Star,
  MapPin,
  Clock,
  Calendar,
  Filter,
  Stethoscope,
  Heart,
  Brain,
  Eye,
  Bone,
  Baby,
  Sparkles,
  X,
  ChevronDown
} from 'lucide-react'

// خريطة الأعراض → التخصصات
const SYMPTOM_MAP = [
  { keywords: ['ألم صدر', 'ضغط', 'قلب', 'نبض', 'ذبحة', 'خفقان', 'ضيق تنفس', 'انتظام'], specialty: 'طب القلب' },
  { keywords: ['صداع', 'دوار', 'دوخة', 'صرع', 'تنميل', 'شلل', 'تذكر', 'أعصاب', 'توتر', 'رعشة', 'رهاب'], specialty: 'طب الأعصاب' },
  { keywords: ['كحة', 'سعال', 'رئة', 'ربو', 'تنفس', 'بلغم', 'التهاب حلق', 'حلق', 'أنف', 'زكام', 'برد'], specialty: 'طب الصدر والجهاز التنفسي' },
  { keywords: ['بطن', 'معدة', 'إسهال', 'إمساك', 'قولون', 'كبد', 'غثيان', 'قيء', 'حرقة', 'هضم', 'كرش'], specialty: 'طب الجهاز الهضمي' },
  { keywords: ['مفصل', 'عظم', 'كسر', 'ظهر', 'خصر', 'ركبة', 'كتف', 'فقرات', 'روماتيزم'], specialty: 'طب العظام' },
  { keywords: ['عين', 'نظر', 'بصر', 'نظارة', 'التهاب عين', 'إبصار'], specialty: 'طب العيون' },
  { keywords: ['طفل', 'رضيع', 'مولود', 'نمو', 'تطعيم', 'تطوير', 'أطفال'], specialty: 'طب الأطفال' },
  { keywords: ['جلد', 'حبوب', 'بشرة', 'طفح', 'أكزيما', 'صدفية', 'شعر', 'أظافر'], specialty: 'الأمراض الجلدية' },
  { keywords: ['ولادة', 'حمل', 'دورة', 'رحم', 'مبيض', 'نساء', 'أمومة'], specialty: 'طب النساء والتوليد' },
  { keywords: ['كلى', 'بول', 'مثانة', 'تبول', 'حصوة'], specialty: 'طب المسالك البولية' },
  { keywords: ['سكر', 'سكري', 'غدة', 'هرمون', 'درقية', 'إنسولين', 'وزن'], specialty: 'الغدد الصماء والسكري' },
  { keywords: ['نفس', 'اكتئاب', 'قلق', 'توتر نفسي', 'نوم', 'وسواس', 'نفسي'], specialty: 'الطب النفسي' },
  { keywords: ['أسنان', 'ضرس', 'لثة', 'تسوس', 'فم'], specialty: 'طب الأسنان' },
  { keywords: ['أنف', 'أذن', 'حلق', 'سمع', 'صوت', 'لوزتين', 'جيوب أنفية'], specialty: 'أنف وأذن وحنجرة' },
]

function detectSpecialty(symptoms) {
  if (!symptoms.trim()) return null
  const lower = symptoms.toLowerCase()
  const scores = {}
  for (const entry of SYMPTOM_MAP) {
    for (const kw of entry.keywords) {
      if (lower.includes(kw)) {
        scores[entry.specialty] = (scores[entry.specialty] || 0) + 1
      }
    }
  }
  if (Object.keys(scores).length === 0) return null
  return Object.entries(scores).sort((a, b) => b[1] - a[1])[0][0]
}

export default function DoctorsPage() {
  const [doctors, setDoctors] = useState([])
  const [filteredDoctors, setFilteredDoctors] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedSpecialization, setSelectedSpecialization] = useState('')
  const [selectedCity, setSelectedCity] = useState('')
  const [loading, setLoading] = useState(true)
  const [symptoms, setSymptoms] = useState('')
  const [detectedSpecialty, setDetectedSpecialty] = useState(null)
  const [showSymptomBox, setShowSymptomBox] = useState(false)

  const mockDoctors = [
    { id: 1, name: 'د. أحمد محمد علي', specialization: 'طب القلب', rating: 4.8, reviews: 156, experience: 15, city: 'القاهرة', district: 'مصر الجديدة', consultationFee: 300, availableToday: true, nextAvailable: 'اليوم 2:00 م', hospital: 'مستشفى القاهرة الجديدة', languages: ['العربية', 'الإنجليزية'] },
    { id: 2, name: 'د. فاطمة أحمد حسن', specialization: 'طب الأطفال', rating: 4.9, reviews: 203, experience: 12, city: 'الإسكندرية', district: 'سموحة', consultationFee: 250, availableToday: false, nextAvailable: 'غداً 10:00 ص', hospital: 'مستشفى الإسكندرية الدولي', languages: ['العربية', 'الفرنسية'] },
    { id: 3, name: 'د. محمد حسام الدين', specialization: 'طب العظام', rating: 4.7, reviews: 89, experience: 18, city: 'الجيزة', district: 'المهندسين', consultationFee: 350, availableToday: true, nextAvailable: 'اليوم 4:00 م', hospital: 'مستشفى الجيزة التخصصي', languages: ['العربية', 'الإنجليزية', 'الألمانية'] },
    { id: 4, name: 'د. سارة محمد إبراهيم', specialization: 'طب النساء والتوليد', rating: 4.9, reviews: 178, experience: 14, city: 'القاهرة', district: 'الزمالك', consultationFee: 400, availableToday: true, nextAvailable: 'اليوم 6:00 م', hospital: 'مستشفى الزمالك النسائي', languages: ['العربية', 'الإنجليزية'] },
    { id: 5, name: 'د. عمر عبد الرحمن', specialization: 'طب العيون', rating: 4.6, reviews: 134, experience: 10, city: 'الإسكندرية', district: 'العطارين', consultationFee: 280, availableToday: false, nextAvailable: 'الأحد 11:00 ص', hospital: 'مستشفى العيون التخصصي', languages: ['العربية', 'الإنجليزية'] },
    { id: 6, name: 'د. نورا أحمد سالم', specialization: 'طب الأعصاب', rating: 4.8, reviews: 92, experience: 16, city: 'القاهرة', district: 'مدينة نصر', consultationFee: 450, availableToday: true, nextAvailable: 'اليوم 3:30 م', hospital: 'مستشفى مدينة نصر للأعصاب', languages: ['العربية', 'الإنجليزية', 'الفرنسية'] },
  ]

  const specializations = [
    { name: 'طب القلب', icon: Heart },
    { name: 'طب الأطفال', icon: Baby },
    { name: 'طب العظام', icon: Bone },
    { name: 'طب النساء والتوليد', icon: Stethoscope },
    { name: 'طب العيون', icon: Eye },
    { name: 'طب الأعصاب', icon: Brain },
    { name: 'طب الصدر والجهاز التنفسي', icon: Stethoscope },
    { name: 'طب الجهاز الهضمي', icon: Stethoscope },
    { name: 'الأمراض الجلدية', icon: Stethoscope },
    { name: 'طب المسالك البولية', icon: Stethoscope },
    { name: 'الغدد الصماء والسكري', icon: Stethoscope },
    { name: 'الطب النفسي', icon: Brain },
    { name: 'طب الأسنان', icon: Stethoscope },
    { name: 'أنف وأذن وحنجرة', icon: Stethoscope },
    { name: 'طب عام', icon: Stethoscope },
  ]

  const cities = ['القاهرة', 'الإسكندرية', 'الجيزة', 'الشرقية', 'البحيرة', 'المنوفية']

  useEffect(() => {
    setDoctors(mockDoctors)
    setFilteredDoctors(mockDoctors)
    setLoading(false)
  }, [])

  useEffect(() => {
    let filtered = doctors
    if (searchTerm) {
      filtered = filtered.filter(d =>
        d.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        d.specialization.toLowerCase().includes(searchTerm.toLowerCase()) ||
        d.hospital.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }
    if (selectedSpecialization) {
      filtered = filtered.filter(d => d.specialization === selectedSpecialization)
    }
    if (selectedCity) {
      filtered = filtered.filter(d => d.city === selectedCity)
    }
    setFilteredDoctors(filtered)
  }, [searchTerm, selectedSpecialization, selectedCity, doctors])

  const handleSymptomAnalyze = () => {
    const result = detectSpecialty(symptoms)
    setDetectedSpecialty(result)
    if (result) setSelectedSpecialization(result)
  }

  const clearSymptoms = () => {
    setSymptoms('')
    setDetectedSpecialty(null)
    setShowSymptomBox(false)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-10" dir="rtl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">أطباؤنا المعتمدون</h1>
          <p className="text-lg text-gray-500 max-w-2xl mx-auto">
            اختر من بين أفضل الأطباء المعتمدين في مختلف التخصصات
          </p>
        </div>

        {/* Symptom / Specialty Search Box */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm mb-6 overflow-hidden">
          <div className="flex items-center gap-4 p-4 cursor-pointer select-none"
            onClick={() => setShowSymptomBox(!showSymptomBox)}>
            <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
              style={{ background: 'linear-gradient(135deg, #0f2444 0%, #2563eb 100%)' }}>
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-gray-900 text-sm">لا تعرف التخصص المطلوب؟</p>
              <p className="text-xs text-gray-500">اكتب أعراضك وسأساعدك في تحديد التخصص المناسب</p>
            </div>
            <ChevronDown className={`h-5 w-5 text-gray-400 transition-transform ${showSymptomBox ? 'rotate-180' : ''}`} />
          </div>

          {showSymptomBox && (
            <div className="border-t border-gray-100 p-4 bg-blue-50/50">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                صف أعراضك أو تشخيصك الطبي
              </label>
              <div className="flex gap-2">
                <textarea
                  value={symptoms}
                  onChange={(e) => setSymptoms(e.target.value)}
                  placeholder="مثال: أشعر بألم في الصدر وضيق في التنفس... أو: عندي كحة وحمى منذ 3 أيام..."
                  rows={2}
                  className="flex-1 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-200 bg-white resize-none"
                  style={{ direction: 'rtl' }}
                />
                <button
                  onClick={handleSymptomAnalyze}
                  disabled={!symptoms.trim()}
                  className="px-5 py-2 rounded-xl text-white text-sm font-medium disabled:opacity-40 flex-shrink-0"
                  style={{ background: 'linear-gradient(135deg, #0f2444 0%, #2563eb 100%)' }}
                >
                  تحليل
                </button>
              </div>

              {/* Quick symptom chips */}
              <div className="mt-3 flex flex-wrap gap-2">
                {['ألم في الصدر', 'صداع ودوار', 'ألم في المفاصل', 'مشاكل في العيون', 'حمى وكحة', 'آلام بطن', 'أعراض جلدية', 'مشاكل الأطفال'].map(s => (
                  <button
                    key={s}
                    onClick={() => { setSymptoms(s); setTimeout(handleSymptomAnalyze, 0) }}
                    className="text-xs bg-white border border-blue-200 text-blue-700 px-3 py-1.5 rounded-full hover:bg-blue-50 transition-colors"
                  >
                    {s}
                  </button>
                ))}
              </div>

              {detectedSpecialty && (
                <div className="mt-3 flex items-center gap-3 bg-green-50 border border-green-200 rounded-xl px-4 py-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full flex-shrink-0"></div>
                  <p className="text-sm text-green-800 flex-1">
                    بناءً على أعراضك، يُنصح بمراجعة: <span className="font-bold">{detectedSpecialty}</span>
                  </p>
                  <button onClick={clearSymptoms} className="text-gray-400 hover:text-gray-600">
                    <X className="h-4 w-4" />
                  </button>
                </div>
              )}
              {symptoms.trim() && !detectedSpecialty && (
                <p className="mt-2 text-xs text-gray-500">
                  لم أتمكن من تحديد التخصص — يمكنك اختياره يدوياً أدناه أو الاستشارة مع طبيب عام.
                </p>
              )}
            </div>
          )}
        </div>

        {/* Filters */}
        <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="relative">
              <Search className="h-4 w-4 text-gray-400 absolute right-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="ابحث عن طبيب أو تخصص..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full border border-gray-200 rounded-xl px-4 py-2.5 pr-10 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-200"
                style={{ direction: 'rtl' }}
              />
            </div>
            <select
              value={selectedSpecialization}
              onChange={(e) => { setSelectedSpecialization(e.target.value); setDetectedSpecialty(null) }}
              className="border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-blue-400 bg-white"
              style={{ direction: 'rtl' }}
            >
              <option value="">جميع التخصصات</option>
              {specializations.map((s, i) => <option key={i} value={s.name}>{s.name}</option>)}
            </select>
            <select
              value={selectedCity}
              onChange={(e) => setSelectedCity(e.target.value)}
              className="border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-blue-400 bg-white"
              style={{ direction: 'rtl' }}
            >
              <option value="">جميع المدن</option>
              {cities.map((c, i) => <option key={i} value={c}>{c}</option>)}
            </select>
          </div>
          {(selectedSpecialization || selectedCity || searchTerm) && (
            <div className="mt-3 flex items-center gap-2 flex-wrap">
              <span className="text-xs text-gray-500">الفلاتر:</span>
              {selectedSpecialization && (
                <span className="inline-flex items-center gap-1 text-xs bg-blue-50 text-blue-700 border border-blue-200 px-3 py-1 rounded-full">
                  {selectedSpecialization}
                  <button onClick={() => { setSelectedSpecialization(''); setDetectedSpecialty(null) }}><X className="h-3 w-3" /></button>
                </span>
              )}
              {selectedCity && (
                <span className="inline-flex items-center gap-1 text-xs bg-blue-50 text-blue-700 border border-blue-200 px-3 py-1 rounded-full">
                  {selectedCity}
                  <button onClick={() => setSelectedCity('')}><X className="h-3 w-3" /></button>
                </span>
              )}
              {searchTerm && (
                <span className="inline-flex items-center gap-1 text-xs bg-blue-50 text-blue-700 border border-blue-200 px-3 py-1 rounded-full">
                  "{searchTerm}"
                  <button onClick={() => setSearchTerm('')}><X className="h-3 w-3" /></button>
                </span>
              )}
              <button onClick={() => { setSearchTerm(''); setSelectedSpecialization(''); setSelectedCity(''); setDetectedSpecialty(null) }}
                className="text-xs text-gray-400 hover:text-red-500 transition-colors">
                مسح الكل
              </button>
            </div>
          )}
        </div>

        {/* Quick Specialties */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">التخصصات الشائعة</h3>
          <div className="grid grid-cols-4 md:grid-cols-8 gap-2">
            {specializations.map((spec, i) => {
              const Icon = spec.icon
              return (
                <button key={i}
                  onClick={() => { setSelectedSpecialization(selectedSpecialization === spec.name ? '' : spec.name); setDetectedSpecialty(null) }}
                  className={`flex flex-col items-center p-3 rounded-xl border transition-all text-center ${
                    selectedSpecialization === spec.name
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-200 bg-white hover:border-blue-200 hover:bg-blue-50/50 text-gray-600'
                  }`}
                >
                  <Icon className="h-5 w-5 mb-1.5" />
                  <span className="text-xs font-medium leading-tight">{spec.name}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Results count */}
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm text-gray-500">
            {filteredDoctors.length > 0
              ? `${filteredDoctors.length} طبيب متاح`
              : 'لا توجد نتائج'}
          </p>
        </div>

        {/* Doctors Grid */}
        {filteredDoctors.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-2xl border border-gray-100">
            <Stethoscope className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 font-medium">لا توجد أطباء بهذه المعايير</p>
            <p className="text-gray-400 text-sm mt-1">جرّب تغيير الفلاتر أو البحث</p>
            <button
              onClick={() => { setSearchTerm(''); setSelectedSpecialization(''); setSelectedCity('') }}
              className="mt-4 text-sm text-blue-600 hover:underline"
            >
              عرض جميع الأطباء
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
            {filteredDoctors.map((doctor) => (
              <div key={doctor.id}
                className="bg-white rounded-2xl border border-gray-100 hover:border-blue-200 hover:shadow-lg transition-all duration-300 overflow-hidden">
                <div className="p-5">
                  <div className="flex items-start gap-4 mb-4">
                    <div className="w-14 h-14 rounded-2xl flex items-center justify-center text-white text-xl font-bold flex-shrink-0"
                      style={{ background: 'linear-gradient(135deg, #0f2444 0%, #2563eb 100%)' }}>
                      {doctor.name.split(' ')[1]?.charAt(0) || 'د'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-bold text-gray-900 text-base truncate">{doctor.name}</h3>
                      <p className="text-blue-600 text-sm font-medium">{doctor.specialization}</p>
                      <div className="flex items-center gap-1 mt-1">
                        <Star className="h-3.5 w-3.5 fill-yellow-400 text-yellow-400" />
                        <span className="text-sm font-semibold text-gray-700">{doctor.rating}</span>
                        <span className="text-xs text-gray-400">({doctor.reviews} تقييم)</span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <MapPin className="h-3.5 w-3.5 flex-shrink-0 text-gray-400" />
                      <span className="truncate">{doctor.hospital} — {doctor.district}، {doctor.city}</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <Clock className="h-3.5 w-3.5 flex-shrink-0 text-gray-400" />
                      <span>خبرة {doctor.experience} سنة</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                      <Calendar className="h-3.5 w-3.5 flex-shrink-0 text-gray-400" />
                      <span className={doctor.availableToday ? 'text-green-600 font-medium' : 'text-gray-500'}>
                        {doctor.nextAvailable}
                      </span>
                      {doctor.availableToday && (
                        <span className="bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded-full font-medium">متاح اليوم</span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                    <div>
                      <span className="text-lg font-bold text-gray-900">{doctor.consultationFee}</span>
                      <span className="text-xs text-gray-400 mr-1">جنيه</span>
                    </div>
                    <button
                      className="px-4 py-2 text-sm font-semibold text-white rounded-xl transition-all hover:opacity-90"
                      style={{ background: 'linear-gradient(135deg, #0f2444 0%, #2563eb 100%)' }}
                      onClick={() => alert('سيتم تفعيل الحجز قريباً')}
                    >
                      <Calendar className="h-4 w-4 inline ml-1.5" />
                      احجز موعداً
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
