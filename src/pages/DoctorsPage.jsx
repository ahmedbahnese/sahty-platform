import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Search, Star, MapPin, Clock, Calendar, Filter,
  Stethoscope, Heart, Brain, Eye, Bone, Baby,
  Sparkles, X, ChevronDown, CheckCircle, Video, Loader2
} from 'lucide-react'

// خريطة الأعراض → التخصصات
const SYMPTOM_MAP = [
  { keywords: ['ألم صدر', 'ضغط', 'قلب', 'نبض', 'ذبحة', 'خفقان', 'ضيق تنفس'], specialty: 'طب القلب' },
  { keywords: ['صداع', 'دوار', 'دوخة', 'صرع', 'تنميل', 'شلل', 'أعصاب', 'رعشة'], specialty: 'طب الأعصاب' },
  { keywords: ['كحة', 'سعال', 'رئة', 'ربو', 'تنفس', 'بلغم', 'التهاب حلق'], specialty: 'طب الصدر والجهاز التنفسي' },
  { keywords: ['بطن', 'معدة', 'إسهال', 'إمساك', 'قولون', 'كبد', 'غثيان', 'قيء', 'حرقة'], specialty: 'طب الجهاز الهضمي' },
  { keywords: ['مفصل', 'عظم', 'كسر', 'ظهر', 'خصر', 'ركبة', 'كتف', 'فقرات', 'روماتيزم'], specialty: 'طب العظام' },
  { keywords: ['عين', 'نظر', 'بصر', 'نظارة', 'التهاب عين', 'إبصار'], specialty: 'طب العيون' },
  { keywords: ['طفل', 'رضيع', 'مولود', 'نمو', 'تطعيم', 'أطفال'], specialty: 'طب الأطفال' },
  { keywords: ['جلد', 'حبوب', 'بشرة', 'طفح', 'أكزيما', 'صدفية', 'شعر'], specialty: 'الأمراض الجلدية' },
  { keywords: ['ولادة', 'حمل', 'دورة', 'رحم', 'مبيض', 'نساء', 'أمومة'], specialty: 'طب النساء والتوليد' },
  { keywords: ['كلى', 'بول', 'مثانة', 'تبول', 'حصوة'], specialty: 'طب المسالك البولية' },
  { keywords: ['سكر', 'سكري', 'غدة', 'هرمون', 'درقية', 'إنسولين', 'وزن'], specialty: 'الغدد الصماء والسكري' },
  { keywords: ['نفس', 'اكتئاب', 'قلق', 'توتر', 'وسواس', 'نفسي'], specialty: 'الطب النفسي' },
  { keywords: ['أسنان', 'ضرس', 'لثة', 'تسوس', 'فم'], specialty: 'طب الأسنان' },
  { keywords: ['أنف', 'أذن', 'حلق', 'سمع', 'صوت', 'لوزتين', 'جيوب أنفية'], specialty: 'أنف وأذن وحنجرة' },
]

function detectSpecialty(text) {
  if (!text.trim()) return null
  const lower = text.toLowerCase()
  const scores = {}
  for (const entry of SYMPTOM_MAP) {
    for (const kw of entry.keywords) {
      if (lower.includes(kw)) scores[entry.specialty] = (scores[entry.specialty] || 0) + 1
    }
  }
  if (!Object.keys(scores).length) return null
  return Object.entries(scores).sort((a, b) => b[1] - a[1])[0][0]
}

