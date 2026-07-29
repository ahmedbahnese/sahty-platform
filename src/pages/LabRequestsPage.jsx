import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { FlaskConical, Plus, CheckCircle, XCircle, Upload, Bell, ChevronDown, ChevronUp, AlertTriangle, Clock, FileText } from 'lucide-react'

const API = '/api'

const STATUS_CONFIG = {
  requested:        { label: 'بانتظار الاعتماد', color: 'bg-yellow-100 text-yellow-800', icon: Clock },
  approved:         { label: 'معتمد',             color: 'bg-blue-100 text-blue-800',    icon: CheckCircle },
  results_uploaded: { label: 'نتائج مرفوعة',     color: 'bg-purple-100 text-purple-800', icon: Upload },
  completed:        { label: 'مكتمل',             color: 'bg-green-100 text-green-800',  icon: CheckCircle },
  rejected:         { label: 'مرفوض',             color: 'bg-red-100 text-red-800',      icon: XCircle },
}

const RESULT_STATUS = {
  normal:   { label: 'طبيعي',  color: 'text-green-600' },
  abnormal: { label: 'غير طبيعي', color: 'text-orange-600' },
  critical: { label: 'حرج',   color: 'text-red-600' },
}

const CATEGORIES = ['blood', 'urine', 'culture', 'hormones', 'biochemistry', 'immunology', 'genetics', 'other']
const CATEGORY_LABELS = {
  blood: 'دم', urine: 'بول', culture: 'مزرعة', hormones: 'هرمونات',
  biochemistry: 'كيمياء حيوية', immunology: 'مناعة', genetics: 'جينات', other: 'أخرى',
}

