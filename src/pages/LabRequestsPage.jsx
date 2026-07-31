import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'
import {
  FlaskConical, Plus, CheckCircle, XCircle, Upload, Bell,
  ChevronDown, ChevronUp, AlertTriangle, Clock, FileText,
  Building2, Home, Calendar, Paperclip, Info,
} from 'lucide-react'

const API = '/api'

const STATUS_CONFIG = {
  requested:        { label: 'بانتظار الاعتماد', color: 'bg-yellow-100 text-yellow-800', icon: Clock },
  approved:         { label: 'معتمد',             color: 'bg-blue-100 text-blue-800',    icon: CheckCircle },
  results_uploaded: { label: 'نتائج مرفوعة',     color: 'bg-purple-100 text-purple-800', icon: Upload },
  completed:        { label: 'مكتمل',             color: 'bg-green-100 text-green-800',  icon: CheckCircle },
  rejected:         { label: 'مرفوض',             color: 'bg-red-100 text-red-800',      icon: XCircle },
}

const RESULT_STATUS = {
  normal:   { label: 'طبيعي',    color: 'text-green-600' },
  abnormal: { label: 'غير طبيعي', color: 'text-orange-600' },
  critical: { label: 'حرج',      color: 'text-red-600' },
}

const CATEGORIES = ['blood', 'urine', 'culture', 'hormones', 'biochemistry', 'immunology', 'genetics', 'other']
const CATEGORY_LABELS = {
  blood: 'دم', urine: 'بول', culture: 'مزرعة', hormones: 'هرمونات',
  biochemistry: 'كيمياء حيوية', immunology: 'مناعة', genetics: 'جينات', other: 'أخرى',
}

const LAB_CENTERS = [
  'مختبر ابن سينا',
  'مختبر الأندلس الطبي',
  'مختبر المملكة',
  'مختبر بيوميد',
  'مختبر الحياة الطبي',
  'مختبر الأمل',
  'أخرى',
]

// تعليمات التحضير لعرضها في الواجهة
const PREP_BY_CATEGORY = {
  blood:        ['صيام 8 ساعات قبل التحليل', 'شرب الماء مسموح'],
  hormones:     ['صيام 8 ساعات', 'جمع العينة صباحاً (8-9 ص)'],
  biochemistry: ['صيام 12 ساعة كاملة', 'الامتناع عن الدهون 24 ساعة'],
  urine:        ['جمع عينة البول الأولى صباحاً', 'تنظيف المنطقة قبل الجمع'],
  culture:      ['جمع العينة قبل أخذ المضادات الحيوية'],
  immunology:   ['صيام 8 ساعات', 'أبلغ المختبر بالأدوية الحالية'],
  genetics:     ['لا يتطلب صياماً'],
  other:        ['اتبع تعليمات طبيبك'],
}

