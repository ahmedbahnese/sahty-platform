import { useEffect, useMemo, useState } from 'react'
import {
  Building2, Clock3, FlaskConical, Home, Loader2, MapPin, Navigation,
  Phone, Pill, Radio, Search, ShieldCheck, X,
} from 'lucide-react'

const TYPES = [
  { value: 'Hospital', label: 'المستشفيات', icon: Building2, color: 'blue' },
  { value: 'Pharmacy', label: 'الصيدليات', icon: Pill, color: 'emerald' },
  { value: 'Laboratory', label: 'معامل التحاليل', icon: FlaskConical, color: 'amber' },
  { value: 'Radiology Center', label: 'مراكز الأشعة', icon: Radio, color: 'purple' },
  { value: 'Blood Bank', label: 'بنوك الدم', icon: ShieldCheck, color: 'rose' },
]

function DirectoryCard({ item, onDetails }) {
  const TypeIcon = TYPES.find(type => type.value === item.facility_type)?.icon || Building2
  const maps = item.google_maps_url || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${item.name_en} ${item.full_address || ''}`)}`
  return (
    <article className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex items-start gap-3">
        <div className="rounded-xl bg-blue-50 p-3 text-blue-600"><TypeIcon className="h-5 w-5" /></div>
        <div className="min-w-0 flex-1">
          <h2 className="truncate font-bold text-gray-900">{item.name_ar}</h2>
          <p className="truncate text-xs text-gray-500">{item.name_en}</p>
        </div>
        {item.is_open !== null && item.is_open !== undefined && (
          <span className={`shrink-0 rounded-full px-2 py-1 text-xs font-semibold ${item.is_open ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'}`}>
            {item.is_open ? 'مفتوح الآن' : 'مغلق الآن'}
          </span>
        )}
      </div>
      <div className="mt-4 space-y-2 text-sm text-gray-600">
        <p className="flex items-start gap-2"><MapPin className="mt-0.5 h-4 w-4 shrink-0 text-gray-400" />{item.full_address || `${item.city}، ${item.governorate}`}</p>
        <p className="flex items-center gap-2"><Phone className="h-4 w-4 text-gray-400" />{item.phone_numbers || 'غير متاح'}</p>
        {item.working_hours && <p className="flex items-center gap-2"><Clock3 className="h-4 w-4 text-gray-400" />{item.working_hours}</p>}
        {item.distance_km !== null && item.distance_km !== undefined && <p className="flex items-center gap-2 text-blue-600"><Navigation className="h-4 w-4" />{item.distance_km} كم</p>}
      </div>
      {item.specialty && <p className="mt-3 line-clamp-2 text-xs text-gray-500">الخدمات/التخصصات: {item.specialty}</p>}
      <div className="mt-4 flex gap-2">
        {item.phone_numbers && <a href={`tel:${item.phone_numbers}`} className="flex-1 rounded-xl bg-blue-600 px-3 py-2 text-center text-xs font-semibold text-white hover:bg-blue-700"><Phone className="mr-1 inline h-3.5 w-3.5" />اتصال</a>}
        <a href={maps} target="_blank" rel="noreferrer" className="rounded-xl border border-gray-200 px-3 py-2 text-xs text-gray-700 hover:bg-gray-50"><Navigation className="mr-1 inline h-3.5 w-3.5" />الاتجاهات</a>
        <button onClick={() => onDetails(item)} className="rounded-xl border border-gray-200 px-3 py-2 text-xs text-gray-700 hover:bg-gray-50">التفاصيل</button>
      </div>
    </article>
  )
}

