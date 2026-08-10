import { useEffect, useMemo, useState } from 'react'
import { CheckCircle2, Clock3, Heart, Loader2, MapPin, XCircle } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

const statusLabels = { PENDING: 'جديد', UNDER_REVIEW: 'قيد المراجعة', ACCEPTED: 'مقبول', REJECTED: 'مرفوض', SCHEDULED: 'مجدول', IN_PROGRESS: 'جارٍ التنفيذ', COMPLETED: 'مكتمل', CANCELLED: 'ملغى' }

export default function NursingDashboardPage() {
  const { user, token } = useAuth()
  const isNurse = user?.user_type === 'nurse'
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [form, setForm] = useState({ service_type: 'زيارة تمريض منزلية', address: '', description: '', scheduled_at: '' })
  const [roleForm, setRoleForm] = useState({ full_name: '', qualification: '', license_number: '', id_document: '' })
  const headers = useMemo(() => ({ Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }), [token])

  const load = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/nursing/requests', { headers })
      const data = await response.json()
      if (!response.ok) throw new Error(data.message)
      setRequests(data.requests || [])
    } catch (error) { setMessage(error.message || 'تعذر تحميل طلبات التمريض') }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [token])

  const createRequest = async event => {
    event.preventDefault(); setMessage('')
    const response = await fetch('/api/nursing/requests', { method: 'POST', headers, body: JSON.stringify(form) })
    const data = await response.json()
    if (!response.ok) { setMessage(data.message || 'تعذر إرسال الطلب'); return }
    setForm({ service_type: 'زيارة تمريض منزلية', address: '', description: '', scheduled_at: '' })
    setMessage('تم إرسال طلب التمريض بنجاح'); load()
  }
  const updateRequest = async (id, action, body = {}) => {
    const response = await fetch(`/api/nursing/requests/${id}/${action}`, { method: 'POST', headers, body: JSON.stringify(body) })
    const data = await response.json()
    setMessage(data.message || (response.ok ? 'تم تحديث الطلب' : 'تعذر تحديث الطلب'))
    if (response.ok) load()
  }
  const requestNurseRole = async event => {
    event.preventDefault(); setMessage('')
    const response = await fetch('/api/nursing/role-request', { method: 'POST', headers, body: JSON.stringify(roleForm) })
    const data = await response.json()
    setMessage(data.message || (response.ok ? 'تم إرسال طلب الدور' : 'تعذر إرسال الطلب'))
  }

  return <div className="min-h-screen bg-gray-50 py-8" dir="rtl"><div className="mx-auto max-w-6xl px-4">
    <header className="mb-6 rounded-3xl bg-gradient-to-l from-rose-700 to-pink-500 p-6 text-white"><div className="flex items-center gap-3"><div className="rounded-2xl bg-white/20 p-3"><Heart className="h-7 w-7" /></div><div><h1 className="text-2xl font-bold">خدمات التمريض</h1><p className="text-sm text-rose-100">{isNurse ? 'إدارة الطلبات والزيارات المسندة إليك' : 'اطلب رعاية تمريضية منزلية آمنة'}</p></div></div></header>
    {message && <div className="mb-4 rounded-xl border border-blue-100 bg-blue-50 p-3 text-sm text-blue-700">{message}</div>}
    {!isNurse && <><form onSubmit={createRequest} className="mb-6 rounded-2xl border border-gray-100 bg-white p-5 shadow-sm"><h2 className="mb-4 text-lg font-bold">طلب خدمة تمريضية</h2><div className="grid gap-3 md:grid-cols-2"><select value={form.service_type} onChange={e => setForm({ ...form, service_type: e.target.value })} className="rounded-xl border border-gray-200 px-3 py-2 text-sm"><option>زيارة تمريض منزلية</option><option>إجراء تمريضي</option><option>متابعة مريض</option><option>خدمة تمريض أخرى</option></select><input required value={form.address} onChange={e => setForm({ ...form, address: e.target.value })} placeholder="عنوان الزيارة *" className="rounded-xl border border-gray-200 px-3 py-2 text-sm" /><input type="datetime-local" value={form.scheduled_at} onChange={e => setForm({ ...form, scheduled_at: e.target.value })} className="rounded-xl border border-gray-200 px-3 py-2 text-sm" /><textarea value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} placeholder="تفاصيل أو احتياجات خاصة" className="rounded-xl border border-gray-200 px-3 py-2 text-sm" /></div><button className="mt-4 rounded-xl bg-rose-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-rose-700">إرسال الطلب</button></form><form onSubmit={requestNurseRole} className="mb-6 rounded-2xl border border-teal-100 bg-teal-50/50 p-5"><h2 className="mb-1 text-lg font-bold text-teal-900">هل تريد تقديم خدمات التمريض؟</h2><p className="mb-4 text-sm text-teal-700">أرسل مؤهلاتك من حسابك الحالي، وسيبقى دور المريض فعالًا حتى الاعتماد.</p><div className="grid gap-3 md:grid-cols-2"><input required value={roleForm.full_name} onChange={e => setRoleForm({ ...roleForm, full_name: e.target.value })} placeholder="الاسم الكامل *" className="rounded-xl border border-teal-200 bg-white px-3 py-2 text-sm" /><input required value={roleForm.qualification} onChange={e => setRoleForm({ ...roleForm, qualification: e.target.value })} placeholder="المؤهل التمريضي *" className="rounded-xl border border-teal-200 bg-white px-3 py-2 text-sm" /><input required value={roleForm.license_number} onChange={e => setRoleForm({ ...roleForm, license_number: e.target.value })} placeholder="رقم الترخيص *" className="rounded-xl border border-teal-200 bg-white px-3 py-2 text-sm" /><input value={roleForm.id_document} onChange={e => setRoleForm({ ...roleForm, id_document: e.target.value })} placeholder="رقم/مرجع وثيقة الهوية" className="rounded-xl border border-teal-200 bg-white px-3 py-2 text-sm" /></div><button className="mt-4 rounded-xl bg-teal-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-teal-700">إرسال طلب اعتماد الممرض</button></form></>}
    <section className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm"><h2 className="mb-4 text-lg font-bold">{isNurse ? 'طلبات المرضى' : 'طلباتي التمريضية'}</h2>{loading ? <div className="flex justify-center py-10"><Loader2 className="animate-spin text-rose-600" /></div> : requests.length === 0 ? <div className="py-12 text-center text-gray-400"><Clock3 className="mx-auto mb-2 h-9 w-9 opacity-40" /><p>لا توجد طلبات حتى الآن</p></div> : <div className="space-y-3">{requests.map(item => <div key={item.id} className="rounded-xl border border-gray-100 p-4"><div className="flex flex-wrap items-start justify-between gap-3"><div><h3 className="font-semibold text-gray-900">{item.service_type}</h3><p className="mt-1 text-sm text-gray-500"><MapPin className="ml-1 inline h-4 w-4" />{item.address}</p><p className="mt-1 text-xs text-gray-400">{item.description || 'بدون تفاصيل إضافية'}</p></div><span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-semibold">{statusLabels[item.status] || item.status}</span></div>{isNurse && ['PENDING', 'UNDER_REVIEW'].includes(item.status) && <div className="mt-3 flex gap-2"><button onClick={() => updateRequest(item.id, 'accept')} className="rounded-lg bg-emerald-600 px-3 py-2 text-xs font-semibold text-white"><CheckCircle2 className="ml-1 inline h-3.5 w-3.5" />قبول</button><button onClick={() => updateRequest(item.id, 'reject', { reason: 'غير متاح حاليًا' })} className="rounded-lg bg-red-50 px-3 py-2 text-xs font-semibold text-red-700"><XCircle className="ml-1 inline h-3.5 w-3.5" />رفض</button></div>}{isNurse && item.nurse_id === user?.id && item.status === 'ACCEPTED' && <button onClick={() => updateRequest(item.id, 'complete', { visit_notes: 'تم تنفيذ الزيارة وتوثيقها' })} className="mt-3 rounded-lg bg-blue-600 px-3 py-2 text-xs font-semibold text-white">تسجيل الزيارة كمكتملة</button>}</div>)}</div>}</section>
  </div></div>
}