export default function LabRequestsPage() {
  const { token, user } = useAuth()
  const [requests, setRequests]   = useState([])
  const [loading, setLoading]     = useState(true)
  const [tab, setTab]             = useState('all')
  const [expanded, setExpanded]   = useState(null)
  const [showForm, setShowForm]   = useState(false)
  const [actionModal, setActionModal] = useState(null)
  const [busy, setBusy]           = useState(false)
  const [toast, setToast]         = useState(null)

  const isAdmin   = ['admin','super_admin','laboratory','lab'].includes(user?.user_type)
  const isPatient = user?.user_type === 'patient'

  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3500)
  }

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API}/lab-requests`, { headers })
      if (res.ok) setRequests(await res.json())
    } finally { setLoading(false) }
  }, [token])

  useEffect(() => { load() }, [load])

  const filtered = requests.filter(r => tab === 'all' || r.status === tab)

  // ── نموذج الطلب ─────────────────────────────────────────
  const [form, setForm] = useState({
    urgency: 'routine', clinical_notes: '', ordering_doctor: '', patient_id: '',
    lab_center_name: '', scheduled_datetime: '',
    home_collection: false,
    collection_address: '', collection_date: '', collection_time: '', collection_staff_name: '',
  })
  const [selectedTests, setSelectedTests] = useState([{ name: '', category: 'blood' }])
  const [requestDoc, setRequestDoc] = useState(null)

  const prepInstructions = PREP_BY_CATEGORY[selectedTests[0]?.category] || PREP_BY_CATEGORY.other

  const addTest = () => setSelectedTests(ts => [...ts, { name: '', category: 'blood' }])
  const removeTest = idx => setSelectedTests(ts => ts.filter((_, i) => i !== idx))
  const updateTest = (idx, field, val) => setSelectedTests(ts => ts.map((t, i) => i === idx ? { ...t, [field]: val } : t))

  const submitRequest = async e => {
    e.preventDefault()
    const validTests = selectedTests.filter(t => t.name.trim())
    if (!validTests.length) { showToast('أدخل اسم تحليل واحد على الأقل', 'error'); return }
    setBusy(true)
    try {
      const fd = new FormData()
      fd.append('test_name', validTests[0].name)
      fd.append('test_category', validTests[0].category)
      fd.append('tests_json', JSON.stringify(validTests))
      Object.entries(form).forEach(([k, v]) => {
        if (k === 'home_collection') fd.append(k, v ? 'true' : 'false')
        else if (v) fd.append(k, v)
      })
      if (isPatient) fd.delete('patient_id')
      if (requestDoc) fd.append('request_doc', requestDoc)

      const res = await fetch(`${API}/lab-requests`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: fd,
      })
      const data = await res.json()
      if (res.ok) {
        showToast('تم إرسال طلب التحليل بنجاح')
        setShowForm(false)
        setSelectedTests([{ name: '', category: 'blood' }])
        setForm({ urgency:'routine', clinical_notes:'', ordering_doctor:'', patient_id:'', lab_center_name:'', scheduled_datetime:'', home_collection:false, collection_address:'', collection_date:'', collection_time:'', collection_staff_name:'' })
        setRequestDoc(null)
        load()
      } else showToast(data.message || 'حدث خطأ', 'error')
    } finally { setBusy(false) }
  }

  // ── اعتماد ─────────────────────────────────────────────
  const [approveNotes, setApproveNotes] = useState('')
  const handleApprove = async () => {
    setBusy(true)
    try {
      const res = await fetch(`${API}/lab-requests/${actionModal.request.id}/approve`, {
        method: 'PUT', headers, body: JSON.stringify({ approval_notes: approveNotes }),
      })
      const data = await res.json()
      if (res.ok) { showToast('تم الاعتماد بنجاح'); setActionModal(null); load() }
      else showToast(data.message || 'حدث خطأ', 'error')
    } finally { setBusy(false) }
  }

  // ── رفض ─────────────────────────────────────────────────
  const [rejectReason, setRejectReason] = useState('')
  const handleReject = async () => {
    setBusy(true)
    try {
      const res = await fetch(`${API}/lab-requests/${actionModal.request.id}/reject`, {
        method: 'PUT', headers, body: JSON.stringify({ rejection_reason: rejectReason }),
      })
      const data = await res.json()
      if (res.ok) { showToast('تم الرفض'); setActionModal(null); load() }
      else showToast(data.message || 'حدث خطأ', 'error')
    } finally { setBusy(false) }
  }

  // ── رفع النتائج ─────────────────────────────────────────
  const [resultForm, setResultForm] = useState({
    lab_name:'', result_value:'', result_unit:'', reference_range:'',
    result_status:'normal', result_interpretation:'',
  })
  const [resultFile, setResultFile] = useState(null)

  const handleUploadResults = async () => {
    setBusy(true)
    try {
      const fd = new FormData()
      Object.entries(resultForm).forEach(([k,v]) => fd.append(k, v))
      if (resultFile) fd.append('result_file', resultFile)
      const res = await fetch(`${API}/lab-requests/${actionModal.request.id}/results`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: fd,
      })
      const data = await res.json()
      if (res.ok) { showToast('تم رفع النتائج بنجاح'); setActionModal(null); load() }
      else showToast(data.message || 'حدث خطأ', 'error')
    } finally { setBusy(false) }
  }

  // ── إشعار ───────────────────────────────────────────────
  const handleNotify = async req => {
    setBusy(true)
    try {
      const res = await fetch(`${API}/lab-requests/${req.id}/notify`, {
        method: 'POST', headers,
      })
      const data = await res.json()
      if (res.ok) { showToast('تم إرسال الإشعارات وحفظها في السجل الطبي'); load() }
      else showToast(data.message || 'حدث خطأ', 'error')
    } finally { setBusy(false) }
  }

  // ── UI ───────────────────────────────────────────────────
  const StatusBadge = ({ status }) => {
    const cfg = STATUS_CONFIG[status] || { label: status, color: 'bg-gray-100 text-gray-700', icon: Clock }
    const Icon = cfg.icon
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${cfg.color}`}>
        <Icon size={12} /> {cfg.label}
      </span>
    )
  }

  const UrgencyBadge = ({ urgency }) => {
    const cfg = { emergency:'bg-red-200 text-red-800', urgent:'bg-red-100 text-red-700', routine:'bg-gray-100 text-gray-600' }
    const lbl = { emergency:'طارئ', urgent:'عاجل', routine:'روتيني' }
    return <span className={`text-xs px-2 py-0.5 rounded-full ${cfg[urgency]||cfg.routine}`}>{lbl[urgency]||urgency}</span>
  }

  const tabs = [
    { key: 'all',              label: 'الكل' },
    { key: 'requested',        label: 'بانتظار الاعتماد' },
    { key: 'approved',         label: 'معتمد' },
    { key: 'results_uploaded', label: 'نتائج مرفوعة' },
    { key: 'completed',        label: 'مكتمل' },
  ]

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 p-4 md:p-8">
      {/* Toast */}
      {toast && (
        <div className={`fixed top-4 left-1/2 -translate-x-1/2 z-50 px-6 py-3 rounded-xl shadow-lg text-white text-sm font-medium
          ${toast.type === 'error' ? 'bg-red-500' : 'bg-green-500'}`}>
          {toast.msg}
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 text-white p-2.5 rounded-xl"><FlaskConical size={22} /></div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">طلبات التحاليل المخبرية</h1>
            <p className="text-sm text-gray-500">إدارة طلبات التحاليل ونتائجها</p>
          </div>
        </div>
        <button onClick={() => setShowForm(v => !v)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          <Plus size={16} /> طلب تحليل جديد
        </button>
      </div>

      {/* نموذج الطلب */}
      {showForm && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
          <h2 className="font-semibold text-gray-800 mb-4">طلب تحليل جديد</h2>
          <form onSubmit={submitRequest} className="space-y-5">

            {/* قائمة التحاليل */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700">التحاليل المطلوبة *</label>
                <button type="button" onClick={addTest}
                  className="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1">
                  <Plus size={13}/> إضافة تحليل آخر
                </button>
              </div>
              <div className="space-y-2">
                {selectedTests.map((t, i) => (
                  <div key={i} className="flex gap-2 items-center">
                    <input
                      required={i === 0}
                      className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={t.name} onChange={e => updateTest(i, 'name', e.target.value)}
                      placeholder={`مثال: ${['صورة دم كاملة CBC', 'سكر صيام', 'وظائف كبد', 'هرمونات الغدة'][i] || 'اسم التحليل'}`} />
                    <select
                      className="border border-gray-200 rounded-lg px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={t.category} onChange={e => updateTest(i, 'category', e.target.value)}>
                      {CATEGORIES.map(c => <option key={c} value={c}>{CATEGORY_LABELS[c]}</option>)}
                    </select>
                    {i > 0 && (
                      <button type="button" onClick={() => removeTest(i)}
                        className="text-red-400 hover:text-red-600 p-1"><XCircle size={16}/></button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* تعليمات التحضير (تلقائية) */}
            {prepInstructions.length > 0 && (
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                <h4 className="text-sm font-semibold text-amber-800 mb-2 flex items-center gap-1">
                  <Info size={14}/> تعليمات التحضير
                </h4>
                <ul className="text-sm text-amber-700 space-y-1">
                  {prepInstructions.map((p, i) => <li key={i} className="flex items-start gap-1.5">• {p}</li>)}
                </ul>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* الأولوية */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الأولوية</label>
                <select className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={form.urgency} onChange={e => setForm(f => ({...f, urgency: e.target.value}))}>
                  <option value="routine">روتيني</option>
                  <option value="urgent">عاجل</option>
                  <option value="emergency">طارئ</option>
                </select>
              </div>

              {/* مركز التحاليل */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1"><Building2 size={13}/> مركز التحاليل</label>
                <select className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={form.lab_center_name} onChange={e => setForm(f=>({...f, lab_center_name: e.target.value}))}>
                  <option value="">-- اختر مركزاً --</option>
                  {LAB_CENTERS.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>

              {/* موعد التحليل */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1"><Calendar size={13}/> موعد التحليل</label>
                <input type="datetime-local" className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={form.scheduled_datetime} onChange={e => setForm(f=>({...f, scheduled_datetime: e.target.value}))} />
              </div>

              {/* الطبيب الآمر */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الطبيب الآمر</label>
                <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={form.ordering_doctor} onChange={e => setForm(f => ({...f, ordering_doctor: e.target.value}))} placeholder="اسم الطبيب" />
              </div>

              {!isPatient && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">معرّف المريض *</label>
                  <input required={!isPatient} type="number" className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={form.patient_id} onChange={e => setForm(f => ({...f, patient_id: e.target.value}))} />
                </div>
              )}
            </div>

            {/* ملاحظات سريرية */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات سريرية</label>
              <textarea rows={2} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={form.clinical_notes} onChange={e => setForm(f => ({...f, clinical_notes: e.target.value}))} placeholder="معلومات إضافية للمختبر..." />
            </div>

            {/* وثيقة الطلب */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
                <Paperclip size={13}/> وثيقة الطلب الأصلي (اختياري)
              </label>
              <input type="file" accept=".pdf,.jpg,.jpeg,.png"
                onChange={e => setRequestDoc(e.target.files[0])}
                className="w-full text-sm text-gray-500 file:ml-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-sm file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" />
              {requestDoc && <p className="text-xs text-blue-600 mt-1">✓ {requestDoc.name}</p>}
            </div>

            {/* التحصيل المنزلي */}
            <div className="border border-blue-100 rounded-xl p-4 bg-blue-50/50">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={form.home_collection}
                  onChange={e => setForm(f=>({...f, home_collection: e.target.checked}))}
                  className="w-4 h-4 rounded text-blue-600" />
                <span className="font-medium text-blue-800 flex items-center gap-1.5 text-sm">
                  <Home size={15}/> التحصيل المنزلي (إرسال فني للمنزل)
                </span>
              </label>
              {form.home_collection && (
                <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="md:col-span-2">
                    <label className="block text-xs font-medium text-gray-600 mb-1">العنوان *</label>
                    <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                      value={form.collection_address} onChange={e => setForm(f=>({...f, collection_address:e.target.value}))} placeholder="العنوان الكامل للمنزل" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">التاريخ المفضّل *</label>
                    <input type="date" className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                      value={form.collection_date} onChange={e => setForm(f=>({...f, collection_date:e.target.value}))} />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">الوقت المفضّل *</label>
                    <select className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                      value={form.collection_time} onChange={e => setForm(f=>({...f, collection_time:e.target.value}))}>
                      <option value="">-- اختر وقتاً --</option>
                      {['07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00'].map(t =>
                        <option key={t} value={t}>{t}</option>
                      )}
                    </select>
                  </div>
                </div>
              )}
            </div>

            <div className="flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800">إلغاء</button>
              <button type="submit" disabled={busy} className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg text-sm font-medium disabled:opacity-60">
                {busy ? 'جاري الإرسال...' : 'إرسال الطلب'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 bg-white rounded-xl p-1 border border-gray-100 mb-6 overflow-x-auto">
        {tabs.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`flex-shrink-0 px-4 py-2 rounded-lg text-sm font-medium transition-colors
              ${tab === t.key ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'}`}>
            {t.label}
            <span className={`mr-1.5 text-xs px-1.5 py-0.5 rounded-full
              ${tab === t.key ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-500'}`}>
              {requests.filter(r => t.key === 'all' || r.status === t.key).length}
            </span>
          </button>
        ))}
      </div>

      {/* القائمة */}
      {loading ? (
        <div className="flex justify-center py-16"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" /></div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <FlaskConical size={40} className="mx-auto mb-3 opacity-40" />
          <p>لا توجد طلبات</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map(req => (
            <div key={req.id} className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => setExpanded(expanded === req.id ? null : req.id)}>
                <div className="flex items-center gap-3">
                  <div className="bg-blue-50 text-blue-600 p-2 rounded-lg"><FlaskConical size={18} /></div>
                  <div>
                    <p className="font-semibold text-gray-800">{req.test_name}</p>
                    <p className="text-xs text-gray-500">
                      {CATEGORY_LABELS[req.test_category] || req.test_category}
                      {req.lab_center_name && <> · {req.lab_center_name}</>}
                      {req.home_collection && <> · <span className="text-blue-600">تحصيل منزلي</span></>}
                      {' · '}{new Date(req.created_at).toLocaleDateString('ar-SA')}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <UrgencyBadge urgency={req.urgency} />
                  <StatusBadge status={req.status} />
                  {expanded === req.id ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
                </div>
              </div>

              {expanded === req.id && (
                <div className="border-t border-gray-50 p-4 bg-gray-50/50">
                  {/* تفاصيل */}
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-3 text-sm">
                    {req.ordering_doctor && <div><span className="text-gray-500">الطبيب: </span><span className="font-medium">{req.ordering_doctor}</span></div>}
                    {req.lab_center_name && <div><span className="text-gray-500">المركز: </span><span className="font-medium">{req.lab_center_name}</span></div>}
                    {req.lab_name && <div><span className="text-gray-500">المختبر: </span><span className="font-medium">{req.lab_name}</span></div>}
                    {req.scheduled_datetime && <div><span className="text-gray-500">الموعد: </span><span className="font-medium">{new Date(req.scheduled_datetime).toLocaleString('ar-SA')}</span></div>}
                    {req.clinical_notes && <div className="col-span-2"><span className="text-gray-500">ملاحظات: </span><span>{req.clinical_notes}</span></div>}
                    {req.rejection_reason && <div className="col-span-2 text-red-600"><span className="font-medium">سبب الرفض: </span>{req.rejection_reason}</div>}
                  </div>

                  {/* تحاليل متعددة */}
                  {req.tests?.length > 1 && (
                    <div className="bg-white rounded-xl border border-gray-100 p-3 mb-3">
                      <h4 className="text-xs font-semibold text-gray-600 mb-2">التحاليل المطلوبة ({req.tests.length})</h4>
                      <div className="flex flex-wrap gap-1.5">
                        {req.tests.map((t, i) => (
                          <span key={i} className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">{t.name}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* تعليمات التحضير */}
                  {req.preparation_instructions && (() => {
                    try {
                      const instr = JSON.parse(req.preparation_instructions)
                      return instr.length > 0 ? (
                        <div className="bg-amber-50 border border-amber-100 rounded-xl p-3 mb-3">
                          <h4 className="text-xs font-semibold text-amber-800 mb-1.5 flex items-center gap-1"><Info size={12}/> تعليمات التحضير</h4>
                          <ul className="text-xs text-amber-700 space-y-0.5">
                            {instr.map((p, i) => <li key={i}>• {p}</li>)}
                          </ul>
                        </div>
                      ) : null
                    } catch { return null }
                  })()}

                  {/* وثيقة الطلب */}
                  {req.request_doc_path && (
                    <div className="bg-blue-50 border border-blue-100 rounded-xl p-3 mb-3 flex items-center gap-2">
                      <Paperclip size={14} className="text-blue-600"/>
                      <a href={`/api/uploads/lab_request_docs/${req.request_doc_path}`} target="_blank" rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:underline font-medium">
                        {req.request_doc_name || 'وثيقة الطلب الأصلي'}
                      </a>
                    </div>
                  )}

                  {/* تحصيل منزلي */}
                  {req.home_collection && (
                    <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-3 mb-3">
                      <h4 className="text-xs font-semibold text-indigo-800 mb-1.5 flex items-center gap-1"><Home size={12}/> تفاصيل التحصيل المنزلي</h4>
                      <div className="text-xs text-indigo-700 space-y-0.5">
                        {req.collection_address && <p>العنوان: {req.collection_address}</p>}
                        {req.collection_date && <p>التاريخ: {req.collection_date}</p>}
                        {req.collection_time && <p>الوقت: {req.collection_time}</p>}
                        {req.collection_staff_name && <p>الفني المعيَّن: {req.collection_staff_name}</p>}
                      </div>
                    </div>
                  )}

                  {/* النتائج */}
                  {req.result_value && (
                    <div className="bg-white rounded-xl border border-gray-100 p-4 mb-3">
                      <h4 className="font-semibold text-gray-700 mb-2 text-sm flex items-center gap-1"><FileText size={13}/> النتائج</h4>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div><span className="text-gray-500">القيمة: </span>
                          <span className={`font-medium ${RESULT_STATUS[req.result_status]?.color || ''}`}>
                            {req.result_value} {req.result_unit || ''}
                          </span>
                        </div>
                        {req.reference_range && <div><span className="text-gray-500">المرجع: </span><span>{req.reference_range}</span></div>}
                        {req.result_status && <div><span className="text-gray-500">الحالة: </span>
                          <span className={`font-medium ${RESULT_STATUS[req.result_status]?.color || ''}`}>{RESULT_STATUS[req.result_status]?.label || req.result_status}</span>
                        </div>}
                        {req.result_interpretation && <div className="col-span-2"><span className="text-gray-500">التفسير: </span><span>{req.result_interpretation}</span></div>}
                      </div>
                      {req.result_file_name && (
                        <a href={`/api/uploads/lab_results/${req.result_file_path}`} target="_blank" rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 mt-2 text-xs text-blue-600 hover:underline">
                          <FileText size={12}/> {req.result_file_name}
                        </a>
                      )}
                    </div>
                  )}

                  {/* إجراءات */}
                  <div className="flex flex-wrap gap-2 mt-2">
                    {isAdmin && req.status === 'requested' && (
                      <>
                        <button onClick={() => { setActionModal({ type:'approve', request:req }); setApproveNotes('') }}
                          className="flex items-center gap-1 bg-green-50 text-green-700 border border-green-200 hover:bg-green-100 px-3 py-1.5 rounded-lg text-xs font-medium">
                          <CheckCircle size={13}/> اعتماد
                        </button>
                        <button onClick={() => { setActionModal({ type:'reject', request:req }); setRejectReason('') }}
                          className="flex items-center gap-1 bg-red-50 text-red-700 border border-red-200 hover:bg-red-100 px-3 py-1.5 rounded-lg text-xs font-medium">
                          <XCircle size={13}/> رفض
                        </button>
                      </>
                    )}
                    {isAdmin && req.status === 'approved' && (
                      <button onClick={() => { setActionModal({ type:'results', request:req }); setResultForm({lab_name:'',result_value:'',result_unit:'',reference_range:'',result_status:'normal',result_interpretation:''}); setResultFile(null) }}
                        className="flex items-center gap-1 bg-purple-50 text-purple-700 border border-purple-200 hover:bg-purple-100 px-3 py-1.5 rounded-lg text-xs font-medium">
                        <Upload size={13}/> رفع النتائج
                      </button>
                    )}
                    {isAdmin && req.status === 'results_uploaded' && (
                      <button onClick={() => handleNotify(req)} disabled={busy}
                        className="flex items-center gap-1 bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 px-3 py-1.5 rounded-lg text-xs font-medium disabled:opacity-60">
                        <Bell size={13}/> إشعار وحفظ في السجل الطبي
                      </button>
                    )}
                    {req.notified_at && <span className="text-xs text-gray-400">أُشعر في {new Date(req.notified_at).toLocaleDateString('ar-SA')}</span>}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Modals */}
      {actionModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-md" dir="rtl">
            {actionModal.type === 'approve' && (
              <>
                <h3 className="font-bold text-gray-900 mb-4">اعتماد طلب التحليل</h3>
                <textarea rows={3} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-green-400 mb-4"
                  value={approveNotes} onChange={e => setApproveNotes(e.target.value)} placeholder="ملاحظات الاعتماد (اختياري)..." />
              </>
            )}
            {actionModal.type === 'reject' && (
              <>
                <h3 className="font-bold text-gray-900 mb-4">رفض طلب التحليل</h3>
                <textarea rows={3} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-red-400 mb-4"
                  value={rejectReason} onChange={e => setRejectReason(e.target.value)} placeholder="سبب الرفض..." />
              </>
            )}
            {actionModal.type === 'results' && (
              <>
                <h3 className="font-bold text-gray-900 mb-4">رفع نتائج التحليل</h3>
                {[
                  ['lab_name','اسم المختبر'],['result_value','قيمة النتيجة'],
                  ['result_unit','الوحدة'],['reference_range','النطاق الطبيعي'],
                ].map(([k, lbl]) => (
                  <div key={k} className="mb-3">
                    <label className="block text-sm font-medium text-gray-700 mb-1">{lbl}</label>
                    <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                      value={resultForm[k]} onChange={e => setResultForm(f=>({...f,[k]:e.target.value}))} />
                  </div>
                ))}
                <div className="mb-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">حالة النتيجة</label>
                  <select className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    value={resultForm.result_status} onChange={e => setResultForm(f=>({...f,result_status:e.target.value}))}>
                    <option value="normal">طبيعي</option>
                    <option value="abnormal">غير طبيعي</option>
                    <option value="critical">حرج</option>
                  </select>
                </div>
                <div className="mb-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">التفسير</label>
                  <textarea rows={2} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    value={resultForm.result_interpretation} onChange={e => setResultForm(f=>({...f,result_interpretation:e.target.value}))} />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">ملف النتائج (اختياري)</label>
                  <input type="file" accept=".pdf,.jpg,.jpeg,.png"
                    onChange={e => setResultFile(e.target.files[0])}
                    className="w-full text-sm text-gray-500 file:ml-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-sm file:bg-purple-50 file:text-purple-700" />
                </div>
              </>
            )}
            <div className="flex gap-3 justify-end">
              <button onClick={() => setActionModal(null)} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800">إلغاء</button>
              <button disabled={busy} onClick={
                actionModal.type === 'approve' ? handleApprove :
                actionModal.type === 'reject'  ? handleReject  :
                handleUploadResults
              }
                className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg text-sm font-medium disabled:opacity-60">
                {busy ? 'جاري...' : 'تأكيد'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
