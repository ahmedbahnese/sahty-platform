import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Video, MessageCircle, Upload, Send, FileText, Stethoscope, AlertTriangle } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

const API = '/api/consultations'
const authHeaders = () => ({ Authorization: `Bearer ${localStorage.getItem('token')}` })

function ConsultationCard({ item }) {
  return (
    <Link to={`/consultations/${item.id}`} className="block rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md dark:border-slate-700 dark:bg-slate-900">
      <div className="flex items-start justify-between gap-3">
        <div><p className="font-bold text-slate-900 dark:text-white">استشارة #{item.id}</p><p className="mt-1 text-sm text-slate-500">{item.scheduled_at ? new Date(item.scheduled_at).toLocaleString('ar-EG') : 'موعد غير محدد'}</p></div>
        <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700 dark:bg-blue-950 dark:text-blue-200">{item.status}</span>
      </div>
      <div className="mt-4 flex flex-wrap gap-2 text-sm text-slate-600 dark:text-slate-300"><span className="inline-flex items-center gap-1"><Video size={16}/> فيديو</span><span className="inline-flex items-center gap-1"><MessageCircle size={16}/> {item.messages?.length || 0} رسالة</span><span className="inline-flex items-center gap-1"><FileText size={16}/> {item.attachments?.length || 0} ملف</span></div>
    </Link>
  )
}

