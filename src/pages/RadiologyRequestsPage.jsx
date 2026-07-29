import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Scan, Plus, Upload, Share2, XCircle, ChevronDown, ChevronUp, Clock, CheckCircle, AlertTriangle, FileText, Image } from 'lucide-react'

const API = '/api'

const STATUS_CONFIG = {
  requested:       { label: 'بانتظار المعالجة', color: 'bg-yellow-100 text-yellow-800', icon: Clock },
  images_uploaded: { label: 'صور مرفوعة',      color: 'bg-blue-100 text-blue-800',     icon: Image },
  report_uploaded: { label: 'تقرير مرفوع',     color: 'bg-purple-100 text-purple-800', icon: FileText },
  shared:          { label: 'مشارك',            color: 'bg-green-100 text-green-800',   icon: CheckCircle },
  rejected:        { label: 'مرفوض',            color: 'bg-red-100 text-red-800',       icon: XCircle },
}

const SCAN_TYPES = {
  xray:       'أشعة سينية (X-Ray)',
  mri:        'رنين مغناطيسي (MRI)',
  ct:         'طبقي محوري (CT)',
  ultrasound: 'موجات فوق صوتية',
  pet:        'بيت سكان (PET)',
  mammo:      'تصوير ثدي (Mammogram)',
  other:      'أخرى',
}

