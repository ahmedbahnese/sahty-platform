import { useEffect, useMemo, useState } from 'react'
import {
  Activity, AlertTriangle, Beaker, CalendarDays, ChevronDown, ClipboardList,
  FileHeart, FlaskConical, HeartPulse, Loader2, Pill, Plus, Search, Stethoscope,
  Syringe, UserRound, X, ArrowUpRight, Clock3, ShieldCheck, ScanLine,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuth } from '../contexts/AuthContext'

const tabs = [
  ['summary', 'ملخص المريض', FileHeart],
  ['problems', 'مشكلات المريض', AlertTriangle],
  ['orders', 'الطلبات', ClipboardList],
  ['sheets', 'السجلات', ClipboardList],
  ['notes', 'الملاحظات السريرية', Stethoscope],
  ['vitals', 'العلامات الحيوية', HeartPulse],
  ['bmi', 'BMI', Activity],
]


const formatDate = value => value ? new Date(value).toLocaleDateString('ar-EG') : 'غير مسجل'
const display = value => value === null || value === undefined || value === '' ? 'غير مسجل' : value

function Metric({ label, value, icon: Icon, tone = 'blue' }) {
  const tones = {
    blue: 'border-blue-100 bg-blue-50 text-blue-700',
    teal: 'border-teal-100 bg-teal-50 text-teal-700',
    amber: 'border-amber-100 bg-amber-50 text-amber-700',
    rose: 'border-rose-100 bg-rose-50 text-rose-700',
  }
  return <div className={`rounded-xl border p-3 ${tones[tone]}`}><div className="flex items-center gap-2 text-xs font-semibold"><Icon className="h-4 w-4" />{label}</div><p className="mt-2 text-lg font-bold text-slate-900">{value}</p></div>
}

function RecordList({ items, empty = 'لا توجد سجلات محفوظة' }) {
  if (!items?.length) return <p className="rounded-xl bg-slate-50 p-6 text-center text-sm text-slate-500">{empty}</p>
  return <div className="space-y-2">{items.map((item, index) => <div key={item.id || `${item.created_at || item.test_date || index}`} className="rounded-xl border border-slate-100 bg-white p-3"><div className="flex items-start justify-between gap-3"><div><p className="font-semibold text-slate-800">{display(item.diagnosis || item.test_name || item.scan_type || item.name || item.title || 'سجل طبي')}</p><p className="mt-1 text-xs text-slate-500">{formatDate(item.visit_date || item.test_date || item.scan_date || item.created_at || item.start_date)}</p></div>{item.status && <span className="rounded-full bg-blue-50 px-2 py-1 text-xs text-blue-700">{item.status}</span>}</div>{(item.notes || item.result || item.treatment || item.findings) && <p className="mt-2 whitespace-pre-line text-sm text-slate-600">{item.notes || item.result || item.treatment || item.findings}</p>}</div>)}</div>
}

function PatientHeader({ patient, onClose }) {
  return <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
    <div className="flex items-center justify-between border-b border-slate-200 bg-gradient-to-l from-[#063b70] via-[#087f9b] to-[#12b8c6] px-4 py-2 text-white"><div className="flex items-center gap-2 text-sm"><span className="font-bold">ملف المريض</span><span className="text-cyan-100">/</span><span>لوحة الطبيب</span></div><div className="flex gap-2"><button className="rounded-lg p-2 hover:bg-white/10" title="إغلاق الملف" onClick={onClose}><X className="h-4 w-4" /></button></div></div>
    <div className="grid gap-4 px-5 py-4 lg:grid-cols-[1.4fr_1fr_1fr]">
      <div className="flex items-center gap-3"><span className="rounded-full bg-cyan-50 p-3 text-cyan-700"><UserRound className="h-6 w-6" /></span><div><h2 className="text-xl font-bold text-slate-900">{patient.full_name}</h2><p className="mt-1 text-sm text-slate-500">{patient.medical_number} · {display(patient.phone)}</p></div></div>
      <div className="grid grid-cols-2 gap-3 text-sm"><div><span className="text-slate-400">العمر</span><strong className="block text-slate-800">{display(patient.age || patient.date_of_birth ? (patient.age || formatDate(patient.date_of_birth)) : 'غير مسجل')}</strong></div><div><span className="text-slate-400">النوع</span><strong className="block text-slate-800">{display(patient.gender)}</strong></div></div>
      <div className="text-sm"><span className="text-slate-400">آخر فحص</span><strong className="mt-1 block text-slate-800">{formatDate(patient.last_exam_date)}</strong><span className="mt-1 flex items-center gap-1 text-xs text-emerald-600"><ShieldCheck className="h-3.5 w-3.5" />وصول الطبيب مصرح</span></div>
    </div>
  </div>
}

