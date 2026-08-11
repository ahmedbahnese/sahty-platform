/**
 * MedicationOrderPage — طلب أدوية من الصيدلية (Sprint X Feature 3)
 * ثلاثة خيارات:
 *   1. رفع وصفة ورقية (صورة)
 *   2. إدخال يدوي للأدوية
 *   3. اختيار من وصفات الطبيب في المنصة
 */
import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import {
  ShoppingBag, Plus, Upload, FileText, Pill, Building2,
  ChevronDown, ChevronUp, CheckCircle, Clock, XCircle, Trash2,
} from 'lucide-react'

const API = '/api'

const STATUS_CONFIG = {
  pending:   { label: 'قيد الانتظار', color: 'bg-yellow-100 text-yellow-800', icon: Clock },
  confirmed: { label: 'مؤكَّد',       color: 'bg-blue-100 text-blue-800',    icon: CheckCircle },
  dispensed: { label: 'تم الصرف',     color: 'bg-green-100 text-green-800',  icon: CheckCircle },
  cancelled: { label: 'ملغى',         color: 'bg-red-100 text-red-800',      icon: XCircle },
}

const ORDER_TYPES = {
  paper_prescription: { label: 'وصفة ورقية',       icon: Upload },
  manual:             { label: 'إدخال يدوي',       icon: Pill },
  from_prescription:  { label: 'من وصفة المنصة', icon: FileText },
}

