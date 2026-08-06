import { useState, useEffect } from 'react'
import { Building2, MapPin, Phone, Navigation, Star, Heart, Stethoscope, X, AlertCircle, Loader2 } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'

const SPECIALTIES = ['عام','قلب','أورام','أطفال','عيون','صدر وجهاز تنفسي','عظام','نساء وتوليد','أمراض جلدية','مخ وأعصاب']
const GOVERNORATES = ['القاهرة','الجيزة','الإسكندرية','الدقهلية','الشرقية','الغربية','المنوفية','البحيرة','أسيوط','سوهاج','الأقصر','أسوان']

function haversine(lat1, lng1, lat2, lng2) {
  const R = 6371
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const a = Math.sin(dLat/2)**2 + Math.cos(lat1*Math.PI/180)*Math.cos(lat2*Math.PI/180)*Math.sin(dLng/2)**2
  return +(R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))).toFixed(1)
}

function Stars({ n }) {
  return (
    <div className="flex items-center gap-0.5">
      {[1,2,3,4,5].map(i => (
        <Star key={i} className={`h-3 w-3 ${i <= Math.round(n) ? 'fill-amber-400 text-amber-400' : 'text-gray-300'}`} />
      ))}
      <span className="text-xs text-gray-500 mr-1">{n}</span>
    </div>
  )
}

