import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Droplets, MapPin, Phone, Heart, Calendar, Plus,
  AlertCircle, CheckCircle, X, Upload, Navigation,
  Building2, Loader2
} from 'lucide-react'

/* ─── Constants ─── */
const BLOOD_TYPES = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

const GOVERNORATES = [
  'القاهرة','الجيزة','الإسكندرية','الدقهلية','الشرقية','البحيرة','القليوبية',
  'المنوفية','الغربية','كفر الشيخ','دمياط','بور سعيد','الإسماعيلية','السويس',
  'الفيوم','بني سويف','المنيا','أسيوط','سوهاج','قنا','الأقصر','أسوان',
  'البحر الأحمر','مطروح','سيناء الشمالية','سيناء الجنوبية','الوادي الجديد',
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
  if (urgency === 'critical') return 'text-red-600 bg-red-100'
  if (urgency === 'urgent')   return 'text-orange-600 bg-orange-100'
  return 'text-green-600 bg-green-100'
}
const URGENCY_LABEL = { critical: 'عاجل جداً', urgent: 'عاجل', routine: 'عادي' }

function getBloodTypeColor(bt) {
  const m = {'O+':'bg-red-100 text-red-800','O-':'bg-red-200 text-red-900','A+':'bg-blue-100 text-blue-800','A-':'bg-blue-200 text-blue-900','B+':'bg-green-100 text-green-800','B-':'bg-green-200 text-green-900','AB+':'bg-purple-100 text-purple-800','AB-':'bg-purple-200 text-purple-900'}
  return m[bt] || 'bg-gray-100 text-gray-800'
}

const API = (path, opts = {}) =>
  fetch(path, {
    headers: { 'Content-Type': 'application/json', ...opts.headers,
      ...(localStorage.getItem('token') ? { Authorization: `Bearer ${localStorage.getItem('token')}` } : {}) },
    ...opts,
  })

