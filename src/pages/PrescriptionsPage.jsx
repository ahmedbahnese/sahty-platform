import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  FileText, Plus, Send, CheckCircle, XCircle, Clock,
  Pill, RefreshCw, ChevronDown, User, Stethoscope,
  Calendar, AlertCircle, Trash2
} from 'lucide-react'

const API = '/api'

const STATUS_CONFIG = {
  active:            { label: 'نشطة',             color: 'bg-emerald-100 text-emerald-700', icon: CheckCircle },
  sent_to_pharmacy:  { label: 'أُرسلت للصيدلية',  color: 'bg-blue-100 text-blue-700',      icon: Send },
  dispensed:         { label: 'تم الصرف',          color: 'bg-purple-100 text-purple-700',  icon: CheckCircle },
  cancelled:         { label: 'ملغاة',             color: 'bg-red-100 text-red-700',        icon: XCircle },
}

const DRUG_FORMS = ['أقراص', 'كبسولات', 'شراب', 'حقن', 'كريم', 'قطرات', 'بخاخ', 'أخرى']
const FREQUENCIES = ['مرة يومياً', 'مرتان يومياً', 'ثلاث مرات يومياً', 'كل 8 ساعات', 'كل 6 ساعات', 'عند الحاجة', 'أسبوعياً']

