import { useEffect, useState } from 'react'
import { FlaskConical, Search, MapPin, Navigation, Phone, Clock, Loader2, Home } from 'lucide-react'

function normalizeLab(item) {
  return {
    ...item,
    name: item.name_ar || item.name_en || 'معمل غير مسمى',
    address: item.full_address || [item.city, item.governorate].filter(Boolean).join('، '),
    phone: item.phone_numbers || '',
    hours: item.working_hours || 'مواعيد العمل غير متاحة',
    hasHome: Boolean(item.home_services),
    isOpen: item.is_open,
    specialties: (item.services || item.specialty || '')
      .split(/[،,]/)
      .map(value => value.trim())
      .filter(Boolean),
  }
}

function LabCard({ lab }) {
  const mapsUrl = lab.google_maps_url || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${lab.name} ${lab.address}`)}`
  const statusLabel = lab.isOpen === null || lab.isOpen === undefined
    ? 'مواعيد غير معروفة'
    : lab.isOpen ? '● مفتوح' : '● مغلق'
  const statusClass = lab.isOpen === null || lab.isOpen === undefined
    ? 'bg-gray-100 text-gray-600'
    : lab.isOpen ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-start gap-3 flex-1">
          <div className="w-10 h-10 bg-indigo-100 rounded-xl flex items-center justify-center shrink-0">
            <FlaskConical className="w-5 h-5 text-indigo-600" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-gray-900 text-sm">{lab.name}</h3>
            <p className="text-xs text-gray-500 mt-0.5 flex items-center gap-1">
              <MapPin className="w-3 h-3 shrink-0" />
              <span className="truncate">{lab.address || 'العنوان غير متاح'}</span>
            </p>
          </div>
        </div>
        <span className={`text-xs px-2 py-1 rounded-lg font-medium shrink-0 ${statusClass}`}>
          {statusLabel}
        </span>
      </div>

      {lab.specialties.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {lab.specialties.map(specialty => (
            <span key={specialty} className="text-xs bg-indigo-50 text-indigo-700 rounded-lg px-2 py-0.5">{specialty}</span>
          ))}
        </div>
      )}

      <div className="flex flex-wrap gap-2 mb-3">
        <div className="flex items-center gap-1 text-xs text-gray-500 bg-gray-50 rounded-lg px-2 py-1">
          <Clock className="w-3 h-3" /> {lab.hours}
        </div>
        {lab.distance_km !== null && lab.distance_km !== undefined && (
          <div className="flex items-center gap-1 text-xs text-indigo-600 bg-indigo-50 rounded-lg px-2 py-1">
            <Navigation className="w-3 h-3" /> {lab.distance_km} كم
          </div>
        )}
        {lab.hasHome && (
          <span className="text-xs bg-blue-50 text-blue-700 rounded-lg px-2 py-1 flex items-center gap-1">
            <Home className="w-3 h-3" /> سحب منزلي
          </span>
        )}
      </div>

      <div className="flex gap-2">
        {lab.phone ? (
          <a href={`tel:${lab.phone}`} className="flex-1 flex items-center justify-center gap-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl py-2 text-xs font-medium transition-colors">
            <Phone className="w-3.5 h-3.5" /> {lab.phone}
          </a>
        ) : (
          <span className="flex-1 flex items-center justify-center rounded-xl bg-gray-100 py-2 text-xs text-gray-500">الهاتف غير متاح</span>
        )}
        <a href={mapsUrl} target="_blank" rel="noopener noreferrer" className="flex items-center justify-center gap-1.5 border border-gray-200 hover:bg-gray-50 text-gray-600 rounded-xl px-3 py-2 text-xs transition-colors">
          <Navigation className="w-3.5 h-3.5" /> الاتجاهات
        </a>
      </div>
    </div>
  )
}

