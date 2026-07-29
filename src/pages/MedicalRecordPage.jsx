import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Badge } from '../components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import {
  Activity, AlertTriangle, Pill, Syringe, FlaskConical,
  RadioTower, History, Stethoscope, Plus, Pencil, Trash2,
  ChevronDown, ChevronUp, User, Calendar, Building2, ClipboardList,
  Loader2, FileText
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

// ── مكوّن عام لعرض بطاقة إدخال ──
function FieldRow({ label, value, children }) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs font-medium text-gray-500">{label}</label>
      {children || <p className="text-sm text-gray-800">{value || '—'}</p>}
    </div>
  )
}

// ── شارات الحالة ──
const severityColors = { mild: 'bg-yellow-100 text-yellow-800', moderate: 'bg-orange-100 text-orange-800', severe: 'bg-red-100 text-red-800' }
const statusColors = { active: 'bg-blue-100 text-blue-800', chronic: 'bg-purple-100 text-purple-800', resolved: 'bg-green-100 text-green-800', normal: 'bg-green-100 text-green-800', abnormal: 'bg-orange-100 text-orange-800', critical: 'bg-red-100 text-red-800' }
const statusLabels = { active: 'نشط', chronic: 'مزمن', resolved: 'شُفي', normal: 'طبيعي', abnormal: 'غير طبيعي', critical: 'حرج' }
const severityLabels = { mild: 'خفيف', moderate: 'متوسط', severe: 'شديد' }
const scanTypeLabels = { xray: 'أشعة X', mri: 'رنين مغناطيسي', ct: 'أشعة مقطعية', ultrasound: 'موجات صوتية', pet: 'PET Scan', mammo: 'ماموجرام' }
const anesthesiaLabels = { general: 'عامة', local: 'موضعية', spinal: 'نخاعية', epidural: 'فوق الجافية' }
const outcomeLabels = { successful: 'ناجحة', complicated: 'مع مضاعفات', failed: 'فاشلة' }

