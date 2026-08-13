import { useState, useEffect, useCallback, useRef } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Badge } from '../components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import {
  Activity, AlertTriangle, Pill, Syringe, FlaskConical,
  RadioTower, History, Stethoscope, Plus, Pencil, Trash2,
  ClipboardList, Loader2, FileText, Camera, Upload, X,
  Weight, Ruler, Droplets, Heart, CheckCircle2, Clock,
  AlertCircle, ChevronDown, ChevronUp, FileDown, User, Building2,
  ZoomIn, Zap
} from 'lucide-react'

const API = '/api/medical-record'

function useApi(token) {
  const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
  const get = (path) => fetch(`${API}${path}`, { headers }).then(r => r.json())
  const post = (path, body) => fetch(`${API}${path}`, { method: 'POST', headers, body: JSON.stringify(body) }).then(r => r.json())
  const put = (path, body) => fetch(`${API}${path}`, { method: 'PUT', headers, body: JSON.stringify(body) }).then(r => r.json())
  const del = (path) => fetch(`${API}${path}`, { method: 'DELETE', headers }).then(r => r.json())
  return { get, post, put, del }
}

function FieldRow({ label, value, children }) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs font-medium text-gray-500">{label}</label>
      {children || <p className="text-sm text-gray-800">{value || '—'}</p>}
    </div>
  )
}

const severityColors = { mild: 'bg-yellow-100 text-yellow-800', moderate: 'bg-orange-100 text-orange-800', severe: 'bg-red-100 text-red-800' }
const statusColors = { active: 'bg-blue-100 text-blue-800', chronic: 'bg-purple-100 text-purple-800', resolved: 'bg-green-100 text-green-800', normal: 'bg-green-100 text-green-800', abnormal: 'bg-orange-100 text-orange-800', critical: 'bg-red-100 text-red-800' }
const statusLabels = { active: 'نشط', chronic: 'مزمن', resolved: 'شُفي', normal: 'طبيعي', abnormal: 'غير طبيعي', critical: 'حرج' }
const severityLabels = { mild: 'خفيف', moderate: 'متوسط', severe: 'شديد' }
const scanTypeLabels = { xray: 'أشعة X', mri: 'رنين مغناطيسي', ct: 'أشعة مقطعية', ultrasound: 'موجات صوتية', pet: 'PET Scan', mammo: 'ماموجرام' }
const outcomeLabels = { successful: 'ناجحة', complicated: 'مع مضاعفات', failed: 'فاشلة' }

// ── مكوّن رفع/تصوير صورة ──
function ImageUpload({ label, value, onChange }) {
  const inputRef = useRef()

  const handleChange = (e) => {
    const file = e.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => onChange(reader.result)
    reader.readAsDataURL(file)
  }

  const handleCamera = () => {
    inputRef.current.setAttribute('capture', 'environment')
    inputRef.current.click()
  }
  const handleUpload = () => {
    inputRef.current.removeAttribute('capture')
    inputRef.current.click()
  }

  return (
    <div className="col-span-2">
      <label className="text-xs font-medium text-gray-500 block mb-1.5">{label}</label>
      <input ref={inputRef} type="file" accept="image/*" onChange={handleChange} className="hidden" />
      {value ? (
        <div className="relative rounded-lg border border-gray-200 overflow-hidden bg-gray-50">
          <img src={value} alt="صورة مرفقة" className="w-full max-h-52 object-contain" />
          <button
            type="button"
            onClick={() => onChange(null)}
            className="absolute top-2 left-2 bg-red-500 hover:bg-red-600 text-white rounded-full w-7 h-7 flex items-center justify-center shadow"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ) : (
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleCamera}
            className="flex-1 border-2 border-dashed border-gray-300 rounded-lg py-3 px-2 text-sm text-gray-500 hover:border-blue-400 hover:text-blue-600 flex items-center justify-center gap-1.5 transition-colors"
          >
            <Camera className="w-4 h-4" /> تصوير
          </button>
          <button
            type="button"
            onClick={handleUpload}
            className="flex-1 border-2 border-dashed border-gray-300 rounded-lg py-3 px-2 text-sm text-gray-500 hover:border-blue-400 hover:text-blue-600 flex items-center justify-center gap-1.5 transition-colors"
          >
            <Upload className="w-4 h-4" /> رفع صورة
          </button>
        </div>
      )}
    </div>
  )
}

// ── بطاقة المقاييس الحيوية للمريض ──
function PatientVitalsCard({ api }) {
  const [profile, setProfile] = useState(null)
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({})
  const [loading, setLoading] = useState(false)

  const load = useCallback(() => {
    api.get('/patient-profile').then(d => {
      if (d.id) { setProfile(d); setForm({ height: d.height || '', weight: d.weight || '', blood_type: d.blood_type || '' }) }
    })
  }, [api])

  useEffect(() => { load() }, [load])

  const save = async () => {
    setLoading(true)
    await api.put('/patient-vitals', form)
    setLoading(false)
    setEditing(false)
    load()
  }

  if (!profile) return null

  const age = profile.date_of_birth ? (() => {
    const dob = new Date(profile.date_of_birth)
    const today = new Date()
    let y = today.getFullYear() - dob.getFullYear()
    const m = today.getMonth() - dob.getMonth()
    if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) y--
    return y
  })() : null

  const bmi = profile.height && profile.weight
    ? (profile.weight / Math.pow(profile.height / 100, 2)).toFixed(1)
    : null

  const bloodTypeColors = { 'A+': 'bg-red-100 text-red-800', 'A-': 'bg-red-100 text-red-800', 'B+': 'bg-blue-100 text-blue-800', 'B-': 'bg-blue-100 text-blue-800', 'AB+': 'bg-purple-100 text-purple-800', 'AB-': 'bg-purple-100 text-purple-800', 'O+': 'bg-green-100 text-green-800', 'O-': 'bg-green-100 text-green-800' }

  return (
    <Card className="mb-6 border-blue-100 bg-gradient-to-l from-blue-50 to-white shadow-sm">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3 flex-wrap flex-1">
            <div className="flex items-center gap-1.5 bg-white rounded-lg px-3 py-2 border shadow-sm">
              <User className="w-4 h-4 text-blue-500" />
              <span className="text-sm font-semibold text-gray-800">{profile.first_name} {profile.last_name}</span>
              {age !== null && <span className="text-xs text-gray-500">({age} سنة)</span>}
            </div>
            {profile.blood_type && (
              <div className={`flex items-center gap-1.5 rounded-lg px-3 py-2 border shadow-sm ${bloodTypeColors[profile.blood_type] || 'bg-gray-100'}`}>
                <Droplets className="w-4 h-4" />
                <span className="text-sm font-bold">{profile.blood_type}</span>
              </div>
            )}
            {profile.height && (
              <div className="flex items-center gap-1.5 bg-white rounded-lg px-3 py-2 border shadow-sm">
                <Ruler className="w-4 h-4 text-teal-500" />
                <span className="text-sm text-gray-700">{profile.height} سم</span>
              </div>
            )}
            {profile.weight && (
              <div className="flex items-center gap-1.5 bg-white rounded-lg px-3 py-2 border shadow-sm">
                <Weight className="w-4 h-4 text-orange-500" />
                <span className="text-sm text-gray-700">{profile.weight} كجم</span>
              </div>
            )}
            {bmi && (
              <div className="flex items-center gap-1.5 bg-white rounded-lg px-3 py-2 border shadow-sm">
                <Activity className="w-4 h-4 text-indigo-500" />
                <span className="text-sm text-gray-700">BMI: {bmi}</span>
              </div>
            )}
            {profile.allergies?.length > 0 && (
              <div className="flex items-center gap-1.5 bg-red-50 rounded-lg px-3 py-2 border border-red-200 shadow-sm">
                <AlertTriangle className="w-4 h-4 text-red-500" />
                <span className="text-sm text-red-700 font-medium">
                  حساسية: {profile.allergies.map(a => a.allergen).join('، ')}
                </span>
              </div>
            )}
          </div>
          <Button size="sm" variant="outline" onClick={() => setEditing(true)} className="shrink-0">
            <Pencil className="w-3.5 h-3.5 ml-1" /> تعديل
          </Button>
        </div>
      </CardContent>

      <Dialog open={editing} onOpenChange={setEditing}>
        <DialogContent className="max-w-md" dir="rtl">
          <DialogHeader><DialogTitle>تحديث البيانات الحيوية</DialogTitle></DialogHeader>
          <div className="grid grid-cols-2 gap-4 py-2">
            <div>
              <label className="text-xs font-medium text-gray-600 block mb-1">الطول (سم)</label>
              <Input type="number" placeholder="170" value={form.height || ''} onChange={e => setForm({ ...form, height: e.target.value })} />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-600 block mb-1">الوزن (كجم)</label>
              <Input type="number" placeholder="70" value={form.weight || ''} onChange={e => setForm({ ...form, weight: e.target.value })} />
            </div>
            <div className="col-span-2">
              <label className="text-xs font-medium text-gray-600 block mb-1">فصيلة الدم</label>
              <Select value={form.blood_type || ''} onValueChange={v => setForm({ ...form, blood_type: v })}>
                <SelectTrigger><SelectValue placeholder="اختر فصيلة الدم" /></SelectTrigger>
                <SelectContent>
                  {['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'].map(bt => (
                    <SelectItem key={bt} value={bt}>{bt}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditing(false)}>إلغاء</Button>
            <Button onClick={save} disabled={loading} className="bg-blue-600 hover:bg-blue-700">
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'حفظ'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  )
}

// ── قائمة عامة ──
function SectionList({ items, renderCard, onAdd, addLabel }) {
  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <Button onClick={onAdd} className="gap-2 bg-blue-600 hover:bg-blue-700">
          <Plus className="w-4 h-4" /> {addLabel}
        </Button>
      </div>
      {items.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <FileText className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>لا توجد سجلات بعد</p>
        </div>
      ) : (
        <div className="grid gap-4">{items.map(renderCard)}</div>
      )}
    </div>
  )
}