export default function DoctorPatientsPage() {
  const { token } = useAuth()
  const [search, setSearch] = useState('')
  const [examDate, setExamDate] = useState('')
  const [patients, setPatients] = useState([])
  const [selected, setSelected] = useState(null)
  const [record, setRecord] = useState(null)
  const [activeTab, setActiveTab] = useState('summary')
  const [ordersOpen, setOrdersOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [recordLoading, setRecordLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [reportForm, setReportForm] = useState({ diagnosis: '', symptoms: '', treatment: '', notes: '' })
  const [reportBusy, setReportBusy] = useState(false)

  const headers = useMemo(() => ({ Authorization: `Bearer ${token}` }), [token])
  const loadPatients = async () => {
    setLoading(true); setMessage('')
    try {
      const params = new URLSearchParams()
      if (search.trim()) params.set('search', search.trim())
      if (examDate) params.set('exam_date', examDate)
      const response = await fetch(`/api/doctors/me/patients?${params}`, { headers })
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || data.message || 'تعذر تحميل المرضى')
      setPatients(data.patients || [])
    } catch (error) { setMessage(error.message) } finally { setLoading(false) }
  }

  useEffect(() => { loadPatients() }, [token])

  const openRecord = async patient => {
    setSelected(patient); setActiveTab('summary'); setRecordLoading(true); setMessage('')
    try {
      const response = await fetch(`/api/doctors/me/patients/${patient.id}/medical-record`, { headers })
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || 'تعذر فتح الملف الطبي')
      setRecord(data)
    } catch (error) { setMessage(error.message); setRecord(null) } finally { setRecordLoading(false) }
  }

  const closeRecord = () => { setSelected(null); setRecord(null); setActiveTab('summary') }

  const submitReport = async event => {
    event.preventDefault(); if (!selected) return
    setReportBusy(true)
    try {
      const response = await fetch(`/api/doctors/me/patients/${selected.id}/medical-records`, { method: 'POST', headers: { ...headers, 'Content-Type': 'application/json' }, body: JSON.stringify(reportForm) })
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || 'تعذر حفظ التقرير')
      setRecord(previous => ({ ...previous, medical_records: [data.record, ...(previous.medical_records || [])] }))
      setReportForm({ diagnosis: '', symptoms: '', treatment: '', notes: '' }); setMessage('تم حفظ التقرير الطبي داخل ملف المريض'); setActiveTab('notes')
    } catch (error) { setMessage(error.message) } finally { setReportBusy(false) }
  }

  const renderTab = () => {
    if (!record) return null
    const vitals = record.medical_records?.find(item => item.vital_signs)?.vital_signs || {}
    if (activeTab === 'summary') return <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4"><Metric label="السجلات الطبية" value={record.medical_records?.length || 0} icon={FileHeart} /><Metric label="التحاليل" value={record.lab_tests?.length || 0} icon={FlaskConical} tone="teal" /><Metric label="الأشعات" value={record.radiology?.length || 0} icon={ScanLine} tone="amber" /><Metric label="الأدوية" value={record.medications?.length || 0} icon={Pill} tone="rose" /><div className="md:col-span-2 xl:col-span-4 grid gap-4 lg:grid-cols-2"><div className="rounded-xl border border-slate-100 bg-slate-50 p-4"><h3 className="mb-3 flex items-center gap-2 font-bold text-slate-800"><AlertTriangle className="h-4 w-4 text-amber-600" />الحساسيات</h3><RecordList items={record.allergies} empty="لا توجد حساسيات مسجلة" /></div><div className="rounded-xl border border-slate-100 bg-slate-50 p-4"><h3 className="mb-3 flex items-center gap-2 font-bold text-slate-800"><Activity className="h-4 w-4 text-blue-600" />آخر السجلات</h3><RecordList items={record.medical_records?.slice(0, 4)} /></div></div></div>
    if (activeTab === 'problems') return <div className="grid gap-4 lg:grid-cols-2"><div className="rounded-xl border border-slate-100 bg-slate-50 p-4"><h3 className="mb-3 font-bold text-slate-800">التشخيصات والأمراض</h3><RecordList items={record.diseases} empty="لا توجد تشخيصات مسجلة" /></div><div className="rounded-xl border border-slate-100 bg-slate-50 p-4"><h3 className="mb-3 font-bold text-slate-800">العمليات والتطعيمات</h3><RecordList items={[...(record.surgeries || []), ...(record.vaccinations || [])]} empty="لا توجد سجلات" /></div></div>
    if (activeTab === 'orders') return <div className="grid gap-4 lg:grid-cols-3"><div className="rounded-xl border border-slate-100 bg-slate-50 p-4"><h3 className="mb-3 flex items-center gap-2 font-bold"><Beaker className="h-4 w-4 text-teal-600" />طلبات التحاليل</h3><RecordList items={record.lab_requests} /></div><div className="rounded-xl border border-slate-100 bg-slate-50 p-4"><h3 className="mb-3 flex items-center gap-2 font-bold"><ScanLine className="h-4 w-4 text-indigo-600" />طلبات الأشعة</h3><RecordList items={record.radiology_requests} /></div><div className="rounded-xl border border-slate-100 bg-slate-50 p-4"><h3 className="mb-3 flex items-center gap-2 font-bold"><Pill className="h-4 w-4 text-rose-600" />الأدوية والوصفات</h3><RecordList items={record.medications} /></div></div>
    if (activeTab === 'sheets') return <div className="rounded-xl border border-slate-100 bg-slate-50 p-4"><h3 className="mb-3 font-bold text-slate-800">السجلات والتقارير الطبية</h3><RecordList items={record.medical_records} /></div>
    if (activeTab === 'notes') return <div className="space-y-4"><div className="rounded-xl border border-teal-100 bg-teal-50/60 p-4"><h3 className="mb-3 flex items-center gap-2 font-bold text-teal-950"><Plus className="h-4 w-4" />إضافة ملاحظة أو تقرير سريري</h3><form onSubmit={submitReport} className="grid gap-3 md:grid-cols-2"><Input value={reportForm.diagnosis} onChange={e => setReportForm(f => ({ ...f, diagnosis: e.target.value }))} placeholder="التشخيص" aria-label="التشخيص" /><Input value={reportForm.symptoms} onChange={e => setReportForm(f => ({ ...f, symptoms: e.target.value }))} placeholder="الأعراض" aria-label="الأعراض" /><textarea value={reportForm.treatment} onChange={e => setReportForm(f => ({ ...f, treatment: e.target.value }))} className="min-h-24 rounded-xl border border-slate-200 p-3 text-sm" placeholder="خطة العلاج" aria-label="خطة العلاج" /><textarea value={reportForm.notes} onChange={e => setReportForm(f => ({ ...f, notes: e.target.value }))} className="min-h-24 rounded-xl border border-slate-200 p-3 text-sm" placeholder="الملاحظات السريرية" aria-label="الملاحظات السريرية" /><Button type="submit" disabled={reportBusy} className="md:col-span-2">{reportBusy ? 'جارٍ الحفظ...' : 'حفظ التقرير في الملف'}</Button></form></div><RecordList items={record.medical_records} /></div>
    if (activeTab === 'vitals') return <div className="rounded-xl border border-slate-100 bg-slate-50 p-4"><h3 className="mb-4 flex items-center gap-2 font-bold"><HeartPulse className="h-5 w-5 text-rose-600" />العلامات الحيوية المسجلة</h3>{Object.keys(vitals).length ? <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{Object.entries(vitals).map(([key, value]) => <Metric key={key} label={key} value={display(value)} icon={Activity} />)}</div> : <p className="rounded-xl bg-white p-6 text-center text-sm text-slate-500">لا توجد علامات حيوية مسجلة في السجل المتاح.</p>}</div>
    return <div className="rounded-xl border border-slate-100 bg-slate-50 p-6 text-center"><Activity className="mx-auto mb-3 h-10 w-10 text-blue-300" /><h3 className="font-bold text-slate-800">مؤشر كتلة الجسم</h3><p className="mt-2 text-sm text-slate-500">{display(vitals.bmi || vitals.BMI)}</p></div>
  }

  return <div className="space-y-5">
    <header className="rounded-2xl bg-gradient-to-l from-[#063b70] to-[#0b9ca8] p-6 text-white shadow-sm"><p className="text-sm text-cyan-100">لوحة الطبيب</p><h1 className="mt-2 text-2xl font-bold">إدارة المرضى والملفات السريرية</h1><p className="mt-2 text-sm text-cyan-50">ابحث بالاسم أو الرقم الطبي أو الهاتف أو تاريخ الفحص، ثم افتح الملف المصرح لك به.</p></header>
    <section className="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm"><div className="grid gap-3 md:grid-cols-[1fr_220px_auto]"><div className="relative"><Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" /><Input value={search} onChange={e => setSearch(e.target.value)} onKeyDown={e => e.key === 'Enter' && loadPatients()} className="pr-10" placeholder="اسم المريض، الرقم الطبي، الهاتف أو الرقم القومي" aria-label="بحث عن مريض" /></div><div className="relative"><CalendarDays className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" /><Input value={examDate} onChange={e => setExamDate(e.target.value)} className="pr-10" type="date" aria-label="تاريخ الفحص" /></div><Button onClick={loadPatients} disabled={loading}>{loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'بحث'}</Button></div></section>
    {message && <div role="alert" className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-rose-800">{message}</div>}
    <section className="grid gap-4 lg:grid-cols-[minmax(280px,350px)_1fr]"><aside className="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm"><div className="mb-3 flex items-center justify-between"><h2 className="font-bold text-slate-900">قائمة المرضى</h2><span className="rounded-full bg-blue-50 px-2 py-1 text-xs text-blue-700">{patients.length}</span></div><div className="space-y-2">{patients.length === 0 && <p className="rounded-xl bg-slate-50 p-6 text-center text-sm text-slate-500">لا توجد نتائج. ابحث عن مريض مرتبط بمواعيدك.</p>}{patients.map(patient => <button key={patient.id} onClick={() => openRecord(patient)} className={`w-full rounded-xl border p-3 text-right transition hover:border-cyan-300 hover:bg-cyan-50 ${selected?.id === patient.id ? 'border-cyan-500 bg-cyan-50' : 'border-slate-100'}`}><div className="flex items-center gap-3"><span className="rounded-full bg-cyan-100 p-2 text-cyan-700"><UserRound className="h-4 w-4" /></span><span><strong className="block text-sm text-slate-900">{patient.full_name}</strong><small className="text-xs text-slate-500">{patient.medical_number} · {patient.phone}</small></span></div></button>)}</div></aside>
      <div className="min-w-0 rounded-2xl border border-slate-100 bg-white p-3 shadow-sm">{!selected && <div className="flex min-h-72 flex-col items-center justify-center text-center text-slate-500"><FileHeart className="mb-3 h-14 w-14 text-cyan-300" /><p className="font-semibold">اختر مريضاً لفتح الملف السريري</p><p className="mt-1 text-sm">ستظهر هنا البيانات المصرح بها للطبيب فقط.</p></div>}{selected && (recordLoading ? <div className="flex min-h-72 items-center justify-center"><Loader2 className="h-8 w-8 animate-spin text-cyan-600" /></div> : record && <div className="space-y-3"><PatientHeader patient={record.patient} onClose={closeRecord} /><nav className="flex gap-1 overflow-x-auto border-b border-slate-200 pb-1" aria-label="أقسام الملف السريري">{tabs.map(([key, label, Icon]) => <button key={key} onClick={() => setActiveTab(key)} className={`flex shrink-0 items-center gap-2 rounded-t-lg px-3 py-3 text-xs font-semibold transition ${activeTab === key ? 'border-b-2 border-cyan-600 bg-cyan-50 text-cyan-800' : 'text-slate-500 hover:bg-slate-50 hover:text-slate-800'}`}><Icon className="h-4 w-4" />{label}</button>)}<div className="relative mr-auto"><button onClick={() => setOrdersOpen(value => !value)} className="flex items-center gap-1 rounded-lg px-3 py-3 text-xs font-semibold text-slate-600 hover:bg-slate-50"><ClipboardList className="h-4 w-4" />إجراءات<ChevronDown className="h-3 w-3" /></button>{ordersOpen && <div className="absolute left-0 top-11 z-10 w-48 rounded-xl border border-slate-200 bg-white p-2 text-sm shadow-xl"><button onClick={() => { setActiveTab('orders'); setOrdersOpen(false) }} className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-right hover:bg-cyan-50"><FlaskConical className="h-4 w-4" />طلبات التحاليل والأشعة</button><button onClick={() => { setActiveTab('notes'); setOrdersOpen(false) }} className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-right hover:bg-cyan-50"><Stethoscope className="h-4 w-4" />ملاحظة سريرية</button><button onClick={() => { setActiveTab('orders'); setOrdersOpen(false) }} className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-right hover:bg-cyan-50"><Pill className="h-4 w-4" />الأدوية</button></div>}</div></nav><div className="rounded-xl bg-white p-1">{renderTab()}</div></div>)}</div>
    </section>
  </div>
}
