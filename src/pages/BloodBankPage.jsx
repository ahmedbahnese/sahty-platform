import { useState, useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Droplets, MapPin, Phone, Heart, Calendar, Plus,
  AlertCircle, CheckCircle, X, Upload, Filter, Navigation,
  Building2, Clock
} from 'lucide-react'

/* ─── Constants ─── */
const BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

const GOVERNORATES = [
  'القاهرة','الجيزة','الإسكندرية','الدقهلية','الشرقية','البحيرة','القليوبية',
  'المنوفية','الغربية','كفر الشيخ','دمياط','بور سعيد','الإسماعيلية','السويس',
  'الفيوم','بني سويف','المنيا','أسيوط','سوهاج','قنا','الأقصر','أسوان',
  'البحر الأحمر','مطروح','سيناء الشمالية','سيناء الجنوبية','الوادي الجديد',
]

/* Egyptian blood banks data */
const BLOOD_BANKS_DATA = [
  { id:1,  name:'بنك دم قصر العيني',          gov:'القاهرة',      address:'شارع القصر العيني، مدينة القاهرة',     phone:'0223654321', lat:30.0341, lng:31.2275, types:['A+','A-','B+','O+','O-','AB+'] },
  { id:2,  name:'بنك دم معهد القلب القومي',    gov:'الجيزة',       address:'إمبابة، الجيزة',                       phone:'0238441701', lat:30.0786, lng:31.2111, types:['A+','B+','B-','AB-','O+','O-'] },
  { id:3,  name:'بنك دم مستشفى العباسية',      gov:'القاهرة',      address:'العباسية، القاهرة',                     phone:'0224822021', lat:30.0627, lng:31.2855, types:['A+','A-','B+','O+','AB+','AB-'] },
  { id:4,  name:'بنك دم مستشفى شبين الكوم',    gov:'المنوفية',     address:'شبين الكوم، المنوفية',                  phone:'0482234567', lat:30.5631, lng:31.0115, types:['A+','B+','O+','O-'] },
  { id:5,  name:'بنك دم الإسكندرية المركزي',   gov:'الإسكندرية',   address:'رأس التين، الإسكندرية',                 phone:'0342934561', lat:31.2001, lng:29.8868, types:['A+','A-','B+','B-','O+','O-','AB+','AB-'] },
  { id:6,  name:'بنك دم معهد أورام الإسكندرية',gov:'الإسكندرية',   address:'المعمورة، الإسكندرية',                  phone:'0343421001', lat:31.2781, lng:30.0543, types:['A+','A-','O+','O-','AB-'] },
  { id:7,  name:'بنك دم مستشفى المنصورة',      gov:'الدقهلية',     address:'شارع الجيش، المنصورة',                  phone:'0502233456', lat:31.0371, lng:31.3806, types:['A+','B+','B-','O+','O-'] },
  { id:8,  name:'بنك دم مستشفى بني سويف',      gov:'بني سويف',     address:'بني سويف الجديدة',                     phone:'0822315678', lat:29.0744, lng:31.0996, types:['A+','O+','O-','AB+'] },
  { id:9,  name:'بنك دم مستشفى أسيوط الجامعي', gov:'أسيوط',        address:'جامعة أسيوط، أسيوط',                   phone:'0882313456', lat:27.1867, lng:31.1716, types:['A+','A-','B+','O+','O-','AB+','AB-'] },
  { id:10, name:'بنك دم مستشفى الأقصر',        gov:'الأقصر',       address:'الأقصر الجديدة',                       phone:'0952380123', lat:25.6872, lng:32.6396, types:['A+','B+','O+','O-'] },
  { id:11, name:'بنك دم مستشفى أسوان',         gov:'أسوان',        address:'كورنيش النيل، أسوان',                   phone:'0972301234', lat:24.0889, lng:32.8998, types:['A+','O+','O-','AB+'] },
  { id:12, name:'بنك دم مستشفى طنطا',          gov:'الغربية',      address:'طنطا، الغربية',                        phone:'0403422222', lat:30.7870, lng:31.0011, types:['A+','A-','B+','O+','O-'] },
  { id:13, name:'بنك دم مستشفى الزقازيق',      gov:'الشرقية',      address:'الزقازيق، الشرقية',                    phone:'0552335678', lat:30.5877, lng:31.5021, types:['A+','B+','B-','O+','O-','AB+'] },
  { id:14, name:'بنك دم بور سعيد',             gov:'بور سعيد',     address:'حي الشرق، بور سعيد',                   phone:'0662224455', lat:31.2565, lng:32.2841, types:['A+','O+','O-','AB+','AB-'] },
  { id:15, name:'بنك دم مستشفى إسماعيلية',     gov:'الإسماعيلية',  address:'الإسماعيلية',                          phone:'0642332211', lat:30.5965, lng:32.2715, types:['A+','B+','O+','O-'] },
]

