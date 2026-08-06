import { useState, useEffect, useCallback } from 'react'
import {
  Pill, Search, MapPin, Navigation, Phone, Clock, Star, Filter,
  Building2, ChevronDown, X, Loader2, ExternalLink
} from 'lucide-react'

const GOVERNORATES = [
  'القاهرة', 'الجيزة', 'الإسكندرية', 'القليوبية', 'الشرقية',
  'المنوفية', 'الغربية', 'كفر الشيخ', 'البحيرة', 'الدقهلية',
  'دمياط', 'بورسعيد', 'الإسماعيلية', 'السويس', 'شمال سيناء',
  'جنوب سيناء', 'البحر الأحمر', 'الفيوم', 'بني سويف', 'المنيا',
  'أسيوط', 'سوهاج', 'قنا', 'الأقصر', 'أسوان', 'مطروح', 'الوادي الجديد'
]

const SAMPLE_PHARMACIES = [
  { id: 1, name: 'صيدلية النهضة', address: 'شارع التحرير، وسط البلد، القاهرة', governorate: 'القاهرة', phone: '01001234567', hours: '24 ساعة', rating: 4.5, distance: null, hasDelivery: true, isOpen: true },
  { id: 2, name: 'صيدلية العزبي', address: 'شارع النزهة، مدينة نصر، القاهرة', governorate: 'القاهرة', phone: '01121234567', hours: '8ص - 12م', rating: 4.3, distance: null, hasDelivery: true, isOpen: true },
  { id: 3, name: 'صيدلية مصر الجديدة', address: 'شارع الثورة، مصر الجديدة', governorate: 'القاهرة', phone: '01231234567', hours: '9ص - 11م', rating: 4.1, distance: null, hasDelivery: false, isOpen: true },
  { id: 4, name: 'صيدلية الدكتور محمد', address: 'شارع المريوطية، الهرم، الجيزة', governorate: 'الجيزة', phone: '01001122334', hours: '24 ساعة', rating: 4.7, distance: null, hasDelivery: true, isOpen: true },
  { id: 5, name: 'صيدلية المعادي الصحية', address: 'شارع 9، المعادي، القاهرة', governorate: 'القاهرة', phone: '01211122334', hours: '8ص - 1ص', rating: 4.2, distance: null, hasDelivery: false, isOpen: false },
  { id: 6, name: 'صيدلية سيدي جابر', address: 'شارع مصطفى كامل، الإسكندرية', governorate: 'الإسكندرية', phone: '01001234000', hours: '24 ساعة', rating: 4.4, distance: null, hasDelivery: true, isOpen: true },
  { id: 7, name: 'صيدلية زهراء المعادي', address: 'شارع النصر، المعادي الجديدة', governorate: 'القاهرة', phone: '01121234000', hours: '8ص - 12م', rating: 3.9, distance: null, hasDelivery: true, isOpen: true },
  { id: 8, name: 'صيدلية الدولية', address: 'شارع فيصل، الجيزة', governorate: 'الجيزة', phone: '01001555444', hours: '9ص - 10م', rating: 4.6, distance: null, hasDelivery: false, isOpen: true },
]

function StarRating({ rating }) {
  return (
    <div className="flex items-center gap-1">
      <Star className="w-3.5 h-3.5 text-yellow-400 fill-yellow-400" />
      <span className="text-xs text-gray-600">{rating}</span>
    </div>
  )
}

function PharmacyCard({ pharmacy, coords }) {
  const mapsUrl = `https://www.google.com/maps/search/${encodeURIComponent(pharmacy.name + ' ' + pharmacy.address)}`

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
              <span className="truncate">{pharmacy.address}</span>
            </p>
          </div>
        </div>
        <span className={`text-xs px-2 py-1 rounded-lg font-medium shrink-0 ${pharmacy.isOpen ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
          {pharmacy.isOpen ? '● مفتوح' : '● مغلق'}
        </span>
      </div>

      <div className="flex flex-wrap gap-2 mb-3">
        <div className="flex items-center gap-1 text-xs text-gray-500 bg-gray-50 rounded-lg px-2 py-1">
          <Clock className="w-3 h-3" /> {pharmacy.hours}
        </div>
        <StarRating rating={pharmacy.rating} />
        {pharmacy.hasDelivery && (
          <span className="text-xs bg-blue-50 text-blue-700 rounded-lg px-2 py-1 flex items-center gap-1">
            🚚 توصيل
          </span>
        )}
        {pharmacy.distance && (
          <span className="text-xs bg-purple-50 text-purple-700 rounded-lg px-2 py-1">
            {pharmacy.distance} كم
          </span>
        )}
      </div>

      <div className="flex gap-2">
        <a href={`tel:${pharmacy.phone}`}
          className="flex-1 flex items-center justify-center gap-1.5 bg-green-600 hover:bg-green-700 text-white rounded-xl py-2 text-xs font-medium transition-colors">
          <Phone className="w-3.5 h-3.5" /> {pharmacy.phone}
        </a>
        <a href={mapsUrl} target="_blank" rel="noopener noreferrer"
          className="flex items-center justify-center gap-1.5 border border-gray-200 hover:bg-gray-50 text-gray-600 rounded-xl px-3 py-2 text-xs transition-colors">
          <Navigation className="w-3.5 h-3.5" /> الاتجاهات
        </a>
      </div>
    </div>
  )
}

export default function PharmaciesPage() {
  const [pharmacies, setPharmacies]       = useState(SAMPLE_PHARMACIES)
  const [filtered, setFiltered]           = useState(SAMPLE_PHARMACIES)
  const [search, setSearch]               = useState('')
  const [govFilter, setGovFilter]         = useState('')
  const [deliveryOnly, setDeliveryOnly]   = useState(false)
  const [openOnly, setOpenOnly]           = useState(false)
  const [coords, setCoords]               = useState(null)
  const [locLoading, setLocLoading]       = useState(false)
  const [showFilters, setShowFilters]     = useState(false)

  const applyFilters = useCallback(() => {
    let list = pharmacies
    if (search)       list = list.filter(p => p.name.includes(search) || p.address.includes(search))
    if (govFilter)    list = list.filter(p => p.governorate === govFilter)
    if (deliveryOnly) list = list.filter(p => p.hasDelivery)
    if (openOnly)     list = list.filter(p => p.isOpen)
    setFiltered(list)
  }, [pharmacies, search, govFilter, deliveryOnly, openOnly])

  useEffect(() => { applyFilters() }, [applyFilters])

  const getLocation = () => {
    if (!navigator.geolocation) return
    setLocLoading(true)
    navigator.geolocation.getCurrentPosition(
      ({ coords: c }) => {
        setCoords({ lat: c.latitude, lng: c.longitude })
        setLocLoading(false)
        // Sort by distance (simulated)
        const sorted = [...pharmacies].sort(() => Math.random() - 0.5).map((p, i) => ({
          ...p, distance: (0.5 + i * 0.8).toFixed(1)
        }))
        setPharmacies(sorted)
      },
      () => setLocLoading(false)
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
                {GOVERNORATES.map(g => <option key={g} value={g}>{g}</option>)}
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
            <span className="text-sm text-gray-500">{filtered.length} صيدلية</span>
          </div>
        </div>

        {/* النتائج */}
        {filtered.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <Pill className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>لا توجد صيدليات مطابقة للبحث</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-4">
            {filtered.map(p => <PharmacyCard key={p.id} pharmacy={p} coords={coords} />)}
          </div>
        )}
      </div>
    </div>
  )
}
