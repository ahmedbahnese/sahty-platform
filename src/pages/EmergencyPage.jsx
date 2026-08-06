import { useState, useEffect, useCallback, useRef } from 'react'
import { useAuth } from '../contexts/AuthContext'
import {
  AlertTriangle, Ambulance, Phone, MapPin, Navigation, Heart,
  Zap, Shield, QrCode, Users, Plus, Trash2, CheckCircle,
  Clock, Activity, Bell, X, ChevronDown, ChevronUp
} from 'lucide-react'

const API = '/api'

// ── QR التقرير الطبي الشامل ──
function PublicMedicalQR() {
  const { token } = useAuth()
  const [publicUrl, setPublicUrl] = useState(null)
  const [loading, setLoading]     = useState(true)

  useEffect(() => {
    if (!token) return
    fetch('/api/medical-record/public-token', { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.ok ? r.json() : null)
      .then(d => {
        if (d?.token) setPublicUrl(`${window.location.origin}/public-record/${d.token}`)
      })
      .finally(() => setLoading(false))
  }, [token])

  if (loading || !publicUrl) return null

  return (
    <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-xl">
      <p className="text-sm font-semibold text-blue-800 mb-3 flex items-center gap-2">
        📋 QR التقرير الطبي الشامل
      </p>
      <div className="flex items-center gap-4">
        <img
          src={`https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=${encodeURIComponent(publicUrl)}`}
          alt="QR التقرير الطبي"
          className="w-28 h-28 rounded-lg border border-blue-100 bg-white"
        />
        <div className="flex-1 text-xs text-blue-700 space-y-1">
          <p>امسح هذا الرمز لفتح <strong>تقريرك الطبي الكامل</strong> (للقراءة فقط)</p>
          <p className="text-blue-500">يشمل: الأمراض، الأدوية، التحاليل، الأشعة، التطعيمات</p>
          <a href={publicUrl} target="_blank" rel="noopener noreferrer"
            className="inline-flex items-center gap-1 mt-2 underline text-blue-600 hover:text-blue-800">
            فتح الرابط مباشرة ↗
          </a>
        </div>
      </div>
    </div>
  )
}

/* ──────────────── helpers ──────────────── */
const SEVERITY_CFG = {
  critical: { label: 'حرج — يهدد الحياة',       color: 'text-red-700',    bg: 'bg-red-100'    },
  urgent:   { label: 'عاجل — تدخل سريع',         color: 'text-orange-700', bg: 'bg-orange-100' },
  moderate: { label: 'متوسط — رعاية طبية',        color: 'text-yellow-700', bg: 'bg-yellow-100' },
  minor:    { label: 'بسيط — غير عاجل',           color: 'text-green-700',  bg: 'bg-green-100'  },
}
const EMERGENCY_TYPES = [
  'نوبة قلبية','صعوبة في التنفس','نزيف شديد','فقدان الوعي',
  'حادث سير','كسور','حروق','تسمم','سكتة دماغية','ألم شديد','أخرى',
]
const RELATIONSHIPS = ['أب','أم','زوج/زوجة','ابن/ابنة','أخ/أخت','صديق','أخرى']

/* ──────────────── component ──────────────── */
export default function EmergencyPage() {
  const { token, user, isAuthenticated } = useAuth()
  const [tab, setTab]     = useState('sos')
  const [toast, setToast] = useState(null)
  const [busy, setBusy]   = useState(false)

  /* location */
  const [coords, setCoords]           = useState(null)
  const [locStatus, setLocStatus]     = useState('')
  const [locLoading, setLocLoading]   = useState(false)

  /* SOS */
  const [sosActive, setSosActive]     = useState(false)
  const [sosResult, setSosResult]     = useState(null)
  const [sosCountdown, setSosCountdown] = useState(0)
  const sosTimer = useRef(null)

  /* ambulance form */
  const [ambForm, setAmbForm] = useState({
    caller_name:'', caller_phone:'', location_text:'',
    emergency_type:'', severity:'urgent', description:'',
  })
  const [ambResult, setAmbResult]   = useState(null)

  /* QR */
  const [qrData, setQrData]         = useState(null)
  const [qrLoading, setQrLoading]   = useState(false)
  const [qrEditing, setQrEditing]   = useState(false)
  const [qrEditForm, setQrEditForm] = useState({ blood_type:'', phone:'', ec_name:'', ec_phone:'' })

  /* family */
  const [contacts, setContacts]     = useState([])
  const [contactForm, setContactForm] = useState({ name:'', phone:'', relationship:'أب', is_primary:false })
  const [showContactForm, setShowContactForm] = useState(false)

  /* alerts history */
  const [alerts, setAlerts]         = useState([])

  const hdr = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }

  const showToast = (msg, type='success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3500)
  }

  /* ── Geolocation ── */
  const getLocation = useCallback(() => {
    if (!navigator.geolocation) { setLocStatus('المتصفح لا يدعم تحديد الموقع'); return }
    setLocLoading(true)
    setLocStatus('جاري تحديد موقعك...')
    navigator.geolocation.getCurrentPosition(
      ({ coords: c }) => {
        setCoords({ lat: c.latitude, lng: c.longitude })
        setAmbForm(f => ({ ...f, location_text: `${c.latitude.toFixed(5)}, ${c.longitude.toFixed(5)}` }))
        setLocStatus(`تم تحديد الموقع: ${c.latitude.toFixed(4)}, ${c.longitude.toFixed(4)}`)
        setLocLoading(false)
      },
      () => { setLocStatus('تعذّر تحديد الموقع. تأكد من الإذن.'); setLocLoading(false) }
    )
  }, [])

  /* ── SOS countdown ── */
  const startSosCountdown = () => {
    if (sosCountdown > 0) { cancelSos(); return }
    setSosCountdown(5)
    sosTimer.current = setInterval(() => {
      setSosCountdown(prev => {
        if (prev <= 1) { clearInterval(sosTimer.current); sendSos(); return 0 }
        return prev - 1
      })
    }, 1000)
  }
  const cancelSos = () => {
    clearInterval(sosTimer.current)
    setSosCountdown(0)
  }
  const sendSos = async () => {
    setBusy(true)
    try {
      const body = {
        latitude:      coords?.lat,
        longitude:     coords?.lng,
        location_text: coords ? `${coords.lat.toFixed(5)}, ${coords.lng.toFixed(5)}` : '',
        emergency_type:'SOS',
        severity:      'critical',
        description:   'طلب استغاثة طارئة',
      }
      const res  = await fetch(`${API}/emergency/sos`, { method:'POST', headers: hdr, body: JSON.stringify(body) })
      const data = await res.json()
      if (res.ok) { setSosActive(true); setSosResult(data); loadAlerts() }
      else showToast(data.message || 'حدث خطأ', 'error')
    } finally { setBusy(false) }
  }

  /* ── Ambulance ── */
  const submitAmbulance = async e => {
    e.preventDefault()
    setBusy(true)
    try {
      const body = { ...ambForm, latitude: coords?.lat, longitude: coords?.lng }
      const res  = await fetch(`${API}/emergency/ambulance`, { method:'POST', headers: hdr, body: JSON.stringify(body) })
      const data = await res.json()
      if (res.ok) { setAmbResult(data); showToast('تم إرسال طلب الإسعاف'); loadAlerts() }
      else showToast(data.message || 'حدث خطأ', 'error')
    } finally { setBusy(false) }
  }

  /* ── QR ── */
  const loadQR = useCallback(async () => {
    if (!isAuthenticated) return
    setQrLoading(true)
    try {
      const res = await fetch(`${API}/emergency/qr`, { headers: hdr })
      if (res.ok) setQrData(await res.json())
    } finally { setQrLoading(false) }
  }, [token, isAuthenticated])

  /* ── Family contacts ── */
  const loadContacts = useCallback(async () => {
    if (!isAuthenticated) return
    const res = await fetch(`${API}/emergency/family-contacts`, { headers: hdr })
    if (res.ok) setContacts(await res.json())
  }, [token, isAuthenticated])

  const addContact = async e => {
    e.preventDefault()
    setBusy(true)
    try {
      const res  = await fetch(`${API}/emergency/family-contacts`, { method:'POST', headers: hdr, body: JSON.stringify(contactForm) })
      const data = await res.json()
      if (res.ok) { showToast('تم الإضافة'); setShowContactForm(false); setContactForm({ name:'', phone:'', relationship:'أب', is_primary:false }); loadContacts() }
      else showToast(data.message || 'حدث خطأ', 'error')
    } finally { setBusy(false) }
  }

  const deleteContact = async id => {
    if (!confirm('حذف جهة الاتصال؟')) return
    const res = await fetch(`${API}/emergency/family-contacts/${id}`, { method:'DELETE', headers: hdr })
    if (res.ok) { showToast('تم الحذف'); loadContacts() }
  }

  const notifyFamily = async alertId => {
    setBusy(true)
    try {
      const res  = await fetch(`${API}/emergency/notify-family/${alertId}`, { method:'POST', headers: hdr })
      const data = await res.json()
      if (res.ok) { showToast(data.message); loadAlerts() }
      else showToast(data.message || 'حدث خطأ', 'error')
    } finally { setBusy(false) }
  }

  /* ── Alerts ── */
  const loadAlerts = useCallback(async () => {
    if (!isAuthenticated) return
    const res = await fetch(`${API}/emergency/alerts`, { headers: hdr })
    if (res.ok) setAlerts(await res.json())
  }, [token, isAuthenticated])

  const resolveAlert = async id => {
    const res = await fetch(`${API}/emergency/alerts/${id}/resolve`, { method:'PUT', headers: hdr })
    if (res.ok) { showToast('تم إغلاق التنبيه'); loadAlerts() }
  }

  useEffect(() => { loadContacts(); loadAlerts() }, [loadContacts, loadAlerts])
  useEffect(() => { if (tab === 'qr') loadQR() }, [tab, loadQR])
  useEffect(() => () => clearInterval(sosTimer.current), [])

  /* ──────────────── render helpers ──────────────── */
  const TabBtn = ({ id, label, icon: Icon, badge }) => (
    <button onClick={() => setTab(id)}
      className={`flex-1 flex flex-col items-center gap-1 py-3 text-xs font-medium rounded-xl transition-all
        ${tab === id ? 'bg-red-600 text-white shadow-md shadow-red-200' : 'text-gray-500 hover:bg-gray-100'}`}>
      <Icon size={18} />
      {label}
      {badge > 0 && <span className="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] rounded-full w-4 h-4 flex items-center justify-center">{badge}</span>}
    </button>
  )

  /* ──────────────── main render ──────────────── */
  return (
    <div dir="rtl" className="min-h-screen bg-red-50/30">
      {/* Toast */}
      {toast && (
        <div className={`fixed top-4 left-1/2 -translate-x-1/2 z-50 px-6 py-3 rounded-xl shadow-lg text-white text-sm font-medium
          ${toast.type==='error' ? 'bg-red-500' : 'bg-green-500'}`}>{toast.msg}</div>
      )}

      {/* ── Hero رأس الصفحة ── */}
      <div className="bg-gradient-to-br from-red-600 via-red-700 to-red-800 text-white pt-10 pb-6 px-4">
        <div className="max-w-2xl mx-auto text-center">
          <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-3">
            <AlertTriangle size={30} />
          </div>
          <h1 className="text-2xl font-bold mb-1">خدمات الطوارئ الطبية</h1>
          <p className="text-red-100 text-sm">متاح 24/7 للحالات الطارئة</p>

          {/* أرقام سريعة */}
          <div className="flex justify-center gap-3 mt-5">
            {[
              { num:'123', label:'إسعاف', Icon: Ambulance },
              { num:'122', label:'شرطة', Icon: Shield },
              { num:'180', label:'إطفاء', Icon: Zap },
            ].map(({ num, label, Icon }) => (
              <a key={num} href={`tel:${num}`}
                className="flex flex-col items-center bg-white/15 hover:bg-white/25 border border-white/25 rounded-xl px-4 py-2.5 transition-colors">
                <Icon size={18} className="mb-0.5" />
                <span className="text-lg font-bold leading-none">{num}</span>
                <span className="text-[10px] opacity-80">{label}</span>
              </a>
            ))}
          </div>
        </div>
      </div>

      {/* ── تبويبات ── */}
      <div className="max-w-2xl mx-auto px-4">
        <div className="flex gap-2 bg-white rounded-2xl p-1.5 shadow-sm border border-gray-100 -mt-4 mb-5 relative">
          <TabBtn id="sos"      label="SOS"      icon={AlertTriangle} />
          <TabBtn id="ambulance"label="إسعاف"    icon={Ambulance}    />
          <TabBtn id="qr"       label="QR طوارئ" icon={QrCode}       />
          <TabBtn id="family"   label="العائلة"  icon={Users}        />
          <TabBtn id="history"  label="السجل"    icon={Clock}  badge={alerts.filter(a=>a.status==='active').length} />
        </div>

        {/* ════════════ SOS ════════════ */}
        {tab === 'sos' && (
          <div className="space-y-4 pb-10">
            {!isAuthenticated && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 text-sm text-yellow-800 text-center">
                سجّل دخولك لتفعيل SOS وإشعار العائلة
              </div>
            )}

            {/* SOS Button */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 text-center">
              {!sosActive ? (
                <>
                  <p className="text-gray-500 text-sm mb-5">اضغط مطوّلاً لتفعيل نداء الاستغاثة</p>
                  <button
                    onClick={startSosCountdown}
                    disabled={busy || !isAuthenticated}
                    className={`relative w-40 h-40 rounded-full mx-auto flex flex-col items-center justify-center font-black text-white text-2xl shadow-2xl transition-all select-none
                      ${sosCountdown > 0
                        ? 'bg-orange-500 scale-95 animate-pulse'
                        : 'bg-red-600 hover:bg-red-700 active:scale-95 hover:shadow-red-300'
                      } disabled:opacity-50`}>
                    {sosCountdown > 0 ? (
                      <>
                        <span className="text-5xl font-black">{sosCountdown}</span>
                        <span className="text-xs font-normal mt-1 opacity-80">اضغط للإلغاء</span>
                      </>
                    ) : (
                      <>
                        <AlertTriangle size={36} />
                        <span className="text-lg mt-1">SOS</span>
                      </>
                    )}
                  </button>
                  {sosCountdown > 0 && (
                    <p className="text-orange-600 text-sm mt-4 font-medium animate-pulse">
                      سيُرسل النداء خلال {sosCountdown} ثوانٍ...
                    </p>
                  )}
                </>
              ) : (
                <div className="space-y-3">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                    <CheckCircle size={32} className="text-green-600" />
                  </div>
                  <p className="text-green-700 font-bold text-lg">تم إرسال SOS!</p>
                  {sosResult && (
                    <div className="bg-gray-50 rounded-xl p-3 text-sm text-right space-y-1">
                      <p className="text-gray-600">رقم التنبيه: <span className="font-bold">#{sosResult.alert?.id}</span></p>
                      <p className="text-gray-600">جهات أسرية مُشعَرة: <span className="font-bold">{sosResult.notified} / {sosResult.contacts_count}</span></p>
                    </div>
                  )}
                  <button onClick={() => { setSosActive(false); setSosResult(null) }}
                    className="text-sm text-red-600 hover:underline">إلغاء التنبيه</button>
                </div>
              )}
            </div>

            {/* تحديد الموقع */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
              <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2"><MapPin size={16} className="text-red-500" /> تحديد الموقع</h3>
              <button onClick={getLocation} disabled={locLoading}
                className="w-full flex items-center justify-center gap-2 border border-red-200 bg-red-50 hover:bg-red-100 text-red-700 rounded-xl py-2.5 text-sm font-medium transition-colors disabled:opacity-60">
                <Navigation size={15} />
                {locLoading ? 'جاري التحديد...' : coords ? 'تحديث الموقع' : 'تحديد موقعي الآن'}
              </button>
              {locStatus && <p className="text-xs text-gray-500 mt-2 text-center">{locStatus}</p>}
              {coords && (
                <div className="mt-3 flex items-center justify-between bg-green-50 rounded-lg px-3 py-2">
                  <span className="text-xs text-green-700 font-mono">{coords.lat.toFixed(5)}, {coords.lng.toFixed(5)}</span>
                  <a href={`https://maps.google.com/?q=${coords.lat},${coords.lng}`} target="_blank" rel="noopener noreferrer"
                    className="text-xs text-blue-600 hover:underline flex items-center gap-1">
                    <Navigation size={11} /> خرائط
                  </a>
                </div>
              )}
            </div>

            {/* إسعافات أولية */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
              <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2"><Heart size={16} className="text-red-500" /> إسعافات أولية سريعة</h3>
              <div className="grid grid-cols-1 gap-2.5">
                {[
                  { title:'نزيف شديد', color:'bg-red-50 border-red-100', tc:'text-red-800',
                    steps:['اضغط مباشرة على الجرح','ارفع العضو المصاب','لا تزيل الضمادة المشبعة','اطلب مساعدة فوراً'] },
                  { title:'توقف التنفس', color:'bg-blue-50 border-blue-100', tc:'text-blue-800',
                    steps:['تحقق من الاستجابة','افتح مجرى الهواء','ابدأ الإنعاش (30 ضغطة + 2 نفخة)','استمر حتى وصول الإسعاف'] },
                  { title:'فقدان الوعي', color:'bg-purple-50 border-purple-100', tc:'text-purple-800',
                    steps:['تحقق من التنفس','ضع في وضع الإفاقة الجانبي','لا تترك المريض وحده','اتصل بالإسعاف فوراً'] },
                ].map(item => (
                  <div key={item.title} className={`${item.color} border rounded-xl p-3`}>
                    <p className={`font-semibold text-sm ${item.tc} mb-1.5`}>{item.title}</p>
                    <ul className="space-y-0.5">
                      {item.steps.map((s,i) => (
                        <li key={i} className={`text-xs ${item.tc} opacity-80 flex items-start gap-1.5`}>
                          <span className="font-bold mt-px">{i+1}.</span>{s}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ════════════ إسعاف ════════════ */}
        {tab === 'ambulance' && (
          <div className="pb-10">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
              <h2 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                <Ambulance size={18} className="text-red-500" /> طلب إسعاف
              </h2>

              {ambResult ? (
                <div className="text-center space-y-4 py-4">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                    <CheckCircle size={30} className="text-green-600" />
                  </div>
                  <p className="text-green-700 font-bold">تم إرسال طلب الإسعاف!</p>
                  <div className="bg-gray-50 rounded-xl p-3 text-sm text-right space-y-1">
                    <p>رقم المرجع: <span className="font-mono font-bold text-red-600">{ambResult.ref_number}</span></p>
                    <p className="text-gray-500 text-xs">احتفظ بهذا الرقم للمتابعة</p>
                  </div>
                  <button onClick={() => setAmbResult(null)} className="text-sm text-blue-600 hover:underline">طلب جديد</button>
                </div>
              ) : (
                <form onSubmit={submitAmbulance} className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">الاسم *</label>
                      <input required className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
                        value={ambForm.caller_name} onChange={e => setAmbForm(f=>({...f,caller_name:e.target.value}))} placeholder="اسمك الكامل" />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">الهاتف *</label>
                      <input required type="tel" className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
                        value={ambForm.caller_phone} onChange={e => setAmbForm(f=>({...f,caller_phone:e.target.value}))} placeholder="01xxxxxxxxx" />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">الموقع *</label>
                    <div className="flex gap-2">
                      <input required className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
                        value={ambForm.location_text} onChange={e => setAmbForm(f=>({...f,location_text:e.target.value}))} placeholder="العنوان التفصيلي" />
                      <button type="button" onClick={getLocation} disabled={locLoading}
                        className="border border-red-200 bg-red-50 text-red-600 rounded-lg px-3 py-2 text-xs hover:bg-red-100 disabled:opacity-60">
                        {locLoading ? '...' : <><Navigation size={14}/></>}
                      </button>
                    </div>
                    {coords && <p className="text-xs text-green-600 mt-1">✓ تم تحديد الإحداثيات</p>}
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">نوع الطارئ *</label>
                      <select required className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
                        value={ambForm.emergency_type} onChange={e => setAmbForm(f=>({...f,emergency_type:e.target.value}))}>
                        <option value="">اختر...</option>
                        {EMERGENCY_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">الخطورة *</label>
                      <select required className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
                        value={ambForm.severity} onChange={e => setAmbForm(f=>({...f,severity:e.target.value}))}>
                        {Object.entries(SEVERITY_CFG).map(([v,c]) => <option key={v} value={v}>{c.label}</option>)}
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">وصف الحالة</label>
                    <textarea rows={2} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
                      value={ambForm.description} onChange={e => setAmbForm(f=>({...f,description:e.target.value}))} placeholder="وصف مختصر للحالة..." />
                  </div>

                  <button type="submit" disabled={busy}
                    className="w-full bg-red-600 hover:bg-red-700 text-white rounded-xl py-3 font-bold text-sm flex items-center justify-center gap-2 disabled:opacity-60">
                    <Ambulance size={16} />
                    {busy ? 'جاري الإرسال...' : 'إرسال طلب الإسعاف'}
                  </button>
                </form>
              )}
            </div>

            {/* مستشفيات قريبة */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 mt-4">
              <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2"><MapPin size={16} className="text-blue-500" /> مستشفيات قريبة</h3>
              {!coords ? (
                <div className="text-center py-4">
                  <p className="text-gray-500 text-sm mb-3">حدّد موقعك لعرض المستشفيات القريبة</p>
                  <button onClick={getLocation} disabled={locLoading}
                    className="flex items-center gap-2 mx-auto bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm">
                    <Navigation size={14}/> {locLoading ? 'جاري...' : 'تحديد موقعي'}
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  {[
                    { name:'مستشفى القاهرة الجديدة', addr:'التجمع الأول', dist:'2.5 كم', time:'8 د', phone:'0227584000', specs:['طوارئ','قلب','جراحة'] },
                    { name:'مستشفى دار الفؤاد',       addr:'مدينة نصر',   dist:'4.2 كم', time:'12 د', phone:'0225555555', specs:['طوارئ','أعصاب','عظام'] },
                    { name:'مستشفى الشروق',           addr:'مدينة الشروق',dist:'6.8 كم', time:'18 د', phone:'0244444444', specs:['طوارئ','أطفال'] },
                  ].map((h,i) => (
                    <div key={i} className="border border-gray-100 rounded-xl p-3">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-semibold text-sm text-gray-800">{h.name}</p>
                          <p className="text-xs text-gray-500 mt-0.5">{h.addr}</p>
                        </div>
                        <div className="text-left">
                          <p className="text-blue-600 text-sm font-medium">{h.dist}</p>
                          <p className="text-gray-400 text-xs">{h.time}</p>
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-1 my-2">
                        {h.specs.map(s => <span key={s} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{s}</span>)}
                      </div>
                      <div className="flex gap-2">
                        <a href={`tel:${h.phone}`} className="flex-1 flex items-center justify-center gap-1 bg-red-600 hover:bg-red-700 text-white rounded-lg py-1.5 text-xs">
                          <Phone size={12}/> اتصال
                        </a>
                        <a href={`https://www.google.com/maps/search/${encodeURIComponent(h.name)}`} target="_blank" rel="noopener noreferrer"
                          className="flex-1 flex items-center justify-center gap-1 border border-gray-200 hover:bg-gray-50 text-gray-600 rounded-lg py-1.5 text-xs">
                          <Navigation size={12}/> الاتجاهات
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* ════════════ QR ════════════ */}
        {tab === 'qr' && (
          <div className="pb-10">
            {/* print styles injected inline */}
            <style>{`
              @media print {
                body > *:not(#emergency-print-card) { display: none !important; }
                #emergency-print-card { display: block !important; page-break-inside: avoid; }
                nav, footer, button { display: none !important; }
              }
            `}</style>

            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
              <div className="flex items-center justify-between mb-1">
                <h2 className="font-bold text-gray-800 flex items-center gap-2"><QrCode size={18} className="text-red-500" /> بطاقة الطوارئ الذكية</h2>
                {qrData && !qrEditing && (
                  <div className="flex gap-2">
                    <button onClick={() => { setQrEditForm({ blood_type: qrData.card.blood_type||'', phone: qrData.card.phone||'', ec_name: qrData.card.ec_name||'', ec_phone: qrData.card.ec_phone||'' }); setQrEditing(true) }}
                      className="text-xs bg-blue-50 text-blue-600 border border-blue-200 px-3 py-1.5 rounded-lg hover:bg-blue-100 font-medium">
                      تعديل
                    </button>
                    <button onClick={() => window.print()}
                      className="text-xs bg-gray-50 text-gray-700 border border-gray-200 px-3 py-1.5 rounded-lg hover:bg-gray-100 font-medium flex items-center gap-1">
                      🖨 طباعة PDF
                    </button>
                  </div>
                )}
              </div>
              <p className="text-xs text-gray-500 mb-4">يحتوي QR على بياناتك الطارئة — يمكن لأي هاتف قراءته فوراً</p>

              {!isAuthenticated ? (
                <p className="text-center text-gray-500 text-sm py-8">سجّل دخولك لعرض بطاقتك</p>
              ) : qrLoading ? (
                <div className="flex justify-center py-10"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-red-600"/></div>
              ) : qrData ? (
                <div className="space-y-4">
                  {/* Edit form */}
                  {qrEditing && (
                    <form className="bg-blue-50 rounded-xl p-4 space-y-3 border border-blue-200"
                      onSubmit={async e => {
                        e.preventDefault()
                        setBusy(true)
                        try {
                          const res = await fetch(`${API}/auth/profile`, {
                            method: 'PUT',
                            headers: hdr,
                            body: JSON.stringify({
                              blood_type: qrEditForm.blood_type,
                              phone: qrEditForm.phone,
                              emergency_contact_name: qrEditForm.ec_name,
                              emergency_contact_phone: qrEditForm.ec_phone,
                            })
                          })
                          if (res.ok) { showToast('تم تحديث البطاقة'); setQrEditing(false); loadQR() }
                          else { const d = await res.json(); showToast(d.message || 'حدث خطأ', 'error') }
                        } finally { setBusy(false) }
                      }}>
                      <h3 className="text-sm font-semibold text-blue-800 mb-2">تعديل بيانات الطوارئ</h3>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="block text-xs text-gray-600 mb-1">فصيلة الدم</label>
                          <select value={qrEditForm.blood_type} onChange={e => setQrEditForm(f => ({...f, blood_type: e.target.value}))}
                            className="w-full border border-gray-200 bg-white rounded-lg px-3 py-2 text-sm focus:ring-red-400 focus:outline-none">
                            <option value="">—</option>
                            {['A+','A-','B+','B-','AB+','AB-','O+','O-'].map(t => <option key={t} value={t}>{t}</option>)}
                          </select>
                        </div>
                        <div>
                          <label className="block text-xs text-gray-600 mb-1">رقم الهاتف</label>
                          <input value={qrEditForm.phone} onChange={e => setQrEditForm(f => ({...f, phone: e.target.value}))}
                            className="w-full border border-gray-200 bg-white rounded-lg px-3 py-2 text-sm focus:ring-red-400 focus:outline-none"
                            placeholder="01xxxxxxxxx" dir="ltr" />
                        </div>
                        <div>
                          <label className="block text-xs text-gray-600 mb-1">اسم جهة الاتصال الطارئة</label>
                          <input value={qrEditForm.ec_name} onChange={e => setQrEditForm(f => ({...f, ec_name: e.target.value}))}
                            className="w-full border border-gray-200 bg-white rounded-lg px-3 py-2 text-sm focus:ring-red-400 focus:outline-none"
                            placeholder="الاسم" />
                        </div>
                        <div>
                          <label className="block text-xs text-gray-600 mb-1">هاتف الاتصال الطارئ</label>
                          <input value={qrEditForm.ec_phone} onChange={e => setQrEditForm(f => ({...f, ec_phone: e.target.value}))}
                            className="w-full border border-gray-200 bg-white rounded-lg px-3 py-2 text-sm focus:ring-red-400 focus:outline-none"
                            placeholder="01xxxxxxxxx" dir="ltr" />
                        </div>
                      </div>
                      <p className="text-xs text-blue-600">لتعديل الحساسية والأدوية، اذهب إلى الملف الطبي.</p>
                      <div className="flex gap-2 pt-1">
                        <button type="submit" disabled={busy}
                          className="flex-1 bg-red-600 text-white text-sm py-2 rounded-lg hover:bg-red-700 font-medium">
                          {busy ? 'جاري الحفظ...' : 'حفظ التغييرات'}
                        </button>
                        <button type="button" onClick={() => setQrEditing(false)}
                          className="flex-1 border border-gray-200 text-gray-700 text-sm py-2 rounded-lg hover:bg-gray-50">
                          إلغاء
                        </button>
                      </div>
                    </form>
                  )}

                  {/* Printable card */}
                  <div id="emergency-print-card">
                    {/* QR Image */}
                    <div className="flex flex-col items-center bg-gray-50 rounded-2xl p-5">
                      <img src={`data:image/png;base64,${qrData.qr_base64}`} alt="QR طوارئ"
                        className="w-48 h-48 rounded-xl shadow-sm" />
                      <p className="text-xs text-gray-400 mt-2">امسح بأي هاتف في حالة الطوارئ</p>
                    </div>

                    {/* بيانات البطاقة */}
                    <div className="border border-red-100 rounded-xl overflow-hidden mt-4">
                      <div className="bg-red-600 text-white px-4 py-2.5 flex items-center gap-2">
                        <Heart size={14}/>
                        <span className="font-semibold text-sm">بيانات الطوارئ — صحتك في أمان</span>
                      </div>
                      <div className="p-3 space-y-2 text-sm">
                        {[
                          ['الاسم',           qrData.card.name],
                          ['فصيلة الدم',      qrData.card.blood_type],
                          ['تاريخ الميلاد',   qrData.card.dob],
                          ['الهاتف',          qrData.card.phone],
                          ['الحساسية',        qrData.card.allergies?.join(', ') || 'لا يوجد'],
                          ['الأدوية الحالية', qrData.card.medications?.join(', ') || 'لا يوجد'],
                          ['اتصال الطوارئ',   `${qrData.card.ec_name || '—'} — ${qrData.card.ec_phone || '—'}`],
                        ].map(([label, val]) => (
                          <div key={label} className="flex justify-between items-start border-b border-gray-50 pb-1.5 last:border-0 last:pb-0">
                            <span className="text-gray-500 text-xs">{label}</span>
                            <span className="font-medium text-gray-800 text-xs text-left max-w-[55%]">{val}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* QR التقرير الطبي الشامل */}
                  <PublicMedicalQR />

                  <div className="flex gap-2">
                    <button onClick={loadQR} className="flex-1 text-sm text-blue-600 border border-blue-200 rounded-lg py-2 hover:bg-blue-50">تحديث البيانات</button>
                    <button onClick={() => window.print()} className="flex-1 text-sm text-gray-700 border border-gray-200 rounded-lg py-2 hover:bg-gray-50">🖨 طباعة / PDF</button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500 text-sm mb-3">لا يوجد ملف مريض مرتبط</p>
                  <p className="text-xs text-gray-400">أكمل ملفك الطبي أولاً لتوليد بطاقة الطوارئ</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ════════════ العائلة ════════════ */}
        {tab === 'family' && (
          <div className="pb-10 space-y-4">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-bold text-gray-800 flex items-center gap-2"><Users size={18} className="text-red-500"/> جهات الاتصال الأسرية</h2>
                {!showContactForm && contacts.length < 5 && (
                  <button onClick={() => setShowContactForm(true)}
                    className="flex items-center gap-1 bg-red-600 hover:bg-red-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium">
                    <Plus size={13}/> إضافة
                  </button>
                )}
              </div>

              {/* نموذج الإضافة */}
              {showContactForm && (
                <form onSubmit={addContact} className="bg-red-50 rounded-xl p-4 mb-4 space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">الاسم *</label>
                      <input required className="w-full border border-gray-200 bg-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
                        value={contactForm.name} onChange={e => setContactForm(f=>({...f,name:e.target.value}))} placeholder="الاسم الكامل" />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">الهاتف *</label>
                      <input required type="tel" className="w-full border border-gray-200 bg-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
                        value={contactForm.phone} onChange={e => setContactForm(f=>({...f,phone:e.target.value}))} placeholder="01xxxxxxxxx" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">صلة القرابة</label>
                      <select className="w-full border border-gray-200 bg-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
                        value={contactForm.relationship} onChange={e => setContactForm(f=>({...f,relationship:e.target.value}))}>
                        {RELATIONSHIPS.map(r => <option key={r} value={r}>{r}</option>)}
                      </select>
                    </div>
                    <div className="flex items-end pb-1">
                      <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                        <input type="checkbox" className="accent-red-600" checked={contactForm.is_primary}
                          onChange={e => setContactForm(f=>({...f,is_primary:e.target.checked}))} />
                        جهة أساسية
                      </label>
                    </div>
                  </div>
                  <div className="flex gap-2 justify-end">
                    <button type="button" onClick={() => setShowContactForm(false)} className="text-sm text-gray-500 px-3 py-1.5">إلغاء</button>
                    <button type="submit" disabled={busy} className="bg-red-600 hover:bg-red-700 text-white px-4 py-1.5 rounded-lg text-sm disabled:opacity-60">
                      {busy ? '...' : 'حفظ'}
                    </button>
                  </div>
                </form>
              )}

              {/* القائمة */}
              {contacts.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  <Users size={32} className="mx-auto mb-2 opacity-40"/>
                  <p className="text-sm">لا توجد جهات مضافة</p>
                  <p className="text-xs mt-1">أضف أفراد عائلتك لإشعارهم عند حالات الطوارئ</p>
                </div>
              ) : (
                <div className="space-y-2.5">
                  {contacts.map(c => (
                    <div key={c.id} className="flex items-center justify-between bg-gray-50 rounded-xl px-3 py-2.5">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 bg-red-100 text-red-600 rounded-full flex items-center justify-center font-bold text-sm">
                          {c.name[0]}
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-gray-800 flex items-center gap-1.5">
                            {c.name}
                            {c.is_primary && <span className="text-[10px] bg-red-100 text-red-600 px-1.5 py-0.5 rounded-full">أساسي</span>}
                          </p>
                          <p className="text-xs text-gray-500">{c.phone} · {c.relationship}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <a href={`tel:${c.phone}`} className="p-1.5 text-green-600 hover:bg-green-50 rounded-lg">
                          <Phone size={14}/>
                        </a>
                        <button onClick={() => deleteContact(c.id)} className="p-1.5 text-red-400 hover:bg-red-50 rounded-lg">
                          <Trash2 size={14}/>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {contacts.length > 0 && (
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-800">
                <p className="font-semibold mb-1 flex items-center gap-1.5"><Bell size={14}/> ملاحظة</p>
                <p className="text-xs">يُرسل الإشعار التلقائي عند SOS للجهات المسجلة في التطبيق بنفس رقم الهاتف المدخل.</p>
              </div>
            )}
          </div>
        )}

        {/* ════════════ السجل ════════════ */}
        {tab === 'history' && (
          <div className="pb-10">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
              <h2 className="font-bold text-gray-800 mb-4 flex items-center gap-2"><Clock size={18} className="text-red-500"/> سجل تنبيهات الطوارئ</h2>

              {alerts.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  <Activity size={32} className="mx-auto mb-2 opacity-40"/>
                  <p className="text-sm">لا توجد تنبيهات مسجلة</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {alerts.map(a => {
                    const sev = SEVERITY_CFG[a.severity] || SEVERITY_CFG.urgent
                    const typeLabel = { sos:'SOS', ambulance_request:'طلب إسعاف', family_notify:'إشعار عائلة' }[a.alert_type] || a.alert_type
                    return (
                      <div key={a.id} className={`rounded-xl border p-3 ${a.status==='active' ? 'border-red-200 bg-red-50' : 'border-gray-100 bg-gray-50'}`}>
                        <div className="flex items-start justify-between">
                          <div>
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${sev.bg} ${sev.color}`}>{sev.label}</span>
                              <span className="text-xs bg-gray-200 text-gray-700 px-2 py-0.5 rounded-full">{typeLabel}</span>
                              {a.status === 'active' && <span className="text-xs bg-red-200 text-red-700 px-2 py-0.5 rounded-full animate-pulse">نشط</span>}
                              {a.status === 'resolved' && <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">مُغلق</span>}
                            </div>
                            <p className="text-sm font-semibold text-gray-800 mt-1">{a.emergency_type}</p>
                            {a.location_text && <p className="text-xs text-gray-500 flex items-center gap-1 mt-0.5"><MapPin size={10}/>{a.location_text}</p>}
                            <p className="text-xs text-gray-400 mt-1">{new Date(a.created_at).toLocaleString('ar-SA')}</p>
                          </div>
                          <div className="flex flex-col gap-1.5">
                            {a.status === 'active' && (
                              <>
                                <button onClick={() => notifyFamily(a.id)} disabled={busy}
                                  className="flex items-center gap-1 text-xs bg-blue-600 hover:bg-blue-700 text-white px-2.5 py-1.5 rounded-lg disabled:opacity-60">
                                  <Bell size={11}/> إشعار
                                </button>
                                <button onClick={() => resolveAlert(a.id)}
                                  className="flex items-center gap-1 text-xs border border-gray-200 hover:bg-gray-100 text-gray-600 px-2.5 py-1.5 rounded-lg">
                                  <CheckCircle size={11}/> إغلاق
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                        {a.family_notified && (
                          <p className="text-xs text-green-600 mt-2 flex items-center gap-1">
                            <CheckCircle size={11}/> تم إشعار العائلة
                          </p>
                        )}
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