export default function LabsDirectoryPage() {
  const [labs, setLabs] = useState([])
  const [metadata, setMetadata] = useState({ governorates: [] })
  const [search, setSearch] = useState('')
  const [govFilter, setGovFilter] = useState('')
  const [homeOnly, setHomeOnly] = useState(false)
  const [openOnly, setOpenOnly] = useState(false)
  const [locLoading, setLocLoading] = useState(false)
  const [coords, setCoords] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch('/api/facilities/metadata')
      .then(response => response.ok ? response.json() : Promise.reject(new Error('metadata')))
      .then(data => setMetadata(data || { governorates: [] }))
      .catch(() => setMetadata({ governorates: [] }))
  }, [])

  useEffect(() => {
    const params = new URLSearchParams({ type: 'Laboratory', per_page: '60' })
    if (search.trim()) params.set('search', search.trim())
    if (govFilter) params.set('governorate', govFilter)
    if (homeOnly) params.set('home_services', '1')
    if (openOnly) params.set('open_now', '1')
    if (coords) {
      params.set('lat', coords.lat)
      params.set('lng', coords.lng)
      params.set('nearest', '1')
    }

    setLoading(true)
    setError('')
    fetch(`/api/facilities?${params}`)
      .then(response => response.ok ? response.json() : Promise.reject(new Error('labs')))
      .then(data => setLabs((data.facilities || []).map(normalizeLab)))
      .catch(() => {
        setLabs([])
        setError('تعذر تحميل دليل المعامل حاليًا. حاول مرة أخرى لاحقًا.')
      })
      .finally(() => setLoading(false))
  }, [search, govFilter, homeOnly, openOnly, coords])

  const getLocation = () => {
    if (!navigator.geolocation) {
      setError('الموقع الجغرافي غير مدعوم في هذا المتصفح.')
      return
    }
    setLocLoading(true)
    navigator.geolocation.getCurrentPosition(
      ({ coords: current }) => {
        setCoords({ lat: current.latitude, lng: current.longitude })
        setLocLoading(false)
      },
      () => {
        setLocLoading(false)
        setError('تعذر الوصول إلى موقعك. يمكنك استخدام البحث والمحافظة بدلًا من ذلك.')
      },
      { enableHighAccuracy: true, timeout: 10000 }
    )
  }

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      <div className="bg-gradient-to-l from-indigo-700 to-indigo-500 text-white py-10 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center">
              <FlaskConical className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">دليل المعامل والتحاليل</h1>
              <p className="text-indigo-100 text-sm">بيانات منشآت مرتبطة بدليل صحتي</p>
            </div>
          </div>
          <div className="mt-5 flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input value={search} onChange={event => setSearch(event.target.value)} placeholder="ابحث باسم المعمل أو نوع التحليل..." className="w-full pr-10 pl-4 py-3 rounded-xl text-gray-800 text-sm focus:outline-none" />
            </div>
            <button onClick={getLocation} disabled={locLoading} className="bg-white/20 hover:bg-white/30 border border-white/30 rounded-xl px-4 py-2 text-sm font-medium flex items-center gap-2 transition-colors disabled:opacity-60">
              {locLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Navigation className="w-4 h-4" />}
              الأقرب
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 mb-6">
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div className="flex items-center gap-3 flex-wrap">
              <select value={govFilter} onChange={event => setGovFilter(event.target.value)} className="border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none">
                <option value="">كل المحافظات</option>
                {metadata.governorates.map(governorate => <option key={governorate} value={governorate}>{governorate}</option>)}
              </select>
              <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                <input type="checkbox" className="accent-indigo-600" checked={homeOnly} onChange={event => setHomeOnly(event.target.checked)} />
                سحب منزلي
              </label>
              <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                <input type="checkbox" className="accent-indigo-600" checked={openOnly} onChange={event => setOpenOnly(event.target.checked)} />
                مفتوح الآن
              </label>
            </div>
            <span className="text-sm text-gray-500">{loading ? 'جار التحميل...' : `${labs.length} معمل`}</span>
          </div>
        </div>

        {error && <div className="mb-5 rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
        {loading ? (
          <div className="flex justify-center py-16"><Loader2 className="w-8 h-8 animate-spin text-indigo-600" /></div>
        ) : labs.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <FlaskConical className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>لا توجد معامل مطابقة للبحث</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-4">
            {labs.map(lab => <LabCard key={lab.id} lab={lab} />)}
          </div>
        )}
      </div>
    </div>
  )
}