// ── مكوّن قائمة عامة ──
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
                <FieldRow label="الحالة">
                  <Badge className={statusColors[d.status] || 'bg-gray-100'}>{statusLabels[d.status] || d.status}</Badge>
                </FieldRow>
                <FieldRow label="الشدة">
                  {d.severity && <Badge className={severityColors[d.severity]}>{severityLabels[d.severity]}</Badge>}
                </FieldRow>
                <FieldRow label="تاريخ التشخيص" value={d.diagnosis_date} />
                <FieldRow label="الطبيب المعالج" value={d.treating_doctor} />
                <FieldRow label="المستشفى" value={d.hospital} />
                {d.notes && <div className="col-span-full"><FieldRow label="ملاحظات" value={d.notes} /></div>}
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
            <Input type="date" placeholder="تاريخ التشخيص" value={form.diagnosis_date || ''} onChange={e => setForm({ ...form, diagnosis_date: e.target.value })} />
            <Input placeholder="الطبيب المعالج" value={form.treating_doctor || ''} onChange={e => setForm({ ...form, treating_doctor: e.target.value })} />
            <Input placeholder="المستشفى / العيادة" value={form.hospital || ''} onChange={e => setForm({ ...form, hospital: e.target.value })} />
            <Input type="date" placeholder="تاريخ الشفاء" value={form.resolution_date || ''} onChange={e => setForm({ ...form, resolution_date: e.target.value })} />
            <div className="col-span-2"><Input placeholder="ملخص العلاج" value={form.treatment_summary || ''} onChange={e => setForm({ ...form, treatment_summary: e.target.value })} /></div>
            <div className="col-span-2"><Input placeholder="ملاحظات" value={form.notes || ''} onChange={e => setForm({ ...form, notes: e.target.value })} /></div>
          </div>
          <DialogFooter><Button onClick={save} disabled={loading} className="bg-blue-600 hover:bg-blue-700">{loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'حفظ'}</Button></DialogFooter>
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
                <FieldRow label="تاريخ العملية" value={s.surgery_date} />
                <FieldRow label="المستشفى" value={s.hospital} />
                <FieldRow label="الجراح" value={s.surgeon} />
                <FieldRow label="التخدير" value={anesthesiaLabels[s.anesthesia_type] || s.anesthesia_type} />
                <FieldRow label="النتيجة">
                  {s.outcome && <Badge className={s.outcome === 'successful' ? 'bg-green-100 text-green-800' : s.outcome === 'complicated' ? 'bg-orange-100 text-orange-800' : 'bg-red-100 text-red-800'}>{outcomeLabels[s.outcome] || s.outcome}</Badge>}
                </FieldRow>
                {s.complications && <FieldRow label="المضاعفات" value={s.complications} />}
                {s.notes && <FieldRow label="ملاحظات" value={s.notes} />}
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
            <Input type="date" placeholder="تاريخ العملية" value={form.surgery_date || ''} onChange={e => setForm({ ...form, surgery_date: e.target.value })} />
            <Input placeholder="المستشفى" value={form.hospital || ''} onChange={e => setForm({ ...form, hospital: e.target.value })} />
            <Input placeholder="الجراح" value={form.surgeon || ''} onChange={e => setForm({ ...form, surgeon: e.target.value })} />
            <Select value={form.anesthesia_type || ''} onValueChange={v => setForm({ ...form, anesthesia_type: v })}>
              <SelectTrigger><SelectValue placeholder="نوع التخدير" /></SelectTrigger>
              <SelectContent><SelectItem value="general">عامة</SelectItem><SelectItem value="local">موضعية</SelectItem><SelectItem value="spinal">نخاعية</SelectItem><SelectItem value="epidural">فوق الجافية</SelectItem></SelectContent>
            </Select>
            <Select value={form.outcome || 'successful'} onValueChange={v => setForm({ ...form, outcome: v })}>
              <SelectTrigger><SelectValue placeholder="النتيجة" /></SelectTrigger>
              <SelectContent><SelectItem value="successful">ناجحة</SelectItem><SelectItem value="complicated">مع مضاعفات</SelectItem><SelectItem value="failed">فاشلة</SelectItem></SelectContent>
            </Select>
            <Input type="number" placeholder="مدة العملية (دقيقة)" value={form.duration_minutes || ''} onChange={e => setForm({ ...form, duration_minutes: e.target.value })} />
            <Input type="date" placeholder="تاريخ المتابعة" value={form.follow_up_date || ''} onChange={e => setForm({ ...form, follow_up_date: e.target.value })} />
            <div className="col-span-2"><Input placeholder="المضاعفات" value={form.complications || ''} onChange={e => setForm({ ...form, complications: e.target.value })} /></div>
            <div className="col-span-2"><Input placeholder="ملاحظات ما بعد العملية" value={form.post_op_notes || ''} onChange={e => setForm({ ...form, post_op_notes: e.target.value })} /></div>
            <div className="col-span-2"><Input placeholder="ملاحظات" value={form.notes || ''} onChange={e => setForm({ ...form, notes: e.target.value })} /></div>
          </div>
          <DialogFooter><Button onClick={save} disabled={loading} className="bg-blue-600 hover:bg-blue-700">{loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'حفظ'}</Button></DialogFooter>
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
                <FieldRow label="الشدة">
                  {a.severity && <Badge className={severityColors[a.severity]}>{severityLabels[a.severity]}</Badge>}
                </FieldRow>
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
          <DialogFooter><Button onClick={save} disabled={loading} className="bg-blue-600 hover:bg-blue-700">{loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'حفظ'}</Button></DialogFooter>
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
    <Card key={m.id} className={`border-r-4 ${m.is_active ? 'border-r-green-500' : 'border-r-gray-300 opacity-75'}`}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 grid grid-cols-2 md:grid-cols-3 gap-4">
            <FieldRow label="اسم الدواء" value={m.name} />
            <FieldRow label="الجرعة" value={m.dosage} />
            <FieldRow label="التكرار" value={m.frequency} />
            <FieldRow label="الشكل" value={m.form} />
            <FieldRow label="من" value={m.start_date} />
            <FieldRow label="إلى" value={m.end_date} />
            <FieldRow label="الحالة">
              <Badge className={m.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}>{m.is_active ? 'جارٍ' : 'منتهٍ'}</Badge>
            </FieldRow>
            {m.instructions && <FieldRow label="التعليمات" value={m.instructions} />}
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
            <Input placeholder="الاسم العلمي" value={form.generic_name || ''} onChange={e => setForm({ ...form, generic_name: e.target.value })} />
            <Input placeholder="الجرعة *" value={form.dosage || ''} onChange={e => setForm({ ...form, dosage: e.target.value })} />
            <Select value={form.form || ''} onValueChange={v => setForm({ ...form, form: v })}>
              <SelectTrigger><SelectValue placeholder="الشكل" /></SelectTrigger>
              <SelectContent><SelectItem value="tablet">حبة</SelectItem><SelectItem value="capsule">كبسولة</SelectItem><SelectItem value="syrup">شراب</SelectItem><SelectItem value="injection">حقنة</SelectItem><SelectItem value="cream">كريم</SelectItem><SelectItem value="drops">قطرة</SelectItem><SelectItem value="inhaler">بخاخ</SelectItem></SelectContent>
            </Select>
            <Input placeholder="التكرار *" value={form.frequency || ''} onChange={e => setForm({ ...form, frequency: e.target.value })} />
            <Input placeholder="المدة" value={form.duration || ''} onChange={e => setForm({ ...form, duration: e.target.value })} />
            <Input type="date" placeholder="تاريخ البدء" value={form.start_date || ''} onChange={e => setForm({ ...form, start_date: e.target.value })} />
            <Input type="date" placeholder="تاريخ الانتهاء" value={form.end_date || ''} onChange={e => setForm({ ...form, end_date: e.target.value })} />
            <div className="col-span-2"><Input placeholder="تعليمات الاستخدام" value={form.instructions || ''} onChange={e => setForm({ ...form, instructions: e.target.value })} /></div>
            <div className="col-span-2 flex items-center gap-3">
              <input type="checkbox" id="is_active" checked={!!form.is_active} onChange={e => setForm({ ...form, is_active: e.target.checked })} className="w-4 h-4" />
              <label htmlFor="is_active" className="text-sm">دواء حالي (جارٍ استخدامه)</label>
            </div>
          </div>
          <DialogFooter><Button onClick={save} disabled={loading} className="bg-blue-600 hover:bg-blue-700">{loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'حفظ'}</Button></DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

