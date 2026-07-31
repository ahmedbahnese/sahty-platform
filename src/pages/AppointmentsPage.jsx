import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Calendar, Clock, CheckCircle, XCircle, AlertCircle,
  Plus, User, Stethoscope, RefreshCw, Bell, ChevronDown,
  FileText, Phone, MapPin, Activity
} from 'lucide-react'

const API = '/api'

const STATUS_CONFIG = {
  scheduled:  { label: 'بانتظار التأكيد', color: 'bg-amber-100 text-amber-700',  icon: Clock },
  confirmed:  { label: 'مؤكد',            color: 'bg-blue-100 text-blue-700',    icon: CheckCircle },
  completed:  { label: 'مكتمل',           color: 'bg-emerald-100 text-emerald-700', icon: CheckCircle },
  cancelled:  { label: 'ملغى',            color: 'bg-red-100 text-red-700',      icon: XCircle },
  no_show:    { label: 'لم يحضر',         color: 'bg-gray-100 text-gray-600',    icon: AlertCircle },
}

const TYPE_LABELS = {
  in_person:    'حضوري',
  telemedicine: 'عن بُعد',
}

function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.scheduled
  const Icon = cfg.icon
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${cfg.color}`}>
      <Icon className="w-3 h-3" />
      {cfg.label}
    </span>
  )
}

function AppointmentCard({ appt, onAction, userType }) {
  const [expanded, setExpanded] = useState(false)
  const dateObj = new Date(appt.appointment_date)
  const isUpcoming = dateObj > new Date() && ['scheduled', 'confirmed'].includes(appt.status)

  return (
    <div className={`rounded-2xl border bg-white shadow-sm transition-all ${isUpcoming ? 'border-blue-200' : 'border-gray-100'}`}>
      <div className="p-5">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
          <div className="flex items-start gap-3">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${isUpcoming ? 'bg-blue-600' : 'bg-gray-100'}`}>
              <Stethoscope className={`w-6 h-6 ${isUpcoming ? 'text-white' : 'text-gray-400'}`} />
            </div>
            <div>
              {userType === 'patient' ? (
                <p className="font-semibold text-gray-900">{appt.doctor?.name || 'طبيب'}</p>
              ) : (
                <p className="font-semibold text-gray-900">{appt.patient?.name || 'مريض'}</p>
              )}
              {appt.for_member_name && (
                <span className="inline-flex items-center gap-1 text-xs bg-purple-50 text-purple-700 border border-purple-100 px-2 py-0.5 rounded-full mt-0.5">
                  👨‍👩‍👧 لصالح: {appt.for_member_name}
                </span>
              )}
              <p className="text-sm text-gray-500">{appt.doctor?.specialization || ''}</p>
              <div className="flex flex-wrap items-center gap-3 mt-1.5 text-sm text-gray-600">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5" />
                  {dateObj.toLocaleDateString('ar-EG', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  {dateObj.toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' })}
                </span>
                <span className="bg-gray-100 px-2 py-0.5 rounded-md text-xs">{TYPE_LABELS[appt.appointment_type] || appt.appointment_type}</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <StatusBadge status={appt.status} />
            <button onClick={() => setExpanded(e => !e)} className="text-gray-400 hover:text-gray-600 p-1">
              <ChevronDown className={`w-4 h-4 transition-transform ${expanded ? 'rotate-180' : ''}`} />
            </button>
          </div>
        </div>

        {expanded && (
          <div className="mt-4 pt-4 border-t border-gray-50 space-y-3">
            {appt.reason && <p className="text-sm text-gray-600"><span className="font-medium">السبب:</span> {appt.reason}</p>}
            {appt.symptoms && <p className="text-sm text-gray-600"><span className="font-medium">الأعراض:</span> {appt.symptoms}</p>}
            {appt.notes && <p className="text-sm text-gray-600"><span className="font-medium">ملاحظات:</span> {appt.notes}</p>}
            {appt.fee && <p className="text-sm text-gray-600"><span className="font-medium">رسوم الكشف:</span> {appt.fee} ج.م</p>}
            {appt.doctor?.clinic_name && <p className="text-sm text-gray-600 flex items-center gap-1"><MapPin className="w-3.5 h-3.5" />{appt.doctor.clinic_name}</p>}
          </div>
        )}

        {/* أزرار الإجراءات */}
        <div className="mt-4 flex flex-wrap gap-2">
          {userType === 'patient' && ['scheduled', 'confirmed'].includes(appt.status) && (
            <>
              <Button size="sm" variant="outline" className="text-amber-600 border-amber-200 hover:bg-amber-50"
                onClick={() => onAction('reschedule', appt)}>تعديل الموعد</Button>
              <Button size="sm" variant="outline" className="text-red-600 border-red-200 hover:bg-red-50"
                onClick={() => onAction('cancel', appt)}>إلغاء</Button>
            </>
          )}
          {userType === 'doctor' && appt.status === 'scheduled' && (
            <>
              <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white"
                onClick={() => onAction('confirm', appt)}>تأكيد الموعد ✓</Button>
              <Button size="sm" variant="outline" className="text-red-600 border-red-200 hover:bg-red-50"
                onClick={() => onAction('cancel', appt)}>رفض</Button>
            </>
          )}
          {userType === 'doctor' && appt.status === 'confirmed' && (
            <Button size="sm" className="bg-emerald-600 hover:bg-emerald-700 text-white"
              onClick={() => onAction('complete', appt)}>تم الكشف ✓</Button>
          )}
        </div>
      </div>
    </div>
  )
}

function BookingModal({ onClose, onBooked, token }) {
  const [doctors, setDoctors] = useState([])
  const [familyMembers, setFamilyMembers] = useState([])
  const [form, setForm] = useState({
    doctor_id: '', appointment_date: '', appointment_type: 'in_person',
    reason: '', symptoms: '',
    for_whom: 'self',          // 'self' | 'member_id' | 'manual'
    for_family_member_id: null,
    for_member_name: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch(`${API}/auth/doctors`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(d => setDoctors(d.doctors || []))
      .catch(() => {})

    // Load family members
    fetch('/api/family/groups', { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(async grpData => {
        if (grpData.success && grpData.groups.length > 0) {
          const g = grpData.groups[0]
          const memRes = await fetch(`/api/family/groups/${g.id}`, { headers: { Authorization: `Bearer ${token}` } })
          const memData = await memRes.json()
          if (memData.success) setFamilyMembers(memData.members)
        }
      })
      .catch(() => {})
  }, [token])

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleForWhom = (val) => {
    if (val === 'self') {
      setForm(f => ({ ...f, for_whom: 'self', for_family_member_id: null, for_member_name: '' }))
    } else if (val === 'manual') {
      setForm(f => ({ ...f, for_whom: 'manual', for_family_member_id: null }))
    } else {
      // It's a member id
      const member = familyMembers.find(m => m.id === parseInt(val))
      setForm(f => ({ ...f, for_whom: val, for_family_member_id: parseInt(val), for_member_name: member ? member.full_name : '' }))
    }
  }

  const submit = async () => {
    if (!form.doctor_id || !form.appointment_date || !form.appointment_type) {
      setError('يرجى تعبئة جميع الحقول المطلوبة')
      return
    }
    if (form.for_whom === 'manual' && !form.for_member_name.trim()) {
      setError('يرجى إدخال اسم الفرد')
      return
    }
    setLoading(true)
    setError('')
    try {
      const payload = {
        doctor_id: parseInt(form.doctor_id),
        appointment_date: form.appointment_date,
        appointment_type: form.appointment_type,
        reason: form.reason,
        symptoms: form.symptoms,
      }
      if (form.for_whom !== 'self') {
        if (form.for_family_member_id) payload.for_family_member_id = form.for_family_member_id
        if (form.for_member_name) payload.for_member_name = form.for_member_name
      }

      const res = await fetch(`${API}/appointments`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const data = await res.json()
      if (res.ok) { onBooked(data.appointment) }
      else { setError(data.message || 'حدث خطأ') }
    } finally { setLoading(false) }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto" dir="rtl">
        <div className="p-6 border-b">
          <h2 className="text-xl font-bold text-gray-900">حجز موعد جديد</h2>
        </div>
        <div className="p-6 space-y-4">
          {error && <div className="bg-red-50 text-red-600 rounded-xl p-3 text-sm">{error}</div>}

          {/* Book for whom */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">الحجز لـ *</label>
            <div className="space-y-2">
              <label className={`flex items-center gap-3 border rounded-xl p-3 cursor-pointer transition-colors ${form.for_whom === 'self' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:bg-gray-50'}`}>
                <input type="radio" className="text-blue-600" checked={form.for_whom === 'self'} onChange={() => handleForWhom('self')} />
                <span className="text-sm font-medium text-gray-700">🧑 أنا شخصياً</span>
              </label>
              {familyMembers.map(m => (
                <label key={m.id} className={`flex items-center gap-3 border rounded-xl p-3 cursor-pointer transition-colors ${form.for_whom === String(m.id) ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:bg-gray-50'}`}>
                  <input type="radio" className="text-blue-600" checked={form.for_whom === String(m.id)} onChange={() => handleForWhom(String(m.id))} />
                  <span className="text-sm font-medium text-gray-700">
                    👨‍👩‍👧 {m.full_name} <span className="text-gray-500 font-normal">({m.relationship})</span>
                  </span>
                </label>
              ))}
              <label className={`flex items-center gap-3 border rounded-xl p-3 cursor-pointer transition-colors ${form.for_whom === 'manual' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:bg-gray-50'}`}>
                <input type="radio" className="text-blue-600" checked={form.for_whom === 'manual'} onChange={() => handleForWhom('manual')} />
                <span className="text-sm font-medium text-gray-700">✏️ فرد آخر (أدخل الاسم)</span>
              </label>
              {form.for_whom === 'manual' && (
                <Input value={form.for_member_name} onChange={e => set('for_member_name', e.target.value)}
                  placeholder="اسم الفرد كاملاً" className="mr-6" />
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">الطبيب *</label>
            <select value={form.doctor_id} onChange={e => set('doctor_id', e.target.value)}
              className="w-full border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">اختر طبيباً…</option>
              {doctors.map(d => (
                <option key={d.id} value={d.id}>
                  د. {d.first_name} {d.last_name} — {d.specialization}
                  {d.consultation_fee ? ` (${d.consultation_fee} ج.م)` : ''}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">تاريخ ووقت الموعد *</label>
            <input type="datetime-local" value={form.appointment_date}
              onChange={e => set('appointment_date', e.target.value)}
              min={new Date().toISOString().slice(0, 16)}
              className="w-full border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">نوع الموعد *</label>
            <div className="flex gap-3">
              {[['in_person', 'حضوري'], ['telemedicine', 'عن بُعد']].map(([v, l]) => (
                <label key={v} className={`flex-1 flex items-center justify-center gap-2 border rounded-xl p-3 cursor-pointer text-sm font-medium transition-colors ${form.appointment_type === v ? 'border-blue-500 bg-blue-50 text-blue-700' : 'border-gray-200 hover:bg-gray-50'}`}>
                  <input type="radio" className="hidden" value={v} checked={form.appointment_type === v} onChange={() => set('appointment_type', v)} />
                  {l}
                </label>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">سبب الزيارة</label>
            <Input value={form.reason} onChange={e => set('reason', e.target.value)} placeholder="اكتب سبب الزيارة…" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">الأعراض</label>
            <textarea value={form.symptoms} onChange={e => set('symptoms', e.target.value)}
              className="w-full border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows={3} placeholder="صف أعراضك…" />
          </div>
        </div>
        <div className="p-6 border-t flex gap-3 justify-end">
          <Button variant="outline" onClick={onClose}>إلغاء</Button>
          <Button onClick={submit} disabled={loading} className="bg-blue-600 hover:bg-blue-700 text-white">
            {loading ? 'جاري الحجز…' : 'تأكيد الحجز'}
          </Button>
        </div>
      </div>
    </div>
  )
}

function RescheduleModal({ appt, onClose, onSaved, token }) {
  const [date, setDate] = useState(appt.appointment_date ? appt.appointment_date.slice(0, 16) : '')
  const [type, setType] = useState(appt.appointment_type)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const submit = async () => {
    if (!date) { setError('يرجى تحديد التاريخ'); return }
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${API}/appointments/${appt.id}`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ appointment_date: date, appointment_type: type })
      })
      const data = await res.json()
      if (res.ok) onSaved(data.appointment)
      else setError(data.message || 'حدث خطأ')
    } finally { setLoading(false) }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md" dir="rtl">
        <div className="p-6 border-b">
          <h2 className="text-xl font-bold text-gray-900">تعديل الموعد</h2>
        </div>
        <div className="p-6 space-y-4">
          {error && <div className="bg-red-50 text-red-600 rounded-xl p-3 text-sm">{error}</div>}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">تاريخ ووقت الموعد الجديد</label>
            <input type="datetime-local" value={date} onChange={e => setDate(e.target.value)}
              min={new Date().toISOString().slice(0, 16)}
              className="w-full border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">نوع الموعد</label>
            <div className="flex gap-3">
              {[['in_person', 'حضوري'], ['telemedicine', 'عن بُعد']].map(([v, l]) => (
                <label key={v} className={`flex-1 flex items-center justify-center gap-2 border rounded-xl p-3 cursor-pointer text-sm font-medium transition-colors ${type === v ? 'border-blue-500 bg-blue-50 text-blue-700' : 'border-gray-200 hover:bg-gray-50'}`}>
                  <input type="radio" className="hidden" value={v} checked={type === v} onChange={() => setType(v)} />
                  {l}
                </label>
              ))}
            </div>
          </div>
        </div>
        <div className="p-6 border-t flex gap-3 justify-end">
          <Button variant="outline" onClick={onClose}>إلغاء</Button>
          <Button onClick={submit} disabled={loading} className="bg-blue-600 hover:bg-blue-700 text-white">
            {loading ? 'جاري الحفظ…' : 'حفظ التعديل'}
          </Button>
        </div>
      </div>
    </div>
  )
}

function CancelModal({ appt, onClose, onCancelled, token }) {
  const [reason, setReason] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API}/appointments/${appt.id}/cancel`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: reason || 'إلغاء من المستخدم' })
      })
      const data = await res.json()
      if (res.ok) onCancelled(data.appointment)
    } finally { setLoading(false) }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm" dir="rtl">
        <div className="p-6">
          <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <XCircle className="w-6 h-6 text-red-600" />
          </div>
          <h2 className="text-xl font-bold text-gray-900 text-center mb-2">إلغاء الموعد</h2>
          <p className="text-sm text-gray-500 text-center mb-4">هل أنت متأكد من إلغاء هذا الموعد؟</p>
          <textarea value={reason} onChange={e => setReason(e.target.value)}
            className="w-full border rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400 resize-none"
            rows={2} placeholder="سبب الإلغاء (اختياري)" />
        </div>
        <div className="p-6 border-t flex gap-3 justify-end">
          <Button variant="outline" onClick={onClose}>تراجع</Button>
          <Button onClick={submit} disabled={loading} className="bg-red-600 hover:bg-red-700 text-white">
            {loading ? 'جاري الإلغاء…' : 'تأكيد الإلغاء'}
          </Button>
        </div>
      </div>
    </div>
  )
}

export default function AppointmentsPage() {
  const { user, token, isPatient, isDoctor } = useAuth()
  const [appointments, setAppointments]   = useState([])
  const [stats, setStats]                 = useState({})
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount]     = useState(0)
  const [loading, setLoading]             = useState(true)
  const [activeTab, setActiveTab]         = useState('upcoming')
  const [showBooking, setShowBooking]     = useState(false)
  const [showNotifs, setShowNotifs]       = useState(false)
  const [modal, setModal]                 = useState(null) // { type, appt }
  const [toast, setToast]                 = useState('')

  const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(''), 3000) }

  const fetchAll = useCallback(async () => {
    setLoading(true)
    try {
      const headers = { Authorization: `Bearer ${token}` }
      const [apptRes, statsRes, notifRes] = await Promise.all([
        fetch(`${API}/appointments`, { headers }),
        fetch(`${API}/appointments/stats`, { headers }),
        fetch(`${API}/appointments/notifications`, { headers }),
      ])
      const [apptData, statsData, notifData] = await Promise.all([apptRes.json(), statsRes.json(), notifRes.json()])
      setAppointments(apptData.appointments || [])
      setStats(statsData)
      setNotifications(notifData.notifications || [])
      setUnreadCount(notifData.unread_count || 0)
    } finally { setLoading(false) }
  }, [token])

  useEffect(() => { fetchAll() }, [fetchAll])

  const updateAppt = (updated) => {
    setAppointments(prev => prev.map(a => a.id === updated.id ? updated : a))
    setModal(null)
  }

  const handleAction = async (type, appt) => {
    if (type === 'confirm') {
      const res = await fetch(`${API}/appointments/${appt.id}/confirm`, {
        method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
      })
      const data = await res.json()
      if (res.ok) { updateAppt(data.appointment); showToast('تم تأكيد الموعد ✓') }
      return
    }
    if (type === 'complete') {
      const res = await fetch(`${API}/appointments/${appt.id}/complete`, {
        method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
      })
      const data = await res.json()
      if (res.ok) { updateAppt(data.appointment); showToast('تم إتمام الموعد ✓') }
      return
    }
    setModal({ type, appt })
  }

  const markNotifsRead = async () => {
    await fetch(`${API}/appointments/notifications/mark-read`, {
      method: 'POST', headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
    })
    setNotifications(prev => prev.map(n => ({ ...n, is_read: true })))
    setUnreadCount(0)
  }

  const now = new Date()
  const filtered = {
    upcoming: appointments.filter(a => new Date(a.appointment_date) >= now && ['scheduled', 'confirmed'].includes(a.status)),
    past:     appointments.filter(a => new Date(a.appointment_date) < now || ['completed', 'cancelled'].includes(a.status)),
    pending:  appointments.filter(a => a.status === 'scheduled'),
    all:      appointments,
  }

  const tabs = isDoctor
    ? [{ key: 'pending', label: `طلبات جديدة (${filtered.pending.length})` }, { key: 'upcoming', label: 'القادمة' }, { key: 'past', label: 'السابقة' }]
    : [{ key: 'upcoming', label: 'القادمة' }, { key: 'past', label: 'السابقة' }, { key: 'all', label: 'جميع المواعيد' }]

  const userType = isDoctor ? 'doctor' : 'patient'

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      {/* هيدر */}
      <div className="bg-gradient-to-l from-blue-700 to-indigo-600 text-white">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">المواعيد</h1>
              <p className="text-blue-100 mt-1 text-sm">
                {isDoctor ? 'إدارة مواعيد مرضاك' : 'مواعيدك الطبية'}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="relative">
                <button onClick={() => { setShowNotifs(v => !v); if (!showNotifs) markNotifsRead() }}
                  className="relative bg-white/20 hover:bg-white/30 rounded-xl p-2.5 transition-colors">
                  <Bell className="w-5 h-5" />
                  {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center font-bold">
                      {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                  )}
                </button>
                {showNotifs && (
                  <div className="absolute left-0 top-12 w-80 bg-white rounded-2xl shadow-xl border border-gray-100 z-50 overflow-hidden">
                    <div className="px-4 py-3 border-b font-semibold text-gray-900 text-sm">الإشعارات</div>
                    <div className="max-h-72 overflow-y-auto">
                      {notifications.length === 0 ? (
                        <p className="text-center text-gray-400 text-sm py-8">لا توجد إشعارات</p>
                      ) : notifications.map(n => (
                        <div key={n.id} className={`px-4 py-3 border-b last:border-0 ${!n.is_read ? 'bg-blue-50' : ''}`}>
                          <p className="text-sm font-medium text-gray-900">{n.title}</p>
                          <p className="text-xs text-gray-500 mt-0.5">{n.message}</p>
                          <p className="text-xs text-gray-400 mt-1">{new Date(n.created_at).toLocaleString('ar-EG')}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              {isPatient && (
                <Button onClick={() => setShowBooking(true)} className="bg-white text-blue-700 hover:bg-blue-50 font-semibold flex items-center gap-2">
                  <Plus className="w-4 h-4" /> حجز موعد
                </Button>
              )}
            </div>
          </div>

          {/* إحصائيات سريعة */}
          <div className="grid grid-cols-3 gap-3 mt-6">
            {(isPatient ? [
              { label: 'القادمة',  value: stats.upcoming  ?? '…' },
              { label: 'المكتملة', value: stats.completed ?? '…' },
              { label: 'الملغاة',  value: stats.cancelled ?? '…' },
            ] : [
              { label: 'طلبات جديدة', value: stats.pending   ?? '…' },
              { label: 'مؤكدة',       value: stats.upcoming  ?? '…' },
              { label: 'مكتملة',      value: stats.completed ?? '…' },
            ]).map(s => (
              <div key={s.label} className="bg-white/10 rounded-xl p-3 text-center">
                <p className="text-2xl font-bold text-white">{s.value}</p>
                <p className="text-xs mt-0.5 text-blue-200">{s.label}</p>
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
              className={`flex-1 min-w-fit px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${activeTab === t.key ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-600 hover:bg-gray-50'}`}>
              {t.label}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <RefreshCw className="w-8 h-8 text-blue-400 animate-spin" />
          </div>
        ) : filtered[activeTab]?.length === 0 ? (
          <div className="text-center py-20">
            <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 font-medium">لا توجد مواعيد</p>
            {isPatient && activeTab === 'upcoming' && (
              <Button onClick={() => setShowBooking(true)} className="mt-4 bg-blue-600 hover:bg-blue-700 text-white">
                احجز موعداً الآن
              </Button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {(filtered[activeTab] || []).map(a => (
              <AppointmentCard key={a.id} appt={a} onAction={handleAction} userType={userType} />
            ))}
          </div>
        )}
      </div>

      {/* نوافذ */}
      {showBooking && (
        <BookingModal token={token} onClose={() => setShowBooking(false)}
          onBooked={a => { setAppointments(prev => [a, ...prev]); setShowBooking(false); showToast('تم حجز الموعد بنجاح ✓') }} />
      )}
      {modal?.type === 'reschedule' && (
        <RescheduleModal token={token} appt={modal.appt} onClose={() => setModal(null)}
          onSaved={a => { updateAppt(a); showToast('تم تعديل الموعد ✓') }} />
      )}
      {modal?.type === 'cancel' && (
        <CancelModal token={token} appt={modal.appt} onClose={() => setModal(null)}
          onCancelled={a => { updateAppt(a); showToast('تم إلغاء الموعد') }} />
      )}

      {/* Toast */}
      {toast && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-gray-900 text-white px-6 py-3 rounded-xl shadow-xl text-sm font-medium z-50 animate-in fade-in slide-in-from-bottom-4">
          {toast}
        </div>
      )}
    </div>
  )
}