/* ─── Helpers ─── */
function haversine(lat1, lng1, lat2, lng2) {
  const R = 6371
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const a = Math.sin(dLat/2)**2 + Math.cos(lat1*Math.PI/180)*Math.cos(lat2*Math.PI/180)*Math.sin(dLng/2)**2
  return +(R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))).toFixed(1)
}

function getUrgencyColor(urgency) {
  if (urgency === 'عاجل جداً') return 'text-red-600 bg-red-100'
  if (urgency === 'عاجل')     return 'text-orange-600 bg-orange-100'
  if (urgency === 'متوسط')    return 'text-yellow-600 bg-yellow-100'
  return 'text-green-600 bg-green-100'
}
function getBloodTypeColor(bt) {
  const m = {'O+':'bg-red-100 text-red-800','O-':'bg-red-200 text-red-900','A+':'bg-blue-100 text-blue-800','A-':'bg-blue-200 text-blue-900','B+':'bg-green-100 text-green-800','B-':'bg-green-200 text-green-900','AB+':'bg-purple-100 text-purple-800','AB-':'bg-purple-200 text-purple-900'}
  return m[bt] || 'bg-gray-100 text-gray-800'
}

const MOCK_REQUESTS = [
  { id:1, patientName:'أحمد محمد علي',    bloodType:'O+',  unitsNeeded:3, hospital:'مستشفى القاهرة الجديدة',       city:'القاهرة',     urgency:'عاجل',      contactPhone:'01234567890', requestDate:'2024-01-15', description:'حالة طوارئ — حادث سير', status:'نشط' },
  { id:2, patientName:'فاطمة أحمد حسن',   bloodType:'A+',  unitsNeeded:2, hospital:'مستشفى الإسكندرية الدولي',    city:'الإسكندرية',  urgency:'متوسط',     contactPhone:'01234567891', requestDate:'2024-01-14', description:'عملية جراحية مجدولة',  status:'نشط' },
  { id:3, patientName:'محمد حسام الدين',  bloodType:'B-',  unitsNeeded:1, hospital:'مستشفى الجيزة التخصصي',       city:'الجيزة',      urgency:'عاجل جداً', contactPhone:'01234567892', requestDate:'2024-01-15', description:'حالة طوارئ — نزيف داخلي', status:'نشط' },
]

