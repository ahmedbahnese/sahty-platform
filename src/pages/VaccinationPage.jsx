import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Syringe, Plus, CheckCircle, Clock, AlertTriangle, Calendar,
  ChevronDown, ChevronUp, Users, User, X, Bell
} from 'lucide-react'

const API = (p) => `/api/vaccinations${p}`
const authHdr = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('token')}`
})

const STATUS_LABEL = { taken: 'مُؤخذ', recommended: 'موصى به', upcoming: 'قادم', overdue: 'متأخر' }
const STATUS_COLOR = {
  taken: 'bg-green-100 text-green-700 border-green-200',
  recommended: 'bg-blue-50 text-blue-700 border-blue-200',
  upcoming: 'bg-amber-50 text-amber-700 border-amber-200',
  overdue: 'bg-red-100 text-red-700 border-red-200',
}

function Badge({ status }) {
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border ${STATUS_COLOR[status] || 'bg-gray-100 text-gray-600'}`}>
      {status === 'taken' && <CheckCircle className="w-3 h-3" />}
      {status === 'overdue' && <AlertTriangle className="w-3 h-3" />}
      {status === 'upcoming' && <Clock className="w-3 h-3" />}
      {STATUS_LABEL[status] || status}
    </span>
  )
}

// ── Vaccine keywords for categorisation ──────────────────────────────────────
const CHILD_VACCINE_KEYWORDS = [
  'bcg', 'السل', 'hepatitis b', 'هيبات', 'التهاب الكبد ب', 'dtp', 'dtap', 'الكزاز الدفتيريا', 'السعال الديكي',
  'polio', 'شلل الأطفال', 'ipv', 'opv', 'hib', 'المستدمية', 'pcv', 'العقدية', 'الرئوية',
  'mmr', 'الحصبة', 'النكاف', 'الحصبة الألمانية', 'varicella', 'الجديري', 'rotavirus', 'العجلي',
  'روتا', 'hepatitis a', 'التهاب الكبد أ', 'meningococcal b', 'السحائي b', 'hpv', 'بابيلوما'
]
const MANDATORY_KEYWORDS = [
  'bcg', 'السل', 'hepatitis b', 'hep b', 'التهاب الكبد ب', 'dtp', 'dtap', 'الكزاز',
  'polio', 'شلل الأطفال', 'hib', 'pcv', 'mmr', 'الحصبة', 'السحائي', 'meningococcal',
  'روتا', 'rotavirus', 'العجلي', 'الجديري', 'varicella'
]

function isChildVaccine(item) {
  const text = `${item.vaccine_name} ${item.disease_prevented || ''} ${item.recommended_ages || ''}`.toLowerCase()
  return CHILD_VACCINE_KEYWORDS.some(k => text.includes(k))
}
function isMandatory(item) {
  const text = `${item.vaccine_name} ${item.disease_prevented || ''}`.toLowerCase()
  return MANDATORY_KEYWORDS.some(k => text.includes(k))
}

