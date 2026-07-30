import { useState, useEffect } from 'react'
import { Building2, MapPin, Phone, Navigation, Filter, Star, Clock, Heart, Stethoscope, X } from 'lucide-react'

/* ─── Egyptian hospitals dataset ─── */
const HOSPITALS = [
  { id:1,  name:'مستشفى قصر العيني',              nameEn:'Kasr Al-Ainy Hospital',    gov:'القاهرة',     type:'حكومي',   specialty:'عام',           phone:'0223654321', lat:30.0341, lng:31.2275, emergency:true,  beds:2000, rating:3.8, hours:'24 ساعة' },
  { id:2,  name:'معهد القلب القومي',               nameEn:'National Heart Institute', gov:'الجيزة',      type:'حكومي',   specialty:'قلب',           phone:'0238441701', lat:30.0786, lng:31.2111, emergency:true,  beds:500,  rating:4.2, hours:'24 ساعة' },
  { id:3,  name:'مستشفى السلام الدولي',            nameEn:'Al Salam International',   gov:'القاهرة',     type:'خاص',     specialty:'عام',           phone:'0224152000', lat:30.0596, lng:31.3341, emergency:true,  beds:300,  rating:4.5, hours:'24 ساعة' },
  { id:4,  name:'مستشفى مصر الجديدة التخصصي',     nameEn:'Heliopolis Specialized',   gov:'القاهرة',     type:'خاص',     specialty:'عام',           phone:'0226903180', lat:30.0868, lng:31.3355, emergency:false, beds:150,  rating:4.1, hours:'24 ساعة' },
  { id:5,  name:'مستشفى ابن سينا التخصصي',        nameEn:'Ibn Sina Specialist',      gov:'الجيزة',      type:'خاص',     specialty:'عام',           phone:'0237600450', lat:29.9900, lng:31.1500, emergency:true,  beds:200,  rating:4.3, hours:'24 ساعة' },
  { id:6,  name:'معهد أبحاث السرطان',             nameEn:'Cancer Research Institute', gov:'القاهرة',     type:'حكومي',   specialty:'أورام',         phone:'0223636801', lat:30.0623, lng:31.2136, emergency:false, beds:450,  rating:4.0, hours:'8ص-8م' },
  { id:7,  name:'مستشفى العجوزة التعليمي',        nameEn:'El Agouza Teaching Hospital',gov:'الجيزة',    type:'حكومي',   specialty:'عام',           phone:'0237494333', lat:30.0570, lng:31.2120, emergency:true,  beds:600,  rating:3.6, hours:'24 ساعة' },
  { id:8,  name:'مستشفى الشيخ زايد التخصصي',     nameEn:'Sheikh Zayed Specialized',  gov:'الجيزة',     type:'حكومي',   specialty:'عام',           phone:'0238535027', lat:30.0171, lng:30.9944, emergency:true,  beds:700,  rating:4.0, hours:'24 ساعة' },
  { id:9,  name:'مستشفى دار الفؤاد',              nameEn:'Dar Al Fouad Hospital',     gov:'الجيزة',      type:'خاص',     specialty:'قلب',           phone:'0238350011', lat:29.9929, lng:31.0036, emergency:true,  beds:300,  rating:4.7, hours:'24 ساعة' },
  { id:10, name:'مستشفى أبو الريش للأطفال',       nameEn:'Abu El Reish Children',     gov:'القاهرة',     type:'حكومي',   specialty:'أطفال',         phone:'0223654218', lat:30.0330, lng:31.2260, emergency:true,  beds:400,  rating:3.9, hours:'24 ساعة' },
  { id:11, name:'مستشفى الإسكندرية الجامعي',      nameEn:'Alexandria University',     gov:'الإسكندرية',  type:'حكومي',   specialty:'عام',           phone:'0342860000', lat:31.2001, lng:29.9187, emergency:true,  beds:1500, rating:3.7, hours:'24 ساعة' },
  { id:12, name:'مستشفى بهية',                    nameEn:'Baheya Hospital',           gov:'الجيزة',      type:'خاص',     specialty:'أورام',         phone:'0238355935', lat:30.0215, lng:31.0140, emergency:false, beds:150,  rating:4.8, hours:'24 ساعة' },
  { id:13, name:'مستشفى وادي النيل',              nameEn:'Wadi El Nile Hospital',     gov:'القاهرة',     type:'خاص',     specialty:'عام',           phone:'0222908000', lat:30.0442, lng:31.2318, emergency:true,  beds:200,  rating:4.4, hours:'24 ساعة' },
  { id:14, name:'مستشفى المنصورة الجامعي',        nameEn:'Mansoura University',       gov:'الدقهلية',    type:'حكومي',   specialty:'عام',           phone:'0502233456', lat:31.0371, lng:31.3806, emergency:true,  beds:1200, rating:3.8, hours:'24 ساعة' },
  { id:15, name:'مستشفى الأطفال بالمنصورة',       nameEn:'Mansoura Children',         gov:'الدقهلية',    type:'حكومي',   specialty:'أطفال',         phone:'0502248888', lat:31.0400, lng:31.3870, emergency:true,  beds:350,  rating:4.0, hours:'24 ساعة' },
  { id:16, name:'مستشفى أسيوط الجامعي',           nameEn:'Assiut University Hospital',gov:'أسيوط',      type:'حكومي',   specialty:'عام',           phone:'0882313456', lat:27.1867, lng:31.1716, emergency:true,  beds:1000, rating:3.6, hours:'24 ساعة' },
  { id:17, name:'مستشفى الرمد القومي',            nameEn:'National Eye Institute',    gov:'القاهرة',     type:'حكومي',   specialty:'عيون',          phone:'0224831616', lat:30.0510, lng:31.2430, emergency:true,  beds:300,  rating:4.1, hours:'24 ساعة' },
  { id:18, name:'مستشفى الصدر (العباسية)',        nameEn:'Abbasia Chest Hospital',    gov:'القاهرة',     type:'حكومي',   specialty:'صدر وجهاز تنفسي',phone:'0224823399', lat:30.0600, lng:31.2900, emergency:true,  beds:500,  rating:3.5, hours:'24 ساعة' },
  { id:19, name:'مستشفى طنطا الجامعي',            nameEn:'Tanta University Hospital', gov:'الغربية',     type:'حكومي',   specialty:'عام',           phone:'0403422222', lat:30.7870, lng:31.0011, emergency:true,  beds:900,  rating:3.7, hours:'24 ساعة' },
  { id:20, name:'مستشفى الزقازيق الجامعي',        nameEn:'Zagazig University',        gov:'الشرقية',     type:'حكومي',   specialty:'عام',           phone:'0552335678', lat:30.5877, lng:31.5021, emergency:true,  beds:800,  rating:3.6, hours:'24 ساعة' },
]

