import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Pill, Plus, Check, X, Clock, AlertCircle, Calendar,
  Activity, TrendingUp, ChevronDown, ChevronUp, Trash2, Edit,
  Download, Bell, Users, BarChart3,
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

const API = (path) => `/api/medications${path}`
const authHeader = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('token')}`,
})

export default function MedicationTrackingPage() {
  const { user } = useAuth()
  const [medications, setMedications] = useState([])
  const [todaySummary, setTodaySummary] = useState([])
  const [adherenceStats, setAdherenceStats] = useState(null)
  const [prescriptions, setPrescriptions] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [showImport, setShowImport] = useState(false)
  const [showStats, setShowStats] = useState(false)
  const [expandedMed, setExpandedMed] = useState(null)
  const [aiAnalysis, setAiAnalysis] = useState(null)
  const [aiLoading, setAiLoading] = useState(false)
  const [msg, setMsg] = useState(null)
  const [importBusy, setImportBusy] = useState(false)
  const [importOptions, setImportOptions] = useState({ notify_family: false, notify_doctor_on_missed: false })

  const [form, setForm] = useState({
    name: '', dosage: '', frequency: '', start_date: '', end_date: '',
    form: 'tablet', instructions: '', side_effects: '', schedule_times: ['08:00'],
    notify_family: false, notify_doctor_on_missed: false, missed_dose_threshold: 3,
  })

  useEffect(() => { fetchData() }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [medsRes, todayRes] = await Promise.all([
        fetch(API('/'), { headers: authHeader() }),
        fetch(API('/today-summary'), { headers: authHeader() })
      ])
      const medsData = await medsRes.json()
      const todayData = await todayRes.json()
      if (medsData.success) setMedications(medsData.medications)
      if (todayData.success) setTodaySummary(todayData.summary)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const fetchStats = async () => {
    try {
      const res = await fetch(API('/adherence-stats'), { headers: authHeader() })
      const data = await res.json()
      if (data.success) setAdherenceStats(data)
    } catch (e) { console.error(e) }
  }

  const fetchPrescriptions = async () => {
    try {
      const res = await fetch('/api/prescriptions?status=active', { headers: authHeader() })
      const data = await res.json()
      if (Array.isArray(data)) setPrescriptions(data)
      else if (data.prescriptions) setPrescriptions(data.prescriptions)
    } catch (e) { console.error(e) }
  }

  const handleAddMedication = async (e) => {
    e.preventDefault()
    try {
      const res = await fetch(API('/'), {
        method: 'POST', headers: authHeader(),
        body: JSON.stringify({ ...form, schedule_times: form.schedule_times.filter(Boolean) })
      })
      const data = await res.json()
      if (data.success) {
        setMsg({ type: 'success', text: 'تم إضافة الدواء بنجاح' })
        setShowAddForm(false)
        setForm({ name: '', dosage: '', frequency: '', start_date: '', end_date: '', form: 'tablet', instructions: '', side_effects: '', schedule_times: ['08:00'], notify_family: false, notify_doctor_on_missed: false, missed_dose_threshold: 3 })
        fetchData()
      } else setMsg({ type: 'error', text: data.error || 'حدث خطأ' })
    } catch (e) { setMsg({ type: 'error', text: 'خطأ في الاتصال' }) }
  }

  const handleImportFromPrescription = async (prescriptionId) => {
    setImportBusy(true)
    try {
      const res = await fetch(API(`/import-from-prescription/${prescriptionId}`), {
        method: 'POST', headers: authHeader(),
        body: JSON.stringify(importOptions),
      })
      const data = await res.json()
      if (data.success) {
        setMsg({ type: 'success', text: `تم استيراد ${data.imported} دواء من الوصفة بنجاح` })
        setShowImport(false)
        fetchData()
      } else setMsg({ type: 'error', text: data.error || 'حدث خطأ' })
    } catch (e) { setMsg({ type: 'error', text: 'خطأ في الاتصال' }) }
    setImportBusy(false)
  }

  const logMedication = async (medId, status) => {
    try {
      const res = await fetch(API(`/${medId}/log`), {
        method: 'POST', headers: authHeader(),
        body: JSON.stringify({ status })
      })
      const data = await res.json()
      if (data.success) {
        setMsg({ type: 'success', text: status === 'taken' ? 'تم تسجيل تناول الدواء ✓' : 'تم تسجيل تفويت الدواء' })
        fetchData()
      }
    } catch (e) { console.error(e) }
  }

  const deleteMedication = async (medId) => {
    try {
      await fetch(API(`/${medId}`), { method: 'DELETE', headers: authHeader() })
      fetchData()
    } catch (e) { console.error(e) }
  }

  const runAIAnalysis = async () => {
    setAiLoading(true)
    try {
      const res = await fetch('/api/ai/medication-adherence', { headers: authHeader() })
      const data = await res.json()
      if (data.success) setAiAnalysis(data.analysis)
      else setMsg({ type: 'error', text: data.error || 'لم يتمكن الذكاء الاصطناعي من التحليل' })
    } catch (e) { setMsg({ type: 'error', text: 'خطأ في التحليل' }) }
    setAiLoading(false)
  }

  const frequencyOptions = [
    'مرة يومياً', 'مرتين يومياً', 'ثلاث مرات يومياً',
    'كل 8 ساعات', 'كل 12 ساعة', 'عند الحاجة', 'أسبوعياً',
  ]

  const formOptions = [
    { value: 'tablet', label: 'قرص' },
    { value: 'capsule', label: 'كبسولة' },
    { value: 'syrup', label: 'شراب' },
    { value: 'injection', label: 'حقنة' },
    { value: 'drops', label: 'قطرات' },
    { value: 'cream', label: 'كريم' },
  ]

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
    </div>
  )

  const todayDone = todaySummary.filter(s => s.is_complete).length
  const todayTotal = todaySummary.length
  const avgAdherence = medications.length > 0
    ? Math.round(medications.reduce((a, m) => a + (m.adherence_rate || 0), 0) / medications.length)
    : 0

  return (
    <div className="min-h-screen bg-gray-50 py-8" dir="rtl">
      <div className="max-w-5xl mx-auto px-4">

        {/* Header */}
        <div className="flex flex-wrap items-center justify-between mb-8 gap-3">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Pill className="text-blue-600" size={32} />
              متابعة الأدوية
            </h1>
            <p className="text-gray-500 mt-1">تتبع جدول أدويتك وسجل تناولها يومياً</p>
          </div>
          <div className="flex gap-2 flex-wrap">
            <Button variant="outline" onClick={async () => { setShowImport(v => !v); if (!showImport) await fetchPrescriptions() }}
              className="border-green-300 text-green-700 hover:bg-green-50">
              <Download size={16} className="ml-1" /> استيراد من وصفة
            </Button>
            <Button variant="outline" onClick={async () => { setShowStats(v => !v); if (!showStats) await fetchStats() }}
              className="border-purple-300 text-purple-700 hover:bg-purple-50">
              <BarChart3 size={16} className="ml-1" /> إحصائيات الالتزام
            </Button>
            <Button onClick={() => setShowAddForm(!showAddForm)} className="bg-blue-600 hover:bg-blue-700">
              <Plus size={18} className="ml-1" /> إضافة دواء
            </Button>
          </div>
        </div>

        {msg && (
          <Alert className={`mb-4 ${msg.type === 'success' ? 'border-green-500' : 'border-red-500'}`}>
            <AlertDescription className="flex items-center justify-between">
              {msg.text}
              <button onClick={() => setMsg(null)} className="text-gray-400 hover:text-gray-600 text-xs ml-3">✕</button>
            </AlertDescription>
          </Alert>
        )}

        {/* استيراد من وصفة */}
        {showImport && (
          <div className="bg-white rounded-xl shadow-sm border border-green-100 p-5 mb-6">
            <h2 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <Download size={20} className="text-green-600" /> استيراد الأدوية من وصفة طبيب
            </h2>
            <div className="flex gap-4 mb-4 text-sm">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={importOptions.notify_family}
                  onChange={e => setImportOptions(o => ({ ...o, notify_family: e.target.checked }))}
                  className="w-4 h-4 rounded text-blue-600" />
                <span className="flex items-center gap-1"><Users size={14} className="text-blue-500" /> إشعار أفراد الأسرة عند التفويت</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={importOptions.notify_doctor_on_missed}
                  onChange={e => setImportOptions(o => ({ ...o, notify_doctor_on_missed: e.target.checked }))}
                  className="w-4 h-4 rounded text-blue-600" />
                <span className="flex items-center gap-1"><Bell size={14} className="text-orange-500" /> إشعار الطبيب عند التفويت المتكرر</span>
              </label>
            </div>
            {prescriptions.length === 0 ? (
              <p className="text-gray-400 text-sm py-4 text-center">لا توجد وصفات نشطة متاحة للاستيراد</p>
            ) : (
              <div className="space-y-2">
                {prescriptions.map(rx => (
                  <div key={rx.id} className="flex items-center justify-between bg-gray-50 rounded-lg p-3 border border-gray-100">
                    <div className="text-sm">
                      <p className="font-medium text-gray-800">
                        وصفة #{rx.id} — {rx.items?.length || 0} دواء
                      </p>
                      <p className="text-gray-400 text-xs">{rx.created_at ? new Date(rx.created_at).toLocaleDateString('ar-SA') : ''}</p>
                    </div>
                    <button
                      disabled={importBusy}
                      onClick={() => handleImportFromPrescription(rx.id)}
                      className="bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded-lg text-xs font-medium disabled:opacity-60">
                      {importBusy ? 'جاري...' : 'استيراد'}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* إحصائيات الالتزام */}
        {showStats && adherenceStats && (
          <div className="bg-white rounded-xl shadow-sm border border-purple-100 p-5 mb-6">
            <h2 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <BarChart3 size={20} className="text-purple-600" /> إحصائيات الالتزام (آخر {adherenceStats.period_days} يوماً)
            </h2>
            <div className="flex items-center gap-4 mb-4">
              <div className="text-center">
                <p className="text-4xl font-bold text-purple-600">{adherenceStats.overall_adherence_rate}%</p>
                <p className="text-sm text-gray-500">معدل الالتزام الإجمالي</p>
              </div>
            </div>
            <div className="space-y-3">
              {adherenceStats.medications.map(stat => (
                <div key={stat.medication_id} className="flex items-center gap-3">
                  <div className="flex-1">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="font-medium text-gray-700">{stat.medication_name} ({stat.dosage})</span>
                      <span className={`font-bold ${stat.adherence_rate >= 80 ? 'text-green-600' : stat.adherence_rate >= 50 ? 'text-orange-500' : 'text-red-600'}`}>
                        {stat.adherence_rate}%
                      </span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full transition-all ${stat.adherence_rate >= 80 ? 'bg-green-500' : stat.adherence_rate >= 50 ? 'bg-orange-500' : 'bg-red-500'}`}
                        style={{ width: `${stat.adherence_rate}%` }} />
                    </div>
                    <p className="text-xs text-gray-400 mt-0.5">
                      أُخذ {stat.taken} · فُوِّت {stat.missed} · تُجووّز {stat.skipped}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Today Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">جرعات اليوم</p>
                <p className="text-3xl font-bold text-blue-600">{todayDone}/{todayTotal}</p>
              </div>
              <Calendar className="text-blue-400" size={36} />
            </div>
          </div>
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">الأدوية النشطة</p>
                <p className="text-3xl font-bold text-green-600">{medications.length}</p>
              </div>
              <Activity className="text-green-400" size={36} />
            </div>
          </div>
          <div className="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">متوسط الالتزام</p>
                <p className={`text-3xl font-bold ${avgAdherence >= 80 ? 'text-green-600' : avgAdherence >= 50 ? 'text-orange-500' : 'text-purple-600'}`}>
                  {avgAdherence}%
                </p>
              </div>
              <TrendingUp className="text-purple-400" size={36} />
            </div>
          </div>
        </div>

        {/* Today's Schedule */}
        {todaySummary.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 mb-6">
            <h2 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <Clock size={20} className="text-blue-500" /> جدول اليوم
            </h2>
            <div className="space-y-3">
              {todaySummary.map((item, i) => (
                <div key={i} className={`flex items-center justify-between p-3 rounded-lg ${item.is_complete ? 'bg-green-50' : 'bg-gray-50'}`}>
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${item.is_complete ? 'bg-green-500' : 'bg-gray-300'}`} />
                    <div>
                      <p className="font-medium text-gray-800">{item.medication.name}</p>
                      <p className="text-sm text-gray-500">{item.medication.dosage} — {item.medication.frequency}</p>
                      {item.medication.source === 'prescription' && (
                        <span className="text-xs text-green-600 bg-green-50 px-1.5 py-0.5 rounded">من وصفة طبيب</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400">{item.taken_today}/{item.total_doses_today}</span>
                    {!item.is_complete && (
                      <>
                        <Button size="sm" onClick={() => logMedication(item.medication.id, 'taken')}
                          className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 text-xs">
                          <Check size={14} className="ml-1" /> تناولت
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => logMedication(item.medication.id, 'missed')}
                          className="text-red-500 border-red-300 px-3 py-1 text-xs">
                          <X size={14} className="ml-1" /> فوّت
                        </Button>
                      </>
                    )}
                    {item.is_complete && <span className="text-green-600 text-sm font-medium">✓ مكتمل</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* AI Analysis */}
        <div className="bg-white rounded-xl shadow-sm border border-blue-100 p-5 mb-6">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-bold text-gray-800 flex items-center gap-2">
              <Activity size={20} className="text-purple-500" /> تحليل الالتزام بالذكاء الاصطناعي
            </h2>
            <Button onClick={runAIAnalysis} disabled={aiLoading} variant="outline"
              className="border-purple-300 text-purple-600 hover:bg-purple-50">
              {aiLoading ? 'جار التحليل...' : '🤖 حلل التزامي'}
            </Button>
          </div>
          {aiAnalysis && (
            <div className="bg-purple-50 rounded-lg p-4 text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
              {aiAnalysis}
            </div>
          )}
          {!aiAnalysis && <p className="text-gray-400 text-sm">اضغط على "حلل التزامي" للحصول على تقرير مخصص</p>}
        </div>

        {/* Add Medication Form */}
        {showAddForm && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
            <h2 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
              <Plus size={20} className="text-blue-600" /> إضافة دواء للمتابعة
            </h2>
            <form onSubmit={handleAddMedication} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label>اسم الدواء *</Label>
                  <Input required value={form.name} onChange={e => setForm(f => ({...f, name: e.target.value}))} placeholder="اسم الدواء" className="mt-1" />
                </div>
                <div>
                  <Label>الجرعة *</Label>
                  <Input required value={form.dosage} onChange={e => setForm(f => ({...f, dosage: e.target.value}))} placeholder="مثال: 500mg" className="mt-1" />
                </div>
                <div>
                  <Label>الشكل الدوائي</Label>
                  <select value={form.form} onChange={e => setForm(f => ({...f, form: e.target.value}))}
                    className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                    {formOptions.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                  </select>
                </div>
                <div>
                  <Label>التكرار *</Label>
                  <select required value={form.frequency} onChange={e => setForm(f => ({...f, frequency: e.target.value}))}
                    className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <option value="">-- اختر --</option>
                    {frequencyOptions.map(o => <option key={o} value={o}>{o}</option>)}
                  </select>
                </div>
                <div>
                  <Label>تاريخ البدء *</Label>
                  <Input required type="date" value={form.start_date} onChange={e => setForm(f => ({...f, start_date: e.target.value}))} className="mt-1" />
                </div>
                <div>
                  <Label>تاريخ الانتهاء</Label>
                  <Input type="date" value={form.end_date} onChange={e => setForm(f => ({...f, end_date: e.target.value}))} className="mt-1" />
                </div>
              </div>

              <div>
                <Label>أوقات التذكير</Label>
                <div className="flex flex-wrap gap-2 mt-1">
                  {form.schedule_times.map((t, i) => (
                    <div key={i} className="flex items-center gap-1">
                      <input type="time" value={t}
                        onChange={e => setForm(f => ({ ...f, schedule_times: f.schedule_times.map((v, j) => j === i ? e.target.value : v) }))}
                        className="border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
                      {i > 0 && (
                        <button type="button" onClick={() => setForm(f => ({ ...f, schedule_times: f.schedule_times.filter((_, j) => j !== i) }))}
                          className="text-red-400 hover:text-red-600"><X size={14} /></button>
                      )}
                    </div>
                  ))}
                  <button type="button" onClick={() => setForm(f => ({ ...f, schedule_times: [...f.schedule_times, '12:00'] }))}
                    className="text-blue-600 hover:text-blue-800 text-xs flex items-center gap-1 border border-blue-200 px-2 py-1 rounded-lg">
                    <Plus size={12} /> إضافة وقت
                  </button>
                </div>
              </div>

              <div>
                <Label>تعليمات خاصة</Label>
                <Input value={form.instructions} onChange={e => setForm(f => ({...f, instructions: e.target.value}))} placeholder="مثال: بعد الأكل" className="mt-1" />
              </div>

              {/* إعدادات الإشعارات */}
              <div className="bg-blue-50 rounded-xl p-4 border border-blue-100">
                <h4 className="text-sm font-semibold text-blue-800 mb-3 flex items-center gap-1"><Bell size={14}/> إعدادات الإشعارات</h4>
                <div className="space-y-2">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" checked={form.notify_family}
                      onChange={e => setForm(f => ({...f, notify_family: e.target.checked}))}
                      className="w-4 h-4 rounded text-blue-600" />
                    <span className="text-sm text-gray-700 flex items-center gap-1"><Users size={13} className="text-blue-500"/> إشعار أفراد الأسرة عند تفويت جرعة</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" checked={form.notify_doctor_on_missed}
                      onChange={e => setForm(f => ({...f, notify_doctor_on_missed: e.target.checked}))}
                      className="w-4 h-4 rounded text-blue-600" />
                    <span className="text-sm text-gray-700 flex items-center gap-1"><Bell size={13} className="text-orange-500"/> إشعار الطبيب عند تكرار التفويت</span>
                  </label>
                  {form.notify_doctor_on_missed && (
                    <div className="flex items-center gap-2 mt-1 mr-6">
                      <span className="text-xs text-gray-500">إشعار الطبيب بعد</span>
                      <input type="number" min={1} max={10} value={form.missed_dose_threshold}
                        onChange={e => setForm(f => ({...f, missed_dose_threshold: parseInt(e.target.value)}))}
                        className="w-14 border border-gray-200 rounded px-2 py-1 text-sm text-center" />
                      <span className="text-xs text-gray-500">جرعات فائتة</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="flex gap-3 justify-end">
                <Button type="button" variant="outline" onClick={() => setShowAddForm(false)}>إلغاء</Button>
                <Button type="submit" className="bg-blue-600 hover:bg-blue-700">حفظ الدواء</Button>
              </div>
            </form>
          </div>
        )}

        {/* Medications List */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-gray-800">أدويتي النشطة ({medications.length})</h2>
          {medications.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-xl border border-gray-100">
              <Pill size={40} className="mx-auto mb-3 text-gray-300" />
              <p className="text-gray-400">لا توجد أدوية مضافة</p>
              <p className="text-sm text-gray-400 mt-1">أضف دواء يدوياً أو استورد من وصفة طبيبك</p>
            </div>
          ) : (
            medications.map(med => (
              <div key={med.id} className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50"
                  onClick={() => setExpandedMed(expandedMed === med.id ? null : med.id)}>
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${med.is_active ? 'bg-blue-50 text-blue-600' : 'bg-gray-50 text-gray-400'}`}>
                      <Pill size={18} />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-semibold text-gray-800">{med.name}</p>
                        {med.source === 'prescription' && (
                          <span className="text-xs text-green-600 bg-green-50 px-1.5 py-0.5 rounded">وصفة طبيب</span>
                        )}
                        {med.notify_family && <Users size={12} className="text-blue-500" title="إشعار الأسرة مفعّل" />}
                        {med.notify_doctor_on_missed && <Bell size={12} className="text-orange-500" title="إشعار الطبيب مفعّل" />}
                      </div>
                      <p className="text-sm text-gray-500">{med.dosage} — {med.frequency}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-center">
                      <p className={`text-lg font-bold ${med.adherence_rate >= 80 ? 'text-green-600' : med.adherence_rate >= 50 ? 'text-orange-500' : 'text-red-500'}`}>
                        {med.adherence_rate}%
                      </p>
                      <p className="text-xs text-gray-400">التزام</p>
                    </div>
                    <button onClick={e => { e.stopPropagation(); deleteMedication(med.id) }}
                      className="p-1.5 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                      <Trash2 size={15} />
                    </button>
                    {expandedMed === med.id ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
                  </div>
                </div>

                {expandedMed === med.id && (
                  <div className="border-t border-gray-50 p-4 bg-gray-50/50">
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm mb-3">
                      {med.form && <div><span className="text-gray-500">الشكل: </span><span className="font-medium">{med.form}</span></div>}
                      {med.start_date && <div><span className="text-gray-500">البدء: </span><span className="font-medium">{med.start_date}</span></div>}
                      {med.end_date && <div><span className="text-gray-500">الانتهاء: </span><span className="font-medium">{med.end_date}</span></div>}
                      {med.instructions && <div className="col-span-2"><span className="text-gray-500">التعليمات: </span><span>{med.instructions}</span></div>}
                    </div>
                    {med.schedules?.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-3">
                        {med.schedules.map((s, i) => (
                          <span key={i} className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded-full flex items-center gap-1">
                            <Clock size={10} /> {s.time_of_day?.slice(0, 5)}
                          </span>
                        ))}
                      </div>
                    )}
                    <div className="flex gap-2 mt-2">
                      <button onClick={() => logMedication(med.id, 'taken')}
                        className="flex items-center gap-1 bg-green-50 text-green-700 border border-green-200 hover:bg-green-100 px-3 py-1.5 rounded-lg text-xs font-medium">
                        <Check size={13}/> تناولت الآن
                      </button>
                      <button onClick={() => logMedication(med.id, 'missed')}
                        className="flex items-center gap-1 bg-red-50 text-red-700 border border-red-200 hover:bg-red-100 px-3 py-1.5 rounded-lg text-xs font-medium">
                        <X size={13}/> سجّل تفويتاً
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