export default function HealthcareDirectoryPage() {
  const [type, setType] = useState('Hospital')
  const [items, setItems] = useState([])
  const [metadata, setMetadata] = useState({ governorates: [], cities: [] })
  const [search, setSearch] = useState('')
  const [governorate, setGovernorate] = useState('')
  const [city, setCity] = useState('')
  const [specialty, setSpecialty] = useState('')
  const [openNow, setOpenNow] = useState(false)
  const [nearest, setNearest] = useState(false)
  const [coords, setCoords] = useState(null)
  const [locationMessage, setLocationMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    fetch('/api/facilities/metadata').then(response => response.ok ? response.json() : null).then(data => data && setMetadata(data)).catch(() => {})
  }, [])

  useEffect(() => {
    const params = new URLSearchParams({ type, per_page: '60' })
    if (search.trim()) params.set('search', search.trim())
    if (governorate) params.set('governorate', governorate)
    if (city) params.set('city', city)
    if (specialty.trim()) params.set('specialty', specialty.trim())
    if (openNow) params.set('open_now', '1')
    if (nearest) params.set('nearest', '1')
    if (coords) { params.set('lat', coords.lat); params.set('lng', coords.lng) }
    setLoading(true); setError('')
    fetch(`/api/facilities?${params}`)
      .then(response => response.ok ? response.json() : Promise.reject())
      .then(data => setItems(data.facilities || []))
      .catch(() => setError('تعذر تحميل بيانات الدليل الطبي'))
      .finally(() => setLoading(false))
  }, [type, search, governorate, city, specialty, openNow, nearest, coords])

  const requestLocation = () => {
    if (!navigator.geolocation) { setLocationMessage('المتصفح لا يدعم تحديد الموقع'); return }
    setLocationMessage('جاري طلب موقعك...')
    navigator.geolocation.getCurrentPosition(
      position => { setCoords({ lat: position.coords.latitude, lng: position.coords.longitude }); setNearest(true); setLocationMessage('تم ترتيب النتائج حسب الأقرب') },
      () => { setLocationMessage('تعذر تحديد الموقع؛ يمكنك متابعة البحث بالمحافظة والمدينة') ; setNearest(false) },
      { enableHighAccuracy: true, timeout: 10000 }
    )
  }

  const cities = useMemo(() => metadata.cities || [], [metadata.cities])
  const selectedType = TYPES.find(item => item.value === type)

  return (
    <div className="min-h-screen bg-gray-50 py-8" dir="rtl">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <header className="mb-6 rounded-3xl bg-gradient-to-l from-[#0f2444] to-blue-600 p-6 text-white shadow-lg">
          <div className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
            <div><p className="mb-2 text-sm text-blue-100">صحتك في أمان</p><h1 className="text-3xl font-bold">الدليل الطبي</h1><p className="mt-2 text-sm text-blue-100">ابحث في قاعدة بيانات المنشآت الصحية المصرية المرفقة</p></div>
            <button onClick={requestLocation} className="rounded-xl border border-white/30 bg-white/10 px-4 py-3 text-sm hover:bg-white/20"><Navigation className="ml-2 inline h-4 w-4" />الأقرب لموقعي</button>
          </div>
        </header>
        <div className="mb-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {TYPES.map(category => { const Icon = category.icon; return <button key={category.value} onClick={() => setType(category.value)} className={`flex items-center gap-3 rounded-2xl border p-4 text-right transition ${type === category.value ? 'border-blue-500 bg-blue-50 text-blue-700 shadow-sm' : 'border-gray-100 bg-white text-gray-700 hover:border-blue-200'}`}><Icon className="h-5 w-5" /><span className="font-semibold">{category.label}</span></button> })}
        </div>
        <section className="mb-6 rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-5">
            <label className="relative lg:col-span-2"><Search className="absolute right-3 top-3 h-4 w-4 text-gray-400" /><input value={search} onChange={event => setSearch(event.target.value)} placeholder={`ابحث في ${selectedType?.label || 'الدليل'}...`} className="w-full rounded-xl border border-gray-200 py-2.5 pr-10 pl-3 text-sm outline-none focus:border-blue-400" /></label>
            <select value={governorate} onChange={event => setGovernorate(event.target.value)} className="rounded-xl border border-gray-200 px-3 py-2 text-sm"><option value="">كل المحافظات</option>{metadata.governorates.map(value => <option key={value}>{value}</option>)}</select>
            <select value={city} onChange={event => setCity(event.target.value)} className="rounded-xl border border-gray-200 px-3 py-2 text-sm"><option value="">كل المدن</option>{cities.map(value => <option key={value}>{value}</option>)}</select>
            <input value={specialty} onChange={event => setSpecialty(event.target.value)} placeholder="التخصص / الخدمة" className="rounded-xl border border-gray-200 px-3 py-2 text-sm outline-none" />
          </div>
          <div className="mt-4 flex flex-wrap items-center gap-4 text-sm text-gray-600">
            {type === 'Hospital' && <label><input type="checkbox" className="ml-2 accent-blue-600" checked={openNow} onChange={event => setOpenNow(event.target.checked)} />طوارئ / مفتوح الآن</label>}
            {type !== 'Hospital' && <label><input type="checkbox" className="ml-2 accent-blue-600" checked={openNow} onChange={event => setOpenNow(event.target.checked)} />مفتوح الآن</label>}
            <label><input type="checkbox" className="ml-2 accent-blue-600" checked={nearest} onChange={event => event.target.checked ? requestLocation() : setNearest(false)} />الأقرب لموقعي</label>
            {locationMessage && <span className="text-xs text-blue-600">{locationMessage}</span>}
            <span className="mr-auto text-gray-400">{items.length} نتيجة</span>
          </div>
        </section>
        {loading && <div className="flex justify-center py-20"><Loader2 className="h-10 w-10 animate-spin text-blue-600" /></div>}
        {!loading && error && <div className="rounded-2xl border border-red-200 bg-red-50 p-5 text-red-700">{error}</div>}
        {!loading && !error && items.length === 0 && <div className="rounded-2xl border border-dashed border-gray-200 bg-white py-20 text-center text-gray-500"><ShieldCheck className="mx-auto mb-3 h-10 w-10 text-gray-300" /><p>لا توجد نتائج مطابقة للفلاتر الحالية</p></div>}
        {!loading && !error && items.length > 0 && <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{items.map(item => <DirectoryCard key={item.id} item={item} onDetails={setSelected} />)}</div>}
      </div>
      {selected && <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={event => event.target === event.currentTarget && setSelected(null)}><div className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-2xl bg-white p-6"><div className="mb-5 flex items-start justify-between"><div><h2 className="text-xl font-bold">{selected.name_ar}</h2><p className="text-sm text-gray-500">{selected.name_en}</p></div><button onClick={() => setSelected(null)}><X className="h-5 w-5 text-gray-500" /></button></div><div className="space-y-3 text-sm text-gray-700"><p><b>النوع:</b> {selected.facility_type}</p><p><b>العنوان:</b> {selected.full_address || `${selected.city}، ${selected.governorate}`}</p><p><b>الهاتف:</b> {selected.phone_numbers || 'غير متاح'}</p><p><b>الخدمات:</b> {selected.services || 'غير متاح في المصدر'}</p><p><b>المصدر:</b> {selected.data_source || 'قاعدة الدليل المرفقة'}</p></div></div></div>}
    </div>
  )
}