export default function HospitalsPage() {
  const [hospitals, setHospitals]   = useState([])
  const [loading, setLoading]       = useState(true)
  const [error, setError]           = useState('')
  const [userCoords, setUserCoords] = useState(null)
  const [locStatus, setLocStatus]   = useState('')
  const [filterGov, setFilterGov]   = useState('')
  const [filterType, setFilterType] = useState('')
  const [filterEmergency, setFilterEmergency] = useState(false)
  const [selected, setSelected]     = useState(null)
  const [search, setSearch]         = useState('')
  const [page, setPage]             = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  const fetchHospitals = () => {
    setLoading(true)
    setError('')
    const params = new URLSearchParams({ page, per_page: 20 })
    if (search.trim())   params.append('search', search.trim())
    if (filterGov)       params.append('city', filterGov)
    if (filterType)      params.append('type', filterType)
    if (filterEmergency) params.append('emergency', '1')

    fetch(`/api/hospitals?${params}`)
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(d => {
        setHospitals(d.hospitals || [])
        setTotalPages(d.pages || 1)
      })
      .catch(() => setError('تعذّر تحميل بيانات المستشفيات'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchHospitals() }, [search, filterGov, filterType, filterEmergency, page])

  const getLocation = () => {
    if (!navigator.geolocation) { setLocStatus('المتصفح لا يدعم تحديد الموقع'); return }
    setLocStatus('جاري تحديد موقعك...')
    navigator.geolocation.getCurrentPosition(
      ({ coords: c }) => { setUserCoords({ lat: c.latitude, lng: c.longitude }); setLocStatus('') },
      () => setLocStatus('تعذّر تحديد الموقع')
    )
  }

  const displayedHospitals = hospitals
    .map(h => ({
      ...h,
      distance: userCoords && h.latitude ? haversine(userCoords.lat, userCoords.lng, h.latitude, h.longitude) : null
    }))
    .sort((a, b) => (a.distance ?? 9999) - (b.distance ?? 9999))

  const clearFilters = () => { setFilterGov(''); setFilterType(''); setFilterEmergency(false); setSearch(''); setPage(1) }
  const hasFilters = filterGov || filterType || filterEmergency || search.trim()

  return (
    <div className="min-h-screen bg-gray-50 py-8" dir="rtl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* Header */}
        <div className="text-center mb-10">
          <div className="flex justify-center mb-4">
            <div className="bg-blue-100 p-4 rounded-full"><Building2 className="h-12 w-12 text-blue-600" /></div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-3">دليل المستشفيات</h1>
          <p className="text-lg text-gray-600">ابحث عن المستشفيات بالتخصص والموقع وخدمات الطوارئ</p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 mb-6">
          <div className="flex flex-col md:flex-row gap-3 items-start md:items-center">
            <input
              value={search}
              onChange={e => { setSearch(e.target.value); setPage(1) }}
              placeholder="ابحث بالاسم..."
              className="flex-1 px-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
            />
            <select value={filterGov} onChange={e => { setFilterGov(e.target.value); setPage(1) }}
              className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-300">
              <option value="">كل المحافظات</option>
              {GOVERNORATES.map(g => <option key={g} value={g}>{g}</option>)}
            </select>
            <select value={filterType} onChange={e => { setFilterType(e.target.value); setPage(1) }}
              className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-300">
              <option value="">كل الأنواع</option>
              <option value="public">حكومي</option>
              <option value="private">خاص</option>
              <option value="specialized">متخصص</option>
            </select>
            <label className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer whitespace-nowrap">
              <input type="checkbox" checked={filterEmergency} onChange={e => { setFilterEmergency(e.target.checked); setPage(1) }}
                className="h-4 w-4 text-blue-600 rounded border-gray-300" />
              طوارئ 24 ساعة
            </label>
            <button onClick={getLocation} className="text-sm text-blue-600 hover:underline flex items-center gap-1 whitespace-nowrap">
              <Navigation className="h-4 w-4" /> {userCoords ? 'تحديث موقعي' : 'ترتيب بالقرب'}
            </button>
            {hasFilters && (
              <button onClick={clearFilters} className="text-sm text-gray-400 hover:text-gray-600 flex items-center gap-1">
                <X className="h-4 w-4" /> مسح
              </button>
            )}
          </div>
          {locStatus && <p className="text-xs text-blue-600 mt-2">{locStatus}</p>}
        </div>

        {/* States */}
        {loading && (
          <div className="flex justify-center py-20">
            <Loader2 className="h-10 w-10 animate-spin text-blue-500" />
          </div>
        )}

        {!loading && error && (
          <Alert className="border-red-200 bg-red-50 mb-4">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-700">{error} <button onClick={fetchHospitals} className="underline mr-2">إعادة المحاولة</button></AlertDescription>
          </Alert>
        )}

        {!loading && !error && hospitals.length === 0 && (
          <div className="text-center py-20 text-gray-500">
            <Building2 className="h-16 w-16 mx-auto mb-4 text-gray-300" />
            <p className="text-lg">لا توجد مستشفيات مسجلة حالياً</p>
            <p className="text-sm mt-2">يمكن للمدير إضافة المستشفيات من لوحة التحكم</p>
          </div>
        )}

        {/* Hospital Grid */}
        {!loading && !error && displayedHospitals.length > 0 && (
          <>
            <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
              {displayedHospitals.map(h => (
                <div key={h.id}
                  className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => setSelected(h)}>
                  <div className="flex items-start gap-3 mb-3">
                    <div className={`p-2 rounded-lg shrink-0 ${h.has_emergency ? 'bg-red-100' : 'bg-blue-100'}`}>
                      <Building2 className={`h-5 w-5 ${h.has_emergency ? 'text-red-600' : 'text-blue-600'}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-gray-900 truncate">{h.name}</h3>
                      <p className="text-xs text-gray-500 flex items-center gap-1 mt-0.5">
                        <MapPin className="h-3 w-3" />{h.city} {h.district && `· ${h.district}`}
                      </p>
                    </div>
                    <div className="flex flex-col items-end gap-1 shrink-0">
                      {h.rating > 0 && <Stars n={h.rating} />}
                      {h.distance !== null && (
                        <span className="text-xs text-blue-600 font-medium">{h.distance} كم</span>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-1.5 mb-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${h.type === 'private' ? 'bg-purple-100 text-purple-700' : 'bg-green-100 text-green-700'}`}>
                      {h.type === 'public' ? 'حكومي' : h.type === 'private' ? 'خاص' : 'متخصص'}
                    </span>
                    {h.has_emergency && <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700 font-medium">طوارئ 24س</span>}
                    {h.is_24_hours && !h.has_emergency && <span className="text-xs px-2 py-0.5 rounded-full bg-orange-100 text-orange-700 font-medium">24 ساعة</span>}
                    {h.is_verified && <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 font-medium">✓ موثق</span>}
                  </div>

                  {h.available_beds != null && (
                    <p className="text-xs text-gray-500 mb-3">
                      أسرة متاحة: <span className="font-medium text-gray-700">{h.available_beds}</span>
                      {h.total_beds ? ` من ${h.total_beds}` : ''}
                    </p>
                  )}

                  <div className="flex gap-2 mt-auto">
                    <a href={`tel:${h.phone}`} onClick={e => e.stopPropagation()} className="flex-1">
                      <button className="w-full text-xs py-1.5 px-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center justify-center gap-1">
                        <Phone className="h-3 w-3" />{h.phone}
                      </button>
                    </a>
                    {h.latitude && h.longitude && (
                      <a href={`https://www.google.com/maps?q=${h.latitude},${h.longitude}`}
                        target="_blank" rel="noopener noreferrer" onClick={e => e.stopPropagation()}
                        className="shrink-0">
                        <button className="py-1.5 px-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                          <Navigation className="h-3.5 w-3.5 text-gray-600" />
                        </button>
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center gap-2 mt-8">
                <button disabled={page === 1} onClick={() => setPage(p => p - 1)}
                  className="px-4 py-2 text-sm border border-gray-300 rounded-lg disabled:opacity-40 hover:bg-gray-50">
                  السابق
                </button>
                <span className="px-4 py-2 text-sm text-gray-600">صفحة {page} من {totalPages}</span>
                <button disabled={page === totalPages} onClick={() => setPage(p => p + 1)}
                  className="px-4 py-2 text-sm border border-gray-300 rounded-lg disabled:opacity-40 hover:bg-gray-50">
                  التالي
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Hospital Detail Modal */}
      {selected && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
          onClick={e => e.target === e.currentTarget && setSelected(null)}>
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-xl font-bold text-gray-900">{selected.name}</h2>
                {selected.name_en && <p className="text-sm text-gray-500">{selected.name_en}</p>}
              </div>
              <button onClick={() => setSelected(null)} className="p-1 hover:bg-gray-100 rounded">
                <X className="h-5 w-5 text-gray-400" />
              </button>
            </div>

            <div className="space-y-3 text-sm text-gray-700">
              <div className="flex items-start gap-2">
                <MapPin className="h-4 w-4 text-gray-400 mt-0.5 shrink-0" />
                <span>{selected.address} — {selected.city}</span>
              </div>
              <div className="flex items-center gap-2">
                <Phone className="h-4 w-4 text-gray-400" />
                <a href={`tel:${selected.phone}`} className="text-blue-600 hover:underline">{selected.phone}</a>
              </div>
              {selected.emergency_phone && (
                <div className="flex items-center gap-2">
                  <Heart className="h-4 w-4 text-red-500" />
                  <span>طوارئ: </span>
                  <a href={`tel:${selected.emergency_phone}`} className="text-red-600 hover:underline">{selected.emergency_phone}</a>
                </div>
              )}
              {selected.email && (
                <div className="flex items-center gap-2">
                  <Stethoscope className="h-4 w-4 text-gray-400" />
                  <a href={`mailto:${selected.email}`} className="text-blue-600 hover:underline">{selected.email}</a>
                </div>
              )}
              {selected.total_beds && (
                <p>السعة: <strong>{selected.total_beds}</strong> سرير
                  {selected.available_beds != null && ` — متاح: ${selected.available_beds}`}
                </p>
              )}
              {selected.icu_beds && (
                <p>العناية المركزة: <strong>{selected.icu_beds}</strong>
                  {selected.available_icu_beds != null && ` — متاح: ${selected.available_icu_beds}`}
                </p>
              )}
              {selected.rating > 0 && (
                <div className="flex items-center gap-2">
                  <Stars n={selected.rating} />
                  <span className="text-gray-500">({selected.total_reviews} تقييم)</span>
                </div>
              )}
            </div>

            <div className="flex gap-3 mt-5">
              <a href={`tel:${selected.phone}`} className="flex-1">
                <button className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium flex items-center justify-center gap-2">
                  <Phone className="h-4 w-4" /> اتصل الآن
                </button>
              </a>
              {selected.latitude && selected.longitude && (
                <a href={`https://www.google.com/maps?q=${selected.latitude},${selected.longitude}`}
                  target="_blank" rel="noopener noreferrer" className="shrink-0">
                  <button className="py-2.5 px-4 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 flex items-center gap-2">
                    <Navigation className="h-4 w-4" /> الخريطة
                  </button>
                </a>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
