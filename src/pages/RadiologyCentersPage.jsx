import { useState, useEffect } from 'react'
import { Scan, Search, MapPin, Navigation, Phone, Clock, Loader2 } from 'lucide-react'

const SCAN_TYPES = ['أشعة X','رنين مغناطيسي','أشعة مقطعية CT','موجات صوتية','ماموجرام','PET Scan']

// Live data only: radiology centres come from the verified directory API
// (/api/facilities?type=Radiology Center). No sample data — a centre must
// never appear in the hospitals, pharmacies or labs lists, and vice versa.
function normalizeCenter(item) {
  return {
    ...item,
    name: item.name_ar || item.name_en || 'مركز أشعة غير مسمى',
    address: item.full_address || [item.city, item.governorate].filter(Boolean).join('، '),
    phone: item.phone_numbers || '',
    hours: item.working_hours || 'مواعيد العمل غير متاحة',
    isOpen: item.is_open,
    types: (item.services || item.specialty || '')
      .split(/[،,]/)
      .map(value => value.trim())
      .filter(Boolean),
  }
}

function CenterCard({ center }) {
  const mapsUrl = center.google_maps_url || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${center.name} ${center.address}`)}`
  const statusLabel = center.isOpen === null || center.isOpen === undefined
    ? 'مواعيد غير معروفة'
    : center.isOpen ? '● مفتوح' : '● مغلق'
  const statusClass = center.isOpen === null || center.isOpen === undefined
    ? 'bg-gray-100 text-gray-600'
    : center.isOpen ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-start gap-3 flex-1">
          <div className="w-10 h-10 bg-purple-100 rounded-xl flex items-center justify-center shrink-0">
            <Scan className="w-5 h-5 text-purple-600" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-gray-900 text-sm">{center.name}</h3>
            <p className="text-xs text-gray-500 mt-0.5 flex items-center gap-1">
              <MapPin className="w-3 h-3 shrink-0" />
              <span className="truncate">{center.address || 'العنوان غير متاح'}</span>
            </p>
          </div>
        </div>
        <span className={`text-xs px-2 py-1 rounded-lg font-medium shrink-0 ${statusClass}`}>
          {statusLabel}
        </span>
      </div>

      {center.types.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {center.types.map(t => (
            <span key={t} className="text-xs bg-purple-50 text-purple-700 rounded-lg px-2 py-0.5">{t}</span>
          ))}
        </div>
      )}

      <div className="flex flex-wrap gap-2 mb-3">
        <div className="flex items-center gap-1 text-xs text-gray-500 bg-gray-50 rounded-lg px-2 py-1">
          <Clock className="w-3 h-3" /> {center.hours}
        </div>
        {center.distance_km !== null && center.distance_km !== undefined && (
          <div className="flex items-center gap-1 text-xs text-purple-600 bg-purple-50 rounded-lg px-2 py-1">
            <Navigation className="w-3 h-3" /> {center.distance_km} كم
          </div>
        )}
      </div>

      <div className="flex gap-2">
        {center.phone ? (
          <a href={`tel:${center.phone}`}
            className="flex-1 flex items-center justify-center gap-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl py-2 text-xs font-medium transition-colors">
            <Phone className="w-3.5 h-3.5" /> {center.phone}
          </a>
        ) : (
          <span className="flex-1 flex items-center justify-center rounded-xl bg-gray-100 py-2 text-xs text-gray-500">الهاتف غير متاح</span>
        )}
        <a href={mapsUrl} target="_blank" rel="noopener noreferrer"
          className="flex items-center justify-center gap-1.5 border border-gray-200 hover:bg-gray-50 text-gray-600 rounded-xl px-3 py-2 text-xs transition-colors">
          <Navigation className="w-3.5 h-3.5" /> الاتجاهات
        </a>
      </div>
    </div>
  )
}

export default function RadiologyCentersPage() {
  const [centers, setCenters]           = useState([])
  const [metadata, setMetadata]         = useState({ governorates: [] })
  const [search, setSearch]             = useState('')
  const [govFilter, setGovFilter]       = useState('')
  const [typeFilter, setTypeFilter]     = useState('')
  const [openOnly, setOpenOnly]         = useState(false)
  const [coords, setCoords]             = useState(null)
  const [locLoading, setLocLoading]     = useState(false)
  const [loading, setLoading]           = useState(true)
  const [error, setError]               = useState('')

  useEffect(() => {
    fetch('/api/facilities/metadata')
      .then(response => response.ok ? response.json() : Promise.reject(new Error('metadata')))
      .then(data => setMetadata(data || { governorates: [] }))
      .catch(() => setMetadata({ governorates: [] }))
  }, [])

  useEffect(() => {
    const params = new URLSearchParams({ type: 'Radiology Center', per_page: '60' })
    if (search.trim()) params.set('search', search.trim())
    if (govFilter) params.set('governorate', govFilter)
    if (openOnly) params.set('open_now', '1')
    if (coords) {
      params.set('lat', coords.lat)
      params.set('lng', coords.lng)
      params.set('nearest', '1')
    }

    setLoading(true)
    setError('')
    fetch(`/api/facilities?${params}`)
      .then(response => response.ok ? response.json() : Promise.reject(new Error('radiology')))
      .then(data => setCenters((data.facilities || []).map(normalizeCenter)))
      .catch(() => {
        setCenters([])
        setError('تعذر تحميل دليل مراكز الأشعة حاليًا. حاول مرة أخرى لاحقًا.')
      })
      .finally(() => setLoading(false))
  }, [search, govFilter, openOnly, coords])

  const filtered = typeFilter
    ? centers.filter(c => c.types.includes(typeFilter))
    : centers

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
      <div className="bg-gradient-to-l from-purple-700 to-purple-500 text-white py-10 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center">
              <Scan className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">دليل مراكز الأشعة</h1>
              <p className="text-purple-100 text-sm">ابحث عن مركز أشعة موثوق بالقرب منك</p>
            </div>
          </div>
          <div className="mt-5 flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="ابحث باسم المركز أو العنوان..."
                className="w-full pr-10 pl-4 py-3 rounded-xl text-gray-800 text-sm focus:outline-none"
              />
            </div>
            <button onClick={getLocation} disabled={locLoading}
              className="bg-white/20 hover:bg-white/30 border border-white/30 rounded-xl px-4 py-2 text-sm font-medium flex items-center gap-2 transition-colors disabled:opacity-60">
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
              <select value={govFilter} onChange={e => setGovFilter(e.target.value)}
                className="border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none">
                <option value="">كل المحافظات</option>
                {metadata.governorates.map(g => <option key={g} value={g}>{g}</option>)}
              </select>
              <select value={typeFilter} onChange={e => setTypeFilter(e.target.value)}
                className="border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none">
                <option value="">كل أنواع الأشعة</option>
                {SCAN_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
              <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                <input type="checkbox" className="accent-purple-600" checked={openOnly} onChange={e => setOpenOnly(e.target.checked)} />
                مفتوح الآن
              </label>
            </div>
            <span className="text-sm text-gray-500">{loading ? 'جار التحميل...' : `${filtered.length} مركز`}</span>
          </div>
        </div>

        {error && <div className="mb-5 rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
        {loading ? (
          <div className="flex justify-center py-16"><Loader2 className="w-8 h-8 animate-spin text-purple-600" /></div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <Scan className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>لا توجد مراكز مطابقة للبحث</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-4">
            {filtered.map(c => <CenterCard key={c.id} center={c} />)}
          </div>
        )}
      </div>
    </div>
  )
}