export default function RadiologyRequestsPage() {
  const { token, user } = useAuth()
  const [requests, setRequests]   = useState([])
  const [loading, setLoading]     = useState(true)
  const [tab, setTab]             = useState('all')
  const [expanded, setExpanded]   = useState(null)
  const [showForm, setShowForm]   = useState(false)
  const [actionModal, setActionModal] = useState(null)
  const [busy, setBusy]           = useState(false)
  const [toast, setToast]         = useState(null)

  const isAdmin    = ['admin','super_admin','radiology_center'].includes(user?.user_type)
  const isPatient  = user?.user_type === 'patient'

  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3500)
  }

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API}/radiology-requests`, { headers })
      if (res.ok) setRequests(await res.json())
    } finally {
      setLoading(false)
    }
  }, [token])

  useEffect(() => { load() }, [load])

  const filtered = requests.filter(r => tab === 'all' || r.status === tab)

  // ── نموذج الطلب الجديد ──────────────────────────────────
  const [form, setForm] = useState({
    scan_type: 'xray', body_part: '', urgency: 'normal',
    clinical_reason: '', ordering_doctor: '', patient_id: '',
  })

  const submitRequest = async e => {
    e.preventDefault()
    setBusy(true)
    try {
      const body = { ...form }
      if (isPatient) delete body.patient_id
      const res = await fetch(`${API}/radiology-requests`, {
        method: 'POST', headers, body: JSON.stringify(body),
      })
      const data = await res.json()
      if (res.ok) {
        showToast('تم إرسال طلب الأشعة بنجاح')
        setShowForm(false)
        setForm({ scan_type:'xray', body_part:'', urgency:'normal', clinical_reason:'', ordering_doctor:'', patient_id:'' })
        load()
      } else showToast(data.message || 'حدث خطأ', 'error')
    } finally { setBusy(false) }
  }

  // ── رفع الصور ────────────────────────────────────────────
  const [imageFiles, setImageFiles] = useState([])
  const [facilityInput, setFacilityInput] = useState('')

  const handleUploadImages = async () => {
    if (!imageFiles.length) { showToast('اختر صورة على الأقل', 'error'); return }
    setBusy(true)
    try {
      const fd = new FormData()
      imageFiles.forEach(f => fd.append('images', f))
      if (facilityInput) fd.append('facility', facilityInput)
      const res = await fetch(`${API}/radiology-requests/${actionModal.request.id}/images`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: fd,
      })
      const data = await res.json()
      if (res.ok) { showToast('تم رفع الصور بنجاح'); setActionModal(null); load() }
      else showToast(data.message || 'حدث خطأ', 'error')
    } finally { setBusy(false) }
  }

  // ── رفع التقرير ──────────────────────────────────────────
  const [reportForm, setReportForm] = useState({
    facility: '', radiologist_name: '', findings: '',
    impression: '', recommendation: '',
  })
  const [reportFile, setReportFile] = useState(null)

  const handleUploadReport = async () => {
    setBusy(true)
    try {
      const fd = new FormData()
      Object.entries(reportForm).forEach(([k,v]) => fd.append(k, v))
      if (reportFile) fd.append('report_file', reportFile)
      const res = await fetch(`${API}/radiology-requests/${actionModal.request.id}/report`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: fd,
      })
      const data = await res.json()
      if (res.ok) { showToast('تم رفع التقرير بنجاح'); setActionModal(null); load() }
      else showToast(data.message || 'حدث خطأ', 'error')
    } finally { setBusy(false) }
  }

  // ── مشاركة النتائج ───────────────────────────────────────
  const handleShare = async req => {
    setBusy(true)
    try {
      const res = await fetch(`${API}/radiology-requests/${req.id}/share`, {
        method: 'POST', headers,
      })
      const data = await res.json()
      if (res.ok) { showToast('تم مشاركة النتائج بنجاح'); load() }
      else showToast(data.message || 'حدث خطأ', 'error')
    } finally { setBusy(false) }
  }

  // ── رفض ─────────────────────────────────────────────────
  const [rejectReason, setRejectReason] = useState('')
  const handleReject = async () => {
    setBusy(true)
    try {
      const res = await fetch(`${API}/radiology-requests/${actionModal.request.id}/reject`, {
        method: 'PUT', headers, body: JSON.stringify({ rejection_reason: rejectReason }),
      })
      const data = await res.json()
      if (res.ok) { showToast('تم الرفض'); setActionModal(null); load() }
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
    const cfg = { urgent:'bg-red-100 text-red-700', normal:'bg-blue-50 text-blue-700', routine:'bg-gray-100 text-gray-600' }
    const lbl = { urgent:'عاجل', normal:'عادي', routine:'روتيني' }
    return <span className={`text-xs px-2 py-0.5 rounded-full ${cfg[urgency]||cfg.normal}`}>{lbl[urgency]||urgency}</span>
  }

  const tabs = [
    { key: 'all',            label: 'الكل' },
    { key: 'requested',      label: 'بانتظار المعالجة' },
    { key: 'images_uploaded',label: 'صور مرفوعة' },
    { key: 'report_uploaded',label: 'تقرير مرفوع' },
    { key: 'shared',         label: 'مشارك' },
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
          <div className="bg-indigo-600 text-white p-2.5 rounded-xl"><Scan size={22} /></div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">طلبات الأشعة والتصوير الطبي</h1>
            <p className="text-sm text-gray-500">إدارة طلبات الأشعة والتقارير الطبية</p>
          </div>
        </div>
        <button onClick={() => setShowForm(v => !v)}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          <Plus size={16} /> طلب أشعة جديد
        </button>
      </div>

      {/* نموذج الطلب */}
      {showForm && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
          <h2 className="font-semibold text-gray-800 mb-4">طلب أشعة جديد</h2>
          <form onSubmit={submitRequest} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">نوع الأشعة *</label>
              <select required className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={form.scan_type} onChange={e => setForm(f=>({...f,scan_type:e.target.value}))}>
                {Object.entries(SCAN_TYPES).map(([v,l]) => <option key={v} value={v}>{l}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الجزء المصوَّر *</label>
              <input required className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={form.body_part} onChange={e => setForm(f=>({...f,body_part:e.target.value}))} placeholder="مثال: الصدر، الركبة اليسرى" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الأولوية</label>
              <select className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={form.urgency} onChange={e => setForm(f=>({...f,urgency:e.target.value}))}>
                <option value="routine">روتيني</option>
                <option value="normal">عادي</option>
                <option value="urgent">عاجل</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الطبيب الآمر</label>
              <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={form.ordering_doctor} onChange={e => setForm(f=>({...f,ordering_doctor:e.target.value}))} placeholder="اسم الطبيب" />
            </div>
            {!isPatient && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">معرّف المريض *</label>
                <input required={!isPatient} type="number" className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  value={form.patient_id} onChange={e => setForm(f=>({...f,patient_id:e.target.value}))} />
              </div>
            )}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">السبب السريري</label>
              <textarea rows={2} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={form.clinical_reason} onChange={e => setForm(f=>({...f,clinical_reason:e.target.value}))} placeholder="سبب طلب الأشعة..." />
            </div>
            <div className="md:col-span-2 flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800">إلغاء</button>
              <button type="submit" disabled={busy} className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg text-sm font-medium disabled:opacity-60">
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
              ${tab === t.key ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:bg-gray-50'}`}>
            {t.label}
            <span className={`mr-1.5 text-xs px-1.5 py-0.5 rounded-full
              ${tab === t.key ? 'bg-indigo-500 text-white' : 'bg-gray-100 text-gray-500'}`}>
              {requests.filter(r => t.key==='all'||r.status===t.key).length}
            </span>
          </button>
        ))}
      </div>

      {/* القائمة */}
      {loading ? (
        <div className="flex justify-center py-16"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600" /></div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <Scan size={40} className="mx-auto mb-3 opacity-40" />
          <p>لا توجد طلبات</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map(req => (
            <div key={req.id} className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => setExpanded(expanded === req.id ? null : req.id)}>
                <div className="flex items-center gap-3">
                  <div className="bg-indigo-50 text-indigo-600 p-2 rounded-lg"><Scan size={18} /></div>
                  <div>
                    <p className="font-semibold text-gray-800">{SCAN_TYPES[req.scan_type] || req.scan_type}</p>
                    <p className="text-xs text-gray-500">{req.body_part} · {new Date(req.created_at).toLocaleDateString('ar-SA')}</p>
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
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4 text-sm">
                    {req.ordering_doctor && <div><span className="text-gray-500">الطبيب الآمر: </span><span className="font-medium">{req.ordering_doctor}</span></div>}
                    {req.facility && <div><span className="text-gray-500">المركز: </span><span className="font-medium">{req.facility}</span></div>}
                    {req.radiologist_name && <div><span className="text-gray-500">الطبيب الشعاعي: </span><span className="font-medium">{req.radiologist_name}</span></div>}
                    {req.clinical_reason && <div className="col-span-2"><span className="text-gray-500">السبب: </span><span>{req.clinical_reason}</span></div>}
                  </div>

                  {/* الصور المرفوعة */}
                  {req.image_paths?.length > 0 && (
                    <div className="bg-white rounded-xl border border-gray-100 p-3 mb-3">
                      <h4 className="text-xs font-semibold text-gray-600 mb-2 flex items-center gap-1"><Image size={13}/> الصور المرفوعة ({req.image_paths.length})</h4>
                      <div className="flex flex-wrap gap-2">
                        {req.image_paths.map((img, i) => (
                          <a key={i} href={`/api/uploads/radiology_images/${img.path}`} target="_blank" rel="noopener noreferrer"
                            className="text-xs text-indigo-600 hover:underline bg-indigo-50 px-2 py-1 rounded">
                            {img.name || `صورة ${i+1}`}
                          </a>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* التقرير */}
                  {(req.findings || req.impression) && (
                    <div className="bg-white rounded-xl border border-gray-100 p-4 mb-4">
                      <h4 className="font-semibold text-gray-700 mb-2 flex items-center gap-2 text-sm"><FileText size={14}/> تقرير الأشعة</h4>
                      {req.findings && <div className="mb-1 text-sm"><span className="text-gray-500 font-medium">النتائج: </span>{req.findings}</div>}
                      {req.impression && <div className="mb-1 text-sm"><span className="text-gray-500 font-medium">التفسير: </span>{req.impression}</div>}
                      {req.recommendation && <div className="text-sm"><span className="text-gray-500 font-medium">التوصيات: </span>{req.recommendation}</div>}
                      {req.report_file_name && (
                        <a href={`/api/uploads/radiology_reports/${req.report_file_path}`} target="_blank" rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-indigo-600 hover:underline text-xs mt-2">
                          <FileText size={12}/> {req.report_file_name}
                        </a>
                      )}
                    </div>
                  )}

                  {/* أزرار الإجراءات */}
                  <div className="flex flex-wrap gap-2">
                    {isAdmin && req.status === 'requested' && (
                      <>
                        <button onClick={() => { setImageFiles([]); setFacilityInput(''); setActionModal({ type:'images', request:req }) }}
                          className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium">
                          <Upload size={13}/> رفع الصور
                        </button>
                        <button onClick={() => { setRejectReason(''); setActionModal({ type:'reject', request:req }) }}
                          className="flex items-center gap-1.5 bg-red-500 hover:bg-red-600 text-white px-3 py-1.5 rounded-lg text-xs font-medium">
                          <XCircle size={13}/> رفض
                        </button>
                      </>
                    )}
                    {isAdmin && req.status === 'images_uploaded' && (
                      <button onClick={() => { setReportForm({ facility:req.facility||'', radiologist_name:'', findings:'', impression:'', recommendation:'' }); setReportFile(null); setActionModal({ type:'report', request:req }) }}
                        className="flex items-center gap-1.5 bg-purple-600 hover:bg-purple-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium">
                        <FileText size={13}/> رفع التقرير
                      </button>
                    )}
                    {isAdmin && req.status === 'report_uploaded' && (
                      <button onClick={() => handleShare(req)} disabled={busy}
                        className="flex items-center gap-1.5 bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium disabled:opacity-60">
                        <Share2 size={13}/> مشاركة النتائج
                      </button>
                    )}
                    {req.status === 'shared' && (
                      <span className="flex items-center gap-1 text-green-600 text-xs font-medium">
                        <CheckCircle size={13}/> تم المشاركة — تم إشعار الطبيب والمريض
                      </span>
                    )}
                    {req.status === 'rejected' && req.rejection_reason && (
                      <span className="flex items-center gap-1 text-red-500 text-xs">
                        <AlertTriangle size={12}/> سبب الرفض: {req.rejection_reason}
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

            {/* رفع الصور */}
            {actionModal.type === 'images' && (
              <>
                <h3 className="font-bold text-gray-800 mb-1">رفع صور الأشعة</h3>
                <p className="text-sm text-gray-500 mb-4">{SCAN_TYPES[actionModal.request.scan_type]} — {actionModal.request.body_part}</p>
                <div className="space-y-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">المركز / المستشفى</label>
                    <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={facilityInput} onChange={e => setFacilityInput(e.target.value)} placeholder="اسم المركز" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">الصور (يمكن اختيار أكثر من صورة)</label>
                    <input type="file" multiple accept=".jpg,.jpeg,.png,.dcm,.tiff,.tif"
                      className="w-full text-sm text-gray-600 file:ml-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-medium file:bg-blue-50 file:text-blue-700"
                      onChange={e => setImageFiles([...e.target.files])} />
                    {imageFiles.length > 0 && <p className="text-xs text-gray-500 mt-1">{imageFiles.length} ملف محدد</p>}
                  </div>
                </div>
                <div className="flex gap-3 justify-end mt-4">
                  <button onClick={() => setActionModal(null)} className="px-4 py-2 text-sm text-gray-600">إلغاء</button>
                  <button onClick={handleUploadImages} disabled={busy} className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg text-sm disabled:opacity-60">
                    {busy ? '...' : 'رفع الصور'}
                  </button>
                </div>
              </>
            )}

            {/* رفع التقرير */}
            {actionModal.type === 'report' && (
              <>
                <h3 className="font-bold text-gray-800 mb-1">رفع تقرير الأشعة</h3>
                <p className="text-sm text-gray-500 mb-4">{SCAN_TYPES[actionModal.request.scan_type]} — {actionModal.request.body_part}</p>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">المركز</label>
                      <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                        value={reportForm.facility} onChange={e => setReportForm(f=>({...f,facility:e.target.value}))} />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">الطبيب الشعاعي</label>
                      <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                        value={reportForm.radiologist_name} onChange={e => setReportForm(f=>({...f,radiologist_name:e.target.value}))} />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">النتائج (Findings)</label>
                    <textarea rows={3} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                      value={reportForm.findings} onChange={e => setReportForm(f=>({...f,findings:e.target.value}))} />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">التفسير النهائي (Impression)</label>
                    <textarea rows={2} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                      value={reportForm.impression} onChange={e => setReportForm(f=>({...f,impression:e.target.value}))} />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">التوصيات</label>
                    <textarea rows={2} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                      value={reportForm.recommendation} onChange={e => setReportForm(f=>({...f,recommendation:e.target.value}))} />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-600 mb-1">ملف التقرير (اختياري)</label>
                    <input type="file" accept=".pdf,.jpg,.jpeg,.png"
                      className="w-full text-sm text-gray-600 file:ml-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-medium file:bg-purple-50 file:text-purple-700"
                      onChange={e => setReportFile(e.target.files[0])} />
                  </div>
                </div>
                <div className="flex gap-3 justify-end mt-4">
                  <button onClick={() => setActionModal(null)} className="px-4 py-2 text-sm text-gray-600">إلغاء</button>
                  <button onClick={handleUploadReport} disabled={busy} className="bg-purple-600 hover:bg-purple-700 text-white px-5 py-2 rounded-lg text-sm disabled:opacity-60">
                    {busy ? '...' : 'رفع التقرير'}
                  </button>
                </div>
              </>
            )}

            {/* رفض */}
            {actionModal.type === 'reject' && (
              <>
                <h3 className="font-bold text-gray-800 mb-1">رفض الطلب</h3>
                <p className="text-sm text-gray-500 mb-4">{SCAN_TYPES[actionModal.request.scan_type]} — {actionModal.request.body_part}</p>
                <label className="block text-sm font-medium text-gray-700 mb-1">سبب الرفض</label>
                <textarea rows={3} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-red-500"
                  value={rejectReason} onChange={e => setRejectReason(e.target.value)} />
                <div className="flex gap-3 justify-end">
                  <button onClick={() => setActionModal(null)} className="px-4 py-2 text-sm text-gray-600">إلغاء</button>
                  <button onClick={handleReject} disabled={busy} className="bg-red-500 hover:bg-red-600 text-white px-5 py-2 rounded-lg text-sm disabled:opacity-60">
                    {busy ? '...' : 'رفض الطلب'}
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