/* ──────────────────────────────────────────────── */
export default function BloodBankPage() {
  const [activeTab, setActiveTab] = useState(
    'banks'
  )

  /* stats */
  const [, setStats] = useState({ total_donors: 0, active_requests: 0, total_donations: 0, critical_requests: 0 })

  /* requests state */
  const [requests, setRequests]       = useState([])
  const [reqLoading, setReqLoading]   = useState(false)
  const [reqError, setReqError]       = useState('')
  const [showAddRequest, setShowAddRequest] = useState(false)
  const [filterBlood, setFilterBlood] = useState('')
  const [filterGov, setFilterGov]     = useState('')

  /* donation form */
  const [donationForm, setDonationForm] = useState({
    blood_type: '', weight: '', age: '', city: '',
    district: '', has_chronic_diseases: false, current_medications: '',
    available_for_emergency: true, notification_enabled: true,
  })
  const [donorLoading, setDonorLoading] = useState(false)
  const [donorMsg, setDonorMsg]         = useState(null) // {type:'success'|'error', text}
  const [donorProfile, setDonorProfile] = useState(null) // existing donor

  /* new request form */
  const [reqForm, setReqForm] = useState({
    patient_name: '', blood_type: '', units_needed: 1,
    hospital_name: '', city: '', urgency_level: 'urgent',
    contact_phone: '', description: '', needed_by_date: '',
  })
  const [reqFile, setReqFile]     = useState(null)
  const [reqSubmitting, setReqSubmitting] = useState(false)
  const [reqSubmitMsg, setReqSubmitMsg]   = useState(null)
  const fileRef = useRef()

  /* ── load stats on mount ── */
  useEffect(() => {
    API('/api/blood-bank/stats').then(r => r.ok ? r.json() : null).then(d => { if (d) setStats(d) }).catch(() => {})
  }, [])

  /* ── load requests when tab active ── */
  useEffect(() => {
    if (activeTab !== 'requests') return
    setReqLoading(true)
    setReqError('')
    const params = new URLSearchParams()
    if (filterBlood) params.append('blood_type', filterBlood)
    if (filterGov)   params.append('city', filterGov)
    API(`/api/blood-bank/requests?${params}`)
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(d => setRequests(d.requests || []))
      .catch(() => setReqError('تعذّر تحميل الطلبات'))
      .finally(() => setReqLoading(false))
  }, [activeTab, filterBlood, filterGov])

  /* ── load donor profile when donate tab active ── */
  useEffect(() => {
    if (activeTab !== 'donate' || !localStorage.getItem('token')) return
    API('/api/blood-bank/donors/me')
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.success && d.donor) setDonorProfile(d.donor) })
      .catch(() => {})
  }, [activeTab])

  /* ── add request ── */
  const handleAddRequest = async e => {
    e.preventDefault()
    if (!localStorage.getItem('token')) {
      setReqSubmitMsg({ type: 'error', text: 'يجب تسجيل الدخول أولاً لإنشاء طلب' })
      return
    }
    setReqSubmitting(true)
    setReqSubmitMsg(null)
    try {
      const res = await API('/api/blood-bank/requests', {
        method: 'POST',
        body: JSON.stringify({
          ...reqForm,
          needed_by_date: reqForm.needed_by_date + 'T00:00:00',
        }),
      })
      const data = await res.json()
      if (res.ok) {
        setReqSubmitMsg({ type: 'success', text: 'تم إنشاء الطلب بنجاح' })
        setRequests(prev => [data.request, ...prev])
        setShowAddRequest(false)
        setReqForm({ patient_name:'', blood_type:'', units_needed:1, hospital_name:'', city:'', urgency_level:'urgent', contact_phone:'', description:'', needed_by_date:'' })
        setReqFile(null)
      } else {
        setReqSubmitMsg({ type: 'error', text: data.error || data.message || 'حدث خطأ' })
      }
    } catch {
      setReqSubmitMsg({ type: 'error', text: 'حدث خطأ في الاتصال' })
    } finally {
      setReqSubmitting(false)
    }
  }

  /* ── donation submit ── */
  const handleDonationSubmit = async e => {
    e.preventDefault()
    if (!localStorage.getItem('token')) {
      setDonorMsg({ type: 'error', text: 'يجب تسجيل الدخول أولاً للتسجيل كمتبرع' })
      return
    }
    setDonorLoading(true)
    setDonorMsg(null)
    try {
      const endpoint = donorProfile ? '/api/blood-bank/donors/me' : '/api/blood-bank/donors/register'
      const method   = donorProfile ? 'PUT' : 'POST'
      const res = await API(endpoint, {
        method,
        body: JSON.stringify({
          ...donationForm,
          weight: Number(donationForm.weight),
          age:    Number(donationForm.age),
        }),
      })
      const data = await res.json()
      if (res.ok) {
        setDonorMsg({ type: 'success', text: donorProfile ? 'تم تحديث بياناتك بنجاح' : 'تم تسجيلك كمتبرع بنجاح! سيتم التواصل معك عند الحاجة.' })
        if (data.donor) setDonorProfile(data.donor)
      } else {
        setDonorMsg({ type: 'error', text: data.error || data.message || 'حدث خطأ' })
      }
    } catch {
      setDonorMsg({ type: 'error', text: 'حدث خطأ في الاتصال' })
    } finally {
      setDonorLoading(false)
    }
  }

  const tabs = [
    { key:'banks',    label:'بنوك الدم' },
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

                {reqSubmitMsg && (
                  <Alert className={reqSubmitMsg.type === 'success' ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
                    <AlertDescription className={reqSubmitMsg.type === 'success' ? 'text-green-700' : 'text-red-700'}>{reqSubmitMsg.text}</AlertDescription>
                  </Alert>
                )}

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
                            <Input required value={reqForm.patient_name} onChange={e=>setReqForm(f=>({...f,patient_name:e.target.value}))} placeholder="الاسم الكامل" />
                          </div>
                          <div>
                            <Label>فصيلة الدم *</Label>
                            <select required value={reqForm.blood_type} onChange={e=>setReqForm(f=>({...f,blood_type:e.target.value}))}
                              className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-red-500 focus:outline-none">
                              <option value="">اختر</option>
                              {BLOOD_TYPES.map(t=><option key={t} value={t}>{t}</option>)}
                            </select>
                          </div>
                          <div>
                            <Label>عدد الوحدات *</Label>
                            <Input required type="number" min="1" max="20" value={reqForm.units_needed} onChange={e=>setReqForm(f=>({...f,units_needed:+e.target.value}))} />
                          </div>
                          <div>
                            <Label>درجة الإلحاح *</Label>
                            <select required value={reqForm.urgency_level} onChange={e=>setReqForm(f=>({...f,urgency_level:e.target.value}))}
                              className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-red-500 focus:outline-none">
                              <option value="critical">عاجل جداً</option>
                              <option value="urgent">عاجل</option>
                              <option value="routine">عادي</option>
                            </select>
                          </div>
                          <div>
                            <Label>محتاج قبل *</Label>
                            <Input required type="date" value={reqForm.needed_by_date} onChange={e=>setReqForm(f=>({...f,needed_by_date:e.target.value}))} />
                          </div>
                          <div>
                            <Label>اسم المستشفى *</Label>
                            <Input required value={reqForm.hospital_name} onChange={e=>setReqForm(f=>({...f,hospital_name:e.target.value}))} placeholder="اسم المستشفى" />
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
                            <Input required type="tel" value={reqForm.contact_phone} onChange={e=>setReqForm(f=>({...f,contact_phone:e.target.value}))} placeholder="01xxxxxxxxx" />
                          </div>
                          <div className="col-span-2">
                            <Label>وصف الحالة</Label>
                            <textarea rows={2} value={reqForm.description} onChange={e=>setReqForm(f=>({...f,description:e.target.value}))}
                              className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md text-sm resize-none focus:ring-red-500 focus:outline-none" placeholder="اذكر تفاصيل الحالة" />
                          </div>
                        </div>
                        {/* File upload note */}
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
                          <Button type="submit" className="flex-1 bg-red-600 hover:bg-red-700" disabled={reqSubmitting}>
                            {reqSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : 'إرسال الطلب'}
                          </Button>
                          <Button type="button" variant="outline" onClick={()=>setShowAddRequest(false)} className="flex-1">إلغاء</Button>
                        </div>
                      </form>
                    </div>
                  </div>
                )}

                {/* States */}
                {reqLoading && (
                  <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-red-500" /></div>
                )}
                {!reqLoading && reqError && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertCircle className="h-4 w-4 text-red-600" />
                    <AlertDescription className="text-red-700">{reqError}</AlertDescription>
                  </Alert>
                )}
                {!reqLoading && !reqError && requests.length === 0 && (
                  <p className="text-center text-gray-500 py-8">لا توجد طلبات تطابق الفلتر المحدد</p>
                )}

                {/* Request cards */}
                {!reqLoading && !reqError && requests.length > 0 && (
                  <div className="space-y-4">
                    {requests.map(req => (
                      <div key={req.id} className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex flex-wrap items-center gap-2 mb-3">
                              <h3 className="font-semibold text-gray-900">{req.patient_name}</h3>
                              <span className={`px-2 py-0.5 text-xs font-bold rounded-full ${getBloodTypeColor(req.blood_type)}`}>{req.blood_type}</span>
                              <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getUrgencyColor(req.urgency_level)}`}>{URGENCY_LABEL[req.urgency_level] || req.urgency_level}</span>
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                              <div className="flex items-center gap-1"><Droplets className="h-3.5 w-3.5"/><span>{req.units_needed} وحدة</span></div>
                              <div className="flex items-center gap-1"><Building2 className="h-3.5 w-3.5"/><span>{req.hospital_name} · {req.city}</span></div>
                              <div className="flex items-center gap-1"><Phone className="h-3.5 w-3.5"/><span dir="ltr">{req.contact_phone}</span></div>
                              <div className="flex items-center gap-1"><Calendar className="h-3.5 w-3.5"/><span>{req.needed_by_date ? new Date(req.needed_by_date).toLocaleDateString('ar-EG') : '—'}</span></div>
                            </div>
                            {req.description && <p className="text-sm text-gray-700 mt-2">{req.description}</p>}
                          </div>
                          <div className="flex flex-col gap-2 shrink-0">
                            <a href={`tel:${req.contact_phone}`}>
                              <Button size="sm" className="bg-red-600 hover:bg-red-700 w-full">
                                <Heart className="h-3.5 w-3.5 ml-1"/> اتصل للمساعدة
                              </Button>
                            </a>
                            <Button size="sm" variant="outline" onClick={()=>navigator.share?.({title:'طلب دم',text:`${req.patient_name} — ${req.blood_type} — ${req.hospital_name}`,url:window.location.href})}>
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
              <BloodBanksTab />
            )}

            {/* ══════════ Donate Tab ══════════ */}
            {activeTab === 'donate' && (
              <div className="max-w-2xl mx-auto space-y-8">
                <div className="text-center">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">
                    {donorProfile ? 'تحديث بياناتك كمتبرع' : 'سجّل كمتبرع بالدم'}
                  </h3>
                  <p className="text-gray-600">انضم إلى شبكة المتبرعين وساعد في إنقاذ الأرواح</p>
                </div>

                {donorMsg && (
                  <Alert className={donorMsg.type === 'success' ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
                    <AlertDescription className={donorMsg.type === 'success' ? 'text-green-700' : 'text-red-700'}>{donorMsg.text}</AlertDescription>
                  </Alert>
                )}

                <form onSubmit={handleDonationSubmit} className="space-y-5">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>فصيلة الدم *</Label>
                      <select required value={donationForm.blood_type} onChange={e=>setDonationForm(f=>({...f,blood_type:e.target.value}))}
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
                    <div>
                      <Label>الوزن (كجم) *</Label>
                      <Input required type="number" min="50" value={donationForm.weight} onChange={e=>setDonationForm(f=>({...f,weight:e.target.value}))} placeholder="60" />
                    </div>
                    <div>
                      <Label>العمر *</Label>
                      <Input required type="number" min="18" max="65" value={donationForm.age} onChange={e=>setDonationForm(f=>({...f,age:e.target.value}))} placeholder="30" />
                    </div>
                    <div className="col-span-2">
                      <Label>المنطقة / الحي (اختياري)</Label>
                      <Input value={donationForm.district} onChange={e=>setDonationForm(f=>({...f,district:e.target.value}))} placeholder="المنطقة" />
                    </div>
                    <div className="col-span-2">
                      <Label>أدوية حالية (اختياري)</Label>
                      <textarea rows={2} value={donationForm.current_medications} onChange={e=>setDonationForm(f=>({...f,current_medications:e.target.value}))}
                        className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md text-sm resize-none focus:ring-red-500 focus:outline-none"
                        placeholder="اذكر أي أدوية تتناولها" />
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <input id="chronic" type="checkbox" checked={donationForm.has_chronic_diseases} onChange={e=>setDonationForm(f=>({...f,has_chronic_diseases:e.target.checked}))}
                      className="h-4 w-4 text-red-600 rounded border-gray-300" />
                    <label htmlFor="chronic" className="text-sm text-gray-700">لديّ أمراض مزمنة</label>
                  </div>
                  <div className="flex items-center gap-2">
                    <input id="avail" type="checkbox" checked={donationForm.available_for_emergency} onChange={e=>setDonationForm(f=>({...f,available_for_emergency:e.target.checked}))}
                      className="h-4 w-4 text-red-600 rounded border-gray-300" />
                    <label htmlFor="avail" className="text-sm text-gray-700">متاح للحالات الطارئة</label>
                  </div>
                  <Alert className="border-blue-200 bg-blue-50">
                    <AlertCircle className="h-4 w-4 text-blue-600" />
                    <AlertDescription className="text-blue-700 text-sm">سيتم التواصل معك عند وجود حالات تحتاج لفصيلة دمك.</AlertDescription>
                  </Alert>
                  <Button type="submit" className="w-full bg-red-600 hover:bg-red-700" disabled={donorLoading}>
                    {donorLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : donorProfile ? 'تحديث بياناتي' : 'سجّل كمتبرع'}
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

/* ══════════ Blood Banks Sub-Component ══════════ */
function BloodBanksTab() {
  const [banks, setBanks]         = useState([])
  const [loading, setLoading]     = useState(true)
  const [error, setError]         = useState('')
  const [bankBlood, setBankBlood] = useState('')
  const [bankGov, setBankGov]     = useState('')
  const [userCoords, setUserCoords] = useState(null)
  const [locStatus, setLocStatus]   = useState('')

  useEffect(() => {
    setLoading(true)
    setError('')
    const params = new URLSearchParams({ type: 'Blood Bank', per_page: '50' })
    fetch(`/api/facilities?${params}`)
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(d => setBanks(d.facilities || []))
      .catch(() => setError('تعذّر تحميل بنوك الدم'))
      .finally(() => setLoading(false))
  }, [bankBlood])

  const getLocation = () => {
    if (!navigator.geolocation) { setLocStatus('المتصفح لا يدعم تحديد الموقع'); return }
    setLocStatus('جاري تحديد موقعك...')
    navigator.geolocation.getCurrentPosition(
      ({ coords: c }) => { setUserCoords({ lat: c.latitude, lng: c.longitude }); setLocStatus('تم تحديد الموقع') },
      () => setLocStatus('تعذّر تحديد الموقع. تأكد من الإذن.')
    )
  }

  const filteredBanks = banks
    .filter(b => !bankGov || b.city === bankGov)
    .map(b => ({
      ...b,
      distance: userCoords && b.latitude ? haversine(userCoords.lat, userCoords.lng, b.latitude, b.longitude) : null
    }))
    .sort((a, b) => (a.distance ?? 9999) - (b.distance ?? 9999))

  return (
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

      {loading && <div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin text-red-500" /></div>}
      {!loading && error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-700">{error}</AlertDescription>
        </Alert>
      )}
      {!loading && !error && filteredBanks.length === 0 && (
        <p className="text-center text-gray-500 py-8">لا توجد مستشفيات مسجلة. يمكن للمدير إضافتها من لوحة التحكم.</p>
      )}
      {!loading && !error && filteredBanks.length > 0 && (
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
              <div className="mt-3 flex gap-2">
                <a href={`tel:${bank.phone}`} className="flex-1">
                  <Button size="sm" className="w-full bg-red-600 hover:bg-red-700 text-xs">
                    <Phone className="h-3 w-3 ml-1"/>{bank.phone}
                  </Button>
                </a>
                {bank.latitude && bank.longitude && (
                  <a href={`https://www.google.com/maps?q=${bank.latitude},${bank.longitude}`} target="_blank" rel="noopener noreferrer" className="shrink-0">
                    <Button size="sm" variant="outline" className="text-xs"><Navigation className="h-3 w-3"/></Button>
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