// ══════════════════════════════════════════════
// الأمراض
// ══════════════════════════════════════════════
function DiseasesTab({ api }) {
  const [items, setItems] = useState([])
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({})
  const [loading, setLoading] = useState(false)

  const load = useCallback(() => api.get('/diseases').then(d => Array.isArray(d) && setItems(d)), [api])
  useEffect(() => { load() }, [load])

  const openAdd = () => { setEditing(null); setForm({ status: 'active' }); setOpen(true) }
  const openEdit = (item) => { setEditing(item); setForm({ ...item }); setOpen(true) }
  const save = async () => {
    setLoading(true)
    const res = editing ? await api.put(`/diseases/${editing.id}`, form) : await api.post('/diseases', form)
    setLoading(false)
    if (res.id) { load(); setOpen(false) }
  }
  const remove = async (id) => { if (confirm('هل تريد حذف هذا السجل؟')) { await api.del(`/diseases/${id}`); load() } }

  return (
    <>
      <SectionList items={items} addLabel="إضافة مرض" onAdd={openAdd} renderCard={(d) => (
        <Card key={d.id} className="border-r-4 border-r-blue-500">
          <CardContent className="p-5">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 grid grid-cols-2 md:grid-cols-3 gap-4">
                <FieldRow label="اسم المرض" value={d.name} />
                <FieldRow label="رمز ICD" value={d.icd_code} />
                <FieldRow label="الحالة"><Badge className={statusColors[d.status] || 'bg-gray-100'}>{statusLabels[d.status] || d.status}</Badge></FieldRow>
                <FieldRow label="الشدة">{d.severity && <Badge className={severityColors[d.severity]}>{severityLabels[d.severity]}</Badge>}</FieldRow>
                <FieldRow label="تاريخ التشخيص" value={d.diagnosis_date} />
                <FieldRow label="الطبيب المعالج" value={d.treating_doctor} />
                {d.notes && <div className="col-span-full"><FieldRow label="ملاحظات" value={d.notes} /></div>}
                {d.attachment_data && (
                  <div className="col-span-full">
                    <p className="text-xs font-medium text-gray-500 mb-1">الروشتة المرفقة</p>
                    <img src={d.attachment_data} alt="الروشتة" className="max-h-32 rounded border object-contain bg-gray-50" />
                  </div>
                )}
              </div>
              <div className="flex gap-2 shrink-0">
                <Button size="icon" variant="ghost" onClick={() => openEdit(d)}><Pencil className="w-4 h-4" /></Button>
                <Button size="icon" variant="ghost" className="text-red-500" onClick={() => remove(d.id)}><Trash2 className="w-4 h-4" /></Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )} />

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-lg" dir="rtl">
          <DialogHeader><DialogTitle>{editing ? 'تعديل' : 'إضافة'} مرض</DialogTitle></DialogHeader>
          <div className="grid grid-cols-2 gap-4 py-2">
            <div className="col-span-2"><Input placeholder="اسم المرض *" value={form.name || ''} onChange={e => setForm({ ...form, name: e.target.value })} /></div>
            <Input placeholder="رمز ICD" value={form.icd_code || ''} onChange={e => setForm({ ...form, icd_code: e.target.value })} />
            <Select value={form.status || 'active'} onValueChange={v => setForm({ ...form, status: v })}>
              <SelectTrigger><SelectValue placeholder="الحالة" /></SelectTrigger>
              <SelectContent><SelectItem value="active">نشط</SelectItem><SelectItem value="chronic">مزمن</SelectItem><SelectItem value="resolved">شُفي</SelectItem></SelectContent>
            </Select>
            <Select value={form.severity || ''} onValueChange={v => setForm({ ...form, severity: v })}>
              <SelectTrigger><SelectValue placeholder="الشدة" /></SelectTrigger>
              <SelectContent><SelectItem value="mild">خفيف</SelectItem><SelectItem value="moderate">متوسط</SelectItem><SelectItem value="severe">شديد</SelectItem></SelectContent>
            </Select>
            <Input type="date" value={form.diagnosis_date || ''} onChange={e => setForm({ ...form, diagnosis_date: e.target.value })} />
            <Input placeholder="الطبيب المعالج" value={form.treating_doctor || ''} onChange={e => setForm({ ...form, treating_doctor: e.target.value })} />
            <Input placeholder="المستشفى / العيادة" value={form.hospital || ''} onChange={e => setForm({ ...form, hospital: e.target.value })} />
            <Input type="date" value={form.resolution_date || ''} onChange={e => setForm({ ...form, resolution_date: e.target.value })} />
            <div className="col-span-2"><Input placeholder="ملخص العلاج" value={form.treatment_summary || ''} onChange={e => setForm({ ...form, treatment_summary: e.target.value })} /></div>
            <div className="col-span-2"><Input placeholder="ملاحظات" value={form.notes || ''} onChange={e => setForm({ ...form, notes: e.target.value })} /></div>
            <ImageUpload label="📋 صورة الروشتة (اختياري)" value={form.attachment_data || null} onChange={v => setForm({ ...form, attachment_data: v })} />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>إلغاء</Button>
            <Button onClick={save} disabled={loading} className="bg-blue-600 hover:bg-blue-700">{loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'حفظ'}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

// ══════════════════════════════════════════════
// العمليات الجراحية
// ══════════════════════════════════════════════
function SurgeriesTab({ api }) {
  const [items, setItems] = useState([])
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({})
  const [loading, setLoading] = useState(false)

  const load = useCallback(() => api.get('/surgeries').then(d => Array.isArray(d) && setItems(d)), [api])
  useEffect(() => { load() }, [load])

  const openAdd = () => { setEditing(null); setForm({ outcome: 'successful' }); setOpen(true) }
  const openEdit = (item) => { setEditing(item); setForm({ ...item }); setOpen(true) }
  const save = async () => {
    setLoading(true)
    const res = editing ? await api.put(`/surgeries/${editing.id}`, form) : await api.post('/surgeries', form)
    setLoading(false)
    if (res.id) { load(); setOpen(false) }
  }
  const remove = async (id) => { if (confirm('هل تريد حذف هذا السجل؟')) { await api.del(`/surgeries/${id}`); load() } }

  return (
    <>
      <SectionList items={items} addLabel="إضافة عملية" onAdd={openAdd} renderCard={(s) => (
        <Card key={s.id} className="border-r-4 border-r-purple-500">
          <CardContent className="p-5">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 grid grid-cols-2 md:grid-cols-3 gap-4">
                <FieldRow label="اسم العملية" value={s.name} />
                <FieldRow label="النوع" value={s.surgery_type} />
                <FieldRow label="التاريخ" value={s.surgery_date} />
                <FieldRow label="الجراح" value={s.surgeon} />
                <FieldRow label="المستشفى" value={s.hospital} />
                <FieldRow label="النتيجة">{s.outcome && <Badge className={s.outcome === 'successful' ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'}>{outcomeLabels[s.outcome]}</Badge>}</FieldRow>
                {s.complications && <div className="col-span-full"><FieldRow label="مضاعفات" value={s.complications} /></div>}
              </div>
              <div className="flex gap-2 shrink-0">
                <Button size="icon" variant="ghost" onClick={() => openEdit(s)}><Pencil className="w-4 h-4" /></Button>
                <Button size="icon" variant="ghost" className="text-red-500" onClick={() => remove(s.id)}><Trash2 className="w-4 h-4" /></Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )} />

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-lg" dir="rtl">
          <DialogHeader><DialogTitle>{editing ? 'تعديل' : 'إضافة'} عملية جراحية</DialogTitle></DialogHeader>
          <div className="grid grid-cols-2 gap-4 py-2">
            <div className="col-span-2"><Input placeholder="اسم العملية *" value={form.name || ''} onChange={e => setForm({ ...form, name: e.target.value })} /></div>
            <Input placeholder="نوع العملية" value={form.surgery_type || ''} onChange={e => setForm({ ...form, surgery_type: e.target.value })} />
            <Input type="date" value={form.surgery_date || ''} onChange={e => setForm({ ...form, surgery_date: e.target.value })} />
            <Input placeholder="الجراح" value={form.surgeon || ''} onChange={e => setForm({ ...form, surgeon: e.target.value })} />
            <Input placeholder="المستشفى" value={form.hospital || ''} onChange={e => setForm({ ...form, hospital: e.target.value })} />
            <Select value={form.anesthesia_type || ''} onValueChange={v => setForm({ ...form, anesthesia_type: v })}>
              <SelectTrigger><SelectValue placeholder="نوع التخدير" /></SelectTrigger>
              <SelectContent><SelectItem value="general">عامة</SelectItem><SelectItem value="local">موضعية</SelectItem><SelectItem value="spinal">نخاعية</SelectItem><SelectItem value="epidural">فوق الجافية</SelectItem></SelectContent>
            </Select>
            <Select value={form.outcome || 'successful'} onValueChange={v => setForm({ ...form, outcome: v })}>
              <SelectTrigger><SelectValue placeholder="النتيجة" /></SelectTrigger>
              <SelectContent><SelectItem value="successful">ناجحة</SelectItem><SelectItem value="complicated">مع مضاعفات</SelectItem><SelectItem value="failed">فاشلة</SelectItem></SelectContent>
            </Select>
            <div className="col-span-2"><Input placeholder="مضاعفات (إن وجدت)" value={form.complications || ''} onChange={e => setForm({ ...form, complications: e.target.value })} /></div>
            <div className="col-span-2"><Input placeholder="ملاحظات ما بعد العملية" value={form.post_op_notes || ''} onChange={e => setForm({ ...form, post_op_notes: e.target.value })} /></div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>إلغاء</Button>
            <Button onClick={save} disabled={loading} className="bg-blue-600 hover:bg-blue-700">{loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'حفظ'}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

// ══════════════════════════════════════════════
// الحساسية
// ══════════════════════════════════════════════
function AllergiesTab({ api }) {
  const [items, setItems] = useState([])
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({})
  const [loading, setLoading] = useState(false)

  const load = useCallback(() => api.get('/allergies').then(d => Array.isArray(d) && setItems(d)), [api])
  useEffect(() => { load() }, [load])

  const openAdd = () => { setEditing(null); setForm({}); setOpen(true) }
  const openEdit = (item) => { setEditing(item); setForm({ ...item }); setOpen(true) }
  const save = async () => {
    setLoading(true)
    const res = editing ? await api.put(`/allergies/${editing.id}`, form) : await api.post('/allergies', form)
    setLoading(false)
    if (res.id) { load(); setOpen(false) }
  }
  const remove = async (id) => { if (confirm('هل تريد حذف هذا السجل؟')) { await api.del(`/allergies/${id}`); load() } }

  return (
    <>
      <SectionList items={items} addLabel="إضافة حساسية" onAdd={openAdd} renderCard={(a) => (
        <Card key={a.id} className="border-r-4 border-r-red-400">
          <CardContent className="p-5">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 grid grid-cols-2 md:grid-cols-3 gap-4">
                <FieldRow label="المسبب" value={a.allergen} />
                <FieldRow label="الشدة">{a.severity && <Badge className={severityColors[a.severity]}>{severityLabels[a.severity]}</Badge>}</FieldRow>
                <FieldRow label="رد الفعل" value={a.reaction} />
                {a.notes && <FieldRow label="ملاحظات" value={a.notes} />}
              </div>
              <div className="flex gap-2 shrink-0">
                <Button size="icon" variant="ghost" onClick={() => openEdit(a)}><Pencil className="w-4 h-4" /></Button>
                <Button size="icon" variant="ghost" className="text-red-500" onClick={() => remove(a.id)}><Trash2 className="w-4 h-4" /></Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )} />

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-md" dir="rtl">
          <DialogHeader><DialogTitle>{editing ? 'تعديل' : 'إضافة'} حساسية</DialogTitle></DialogHeader>
          <div className="grid gap-4 py-2">
            <Input placeholder="المسبب للحساسية *" value={form.allergen || ''} onChange={e => setForm({ ...form, allergen: e.target.value })} />
            <Select value={form.severity || ''} onValueChange={v => setForm({ ...form, severity: v })}>
              <SelectTrigger><SelectValue placeholder="الشدة" /></SelectTrigger>
              <SelectContent><SelectItem value="mild">خفيفة</SelectItem><SelectItem value="moderate">متوسطة</SelectItem><SelectItem value="severe">شديدة</SelectItem></SelectContent>
            </Select>
            <Input placeholder="رد الفعل" value={form.reaction || ''} onChange={e => setForm({ ...form, reaction: e.target.value })} />
            <Input placeholder="ملاحظات" value={form.notes || ''} onChange={e => setForm({ ...form, notes: e.target.value })} />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>إلغاء</Button>
            <Button onClick={save} disabled={loading} className="bg-blue-600 hover:bg-blue-700">{loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'حفظ'}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

// ══════════════════════════════════════════════
// الأدوية
// ══════════════════════════════════════════════
function MedicationsTab({ api }) {
  const [items, setItems] = useState([])
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({})
  const [loading, setLoading] = useState(false)

  const load = useCallback(() => api.get('/medications').then(d => Array.isArray(d) && setItems(d)), [api])
  useEffect(() => { load() }, [load])

  const openAdd = () => { setEditing(null); setForm({ is_active: true, start_date: new Date().toISOString().split('T')[0] }); setOpen(true) }
  const openEdit = (item) => { setEditing(item); setForm({ ...item }); setOpen(true) }
  const save = async () => {
    setLoading(true)
    const res = editing ? await api.put(`/medications/${editing.id}`, form) : await api.post('/medications', form)
    setLoading(false)
    if (res.id) { load(); setOpen(false) }
  }
  const remove = async (id) => { if (confirm('هل تريد حذف هذا السجل؟')) { await api.del(`/medications/${id}`); load() } }

  const active = items.filter(m => m.is_active)
  const inactive = items.filter(m => !m.is_active)

  const MedCard = ({ m }) => (
    <Card className={`border-r-4 ${m.is_active ? 'border-r-green-500' : 'border-r-gray-300 opacity-75'}`}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 grid grid-cols-2 md:grid-cols-3 gap-4">
            <FieldRow label="اسم الدواء" value={m.name} />
            <FieldRow label="الجرعة" value={m.dosage} />
            <FieldRow label="التكرار" value={m.frequency} />
            <FieldRow label="الشكل" value={m.form} />
            <FieldRow label="من" value={m.start_date} />
            <FieldRow label="إلى" value={m.end_date} />
            <FieldRow label="الحالة"><Badge className={m.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}>{m.is_active ? 'جارٍ' : 'منتهٍ'}</Badge></FieldRow>
            {m.instructions && <FieldRow label="التعليمات" value={m.instructions} />}
            {m.attachment_data && (
              <div className="col-span-full">
                <p className="text-xs font-medium text-gray-500 mb-1">الروشتة المرفقة</p>
                <img src={m.attachment_data} alt="الروشتة" className="max-h-32 rounded border object-contain bg-gray-50" />
              </div>
            )}
          </div>
          <div className="flex gap-2 shrink-0">
            <Button size="icon" variant="ghost" onClick={() => openEdit(m)}><Pencil className="w-4 h-4" /></Button>
            <Button size="icon" variant="ghost" className="text-red-500" onClick={() => remove(m.id)}><Trash2 className="w-4 h-4" /></Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  return (
    <>
      <div className="flex justify-end mb-4">
        <Button onClick={openAdd} className="gap-2 bg-blue-600 hover:bg-blue-700"><Plus className="w-4 h-4" /> إضافة دواء</Button>
      </div>
      {items.length === 0 ? (
        <div className="text-center py-16 text-gray-400"><FileText className="w-12 h-12 mx-auto mb-3 opacity-30" /><p>لا توجد سجلات بعد</p></div>
      ) : (
        <div className="space-y-6">
          {active.length > 0 && <div><h3 className="text-sm font-semibold text-green-700 mb-3 flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-green-500 inline-block" />الأدوية الحالية</h3><div className="grid gap-3">{active.map(m => <MedCard key={m.id} m={m} />)}</div></div>}
          {inactive.length > 0 && <div><h3 className="text-sm font-semibold text-gray-500 mb-3 flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-gray-400 inline-block" />الأدوية السابقة</h3><div className="grid gap-3">{inactive.map(m => <MedCard key={m.id} m={m} />)}</div></div>}
        </div>
      )}

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-lg" dir="rtl">
          <DialogHeader><DialogTitle>{editing ? 'تعديل' : 'إضافة'} دواء</DialogTitle></DialogHeader>
          <div className="grid grid-cols-2 gap-4 py-2">
            <div className="col-span-2"><Input placeholder="اسم الدواء *" value={form.name || ''} onChange={e => setForm({ ...form, name: e.target.value })} /></div>
            <Input placeholder="الجرعة *" value={form.dosage || ''} onChange={e => setForm({ ...form, dosage: e.target.value })} />
            <Input placeholder="التكرار *" value={form.frequency || ''} onChange={e => setForm({ ...form, frequency: e.target.value })} />
            <Select value={form.form || ''} onValueChange={v => setForm({ ...form, form: v })}>
              <SelectTrigger><SelectValue placeholder="الشكل" /></SelectTrigger>
              <SelectContent><SelectItem value="tablet">قرص</SelectItem><SelectItem value="capsule">كبسولة</SelectItem><SelectItem value="syrup">شراب</SelectItem><SelectItem value="injection">حقنة</SelectItem><SelectItem value="drops">قطرة</SelectItem><SelectItem value="cream">مرهم</SelectItem></SelectContent>
            </Select>
            <Input placeholder="المدة" value={form.duration || ''} onChange={e => setForm({ ...form, duration: e.target.value })} />
            <div><label className="text-xs text-gray-500 mb-1 block">تاريخ البداية</label><Input type="date" value={form.start_date || ''} onChange={e => setForm({ ...form, start_date: e.target.value })} /></div>
            <div><label className="text-xs text-gray-500 mb-1 block">تاريخ الانتهاء</label><Input type="date" value={form.end_date || ''} onChange={e => setForm({ ...form, end_date: e.target.value })} /></div>
            <div className="col-span-2"><Input placeholder="تعليمات خاصة" value={form.instructions || ''} onChange={e => setForm({ ...form, instructions: e.target.value })} /></div>
            <ImageUpload label="📋 صورة الروشتة (اختياري)" value={form.attachment_data || null} onChange={v => setForm({ ...form, attachment_data: v })} />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>إلغاء</Button>
            <Button onClick={save} disabled={loading} className="bg-blue-600 hover:bg-blue-700">{loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'حفظ'}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

// ══════════════════════════════════════════════
// التطعيمات — مع جدول حسب العمر
// ══════════════════════════════════════════════

// جدول التطعيمات المصري
const VACCINE_SCHEDULE = [
  // إجبارية
  { key: 'bcg', nameAr: 'BCG (السل)', disease: 'السل', ageMonths: 0, ageLabel: 'عند الولادة', category: 'mandatory' },
  { key: 'hepb1', nameAr: 'التهاب الكبد B (1)', disease: 'التهاب الكبد B', ageMonths: 0, ageLabel: 'عند الولادة', category: 'mandatory' },
  { key: 'opv0', nameAr: 'شلل الأطفال الفموي (0)', disease: 'شلل الأطفال', ageMonths: 0, ageLabel: 'عند الولادة', category: 'mandatory' },
  { key: 'penta1', nameAr: 'الخماسي (1)', disease: 'دفتيريا / سعال / كزاز / هيموفيليس / كبد B', ageMonths: 2, ageLabel: 'شهران', category: 'mandatory' },
  { key: 'opv1', nameAr: 'شلل الأطفال الفموي (1)', disease: 'شلل الأطفال', ageMonths: 2, ageLabel: 'شهران', category: 'mandatory' },
  { key: 'pcv1', nameAr: 'المكورات الرئوية (1)', disease: 'التهاب رئوي / سحايا', ageMonths: 2, ageLabel: 'شهران', category: 'mandatory' },
  { key: 'rota1', nameAr: 'روتا فيروس (1)', disease: 'إسهال حاد', ageMonths: 2, ageLabel: 'شهران', category: 'mandatory' },
  { key: 'penta2', nameAr: 'الخماسي (2)', disease: 'دفتيريا / سعال / كزاز / هيموفيليس / كبد B', ageMonths: 4, ageLabel: '4 أشهر', category: 'mandatory' },
  { key: 'opv2', nameAr: 'شلل الأطفال الفموي (2)', disease: 'شلل الأطفال', ageMonths: 4, ageLabel: '4 أشهر', category: 'mandatory' },
  { key: 'pcv2', nameAr: 'المكورات الرئوية (2)', disease: 'التهاب رئوي / سحايا', ageMonths: 4, ageLabel: '4 أشهر', category: 'mandatory' },
  { key: 'rota2', nameAr: 'روتا فيروس (2)', disease: 'إسهال حاد', ageMonths: 4, ageLabel: '4 أشهر', category: 'mandatory' },
  { key: 'penta3', nameAr: 'الخماسي (3)', disease: 'دفتيريا / سعال / كزاز', ageMonths: 6, ageLabel: '6 أشهر', category: 'mandatory' },
  { key: 'opv3', nameAr: 'شلل الأطفال الفموي (3)', disease: 'شلل الأطفال', ageMonths: 6, ageLabel: '6 أشهر', category: 'mandatory' },
  { key: 'pcv3', nameAr: 'المكورات الرئوية (3)', disease: 'التهاب رئوي / سحايا', ageMonths: 6, ageLabel: '6 أشهر', category: 'mandatory' },
  { key: 'mmr1', nameAr: 'حصبة / حصبة ألمانية / نكاف (1)', disease: 'حصبة / حصبة ألمانية / نكاف', ageMonths: 9, ageLabel: '9 أشهر', category: 'mandatory' },
  { key: 'mena', nameAr: 'التهاب السحايا A', disease: 'التهاب السحايا البكتيري', ageMonths: 9, ageLabel: '9 أشهر', category: 'mandatory' },
  { key: 'varicella1', nameAr: 'جدري الماء (1)', disease: 'جدري الماء', ageMonths: 12, ageLabel: 'سنة', category: 'mandatory' },
  { key: 'hepa1', nameAr: 'التهاب الكبد A (1)', disease: 'التهاب الكبد A', ageMonths: 12, ageLabel: 'سنة', category: 'mandatory' },
  { key: 'penta4', nameAr: 'الخماسي منشط', disease: 'دفتيريا / سعال / كزاز', ageMonths: 18, ageLabel: '18 شهراً', category: 'mandatory' },
  { key: 'opv4', nameAr: 'شلل الأطفال الفموي (4)', disease: 'شلل الأطفال', ageMonths: 18, ageLabel: '18 شهراً', category: 'mandatory' },
  { key: 'mmr2', nameAr: 'حصبة / حصبة ألمانية / نكاف (2)', disease: 'حصبة / حصبة ألمانية / نكاف', ageMonths: 18, ageLabel: '18 شهراً', category: 'mandatory' },
  { key: 'dt_boost', nameAr: 'دفتيريا / كزاز (جرعة منشطة)', disease: 'دفتيريا / كزاز', ageMonths: 48, ageLabel: '4-5 سنوات', category: 'mandatory' },
  { key: 'opv5', nameAr: 'شلل الأطفال الفموي (5)', disease: 'شلل الأطفال', ageMonths: 48, ageLabel: '4-5 سنوات', category: 'mandatory' },
  { key: 'td', nameAr: 'كزاز / دفتيريا للمراهقين', disease: 'كزاز / دفتيريا', ageMonths: 132, ageLabel: '11-12 سنة', category: 'mandatory' },
  // إضافية
  { key: 'flu', nameAr: 'الإنفلونزا الموسمية (سنوياً)', disease: 'الإنفلونزا', ageMonths: 6, ageLabel: 'من 6 أشهر — سنوياً', category: 'optional' },
  { key: 'typhoid', nameAr: 'التيفود', disease: 'حمى التيفود', ageMonths: 24, ageLabel: 'من سنتين', category: 'optional' },
  { key: 'hpv', nameAr: 'فيروس الورم الحليمي (HPV)', disease: 'سرطان عنق الرحم', ageMonths: 132, ageLabel: '11-12 سنة (إناث)', category: 'optional' },
  { key: 'hepa2', nameAr: 'التهاب الكبد A (2)', disease: 'التهاب الكبد A', ageMonths: 18, ageLabel: '18-24 شهراً', category: 'optional' },
  { key: 'varicella2', nameAr: 'جدري الماء (2)', disease: 'جدري الماء', ageMonths: 48, ageLabel: '4-6 سنوات', category: 'optional' },
  { key: 'pneumo_adult', nameAr: 'المكورات الرئوية للبالغين', disease: 'التهاب رئوي', ageMonths: 780, ageLabel: 'من 65 سنة', category: 'optional' },
]

function VaccinationsTab({ api }) {
  const [given, setGiven] = useState([])
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({})
  const [loading, setLoading] = useState(false)
  const [patient, setPatient] = useState(null)
  const [activeView, setActiveView] = useState('schedule') // 'schedule' | 'given'

  const loadGiven = useCallback(() => api.get('/vaccinations').then(d => Array.isArray(d) && setGiven(d)), [api])
  const loadPatient = useCallback(() => api.get('/patient-profile').then(d => d.id && setPatient(d)), [api])

  useEffect(() => { loadGiven(); loadPatient() }, [loadGiven, loadPatient])

  // احسب العمر بالأشهر
  const ageMonths = patient?.date_of_birth ? (() => {
    const dob = new Date(patient.date_of_birth)
    const now = new Date()
    return (now.getFullYear() - dob.getFullYear()) * 12 + (now.getMonth() - dob.getMonth())
  })() : null

  // فلتر التطعيمات حسب العمر (±3 أشهر مستقبلاً)
  const relevantSchedule = ageMonths !== null
    ? VACCINE_SCHEDULE.filter(v => v.ageMonths <= ageMonths + 3)
    : VACCINE_SCHEDULE

  const isGiven = (key) => given.some(g =>
    g.vaccine_name?.toLowerCase().includes(key.toLowerCase()) ||
    g.notes?.toLowerCase().includes(key.toLowerCase())
  )

  const isOverdue = (v) => ageMonths !== null && v.ageMonths < ageMonths - 1 && !isGiven(v.key)
  const isDue = (v) => ageMonths !== null && Math.abs(v.ageMonths - ageMonths) <= 3 && !isGiven(v.key)

  const overdueVaccines = relevantSchedule.filter(isOverdue)
  const dueVaccines = relevantSchedule.filter(isDue)

  const mandatory = relevantSchedule.filter(v => v.category === 'mandatory')
  const optional = relevantSchedule.filter(v => v.category === 'optional')

  const openAdd = (prefill = {}) => { setEditing(null); setForm({ dose_number: 1, date_given: new Date().toISOString().split('T')[0], ...prefill }); setOpen(true) }
  const openEdit = (item) => { setEditing(item); setForm({ ...item }); setOpen(true) }
  const save = async () => {
    setLoading(true)
    const res = editing ? await api.put(`/vaccinations/${editing.id}`, form) : await api.post('/vaccinations', form)
    setLoading(false)
    if (res.id) { loadGiven(); setOpen(false) }
  }
  const remove = async (id) => { if (confirm('حذف هذا التطعيم؟')) { await api.del(`/vaccinations/${id}`); loadGiven() } }

  const VaccineRow = ({ v }) => {
    const given_ = isGiven(v.key)
    const overdue_ = isOverdue(v)
    const due_ = isDue(v)
    return (
      <div className={`flex items-center justify-between p-3 rounded-lg border gap-3 ${given_ ? 'bg-green-50 border-green-200' : overdue_ ? 'bg-red-50 border-red-200' : due_ ? 'bg-yellow-50 border-yellow-200' : 'bg-white border-gray-100'}`}>
        <div className="flex items-center gap-3 flex-1 min-w-0">
          {given_
            ? <CheckCircle2 className="w-5 h-5 text-green-500 shrink-0" />
            : overdue_ ? <AlertCircle className="w-5 h-5 text-red-500 shrink-0" />
            : due_ ? <Clock className="w-5 h-5 text-yellow-500 shrink-0" />
            : <div className="w-5 h-5 rounded-full border-2 border-gray-300 shrink-0" />
          }
          <div className="min-w-0">
            <p className="text-sm font-medium text-gray-800 truncate">{v.nameAr}</p>
            <p className="text-xs text-gray-500 truncate">{v.disease} · {v.ageLabel}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {given_
            ? <Badge className="bg-green-100 text-green-700 text-xs">✓ تم التطعيم</Badge>
            : overdue_ ? <Badge className="bg-red-100 text-red-700 text-xs">متأخر</Badge>
            : due_ ? <Badge className="bg-yellow-100 text-yellow-700 text-xs">موعده الآن</Badge>
            : null
          }
          {!given_ && (
            <Button size="sm" variant="outline" onClick={() => openAdd({ vaccine_name: v.nameAr, disease_prevented: v.disease })} className="text-xs py-1 h-7">
              تسجيل
            </Button>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* تنبيهات */}
      {overdueVaccines.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <p className="font-semibold text-red-800">تطعيمات متأخرة ({overdueVaccines.length})</p>
          </div>
          <p className="text-sm text-red-700">{overdueVaccines.map(v => v.nameAr).join(' · ')}</p>
        </div>
      )}
      {dueVaccines.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-5 h-5 text-yellow-600" />
            <p className="font-semibold text-yellow-800">تطعيمات موعدها الآن ({dueVaccines.length})</p>
          </div>
          <p className="text-sm text-yellow-700">{dueVaccines.map(v => v.nameAr).join(' · ')}</p>
        </div>
      )}

      {/* تبديل بين الجدول والتطعيمات المعطاة */}
      <div className="flex gap-2">
        <Button size="sm" variant={activeView === 'schedule' ? 'default' : 'outline'} onClick={() => setActiveView('schedule')} className={activeView === 'schedule' ? 'bg-blue-600' : ''}>
          جدول التطعيمات
        </Button>
        <Button size="sm" variant={activeView === 'given' ? 'default' : 'outline'} onClick={() => setActiveView('given')} className={activeView === 'given' ? 'bg-blue-600' : ''}>
          التطعيمات المُعطاة ({given.length})
        </Button>
        <div className="flex-1" />
        <Button onClick={() => openAdd()} className="gap-1 bg-blue-600 hover:bg-blue-700 text-sm h-8 px-3">
          <Plus className="w-3.5 h-3.5" /> إضافة تطعيم
        </Button>
      </div>

      {activeView === 'schedule' && (
        <div className="space-y-5">
          {/* إجبارية */}
          <div>
            <h3 className="text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
              <Syringe className="w-4 h-4 text-blue-500" /> التطعيمات الإجبارية
              {ageMonths !== null && <span className="text-xs font-normal text-gray-500">(حسب عمر المريض: {ageMonths < 24 ? `${ageMonths} شهراً` : `${Math.floor(ageMonths/12)} سنة`})</span>}
            </h3>
            <div className="space-y-2">
              {mandatory.map(v => <VaccineRow key={v.key} v={v} />)}
              {mandatory.length === 0 && <p className="text-sm text-gray-400 text-center py-4">لا توجد تطعيمات إجبارية للعمر الحالي</p>}
            </div>
          </div>
          {/* إضافية */}
          <div>
            <h3 className="text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
              <Heart className="w-4 h-4 text-pink-500" /> التطعيمات الإضافية (اختيارية)
            </h3>
            <div className="space-y-2">
              {optional.map(v => <VaccineRow key={v.key} v={v} />)}
            </div>
          </div>
        </div>
      )}

      {activeView === 'given' && (
        <div className="space-y-3">
          {given.length === 0
            ? <div className="text-center py-12 text-gray-400"><Syringe className="w-12 h-12 mx-auto mb-3 opacity-30" /><p>لم يتم تسجيل أي تطعيمات بعد</p></div>
            : given.map(g => (
              <Card key={g.id} className="border-r-4 border-r-green-400">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-3">
                      <FieldRow label="التطعيم" value={g.vaccine_name} />
                      <FieldRow label="المرض المقاوم" value={g.disease_prevented} />
                      <FieldRow label="تاريخ الإعطاء" value={g.date_given} />
                      <FieldRow label="الجرعة" value={g.dose_number ? `${g.dose_number}/${g.total_doses || '?'}` : '—'} />
                      {g.provider && <FieldRow label="الجهة" value={g.provider} />}
                      {g.reaction && <FieldRow label="التفاعل" value={g.reaction} />}
                      {g.attachment_data && (
                        <div className="col-span-full">
                          <p className="text-xs text-gray-500 mb-1">شهادة التطعيم</p>
                          <img src={g.attachment_data} alt="شهادة" className="max-h-28 rounded border object-contain bg-gray-50" />
                        </div>
                      )}
                    </div>
                    <div className="flex gap-2 shrink-0">
                      <Button size="icon" variant="ghost" onClick={() => openEdit(g)}><Pencil className="w-4 h-4" /></Button>
                      <Button size="icon" variant="ghost" className="text-red-500" onClick={() => remove(g.id)}><Trash2 className="w-4 h-4" /></Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
        </div>
      )}

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-lg" dir="rtl">
          <DialogHeader><DialogTitle>{editing ? 'تعديل' : 'تسجيل'} تطعيم</DialogTitle></DialogHeader>
          <div className="grid grid-cols-2 gap-4 py-2">
            <div className="col-span-2"><Input placeholder="اسم التطعيم *" value={form.vaccine_name || ''} onChange={e => setForm({ ...form, vaccine_name: e.target.value })} /></div>
            <div className="col-span-2"><Input placeholder="المرض الذي يقي منه" value={form.disease_prevented || ''} onChange={e => setForm({ ...form, disease_prevented: e.target.value })} /></div>
            <Input type="number" placeholder="رقم الجرعة" value={form.dose_number || ''} onChange={e => setForm({ ...form, dose_number: parseInt(e.target.value) })} />
            <Input type="number" placeholder="إجمالي الجرعات" value={form.total_doses || ''} onChange={e => setForm({ ...form, total_doses: parseInt(e.target.value) })} />
            <div><label className="text-xs text-gray-500 mb-1 block">تاريخ الإعطاء</label><Input type="date" value={form.date_given || ''} onChange={e => setForm({ ...form, date_given: e.target.value })} /></div>
            <div><label className="text-xs text-gray-500 mb-1 block">الموعد القادم</label><Input type="date" value={form.next_due_date || ''} onChange={e => setForm({ ...form, next_due_date: e.target.value })} /></div>
            <div className="col-span-2"><Input placeholder="الجهة المقدِّمة (مستشفى / مركز صحي)" value={form.provider || ''} onChange={e => setForm({ ...form, provider: e.target.value })} /></div>
            <Select value={form.administration_site || ''} onValueChange={v => setForm({ ...form, administration_site: v })}>
              <SelectTrigger><SelectValue placeholder="موضع الحقن" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="left_arm">الذراع الأيسر</SelectItem>
                <SelectItem value="right_arm">الذراع الأيمن</SelectItem>
                <SelectItem value="left_thigh">الفخذ الأيسر</SelectItem>
                <SelectItem value="right_thigh">الفخذ الأيمن</SelectItem>
                <SelectItem value="oral">فموي</SelectItem>
              </SelectContent>
            </Select>
            <Input placeholder="رقم دفعة اللقاح" value={form.batch_number || ''} onChange={e => setForm({ ...form, batch_number: e.target.value })} />
            <div className="col-span-2"><Input placeholder="تفاعل ما بعد التطعيم (إن وجد)" value={form.reaction || ''} onChange={e => setForm({ ...form, reaction: e.target.value })} /></div>
            <div className="col-span-2"><Input placeholder="ملاحظات" value={form.notes || ''} onChange={e => setForm({ ...form, notes: e.target.value })} /></div>
            <ImageUpload label="📜 صورة شهادة التطعيم (اختياري)" value={form.attachment_data || null} onChange={v => setForm({ ...form, attachment_data: v })} />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>إلغاء</Button>
            <Button onClick={save} disabled={loading} className="bg-blue-600 hover:bg-blue-700">{loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'حفظ'}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

// ══════════════════════════════════════════════
// التحاليل المخبرية
// ══════════════════════════════════════════════
function LabTestsTab({ api }) {
  const [items, setItems] = useState([])
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({})
  const [loading, setLoading] = useState(false)
  const [bloodTypeDetected, setBloodTypeDetected] = useState(null)
  const [lightbox, setLightbox] = useState(null)

  const load = useCallback(() => api.get('/lab-tests').then(d => Array.isArray(d) && setItems(d)), [api])
  useEffect(() => { load() }, [load])

  const openAdd = () => { setEditing(null); setForm({ status: 'normal' }); setBloodTypeDetected(null); setOpen(true) }
  const openEdit = (item) => { setEditing(item); setForm({ ...item }); setBloodTypeDetected(null); setOpen(true) }

  const handleTestNameChange = (val) => {
    setForm(f => ({ ...f, test_name: val }))
    setBloodTypeDetected(
      val.toLowerCase().includes('فصيلة') || val.toLowerCase().includes('blood type') ||
      val.toLowerCase().includes('blood group') || val.toLowerCase().includes('abo')
    )
  }

  const save = async () => {
    setLoading(true)
    const res = editing ? await api.put(`/lab-tests/${editing.id}`, form) : await api.post('/lab-tests', form)
    setLoading(false)
    if (res.id) { load(); setOpen(false) }
  }
  const remove = async (id) => { if (confirm('هل تريد حذف هذا السجل؟')) { await api.del(`/lab-tests/${id}`); load() } }

  // Group by test_name for comparison table
  const grouped = items.reduce((acc, t) => {
    const key = t.test_name || 'غير مصنف'
    if (!acc[key]) acc[key] = []
    acc[key].push(t)
    return acc
  }, {})

  return (
    <>
      {lightbox && (
        <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4" onClick={() => setLightbox(null)}>
          <img src={lightbox} alt="نتيجة التحليل" className="max-w-full max-h-full rounded-xl object-contain" />
        </div>
      )}

      <div className="flex justify-end mb-4">
        <Button onClick={openAdd} className="gap-2 bg-blue-600 hover:bg-blue-700"><Plus className="w-4 h-4" /> إضافة تحليل</Button>
      </div>

      {items.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <FlaskConical className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>لا توجد تحاليل مخبرية مسجلة بعد</p>
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(grouped).map(([testName, rows]) => {
            const refRange = rows.find(r => r.reference_range)?.reference_range
            const sorted = [...rows].sort((a, b) => (a.test_date || '').localeCompare(b.test_date || ''))
            return (
              <div key={testName} className="bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden">
                {/* رأس التحليل */}
                <div className="flex items-center justify-between gap-3 px-4 py-3 bg-indigo-50 border-b border-indigo-100">
                  <div className="flex items-center gap-2">
                    <FlaskConical className="w-4 h-4 text-indigo-600" />
                    <span className="font-bold text-indigo-900 text-sm">{testName}</span>
                    {rows.length > 1 && (
                      <span className="text-xs bg-indigo-200 text-indigo-800 rounded-full px-2 py-0.5">{rows.length} نتيجة</span>
                    )}
                  </div>
                  {refRange && (
                    <div className="text-xs bg-green-50 text-green-700 border border-green-200 rounded-lg px-3 py-1">
                      <span className="opacity-60 ml-1">المجال الطبيعي:</span>
                      <span className="font-mono font-medium">{refRange}</span>
                    </div>
                  )}
                </div>

                {/* جدول المقارنة */}
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-xs text-gray-500 bg-gray-50 border-b border-gray-100">
                        <th className="text-right px-4 py-2">التاريخ</th>
                        <th className="text-center px-3 py-2">النتيجة</th>
                        <th className="text-center px-3 py-2">الحالة</th>
                        <th className="text-right px-3 py-2">المعمل</th>
                        <th className="text-center px-3 py-2">صورة</th>
                        <th className="text-center px-3 py-2">إجراء</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50">
                      {sorted.map(t => (
                        <tr key={t.id} className={`hover:bg-gray-50/50 ${t.status === 'critical' ? 'bg-red-50/40' : t.status === 'abnormal' ? 'bg-orange-50/40' : ''}`}>
                          <td className="px-4 py-2.5 font-medium text-gray-800 whitespace-nowrap">{t.test_date || '—'}</td>
                          <td className="px-3 py-2.5 text-center">
                            <span className="font-mono font-semibold text-gray-900">{t.result_value || '—'}</span>
                            {t.unit && <span className="text-xs text-gray-400 mr-1">{t.unit}</span>}
                          </td>
                          <td className="px-3 py-2.5 text-center">
                            <Badge className={`text-xs ${statusColors[t.status] || 'bg-gray-100'}`}>{statusLabels[t.status] || t.status}</Badge>
                          </td>
                          <td className="px-3 py-2.5 text-gray-500 text-xs">{t.lab_name || '—'}</td>
                          <td className="px-3 py-2.5 text-center">
                            {t.attachment_data
                              ? <button onClick={() => setLightbox(t.attachment_data)} className="text-blue-500 hover:text-blue-700"><ZoomIn className="w-4 h-4 mx-auto" /></button>
                              : <span className="text-gray-300">—</span>
                            }
                          </td>
                          <td className="px-3 py-2.5">
                            <div className="flex items-center justify-center gap-1">
                              <Button size="icon" variant="ghost" className="w-7 h-7" onClick={() => openEdit(t)}><Pencil className="w-3.5 h-3.5" /></Button>
                              <Button size="icon" variant="ghost" className="w-7 h-7 text-red-500" onClick={() => remove(t.id)}><Trash2 className="w-3.5 h-3.5" /></Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )
          })}
        </div>
      )}

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-lg" dir="rtl">
          <DialogHeader><DialogTitle>{editing ? 'تعديل' : 'إضافة'} تحليل مخبري</DialogTitle></DialogHeader>
          <div className="grid grid-cols-2 gap-4 py-2">
            <div className="col-span-2">
              <Input placeholder="اسم التحليل *" value={form.test_name || ''} onChange={e => handleTestNameChange(e.target.value)} />
              {bloodTypeDetected && (
                <p className="text-xs text-blue-600 mt-1 flex items-center gap-1">
                  <Droplets className="w-3 h-3" /> سيتم تحديث فصيلة الدم تلقائياً من النتيجة
                </p>
              )}
            </div>
            <Select value={form.test_category || ''} onValueChange={v => setForm({ ...form, test_category: v })}>
              <SelectTrigger><SelectValue placeholder="التصنيف" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="blood">دم</SelectItem><SelectItem value="urine">بول</SelectItem>
                <SelectItem value="culture">مزرعة</SelectItem><SelectItem value="hormones">هرمونات</SelectItem>
                <SelectItem value="chemistry">كيمياء</SelectItem><SelectItem value="immunology">مناعة</SelectItem>
                <SelectItem value="other">أخرى</SelectItem>
              </SelectContent>
            </Select>
            <Input type="date" value={form.test_date || ''} onChange={e => setForm({ ...form, test_date: e.target.value })} />
            <Input placeholder="اسم المعمل" value={form.lab_name || ''} onChange={e => setForm({ ...form, lab_name: e.target.value })} />
            <Input placeholder="الطبيب الطالب" value={form.ordering_doctor || ''} onChange={e => setForm({ ...form, ordering_doctor: e.target.value })} />
            <Input placeholder="قيمة النتيجة" value={form.result_value || ''} onChange={e => setForm({ ...form, result_value: e.target.value })} />
            <Input placeholder="الوحدة" value={form.unit || ''} onChange={e => setForm({ ...form, unit: e.target.value })} />
            <Input placeholder="المجال الطبيعي" value={form.reference_range || ''} onChange={e => setForm({ ...form, reference_range: e.target.value })} />
            <Select value={form.status || 'normal'} onValueChange={v => setForm({ ...form, status: v })}>
              <SelectTrigger><SelectValue placeholder="الحالة" /></SelectTrigger>
              <SelectContent><SelectItem value="normal">طبيعي</SelectItem><SelectItem value="abnormal">غير طبيعي</SelectItem><SelectItem value="critical">حرج</SelectItem></SelectContent>
            </Select>
            <div className="col-span-2"><Input placeholder="التفسير" value={form.interpretation || ''} onChange={e => setForm({ ...form, interpretation: e.target.value })} /></div>
            <ImageUpload label="🔬 صورة نتيجة التحليل (اختياري)" value={form.attachment_data || null} onChange={v => setForm({ ...form, attachment_data: v })} />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>إلغاء</Button>
            <Button onClick={save} disabled={loading} className="bg-blue-600 hover:bg-blue-700">{loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'حفظ'}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

// ══════════════════════════════════════════════
// الأشعة والتصوير الطبي
// ══════════════════════════════════════════════
function RadiologyTab({ api }) {
  const [items, setItems] = useState([])
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({})
  const [loading, setLoading] = useState(false)

  const load = useCallback(() => api.get('/radiology').then(d => Array.isArray(d) && setItems(d)), [api])
  useEffect(() => { load() }, [load])

  const openAdd = () => { setEditing(null); setForm({ scan_type: 'xray' }); setOpen(true) }
  const openEdit = (item) => { setEditing(item); setForm({ ...item }); setOpen(true) }
  const save = async () => {
    setLoading(true)
    const res = editing ? await api.put(`/radiology/${editing.id}`, form) : await api.post('/radiology', form)
    setLoading(false)
    if (res.id) { load(); setOpen(false) }
  }
  const remove = async (id) => { if (confirm('هل تريد حذف هذا السجل؟')) { await api.del(`/radiology/${id}`); load() } }

  const [lightboxRad, setLightboxRad] = useState(null)

  return (
    <>
      {lightboxRad && (
        <div className="fixed inset-0 bg-black/85 z-50 flex items-center justify-center p-4" onClick={() => setLightboxRad(null)}>
          <img src={lightboxRad} alt="صورة طبية" className="max-w-full max-h-[90vh] rounded-xl object-contain shadow-2xl" />
          <button className="absolute top-4 right-4 text-white bg-black/30 rounded-full p-2" onClick={() => setLightboxRad(null)}>✕</button>
        </div>
      )}
      <SectionList items={items} addLabel="إضافة أشعة" onAdd={openAdd} renderCard={(r) => (
        <Card key={r.id} className="border-r-4 border-r-indigo-400">
          <CardContent className="p-5">
            <div className="flex items-start justify-between gap-4">
              {/* صورة مصغرة قابلة للنقر */}
              {r.attachment_data && (
                <button onClick={() => setLightboxRad(r.attachment_data)} className="shrink-0 group relative rounded-xl overflow-hidden border border-gray-200 bg-gray-50">
                  <img src={r.attachment_data} alt="أشعة" className="w-24 h-20 object-cover group-hover:opacity-75 transition-opacity" />
                  <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 bg-black/30 transition-opacity">
                    <ZoomIn className="w-6 h-6 text-white" />
                  </div>
                </button>
              )}
              <div className="flex-1 grid grid-cols-2 md:grid-cols-3 gap-4">
                <FieldRow label="نوع الأشعة"><Badge className="bg-indigo-100 text-indigo-800">{scanTypeLabels[r.scan_type] || r.scan_type}</Badge></FieldRow>
                <FieldRow label="الجزء المصوَّر" value={r.body_part} />
                <FieldRow label="التاريخ" value={r.scan_date} />
                <FieldRow label="المركز" value={r.facility} />
                <FieldRow label="الطبيب الطالب" value={r.ordering_doctor} />
                {r.findings && <div className="col-span-full"><FieldRow label="النتائج" value={r.findings} /></div>}
                {r.impression && <div className="col-span-full"><FieldRow label="التفسير النهائي" value={r.impression} /></div>}
                {r.report_data && (
                  <div className="col-span-full">
                    <p className="text-xs text-gray-500 mb-1">صورة التقرير</p>
                    <button onClick={() => setLightboxRad(r.report_data)} className="group relative inline-block rounded-lg overflow-hidden border border-gray-200">
                      <img src={r.report_data} alt="تقرير" className="max-h-32 rounded object-contain bg-gray-50 group-hover:opacity-75 transition-opacity" />
                    </button>
                  </div>
                )}
              </div>
              <div className="flex gap-2 shrink-0">
                <Button size="icon" variant="ghost" onClick={() => openEdit(r)}><Pencil className="w-4 h-4" /></Button>
                <Button size="icon" variant="ghost" className="text-red-500" onClick={() => remove(r.id)}><Trash2 className="w-4 h-4" /></Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )} />

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-lg" dir="rtl">
          <DialogHeader><DialogTitle>{editing ? 'تعديل' : 'إضافة'} أشعة / تصوير طبي</DialogTitle></DialogHeader>
          <div className="grid grid-cols-2 gap-4 py-2">
            <Select value={form.scan_type || 'xray'} onValueChange={v => setForm({ ...form, scan_type: v })}>
              <SelectTrigger><SelectValue placeholder="نوع الأشعة *" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="xray">أشعة X</SelectItem><SelectItem value="mri">رنين مغناطيسي</SelectItem>
                <SelectItem value="ct">أشعة مقطعية CT</SelectItem><SelectItem value="ultrasound">موجات صوتية</SelectItem>
                <SelectItem value="pet">PET Scan</SelectItem><SelectItem value="mammo">ماموجرام</SelectItem>
              </SelectContent>
            </Select>
            <Input placeholder="الجزء المصوَّر *" value={form.body_part || ''} onChange={e => setForm({ ...form, body_part: e.target.value })} />
            <Input type="date" value={form.scan_date || ''} onChange={e => setForm({ ...form, scan_date: e.target.value })} />
            <Input placeholder="المركز / المستشفى" value={form.facility || ''} onChange={e => setForm({ ...form, facility: e.target.value })} />
            <Input placeholder="طبيب الأشعة" value={form.radiologist || ''} onChange={e => setForm({ ...form, radiologist: e.target.value })} />
            <Input placeholder="الطبيب الطالب" value={form.ordering_doctor || ''} onChange={e => setForm({ ...form, ordering_doctor: e.target.value })} />
            <div className="col-span-2"><Input placeholder="سبب الطلب" value={form.reason || ''} onChange={e => setForm({ ...form, reason: e.target.value })} /></div>
            <div className="col-span-2"><Input placeholder="النتائج" value={form.findings || ''} onChange={e => setForm({ ...form, findings: e.target.value })} /></div>
            <div className="col-span-2"><Input placeholder="التفسير النهائي" value={form.impression || ''} onChange={e => setForm({ ...form, impression: e.target.value })} /></div>
            <div className="col-span-2"><Input placeholder="التوصيات" value={form.recommendation || ''} onChange={e => setForm({ ...form, recommendation: e.target.value })} /></div>
            <ImageUpload label="🩻 صورة الأشعة (اختياري)" value={form.attachment_data || null} onChange={v => setForm({ ...form, attachment_data: v })} />
            <ImageUpload label="📄 صورة التقرير (اختياري)" value={form.report_data || null} onChange={v => setForm({ ...form, report_data: v })} />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>إلغاء</Button>
            <Button onClick={save} disabled={loading} className="bg-blue-600 hover:bg-blue-700">{loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'حفظ'}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

// ══════════════════════════════════════════════
// التاريخ المرضي
// ══════════════════════════════════════════════
function MedicalHistoryTab({ api }) {
  const [data, setData] = useState(null)
  const [form, setForm] = useState({})
  const [editing, setEditing] = useState(false)
  const [loading, setLoading] = useState(false)
  const [familyForm, setFamilyForm] = useState({ disease: '', relation: '', notes: '' })

  const load = useCallback(() => api.get('/history').then(d => { setData(d); setForm({ ...d, family_history: d?.family_history || [] }) }), [api])
  useEffect(() => { load() }, [load])

  const save = async () => {
    setLoading(true)
    const res = await api.put('/history', form)
    setLoading(false)
    if (res.patient_id) { setData(res); setEditing(false) }
  }

  const addFamily = () => {
    if (!familyForm.disease) return
    setForm(f => ({ ...f, family_history: [...(f.family_history || []), { ...familyForm }] }))
    setFamilyForm({ disease: '', relation: '', notes: '' })
  }
  const removeFamily = (i) => setForm(f => ({ ...f, family_history: (f.family_history || []).filter((_, idx) => idx !== i) }))

  const smokeLabels = { never: 'لا يدخن', former: 'سبق له', current: 'مدخن' }
  const alcoholLabels = { never: 'لا', occasional: 'أحياناً', regular: 'منتظم' }
  const activityLabels = { sedentary: 'خامل', light: 'خفيف', moderate: 'معتدل', active: 'نشط' }

  if (!editing) return (
    <div className="space-y-6">
      <div className="flex justify-end">
        <Button onClick={() => setEditing(true)} className="gap-2 bg-blue-600 hover:bg-blue-700"><Pencil className="w-4 h-4" /> تعديل التاريخ المرضي</Button>
      </div>
      {!data || Object.keys(data).length === 0 ? (
        <div className="text-center py-16 text-gray-400"><History className="w-12 h-12 mx-auto mb-3 opacity-30" /><p>لم يتم إدخال التاريخ المرضي بعد</p></div>
      ) : (
        <div className="grid md:grid-cols-2 gap-6">
          <Card><CardHeader><CardTitle className="text-base">العادات الصحية</CardTitle></CardHeader>
            <CardContent className="grid grid-cols-2 gap-4">
              <FieldRow label="التدخين" value={smokeLabels[data.smoking_status] || data.smoking_status} />
              {data.smoking_years && <FieldRow label="سنوات التدخين" value={`${data.smoking_years} سنة`} />}
              <FieldRow label="الكحول" value={alcoholLabels[data.alcohol_use] || data.alcohol_use} />
              <FieldRow label="النشاط البدني" value={activityLabels[data.physical_activity] || data.physical_activity} />
            </CardContent>
          </Card>
          <Card><CardHeader><CardTitle className="text-base">الحالات المزمنة والوراثية</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <FieldRow label="أمراض مزمنة" value={data.chronic_conditions} />
              <FieldRow label="أمراض وراثية" value={data.genetic_conditions} />
              <FieldRow label="ملاحظات" value={data.general_notes} />
            </CardContent>
          </Card>
          {data.family_history?.length > 0 && (
            <Card className="md:col-span-2"><CardHeader><CardTitle className="text-base">التاريخ العائلي</CardTitle></CardHeader>
              <CardContent>
                <div className="divide-y">
                  {data.family_history.map((f, i) => (
                    <div key={i} className="py-3 grid grid-cols-3 gap-4">
                      <FieldRow label="المرض" value={f.disease} />
                      <FieldRow label="صلة القرابة" value={f.relation} />
                      <FieldRow label="ملاحظات" value={f.notes} />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )

  return (
    <div className="space-y-5">
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <label className="text-xs font-medium text-gray-600 block mb-1">التدخين</label>
          <Select value={form.smoking_status || ''} onValueChange={v => setForm({ ...form, smoking_status: v })}>
            <SelectTrigger><SelectValue placeholder="اختر" /></SelectTrigger>
            <SelectContent><SelectItem value="never">لا يدخن</SelectItem><SelectItem value="former">سبق له</SelectItem><SelectItem value="current">مدخن حالياً</SelectItem></SelectContent>
          </Select>
        </div>
        <div>
          <label className="text-xs font-medium text-gray-600 block mb-1">النشاط البدني</label>
          <Select value={form.physical_activity || ''} onValueChange={v => setForm({ ...form, physical_activity: v })}>
            <SelectTrigger><SelectValue placeholder="اختر" /></SelectTrigger>
            <SelectContent><SelectItem value="sedentary">خامل</SelectItem><SelectItem value="light">خفيف</SelectItem><SelectItem value="moderate">معتدل</SelectItem><SelectItem value="active">نشط</SelectItem></SelectContent>
          </Select>
        </div>
        <div className="col-span-2"><Input placeholder="الأمراض المزمنة" value={form.chronic_conditions || ''} onChange={e => setForm({ ...form, chronic_conditions: e.target.value })} /></div>
        <div className="col-span-2"><Input placeholder="الأمراض الوراثية" value={form.genetic_conditions || ''} onChange={e => setForm({ ...form, genetic_conditions: e.target.value })} /></div>
        <div className="col-span-2"><Input placeholder="ملاحظات عامة" value={form.general_notes || ''} onChange={e => setForm({ ...form, general_notes: e.target.value })} /></div>
      </div>

      <Card><CardHeader><CardTitle className="text-base">التاريخ العائلي</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {(form.family_history || []).map((f, i) => (
            <div key={i} className="flex items-center gap-2 bg-gray-50 p-2 rounded-lg text-sm">
              <span className="flex-1">{f.disease} · {f.relation}</span>
              <Button size="icon" variant="ghost" className="w-6 h-6 text-red-400" onClick={() => removeFamily(i)}><X className="w-3 h-3" /></Button>
            </div>
          ))}
          <div className="grid grid-cols-3 gap-2">
            <Input placeholder="المرض" value={familyForm.disease} onChange={e => setFamilyForm({ ...familyForm, disease: e.target.value })} />
            <Input placeholder="صلة القرابة" value={familyForm.relation} onChange={e => setFamilyForm({ ...familyForm, relation: e.target.value })} />
            <Button variant="outline" onClick={addFamily}><Plus className="w-4 h-4" /></Button>
          </div>
        </CardContent>
      </Card>

      <div className="flex gap-2 justify-end">
        <Button variant="outline" onClick={() => setEditing(false)}>إلغاء</Button>
        <Button onClick={save} disabled={loading} className="bg-blue-600 hover:bg-blue-700">{loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'حفظ التغييرات'}</Button>
      </div>
    </div>
  )
}

// ══════════════════════════════════════════════
// التقرير الطبي الشامل
// ══════════════════════════════════════════════
function MedicalReportModal({ api, open, onClose }) {
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!open) return
    setLoading(true)
    api.get('/report').then(d => { setReport(d); setLoading(false) })
  }, [open, api])

  if (!open) return null

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl" dir="rtl">
        <DialogHeader><DialogTitle className="flex items-center gap-2"><FileDown className="w-5 h-5 text-blue-500" /> التقرير الطبي الشامل</DialogTitle></DialogHeader>
        {loading ? (
          <div className="flex items-center justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-blue-500" /></div>
        ) : report ? (
          <div className="space-y-4 py-2 max-h-[60vh] overflow-y-auto">
            {/* بيانات المريض */}
            <div className="bg-blue-50 rounded-xl p-4">
              <h3 className="font-bold text-blue-800 mb-3">بيانات المريض</h3>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <FieldRow label="الاسم" value={report.patient?.name} />
                <FieldRow label="العمر" value={report.patient?.age ? `${report.patient.age} سنة` : '—'} />
                <FieldRow label="فصيلة الدم" value={report.patient?.blood_type || '—'} />
                <FieldRow label="الطول / الوزن" value={`${report.patient?.height || '—'} سم / ${report.patient?.weight || '—'} كجم`} />
                {report.patient?.bmi && <FieldRow label="مؤشر الكتلة (BMI)" value={report.patient.bmi} />}
              </div>
            </div>
            {/* الحساسية */}
            {report.allergies?.length > 0 && (
              <div className="bg-red-50 rounded-xl p-4">
                <h3 className="font-bold text-red-800 mb-2">⚠ الحساسية</h3>
                <div className="flex flex-wrap gap-2">
                  {report.allergies.map((a, i) => <Badge key={i} className="bg-red-100 text-red-800">{a.allergen} ({severityLabels[a.severity] || a.severity})</Badge>)}
                </div>
              </div>
            )}
            {/* الأمراض النشطة */}
            {report.active_diseases?.length > 0 && (
              <div className="bg-white border rounded-xl p-4">
                <h3 className="font-bold text-gray-800 mb-2">التاريخ المرضي</h3>
                <ul className="space-y-1 text-sm">
                  {report.active_diseases.map((d, i) => <li key={i} className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-blue-400 inline-block" />{d.name} {d.severity && `(${severityLabels[d.severity]})`}</li>)}
                </ul>
              </div>
            )}
            {/* الأدوية الحالية */}
            {report.current_medications?.length > 0 && (
              <div className="bg-white border rounded-xl p-4">
                <h3 className="font-bold text-gray-800 mb-2">الأدوية الحالية</h3>
                <ul className="space-y-1 text-sm">
                  {report.current_medications.map((m, i) => <li key={i} className="flex items-center gap-2"><Pill className="w-3 h-3 text-green-500" />{m.name} — {m.dosage} — {m.frequency}</li>)}
                </ul>
              </div>
            )}
            {/* آخر التحاليل */}
            {report.recent_lab_tests?.length > 0 && (
              <div className="bg-white border rounded-xl p-4">
                <h3 className="font-bold text-gray-800 mb-2">آخر التحاليل</h3>
                <ul className="space-y-1 text-sm">
                  {report.recent_lab_tests.slice(0, 5).map((t, i) => <li key={i} className="flex items-center gap-2"><FlaskConical className="w-3 h-3 text-indigo-500" />{t.test_name} — {t.result_value}{t.unit && ` ${t.unit}`} <Badge className={`text-xs ${statusColors[t.status] || 'bg-gray-100'}`}>{statusLabels[t.status]}</Badge></li>)}
                </ul>
              </div>
            )}
            <p className="text-xs text-gray-400 text-center">تم إنشاء هذا التقرير في {new Date(report.generated_at).toLocaleString('ar-EG')}</p>
          </div>
        ) : null}
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>إغلاق</Button>
          {report && (
            <Button onClick={() => window.print()} className="bg-blue-600 hover:bg-blue-700 gap-2">
              <FileDown className="w-4 h-4" /> طباعة التقرير
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ══════════════════════════════════════════════
// غازات الدم (ABG)
// ══════════════════════════════════════════════
const ABG_FIELDS = [
  { key: 'ph',      label: 'pH',     normal: '7.35-7.45' },
  { key: 'pco2',    label: 'pCO₂',   normal: '35-45 mmHg' },
  { key: 'hco3',    label: 'HCO₃',   normal: '22-26 mEq/L' },
  { key: 'o2',      label: 'O₂',     normal: '80-100 mmHg' },
  { key: 'spo2',    label: 'SpO₂',   normal: '95-100%' },
  { key: 'k',       label: 'K⁺',     normal: '3.5-5.0' },
  { key: 'lactate', label: 'Lactate', normal: '< 2 mmol/L' },
]

function BloodGasTab({ api }) {
  const [items, setItems]     = useState([])
  const [open, setOpen]       = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm]       = useState({})
  const [loading, setLoading] = useState(false)
  const [lightbox, setLightbox] = useState(null)

  const load = useCallback(() => api.get('/blood-gas').then(d => Array.isArray(d) && setItems(d)), [api])
  useEffect(() => { load() }, [load])

  const openAdd  = () => { setEditing(null); setForm({ reading_date: new Date().toISOString().split('T')[0] }); setOpen(true) }
  const openEdit = (item) => { setEditing(item); setForm({ ...item }); setOpen(true) }
  const save = async () => {
    setLoading(true)
    const res = editing ? await api.put(`/blood-gas/${editing.id}`, form) : await api.post('/blood-gas', form)
    setLoading(false)
    if (res.id) { load(); setOpen(false) }
  }
  const remove = async (id) => { if (confirm('حذف هذه القراءة؟')) { await api.del(`/blood-gas/${id}`); load() } }

  return (
    <>
      {lightbox && (
        <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4" onClick={() => setLightbox(null)}>
          <img src={lightbox} alt="صورة مرفقة" className="max-w-full max-h-full rounded-xl object-contain" />
        </div>
      )}

      <div className="flex justify-end mb-4">
        <Button onClick={openAdd} className="gap-2 bg-blue-600 hover:bg-blue-700"><Plus className="w-4 h-4" /> إضافة قراءة</Button>
      </div>

      {/* معلومات المجالات الطبيعية */}
      <div className="flex flex-wrap gap-2 mb-4 p-3 bg-blue-50 rounded-xl border border-blue-100">
        {ABG_FIELDS.map(f => (
          <div key={f.key} className="bg-white rounded-lg px-2.5 py-1.5 border border-blue-100 text-center">
            <p className="text-xs font-bold text-blue-800">{f.label}</p>
            <p className="text-xs text-gray-500">{f.normal}</p>
          </div>
        ))}
      </div>

      {items.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <Activity className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>لا توجد قراءات غازات دم بعد</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-blue-50 text-blue-800">
                <th className="text-right px-3 py-2.5 rounded-r-xl font-semibold">التاريخ / الوقت</th>
                <th className="text-right px-3 py-2.5 font-semibold">Mode</th>
                {ABG_FIELDS.map(f => <th key={f.key} className="text-center px-3 py-2.5 font-semibold">{f.label}</th>)}
                <th className="text-center px-3 py-2.5 font-semibold rounded-l-xl">صورة / إجراء</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {items.map(r => (
                <tr key={r.id} className="hover:bg-gray-50 bg-white">
                  <td className="px-3 py-2.5">
                    <p className="font-medium text-gray-800">{r.reading_date}</p>
                    {r.reading_time && <p className="text-xs text-gray-400">{r.reading_time}</p>}
                  </td>
                  <td className="px-3 py-2.5 text-gray-600 text-xs">{r.mode || '—'}</td>
                  {ABG_FIELDS.map(f => (
                    <td key={f.key} className="px-3 py-2.5 text-center font-mono">
                      <span className="font-medium text-gray-800">{r[f.key] || '—'}</span>
                    </td>
                  ))}
                  <td className="px-3 py-2.5">
                    <div className="flex items-center justify-center gap-1.5">
                      {r.attachment_data && (
                        <button onClick={() => setLightbox(r.attachment_data)} className="text-blue-500 hover:text-blue-700">
                          <ZoomIn className="w-4 h-4" />
                        </button>
                      )}
                      <Button size="icon" variant="ghost" className="w-7 h-7" onClick={() => openEdit(r)}><Pencil className="w-3.5 h-3.5" /></Button>
                      <Button size="icon" variant="ghost" className="w-7 h-7 text-red-500" onClick={() => remove(r.id)}><Trash2 className="w-3.5 h-3.5" /></Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-2xl" dir="rtl">
          <DialogHeader><DialogTitle>{editing ? 'تعديل' : 'إضافة'} قراءة غازات الدم</DialogTitle></DialogHeader>
          <div className="grid grid-cols-2 gap-4 py-2">
            <div>
              <label className="text-xs text-gray-500 mb-1 block">التاريخ</label>
              <Input type="date" value={form.reading_date || ''} onChange={e => setForm({...form, reading_date: e.target.value})} />
            </div>
            <div>
              <label className="text-xs text-gray-500 mb-1 block">الوقت</label>
              <Input type="time" value={form.reading_time || ''} onChange={e => setForm({...form, reading_time: e.target.value})} />
            </div>
            <div className="col-span-2">
              <label className="text-xs text-gray-500 mb-1 block">وضع التنفس (Mode)</label>
              <Select value={form.mode || ''} onValueChange={v => setForm({...form, mode: v})}>
                <SelectTrigger><SelectValue placeholder="اختر وضع التنفس" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="Room Air">Room Air (هواء الغرفة)</SelectItem>
                  <SelectItem value="O2 Mask">O2 Mask (قناع أكسجين)</SelectItem>
                  <SelectItem value="Nasal Cannula">Nasal Cannula (خرطوم أنفي)</SelectItem>
                  <SelectItem value="Ventilator">Ventilator (جهاز تنفس)</SelectItem>
                  <SelectItem value="CPAP">CPAP</SelectItem>
                  <SelectItem value="BiPAP">BiPAP</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {ABG_FIELDS.map(f => (
              <div key={f.key}>
                <label className="text-xs text-gray-500 mb-1 block">{f.label} <span className="text-gray-400">({f.normal})</span></label>
                <Input placeholder={f.label} value={form[f.key] || ''} onChange={e => setForm({...form, [f.key]: e.target.value})} />
              </div>
            ))}
            <div className="col-span-2">
              <Input placeholder="ملاحظات" value={form.notes || ''} onChange={e => setForm({...form, notes: e.target.value})} />
            </div>
            <ImageUpload label="📊 صورة مرفقة (اختياري)" value={form.attachment_data || null} onChange={v => setForm({...form, attachment_data: v})} />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>إلغاء</Button>
            <Button onClick={save} disabled={loading} className="bg-blue-600 hover:bg-blue-700">{loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'حفظ'}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

// ══════════════════════════════════════════════
// رسم القلب (ECG)
// ══════════════════════════════════════════════
function ECGTab({ api }) {
  const [items, setItems]     = useState([])
  const [open, setOpen]       = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm]       = useState({})
  const [loading, setLoading] = useState(false)
  const [lightbox, setLightbox] = useState(null)

  const load = useCallback(() => api.get('/ecg').then(d => Array.isArray(d) && setItems(d)), [api])
  useEffect(() => { load() }, [load])

  const openAdd  = () => { setEditing(null); setForm({ ecg_date: new Date().toISOString().split('T')[0] }); setOpen(true) }
  const openEdit = (item) => { setEditing(item); setForm({...item}); setOpen(true) }
  const save = async () => {
    setLoading(true)
    const res = editing ? await api.put(`/ecg/${editing.id}`, form) : await api.post('/ecg', form)
    setLoading(false)
    if (res.id) { load(); setOpen(false) }
  }
  const remove = async (id) => { if (confirm('حذف هذا السجل؟')) { await api.del(`/ecg/${id}`); load() } }

  return (
    <>
      {lightbox && (
        <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4" onClick={() => setLightbox(null)}>
          <img src={lightbox} alt="رسم القلب" className="max-w-full max-h-full rounded-xl object-contain" />
        </div>
      )}
      <div className="flex justify-end mb-4">
        <Button onClick={openAdd} className="gap-2 bg-blue-600 hover:bg-blue-700"><Plus className="w-4 h-4" /> إضافة رسم قلب</Button>
      </div>

      {items.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <Zap className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>لا توجد رسومات قلب مسجلة بعد</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {items.map(r => (
            <Card key={r.id} className="border-r-4 border-r-red-400">
              <CardContent className="p-5">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex gap-4 flex-1 min-w-0">
                    {r.attachment_data ? (
                      <button onClick={() => setLightbox(r.attachment_data)} className="shrink-0 group relative">
                        <img src={r.attachment_data} alt="ECG" className="w-24 h-16 object-cover rounded-lg border border-gray-200 group-hover:opacity-80 transition-opacity" />
                        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 bg-black/30 rounded-lg transition-opacity">
                          <ZoomIn className="w-5 h-5 text-white" />
                        </div>
                      </button>
                    ) : (
                      <div className="w-24 h-16 bg-gray-100 rounded-lg flex items-center justify-center shrink-0">
                        <Zap className="w-6 h-6 text-gray-300" />
                      </div>
                    )}
                    <div className="flex-1 grid grid-cols-2 md:grid-cols-3 gap-3">
                      <FieldRow label="التاريخ" value={r.ecg_date} />
                      {r.facility && <FieldRow label="المركز" value={r.facility} />}
                      {r.ordering_doctor && <FieldRow label="الطبيب" value={r.ordering_doctor} />}
                      {r.findings && <div className="col-span-full"><FieldRow label="النتائج" value={r.findings} /></div>}
                    </div>
                  </div>
                  <div className="flex gap-2 shrink-0">
                    <Button size="icon" variant="ghost" onClick={() => openEdit(r)}><Pencil className="w-4 h-4" /></Button>
                    <Button size="icon" variant="ghost" className="text-red-500" onClick={() => remove(r.id)}><Trash2 className="w-4 h-4" /></Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-lg" dir="rtl">
          <DialogHeader><DialogTitle>{editing ? 'تعديل' : 'إضافة'} رسم قلب (ECG)</DialogTitle></DialogHeader>
          <div className="grid grid-cols-2 gap-4 py-2">
            <div className="col-span-2">
              <label className="text-xs text-gray-500 mb-1 block">تاريخ رسم القلب</label>
              <Input type="date" value={form.ecg_date || ''} onChange={e => setForm({...form, ecg_date: e.target.value})} />
            </div>
            <Input placeholder="المركز / المستشفى" value={form.facility || ''} onChange={e => setForm({...form, facility: e.target.value})} />
            <Input placeholder="الطبيب المعالج" value={form.ordering_doctor || ''} onChange={e => setForm({...form, ordering_doctor: e.target.value})} />
            <div className="col-span-2">
              <label className="text-xs text-gray-500 mb-1 block">النتائج / الملاحظات</label>
              <textarea value={form.findings || ''} onChange={e => setForm({...form, findings: e.target.value})} rows={3} className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-400" placeholder="وصف موجات رسم القلب، أي ملاحظات..." />
            </div>
            <ImageUpload label="📈 صورة رسم القلب *" value={form.attachment_data || null} onChange={v => setForm({...form, attachment_data: v})} />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>إلغاء</Button>
            <Button onClick={save} disabled={loading} className="bg-blue-600 hover:bg-blue-700">{loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'حفظ'}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

// ══════════════════════════════════════════════
// الصفحة الرئيسية
// ══════════════════════════════════════════════
export default function MedicalRecordPage() {
  const { token } = useAuth()
  const navigate  = useNavigate()
  const api = useApi(token)

  const tabs = [
    { id: 'diseases',    label: 'الأمراض',       icon: <Activity className="w-4 h-4" />,      component: <DiseasesTab api={api} /> },
    { id: 'surgeries',   label: 'العمليات',       icon: <Stethoscope className="w-4 h-4" />,   component: <SurgeriesTab api={api} /> },
    { id: 'allergies',   label: 'الحساسية',       icon: <AlertTriangle className="w-4 h-4" />, component: <AllergiesTab api={api} /> },
    { id: 'medications', label: 'الأدوية',        icon: <Pill className="w-4 h-4" />,          component: <MedicationsTab api={api} /> },
    { id: 'vaccinations',label: 'التطعيمات',      icon: <Syringe className="w-4 h-4" />,       component: <VaccinationsTab api={api} /> },
    { id: 'lab_tests',   label: 'التحاليل',       icon: <FlaskConical className="w-4 h-4" />,  component: <LabTestsTab api={api} /> },
    { id: 'blood_gas',   label: 'غازات الدم',     icon: <Activity className="w-4 h-4" />,      component: <BloodGasTab api={api} /> },
    { id: 'ecg',         label: 'رسم القلب',      icon: <Zap className="w-4 h-4" />,           component: <ECGTab api={api} /> },
    { id: 'radiology',   label: 'الأشعة',         icon: <RadioTower className="w-4 h-4" />,    component: <RadiologyTab api={api} /> },
    { id: 'history',     label: 'التاريخ المرضي', icon: <History className="w-4 h-4" />,       component: <MedicalHistoryTab api={api} /> },
  ]

  return (
    <div className="min-h-screen bg-gray-50 py-8" dir="rtl">
      <div className="max-w-6xl mx-auto px-4">
        {/* رأس الصفحة */}
        <div className="flex items-center justify-between gap-4 mb-6">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl flex items-center justify-center shadow-lg">
              <ClipboardList className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">الملف الطبي الإلكتروني</h1>
              <p className="text-gray-500 text-sm mt-0.5">سجلك الصحي الشامل في مكان واحد</p>
            </div>
          </div>
          <Button
            onClick={() => navigate('/medical-record/report')}
            variant="outline"
            className="gap-2 border-blue-200 text-blue-700 hover:bg-blue-50"
          >
            <FileDown className="w-4 h-4" /> تقرير طبي شامل
          </Button>
        </div>

        {/* المقاييس الحيوية */}
        <PatientVitalsCard api={api} />

        {/* التبويبات */}
        <Tabs defaultValue="diseases">
          <TabsList className="flex flex-wrap h-auto gap-1 bg-white border rounded-xl p-2 mb-6 shadow-sm">
            {tabs.map(t => (
              <TabsTrigger
                key={t.id}
                value={t.id}
                className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm data-[state=active]:bg-blue-600 data-[state=active]:text-white"
              >
                {t.icon} {t.label}
              </TabsTrigger>
            ))}
          </TabsList>

          {tabs.map(t => (
            <TabsContent key={t.id} value={t.id}>
              <Card className="shadow-sm">
                <CardHeader className="border-b pb-4">
                  <div className="flex items-center gap-2">
                    <span className="text-blue-600">{t.icon}</span>
                    <CardTitle className="text-lg">{t.label}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent className="pt-6">
                  {t.component}
                </CardContent>
              </Card>
            </TabsContent>
          ))}
        </Tabs>
      </div>
    </div>
  )
}