function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.active
  const Icon = cfg.icon
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${cfg.color}`}>
      <Icon className="w-3 h-3" />
      {cfg.label}
    </span>
  )
}

function PrescriptionCard({ rx, onAction, userType }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="rounded-2xl border bg-white shadow-sm border-gray-100">
      <div className="p-5">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
          <div className="flex items-start gap-3">
            <div className="w-12 h-12 rounded-xl bg-purple-600 flex items-center justify-center shrink-0">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div>
              {userType === 'patient' ? (
                <p className="font-semibold text-gray-900">{rx.doctor?.name || 'طبيب'}</p>
              ) : userType === 'doctor' ? (
                <p className="font-semibold text-gray-900">{rx.patient?.name || 'مريض'}</p>
              ) : (
                <p className="font-semibold text-gray-900">وصفة #{rx.id}</p>
              )}
              <p className="text-sm text-gray-500">
                {userType === 'patient' ? rx.doctor?.specialization : rx.patient?.phone || ''}
              </p>
              <div className="flex flex-wrap items-center gap-3 mt-1.5 text-sm text-gray-600">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5" />
                  {new Date(rx.created_at).toLocaleDateString('ar-EG', { year: 'numeric', month: 'long', day: 'numeric' })}
                </span>
                <span className="flex items-center gap-1">
                  <Pill className="w-3.5 h-3.5" />
                  {rx.items?.length || 0} {rx.items?.length === 1 ? 'دواء' : 'أدوية'}
                </span>
                {rx.valid_until && (
                  <span className="text-xs bg-gray-100 px-2 py-0.5 rounded-md">
                    صالحة حتى: {new Date(rx.valid_until).toLocaleDateString('ar-EG')}
                  </span>
                )}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <StatusBadge status={rx.status} />
            <button onClick={() => setExpanded(e => !e)} className="text-gray-400 hover:text-gray-600 p-1">
              <ChevronDown className={`w-4 h-4 transition-transform ${expanded ? 'rotate-180' : ''}`} />
            </button>
          </div>
        </div>

        {expanded && (
          <div className="mt-4 pt-4 border-t border-gray-50">
            {rx.diagnosis && (
              <p className="text-sm text-gray-600 mb-3"><span className="font-medium">التشخيص:</span> {rx.diagnosis}</p>
            )}
            {rx.notes && (
              <p className="text-sm text-gray-600 mb-3"><span className="font-medium">ملاحظات:</span> {rx.notes}</p>
            )}
            {rx.pharmacy_name && (
              <p className="text-sm text-gray-600 mb-3"><span className="font-medium">الصيدلية:</span> {rx.pharmacy_name}</p>
            )}
            {rx.dispensed_at && (
              <p className="text-sm text-gray-600 mb-3">
                <span className="font-medium">تاريخ الصرف:</span> {new Date(rx.dispensed_at).toLocaleString('ar-EG')}
                {rx.dispensed_by && ` — ${rx.dispensed_by}`}
              </p>
            )}
            {/* الأدوية */}
            <div className="space-y-2 mt-3">
              <p className="text-sm font-semibold text-gray-800">الأدوية الموصوفة:</p>
              {rx.items?.map((item, i) => (
                <div key={item.id} className="bg-gray-50 rounded-xl p-3">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="font-medium text-gray-900 text-sm">{item.drug_name}</p>
                      {item.generic_name && <p className="text-xs text-gray-500">{item.generic_name}</p>}
                    </div>
                    <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-md shrink-0">{item.form || ''}</span>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-2 text-xs text-gray-600">
                    <span className="bg-white border rounded-md px-2 py-0.5">الجرعة: {item.dosage}</span>
                    <span className="bg-white border rounded-md px-2 py-0.5">التكرار: {item.frequency}</span>
                    {item.duration && <span className="bg-white border rounded-md px-2 py-0.5">المدة: {item.duration}</span>}
                    {item.quantity && <span className="bg-white border rounded-md px-2 py-0.5">الكمية: {item.quantity}</span>}
                  </div>
                  {item.instructions && <p className="text-xs text-gray-500 mt-1.5 italic">{item.instructions}</p>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* أزرار الإجراءات */}
        <div className="mt-4 flex flex-wrap gap-2">
          {userType === 'doctor' && rx.status === 'active' && (
            <>
              <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-1.5"
                onClick={() => onAction('send', rx)}>
                <Send className="w-3.5 h-3.5" /> إرسال للصيدلية
              </Button>
              <Button size="sm" variant="outline" className="text-red-600 border-red-200 hover:bg-red-50"
                onClick={() => onAction('cancel', rx)}>إلغاء الوصفة</Button>
            </>
          )}
          {userType === 'doctor' && rx.status === 'sent_to_pharmacy' && (
            <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700 text-white flex items-center gap-1.5"
              onClick={() => onAction('dispense', rx)}>
              <CheckCircle className="w-3.5 h-3.5" /> تأكيد الصرف
            </Button>
          )}
          {userType === 'pharmacy' && rx.status === 'sent_to_pharmacy' && (
            <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700 text-white flex items-center gap-1.5"
              onClick={() => onAction('dispense', rx)}>
              <CheckCircle className="w-3.5 h-3.5" /> تأكيد الصرف
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}

// ── نموذج إنشاء وصفة ──────────────────────────────
function CreatePrescriptionModal({ onClose, onCreated, token }) {
  const [patients, setPatients] = useState([])
  const [form, setForm] = useState({ patient_id: '', diagnosis: '', notes: '', valid_until: '' })
  const [items, setItems] = useState([{ drug_name: '', generic_name: '', dosage: '', form: '', frequency: '', duration: '', quantity: '', instructions: '' }])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch(`${API}/auth/patients`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(d => setPatients(d.patients || []))
      .catch(() => {})
  }, [token])

  const setField = (k, v) => setForm(f => ({ ...f, [k]: v }))
  const setItem  = (i, k, v) => setItems(prev => prev.map((it, idx) => idx === i ? { ...it, [k]: v } : it))
  const addItem  = () => setItems(prev => [...prev, { drug_name: '', generic_name: '', dosage: '', form: '', frequency: '', duration: '', quantity: '', instructions: '' }])
  const removeItem = (i) => { if (items.length > 1) setItems(prev => prev.filter((_, idx) => idx !== i)) }

  const submit = async () => {
    if (!form.patient_id) { setError('يرجى اختيار المريض'); return }
    const validItems = items.filter(it => it.drug_name && it.dosage && it.frequency)
    if (validItems.length === 0) { setError('يرجى إضافة دواء واحد على الأقل بجميع الحقول المطلوبة'); return }
    setLoading(true); setError('')
    try {
      const res = await fetch(`${API}/prescriptions`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, patient_id: parseInt(form.patient_id), items: validItems })
      })
      const data = await res.json()
      if (res.ok) onCreated(data.prescription)
      else setError(data.message || 'حدث خطأ')
    } finally { setLoading(false) }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-start justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl my-8" dir="rtl">
        <div className="p-6 border-b sticky top-0 bg-white rounded-t-2xl z-10">
          <h2 className="text-xl font-bold text-gray-900">وصفة طبية جديدة</h2>
        </div>
        <div className="p-6 space-y-5">
          {error && <div className="bg-red-50 text-red-600 rounded-xl p-3 text-sm">{error}</div>}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">المريض *</label>
              <select value={form.patient_id} onChange={e => setField('patient_id', e.target.value)}
                className="w-full border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500">
                <option value="">اختر مريضاً…</option>
                {patients.map(p => (
                  <option key={p.id} value={p.id}>{p.first_name} {p.last_name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">صالحة حتى</label>
              <input type="date" value={form.valid_until} onChange={e => setField('valid_until', e.target.value)}
                min={new Date().toISOString().split('T')[0]}
                className="w-full border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">التشخيص</label>
            <Input value={form.diagnosis} onChange={e => setField('diagnosis', e.target.value)} placeholder="التشخيص الطبي…" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات</label>
            <textarea value={form.notes} onChange={e => setField('notes', e.target.value)}
              className="w-full border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
              rows={2} placeholder="ملاحظات إضافية…" />
          </div>

          {/* الأدوية */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="text-sm font-semibold text-gray-800">الأدوية *</label>
              <Button size="sm" variant="outline" onClick={addItem} className="flex items-center gap-1 text-xs">
                <Plus className="w-3.5 h-3.5" /> إضافة دواء
              </Button>
            </div>
            <div className="space-y-4">
              {items.map((item, i) => (
                <div key={i} className="border rounded-xl p-4 bg-gray-50">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-medium text-gray-700">دواء {i + 1}</span>
                    {items.length > 1 && (
                      <button onClick={() => removeItem(i)} className="text-red-400 hover:text-red-600 p-1">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="text-xs text-gray-600 mb-1 block">اسم الدواء *</label>
                      <Input value={item.drug_name} onChange={e => setItem(i, 'drug_name', e.target.value)} placeholder="اسم الدواء التجاري" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-600 mb-1 block">الاسم العلمي</label>
                      <Input value={item.generic_name} onChange={e => setItem(i, 'generic_name', e.target.value)} placeholder="الاسم العلمي (اختياري)" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-600 mb-1 block">الجرعة *</label>
                      <Input value={item.dosage} onChange={e => setItem(i, 'dosage', e.target.value)} placeholder="مثال: 500 مجم" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-600 mb-1 block">الشكل الدوائي</label>
                      <select value={item.form} onChange={e => setItem(i, 'form', e.target.value)}
                        className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white">
                        <option value="">اختر…</option>
                        {DRUG_FORMS.map(f => <option key={f} value={f}>{f}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-gray-600 mb-1 block">تكرار الجرعة *</label>
                      <select value={item.frequency} onChange={e => setItem(i, 'frequency', e.target.value)}
                        className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white">
                        <option value="">اختر…</option>
                        {FREQUENCIES.map(f => <option key={f} value={f}>{f}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-gray-600 mb-1 block">مدة العلاج</label>
                      <Input value={item.duration} onChange={e => setItem(i, 'duration', e.target.value)} placeholder="مثال: 7 أيام" />
                    </div>
                    <div>
                      <label className="text-xs text-gray-600 mb-1 block">الكمية</label>
                      <Input value={item.quantity} onChange={e => setItem(i, 'quantity', e.target.value)} placeholder="مثال: 20 قرص" />
                    </div>
                    <div className="sm:col-span-2">
                      <label className="text-xs text-gray-600 mb-1 block">تعليمات خاصة</label>
                      <Input value={item.instructions} onChange={e => setItem(i, 'instructions', e.target.value)} placeholder="مثال: تؤخذ بعد الأكل" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        <div className="p-6 border-t flex gap-3 justify-end sticky bottom-0 bg-white rounded-b-2xl">
          <Button variant="outline" onClick={onClose}>إلغاء</Button>
          <Button onClick={submit} disabled={loading} className="bg-purple-600 hover:bg-purple-700 text-white">
            {loading ? 'جاري الإنشاء…' : 'إنشاء الوصفة'}
          </Button>
        </div>
      </div>
    </div>
  )
}

function SendPharmacyModal({ rx, onClose, onSent, token }) {
  const [pharmacyName, setPharmacyName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const submit = async () => {
    setLoading(true); setError('')
    try {
      const res = await fetch(`${API}/prescriptions/${rx.id}/send-pharmacy`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ pharmacy_name: pharmacyName || 'الصيدلية' })
      })
      const data = await res.json()
      if (res.ok) onSent(data.prescription)
      else setError(data.message || 'حدث خطأ')
    } finally { setLoading(false) }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm" dir="rtl">
        <div className="p-6 border-b">
          <h2 className="text-xl font-bold text-gray-900">إرسال إلى الصيدلية</h2>
        </div>
        <div className="p-6 space-y-4">
          {error && <div className="bg-red-50 text-red-600 rounded-xl p-3 text-sm">{error}</div>}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">اسم الصيدلية</label>
            <Input value={pharmacyName} onChange={e => setPharmacyName(e.target.value)} placeholder="اسم الصيدلية (اختياري)" />
          </div>
          <p className="text-sm text-gray-500">سيتم إرسال الوصفة إلى الصيدلية المحددة لصرفها للمريض.</p>
        </div>
        <div className="p-6 border-t flex gap-3 justify-end">
          <Button variant="outline" onClick={onClose}>إلغاء</Button>
          <Button onClick={submit} disabled={loading} className="bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-1.5">
            <Send className="w-3.5 h-3.5" />
            {loading ? 'جاري الإرسال…' : 'إرسال'}
          </Button>
        </div>
      </div>
    </div>
  )
}

export default function PrescriptionsPage() {
  const { user, token, isPatient, isDoctor, isProvider } = useAuth()
  const isPharmacy = user?.user_type === 'pharmacy'

  const [prescriptions, setPrescriptions] = useState([])
  const [loading, setLoading]             = useState(true)
  const [activeTab, setActiveTab]         = useState('all')
  const [modal, setModal]                 = useState(null) // { type, rx? }
  const [toast, setToast]                 = useState('')

  const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(''), 3000) }

  const fetchPrescriptions = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API}/prescriptions`, { headers: { Authorization: `Bearer ${token}` } })
      const data = await res.json()
      setPrescriptions(data.prescriptions || [])
    } finally { setLoading(false) }
  }, [token])

  useEffect(() => { fetchPrescriptions() }, [fetchPrescriptions])

  const updateRx = (updated) => {
    setPrescriptions(prev => prev.map(rx => rx.id === updated.id ? updated : rx))
    setModal(null)
  }

  const handleAction = async (type, rx) => {
    if (type === 'send') { setModal({ type: 'send', rx }); return }
    if (type === 'cancel') {
      if (!window.confirm('هل تريد إلغاء هذه الوصفة؟')) return
      const res = await fetch(`${API}/prescriptions/${rx.id}/cancel`, {
        method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
      })
      if (res.ok) { updateRx({ ...rx, status: 'cancelled' }); showToast('تم إلغاء الوصفة') }
      return
    }
    if (type === 'dispense') {
      const dispensedBy = window.prompt('اسم الصيدلي / الصيدلية:', user?.profile?.legal_name || 'الصيدلية') || 'الصيدلية'
      const res = await fetch(`${API}/prescriptions/${rx.id}/dispense`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ dispensed_by: dispensedBy })
      })
      const data = await res.json()
      if (res.ok) { updateRx(data.prescription); showToast('تم تأكيد صرف الوصفة ✓') }
      return
    }
  }

  const userType = isDoctor ? 'doctor' : isPharmacy ? 'pharmacy' : 'patient'

  const tabs = isDoctor
    ? [
        { key: 'all',           label: 'جميع الوصفات' },
        { key: 'active',        label: 'نشطة' },
        { key: 'sent_to_pharmacy', label: 'أُرسلت للصيدلية' },
        { key: 'dispensed',     label: 'تم الصرف' },
      ]
    : isPharmacy
    ? [
        { key: 'sent_to_pharmacy', label: 'وصفات للصرف' },
        { key: 'dispensed',        label: 'تم الصرف' },
      ]
    : [
        { key: 'all',       label: 'جميع الوصفات' },
        { key: 'active',    label: 'نشطة' },
        { key: 'dispensed', label: 'تم الصرف' },
      ]

  const filtered = activeTab === 'all'
    ? prescriptions
    : prescriptions.filter(rx => rx.status === activeTab)

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      {/* هيدر */}
      <div className="bg-gradient-to-l from-purple-700 to-violet-600 text-white">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">الوصفات الدوائية</h1>
              <p className="text-purple-100 mt-1 text-sm">
                {isDoctor ? 'إدارة وصفاتك الطبية' : isPharmacy ? 'وصفات للصرف' : 'وصفاتك الطبية'}
              </p>
            </div>
            {isDoctor && (
              <Button onClick={() => setModal({ type: 'create' })}
                className="bg-white text-purple-700 hover:bg-purple-50 font-semibold flex items-center gap-2">
                <Plus className="w-4 h-4" /> وصفة جديدة
              </Button>
            )}
          </div>

          {/* إحصائيات */}
          <div className="grid grid-cols-4 gap-3 mt-6">
            {[
              { label: 'الكل',           value: prescriptions.length,                                        key: 'all' },
              { label: 'نشطة',           value: prescriptions.filter(r => r.status === 'active').length,    key: 'active' },
              { label: 'بالصيدلية',     value: prescriptions.filter(r => r.status === 'sent_to_pharmacy').length, key: 'sent' },
              { label: 'تم الصرف',     value: prescriptions.filter(r => r.status === 'dispensed').length,  key: 'dispensed' },
            ].map(s => (
              <div key={s.key} className="bg-white/10 rounded-xl p-3 text-center">
                <p className="text-2xl font-bold text-white">{s.value}</p>
                <p className="text-xs mt-0.5 text-purple-200">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* المحتوى */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* تابز */}
        <div className="flex gap-1 bg-white rounded-xl p-1 shadow-sm border border-gray-100 mb-6 overflow-x-auto">
          {tabs.map(t => (
            <button key={t.key} onClick={() => setActiveTab(t.key)}
              className={`flex-1 min-w-fit px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${activeTab === t.key ? 'bg-purple-600 text-white shadow-sm' : 'text-gray-600 hover:bg-gray-50'}`}>
              {t.label}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <RefreshCw className="w-8 h-8 text-purple-400 animate-spin" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-20">
            <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 font-medium">لا توجد وصفات</p>
            {isDoctor && (
              <Button onClick={() => setModal({ type: 'create' })} className="mt-4 bg-purple-600 hover:bg-purple-700 text-white">
                أنشئ وصفة الآن
              </Button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {filtered.map(rx => (
              <PrescriptionCard key={rx.id} rx={rx} onAction={handleAction} userType={userType} />
            ))}
          </div>
        )}
      </div>

      {/* نوافذ */}
      {modal?.type === 'create' && (
        <CreatePrescriptionModal token={token} onClose={() => setModal(null)}
          onCreated={rx => { setPrescriptions(prev => [rx, ...prev]); setModal(null); showToast('تم إنشاء الوصفة ✓') }} />
      )}
      {modal?.type === 'send' && (
        <SendPharmacyModal token={token} rx={modal.rx} onClose={() => setModal(null)}
          onSent={rx => { updateRx(rx); showToast('تم إرسال الوصفة للصيدلية ✓') }} />
      )}

      {/* Toast */}
      {toast && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-gray-900 text-white px-6 py-3 rounded-xl shadow-xl text-sm font-medium z-50">
          {toast}
        </div>
      )}
    </div>
  )
}