const SPECIALIZATIONS = [
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

const CITIES = ['القاهرة', 'الإسكندرية', 'الجيزة', 'الشرقية', 'البحيرة', 'المنوفية']

export default function DoctorsPage() {
  const navigate = useNavigate()
  const [doctors, setDoctors]                 = useState([])
  const [loading, setLoading]                 = useState(true)
  const [total, setTotal]                     = useState(0)
  const [page, setPage]                       = useState(1)
  const [searchTerm, setSearchTerm]           = useState('')
  const [selectedSpec, setSelectedSpec]       = useState('')
  const [selectedCity, setSelectedCity]       = useState('')
  const [telemedicine, setTelemedicine]       = useState(false)
  const [symptoms, setSymptoms]               = useState('')
  const [detectedSpec, setDetectedSpec]       = useState(null)
  const [showSymptomBox, setShowSymptomBox]   = useState(false)
  const [apiError, setApiError]               = useState(false)

  const PER_PAGE = 18

  const fetchDoctors = useCallback(async () => {
    setLoading(true)
    setApiError(false)
    try {
      const params = new URLSearchParams({
        page,
        per_page: PER_PAGE,
        ...(searchTerm   && { search: searchTerm }),
        ...(selectedSpec && { specialization: selectedSpec }),
        ...(selectedCity && { city: selectedCity }),
        ...(telemedicine && { telemedicine: '1' }),
      })
      const res = await fetch(`/api/doctors?${params}`)
      if (!res.ok) throw new Error()
      const data = await res.json()
      setDoctors(data.doctors || [])
      setTotal(data.total || 0)
    } catch {
      setApiError(true)
      setDoctors([])
    } finally {
      setLoading(false)
    }
  }, [page, searchTerm, selectedSpec, selectedCity, telemedicine])

  useEffect(() => { fetchDoctors() }, [fetchDoctors])

  // Reset page on filter change
  useEffect(() => { setPage(1) }, [searchTerm, selectedSpec, selectedCity, telemedicine])

  const handleSymptomAnalyze = () => {
    const result = detectSpecialty(symptoms)
    setDetectedSpec(result)
    if (result) setSelectedSpec(result)
  }

  const clearAll = () => {
    setSearchTerm(''); setSelectedSpec(''); setSelectedCity('')
    setTelemedicine(false); setDetectedSpec(null); setSymptoms('')
  }

  const hasFilters = searchTerm || selectedSpec || selectedCity || telemedicine

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

        {/* Symptom box */}
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
              <div className="flex gap-2">
                <textarea
                  value={symptoms}
                  onChange={e => setSymptoms(e.target.value)}
                  placeholder="مثال: أشعر بألم في الصدر وضيق في التنفس..."
                  rows={2}
                  className="flex-1 border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-blue-400 bg-white resize-none"
                  style={{ direction: 'rtl' }}
                />
                <button onClick={handleSymptomAnalyze} disabled={!symptoms.trim()}
                  className="px-5 py-2 rounded-xl text-white text-sm font-medium disabled:opacity-40"
                  style={{ background: 'linear-gradient(135deg, #0f2444 0%, #2563eb 100%)' }}>
                  تحليل
                </button>
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                {['ألم في الصدر', 'صداع ودوار', 'ألم في المفاصل', 'مشاكل في العيون', 'حمى وكحة', 'آلام بطن'].map(s => (
                  <button key={s}
                    onClick={() => { setSymptoms(s); setTimeout(handleSymptomAnalyze, 0) }}
                    className="text-xs bg-white border border-blue-200 text-blue-700 px-3 py-1.5 rounded-full hover:bg-blue-50 transition-colors">
                    {s}
                  </button>
                ))}
              </div>
              {detectedSpec && (
                <div className="mt-3 flex items-center gap-3 bg-green-50 border border-green-200 rounded-xl px-4 py-3">
                  <span className="w-2 h-2 bg-green-500 rounded-full flex-shrink-0" />
                  <p className="text-sm text-green-800 flex-1">
                    يُنصح بمراجعة: <strong>{detectedSpec}</strong>
                  </p>
                  <button onClick={() => { setDetectedSpec(null); setSymptoms('') }}
                    className="text-gray-400 hover:text-gray-600"><X className="h-4 w-4" /></button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Filters */}
        <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="h-4 w-4 text-gray-400 absolute right-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="ابحث عن طبيب أو تخصص..."
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
                className="w-full border border-gray-200 rounded-xl px-4 py-2.5 pr-10 text-sm focus:outline-none focus:border-blue-400"
                style={{ direction: 'rtl' }}
              />
            </div>
            <select value={selectedSpec}
              onChange={e => { setSelectedSpec(e.target.value); setDetectedSpec(null) }}
              className="border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-blue-400 bg-white"
              style={{ direction: 'rtl' }}>
              <option value="">جميع التخصصات</option>
              {SPECIALIZATIONS.map((s, i) => <option key={i} value={s.name}>{s.name}</option>)}
            </select>
            <select value={selectedCity} onChange={e => setSelectedCity(e.target.value)}
              className="border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-blue-400 bg-white"
              style={{ direction: 'rtl' }}>
              <option value="">جميع المدن</option>
              {CITIES.map((c, i) => <option key={i} value={c}>{c}</option>)}
            </select>
            <button
              onClick={() => setTelemedicine(t => !t)}
              className={`flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl border text-sm font-medium transition-all ${
                telemedicine
                  ? 'text-white border-blue-600'
                  : 'text-gray-600 border-gray-200 hover:border-blue-300 hover:bg-blue-50/50'
              }`}
              style={telemedicine ? { background: 'linear-gradient(135deg, #0f2444 0%, #2563eb 100%)' } : {}}>
              <Video className="h-4 w-4" />
              عيادة افتراضية
            </button>
          </div>
          {hasFilters && (
            <div className="mt-3 flex items-center gap-2 flex-wrap">
              <span className="text-xs text-gray-500">الفلاتر:</span>
              {selectedSpec && (
                <span className="inline-flex items-center gap-1 text-xs bg-blue-50 text-blue-700 border border-blue-200 px-3 py-1 rounded-full">
                  {selectedSpec}<button onClick={() => { setSelectedSpec(''); setDetectedSpec(null) }}><X className="h-3 w-3" /></button>
                </span>
              )}
              {selectedCity && (
                <span className="inline-flex items-center gap-1 text-xs bg-blue-50 text-blue-700 border border-blue-200 px-3 py-1 rounded-full">
                  {selectedCity}<button onClick={() => setSelectedCity('')}><X className="h-3 w-3" /></button>
                </span>
              )}
              {searchTerm && (
                <span className="inline-flex items-center gap-1 text-xs bg-blue-50 text-blue-700 border border-blue-200 px-3 py-1 rounded-full">
                  "{searchTerm}"<button onClick={() => setSearchTerm('')}><X className="h-3 w-3" /></button>
                </span>
              )}
              <button onClick={clearAll} className="text-xs text-gray-400 hover:text-red-500 transition-colors">مسح الكل</button>
            </div>
          )}
        </div>

        {/* Specialization chips */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">التخصصات الشائعة</h3>
          <div className="grid grid-cols-4 md:grid-cols-8 gap-2">
            {SPECIALIZATIONS.map((spec, i) => {
              const Icon = spec.icon
              return (
                <button key={i}
                  onClick={() => { setSelectedSpec(selectedSpec === spec.name ? '' : spec.name); setDetectedSpec(null) }}
                  className={`flex flex-col items-center p-3 rounded-xl border transition-all text-center ${
                    selectedSpec === spec.name
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-200 bg-white hover:border-blue-200 hover:bg-blue-50/50 text-gray-600'
                  }`}>
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
            {loading ? 'جارٍ البحث...' : apiError ? '' : `${total} طبيب متاح`}
          </p>
          {total > PER_PAGE && !loading && (
            <div className="flex items-center gap-2 text-sm">
              <button disabled={page === 1}
                onClick={() => setPage(p => p - 1)}
                className="px-3 py-1 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50">
                السابق
              </button>
              <span className="text-gray-500">{page} / {Math.ceil(total / PER_PAGE)}</span>
              <button disabled={page >= Math.ceil(total / PER_PAGE)}
                onClick={() => setPage(p => p + 1)}
                className="px-3 py-1 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50">
                التالي
              </button>
            </div>
          )}
        </div>

        {/* Doctors Grid */}
        {loading ? (
          <div className="flex justify-center py-20">
            <Loader2 className="h-10 w-10 animate-spin text-blue-400" />
          </div>
        ) : apiError ? (
          <div className="text-center py-20 bg-white rounded-2xl border border-gray-100">
            <Stethoscope className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 font-medium">لا يوجد أطباء مسجلون بعد</p>
            <p className="text-gray-400 text-sm mt-1">سيظهر الأطباء هنا بعد تسجيلهم وتوثيقهم</p>
          </div>
        ) : doctors.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-2xl border border-gray-100">
            <Stethoscope className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 font-medium">لا توجد أطباء بهذه المعايير</p>
            <button onClick={clearAll} className="mt-4 text-sm text-blue-600 hover:underline">
              عرض جميع الأطباء
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
            {doctors.map(doctor => (
              <DoctorCard key={doctor.id} doctor={doctor}
                onClick={() => navigate(`/doctors/${doctor.id}`)} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function DoctorCard({ doctor, onClick }) {
  const stars = Array.from({ length: 5 }, (_, i) => i < Math.round(doctor.rating || 0))
  return (
    <div className="bg-white rounded-2xl border border-gray-100 hover:border-blue-200 hover:shadow-lg transition-all duration-300 overflow-hidden cursor-pointer"
      onClick={onClick}>
      <div className="p-5">
        <div className="flex items-start gap-4 mb-4">
          <div className="w-14 h-14 rounded-2xl flex items-center justify-center text-white text-xl font-bold flex-shrink-0"
            style={{ background: 'linear-gradient(135deg, #0f2444 0%, #2563eb 100%)' }}>
            {doctor.first_name?.charAt(0) || 'د'}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-1.5 flex-wrap">
              <h3 className="font-bold text-gray-900 text-base truncate">
                د. {doctor.first_name} {doctor.last_name}
              </h3>
              {doctor.is_verified && (
                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
              )}
            </div>
            <p className="text-blue-600 text-sm font-medium">{doctor.specialization}</p>
            <div className="flex items-center gap-1 mt-1">
              <div className="flex gap-0.5">
                {stars.map((filled, i) => (
                  <Star key={i} className={`h-3.5 w-3.5 ${filled ? 'fill-yellow-400 text-yellow-400' : 'text-gray-200'}`} />
                ))}
              </div>
              <span className="text-sm font-semibold text-gray-700">{(doctor.rating || 0).toFixed(1)}</span>
              <span className="text-xs text-gray-400">({doctor.total_reviews || 0})</span>
            </div>
          </div>
        </div>

        <div className="space-y-2 mb-4">
          {doctor.years_of_experience && (
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <Clock className="h-3.5 w-3.5 text-gray-400" />
              <span>خبرة {doctor.years_of_experience} سنة</span>
            </div>
          )}
          {(doctor.clinic_name || doctor.clinic_address) && (
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <MapPin className="h-3.5 w-3.5 text-gray-400" />
              <span className="truncate">{doctor.clinic_name || doctor.clinic_address}</span>
            </div>
          )}
          {doctor.availability_days?.length > 0 && (
            <div className="flex items-center gap-2 text-xs text-green-600">
              <Calendar className="h-3.5 w-3.5" />
              <span>{doctor.availability_days.map(d => d.day).slice(0, 3).join('، ')}</span>
            </div>
          )}
          {doctor.available_for_telemedicine && (
            <div className="flex items-center gap-1.5 text-xs text-blue-600">
              <Video className="h-3.5 w-3.5" />
              <span>عيادة افتراضية متاحة</span>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between pt-3 border-t border-gray-100">
          <div>
            {doctor.consultation_fee ? (
              <>
                <span className="text-lg font-bold text-gray-900">{doctor.consultation_fee}</span>
                <span className="text-xs text-gray-400 mr-1">ج.م</span>
              </>
            ) : (
              <span className="text-sm text-gray-400">السعر عند الحجز</span>
            )}
          </div>
          <button
            className="px-4 py-2 text-sm font-semibold text-white rounded-xl transition-all hover:opacity-90"
            style={{ background: 'linear-gradient(135deg, #0f2444 0%, #2563eb 100%)' }}
            onClick={e => { e.stopPropagation(); onClick() }}>
            <Calendar className="h-4 w-4 inline ml-1.5" />
            احجز موعداً
          </button>
        </div>
      </div>
    </div>
  )
}
