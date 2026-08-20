import { useEffect, useMemo, useState } from 'react'
import { CalendarDays, FileHeart, Loader2, Search, UserRound, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuth } from '../contexts/AuthContext'

const sections = [
  ['medical_records', 'التقارير الطبية'],
  ['lab_tests', 'التحاليل السابقة'],
  ['radiology', 'الأشعات السابقة'],
  ['medications', 'الأدوية'],
]

export default function DoctorPatientsPage() {
  const { token } = useAuth()
  const [search, setSearch] = useState('')
  const [examDate, setExamDate] = useState('')
  const [patients, setPatients] = useState([])
  const [selected, setSelected] = useState(null)
  const [record, setRecord] = useState(null)
  const [loading, setLoading] = useState(false)
  const [recordLoading, setRecordLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [reportForm, setReportForm] = useState({ diagnosis: '', symptoms: '', treatment: '', notes: '' })
  const [reportBusy, setReportBusy] = useState(false)

  const headers = useMemo(() => ({ Authorization: `Bearer ${token}` }), [token])
  const loadPatients = async () => {
    setLoading(true)
    setMessage('')
    try {
      const params = new URLSearchParams()
      if (search.trim()) params.set('search', search.trim())
      if (examDate) params.set('exam_date', examDate)
      const response = await fetch(`/api/doctors/me/patients?${params}`, { headers })
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || data.message || 'تعذر تحميل المرضى')
      setPatients(data.patients || [])
    } catch (error) {
      setMessage(error.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadPatients() }, [token])

  const openRecord = async (patient) => {
    setSelected(patient)
    setRecordLoading(true)
    setMessage('')
    try {
      const response = await fetch(`/api/doctors/me/patients/${patient.id}/medical-record`, { headers })
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || 'تعذر فتح الملف الطبي')
      setRecord(data)
    } catch (error) {
      setMessage(error.message)
      setRecord(null)
    } finally {
      setRecordLoading(false)
    }
  }

  const submitReport = async event => {
    event.preventDefault()
    if (!selected) return
    setReportBusy(true)
    try {
      const response = await fetch(`/api/doctors/me/patients/${selected.id}/medical-records`, { method: 'POST', headers: { ...headers, 'Content-Type': 'application/json' }, body: JSON.stringify(reportForm) })
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || 'تعذر حفظ التقرير')
      setRecord(previous => ({ ...previous, medical_records: [data.record, ...(previous.medical_records || [])] }))
      setReportForm({ diagnosis: '', symptoms: '', treatment: '', notes: '' })
      setMessage('تم حفظ التقرير الطبي داخل ملف المريض')
    } catch (error) { setMessage(error.message) } finally { setReportBusy(false) }
  }

  return <div className="space-y-6">
    <header className="rounded-2xl bg-gradient-to-l from-blue-700 to-teal-600 p-6 text-white shadow-sm">
      <p className="text-sm text-blue-100">لوحة الطبيب</p>
      <h1 className="mt-2 text-2xl font-bold">إدارة المرضى والملفات الطبية</h1>
      <p className="mt-2 text-sm text-blue-100">ابحث بالاسم أو الرقم الطبي أو الهاتف أو تاريخ الفحص، ثم افتح السجل المصرح لك به.</p>
    </header>

    <section className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">
      <div className="grid gap-3 md:grid-cols-[1fr_220px_auto]">
        <div className="relative"><Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" /><Input value={search} onChange={event => setSearch(event.target.value)} onKeyDown={event => event.key === 'Enter' && loadPatients()} className="pr-10" placeholder="اسم المريض، الرقم الطبي، الهاتف أو الرقم القومي" aria-label="بحث عن مريض" /></div>
        <div className="relative"><CalendarDays className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" /><Input value={examDate} onChange={event => setExamDate(event.target.value)} className="pr-10" type="date" aria-label="تاريخ الفحص" /></div>
        <Button onClick={loadPatients} disabled={loading}>{loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'بحث'}</Button>
      </div>
    </section>

    {message && <div role="alert" className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-rose-800">{message}</div>}

    <section className="grid gap-4 lg:grid-cols-[minmax(280px,380px)_1fr]">
      <div className="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm">
        <div className="mb-3 flex items-center justify-between"><h2 className="font-bold text-slate-900">مرضاي</h2><span className="rounded-full bg-blue-50 px-2 py-1 text-xs text-blue-700">{patients.length}</span></div>
        <div className="space-y-2">{patients.length === 0 && <p className="rounded-xl bg-slate-50 p-6 text-center text-sm text-slate-500">لا توجد نتائج. ابحث عن مريض مرتبط بمواعيدك.</p>}{patients.map(patient => <button key={patient.id} onClick={() => openRecord(patient)} className={`w-full rounded-xl border p-3 text-right transition hover:border-blue-300 hover:bg-blue-50 ${selected?.id === patient.id ? 'border-blue-500 bg-blue-50' : 'border-slate-100'}`}><div className="flex items-center gap-3"><span className="rounded-full bg-blue-100 p-2 text-blue-700"><UserRound className="h-4 w-4" /></span><span><strong className="block text-sm text-slate-900">{patient.full_name}</strong><small className="text-xs text-slate-500">{patient.medical_number} · {patient.phone}</small></span></div></button>)}</div>
      </div>

      <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm">{!selected && <div className="flex min-h-64 flex-col items-center justify-center text-center text-slate-500"><FileHeart className="mb-3 h-12 w-12 text-blue-300" /><p>اختر مريضًا لفتح الملف الطبي</p></div>}{selected && <>{recordLoading ? <div className="flex min-h-64 items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-blue-600" /></div> : record && <div className="space-y-5"><div className="flex items-start justify-between gap-3 border-b border-slate-100 pb-4"><div><h2 className="text-xl font-bold text-slate-900">{record.patient.full_name}</h2><p className="mt-1 text-sm text-slate-500">{record.patient.medical_number} · آخر فحص: {record.patient.last_exam_date ? new Date(record.patient.last_exam_date).toLocaleDateString('ar-EG') : 'غير متاح'}</p></div><Button variant="ghost" size="icon" onClick={() => { setSelected(null); setRecord(null) }} aria-label="إغلاق الملف"><X className="h-4 w-4" /></Button></div><div className="grid gap-3 sm:grid-cols-2">{sections.map(([key, label]) => <div key={key} className="rounded-xl bg-slate-50 p-4"><div className="flex items-center justify-between"><h3 className="font-semibold text-slate-800">{label}</h3><span className="rounded-full bg-white px-2 py-1 text-xs text-blue-700">{record[key]?.length || 0}</span></div>{record[key]?.slice(0, 3).map(item => <p key={item.id} className="mt-2 truncate text-xs text-slate-500">{item.diagnosis || item.test_name || item.scan_type || item.name || 'سجل محفوظ'}</p>)}</div>)}</div><form onSubmit={submitReport} className="rounded-xl border border-teal-100 bg-teal-50/60 p-4"><h3 className="mb-3 font-bold text-teal-950">كتابة تقرير طبي جديد</h3><div className="grid gap-3 md:grid-cols-2"><Input value={reportForm.diagnosis} onChange={event => setReportForm(form => ({ ...form, diagnosis: event.target.value }))} placeholder="التشخيص" aria-label="التشخيص" /><Input value={reportForm.symptoms} onChange={event => setReportForm(form => ({ ...form, symptoms: event.target.value }))} placeholder="الأعراض" aria-label="الأعراض" /><textarea value={reportForm.treatment} onChange={event => setReportForm(form => ({ ...form, treatment: event.target.value }))} className="min-h-20 rounded-xl border border-slate-200 p-3 text-sm" placeholder="خطة العلاج" aria-label="خطة العلاج" /><textarea value={reportForm.notes} onChange={event => setReportForm(form => ({ ...form, notes: event.target.value }))} className="min-h-20 rounded-xl border border-slate-200 p-3 text-sm" placeholder="ملاحظات الطبيب" aria-label="ملاحظات الطبيب" /></div><Button type="submit" disabled={reportBusy} className="mt-3">{reportBusy ? 'جارٍ الحفظ...' : 'حفظ التقرير'}</Button></form><div className="rounded-xl border border-blue-100 bg-blue-50 p-4 text-sm text-blue-900">يمكن للطبيب فتح طلبات التحاليل والأشعة من القائمة العلوية، وكتابة الوصفة والتقرير بعد اختيار المريض من هذه الصفحة.</div></div>}</>}</div>
    </section>
  </div>
}