const authHeader = () => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`,
})

export default function MedicationOrderPage() {
  const { user } = useAuth()
  const [orders, setOrders] = useState([])
  const [prescriptions, setPrescriptions] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [busy, setBusy] = useState(false)
  const [toast, setToast] = useState(null)
  const [expanded, setExpanded] = useState(null)
  const [tab, setTab] = useState('all')

  // نموذج الطلب
  const [orderType, setOrderType] = useState('manual')
  const [prescriptionImage, setPrescriptionImage] = useState(null)
  const [selectedPrescriptionId, setSelectedPrescriptionId] = useState('')
  const [medications, setMedications] = useState([{ name: '', dosage: '', quantity: '', notes: '' }])
  const [preferredPharmacy, setPreferredPharmacy] = useState('')
  const [pharmacies, setPharmacies] = useState([])
  const [fulfillmentMethod, setFulfillmentMethod] = useState('pickup')
  const [deliveryAddress, setDeliveryAddress] = useState('')
  const [orderNotes, setOrderNotes] = useState('')

  const isPharmacy = ['pharmacy', 'admin', 'super_admin'].includes(user?.user_type)

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3500)
  }

  const load = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API}/pharmacy-orders`, { headers: authHeader() })
      if (res.ok) setOrders(await res.json())
    } finally { setLoading(false) }
  }

  const loadPrescriptions = async () => {
    try {
      const res = await fetch(`${API}/prescriptions`, { headers: authHeader() })
      if (res.ok) {
        const data = await res.json()
        setPrescriptions(Array.isArray(data) ? data : data.prescriptions || [])
      }
    } catch (e) { console.error(e) }
  }

  useEffect(() => { load(); loadPrescriptions() }, [])
  useEffect(() => {
    fetch('/api/facilities?type=pharmacy&per_page=100')
      .then(response => response.ok ? response.json() : null)
      .then(data => setPharmacies(data?.facilities || []))
      .catch(() => setPharmacies([]))
  }, [])

  const filtered = orders.filter(o => tab === 'all' || o.status === tab)

  const addMed = () => setMedications(m => [...m, { name: '', dosage: '', quantity: '', notes: '' }])
  const removeMed = i => setMedications(m => m.filter((_, j) => j !== i))
  const updateMed = (i, field, val) => setMedications(m => m.map((item, j) => j === i ? { ...item, [field]: val } : item))

  const submitOrder = async e => {
    e.preventDefault()
    setBusy(true)
    try {
      const fd = new FormData()
      fd.append('order_type', orderType)
      fd.append('preferred_pharmacy_name', preferredPharmacy)
      const selectedPharmacy = pharmacies.find(item => item.name_ar === preferredPharmacy)
      if (selectedPharmacy?.id) fd.append('preferred_pharmacy_id', selectedPharmacy.id)
      fd.append('fulfillment_method', fulfillmentMethod)
      fd.append('delivery_address', deliveryAddress)
      fd.append('notes', orderNotes)

      if (orderType === 'paper_prescription' && prescriptionImage) {
        fd.append('prescription_image', prescriptionImage)
      } else if (orderType === 'from_prescription' && selectedPrescriptionId) {
        fd.append('source_prescription_id', selectedPrescriptionId)
      }

      const validMeds = medications.filter(m => m.name.trim())
      fd.append('medications_json', JSON.stringify(validMeds))

      const res = await fetch(`${API}/pharmacy-orders`, {
        method: 'POST',
        headers: authHeader(),
        body: fd,
      })
      const data = await res.json()
      if (res.ok) {
        showToast('تم إرسال طلب الدواء بنجاح')
        setShowForm(false)
        setMedications([{ name: '', dosage: '', quantity: '', notes: '' }])
        setPrescriptionImage(null)
        setSelectedPrescriptionId('')
        setPreferredPharmacy('')
        setFulfillmentMethod('pickup')
        setDeliveryAddress('')
        setOrderNotes('')
        setPreferredPharmacy('')
        setOrderNotes('')
        load()
      } else showToast(data.message || 'حدث خطأ', 'error')
    } finally { setBusy(false) }
  }

  const handleAction = async (orderId, action) => {
    setBusy(true)
    try {
      const res = await fetch(`${API}/pharmacy-orders/${orderId}/${action}`, {
        method: 'PUT', headers: { ...authHeader(), 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      })
      const data = await res.json()
      if (res.ok) { showToast('تم التحديث بنجاح'); load() }
      else showToast(data.message || 'حدث خطأ', 'error')
    } finally { setBusy(false) }
  }

  const handleCancel = async (orderId) => {
    if (!confirm('هل تريد إلغاء هذا الطلب؟')) return
    setBusy(true)
    try {
      const res = await fetch(`${API}/pharmacy-orders/${orderId}/cancel`, {
        method: 'PUT', headers: { ...authHeader(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: 'إلغاء من قِبَل المريض' }),
      })
      if (res.ok) { showToast('تم إلغاء الطلب'); load() }
    } finally { setBusy(false) }
  }

  const tabs = [
    { key: 'all', label: 'الكل' },
    { key: 'pending', label: 'قيد الانتظار' },
    { key: 'confirmed', label: 'مؤكَّد' },
    { key: 'dispensed', label: 'تم الصرف' },
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
          <div className="bg-emerald-600 text-white p-2.5 rounded-xl"><ShoppingBag size={22} /></div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">طلب الأدوية من الصيدلية</h1>
            <p className="text-sm text-gray-500">أرسل وصفتك أو اطلب دواءك مباشرة</p>
          </div>
        </div>
        {!isPharmacy && (
          <button onClick={() => setShowForm(v => !v)}
            className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            <Plus size={16} /> طلب جديد
          </button>
        )}
      </div>

      {/* نموذج الطلب */}
      {showForm && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
          <h2 className="font-semibold text-gray-800 mb-5">طلب دواء جديد</h2>
          <form onSubmit={submitOrder} className="space-y-5">

            {/* نوع الطلب */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">طريقة الطلب *</label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {Object.entries(ORDER_TYPES).map(([val, { label, icon: Icon }]) => (
                  <label key={val}
                    className={`flex items-center gap-3 p-3 rounded-xl border-2 cursor-pointer transition-colors
                      ${orderType === val ? 'border-emerald-500 bg-emerald-50' : 'border-gray-200 hover:border-gray-300'}`}>
                    <input type="radio" name="order_type" value={val} checked={orderType === val}
                      onChange={() => setOrderType(val)} className="sr-only" />
                    <Icon size={18} className={orderType === val ? 'text-emerald-600' : 'text-gray-400'} />
                    <span className={`text-sm font-medium ${orderType === val ? 'text-emerald-700' : 'text-gray-700'}`}>{label}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* وصفة ورقية */}
            {orderType === 'paper_prescription' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">صورة الوصفة الطبية (اختياري)</label>
                <input type="file" accept=".jpg,.jpeg,.png,.pdf,.webp"
                  onChange={e => setPrescriptionImage(e.target.files[0])}
                  className="w-full text-sm text-gray-500 file:ml-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-sm file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100" />
                {prescriptionImage && <p className="text-xs text-emerald-600 mt-1">✓ {prescriptionImage.name}</p>}
                <p className="text-xs text-gray-400 mt-1">ارفع صورة واضحة للوصفة الطبية</p>
              </div>
            )}

            {/* وصفة المنصة */}
            {orderType === 'from_prescription' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">اختر الوصفة *</label>
                {prescriptions.length === 0 ? (
                  <p className="text-sm text-gray-400 py-2">لا توجد وصفات متاحة</p>
                ) : (
                  <select required={orderType === 'from_prescription'}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                    value={selectedPrescriptionId} onChange={e => setSelectedPrescriptionId(e.target.value)}>
                    <option value="">-- اختر وصفة --</option>
                    {prescriptions.map(rx => (
                      <option key={rx.id} value={rx.id}>
                        وصفة #{rx.id} — {rx.items?.length || '?'} دواء — {rx.created_at ? new Date(rx.created_at).toLocaleDateString('ar-SA') : ''}
                      </option>
                    ))}
                  </select>
                )}
              </div>
            )}

            {/* قائمة الأدوية (للإدخال اليدوي وعند الرغبة في التعديل) */}
            {(orderType === 'manual' || orderType === 'paper_prescription') && (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700">
                    {orderType === 'paper_prescription' ? 'أدوية الوصفة (اختياري — تُستخرج تلقائياً)' : 'الأدوية المطلوبة *'}
                  </label>
                  <button type="button" onClick={addMed}
                    className="text-xs text-emerald-600 hover:text-emerald-800 flex items-center gap-1">
                    <Plus size={13}/> إضافة دواء
                  </button>
                </div>
                <div className="space-y-2">
                  {medications.map((m, i) => (
                    <div key={i} className="bg-gray-50 rounded-xl p-3 space-y-2">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                        <input className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                          value={m.name} onChange={e => updateMed(i, 'name', e.target.value)} placeholder="اسم الدواء" />
                        <input className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                          value={m.dosage} onChange={e => updateMed(i, 'dosage', e.target.value)} placeholder="الجرعة" />
                        <input className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                          value={m.quantity} onChange={e => updateMed(i, 'quantity', e.target.value)} placeholder="الكمية" />
                        <div className="flex gap-1">
                          <input className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                            value={m.notes} onChange={e => updateMed(i, 'notes', e.target.value)} placeholder="ملاحظات" />
                          {i > 0 && (
                            <button type="button" onClick={() => removeMed(i)}
                              className="p-2 text-red-400 hover:text-red-600"><Trash2 size={15}/></button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* الصيدلية المفضّلة */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center gap-1">
                <Building2 size={13}/> الصيدلية المفضّلة
              </label>
              <select className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                value={preferredPharmacy} onChange={e => setPreferredPharmacy(e.target.value)}>
                <option value="">-- اختر صيدلية --</option>
                {pharmacies.map(p => <option key={p.id} value={p.name_ar}>{p.name_ar}</option>)}
              </select>
              {!pharmacies.length && <p className="text-xs text-amber-700 mt-1">لا توجد صيدليات متاحة في الدليل حالياً.</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">طريقة الاستلام</label>
              <select value={fulfillmentMethod} onChange={e => setFulfillmentMethod(e.target.value)}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500 outline-none">
                <option value="pickup">استلام من الصيدلية</option>
                <option value="delivery">توصيل إلى المنزل</option>
              </select>
            </div>
            {fulfillmentMethod === 'delivery' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">عنوان التوصيل *</label>
                <input required value={deliveryAddress} onChange={e => setDeliveryAddress(e.target.value)}
                  placeholder="العنوان بالتفصيل"
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500 outline-none" />
              </div>
            )}

            {/* ملاحظات */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات</label>
              <textarea rows={2} className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
                value={orderNotes} onChange={e => setOrderNotes(e.target.value)} placeholder="أي معلومات إضافية..." />
            </div>

            <div className="flex gap-3 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800">إلغاء</button>
              <button type="submit" disabled={busy}
                className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-lg text-sm font-medium disabled:opacity-60">
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
              ${tab === t.key ? 'bg-emerald-600 text-white' : 'text-gray-600 hover:bg-gray-50'}`}>
            {t.label}
            <span className={`mr-1.5 text-xs px-1.5 py-0.5 rounded-full
              ${tab === t.key ? 'bg-emerald-500 text-white' : 'bg-gray-100 text-gray-500'}`}>
              {orders.filter(o => t.key === 'all' || o.status === t.key).length}
            </span>
          </button>
        ))}
      </div>

      {/* القائمة */}
      {loading ? (
        <div className="flex justify-center py-16"><div className="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-600" /></div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <ShoppingBag size={40} className="mx-auto mb-3 opacity-40" />
          <p>لا توجد طلبات</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map(order => {
            const cfg = STATUS_CONFIG[order.status] || STATUS_CONFIG.pending
            const Icon = cfg.icon
            const TypeCfg = ORDER_TYPES[order.order_type] || ORDER_TYPES.manual
            const TypeIcon = TypeCfg.icon
            return (
              <div key={order.id} className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50"
                  onClick={() => setExpanded(expanded === order.id ? null : order.id)}>
                  <div className="flex items-center gap-3">
                    <div className="bg-emerald-50 text-emerald-600 p-2 rounded-lg"><TypeIcon size={18} /></div>
                    <div>
                      <p className="font-semibold text-gray-800">{TypeCfg.label}</p>
                      <p className="text-xs text-gray-500">
                        {order.medications?.length || 0} دواء
                        {order.preferred_pharmacy_name && <> · {order.preferred_pharmacy_name}</>}
                        {' · '}{new Date(order.created_at).toLocaleDateString('ar-SA')}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${cfg.color}`}>
                      <Icon size={11}/> {cfg.label}
                    </span>
                    {expanded === order.id ? <ChevronUp size={16} className="text-gray-400"/> : <ChevronDown size={16} className="text-gray-400"/>}
                  </div>
                </div>

                {expanded === order.id && (
                  <div className="border-t border-gray-50 p-4 bg-gray-50/50">
                    {/* أدوية */}
                    {order.medications?.length > 0 && (
                      <div className="bg-white rounded-xl border border-gray-100 p-3 mb-3">
                        <h4 className="text-xs font-semibold text-gray-600 mb-2">الأدوية المطلوبة</h4>
                        <div className="space-y-1.5">
                          {order.medications.map((m, i) => (
                            <div key={i} className="flex items-center gap-3 text-sm">
                              <Pill size={13} className="text-emerald-500 flex-shrink-0"/>
                              <span className="font-medium">{m.name}</span>
                              {m.dosage && <span className="text-gray-400">({m.dosage})</span>}
                              {m.quantity && <span className="text-gray-400">× {m.quantity}</span>}
                              {m.notes && <span className="text-gray-400 text-xs">— {m.notes}</span>}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* صورة الوصفة */}
                    {order.prescription_image_path && (
                      <div className="mb-3">
                        <a href={`/api/uploads/prescription_images/${order.prescription_image_path}`}
                          target="_blank" rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-sm text-emerald-600 hover:underline bg-emerald-50 px-3 py-1.5 rounded-lg">
                          <Upload size={13}/> {order.prescription_image_name || 'صورة الوصفة'}
                        </a>
                      </div>
                    )}

                    {order.notes && <p className="text-sm text-gray-500 mb-3">ملاحظات: {order.notes}</p>}

                    {/* إجراءات الصيدلية */}
                    <div className="flex flex-wrap gap-2 mt-2">
                      {isPharmacy && order.status === 'pending' && (
                        <button onClick={() => handleAction(order.id, 'confirm')} disabled={busy}
                          className="flex items-center gap-1 bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 px-3 py-1.5 rounded-lg text-xs font-medium disabled:opacity-60">
                          <CheckCircle size={13}/> تأكيد الطلب
                        </button>
                      )}
                      {isPharmacy && ['pending', 'confirmed'].includes(order.status) && (
                        <button onClick={() => handleAction(order.id, 'dispense')} disabled={busy}
                          className="flex items-center gap-1 bg-green-50 text-green-700 border border-green-200 hover:bg-green-100 px-3 py-1.5 rounded-lg text-xs font-medium disabled:opacity-60">
                          <CheckCircle size={13}/> صرف الدواء
                        </button>
                      )}
                      {!isPharmacy && order.status === 'pending' && (
                        <button onClick={() => handleCancel(order.id)} disabled={busy}
                          className="flex items-center gap-1 bg-red-50 text-red-700 border border-red-200 hover:bg-red-100 px-3 py-1.5 rounded-lg text-xs font-medium disabled:opacity-60">
                          <XCircle size={13}/> إلغاء الطلب
                        </button>
                      )}
                      {order.dispensed_at && (
                        <span className="text-xs text-gray-400">صُرف في {new Date(order.dispensed_at).toLocaleDateString('ar-SA')}</span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