// ── ScheduleTab component ─────────────────────────────────────────────────────
function ScheduleTab({ schedule, expandSchedule, setExpandSchedule, setAddPrefill, setShowAdd }) {
  const [scheduleFor, setScheduleFor] = useState('adult') // 'adult' | 'child'

  const filtered = schedule.filter(item =>
    scheduleFor === 'child' ? isChildVaccine(item) : !isChildVaccine(item)
  )
  const mandatory = filtered.filter(isMandatory)
  const additional = filtered.filter(item => !isMandatory(item))

  const VaccineRow = ({ item }) => (
    <div className="flex items-center justify-between bg-white border border-gray-100 rounded-xl px-4 py-3">
      <div className="flex-1">
        <p className="font-medium text-gray-900 text-sm">{item.vaccine_name}</p>
        {item.disease_prevented && <p className="text-xs text-gray-500">{item.disease_prevented}</p>}
        {item.recommended_ages && <p className="text-xs text-gray-400 mt-0.5">{item.recommended_ages}</p>}
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <Badge status={item.status} />
        {item.status !== 'taken' && (
          <button
            onClick={() => { setAddPrefill({ vaccine_name: item.vaccine_name, disease_prevented: item.disease_prevented }); setShowAdd(true) }}
            className="text-xs text-blue-600 hover:underline border border-blue-200 px-2 py-1 rounded-lg"
          >
            سجّل
          </button>
        )}
      </div>
    </div>
  )

  return (
    <div className="space-y-4">
      {/* Toggle: adult/child */}
      <div className="flex rounded-xl overflow-hidden border border-gray-200 w-fit">
        {[{ id: 'adult', label: '🧑 البالغون' }, { id: 'child', label: '👶 الأطفال' }].map(t => (
          <button
            key={t.id}
            onClick={() => setScheduleFor(t.id)}
            className={`px-5 py-2 text-sm font-medium transition-colors ${scheduleFor === t.id ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <p className="text-xs text-gray-400">
        {scheduleFor === 'adult' ? 'الجدول الموصى به للبالغين (18 سنة فأكثر)' : 'الجدول الموصى به للأطفال (0-18 سنة)'}
        {' '}— انقر «سجّل» لإضافة أي لقاح مُؤخذ.
      </p>

      {/* Mandatory section */}
      {mandatory.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-red-500 inline-block" />
            <p className="text-xs font-semibold text-red-700 uppercase tracking-wide">تطعيمات إجبارية ({mandatory.length})</p>
          </div>
          {mandatory.map((item, i) => <VaccineRow key={i} item={item} />)}
        </div>
      )}

      {/* Additional section */}
      {additional.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-400 inline-block" />
            <p className="text-xs font-semibold text-blue-700 uppercase tracking-wide">تطعيمات إضافية ({additional.length})</p>
          </div>
          <div className={`space-y-2 ${!expandSchedule && additional.length > 4 ? 'max-h-64 overflow-hidden relative' : ''}`}>
            {additional.map((item, i) => <VaccineRow key={i} item={item} />)}
            {!expandSchedule && additional.length > 4 && (
              <div className="absolute bottom-0 left-0 right-0 h-12 bg-gradient-to-t from-white to-transparent" />
            )}
          </div>
          {additional.length > 4 && (
            <button onClick={() => setExpandSchedule(e => !e)} className="flex items-center gap-1 text-sm text-blue-600 hover:underline mx-auto">
              {expandSchedule ? <><ChevronUp className="w-4 h-4" />عرض أقل</> : <><ChevronDown className="w-4 h-4" />عرض الكل ({additional.length} لقاح)</>}
            </button>
          )}
        </div>
      )}

      {filtered.length === 0 && (
        <div className="text-center py-10 text-gray-400 text-sm">
          <Syringe className="w-10 h-10 mx-auto mb-2 opacity-30" />
          لا توجد لقاحات مطابقة لهذه الفئة
        </div>
      )}
    </div>
  )
}

// ── AddVaccinationModal ────────────────────────────────────────────────────────
function AddVaccinationModal({ onClose, onSave, prefill = {}, scheduleList = [] }) {
  const [form, setForm] = useState({
    vaccine_name: prefill.vaccine_name || '',
    disease_prevented: prefill.disease_prevented || '',
    dose_number: 1,
    total_doses: '',
    date_given: '',
    next_due_date: '',
    provider: '',
    batch_number: '',
    administration_site: '',
    reaction: '',
    notes: '',
  })
  const [saving, setSaving] = useState(false)
  const [suggestions, setSuggestions] = useState([])

  // Autocomplete from schedule
  const handleVaccineNameChange = (val) => {
    setForm(f => ({ ...f, vaccine_name: val }))
    if (val.length >= 2) {
      const filtered = scheduleList.filter(s =>
        s.vaccine_name.toLowerCase().includes(val.toLowerCase()) ||
        (s.disease_prevented || '').toLowerCase().includes(val.toLowerCase())
      )
      setSuggestions(filtered.slice(0, 6))
    } else {
      setSuggestions([])
    }
  }

  const selectSuggestion = (item) => {
    setForm(f => ({ ...f, vaccine_name: item.vaccine_name, disease_prevented: item.disease_prevented || f.disease_prevented }))
    setSuggestions([])
  }

  const save = async () => {
    if (!form.vaccine_name) return
    setSaving(true)
    try {
      const res = await fetch(API('/'), {
        method: 'POST',
        headers: authHdr(),
        body: JSON.stringify(form),
      })
      const data = await res.json()
      if (data.success) { onSave(data.vaccination); onClose() }
      else alert(data.error || 'حدث خطأ')
    } finally { setSaving(false) }
  }

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between p-5 border-b">
          <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
            <Syringe className="w-5 h-5 text-blue-600" /> تسجيل تطعيم
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600"><X className="w-5 h-5" /></button>
        </div>
        <div className="p-5 space-y-4">
          <div className="relative">
            <Label>اسم اللقاح *</Label>
            <Input
              value={form.vaccine_name}
              onChange={e => handleVaccineNameChange(e.target.value)}
              placeholder="ابدأ بالكتابة للاقتراحات من الجدول..."
              className="mt-1"
              autoComplete="off"
            />
            {suggestions.length > 0 && (
              <div className="absolute z-10 mt-1 w-full bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden">
                {suggestions.map((s, i) => (
                  <button key={i} type="button" onClick={() => selectSuggestion(s)}
                    className="w-full text-right px-4 py-2.5 text-sm hover:bg-blue-50 hover:text-blue-700 border-b border-gray-50 last:border-0 transition-colors">
                    <span className="font-medium">{s.vaccine_name}</span>
                    {s.disease_prevented && <span className="text-gray-400 text-xs mr-2">— {s.disease_prevented}</span>}
                  </button>
                ))}
              </div>
            )}
          </div>
          <div>
            <Label>المرض الذي يقي منه</Label>
            <Input value={form.disease_prevented} onChange={e => setForm(f => ({ ...f, disease_prevented: e.target.value }))} className="mt-1" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label>رقم الجرعة</Label>
              <Input type="number" min="1" value={form.dose_number} onChange={e => setForm(f => ({ ...f, dose_number: parseInt(e.target.value) || 1 }))} className="mt-1" />
            </div>
            <div>
              <Label>إجمالي الجرعات</Label>
              <Input type="number" min="1" value={form.total_doses} onChange={e => setForm(f => ({ ...f, total_doses: e.target.value }))} className="mt-1" placeholder="اختياري" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label>تاريخ التطعيم</Label>
              <Input type="date" value={form.date_given} onChange={e => setForm(f => ({ ...f, date_given: e.target.value }))} className="mt-1" />
            </div>
            <div>
              <Label>موعد الجرعة التالية</Label>
              <Input type="date" value={form.next_due_date} onChange={e => setForm(f => ({ ...f, next_due_date: e.target.value }))} className="mt-1" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label>الجهة المقدِّمة</Label>
              <Input value={form.provider} onChange={e => setForm(f => ({ ...f, provider: e.target.value }))} className="mt-1" placeholder="مثال: مستشفى..." />
            </div>
            <div>
              <Label>موقع الحقن</Label>
              <select value={form.administration_site} onChange={e => setForm(f => ({ ...f, administration_site: e.target.value }))} className="mt-1 w-full border rounded-md px-3 py-2 text-sm">
                <option value="">اختر...</option>
                <option>ذراع يمين</option>
                <option>ذراع يسار</option>
                <option>فخذ يمين</option>
                <option>فخذ يسار</option>
                <option>عضلي</option>
                <option>تحت الجلد</option>
                <option>فموي</option>
              </select>
            </div>
          </div>
          <div>
            <Label>رقم التشغيلة (Batch)</Label>
            <Input value={form.batch_number} onChange={e => setForm(f => ({ ...f, batch_number: e.target.value }))} className="mt-1" placeholder="اختياري" />
          </div>
          <div>
            <Label>تفاعل ما بعد التطعيم</Label>
            <Input value={form.reaction} onChange={e => setForm(f => ({ ...f, reaction: e.target.value }))} className="mt-1" placeholder="لا يوجد / ألم موضعي / ارتفاع حرارة..." />
          </div>
          <div>
            <Label>ملاحظات</Label>
            <textarea value={form.notes} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))} rows={2} className="mt-1 w-full border rounded-md px-3 py-2 text-sm resize-none" />
          </div>
        </div>
        <div className="flex justify-end gap-3 p-5 border-t">
          <Button variant="outline" onClick={onClose}>إلغاء</Button>
          <Button onClick={save} disabled={saving || !form.vaccine_name} className="bg-blue-600 hover:bg-blue-700">
            {saving ? 'جاري الحفظ...' : 'حفظ التطعيم'}
          </Button>
        </div>
      </div>
    </div>
  )
}

function FamilyMemberVaccinations({ members }) {
  const [selected, setSelected] = useState(null)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [showAdd, setShowAdd] = useState(false)
  const [addPrefill, setAddPrefill] = useState({})

  const loadMember = async (m) => {
    setSelected(m)
    setLoading(true)
    try {
      const res = await fetch(API(`/family-member/${m.id}`), { headers: authHdr() })
      const d = await res.json()
      if (d.success) setData(d)
    } finally { setLoading(false) }
  }

  const addMemberVac = async (form) => {
    const res = await fetch(API(`/family-member/${selected.id}`), {
      method: 'POST',
      headers: authHdr(),
      body: JSON.stringify(form),
    })
    const d = await res.json()
    if (d.success && selected) loadMember(selected)
    return d
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-500">اختر فرداً من الأسرة لعرض جدول تطعيماته:</p>
      <div className="flex flex-wrap gap-2">
        {members.map(m => (
          <button key={m.id} onClick={() => loadMember(m)}
            className={`px-3 py-2 rounded-xl text-sm font-medium border transition-all ${selected?.id === m.id ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-700 border-gray-200 hover:border-blue-300'}`}>
            <Users className="inline w-3.5 h-3.5 mr-1" />
            {m.full_name} ({m.relationship})
          </button>
        ))}
      </div>

      {loading && <p className="text-center text-gray-500 py-4">جاري التحميل...</p>}

      {data && selected && !loading && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="font-semibold text-gray-900">تطعيمات {selected.first_name}</h4>
            <Button size="sm" onClick={() => { setAddPrefill({}); setShowAdd(true) }} className="bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 ml-1" /> إضافة
            </Button>
          </div>

          {/* الجرعات المسجلة */}
          {data.vaccinations?.length > 0 ? (
            <div className="space-y-2">
              <p className="text-xs text-gray-500 font-medium">الجرعات المسجلة</p>
              {data.vaccinations.map(v => (
                <div key={v.id} className="bg-green-50 border border-green-200 rounded-xl px-4 py-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900 text-sm">{v.title}</p>
                      {v.description && <p className="text-xs text-gray-500">{v.description}</p>}
                    </div>
                    <div className="text-right text-xs text-gray-500">
                      {v.date && <p>{v.date}</p>}
                      {v.next_due_date && <p className="text-amber-600">التالي: {v.next_due_date}</p>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : <p className="text-sm text-gray-400">لا توجد جرعات مسجلة بعد</p>}

          {/* الجدول المقترح للطفل */}
          {data.schedule?.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs text-gray-500 font-medium">الجدول المقترح</p>
              <div className="space-y-1.5 max-h-64 overflow-y-auto">
                {data.schedule.map((item, i) => (
                  <div key={i} className="flex items-center justify-between bg-white border border-gray-100 rounded-lg px-3 py-2">
                    <div>
                      <p className="text-sm font-medium text-gray-800">{item.vaccine_name}</p>
                      {item.due_date && <p className="text-xs text-gray-400">{item.due_date}</p>}
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge status={item.status} />
                      {item.status !== 'taken' && (
                        <button onClick={() => { setAddPrefill({ vaccine_name: item.vaccine_name, disease_prevented: item.disease_prevented }); setShowAdd(true) }}
                          className="text-xs text-blue-600 hover:underline">سجّل</button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {showAdd && (
        <AddMemberVacModal
          onClose={() => setShowAdd(false)}
          onSave={async (form) => { await addMemberVac(form); setShowAdd(false) }}
          prefill={addPrefill}
        />
      )}
    </div>
  )
}

function AddMemberVacModal({ onClose, onSave, prefill = {} }) {
  const [form, setForm] = useState({
    vaccine_name: prefill.vaccine_name || '',
    disease_prevented: prefill.disease_prevented || '',
    date: '',
    next_due_date: '',
    provider: '',
    hospital_name: '',
    reaction: '',
  })
  const [saving, setSaving] = useState(false)
  const save = async () => {
    setSaving(true)
    try { await onSave(form) } finally { setSaving(false) }
  }

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between p-5 border-b">
          <h3 className="font-bold text-gray-900">تسجيل تطعيم لفرد الأسرة</h3>
          <button onClick={onClose}><X className="w-5 h-5 text-gray-400" /></button>
        </div>
        <div className="p-5 space-y-3">
          <div>
            <Label>اسم اللقاح *</Label>
            <Input value={form.vaccine_name} onChange={e => setForm(f => ({ ...f, vaccine_name: e.target.value }))} className="mt-1" />
          </div>
          <div>
            <Label>المرض الذي يقي منه</Label>
            <Input value={form.disease_prevented} onChange={e => setForm(f => ({ ...f, disease_prevented: e.target.value }))} className="mt-1" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><Label>تاريخ التطعيم *</Label><Input type="date" value={form.date} onChange={e => setForm(f => ({ ...f, date: e.target.value }))} className="mt-1" /></div>
            <div><Label>الجرعة التالية</Label><Input type="date" value={form.next_due_date} onChange={e => setForm(f => ({ ...f, next_due_date: e.target.value }))} className="mt-1" /></div>
          </div>
          <div><Label>الجهة</Label><Input value={form.provider} onChange={e => setForm(f => ({ ...f, provider: e.target.value }))} className="mt-1" /></div>
          <div><Label>تفاعل</Label><Input value={form.reaction} onChange={e => setForm(f => ({ ...f, reaction: e.target.value }))} className="mt-1" /></div>
        </div>
        <div className="flex justify-end gap-3 p-5 border-t">
          <Button variant="outline" onClick={onClose}>إلغاء</Button>
          <Button onClick={save} disabled={saving || !form.vaccine_name || !form.date} className="bg-blue-600 hover:bg-blue-700">
            {saving ? 'حفظ...' : 'حفظ'}
          </Button>
        </div>
      </div>
    </div>
  )
}

export default function VaccinationPage() {
  const { user } = useAuth()
  const [tab, setTab] = useState('my')
  const [vaccinations, setVaccinations] = useState([])
  const [schedule, setSchedule] = useState([])
  const [upcoming, setUpcoming] = useState([])
  const [overdue, setOverdue] = useState([])
  const [familyMembers, setFamilyMembers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [addPrefill, setAddPrefill] = useState({})
  const [expandSchedule, setExpandSchedule] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [vacRes, schedRes, upRes] = await Promise.all([
        fetch(API('/'), { headers: authHdr() }),
        fetch(API('/schedule'), { headers: authHdr() }),
        fetch(API('/upcoming'), { headers: authHdr() }),
      ])
      const [vacData, schedData, upData] = await Promise.all([vacRes.json(), schedRes.json(), upRes.json()])
      if (vacData.success) setVaccinations(vacData.vaccinations)
      if (schedData.success) setSchedule(schedData.schedule)
      if (upData.success) { setUpcoming(upData.upcoming); setOverdue(upData.overdue) }

      // أفراد الأسرة
      const grpRes = await fetch('/api/family/groups', { headers: authHdr() })
      const grpData = await grpRes.json()
      if (grpData.success && grpData.groups.length > 0) {
        const g = grpData.groups[0]
        const memRes = await fetch(`/api/family/groups/${g.id}`, { headers: authHdr() })
        const memData = await memRes.json()
        if (memData.success) setFamilyMembers(memData.members)
      }
    } catch (e) { console.error(e) }
    setLoading(false)
  }, [])

  useEffect(() => { load() }, [load])

  const onVacSaved = (vac) => {
    setVaccinations(prev => [vac, ...prev])
    load()
  }

  const takenCount = vaccinations.filter(v => v.date_given).length

  return (
    <div className="min-h-screen bg-gray-50 py-8" dir="rtl">
      <div className="max-w-5xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 rounded-2xl bg-blue-600 flex items-center justify-center">
              <Syringe className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">إدارة التطعيمات</h1>
              <p className="text-sm text-gray-500">تتبع جدول تطعيماتك وتطعيمات أسرتك</p>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5">
            <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm text-center">
              <p className="text-2xl font-bold text-green-600">{takenCount}</p>
              <p className="text-xs text-gray-500 mt-0.5">تطعيم مُكتمل</p>
            </div>
            <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm text-center">
              <p className="text-2xl font-bold text-amber-500">{upcoming.length}</p>
              <p className="text-xs text-gray-500 mt-0.5">قادم خلال 30 يوم</p>
            </div>
            <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm text-center">
              <p className="text-2xl font-bold text-red-500">{overdue.length}</p>
              <p className="text-xs text-gray-500 mt-0.5">متأخر</p>
            </div>
            <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm text-center">
              <p className="text-2xl font-bold text-blue-600">{familyMembers.length}</p>
              <p className="text-xs text-gray-500 mt-0.5">أفراد الأسرة</p>
            </div>
          </div>
        </div>

        {/* Alerts */}
        {overdue.length > 0 && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5 shrink-0" />
            <div>
              <p className="font-semibold text-red-700">لديك {overdue.length} تطعيم متأخر</p>
              <ul className="mt-1 space-y-0.5">
                {overdue.slice(0, 3).map(v => (
                  <li key={v.id} className="text-sm text-red-600">• {v.vaccine_name} — كان موعده {v.next_due_date}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
        {upcoming.length > 0 && (
          <div className="mb-4 bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
            <Bell className="w-5 h-5 text-amber-500 mt-0.5 shrink-0" />
            <div>
              <p className="font-semibold text-amber-700">{upcoming.length} تطعيم قادم خلال 30 يوماً</p>
              <ul className="mt-1 space-y-0.5">
                {upcoming.slice(0, 3).map(v => (
                  <li key={v.id} className="text-sm text-amber-700">• {v.vaccine_name} — {v.next_due_date}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="flex border-b border-gray-100">
            {[
              { id: 'my', label: 'تطعيماتي', icon: User },
              { id: 'schedule', label: 'الجدول الموصى به', icon: Calendar },
              { id: 'family', label: 'الأسرة', icon: Users },
            ].map(({ id, label, icon: Icon }) => (
              <button key={id} onClick={() => setTab(id)}
                className={`flex-1 flex items-center justify-center gap-2 py-3.5 text-sm font-medium transition-colors border-b-2 ${tab === id ? 'border-blue-500 text-blue-600 bg-blue-50/50' : 'border-transparent text-gray-500 hover:text-gray-700'}`}>
                <Icon className="w-4 h-4" />{label}
              </button>
            ))}
          </div>

          <div className="p-5">
            {loading ? (
              <div className="text-center py-10 text-gray-400">
                <div className="animate-spin w-8 h-8 border-2 border-blue-400 border-t-transparent rounded-full mx-auto mb-2" />
                جاري التحميل...
              </div>
            ) : (
              <>
                {/* --- تبويب تطعيماتي --- */}
                {tab === 'my' && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-gray-900">سجل تطعيماتي</h3>
                      <Button size="sm" onClick={() => { setAddPrefill({}); setShowAdd(true) }} className="bg-blue-600 hover:bg-blue-700">
                        <Plus className="w-4 h-4 ml-1" /> إضافة تطعيم
                      </Button>
                    </div>

                    {vaccinations.length === 0 ? (
                      <div className="text-center py-10 text-gray-400">
                        <Syringe className="w-12 h-12 mx-auto mb-2 opacity-30" />
                        <p>لا يوجد سجل تطعيمات بعد</p>
                        <Button size="sm" variant="outline" className="mt-3" onClick={() => { setAddPrefill({}); setShowAdd(true) }}>
                          أضف أول تطعيم
                        </Button>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        {vaccinations.map(v => (
                          <div key={v.id} className="bg-white border border-gray-100 rounded-xl px-4 py-3 shadow-sm flex items-center justify-between">
                            <div>
                              <p className="font-medium text-gray-900">{v.vaccine_name}</p>
                              {v.disease_prevented && <p className="text-xs text-gray-500">يقي من: {v.disease_prevented}</p>}
                              <div className="flex flex-wrap gap-2 mt-1 text-xs text-gray-400">
                                {v.date_given && <span>تاريخ: {v.date_given}</span>}
                                {v.provider && <span>الجهة: {v.provider}</span>}
                                {v.administration_site && <span>الموقع: {v.administration_site}</span>}
                              </div>
                            </div>
                            <div className="text-right">
                              {v.next_due_date && (
                                <div className="text-xs text-amber-600 flex items-center gap-1 mb-1">
                                  <Clock className="w-3 h-3" /> التالي: {v.next_due_date}
                                </div>
                              )}
                              <Badge status="taken" />
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* --- تبويب الجدول الموصى به --- */}
                {tab === 'schedule' && (
                  <ScheduleTab
                    schedule={schedule}
                    expandSchedule={expandSchedule}
                    setExpandSchedule={setExpandSchedule}
                    setAddPrefill={setAddPrefill}
                    setShowAdd={setShowAdd}
                  />
                )}

                {/* --- تبويب الأسرة --- */}
                {tab === 'family' && (
                  familyMembers.length === 0 ? (
                    <div className="text-center py-10 text-gray-400">
                      <Users className="w-12 h-12 mx-auto mb-2 opacity-30" />
                      <p>لم تضف أفراداً للأسرة بعد</p>
                      <a href="/family-health" className="mt-2 text-blue-600 hover:underline text-sm block">إضافة أفراد الأسرة</a>
                    </div>
                  ) : (
                    <FamilyMemberVaccinations members={familyMembers} />
                  )
                )}
              </>
            )}
          </div>
        </div>
      </div>

      {showAdd && (
        <AddVaccinationModal
          onClose={() => setShowAdd(false)}
          onSave={onVacSaved}
          prefill={addPrefill}
          scheduleList={schedule}
        />
      )}
    </div>
  )
}