const SPECIALTIES = ['عام','قلب','أورام','أطفال','عيون','صدر وجهاز تنفسي','عظام','نساء وتوليد','أمراض جلدية','مخ وأعصاب']
const GOVERNORATES = ['القاهرة','الجيزة','الإسكندرية','الدقهلية','الشرقية','الغربية','المنوفية','أسيوط','سوهاج','الأقصر','أسوان']

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
  const [userCoords, setUserCoords]     = useState(null)
  const [locStatus, setLocStatus]       = useState('')
  const [filterGov, setFilterGov]       = useState('')
  const [filterType, setFilterType]     = useState('')
  const [filterSpec, setFilterSpec]     = useState('')
  const [filterEmergency, setFilterEmergency] = useState(false)
  const [selected, setSelected]         = useState(null)
  const [search, setSearch]             = useState('')

  const getLocation = () => {
    if (!navigator.geolocation) { setLocStatus('المتصفح لا يدعم تحديد الموقع'); return }
    setLocStatus('جاري تحديد موقعك...')
    navigator.geolocation.getCurrentPosition(
      ({ coords: c }) => { setUserCoords({ lat: c.latitude, lng: c.longitude }); setLocStatus('') },
      () => setLocStatus('تعذّر تحديد الموقع — تأكد من الإذن')
    )
  }

  useEffect(() => { getLocation() }, [])

  const hospitals = HOSPITALS
    .filter(h => !filterGov  || h.gov === filterGov)
    .filter(h => !filterType || h.type === filterType)
    .filter(h => !filterSpec || h.specialty === filterSpec)
    .filter(h => !filterEmergency || h.emergency)
    .filter(h => !search || h.name.includes(search) || h.nameEn.toLowerCase().includes(search.toLowerCase()))
    .map(h => ({ ...h, distance: userCoords ? haversine(userCoords.lat, userCoords.lng, h.lat, h.lng) : null }))
    .sort((a, b) => (a.distance ?? 9999) - (b.distance ?? 9999))

  const typeColor = { حكومي:'bg-blue-100 text-blue-700', خاص:'bg-purple-100 text-purple-700', متخصص:'bg-emerald-100 text-emerald-700' }

  return (
    <div className="min-h-screen bg-gray-50 py-8" dir="rtl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-3">
            <div className="bg-blue-100 p-4 rounded-full"><Building2 className="h-10 w-10 text-blue-600"/></div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">المستشفيات القريبة</h1>
          <p className="text-gray-600">اعثر على أقرب مستشفى حسب تخصصه ونوعه</p>
        </div>

        {/* Location banner */}
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6 flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <Navigation className="h-5 w-5 text-blue-600 shrink-0"/>
            <p className="text-sm text-blue-800">
              {userCoords
                ? `تم تحديد موقعك — المستشفيات مرتبة بالأقرب إليك`
                : locStatus || 'يسمح بتحديد موقعك لترتيب المستشفيات بالأقرب إليك'}
            </p>
          </div>
          {!userCoords && (
            <button onClick={getLocation} className="text-sm font-medium bg-blue-600 text-white px-4 py-1.5 rounded-lg hover:bg-blue-700 shrink-0">
              تحديد موقعي
            </button>
          )}
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-6">
          <div className="flex flex-wrap gap-3 items-center">
            <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="ابحث بالاسم..."
              className="px-3 py-2 border border-gray-200 rounded-lg text-sm flex-1 min-w-[160px] focus:ring-blue-400 focus:outline-none" />
            <select value={filterGov} onChange={e=>setFilterGov(e.target.value)}
              className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-blue-400 focus:outline-none">
              <option value="">كل المحافظات</option>
              {GOVERNORATES.map(g=><option key={g} value={g}>{g}</option>)}
            </select>
            <select value={filterType} onChange={e=>setFilterType(e.target.value)}
              className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-blue-400 focus:outline-none">
              <option value="">حكومي وخاص</option>
              <option value="حكومي">حكومي</option>
              <option value="خاص">خاص</option>
            </select>
            <select value={filterSpec} onChange={e=>setFilterSpec(e.target.value)}
              className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-blue-400 focus:outline-none">
              <option value="">كل التخصصات</option>
              {SPECIALTIES.map(s=><option key={s} value={s}>{s}</option>)}
            </select>
            <label className="flex items-center gap-1.5 text-sm text-gray-700 cursor-pointer">
              <input type="checkbox" checked={filterEmergency} onChange={e=>setFilterEmergency(e.target.checked)}
                className="h-4 w-4 text-red-600 rounded border-gray-300" />
              طوارئ فقط
            </label>
            {(filterGov||filterType||filterSpec||filterEmergency||search) && (
              <button onClick={()=>{setFilterGov('');setFilterType('');setFilterSpec('');setFilterEmergency(false);setSearch('')}}
                className="text-xs text-gray-500 underline">إلغاء الكل</button>
            )}
          </div>
        </div>

        {/* Results count */}
        <p className="text-sm text-gray-500 mb-4">عرض {hospitals.length} مستشفى</p>

        {/* Grid */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {hospitals.map(h => (
            <div key={h.id} onClick={()=>setSelected(h)}
              className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex items-start justify-between gap-2 mb-3">
                <h3 className="font-semibold text-gray-900 text-sm leading-tight">{h.name}</h3>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium shrink-0 ${typeColor[h.type]||'bg-gray-100 text-gray-700'}`}>{h.type}</span>
              </div>
              <div className="space-y-1.5 text-xs text-gray-600">
                <div className="flex items-center gap-1.5"><Stethoscope className="h-3.5 w-3.5 text-blue-500"/><span>{h.specialty}</span></div>
                <div className="flex items-center gap-1.5"><MapPin className="h-3.5 w-3.5 text-gray-400"/><span>{h.gov}</span>{h.distance!==null&&<span className="text-blue-600 font-medium mr-1">· {h.distance} كم</span>}</div>
                <div className="flex items-center gap-1.5"><Clock className="h-3.5 w-3.5 text-gray-400"/><span>{h.hours}</span></div>
              </div>
              <div className="mt-3 flex items-center justify-between">
                <Stars n={h.rating}/>
                {h.emergency && <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full font-medium flex items-center gap-1"><Heart className="h-3 w-3"/>طوارئ</span>}
              </div>
            </div>
          ))}
        </div>

        {hospitals.length === 0 && (
          <div className="text-center py-16 text-gray-400">
            <Building2 className="h-12 w-12 mx-auto mb-3 opacity-40"/>
            <p>لا توجد مستشفيات تطابق الفلاتر المحددة</p>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selected && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={e=>e.target===e.currentTarget&&setSelected(null)}>
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="font-bold text-gray-900">{selected.name}</h2>
                <p className="text-xs text-gray-500 mt-0.5">{selected.nameEn}</p>
              </div>
              <button onClick={()=>setSelected(null)}><X className="h-5 w-5 text-gray-400"/></button>
            </div>
            <div className="space-y-2.5 text-sm text-gray-700 mb-5">
              <div className="flex items-center gap-2"><Building2 className="h-4 w-4 text-blue-500"/><span>{selected.type} · {selected.specialty}</span></div>
              <div className="flex items-center gap-2"><MapPin className="h-4 w-4 text-gray-400"/><span>{selected.gov}</span>{selected.distance!==null&&<span className="text-blue-600 font-medium">· {selected.distance} كم</span>}</div>
              <div className="flex items-center gap-2"><Phone className="h-4 w-4 text-gray-400"/><span dir="ltr">{selected.phone}</span></div>
              <div className="flex items-center gap-2"><Clock className="h-4 w-4 text-gray-400"/><span>{selected.hours}</span></div>
              {selected.beds && <div className="flex items-center gap-2"><Stethoscope className="h-4 w-4 text-gray-400"/><span>{selected.beds} سرير</span></div>}
              {selected.emergency && <div className="flex items-center gap-2"><Heart className="h-4 w-4 text-red-500"/><span className="text-red-600 font-medium">يوجد قسم طوارئ</span></div>}
            </div>
            <Stars n={selected.rating}/>
            <div className="mt-4 grid grid-cols-2 gap-3">
              <a href={`tel:${selected.phone}`} className="block">
                <button className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm py-2.5 rounded-xl font-medium flex items-center justify-center gap-1.5">
                  <Phone className="h-4 w-4"/> اتصل
                </button>
              </a>
              <a href={`https://www.google.com/maps?q=${selected.lat},${selected.lng}`} target="_blank" rel="noopener noreferrer" className="block">
                <button className="w-full border border-blue-600 text-blue-600 text-sm py-2.5 rounded-xl font-medium flex items-center justify-center gap-1.5 hover:bg-blue-50">
                  <Navigation className="h-4 w-4"/> الاتجاهات
                </button>
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
