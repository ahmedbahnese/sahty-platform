import { useState, useEffect, useCallback } from 'react'
import { Scan, Search, MapPin, Navigation, Phone, Clock, Star, Loader2 } from 'lucide-react'

const GOVERNORATES = ['القاهرة','الجيزة','الإسكندرية','القليوبية','الشرقية','المنوفية']

const SCAN_TYPES = ['أشعة X','رنين مغناطيسي','أشعة مقطعية CT','موجات صوتية','ماموجرام','PET Scan']

const SAMPLE_CENTERS = [
  { id: 1, name: 'مركز سكان التصوير الطبي', address: 'شارع التحرير، وسط القاهرة', governorate: 'القاهرة', phone: '01001234567', hours: '8ص - 8م', rating: 4.7, isOpen: true, types: ['أشعة X','رنين مغناطيسي','أشعة مقطعية CT','موجات صوتية'] },
  { id: 2, name: 'مركز الأشعة التخصصي', address: 'شارع يوسف عباس، مدينة نصر', governorate: 'القاهرة', phone: '01121234567', hours: '9ص - 6م', rating: 4.4, isOpen: true, types: ['رنين مغناطيسي','أشعة مقطعية CT','ماموجرام'] },
  { id: 3, name: 'مركز النيل للأشعة', address: 'شارع المنيل، الجيزة', governorate: 'الجيزة', phone: '01231234567', hours: '8ص - 4م', rating: 4.2, isOpen: true, types: ['أشعة X','موجات صوتية','أشعة مقطعية CT'] },
  { id: 4, name: 'مركز الإسكندرية الطبي', address: 'شارع سيدي جابر، الإسكندرية', governorate: 'الإسكندرية', phone: '01001122334', hours: '8ص - 10م', rating: 4.5, isOpen: false, types: ['أشعة X','رنين مغناطيسي','ماموجرام','موجات صوتية'] },
  { id: 5, name: 'مركز المعادي للأشعة', address: 'شارع 9، المعادي، القاهرة', governorate: 'القاهرة', phone: '01211122334', hours: '9ص - 7م', rating: 4.3, isOpen: true, types: ['أشعة X','موجات صوتية','رنين مغناطيسي'] },
  { id: 6, name: 'مركز الدقي التصويري', address: 'شارع مصدق، الدقي، الجيزة', governorate: 'الجيزة', phone: '01001234000', hours: '8ص - 5م', rating: 4.6, isOpen: true, types: ['رنين مغناطيسي','أشعة مقطعية CT','PET Scan','موجات صوتية'] },
]

function CenterCard({ center }) {
  const mapsUrl = `https://www.google.com/maps/search/${encodeURIComponent(center.name + ' ' + center.address)}`
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
              <span className="truncate">{center.address}</span>
            </p>
          </div>
        </div>
        <span className={`text-xs px-2 py-1 rounded-lg font-medium shrink-0 ${center.isOpen ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
          {center.isOpen ? '● مفتوح' : '● مغلق'}
        </span>
      </div>

      <div className="flex flex-wrap gap-1 mb-3">
        {center.types.map(t => (
          <span key={t} className="text-xs bg-purple-50 text-purple-700 rounded-lg px-2 py-0.5">{t}</span>
        ))}
      </div>

      <div className="flex flex-wrap gap-2 mb-3">
        <div className="flex items-center gap-1 text-xs text-gray-500 bg-gray-50 rounded-lg px-2 py-1">
          <Clock className="w-3 h-3" /> {center.hours}
        </div>
        <div className="flex items-center gap-1">
          <Star className="w-3.5 h-3.5 text-yellow-400 fill-yellow-400" />
          <span className="text-xs text-gray-600">{center.rating}</span>
        </div>
      </div>

      <div className="flex gap-2">
        <a href={`tel:${center.phone}`}
          className="flex-1 flex items-center justify-center gap-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl py-2 text-xs font-medium transition-colors">
          <Phone className="w-3.5 h-3.5" /> {center.phone}
        </a>
        <a href={mapsUrl} target="_blank" rel="noopener noreferrer"
          className="flex items-center justify-center gap-1.5 border border-gray-200 hover:bg-gray-50 text-gray-600 rounded-xl px-3 py-2 text-xs transition-colors">
          <Navigation className="w-3.5 h-3.5" /> الاتجاهات
        </a>
      </div>
    </div>
  )
}

export default function RadiologyCentersPage() {
  const [centers, setCenters]       = useState(SAMPLE_CENTERS)
  const [filtered, setFiltered]     = useState(SAMPLE_CENTERS)
  const [search, setSearch]         = useState('')
  const [govFilter, setGovFilter]   = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [openOnly, setOpenOnly]     = useState(false)
  const [locLoading, setLocLoading] = useState(false)

  const applyFilters = useCallback(() => {
    let list = centers
    if (search)     list = list.filter(c => c.name.includes(search) || c.address.includes(search))
    if (govFilter)  list = list.filter(c => c.governorate === govFilter)
    if (typeFilter) list = list.filter(c => c.types.includes(typeFilter))
    if (openOnly)   list = list.filter(c => c.isOpen)
    setFiltered(list)
  }, [centers, search, govFilter, typeFilter, openOnly])

  useEffect(() => { applyFilters() }, [applyFilters])

  const getLocation = () => {
    if (!navigator.geolocation) return
    setLocLoading(true)
    navigator.geolocation.getCurrentPosition(
      () => setLocLoading(false),
      () => setLocLoading(false)
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
                {GOVERNORATES.map(g => <option key={g} value={g}>{g}</option>)}
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
            <span className="text-sm text-gray-500">{filtered.length} مركز</span>
          </div>
        </div>

        {filtered.length === 0 ? (
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
