import { useState, useEffect, useCallback, useMemo } from 'react'
import { useAuth } from '../contexts/AuthContext'
import {
  Scan, Plus, Upload, Share2, XCircle, ChevronDown, ChevronUp,
  Clock, CheckCircle, AlertTriangle, FileText, Image, Calendar,
  Building2, Paperclip,
} from 'lucide-react'

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

const RADIOLOGY_CENTERS = [
  'مركز الأشعة الطبي المتكامل',
  'مركز إم آر آي للأشعة',
  'مركز بصر للتصوير الطبي',
  'مركز الضوء للأشعة',
  'مستشفى الملك فيصل التخصصي',
  'أخرى',
]

const BODY_PARTS = [
  { code: 'head', label: 'الرأس والمخ' },
  { code: 'chest', label: 'الصدر' },
  { code: 'abdomen', label: 'البطن والحوض' },
  { code: 'spine', label: 'العمود الفقري' },
  { code: 'knee', label: 'الركبة' },
  { code: 'shoulder', label: 'الكتف' },
  { code: 'neck', label: 'الرقبة' },
  { code: 'other', label: 'جزء آخر' },
]

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
  const [radiologyCenters, setRadiologyCenters] = useState([])
  const [editingRequest, setEditingRequest] = useState(null)

  const isAdmin   = ['admin','super_admin','radiology_center'].includes(user?.user_type)
  const isPatient = user?.user_type === 'patient'
  const isDoctor = user?.user_type === 'doctor'
  const doctorLabel = [user?.profile?.first_name, user?.profile?.last_name].filter(Boolean).join(' ') || user?.email || ''
  const [doctorPatients, setDoctorPatients] = useState([])

  const headers = useMemo(() => ({ Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }), [token])

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
  }, [headers])

  useEffect(() => { load() }, [load])
  useEffect(() => {
    if (!isDoctor) return
    fetch('/api/doctors/me/patients', { headers: { Authorization: `Bearer ${token}` } })
      .then(res => res.ok ? res.json() : null)
      .then(data => setDoctorPatients(data?.patients || []))
      .catch(() => setDoctorPatients([]))
  }, [isDoctor, token])
  useEffect(() => {
    fetch('/api/facilities?type=radiology&per_page=100')
      .then(res => res.ok ? res.json() : null)
      .then(data => setRadiologyCenters(data?.facilities || []))
      .catch(() => setRadiologyCenters([]))
  }, [])

  const filtered = requests.filter(r => tab === 'all' || r.status === tab)

  // ── نموذج الطلب الجديد ──────────────────────────────────
  const [form, setForm] = useState({
    scan_type: 'xray', body_part: '', body_part_code: '', urgency: 'routine',
    clinical_reason: '', ordering_doctor: doctorLabel, patient_id: '',
    radiology_center_name: '', scheduled_datetime: '',
    patient_weight: '', requires_sedation: false, uses_contrast: false,
    preparation_required: false,
  })
  const [requestDoc, setRequestDoc] = useState(null)
  const [preparationChecklist, setPreparationChecklist] = useState([])
  const [preparationNotes, setPreparationNotes] = useState('')

  const submitRequest = async e => {
    e.preventDefault()
    if (!isPatient && !form.patient_id) { showToast('يجب تحديد المريض من قائمة مرضاك', 'error'); return }
    if (isDoctor) form.ordering_doctor = doctorLabel
    setBusy(true)
    try {
      const fd = new FormData()
      Object.entries(form).forEach(([k, v]) => {
        if (typeof v === 'boolean') fd.append(k, v ? 'true' : 'false')
        else if (v) fd.append(k, v)
      })
      if (isPatient) fd.delete('patient_id')
      if (requestDoc) fd.append('request_doc', requestDoc)
      fd.append('preparation_checklist', JSON.stringify(preparationChecklist))
      if (preparationNotes) fd.append('clinical_reason', `${form.clinical_reason || ''}\n${preparationNotes}`.trim())

      const res = editingRequest
        ? await fetch(`${API}/radiology-requests/${editingRequest.id}`, {
            method: 'PUT', headers,
            body: JSON.stringify({ ...form, preparation_checklist: preparationChecklist }),
          })
        : await fetch(`${API}/radiology-requests`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${token}` },
            body: fd,
          })
      const data = await res.json()
      if (res.ok) {
        showToast(editingRequest ? 'تم تعديل طلب الأشعة' : 'تم إرسال طلب الأشعة بنجاح')
        setShowForm(false)
        setForm({ scan_type:'xray', body_part:'', body_part_code:'', urgency:'routine', clinical_reason:'', ordering_doctor: doctorLabel, patient_id:'', radiology_center_name:'', scheduled_datetime:'', patient_weight:'', requires_sedation:false, uses_contrast:false, preparation_required:false })
        setRequestDoc(null)
        setPreparationChecklist([])
        setPreparationNotes('')
        setEditingRequest(null)
        load()
      } else showToast(data.message || 'حدث خطأ', 'error')
    } finally { setBusy(false) }
  }

  const startEdit = req => {
    setEditingRequest(req)
    setForm({
      scan_type: req.scan_type || 'xray',
      body_part: req.body_part || '',
      body_part_code: req.body_part_code || '',
      urgency: req.urgency || 'routine',
      clinical_reason: req.clinical_reason || '',
      ordering_doctor: req.ordering_doctor || '',
      patient_id: req.patient_id || '',
      radiology_center_name: req.radiology_center_name || '',
      scheduled_datetime: req.scheduled_datetime?.slice(0, 16) || '',
      patient_weight: req.patient_weight || '',
      requires_sedation: !!req.requires_sedation,
      uses_contrast: !!req.uses_contrast,
      preparation_required: !!req.preparation_required,
    })
    setPreparationChecklist(req.preparation_checklist || [])
    setShowForm(true)
  }

  const deleteRequest = async req => {
    if (!window.confirm('هل تريد حذف طلب الأشعة؟')) return
    const res = await fetch(`${API}/radiology-requests/${req.id}`, {
      method: 'DELETE', headers: { Authorization: `Bearer ${token}` },
    })
    const data = await res.json()
    if (res.ok) { showToast('تم حذف الطلب'); load() }
    else showToast(data.message || 'لا يمكن حذف الطلب', 'error')
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
      if (res.ok) { showToast('تم مشاركة النتائج وحفظها في السجل الطبي'); load() }
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
    const cfg = {
      emergency: 'bg-red-200 text-red-800',
      urgent:    'bg-red-100 text-red-700',
      routine:   'bg-gray-100 text-gray-600',
    }
    const lbl = { emergency: 'طارئ', urgent: 'عاجل', routine: 'روتيني' }
    return <span className={`text-xs px-2 py-0.5 rounded-full ${cfg[urgency] || cfg.routine}`}>{lbl[urgency] || urgency}</span>
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
          <h2 className="font-semibold text-gray-800 mb-4">{editingRequest ? 'تعديل طلب الأشعة' : 'طلب أشعة جديد'}</h2>
          <form onSubmit={submitRequest} className="grid grid-cols-1 md:grid-cols-2 gap-4">

            {/* نوع الأشعة */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">نوع الأشعة *</label>
              <select required className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={form.scan_type} onChange={e => setForm(f=>({...f,scan_type:e.target.value}))}>
                {Object.entries(SCAN_TYPES).map(([v,l]) => <option key={v} value={v}>{l}</option>)}
              </select>
            </div>

            {/* الجزء المصوَّر */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الجزء المصوَّر *</label>
              <div className="flex gap-2">
                <select required value={form.body_part_code}
                  onChange={e => setForm(f => ({
                    ...f,
                    body_part_code: e.target.value,
                    body_part: BODY_PARTS.find(p => p.code === e.target.value)?.label || '',
                  }))}
                  className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                  <option value="">اختر الجزء</option>
                  {BODY_PARTS.map(part => <option key={part.code} value={part.code}>{part.label}</option>)}
                </select>
                <input required className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  value={form.body_part} onChange={e=>setForm(f=>({...f,body_part:e.target.value}))} placeholder="أو اكتب يدوياً" />
              </div>
            </div>

            {/* الأولوية */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الأولوية</label>
              <select className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={form.urgency} onChange={e => setForm(f=>({...f,urgency:e.target.value}))}>
                <option value="routine">روتيني</option>
                <option value="urgent">عاجل</option>
                <option value="emergency">طارئ</option>
              </select>
            </div>

            {/* مركز الأشعة */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1"><Building2 size={13}/> مركز الأشعة</label>
              <select className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={form.radiology_center_name} onChange={e => setForm(f=>({...f,radiology_center_name:e.target.value}))}>
                <option value="">-- اختر مركز --</option>
                {radiologyCenters.map(c => <option key={c.id} value={c.name_ar}>{c.name_ar}</option>)}
              </select>
              {!radiologyCenters.length && <p className="text-xs text-amber-700 mt-1">لا توجد مراكز أشعة متاحة في الدليل حالياً.</p>}
            </div>

            {/* موعد الفحص */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1"><Calendar size={13}/> موعد الفحص</label>
              <input type="datetime-local" className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={form.scheduled_datetime} onChange={e => setForm(f=>({...f,scheduled_datetime:e.target.value}))} />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">وزن المريض (كجم)</label>
              <input type="number" min="0" step="0.1" value={form.patient_weight}
                onChange={e => setForm(f => ({ ...f, patient_weight: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>

            {/* الطبيب الآمر */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">الطبيب الآمر</label>
              <input readOnly={isDoctor} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={form.ordering_doctor} onChange={e => setForm(f=>({...f,ordering_doctor:e.target.value}))} placeholder="اسم الطبيب" />
            </div>

            {!isPatient && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">المريض *</label>
                {isDoctor ? <select required value={form.patient_id} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" onChange={e => setForm(f => ({...f, patient_id: e.target.value}))}><option value="">-- اختر مريضًا من مرضاك --</option>{doctorPatients.map(patient => <option key={patient.id} value={patient.id}>{patient.full_name} · {patient.medical_number} · {patient.phone}</option>)}</select> : <input required type="number" className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" value={form.patient_id} onChange={e=>setForm(f=>({...f,patient_id:e.target.value}))} />}
              </div>
            )}

            <div className="md:col-span-2 grid md:grid-cols-3 gap-3 rounded-xl bg-purple-50 border border-purple-100 p-4">
              {[
                ['requires_sedation', 'الفحص يحتاج تخديراً'],
                ['uses_contrast', 'الفحص بصبغة'],
                ['preparation_required', 'يحتاج تحضيراً'],
              ].map(([key, label]) => (
                <label key={key} className="flex items-center gap-2 text-sm text-purple-900 cursor-pointer">
                  <input type="checkbox" checked={form[key]}
                    onChange={e => setForm(f => ({ ...f, [key]: e.target.checked }))}
                    className="accent-purple-600" />
                  {label}
                </label>
              ))}
            </div>

            {form.preparation_required && (
              <div className="md:col-span-2 rounded-xl border border-amber-200 bg-amber-50 p-4">
                <label className="block text-sm font-medium text-amber-900 mb-2">قائمة تحضير المريض</label>
                <div className="grid md:grid-cols-2 gap-2">
                  {[
                    'الصيام حسب تعليمات المركز',
                    'إزالة المعادن والمجوهرات',
                    'إحضار التحاليل السابقة',
                    'إبلاغ المركز بالحساسية من الصبغة',
                  ].map(item => (
                    <label key={item} className="flex items-center gap-2 text-sm text-amber-800">
                      <input type="checkbox" checked={preparationChecklist.includes(item)}
                        onChange={e => setPreparationChecklist(items => e.target.checked
                          ? [...items, item] : items.filter(x => x !== item))}
                        className="accent-amber-600" />
                      {item}
                    </label>
                  ))}
                </div>
                <textarea rows={2} value={preparationNotes}
                  onChange={e => setPreparationNotes(e.target.value)}
                  placeholder="تعليمات تحضير إضافية..."
                  className="mt-3 w-full border border-amber-200 rounded-lg px-3 py-2 text-sm" />
              </div>
            )}

            {/* السبب السريري */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">السبب السريري</label>
              <textarea rows={2} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={form.clinical_reason} onChange={e => setForm(f=>({...f,clinical_reason:e.target.value}))} placeholder="سبب طلب الأشعة..." />
            </div>

            {/* رفع وثيقة الطلب */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
                <Paperclip size={13}/> وثيقة الطلب الأصلي (PDF أو صورة — اختياري)
              </label>
              <input type="file" accept=".pdf,.jpg,.jpeg,.png"
                onChange={e => setRequestDoc(e.target.files[0])}
                className="w-full text-sm text-gray-500 file:ml-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100" />
              {requestDoc && <p className="text-xs text-indigo-600 mt-1">✓ {requestDoc.name}</p>}
            </div>

            <div className="md:col-span-2 flex gap-3 justify-end">
              <button type="button" onClick={() => { setShowForm(false); setEditingRequest(null) }} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800">إلغاء</button>
              <button type="submit" disabled={busy} className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg text-sm font-medium disabled:opacity-60">
                {busy ? 'جاري الحفظ...' : editingRequest ? 'حفظ التعديل' : 'إرسال الطلب'}
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
                    <p className="text-xs text-gray-500">
                      {req.body_part}
                      {req.radiology_center_name && <> · {req.radiology_center_name}</>}
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
                  {isPatient && ['requested', 'rejected'].includes(req.status) && (
                    <div className="flex gap-2 mb-3">
                      <button onClick={() => startEdit(req)} className="rounded-lg bg-blue-50 px-3 py-1.5 text-xs font-medium text-blue-700 hover:bg-blue-100">تعديل الطلب</button>
                      <button onClick={() => deleteRequest(req)} className="rounded-lg bg-red-50 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-100">حذف الطلب</button>
                    </div>
                  )}
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4 text-sm">
                    {req.ordering_doctor && <div><span className="text-gray-500">الطبيب الآمر: </span><span className="font-medium">{req.ordering_doctor}</span></div>}
                    {req.radiology_center_name && <div><span className="text-gray-500">المركز: </span><span className="font-medium">{req.radiology_center_name}</span></div>}
                    {req.facility && req.facility !== req.radiology_center_name && <div><span className="text-gray-500">المرفق: </span><span className="font-medium">{req.facility}</span></div>}
                    {req.radiologist_name && <div><span className="text-gray-500">الطبيب الشعاعي: </span><span className="font-medium">{req.radiologist_name}</span></div>}
                    {req.scheduled_datetime && (
                      <div><span className="text-gray-500">موعد الفحص: </span>
                        <span className="font-medium">{new Date(req.scheduled_datetime).toLocaleString('ar-SA')}</span>
                      </div>
                    )}
                    {req.clinical_reason && <div className="col-span-2"><span className="text-gray-500">السبب: </span><span>{req.clinical_reason}</span></div>}
                    {req.patient_weight && <div><span className="text-gray-500">الوزن: </span><span className="font-medium">{req.patient_weight} كجم</span></div>}
                    {req.requires_sedation && <div className="text-purple-700">يتطلب تخديراً</div>}
                    {req.uses_contrast && <div className="text-purple-700">بصبغة</div>}
                    {req.preparation_checklist?.length > 0 && <div className="col-span-2 text-amber-700">التحضير: {req.preparation_checklist.join('، ')}</div>}
                    {req.rejection_reason && <div className="col-span-2 text-red-600"><span className="font-medium">سبب الرفض: </span>{req.rejection_reason}</div>}
                  </div>

                  {/* وثيقة الطلب الأصلي */}
                  {req.request_doc_path && (
                    <div className="bg-indigo-50 rounded-xl border border-indigo-100 p-3 mb-3 flex items-center gap-2">
                      <Paperclip size={14} className="text-indigo-600" />
                      <a href={`/api/uploads/radiology_request_docs/${req.request_doc_path}`} target="_blank" rel="noopener noreferrer"
                        className="text-sm text-indigo-600 hover:underline font-medium">
                        {req.request_doc_name || 'وثيقة الطلب الأصلي'}
                      </a>
                    </div>
                  )}

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
                          className="inline-flex items-center gap-1 mt-2 text-xs text-indigo-600 hover:underline">
                          <FileText size={12}/> {req.report_file_name}
                        </a>
                      )}
                    </div>
                  )}

                  {/* إجراءات */}
                  <div className="flex flex-wrap gap-2 mt-2">
                    {isAdmin && req.status === 'requested' && (
                      <>
                        <button onClick={() => { setActionModal({ type:'images', request:req }); setImageFiles([]); setFacilityInput('') }}
                          className="flex items-center gap-1 bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 px-3 py-1.5 rounded-lg text-xs font-medium">
                          <Upload size={13}/> رفع صور
                        </button>
                        <button onClick={() => { setActionModal({ type:'reject', request:req }); setRejectReason('') }}
                          className="flex items-center gap-1 bg-red-50 text-red-700 border border-red-200 hover:bg-red-100 px-3 py-1.5 rounded-lg text-xs font-medium">
                          <XCircle size={13}/> رفض
                        </button>
                      </>
                    )}
                    {isAdmin && req.status === 'images_uploaded' && (
                      <button onClick={() => { setActionModal({ type:'report', request:req }); setReportForm({facility:'',radiologist_name:'',findings:'',impression:'',recommendation:''}); setReportFile(null) }}
                        className="flex items-center gap-1 bg-purple-50 text-purple-700 border border-purple-200 hover:bg-purple-100 px-3 py-1.5 rounded-lg text-xs font-medium">
                        <FileText size={13}/> رفع تقرير
                      </button>
                    )}
                    {isAdmin && req.status === 'report_uploaded' && (
                      <button onClick={() => handleShare(req)} disabled={busy}
                        className="flex items-center gap-1 bg-green-50 text-green-700 border border-green-200 hover:bg-green-100 px-3 py-1.5 rounded-lg text-xs font-medium disabled:opacity-60">
                        <Share2 size={13}/> مشاركة وحفظ في السجل الطبي
                      </button>
                    )}
                    {req.shared_at && (
                      <span className="text-xs text-gray-400">
                        شورك في {new Date(req.shared_at).toLocaleDateString('ar-SA')}
                      </span>
                    )}
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
            {actionModal.type === 'images' && (
              <>
                <h3 className="font-bold text-gray-900 mb-4">رفع صور الأشعة</h3>
                <div className="mb-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">المرفق / المركز</label>
                  <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                    value={facilityInput} onChange={e => setFacilityInput(e.target.value)} placeholder="اسم المركز" />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">الصور *</label>
                  <input type="file" multiple accept=".jpg,.jpeg,.png,.dcm,.tiff,.tif"
                    onChange={e => setImageFiles(Array.from(e.target.files))}
                    className="w-full text-sm text-gray-500 file:ml-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-sm file:bg-indigo-50 file:text-indigo-700" />
                  {imageFiles.length > 0 && <p className="text-xs text-indigo-600 mt-1">{imageFiles.length} ملف مختار</p>}
                </div>
              </>
            )}
            {actionModal.type === 'report' && (
              <>
                <h3 className="font-bold text-gray-900 mb-4">رفع تقرير الأشعة</h3>
                {['facility','radiologist_name','findings','impression','recommendation'].map(k => {
                  const labels = { facility:'المرفق', radiologist_name:'اسم الطبيب الشعاعي', findings:'النتائج', impression:'التفسير', recommendation:'التوصيات' }
                  const multiline = ['findings','impression','recommendation'].includes(k)
                  return (
                    <div key={k} className="mb-3">
                      <label className="block text-sm font-medium text-gray-700 mb-1">{labels[k]}</label>
                      {multiline
                        ? <textarea rows={2} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
                            value={reportForm[k]} onChange={e => setReportForm(f=>({...f,[k]:e.target.value}))} />
                        : <input className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-indigo-500"
                            value={reportForm[k]} onChange={e => setReportForm(f=>({...f,[k]:e.target.value}))} />
                      }
                    </div>
                  )
                })}
                <div className="mb-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">ملف التقرير (اختياري)</label>
                  <input type="file" accept=".pdf,.jpg,.jpeg,.png"
                    onChange={e => setReportFile(e.target.files[0])}
                    className="w-full text-sm text-gray-500 file:ml-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-sm file:bg-purple-50 file:text-purple-700" />
                </div>
              </>
            )}
            {actionModal.type === 'reject' && (
              <>
                <h3 className="font-bold text-gray-900 mb-4">رفض طلب الأشعة</h3>
                <textarea rows={3} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-red-400 mb-4"
                  value={rejectReason} onChange={e => setRejectReason(e.target.value)} placeholder="سبب الرفض..." />
              </>
            )}
            <div className="flex gap-3 justify-end">
              <button onClick={() => setActionModal(null)} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800">إلغاء</button>
              <button disabled={busy} onClick={
                actionModal.type === 'images' ? handleUploadImages :
                actionModal.type === 'report' ? handleUploadReport :
                handleReject
              }
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-lg text-sm font-medium disabled:opacity-60">
                {busy ? 'جاري...' : 'تأكيد'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