export default function ConsultationsPage() {
  const { id } = useParams()
  const { user } = useAuth()
  const [items, setItems] = useState([])
  const [current, setCurrent] = useState(null)
  const [doctorId, setDoctorId] = useState('')
  const [scheduledAt, setScheduledAt] = useState('')
  const [body, setBody] = useState('')
  const [file, setFile] = useState(null)
  const [clinical, setClinical] = useState({ diagnosis: '', treatment_plan: '', prescription: '', referral_type: '', referral_note: '', emergency_requested: false })
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const response = await fetch(id ? `${API}/${id}` : API, { headers: authHeaders() })
      const data = await response.json()
      if (!response.ok) throw new Error(data.message || 'تعذر تحميل الاستشارات')
      if (id) setCurrent(data.consultation)
      else setItems(data.consultations || [])
    } catch (error) { setMessage(error.message) } finally { setLoading(false) }
  }, [id])
  useEffect(() => { load() }, [load])

  const create = async (event) => {
    event.preventDefault(); setMessage('')
    const response = await fetch(API, { method: 'POST', headers: { ...authHeaders(), 'Content-Type': 'application/json' }, body: JSON.stringify({ doctor_id: Number(doctorId), scheduled_at: scheduledAt }) })
    const data = await response.json(); setMessage(data.message || data.error || 'تم')
    if (response.ok) { setDoctorId(''); setScheduledAt(''); load() }
  }

  const sendMessage = async (event) => {
    event.preventDefault()
    const response = await fetch(`${API}/${id}/messages`, { method: 'POST', headers: { ...authHeaders(), 'Content-Type': 'application/json' }, body: JSON.stringify({ body }) })
    const data = await response.json(); setMessage(data.message || 'تم إرسال الرسالة')
    if (response.ok) { setBody(''); load() }
  }

  const upload = async (event) => {
    event.preventDefault(); if (!file) return
    const form = new FormData(); form.append('file', file); form.append('kind', 'medical_report')
    const response = await fetch(`${API}/${id}/attachments`, { method: 'POST', headers: authHeaders(), body: form })
    const data = await response.json(); setMessage(data.message || 'تم رفع الملف')
    if (response.ok) { setFile(null); load() }
  }

  const complete = async (event) => {
    event.preventDefault()
    const response = await fetch(`${API}/${id}/complete`, { method: 'POST', headers: { ...authHeaders(), 'Content-Type': 'application/json' }, body: JSON.stringify({ ...clinical, prescription: clinical.prescription ? { text: clinical.prescription } : {} }) })
    const data = await response.json(); setMessage(data.message || 'تم حفظ النتيجة')
    if (response.ok) setCurrent(data.consultation)
  }

  if (loading) return <div className="mx-auto max-w-5xl p-8 text-center">جارٍ تحميل الاستشارات...</div>
  if (!id) return <div dir="rtl" className="mx-auto max-w-6xl space-y-6 p-4 sm:p-8"><header><p className="text-sm font-semibold text-cyan-600">الرعاية عن بُعد</p><h1 className="mt-2 text-3xl font-black text-slate-900 dark:text-white">الاستشارات المرئية</h1><p className="mt-2 text-slate-500">فيديو آمن، شات، تقارير، وتحويلات موثقة بين المريض والطبيب.</p></header>{user?.user_type === 'patient' && <form onSubmit={create} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900"><h2 className="mb-4 font-bold">طلب استشارة جديدة</h2><div className="grid gap-3 sm:grid-cols-2"><input required value={doctorId} onChange={e => setDoctorId(e.target.value)} placeholder="رقم الطبيب" className="rounded-xl border p-3 dark:bg-slate-800"/><input required type="datetime-local" value={scheduledAt} onChange={e => setScheduledAt(e.target.value)} className="rounded-xl border p-3 dark:bg-slate-800"/></div><button className="mt-4 rounded-xl bg-blue-600 px-5 py-3 font-bold text-white">طلب الاستشارة</button></form>} {message && <p className="rounded-xl bg-amber-50 p-3 text-amber-800">{message}</p>}<div className="grid gap-4 md:grid-cols-2">{items.map(item => <ConsultationCard item={item} key={item.id}/>)}</div></div>

  return <div dir="rtl" className="mx-auto max-w-5xl space-y-5 p-4 sm:p-8"><Link to="/consultations" className="text-sm font-semibold text-blue-600">← العودة للاستشارات</Link><header><h1 className="mt-3 text-3xl font-black text-slate-900 dark:text-white">استشارة #{current?.id}</h1><p className="text-slate-500">الحالة: {current?.status}</p></header>{message && <p className="rounded-xl bg-blue-50 p-3 text-blue-800 dark:bg-blue-950 dark:text-blue-100">{message}</p>}<div className="grid gap-4 md:grid-cols-3"><a href={current?.meeting_url} target="_blank" rel="noreferrer" className="flex items-center justify-center gap-2 rounded-2xl bg-blue-600 p-4 font-bold text-white"><Video/> دخول غرفة الفيديو</a><div className="rounded-2xl border bg-white p-4 dark:border-slate-700 dark:bg-slate-900"><p className="text-sm text-slate-500">التشخيص</p><p className="mt-2 font-semibold">{current?.diagnosis || 'بانتظار الطبيب'}</p></div><div className="rounded-2xl border bg-white p-4 dark:border-slate-700 dark:bg-slate-900"><p className="text-sm text-slate-500">خطة العلاج</p><p className="mt-2 font-semibold">{current?.treatment_plan || 'بانتظار الطبيب'}</p></div></div><section className="rounded-2xl border bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900"><h2 className="mb-4 flex items-center gap-2 font-bold"><MessageCircle/> المحادثة</h2><div className="max-h-80 space-y-2 overflow-auto">{(current?.messages || []).map(item => <div key={item.id} className={`rounded-xl p-3 ${item.sender_user_id === user?.id ? 'bg-blue-50 dark:bg-blue-950' : 'bg-slate-50 dark:bg-slate-800'}`}><p>{item.body}</p><small className="text-slate-400">{new Date(item.created_at).toLocaleString('ar-EG')}</small></div>)}</div><form onSubmit={sendMessage} className="mt-4 flex gap-2"><input required value={body} onChange={e => setBody(e.target.value)} placeholder="اكتب رسالة للطبيب..." className="min-w-0 flex-1 rounded-xl border p-3 dark:bg-slate-800"/><button className="rounded-xl bg-blue-600 px-4 text-white"><Send/></button></form></section><section className="rounded-2xl border bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-900"><h2 className="mb-4 flex items-center gap-2 font-bold"><Upload/> التقارير والتحاليل والعلاجات</h2><div className="space-y-2">{(current?.attachments || []).map(item => <a key={item.id} className="block rounded-lg bg-slate-50 p-3 text-blue-700 dark:bg-slate-800 dark:text-blue-200" href={item.file_path} target="_blank" rel="noreferrer">{item.file_name}</a>)}</div><form onSubmit={upload} className="mt-4 flex flex-wrap items-center gap-3"><input required type="file" accept=".pdf,.png,.jpg,.jpeg,.webp,.dcm" onChange={e => setFile(e.target.files?.[0] || null)}/><button className="rounded-xl bg-cyan-600 px-4 py-2 font-bold text-white">رفع الملف</button></form></section>{user?.user_type === 'doctor' && <form onSubmit={complete} className="rounded-2xl border border-emerald-200 bg-emerald-50 p-5 dark:border-emerald-900 dark:bg-emerald-950/30"><h2 className="mb-4 flex items-center gap-2 font-bold"><Stethoscope/> توثيق نتيجة الطبيب</h2><div className="grid gap-3 sm:grid-cols-2"><textarea required placeholder="التشخيص" value={clinical.diagnosis} onChange={e => setClinical({ ...clinical, diagnosis: e.target.value })} className="rounded-xl border p-3"/><textarea required placeholder="خطة العلاج" value={clinical.treatment_plan} onChange={e => setClinical({ ...clinical, treatment_plan: e.target.value })} className="rounded-xl border p-3"/><textarea placeholder="الروشتة والأدوية" value={clinical.prescription} onChange={e => setClinical({ ...clinical, prescription: e.target.value })} className="rounded-xl border p-3"/><input placeholder="نوع التحويل (فحص/علاج/طوارئ)" value={clinical.referral_type} onChange={e => setClinical({ ...clinical, referral_type: e.target.value })} className="rounded-xl border p-3"/></div><label className="mt-3 flex items-center gap-2"><input type="checkbox" checked={clinical.emergency_requested} onChange={e => setClinical({ ...clinical, emergency_requested: e.target.checked })}/><AlertTriangle size={18}/> طلب طوارئ للحالة</label><button className="mt-4 rounded-xl bg-emerald-600 px-5 py-3 font-bold text-white">حفظ التشخيص والروشتة</button></form>}</div>
}