// ══════════════════════════════════════════════
// التطعيمات
// ══════════════════════════════════════════════
function VaccinationsTab({ api }) {
  const [items, setItems] = useState([])
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({})
  const [loading, setLoading] = useState(false)

  const load = useCallback(() => api.get('/vaccinations').then(d => Array.isArray(d) && setItems(d)), [api])
  useEffect(() => { load() }, [load])
  const openAdd = () => { setEditing(null); setForm({ dose_number: 1 }); setOpen(true) }
  const openEdit = (item) => { setEditing(item); setForm({ ...item }); setOpen(true) }
  const save = async () => {
    setLoading(true)
    const res = editing ? await api.put(`/vaccinations/${editing.id}`, form) : await api.post('/vaccinations', form)
    setLoading(false)
    if (res.id) { load(); setOpen(false) }
  }
  const remove = async (id) => { if (confirm('هل تريد حذف هذا السجل؟')) { await api.del(`/vaccinations/${id}`); load() } }

  return (
    <>
      <SectionList items={items} addLabel="إضافة تطعيم" onAdd={openAdd} renderCard={(v) => (
        <Card key={v.id} className="border-r-4 border-r-teal-500">
          <CardContent className="p-5">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 grid grid-cols-2 md:grid-cols-3 gap-4">
                <FieldRow label="التطعيم" value={v.vaccine_name} />
                <FieldRow label="يقي من" value={v.disease_prevented} />
                <FieldRow label="الجرعة" value={v.dose_number && v.total_doses ? `${v.dose_number} / ${v.total_doses}` : v.dose_number} />
                <FieldRow label="تاريخ التطعيم" value={v.date_given} />
                <FieldRow label="الجرعة التالية" value={v.next_due_date} />
                <FieldRow label="الجهة المقدِّمة" value={v.provider} />
                <FieldRow label="مكان الحقن" value={v.administration_site} />
                {v.reaction && <FieldRow label="رد فعل" value={v.reaction} />}
              </div>
              <div className="flex gap-2 shrink-0">
                <Button size="icon" variant="ghost" onClick={() => openEdit(v)}><Pencil className="w-4 h-4" /></Button>
                <Button size="icon" variant="ghost" className="text-red-500" onClick={() => remove(v.id)}><Trash2 className="w-4 h-4" /></Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )} />
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-lg" dir="rtl">
          <DialogHeader><DialogTitle>{editing ? 'تعديل' : 'إضافة'} تطعيم</DialogTitle></DialogHeader>
          <div className="grid grid-cols-2 gap-4 py-2">
            <div className="col-span-2"><Input placeholder="اسم التطعيم *" value={form.vaccine_name || ''} onChange={e => setForm({ ...form, vaccine_name: e.target.value })} /></div>
            <Input placeholder="يقي من" value={form.disease_prevented || ''} onChange={e => setForm({ ...form, disease_prevented: e.target.value })} />
            <Input placeholder="الجهة المقدِّمة" value={form.provider || ''} onChange={e => setForm({ ...form, provider: e.target.value })} />
            <Input type="number" placeholder="رقم الجرعة" value={form.dose_number || ''} onChange={e => setForm({ ...form, dose_number: e.target.value })} />
            <Input type="number" placeholder="إجمالي الجرعات" value={form.total_doses || ''} onChange={e => setForm({ ...form, total_doses: e.target.value })} />
            <Input type="date" placeholder="تاريخ التطعيم" value={form.date_given || ''} onChange={e => setForm({ ...form, date_given: e.target.value })} />
            <Input type="date" placeholder="تاريخ الجرعة القادمة" value={form.next_due_date || ''} onChange={e => setForm({ ...form, next_due_date: e.target.value })} />
            <Input placeholder="مكان الحقن" value={form.administration_site || ''} onChange={e => setForm({ ...form, administration_site: e.target.value })} />
            <Input placeholder="رقم الدُّفعة" value={form.batch_number || ''} onChange={e => setForm({ ...form, batch_number: e.target.value })} />
            <div className="col-span-2"><Input placeholder="رد فعل بعد التطعيم" value={form.reaction || ''} onChange={e => setForm({ ...form, reaction: e.target.value })} /></div>
            <div className="col-span-2"><Input placeholder="ملاحظات" value={form.notes || ''} onChange={e => setForm({ ...form, notes: e.target.value })} /></div>
          </div>
          <DialogFooter><Button onClick={save} disabled={loading} className="bg-blue-600 hover:bg-blue-700">{loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'حفظ'}</Button></DialogFooter>
        </DialogContent>
      </Dialog>
    </>
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

  const load = useCallback(() => api.get('/lab-tests').then(d => Array.isArray(d) && setItems(d)), [api])
  useEffect(() => { load() }, [load])
  const openAdd = () => { setEditing(null); setForm({ status: 'normal' }); setOpen(true) }
  const openEdit = (item) => { setEditing(item); setForm({ ...item }); setOpen(true) }
  const save = async () => {
    setLoading(true)
    const res = editing ? await api.put(`/lab-tests/${editing.id}`, form) : await api.post('/lab-tests', form)
    setLoading(false)
    if (res.id) { load(); setOpen(false) }
  }
  const remove = async (id) => { if (confirm('هل تريد حذف هذا السجل؟')) { await api.del(`/lab-tests/${id}`); load() } }

  return (
    <>
      <SectionList items={items} addLabel="إضافة تحليل" onAdd={openAdd} renderCard={(t) => (
        <Card key={t.id} className={`border-r-4 ${t.status === 'critical' ? 'border-r-red-500' : t.status === 'abnormal' ? 'border-r-orange-400' : 'border-r-green-400'}`}>
          <CardContent className="p-5">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-4">
                <FieldRow label="التحليل" value={t.test_name} />
                <FieldRow label="التصنيف" value={t.test_category} />
                <FieldRow label="التاريخ" value={t.test_date} />
                <FieldRow label="المعمل" value={t.lab_name} />
                <FieldRow label="النتيجة" value={t.result_value && `${t.result_value} ${t.unit || ''}`} />
                <FieldRow label="المرجع الطبيعي" value={t.reference_range} />
                <FieldRow label="الحالة">
                  <Badge className={statusColors[t.status] || 'bg-gray-100'}>{statusLabels[t.status] || t.status}</Badge>
                </FieldRow>
                <FieldRow label="الطبيب الطالب" value={t.ordering_doctor} />
                {t.interpretation && <div className="col-span-full"><FieldRow label="التفسير" value={t.interpretation} /></div>}
              </div>
              <div className="flex gap-2 shrink-0">
                <Button size="icon" variant="ghost" onClick={() => openEdit(t)}><Pencil className="w-4 h-4" /></Button>
                <Button size="icon" variant="ghost" className="text-red-500" onClick={() => remove(t.id)}><Trash2 className="w-4 h-4" /></Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )} />
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-lg" dir="rtl">
          <DialogHeader><DialogTitle>{editing ? 'تعديل' : 'إضافة'} تحليل مخبري</DialogTitle></DialogHeader>
          <div className="grid grid-cols-2 gap-4 py-2">
            <div className="col-span-2"><Input placeholder="اسم التحليل *" value={form.test_name || ''} onChange={e => setForm({ ...form, test_name: e.target.value })} /></div>
            <Select value={form.test_category || ''} onValueChange={v => setForm({ ...form, test_category: v })}>
              <SelectTrigger><SelectValue placeholder="التصنيف" /></SelectTrigger>
              <SelectContent><SelectItem value="blood">دم</SelectItem><SelectItem value="urine">بول</SelectItem><SelectItem value="culture">مزرعة</SelectItem><SelectItem value="hormones">هرمونات</SelectItem><SelectItem value="chemistry">كيمياء</SelectItem><SelectItem value="immunology">مناعة</SelectItem><SelectItem value="other">أخرى</SelectItem></SelectContent>
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
          </div>
          <DialogFooter><Button onClick={save} disabled={loading} className="bg-blue-600 hover:bg-blue-700">{loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'حفظ'}</Button></DialogFooter>
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

  return (
    <>
      <SectionList items={items} addLabel="إضافة أشعة" onAdd={openAdd} renderCard={(r) => (
        <Card key={r.id} className="border-r-4 border-r-indigo-500">
          <CardContent className="p-5">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 grid grid-cols-2 md:grid-cols-3 gap-4">
                <FieldRow label="نوع الأشعة" value={scanTypeLabels[r.scan_type] || r.scan_type} />
                <FieldRow label="المنطقة" value={r.body_part} />
                <FieldRow label="التاريخ" value={r.scan_date} />
                <FieldRow label="المنشأة" value={r.facility} />
                <FieldRow label="أخصائي الأشعة" value={r.radiologist} />
                <FieldRow label="الطبيب الطالب" value={r.ordering_doctor} />
                {r.reason && <FieldRow label="سبب الطلب" value={r.reason} />}
                {r.findings && <div className="col-span-full"><FieldRow label="النتائج" value={r.findings} /></div>}
                {r.impression && <div className="col-span-full"><FieldRow label="التفسير النهائي" value={r.impression} /></div>}
                {r.recommendation && <div className="col-span-full"><FieldRow label="التوصيات" value={r.recommendation} /></div>}
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
          <DialogHeader><DialogTitle>{editing ? 'تعديل' : 'إضافة'} أشعة</DialogTitle></DialogHeader>
          <div className="grid grid-cols-2 gap-4 py-2">
            <Select value={form.scan_type || 'xray'} onValueChange={v => setForm({ ...form, scan_type: v })}>
              <SelectTrigger><SelectValue placeholder="نوع الأشعة *" /></SelectTrigger>
              <SelectContent><SelectItem value="xray">أشعة X</SelectItem><SelectItem value="mri">رنين مغناطيسي</SelectItem><SelectItem value="ct">أشعة مقطعية CT</SelectItem><SelectItem value="ultrasound">موجات صوتية</SelectItem><SelectItem value="pet">PET Scan</SelectItem><SelectItem value="mammo">ماموجرام</SelectItem></SelectContent>
            </Select>
            <Input placeholder="المنطقة المصوَّرة *" value={form.body_part || ''} onChange={e => setForm({ ...form, body_part: e.target.value })} />
            <Input type="date" value={form.scan_date || ''} onChange={e => setForm({ ...form, scan_date: e.target.value })} />
            <Input placeholder="المنشأة / المركز" value={form.facility || ''} onChange={e => setForm({ ...form, facility: e.target.value })} />
            <Input placeholder="أخصائي الأشعة" value={form.radiologist || ''} onChange={e => setForm({ ...form, radiologist: e.target.value })} />
            <Input placeholder="الطبيب الطالب" value={form.ordering_doctor || ''} onChange={e => setForm({ ...form, ordering_doctor: e.target.value })} />
            <div className="col-span-2"><Input placeholder="سبب الطلب" value={form.reason || ''} onChange={e => setForm({ ...form, reason: e.target.value })} /></div>
            <div className="col-span-2"><textarea rows={2} placeholder="النتائج" className="w-full border rounded-md px-3 py-2 text-sm" value={form.findings || ''} onChange={e => setForm({ ...form, findings: e.target.value })} /></div>
            <div className="col-span-2"><textarea rows={2} placeholder="التفسير النهائي" className="w-full border rounded-md px-3 py-2 text-sm" value={form.impression || ''} onChange={e => setForm({ ...form, impression: e.target.value })} /></div>
            <div className="col-span-2"><Input placeholder="التوصيات" value={form.recommendation || ''} onChange={e => setForm({ ...form, recommendation: e.target.value })} /></div>
          </div>
          <DialogFooter><Button onClick={save} disabled={loading} className="bg-blue-600 hover:bg-blue-700">{loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'حفظ'}</Button></DialogFooter>
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

  return (
    <div className="space-y-6">
      {!editing ? (
        <>
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
                  {data.diet_type && <FieldRow label="النظام الغذائي" value={data.diet_type} />}
                </CardContent>
              </Card>
              <Card><CardHeader><CardTitle className="text-base">الحالات المزمنة والوراثية</CardTitle></CardHeader>
                <CardContent className="space-y-3">
                  <FieldRow label="أمراض مزمنة" value={data.chronic_conditions} />
                  <FieldRow label="أمراض وراثية" value={data.genetic_conditions} />
                  <FieldRow label="ملاحظات عامة" value={data.general_notes} />
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
        </>
      ) : (
        <div className="space-y-6">
          <Card><CardHeader><CardTitle className="text-base">العادات الصحية</CardTitle></CardHeader>
            <CardContent className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div>
                <label className="text-xs text-gray-500 mb-1 block">التدخين</label>
                <Select value={form.smoking_status || ''} onValueChange={v => setForm({ ...form, smoking_status: v })}>
                  <SelectTrigger><SelectValue placeholder="التدخين" /></SelectTrigger>
                  <SelectContent><SelectItem value="never">لا يدخن</SelectItem><SelectItem value="former">سبق له</SelectItem><SelectItem value="current">مدخن حالياً</SelectItem></SelectContent>
                </Select>
              </div>
              <div><label className="text-xs text-gray-500 mb-1 block">سنوات التدخين</label><Input type="number" value={form.smoking_years || ''} onChange={e => setForm({ ...form, smoking_years: e.target.value })} /></div>
              <div>
                <label className="text-xs text-gray-500 mb-1 block">الكحول</label>
                <Select value={form.alcohol_use || ''} onValueChange={v => setForm({ ...form, alcohol_use: v })}>
                  <SelectTrigger><SelectValue placeholder="الكحول" /></SelectTrigger>
                  <SelectContent><SelectItem value="never">لا</SelectItem><SelectItem value="occasional">أحياناً</SelectItem><SelectItem value="regular">منتظم</SelectItem></SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-xs text-gray-500 mb-1 block">النشاط البدني</label>
                <Select value={form.physical_activity || ''} onValueChange={v => setForm({ ...form, physical_activity: v })}>
                  <SelectTrigger><SelectValue placeholder="النشاط" /></SelectTrigger>
                  <SelectContent><SelectItem value="sedentary">خامل</SelectItem><SelectItem value="light">خفيف</SelectItem><SelectItem value="moderate">معتدل</SelectItem><SelectItem value="active">نشط</SelectItem></SelectContent>
                </Select>
              </div>
              <div><label className="text-xs text-gray-500 mb-1 block">النظام الغذائي</label><Input placeholder="مثال: نباتي، خالٍ من الغلوتين..." value={form.diet_type || ''} onChange={e => setForm({ ...form, diet_type: e.target.value })} /></div>
            </CardContent>
          </Card>

          <Card><CardHeader><CardTitle className="text-base">الحالات الصحية</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div><label className="text-xs text-gray-500 mb-1 block">أمراض مزمنة معروفة</label><textarea rows={2} className="w-full border rounded-md px-3 py-2 text-sm" value={form.chronic_conditions || ''} onChange={e => setForm({ ...form, chronic_conditions: e.target.value })} /></div>
              <div><label className="text-xs text-gray-500 mb-1 block">أمراض وراثية</label><textarea rows={2} className="w-full border rounded-md px-3 py-2 text-sm" value={form.genetic_conditions || ''} onChange={e => setForm({ ...form, genetic_conditions: e.target.value })} /></div>
              <div><label className="text-xs text-gray-500 mb-1 block">ملاحظات عامة</label><textarea rows={2} className="w-full border rounded-md px-3 py-2 text-sm" value={form.general_notes || ''} onChange={e => setForm({ ...form, general_notes: e.target.value })} /></div>
            </CardContent>
          </Card>

          <Card><CardHeader><CardTitle className="text-base">التاريخ العائلي</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-3 gap-3">
                <Input placeholder="المرض" value={familyForm.disease} onChange={e => setFamilyForm({ ...familyForm, disease: e.target.value })} />
                <Input placeholder="صلة القرابة" value={familyForm.relation} onChange={e => setFamilyForm({ ...familyForm, relation: e.target.value })} />
                <div className="flex gap-2"><Input placeholder="ملاحظات" value={familyForm.notes} onChange={e => setFamilyForm({ ...familyForm, notes: e.target.value })} /><Button type="button" size="icon" onClick={addFamily}><Plus className="w-4 h-4" /></Button></div>
              </div>
              {form.family_history?.length > 0 && (
                <div className="divide-y border rounded-md">
                  {form.family_history.map((f, i) => (
                    <div key={i} className="flex items-center justify-between px-4 py-2 text-sm">
                      <span className="font-medium">{f.disease}</span><span className="text-gray-500">{f.relation}</span><span className="text-gray-400">{f.notes}</span>
                      <Button size="icon" variant="ghost" className="text-red-400" onClick={() => removeFamily(i)}><Trash2 className="w-3 h-3" /></Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <div className="flex gap-3 justify-end">
            <Button variant="outline" onClick={() => { setEditing(false); load() }}>إلغاء</Button>
            <Button onClick={save} disabled={loading} className="bg-blue-600 hover:bg-blue-700">{loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'حفظ التاريخ المرضي'}</Button>
          </div>
        </div>
      )}
    </div>
  )
}

// ══════════════════════════════════════════════
// الصفحة الرئيسية
// ══════════════════════════════════════════════
export default function MedicalRecordPage() {
  const { token, user } = useAuth()
  const api = useApi(token)

  const tabs = [
    { id: 'diseases',   label: 'الأمراض',       icon: <Activity className="w-4 h-4" />,     component: <DiseasesTab api={api} /> },
    { id: 'surgeries',  label: 'العمليات',       icon: <Stethoscope className="w-4 h-4" />,  component: <SurgeriesTab api={api} /> },
    { id: 'allergies',  label: 'الحساسية',       icon: <AlertTriangle className="w-4 h-4" />, component: <AllergiesTab api={api} /> },
    { id: 'medications',label: 'الأدوية',        icon: <Pill className="w-4 h-4" />,          component: <MedicationsTab api={api} /> },
    { id: 'vaccinations',label: 'التطعيمات',     icon: <Syringe className="w-4 h-4" />,      component: <VaccinationsTab api={api} /> },
    { id: 'lab',        label: 'التحاليل',       icon: <FlaskConical className="w-4 h-4" />,  component: <LabTestsTab api={api} /> },
    { id: 'radiology',  label: 'الأشعة',         icon: <RadioTower className="w-4 h-4" />,   component: <RadiologyTab api={api} /> },
    { id: 'history',    label: 'التاريخ المرضي', icon: <History className="w-4 h-4" />,      component: <MedicalHistoryTab api={api} /> },
  ]

  return (
    <div className="min-h-screen bg-gray-50 py-8" dir="rtl">
      <div className="max-w-6xl mx-auto px-4">
        {/* رأس الصفحة */}
        <div className="flex items-center gap-4 mb-8">
          <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl flex items-center justify-center shadow-lg">
            <ClipboardList className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">الملف الطبي الإلكتروني</h1>
            <p className="text-gray-500 text-sm mt-0.5">سجلك الصحي الشامل في مكان واحد</p>
          </div>
        </div>

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
