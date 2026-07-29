import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Pill, Plus, Check, X, Clock, AlertCircle, Calendar,
  Activity, TrendingUp, ChevronDown, ChevronUp, Trash2, Edit
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

const API = (path) => `/api/medications${path}`
const authHeader = () => ({ 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` })

export default function MedicationTrackingPage() {
  const { user } = useAuth()
  const [medications, setMedications] = useState([])
  const [todaySummary, setTodaySummary] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAddForm, setShowAddForm] = useState(false)
  const [expandedMed, setExpandedMed] = useState(null)
  const [aiAnalysis, setAiAnalysis] = useState(null)
  const [aiLoading, setAiLoading] = useState(false)
  const [msg, setMsg] = useState(null)

  const [form, setForm] = useState({
    name: '', dosage: '', frequency: '', start_date: '', end_date: '',
    form: 'tablet', instructions: '', side_effects: '', schedule_times: ['08:00']
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
        setForm({ name: '', dosage: '', frequency: '', start_date: '', end_date: '', form: 'tablet', instructions: '', side_effects: '', schedule_times: ['08:00'] })
        fetchData()
      } else setMsg({ type: 'error', text: data.error || 'حدث خطأ' })
    } catch (e) { setMsg({ type: 'error', text: 'خطأ في الاتصال' }) }
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
    { value: 'مرة يومياً', label: 'مرة يومياً' },
    { value: 'مرتين يومياً', label: 'مرتين يومياً' },
    { value: 'ثلاث مرات يومياً', label: 'ثلاث مرات يومياً' },
    { value: 'كل 8 ساعات', label: 'كل 8 ساعات' },
    { value: 'كل 12 ساعة', label: 'كل 12 ساعة' },
    { value: 'عند الحاجة', label: 'عند الحاجة' },
    { value: 'أسبوعياً', label: 'أسبوعياً' },
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

  return (
    <div className="min-h-screen bg-gray-50 py-8" dir="rtl">
      <div className="max-w-5xl mx-auto px-4">

        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
              <Pill className="text-blue-600" size={32} />
              متابعة الأدوية
            </h1>
            <p className="text-gray-500 mt-1">تتبع جدول أدويتك وسجل تناولها يومياً</p>
          </div>
          <Button onClick={() => setShowAddForm(!showAddForm)} className="bg-blue-600 hover:bg-blue-700">
            <Plus size={18} className="ml-1" /> إضافة دواء
          </Button>
        </div>

        {msg && (
          <Alert className={`mb-4 ${msg.type === 'success' ? 'border-green-500' : 'border-red-500'}`}>
            <AlertDescription>{msg.text}</AlertDescription>
          </Alert>
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
                <p className="text-3xl font-bold text-purple-600">
                  {medications.length > 0
                    ? Math.round(medications.reduce((a, m) => a + (m.adherence_rate || 0), 0) / medications.length)
                    : 0}%
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
          {!aiAnalysis && <p className="text-gray-400 text-sm">اضغط على "حلل التزامي" للحصول على تقرير مخصص من الذكاء الاصطناعي</p>}
        </div>

        {/* Add Medication Form */}
        {showAddForm && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
            <h2 className="text-lg font-bold text-gray-800 mb-4">إضافة دواء جديد</h2>
            <form onSubmit={handleAddMedication} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label>اسم الدواء *</Label>
                  <Input value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))}
                    placeholder="مثال: باراسيتامول" required />
                </div>
                <div>
                  <Label>الجرعة *</Label>
                  <Input value={form.dosage} onChange={e => setForm(p => ({ ...p, dosage: e.target.value }))}
                    placeholder="مثال: 500 مغ" required />
                </div>
                <div>
                  <Label>التكرار *</Label>
                  <select value={form.frequency} onChange={e => setForm(p => ({ ...p, frequency: e.target.value }))}
                    className="w-full border rounded-md px-3 py-2 text-sm" required>
                    <option value="">اختر التكرار</option>
                    {frequencyOptions.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                  </select>
                </div>
                <div>
                  <Label>شكل الدواء</Label>
                  <select value={form.form} onChange={e => setForm(p => ({ ...p, form: e.target.value }))}
                    className="w-full border rounded-md px-3 py-2 text-sm">
                    {formOptions.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                  </select>
                </div>
                <div>
                  <Label>تاريخ البدء *</Label>
                  <Input type="date" value={form.start_date}
                    onChange={e => setForm(p => ({ ...p, start_date: e.target.value }))} required />
                </div>
                <div>
                  <Label>تاريخ الانتهاء</Label>
                  <Input type="date" value={form.end_date}
                    onChange={e => setForm(p => ({ ...p, end_date: e.target.value }))} />
                </div>
              </div>
              <div>
                <Label>التعليمات</Label>
                <Input value={form.instructions} onChange={e => setForm(p => ({ ...p, instructions: e.target.value }))}
                  placeholder="مثال: يؤخذ بعد الأكل" />
              </div>
              <div>
                <Label>مواعيد التذكير</Label>
                <div className="flex flex-wrap gap-2">
                  {form.schedule_times.map((t, i) => (
                    <div key={i} className="flex items-center gap-1">
                      <Input type="time" value={t}
                        onChange={e => { const arr = [...form.schedule_times]; arr[i] = e.target.value; setForm(p => ({ ...p, schedule_times: arr })) }}
                        className="w-32" />
                      {i > 0 && <button type="button" onClick={() => setForm(p => ({ ...p, schedule_times: p.schedule_times.filter((_, j) => j !== i) }))}
                        className="text-red-400 hover:text-red-600"><X size={14} /></button>}
                    </div>
                  ))}
                  <Button type="button" variant="outline" size="sm"
                    onClick={() => setForm(p => ({ ...p, schedule_times: [...p.schedule_times, '12:00'] }))}>
                    <Plus size={14} className="ml-1" /> إضافة موعد
                  </Button>
                </div>
              </div>
              <div className="flex gap-3">
                <Button type="submit" className="bg-blue-600 hover:bg-blue-700">حفظ الدواء</Button>
                <Button type="button" variant="outline" onClick={() => setShowAddForm(false)}>إلغاء</Button>
              </div>
            </form>
          </div>
        )}

        {/* Medications List */}
        <div className="space-y-3">
          <h2 className="text-lg font-bold text-gray-800">الأدوية النشطة ({medications.length})</h2>
          {medications.length === 0 && (
            <div className="bg-white rounded-xl p-8 text-center text-gray-400">
              <Pill size={48} className="mx-auto mb-3 opacity-30" />
              <p>لا توجد أدوية مسجلة</p>
              <Button onClick={() => setShowAddForm(true)} className="mt-3 bg-blue-600 hover:bg-blue-700">
                إضافة أول دواء
              </Button>
            </div>
          )}
          {medications.map(med => (
            <div key={med.id} className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="p-4 flex items-center justify-between cursor-pointer"
                onClick={() => setExpandedMed(expandedMed === med.id ? null : med.id)}>
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${med.adherence_rate >= 80 ? 'bg-green-100' : med.adherence_rate >= 50 ? 'bg-yellow-100' : 'bg-red-100'}`}>
                    <Pill size={20} className={med.adherence_rate >= 80 ? 'text-green-600' : med.adherence_rate >= 50 ? 'text-yellow-600' : 'text-red-600'} />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-800">{med.name}</p>
                    <p className="text-sm text-gray-500">{med.dosage} — {med.frequency}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-center">
                    <p className={`text-lg font-bold ${med.adherence_rate >= 80 ? 'text-green-600' : med.adherence_rate >= 50 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {med.adherence_rate}%
                    </p>
                    <p className="text-xs text-gray-400">الالتزام</p>
                  </div>
                  {expandedMed === med.id ? <ChevronUp size={18} className="text-gray-400" /> : <ChevronDown size={18} className="text-gray-400" />}
                </div>
              </div>
              {expandedMed === med.id && (
                <div className="border-t border-gray-100 p-4 bg-gray-50 space-y-3">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    {med.form && <div><span className="text-gray-400">الشكل:</span> <span className="text-gray-700">{med.form}</span></div>}
                    {med.start_date && <div><span className="text-gray-400">البدء:</span> <span className="text-gray-700">{med.start_date}</span></div>}
                    {med.end_date && <div><span className="text-gray-400">الانتهاء:</span> <span className="text-gray-700">{med.end_date}</span></div>}
                  </div>
                  {med.instructions && <p className="text-sm text-gray-600">📋 {med.instructions}</p>}
                  {med.schedules?.length > 0 && (
                    <div>
                      <p className="text-xs font-medium text-gray-400 mb-1">مواعيد التذكير:</p>
                      <div className="flex gap-2 flex-wrap">
                        {med.schedules.map(s => (
                          <span key={s.id} className="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded-full">
                            <Clock size={10} className="inline ml-1" />{s.time_of_day}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  <div className="flex gap-2">
                    <Button size="sm" onClick={() => logMedication(med.id, 'taken')}
                      className="bg-green-500 hover:bg-green-600 text-white text-xs">
                      <Check size={14} className="ml-1" /> تناولت الآن
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => logMedication(med.id, 'missed')}
                      className="text-red-500 border-red-300 text-xs">
                      تفويت
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
