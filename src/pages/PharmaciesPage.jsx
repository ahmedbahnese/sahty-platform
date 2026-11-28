import { useState, useEffect } from 'react'
import {
  Pill, Search, MapPin, Navigation, Phone, Clock, Filter,
  Building2, ChevronDown, X, Loader2, ExternalLink
} from 'lucide-react'

// Live data only: pharmacies come from the verified directory API
// (/api/facilities?type=Pharmacy). No sample data — a pharmacy must never
// appear in the hospitals, labs or radiology lists, and vice versa.
function normalizePharmacy(item) {
  return {
    ...item,
    name: item.name_ar || item.name_en || 'صيدلية غير مسماة',
    address: item.full_address || [item.city, item.governorate].filter(Boolean).join('، '),
    phone: item.phone_numbers || '',
    hours: item.working_hours || 'مواعيد العمل غير متاحة',
    hasDelivery: Boolean(item.home_services),
    isOpen: item.is_open,
  }
}

function PharmacyCard({ pharmacy }) {
  const mapsUrl = pharmacy.google_maps_url || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${pharmacy.name} ${pharmacy.address}`)}`
  const statusLabel = pharmacy.isOpen === null || pharmacy.isOpen === undefined
    ? 'مواعيد غير معروفة'
    : pharmacy.isOpen ? '● مفتوح' : '● مغلق'
  const statusClass = pharmacy.isOpen === null || pharmacy.isOpen === undefined
    ? 'bg-gray-100 text-gray-600'
    : pharmacy.isOpen ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-start gap-3 flex-1">
          <div className="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center shrink-0">
            <Pill className="w-5 h-5 text-green-600" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-gray-900 text-sm">{pharmacy.name}</h3>
            <p className="text-xs text-gray-500 mt-0.5 flex items-center gap-1">
              <MapPin className="w-3 h-3 shrink-0" />
              <span className="truncate">{pharmacy.address || 'العنوان غير متاح'}</span>
            </p>
          </div>
        </div>
        <span className={`text-xs px-2 py-1 rounded-lg font-medium shrink-0 ${statusClass}`}>
          {statusLabel}
        </span>
      </div>

      <div className="flex flex-wrap gap-2 mb-3">
        <div className="flex items-center gap-1 text-xs text-gray-500 bg-gray-50 rounded-lg px-2 py-1">
          <Clock className="w-3 h-3" /> {pharmacy.hours}
        </div>
        {pharmacy.hasDelivery && (
          <span className="text-xs bg-blue-50 text-blue-700 rounded-lg px-2 py-1 flex items-center gap-1">
            🚚 توصيل
          </span>
        )}
        {pharmacy.distance_km !== null && pharmacy.distance_km !== undefined && (
          <span className="text-xs bg-purple-50 text-purple-700 rounded-lg px-2 py-1">
            {pharmacy.distance_km} كم
          </span>
        )}
      </div>

      <div className="flex gap-2">
        {pharmacy.phone ? (
          <a href={`tel:${pharmacy.phone}`}
            className="flex-1 flex items-center justify-center gap-1.5 bg-green-600 hover:bg-green-700 text-white rounded-xl py-2 text-xs font-medium transition-colors">
            <Phone className="w-3.5 h-3.5" /> {pharmacy.phone}
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

export default function PharmaciesPage() {
  const [pharmacies, setPharmacies]       = useState([])
  const [metadata, setMetadata]           = useState({ governorates: [] })
  const [search, setSearch]               = useState('')
  const [govFilter, setGovFilter]         = useState('')
  const [deliveryOnly, setDeliveryOnly]   = useState(false)
  const [openOnly, setOpenOnly]           = useState(false)
  const [coords, setCoords]               = useState(null)
  const [locLoading, setLocLoading]       = useState(false)
  const [loading, setLoading]             = useState(true)
  const [error, setError]                 = useState('')

  useEffect(() => {
    fetch('/api/facilities/metadata')
      .then(response => response.ok ? response.json() : Promise.reject(new Error('metadata')))
      .then(data => setMetadata(data || { governorates: [] }))
      .catch(() => setMetadata({ governorates: [] }))
  }, [])

  useEffect(() => {
    const params = new URLSearchParams({ type: 'Pharmacy', per_page: '60' })
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
      .then(response => response.ok ? response.json() : Promise.reject(new Error('pharmacies')))
      .then(data => setPharmacies((data.facilities || []).map(normalizePharmacy)))
      .catch(() => {
        setPharmacies([])
        setError('تعذر تحميل دليل الصيدليات حاليًا. حاول مرة أخرى لاحقًا.')
      })
      .finally(() => setLoading(false))
  }, [search, govFilter, openOnly, coords])

  const filtered = deliveryOnly ? pharmacies.filter(p => p.hasDelivery) : pharmacies

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
      {/* رأس الصفحة */}
      <div className="bg-gradient-to-l from-green-700 to-green-500 text-white py-10 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center">
              <Pill className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">دليل الصيدليات</h1>
              <p className="text-green-100 text-sm">ابحث عن الصيدلية الأقرب إليك</p>
            </div>
          </div>
          <div className="mt-5 flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="ابحث باسم الصيدلية أو العنوان..."
                className="w-full pr-10 pl-4 py-3 rounded-xl text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-green-300"
              />
            </div>
            <button
              onClick={getLocation}
              disabled={locLoading}
              className="bg-white/20 hover:bg-white/30 border border-white/30 rounded-xl px-4 py-2 text-sm font-medium flex items-center gap-2 transition-colors disabled:opacity-60"
            >
              {locLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Navigation className="w-4 h-4" />}
              الأقرب
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* فلاتر */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 flex-wrap">
              <select
                value={govFilter}
                onChange={e => setGovFilter(e.target.value)}
                className="border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
              >
                <option value="">كل المحافظات</option>
                {metadata.governorates.map(g => <option key={g} value={g}>{g}</option>)}
              </select>
              <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                <input type="checkbox" className="accent-green-600" checked={deliveryOnly} onChange={e => setDeliveryOnly(e.target.checked)} />
                توصيل فقط
              </label>
              <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                <input type="checkbox" className="accent-green-600" checked={openOnly} onChange={e => setOpenOnly(e.target.checked)} />
                مفتوح الآن
              </label>
            </div>
            <span className="text-sm text-gray-500">{loading ? 'جار التحميل...' : `${filtered.length} صيدلية`}</span>
          </div>
        </div>

        {/* النتائج */}
        {error && <div className="mb-5 rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
        {loading ? (
          <div className="flex justify-center py-16"><Loader2 className="w-8 h-8 animate-spin text-green-600" /></div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <Pill className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>لا توجد صيدليات مطابقة للبحث</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-4">
            {filtered.map(p => <PharmacyCard key={p.id} pharmacy={p} />)}
          </div>
        )}
      </div>
    </div>
  )
}