/* ──────────────────────────────────────────────── */
export default function BloodBankPage() {
  const [searchParams] = useSearchParams()
  const [activeTab, setActiveTab] = useState(
    searchParams.get('tab') === 'donate' ? 'donate' : searchParams.get('tab') === 'banks' ? 'banks' : 'requests'
  )

  /* requests state */
  const [requests, setRequests]       = useState(MOCK_REQUESTS)
  const [showAddRequest, setShowAddRequest] = useState(false)
  const [filterBlood, setFilterBlood] = useState('')
  const [filterGov, setFilterGov]     = useState('')

  /* blood banks state */
  const [bankBlood, setBankBlood]     = useState('')
  const [bankGov, setBankGov]         = useState('')
  const [userCoords, setUserCoords]   = useState(null)
  const [locStatus, setLocStatus]     = useState('')

  /* donation form */
  const [donationForm, setDonationForm] = useState({ name:'', phone:'', bloodType:'', city:'', lastDonation:'', medicalConditions:'', available:true })
  const [loading, setLoading]           = useState(false)

  /* new request form */
  const [reqForm, setReqForm] = useState({ patientName:'', bloodType:'', unitsNeeded:1, hospital:'', city:'', urgency:'عاجل', contactPhone:'', description:'', neededBy:'' })
  const [reqFile, setReqFile] = useState(null)
  const fileRef = useRef()

  /* ── geolocation ── */
  const getLocation = () => {
    if (!navigator.geolocation) { setLocStatus('المتصفح لا يدعم تحديد الموقع'); return }
    setLocStatus('جاري تحديد موقعك...')
    navigator.geolocation.getCurrentPosition(
      ({ coords: c }) => { setUserCoords({ lat: c.latitude, lng: c.longitude }); setLocStatus('تم تحديد الموقع') },
      () => setLocStatus('تعذّر تحديد الموقع. تأكد من الإذن.')
    )
  }

  /* ── derived: filtered banks ── */
  const filteredBanks = BLOOD_BANKS_DATA
    .filter(b => !bankGov  || b.gov === bankGov)
    .filter(b => !bankBlood || b.types.includes(bankBlood))
    .map(b => ({ ...b, distance: userCoords ? haversine(userCoords.lat, userCoords.lng, b.lat, b.lng) : null }))
    .sort((a, b) => (a.distance ?? 9999) - (b.distance ?? 9999))

  /* ── derived: filtered requests ── */
  const filteredRequests = requests
    .filter(r => !filterBlood || r.bloodType === filterBlood)
    .filter(r => !filterGov   || r.city === filterGov)

  /* ── add request ── */
  const handleAddRequest = e => {
    e.preventDefault()
    const newReq = { ...reqForm, id: Date.now(), requestDate: new Date().toISOString().slice(0,10), status:'نشط', attachedFile: reqFile?.name }
    setRequests(prev => [newReq, ...prev])
    setShowAddRequest(false)
    setReqForm({ patientName:'', bloodType:'', unitsNeeded:1, hospital:'', city:'', urgency:'عاجل', contactPhone:'', description:'', neededBy:'' })
    setReqFile(null)
  }

  /* ── donation submit ── */
  const handleDonationSubmit = async e => {
    e.preventDefault()
    setLoading(true)
    setTimeout(() => {
      setLoading(false)
      alert('تم تسجيلك كمتبرع بنجاح! سيتم التواصل معك عند الحاجة.')
      setDonationForm({ name:'', phone:'', bloodType:'', city:'', lastDonation:'', medicalConditions:'', available:true })
    }, 1500)
  }

  const tabs = [
    { key:'requests', label:'طلبات الدم' },
    { key:'banks',    label:'بنوك الدم' },
    { key:'donate',   label:'سجّل متبرعاً' },
  ]

  return (
    <div className="min-h-screen bg-gray-50 py-8" dir="rtl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* Header */}
        <div className="text-center mb-10">
          <div className="flex justify-center mb-4">
            <div className="bg-red-100 p-4 rounded-full"><Droplets className="h-12 w-12 text-red-600" /></div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-3">بنك الدم الرقمي</h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">طلبات الدم · بنوك الدم بمواقعها وأرقامها · تسجيل المتبرعين</p>
        </div>

        {/* Quick stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[['1,250','متبرع نشط','text-red-600'],['89','طلب نشط','text-blue-600'],['3,420','عملية تبرع','text-green-600'],['24/7','خدمة متواصلة','text-purple-600']].map(([v,l,c])=>(
            <div key={l} className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 text-center">
              <div className={`text-3xl font-bold mb-1 ${c}`}>{v}</div>
              <div className="text-gray-600 text-sm">{l}</div>
            </div>
          ))}
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 mb-8">
          <div className="border-b border-gray-200">
            <nav className="flex gap-2 px-4">
              {tabs.map(t => (
                <button key={t.key} onClick={()=>setActiveTab(t.key)}
                  className={`py-4 px-4 border-b-2 font-medium text-sm transition-colors ${activeTab===t.key ? 'border-red-500 text-red-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}>
                  {t.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">

            {/* ══════════ Requests Tab ══════════ */}
            {activeTab === 'requests' && (
              <div className="space-y-5">
                {/* Filters + Add */}
                <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
                  <div className="flex gap-2 flex-wrap">
                    <select value={filterBlood} onChange={e=>setFilterBlood(e.target.value)}
                      className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-red-400 focus:outline-none">
                      <option value="">كل فصائل الدم</option>
                      {BLOOD_TYPES.map(t=><option key={t} value={t}>{t}</option>)}
                    </select>
                    <select value={filterGov} onChange={e=>setFilterGov(e.target.value)}
                      className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-red-400 focus:outline-none">
                      <option value="">كل المحافظات</option>
                      {GOVERNORATES.map(g=><option key={g} value={g}>{g}</option>)}
                    </select>
                    {(filterBlood||filterGov) && <button onClick={()=>{setFilterBlood('');setFilterGov('')}} className="text-sm text-gray-500 underline">إلغاء الفلتر</button>}
                  </div>
                  <Button onClick={()=>setShowAddRequest(true)} className="bg-red-600 hover:bg-red-700 shrink-0">
                    <Plus className="h-4 w-4 ml-1" /> إضافة طلب جديد
                  </Button>
                </div>

                {/* Add Request Modal */}
                {showAddRequest && (
                  <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={e=>e.target===e.currentTarget&&setShowAddRequest(false)}>
                    <div className="bg-white rounded-2xl shadow-xl w-full max-w-xl max-h-[90vh] overflow-y-auto p-6">
                      <div className="flex justify-between items-center mb-5">
                        <h3 className="text-lg font-bold text-gray-900">طلب نقل دم جديد</h3>
                        <button onClick={()=>setShowAddRequest(false)}><X className="h-5 w-5 text-gray-400" /></button>
                      </div>
                      <form onSubmit={handleAddRequest} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div className="col-span-2">
                            <Label>اسم المريض *</Label>
                            <Input required value={reqForm.patientName} onChange={e=>setReqForm(f=>({...f,patientName:e.target.value}))} placeholder="الاسم الكامل" />
                          </div>
                          <div>
                            <Label>فصيلة الدم *</Label>
                            <select required value={reqForm.bloodType} onChange={e=>setReqForm(f=>({...f,bloodType:e.target.value}))}
                              className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-red-500 focus:outline-none">
                              <option value="">اختر</option>
                              {BLOOD_TYPES.map(t=><option key={t} value={t}>{t}</option>)}
                            </select>
                          </div>
                          <div>
                            <Label>عدد الوحدات *</Label>
                            <Input required type="number" min="1" max="20" value={reqForm.unitsNeeded} onChange={e=>setReqForm(f=>({...f,unitsNeeded:+e.target.value}))} />
                          </div>
                          <div>
                            <Label>درجة الإلحاح *</Label>
                            <select required value={reqForm.urgency} onChange={e=>setReqForm(f=>({...f,urgency:e.target.value}))}
                              className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-red-500 focus:outline-none">
                              <option value="عاجل جداً">عاجل جداً</option>
                              <option value="عاجل">عاجل</option>
                              <option value="متوسط">متوسط</option>
                              <option value="عادي">عادي</option>
                            </select>
                          </div>
                          <div>
                            <Label>محتاج قبل *</Label>
                            <Input required type="date" value={reqForm.neededBy} onChange={e=>setReqForm(f=>({...f,neededBy:e.target.value}))} />
                          </div>
                          <div>
                            <Label>اسم المستشفى *</Label>
                            <Input required value={reqForm.hospital} onChange={e=>setReqForm(f=>({...f,hospital:e.target.value}))} placeholder="اسم المستشفى" />
                          </div>
                          <div>
                            <Label>المحافظة *</Label>
                            <select required value={reqForm.city} onChange={e=>setReqForm(f=>({...f,city:e.target.value}))}
                              className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-red-500 focus:outline-none">
                              <option value="">اختر</option>
                              {GOVERNORATES.map(g=><option key={g} value={g}>{g}</option>)}
                            </select>
                          </div>
                          <div className="col-span-2">
                            <Label>رقم التواصل *</Label>
                            <Input required type="tel" value={reqForm.contactPhone} onChange={e=>setReqForm(f=>({...f,contactPhone:e.target.value}))} placeholder="01xxxxxxxxx" />
                          </div>
                          <div className="col-span-2">
                            <Label>وصف الحالة</Label>
                            <textarea rows={2} value={reqForm.description} onChange={e=>setReqForm(f=>({...f,description:e.target.value}))}
                              className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md text-sm resize-none focus:ring-red-500 focus:outline-none" placeholder="اذكر تفاصيل الحالة" />
                          </div>
                        </div>
                        {/* File upload */}
                        <div>
                          <Label>رفع طلب نقل الدم (صورة أو PDF)</Label>
                          <div className="mt-1 border-2 border-dashed border-gray-300 rounded-lg p-4 text-center cursor-pointer hover:border-red-400 transition-colors"
                            onClick={()=>fileRef.current?.click()}>
                            <input ref={fileRef} type="file" accept="image/*,application/pdf" className="hidden"
                              onChange={e=>setReqFile(e.target.files?.[0]||null)} />
                            {reqFile ? (
                              <div className="flex items-center justify-center gap-2 text-green-600">
                                <CheckCircle className="h-5 w-5" /><span className="text-sm font-medium">{reqFile.name}</span>
                              </div>
                            ) : (
                              <div className="text-gray-500">
                                <Upload className="h-6 w-6 mx-auto mb-1 text-gray-400" />
                                <p className="text-sm">اضغط لرفع صورة أو ملف طلب نقل الدم</p>
                                <p className="text-xs text-gray-400 mt-1">PNG · JPG · PDF (حتى 10MB)</p>
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="flex gap-3 pt-2">
                          <Button type="submit" className="flex-1 bg-red-600 hover:bg-red-700">إرسال الطلب</Button>
                          <Button type="button" variant="outline" onClick={()=>setShowAddRequest(false)} className="flex-1">إلغاء</Button>
                        </div>
                      </form>
                    </div>
                  </div>
                )}

                {/* Request cards */}
                {filteredRequests.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">لا توجد طلبات تطابق الفلتر المحدد</p>
                ) : (
                  <div className="space-y-4">
                    {filteredRequests.map(req => (
                      <div key={req.id} className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex flex-wrap items-center gap-2 mb-3">
                              <h3 className="font-semibold text-gray-900">{req.patientName}</h3>
                              <span className={`px-2 py-0.5 text-xs font-bold rounded-full ${getBloodTypeColor(req.bloodType)}`}>{req.bloodType}</span>
                              <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getUrgencyColor(req.urgency)}`}>{req.urgency}</span>
                              {req.attachedFile && <span className="px-2 py-0.5 text-xs bg-green-50 text-green-700 rounded-full flex items-center gap-1"><CheckCircle className="h-3 w-3"/>مرفق</span>}
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                              <div className="flex items-center gap-1"><Droplets className="h-3.5 w-3.5"/><span>{req.unitsNeeded} وحدة</span></div>
                              <div className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5"/><span>{req.hospital} · {req.city}</span></div>
                              <div className="flex items-center gap-1"><Phone className="h-3.5 w-3.5"/><span dir="ltr">{req.contactPhone}</span></div>
                              <div className="flex items-center gap-1"><Calendar className="h-3.5 w-3.5"/><span>{req.requestDate}</span></div>
                            </div>
                            {req.description && <p className="text-sm text-gray-700 mt-2">{req.description}</p>}
                          </div>
                          <div className="flex flex-col gap-2 shrink-0">
                            <a href={`tel:${req.contactPhone}`}>
                              <Button size="sm" className="bg-red-600 hover:bg-red-700 w-full">
                                <Heart className="h-3.5 w-3.5 ml-1"/> اتصل للمساعدة
                              </Button>
                            </a>
                            <Button size="sm" variant="outline" onClick={()=>navigator.share?.({title:'طلب دم',text:`${req.patientName} — ${req.bloodType} — ${req.hospital}`,url:window.location.href})}>
                              مشاركة
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* ══════════ Blood Banks Tab ══════════ */}
            {activeTab === 'banks' && (
              <div className="space-y-5">
                <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
                  <div className="flex gap-2 flex-wrap">
                    <select value={bankBlood} onChange={e=>setBankBlood(e.target.value)}
                      className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-red-400 focus:outline-none">
                      <option value="">كل الفصائل</option>
                      {BLOOD_TYPES.map(t=><option key={t} value={t}>{t}</option>)}
                    </select>
                    <select value={bankGov} onChange={e=>setBankGov(e.target.value)}
                      className="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-red-400 focus:outline-none">
                      <option value="">كل المحافظات</option>
                      {GOVERNORATES.map(g=><option key={g} value={g}>{g}</option>)}
                    </select>
                    {(bankBlood||bankGov) && <button onClick={()=>{setBankBlood('');setBankGov('')}} className="text-sm text-gray-500 underline">إلغاء</button>}
                  </div>
                  <Button variant="outline" onClick={getLocation} className="shrink-0">
                    <Navigation className="h-4 w-4 ml-1"/> {userCoords ? 'تحديث موقعي' : 'تحديد موقعي (ترتيب بالقرب)'}
                  </Button>
                </div>
                {locStatus && <p className="text-xs text-blue-600">{locStatus}</p>}

                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {filteredBanks.map(bank => (
                    <div key={bank.id} className="bg-white border border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start gap-3">
                        <div className="bg-red-100 p-2 rounded-lg shrink-0"><Building2 className="h-5 w-5 text-red-600"/></div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-gray-900 text-sm leading-tight">{bank.name}</h3>
                          <p className="text-xs text-gray-500 mt-0.5 flex items-center gap-1"><MapPin className="h-3 w-3"/>{bank.address}</p>
                          {bank.distance !== null && <p className="text-xs text-blue-600 mt-0.5 font-medium">{bank.distance} كم منك</p>}
                        </div>
                      </div>
                      <div className="mt-3 flex flex-wrap gap-1">
                        {bank.types.map(t=>(
                          <span key={t} className={`text-xs px-1.5 py-0.5 rounded font-medium ${getBloodTypeColor(t)}`}>{t}</span>
                        ))}
                      </div>
                      <div className="mt-3 flex gap-2">
                        <a href={`tel:${bank.phone}`} className="flex-1">
                          <Button size="sm" className="w-full bg-red-600 hover:bg-red-700 text-xs">
                            <Phone className="h-3 w-3 ml-1"/>{bank.phone}
                          </Button>
                        </a>
                        <a href={`https://www.google.com/maps?q=${bank.lat},${bank.lng}`} target="_blank" rel="noopener noreferrer" className="shrink-0">
                          <Button size="sm" variant="outline" className="text-xs"><Navigation className="h-3 w-3"/></Button>
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ══════════ Donate Tab ══════════ */}
            {activeTab === 'donate' && (
              <div className="max-w-2xl mx-auto space-y-8">
                <div className="text-center">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">سجّل كمتبرع بالدم</h3>
                  <p className="text-gray-600">انضم إلى شبكة المتبرعين وساعد في إنقاذ الأرواح</p>
                </div>
                <form onSubmit={handleDonationSubmit} className="space-y-5">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="col-span-2 sm:col-span-1">
                      <Label>الاسم الكامل *</Label>
                      <Input required value={donationForm.name} onChange={e=>setDonationForm(f=>({...f,name:e.target.value}))} placeholder="أدخل اسمك" />
                    </div>
                    <div className="col-span-2 sm:col-span-1">
                      <Label>رقم الهاتف *</Label>
                      <Input required type="tel" value={donationForm.phone} onChange={e=>setDonationForm(f=>({...f,phone:e.target.value}))} placeholder="01xxxxxxxxx" />
                    </div>
                    <div>
                      <Label>فصيلة الدم *</Label>
                      <select required value={donationForm.bloodType} onChange={e=>setDonationForm(f=>({...f,bloodType:e.target.value}))}
                        className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-red-500 focus:outline-none">
                        <option value="">اختر</option>
                        {BLOOD_TYPES.map(t=><option key={t} value={t}>{t}</option>)}
                      </select>
                    </div>
                    <div>
                      <Label>المحافظة *</Label>
                      <select required value={donationForm.city} onChange={e=>setDonationForm(f=>({...f,city:e.target.value}))}
                        className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-red-500 focus:outline-none">
                        <option value="">اختر</option>
                        {GOVERNORATES.map(g=><option key={g} value={g}>{g}</option>)}
                      </select>
                    </div>
                    <div className="col-span-2">
                      <Label>تاريخ آخر تبرع</Label>
                      <Input type="date" value={donationForm.lastDonation} onChange={e=>setDonationForm(f=>({...f,lastDonation:e.target.value}))} />
                    </div>
                    <div className="col-span-2">
                      <Label>حالات طبية (اختياري)</Label>
                      <textarea rows={3} value={donationForm.medicalConditions} onChange={e=>setDonationForm(f=>({...f,medicalConditions:e.target.value}))}
                        className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md text-sm resize-none focus:ring-red-500 focus:outline-none"
                        placeholder="اذكر أي حالات طبية أو أدوية" />
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <input id="avail" type="checkbox" checked={donationForm.available} onChange={e=>setDonationForm(f=>({...f,available:e.target.checked}))}
                      className="h-4 w-4 text-red-600 rounded border-gray-300" />
                    <label htmlFor="avail" className="text-sm text-gray-700">متاح للتبرع حالياً</label>
                  </div>
                  <Alert className="border-blue-200 bg-blue-50">
                    <AlertCircle className="h-4 w-4 text-blue-600" />
                    <AlertDescription className="text-blue-700 text-sm">سيتم التواصل معك عند وجود حالات تحتاج لفصيلة دمك.</AlertDescription>
                  </Alert>
                  <Button type="submit" className="w-full bg-red-600 hover:bg-red-700" disabled={loading}>
                    {loading ? 'جاري التسجيل...' : 'سجّل كمتبرع'}
                  </Button>
                </form>
              </div>
            )}
          </div>
        </div>

        {/* Info box */}
        <div className="bg-gradient-to-l from-red-50 to-pink-50 border border-red-200 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-red-800 mb-4">معلومات مهمة عن التبرع بالدم</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-red-700">
            <div>
              <h4 className="font-medium mb-2">شروط التبرع:</h4>
              <ul className="space-y-1">
                <li>• العمر من 18 إلى 65 سنة</li><li>• الوزن أكثر من 50 كيلو</li>
                <li>• عدم التبرع خلال آخر 3 أشهر</li><li>• عدم وجود أمراض معدية</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">فوائد التبرع:</h4>
              <ul className="space-y-1">
                <li>• تجديد خلايا الدم</li><li>• تحسين الدورة الدموية</li>
                <li>• فحص طبي مجاني</li><li>• إنقاذ حياة الآخرين</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