export default function LabRequestsPage() {
  const { token, user } = useAuth()
  const [requests, setRequests]   = useState([])
  const [loading, setLoading]     = useState(true)
  const [tab, setTab]             = useState('all')          // all | requested | approved | completed
  const [expanded, setExpanded]   = useState(null)
  const [showForm, setShowForm]   = useState(false)
  const [actionModal, setActionModal] = useState(null)       // { type, request }
  const [busy, setBusy]           = useState(false)
  const [toast, setToast]         = useState(null)

  const isAdmin = ['admin','super_admin','laboratory','lab'].includes(user?.user_type)
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
    } finally {
      setLoading(false)
    }
  }, [token])

  useEffect(() => { load() }, [load])

  const filtered = requests.filter(r => tab === 'all' || r.status === tab)

  // ── إنشاء طلب ──────────────────────────────────────────
  const [form, setForm] = useState({
    test_name: '', test_category: 'blood', urgency: 'normal',
    clinical_notes: '', ordering_doctor: '', patient_id: '',
  })

  const submitRequest = async e => {
    e.preventDefault()
    setBusy(true)
    try {
      const body = { ...form }
      if (isPatient) delete body.patient_id
      const res = await fetch(`${API}/lab-requests`, {
        method: 'POST', headers, body: JSON.stringify(body),
      })
      const data = await res.json()
      if (res.ok) {
        showToast('تم إرسال طلب التحليل بنجاح')
        setShowForm(false)
        setForm({ test_name:'', test_category:'blood', urgency:'normal', clinical_notes:'', ordering_doctor:'', patient_id:'' })
        load()
      } else showToast(data.message || 'حدث خطأ', 'error')
    } finally { setBusy(false) }
  }

  // ── اعتماد ──────────────────────────────────────────────
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

  // ── رفع النتائج ──────────────────────────────────────────
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

  // ── إرسال إشعار ─────────────────────────────────────────
  const handleNotify = async req => {
    setBusy(true)
    try {
      const res = await fetch(`${API}/lab-requests/${req.id}/notify`, {
        method: 'POST', headers,
      })
      const data = await res.json()
      if (res.ok) { showToast('تم إرسال الإشعارات بنجاح'); load() }
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
    const cfg = { urgent: 'bg-red-100 text-red-700', normal: 'bg-blue-50 text-blue-700', routine: 'bg-gray-100 text-gray-600' }
    const lbl = { urgent: 'عاجل', normal: 'عادي', routine: 'روتيني' }
    return <span className={`text-xs px-2 py-0.5 rounded-full ${cfg[urgency] || cfg.normal}`}>{lbl[urgency] || urgency}</span>
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
        <div className={`fixed top-4 left-1/2 -translate-x-1/2 z-50 px-6 py-3 rounded-xl shadow-lg text-white text-sm font-medium transition-all
          ${toast.type === 'error' ? 'bg-red-500' : 'bg-green-500'}`}>
          {toast.msg}
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 text-white p-2.5 rounded-xl">
            <FlaskConical size={22} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">طلبات التحاليل المخبرية</h1>
            <p className="text-sm text-gray-500">إدارة طلبات التحاليل ونتائجها</p>
          </div>
        </div>
        <button
          onClick={() => setShowForm(v => !v)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          <Plus size={16} /> طلب تحليل جديد
        </button>
      </div>

      {/* نموذج الطلب الجديد */}
      {showForm && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
          <h2 className="font-semibold text-gray-800 mb-4">طلب تحليل جديد</h2>
          <form onSubmit={submitRequest} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">اسم التحليل *</label>
              <input required className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={form.test_name} onChange={e => setForm(f => ({...f, test_name: e.target.value}))} placeholder="مثال: CBC صورة دم كاملة" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الفئة</label>
              <select className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={form.test_category} onChange={e => setForm(f => ({...f, test_category: e.target.value}))}>
                {CATEGORIES.map(c => <option key={c} value={c}>{CATEGORY_LABELS[c]}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الأولوية</label>
              <select className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={form.urgency} onChange={e => setForm(f => ({...f, urgency: e.target.value}))}>
                <option value="routine">روتيني</option>
                <option value="normal">عادي</option>
                <option value="urgent">عاجل</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الطبيب الآمر</label>
              <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={form.ordering_doctor} onChange={e => setForm(f => ({...f, ordering_doctor: e.target.value}))} placeholder="اسم الطبيب" />
            </div>
            {!isPatient && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">معرّف المريض *</label>
                <input required={!isPatient} type="number" className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={form.patient_id} onChange={e => setForm(f => ({...f, patient_id: e.target.value}))} placeholder="رقم المريض" />
              </div>
            )}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات سريرية</label>
              <textarea rows={2} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={form.clinical_notes} onChange={e => setForm(f => ({...f, clinical_notes: e.target.value}))} placeholder="معلومات إضافية للمختبر..." />
            </div>
            <div className="md:col-span-2 flex gap-3 justify-end">
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
              {/* Row Header */}
              <div className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => setExpanded(expanded === req.id ? null : req.id)}>
                <div className="flex items-center gap-3">
                  <div className="bg-blue-50 text-blue-600 p-2 rounded-lg"><FlaskConical size={18} /></div>
                  <div>
                    <p className="font-semibold text-gray-800">{req.test_name}</p>
                    <p className="text-xs text-gray-500">{CATEGORY_LABELS[req.test_category] || req.test_category} · {new Date(req.created_at).toLocaleDateString('ar-SA')}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <UrgencyBadge urgency={req.urgency} />
                  <StatusBadge status={req.status} />
                  {expanded === req.id ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
                </div>
              </div>

              {/* Expanded Details */}
              {expanded === req.id && (
                <div className="border-t border-gray-50 p-4 bg-gray-50/50">
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4 text-sm">
                    {req.ordering_doctor && <div><span className="text-gray-500">الطبيب الآمر: </span><span className="font-medium">{req.ordering_doctor}</span></div>}
                    {req.lab_name && <div><span className="text-gray-500">المختبر: </span><span className="font-medium">{req.lab_name}</span></div>}
                    {req.clinical_notes && <div className="col-span-2"><span className="text-gray-500">ملاحظات: </span><span>{req.clinical_notes}</span></div>}
                  </div>

                  {/* نتائج */}
                  {req.result_value && (
                    <div className="bg-white rounded-xl border border-gray-100 p-4 mb-4">
                      <h4 className="font-semibold text-gray-700 mb-2 flex items-center gap-2"><FileText size={15} /> النتائج</h4>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div><span className="text-gray-500">القيمة: </span>
                          <span className={`font-bold ${RESULT_STATUS[req.result_status]?.color || 'text-gray-800'}`}>
                            {req.result_value} {req.result_unit}
                          </span>
                          {req.result_status && <span className={`mr-2 text-xs ${RESULT_STATUS[req.result_status]?.color}`}>({RESULT_STATUS[req.result_status]?.label})</span>}
                        </div>
                        {req.reference_range && <div><span className="text-gray-500">المرجع: </span>{req.reference_range}</div>}
                        {req.result_interpretation && <div className="col-span-2"><span className="text-gray-500">التفسير: </span>{req.result_interpretation}</div>}
                        {req.result_file_name && (
                          <div className="col-span-2">
                            <a href={`/api/uploads/lab_results/${req.result_file_path}`} target="_blank" rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-blue-600 hover:underline text-xs">
                              <FileText size={12} /> {req.result_file_name}
                            </a>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* أزرار الإجراءات */}
                  <div className="flex flex-wrap gap-2">
                    {isAdmin && req.status === 'requested' && (
                      <>
                        <button onClick={() => { setApproveNotes(''); setActionModal({ type: 'approve', request: req }) }}
                          className="flex items-center gap-1.5 bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium">
                          <CheckCircle size={13} /> اعتماد الطلب
                        </button>
                        <button onClick={() => { setRejectReason(''); setActionModal({ type: 'reject', request: req }) }}
                          className="flex items-center gap-1.5 bg-red-500 hover:bg-red-600 text-white px-3 py-1.5 rounded-lg text-xs font-medium">
                          <XCircle size={13} /> رفض
                        </button>
                      </>
                    )}
                    {isAdmin && (req.status === 'approved' || req.status === 'requested') && (
                      <button onClick={() => { setResultForm({ lab_name:'', result_value:'', result_unit:'', reference_range:'', result_status:'normal', result_interpretation:'' }); setResultFile(null); setActionModal({ type: 'results', request: req }) }}
                        className="flex items-center gap-1.5 bg-purple-600 hover:bg-purple-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium">
                        <Upload size={13} /> رفع النتائج
                      </button>
                    )}
                    {isAdmin && req.status === 'results_uploaded' && (
                      <button onClick={() => handleNotify(req)} disabled={busy}
                        className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium disabled:opacity-60">
                        <Bell size={13} /> إرسال الإشعارات
                      </button>
                    )}
                    {req.status === 'completed' && (
                      <span className="flex items-center gap-1 text-green-600 text-xs font-medium">
                        <CheckCircle size={13} /> مكتمل — تم إشعار الطبيب والمريض
                      </span>
                    )}
                    {req.status === 'rejected' && req.rejection_reason && (
                      <span className="flex items-center gap-1 text-red-500 text-xs">
                        <AlertTriangle size={12} /> سبب الرفض: {req.rejection_reason}
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* ── Modals ── */}
      {actionModal && (
        <div className="fixed inset-0 bg-black/50 z-40 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">

            {/* اعتماد */}
            {actionModal.type === 'approve' && (
              <>
                <h3 className="font-bold text-gray-800 mb-1">اعتماد الطلب</h3>
                <p className="text-sm text-gray-500 mb-4">التحليل: <strong>{actionModal.request.test_name}</strong></p>
                <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات الاعتماد (اختياري)</label>
                <textarea rows={3} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-green-500"
                  value={approveNotes} onChange={e => setApproveNotes(e.target.value)} />
                <div className="flex gap-3 justify-end">
                  <button onClick={() => setActionModal(null)} className="px-4 py-2 text-sm text-gray-600">إلغاء</button>
                  <button onClick={handleApprove} disabled={busy} className="bg-green-600 hover:bg-green-700 text-white px-5 py-2 rounded-lg text-sm disabled:opacity-60">
                    {busy ? '...' : 'اعتماد'}
                  </button>
                </div>
              </>
            )}

            {/* رفض */}
            {actionModal.type === 'reject' && (
              <>
                <h3 className="font-bold text-gray-800 mb-1">رفض الطلب</h3>
                <p className="text-sm text-gray-500 mb-4">التحليل: <strong>{actionModal.request.test_name}</strong></p>
                <label className="block text-sm font-medium text-gray-700 mb-1">سبب الرفض</label>
                <textarea rows={3} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-red-500"
                  value={rejectReason} onChange={e => setRejectReason(e.target.value)} placeholder="اكتب سبب الرفض..." />
                <div className="flex gap-3 justify-end">
                  <button onClick={() => setActionModal(null)} className="px-4 py-2 text-sm text-gray-600">إلغاء</button>
                  <button onClick={handleReject} disabled={busy} className="bg-red-500 hover:bg-red-600 text-white px-5 py-2 rounded-lg text-sm disabled:opacity-60">
                    {busy ? '...' : 'رفض الطلب'}
                  </button>
                </div>
              </>
            )}

            {/* رفع النتائج */}
            {actionModal.type === 'results' && (
              <>
                <h3 className="font-bold text-gray-800 mb-1">رفع نتائج التحليل</h3>
                <p className="text-sm text-gray-500 mb-4">التحليل: <strong>{actionModal.request.test_name}</strong></p>
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">اسم المختبر</label>
                      <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                        value={resultForm.lab_name} onChange={e => setResultForm(f=>({...f,lab_name:e.target.value}))} />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">حالة النتيجة</label>
                      <select className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                        value={resultForm.result_status} onChange={e => setResultForm(f=>({...f,result_status:e.target.value}))}>
                        <option value="normal">طبيعي</option>
                        <option value="abnormal">غير طبيعي</option>
                        <option value="critical">حرج</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">قيمة النتيجة</label>
                      <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                        value={resultForm.result_value} onChange={e => setResultForm(f=>({...f,result_value:e.target.value}))} placeholder="مثال: 5.2" />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">الوحدة</label>
                      <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                        value={resultForm.result_unit} onChange={e => setResultForm(f=>({...f,result_unit:e.target.value}))} placeholder="مثال: g/dL" />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">النطاق المرجعي</label>
                    <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                      value={resultForm.reference_range} onChange={e => setResultForm(f=>({...f,reference_range:e.target.value}))} placeholder="مثال: 4.5 - 6.0" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">التفسير</label>
                    <textarea rows={2} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                      value={resultForm.result_interpretation} onChange={e => setResultForm(f=>({...f,result_interpretation:e.target.value}))} />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">ملف النتيجة (اختياري)</label>
                    <input type="file" accept=".pdf,.jpg,.jpeg,.png" className="w-full text-sm text-gray-600 file:ml-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-medium file:bg-purple-50 file:text-purple-700"
                      onChange={e => setResultFile(e.target.files[0])} />
                  </div>
                </div>
                <div className="flex gap-3 justify-end mt-4">
                  <button onClick={() => setActionModal(null)} className="px-4 py-2 text-sm text-gray-600">إلغاء</button>
                  <button onClick={handleUploadResults} disabled={busy} className="bg-purple-600 hover:bg-purple-700 text-white px-5 py-2 rounded-lg text-sm disabled:opacity-60">
                    {busy ? '...' : 'رفع النتائج'}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
