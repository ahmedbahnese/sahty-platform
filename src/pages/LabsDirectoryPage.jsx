import { useState, useEffect, useCallback } from 'react'
import { FlaskConical, Search, MapPin, Navigation, Phone, Clock, Star, Loader2, Home } from 'lucide-react'

const GOVERNORATES = ['القاهرة','الجيزة','الإسكندرية','القليوبية','الشرقية','المنوفية','الغربية','الدقهلية','دمياط','بورسعيد']

const SAMPLE_LABS = [
  { id: 1, name: 'معمل القاهرة المركزي', address: 'شارع رمسيس، وسط القاهرة', governorate: 'القاهرة', phone: '01001234567', hours: '7ص - 5م', rating: 4.6, hasHome: true, isOpen: true, specialties: ['دم كامل','هرمونات','ثقافة بكتيرية','سكر'] },
  { id: 2, name: 'معمل الدكتور إلياس', address: 'شارع مصدق، الدقي، الجيزة', governorate: 'الجيزة', phone: '01121234567', hours: '7ص - 4م', rating: 4.8, hasHome: true, isOpen: true, specialties: ['جينات','هرمونات','دم كامل'] },
  { id: 3, name: 'معمل النيل', address: 'شارع الجلاء، الإسكندرية', governorate: 'الإسكندرية', phone: '01231234567', hours: '8ص - 3م', rating: 4.2, hasHome: false, isOpen: true, specialties: ['دم','بول','براز'] },
  { id: 4, name: 'معمل الشيخ زايد', address: 'مدينة الشيخ زايد، الجيزة', governorate: 'الجيزة', phone: '01001122334', hours: '7:30ص - 5م', rating: 4.4, hasHome: true, isOpen: false, specialties: ['سكر','صدى قلب','هرمونات'] },
  { id: 5, name: 'معمل مدينة نصر', address: 'شارع عباس العقاد، مدينة نصر', governorate: 'القاهرة', phone: '01211122334', hours: '7ص - 4م', rating: 4.1, hasHome: true, isOpen: true, specialties: ['دم كامل','كبد','كلى'] },
  { id: 6, name: 'معمل الإسكندرية التخصصي', address: 'شارع صفر باشا، الإسكندرية', governorate: 'الإسكندرية', phone: '01001234000', hours: '8ص - 2م', rating: 4.5, hasHome: false, isOpen: true, specialties: ['أورام','هرمونات','دم','بول'] },
]

function LabCard({ lab }) {
  const mapsUrl = `https://www.google.com/maps/search/${encodeURIComponent(lab.name + ' ' + lab.address)}`
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
              <span className="truncate">{lab.address}</span>
            </p>
          </div>
        </div>
        <span className={`text-xs px-2 py-1 rounded-lg font-medium shrink-0 ${lab.isOpen ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
          {lab.isOpen ? '● مفتوح' : '● مغلق'}
        </span>
      </div>

      {/* التخصصات */}
      <div className="flex flex-wrap gap-1 mb-3">
        {lab.specialties.map(s => (
          <span key={s} className="text-xs bg-indigo-50 text-indigo-700 rounded-lg px-2 py-0.5">{s}</span>
        ))}
      </div>

      <div className="flex flex-wrap gap-2 mb-3">
        <div className="flex items-center gap-1 text-xs text-gray-500 bg-gray-50 rounded-lg px-2 py-1">
          <Clock className="w-3 h-3" /> {lab.hours}
        </div>
        <div className="flex items-center gap-1">
          <Star className="w-3.5 h-3.5 text-yellow-400 fill-yellow-400" />
          <span className="text-xs text-gray-600">{lab.rating}</span>
        </div>
        {lab.hasHome && (
          <span className="text-xs bg-blue-50 text-blue-700 rounded-lg px-2 py-1 flex items-center gap-1">
            <Home className="w-3 h-3" /> سحب منزلي
          </span>
        )}
      </div>

      <div className="flex gap-2">
        <a href={`tel:${lab.phone}`}
          className="flex-1 flex items-center justify-center gap-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl py-2 text-xs font-medium transition-colors">
          <Phone className="w-3.5 h-3.5" /> {lab.phone}
        </a>
        <a href={mapsUrl} target="_blank" rel="noopener noreferrer"
          className="flex items-center justify-center gap-1.5 border border-gray-200 hover:bg-gray-50 text-gray-600 rounded-xl px-3 py-2 text-xs transition-colors">
          <Navigation className="w-3.5 h-3.5" /> الاتجاهات
        </a>
      </div>
    </div>
  )
}

export default function LabsDirectoryPage() {
  const [labs, setLabs]             = useState(SAMPLE_LABS)
  const [filtered, setFiltered]     = useState(SAMPLE_LABS)
  const [search, setSearch]         = useState('')
  const [govFilter, setGovFilter]   = useState('')
  const [homeOnly, setHomeOnly]     = useState(false)
  const [openOnly, setOpenOnly]     = useState(false)
  const [locLoading, setLocLoading] = useState(false)
  const [coords, setCoords]         = useState(null)

  const applyFilters = useCallback(() => {
    let list = labs
    if (search)   list = list.filter(l => l.name.includes(search) || l.address.includes(search) || l.specialties.some(s => s.includes(search)))
    if (govFilter) list = list.filter(l => l.governorate === govFilter)
    if (homeOnly)  list = list.filter(l => l.hasHome)
    if (openOnly)  list = list.filter(l => l.isOpen)
    setFiltered(list)
  }, [labs, search, govFilter, homeOnly, openOnly])

  useEffect(() => { applyFilters() }, [applyFilters])

  const getLocation = () => {
    if (!navigator.geolocation) return
    setLocLoading(true)
    navigator.geolocation.getCurrentPosition(
      ({ coords: c }) => { setCoords({ lat: c.latitude, lng: c.longitude }); setLocLoading(false) },
      () => setLocLoading(false)
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
              <p className="text-indigo-100 text-sm">ابحث عن المعمل المناسب لإجراء تحاليلك</p>
            </div>
          </div>
          <div className="mt-5 flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="ابحث باسم المعمل أو نوع التحليل..."
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
                {GOVERNORATES.map(g => <option key={g} value={g}>{g}</option>)}
              </select>
              <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                <input type="checkbox" className="accent-indigo-600" checked={homeOnly} onChange={e => setHomeOnly(e.target.checked)} />
                سحب منزلي
              </label>
              <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                <input type="checkbox" className="accent-indigo-600" checked={openOnly} onChange={e => setOpenOnly(e.target.checked)} />
                مفتوح الآن
              </label>
            </div>
            <span className="text-sm text-gray-500">{filtered.length} معمل</span>
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <FlaskConical className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>لا توجد معامل مطابقة للبحث</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-4">
            {filtered.map(l => <LabCard key={l.id} lab={l} />)}
          </div>
        )}
      </div>
    </div>
  )
}
