import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Users, Plus, Heart, User, Calendar, Activity, Brain,
  ChevronDown, ChevronUp, X, Check, Target, FileText, Pencil, Trash2, Printer
} from 'lucide-react'

const API = (path) => `/api/family${path}`
const authHeader = () => ({ 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` })

export default function FamilyHealthPage() {
  const [groups, setGroups] = useState([])
  const [activeGroup, setActiveGroup] = useState(null)
  const [members, setMembers] = useState([])
  const [goals, setGoals] = useState([])
  const [activeMember, setActiveMember] = useState(null)
  const [memberRecords, setMemberRecords] = useState([])
  const [aiAnalysis, setAiAnalysis] = useState(null)
  const [aiLoading, setAiLoading] = useState(false)
  const [loading, setLoading] = useState(true)
  const [msg, setMsg] = useState(null)
  const [view, setView] = useState('groups')  // groups | members | member-detail | goals

  // Forms
  const [showGroupForm, setShowGroupForm] = useState(false)
  const [showMemberForm, setShowMemberForm] = useState(false)
  const [showRecordForm, setShowRecordForm] = useState(false)
  const [showGoalForm, setShowGoalForm] = useState(false)
  const [editingMemberId, setEditingMemberId] = useState(null)
  const [editingRecordId, setEditingRecordId] = useState(null)
  const [memberReport, setMemberReport] = useState(null)

  const [groupForm, setGroupForm] = useState({ name: '', description: '' })
  const [memberForm, setMemberForm] = useState({
    first_name: '', last_name: '', relationship: '', date_of_birth: '',
    gender: '', blood_type: '', phone: '', chronic_diseases: [], allergies: [], current_medications: [], notes: ''
  })
  const [recordForm, setRecordForm] = useState({
    record_type: 'checkup', title: '', description: '', date: '', next_due_date: '', doctor_name: '', hospital_name: ''
  })
  const [goalForm, setGoalForm] = useState({ title: '', description: '', target_date: '', member_id: '' })

  useEffect(() => { fetchGroups() }, [])

  const fetchGroups = async () => {
    setLoading(true)
    try {
      const res = await fetch(API('/groups'), { headers: authHeader() })
      const data = await res.json()
      if (data.success) setGroups(data.groups)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const loadGroup = async (group) => {
    setActiveGroup(group)
    try {
      const res = await fetch(API(`/groups/${group.id}`), { headers: authHeader() })
      const data = await res.json()
      if (data.success) {
        setMembers(data.members)
        setGoals(data.goals)
      }
    } catch (e) { console.error(e) }
    setView('members')
  }

  const loadMember = async (member) => {
    setActiveMember(member)
    try {
      const res = await fetch(API(`/members/${member.id}`), { headers: authHeader() })
      const data = await res.json()
      if (data.success) setMemberRecords(data.records)
    } catch (e) { console.error(e) }
    setView('member-detail')
  }

  const createGroup = async (e) => {
    e.preventDefault()
    try {
      const res = await fetch(API('/groups'), {
        method: 'POST', headers: authHeader(), body: JSON.stringify(groupForm)
      })
      const data = await res.json()
      if (data.success) {
        setMsg({ type: 'success', text: 'تم إنشاء مجموعة الأسرة' })
        setShowGroupForm(false)
        setGroupForm({ name: '', description: '' })
        fetchGroups()
      }
    } catch { setMsg({ type: 'error', text: 'خطأ في الإنشاء' }) }
  }

  const addMember = async (e) => {
    e.preventDefault()
    try {
      const res = await fetch(API(editingMemberId ? `/members/${editingMemberId}` : `/groups/${activeGroup.id}/members`), {
        method: editingMemberId ? 'PUT' : 'POST', headers: authHeader(), body: JSON.stringify(memberForm)
      })
      const data = await res.json()
      if (data.success) {
        setMsg({ type: 'success', text: editingMemberId ? 'تم تعديل بيانات الفرد' : 'تم إضافة الفرد' })
        setShowMemberForm(false)
        setEditingMemberId(null)
        loadGroup(activeGroup)
        // Auto-add to emergency contacts if they have a phone number
        if (memberForm.phone) {
          try {
            await fetch('/api/emergency/family-contacts', {
              method: 'POST',
              headers: authHeader(),
              body: JSON.stringify({
                name: `${memberForm.first_name} ${memberForm.last_name}`.trim(),
                phone: memberForm.phone,
                relationship: memberForm.relationship || 'آخر',
                is_primary: false,
              }),
            })
          } catch { /* ignore — emergency contact is bonus, not critical */ }
        }
      }
    } catch { setMsg({ type: 'error', text: 'خطأ في الإضافة' }) }
  }

  const editMember = (member) => {
    setEditingMemberId(member.id)
    setMemberForm({
      first_name: member.first_name || '', last_name: member.last_name || '',
      relationship: member.relationship || '', date_of_birth: member.date_of_birth || '',
      gender: member.gender || '', blood_type: member.blood_type || '', phone: member.phone || '',
      chronic_diseases: member.chronic_diseases || [], allergies: member.allergies || [],
      current_medications: member.current_medications || [], notes: member.notes || ''
    })
    setShowMemberForm(true)
  }

  const deleteMember = async (member) => {
    if (!window.confirm(`حذف ${member.full_name} من الأسرة؟`)) return
    const res = await fetch(API(`/members/${member.id}`), { method: 'DELETE', headers: authHeader() })
    const data = await res.json()
    if (data.success) { setMsg({ type: 'success', text: 'تم حذف الفرد' }); loadGroup(activeGroup) }
    else setMsg({ type: 'error', text: data.error || 'تعذر حذف الفرد' })
  }

  const addRecord = async (e) => {
    e.preventDefault()
    try {
      const path = editingRecordId ? `/members/${activeMember.id}/records/${editingRecordId}` : `/members/${activeMember.id}/records`
      const res = await fetch(API(path), {
        method: editingRecordId ? 'PUT' : 'POST', headers: authHeader(), body: JSON.stringify(recordForm)
      })
      const data = await res.json()
      if (data.success) {
        setMsg({ type: 'success', text: editingRecordId ? 'تم تعديل السجل الصحي' : 'تم إضافة السجل الصحي' })
        setShowRecordForm(false)
        setEditingRecordId(null)
        loadMember(activeMember)
      }
    } catch { setMsg({ type: 'error', text: 'خطأ في الإضافة' }) }
  }

  const editRecord = (record) => {
    setEditingRecordId(record.id)
    setRecordForm({
      record_type: record.record_type || 'checkup', title: record.title || '',
      description: record.description || '', date: record.date || '',
      next_due_date: record.next_due_date || '', doctor_name: record.doctor_name || '',
      hospital_name: record.hospital_name || ''
    })
    setShowRecordForm(true)
  }

  const deleteRecord = async (record) => {
    if (!window.confirm('حذف هذا السجل الصحي؟')) return
    const res = await fetch(API(`/members/${activeMember.id}/records/${record.id}`), { method: 'DELETE', headers: authHeader() })
    const data = await res.json()
    if (data.success) { setMsg({ type: 'success', text: 'تم حذف السجل' }); loadMember(activeMember) }
    else setMsg({ type: 'error', text: data.error || 'تعذر حذف السجل' })
  }

  const loadMemberReport = async () => {
    const res = await fetch(API(`/members/${activeMember.id}/report`), { headers: authHeader() })
    const data = await res.json()
    if (data.success) setMemberReport(data)
    else setMsg({ type: 'error', text: data.error || 'تعذر إنشاء التقرير' })
  }

  const addGoal = async (e) => {
    e.preventDefault()
    try {
      const res = await fetch(API(`/groups/${activeGroup.id}/goals`), {
        method: 'POST', headers: authHeader(), body: JSON.stringify(goalForm)
      })
      const data = await res.json()
      if (data.success) {
        setMsg({ type: 'success', text: 'تم إضافة الهدف الصحي' })
        setShowGoalForm(false)
        loadGroup(activeGroup)
      }
    } catch { setMsg({ type: 'error', text: 'خطأ في الإضافة' }) }
  }

  const updateGoalProgress = async (goalId, progress, status) => {
    try {
      const res = await fetch(API(`/goals/${goalId}/progress`), {
        method: 'PUT', headers: authHeader(), body: JSON.stringify({ progress, status })
      })
      const data = await res.json()
      if (data.success) loadGroup(activeGroup)
    } catch (e) { console.error(e) }
  }

  const runAIAnalysis = async () => {
    setAiLoading(true)
    setAiAnalysis(null)
    try {
      const res = await fetch(API(`/groups/${activeGroup.id}/ai-analysis`), { headers: authHeader() })
      const data = await res.json()
      if (data.success) setAiAnalysis(data.analysis)
      else setMsg({ type: 'error', text: data.error || 'خطأ في التحليل' })
    } catch { setMsg({ type: 'error', text: 'خطأ في التحليل' }) }
    setAiLoading(false)
  }

  const relationships = ['أب', 'أم', 'أخ', 'أخت', 'ابن', 'بنت', 'زوج', 'زوجة', 'جد', 'جدة', 'عم', 'خال', 'آخر']
  const recordTypes = [
    { value: 'checkup', label: 'فحص دوري' },
    { value: 'vaccination', label: 'تطعيم' },
    { value: 'test', label: 'تحليل / فحص' },
    { value: 'medication', label: 'دواء' },
    { value: 'note', label: 'ملاحظة' },
  ]

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50 py-8" dir="rtl">
      <div className="max-w-5xl mx-auto px-4">

        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            {view !== 'groups' && (
              <button onClick={() => {
                if (view === 'member-detail') setView('members')
                else setView('groups')
              }} className="text-gray-400 hover:text-gray-600 text-2xl">←</button>
            )}
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
                <Users className="text-green-600" size={32} />
                {view === 'groups' && 'إدارة صحة الأسرة'}
                {view === 'members' && activeGroup?.name}
                {view === 'member-detail' && activeMember ? `${activeMember.first_name} ${activeMember.last_name}` : ''}
                {view === 'goals' && 'الأهداف الصحية'}
              </h1>
              <p className="text-gray-500 text-sm mt-1">تتبع وإدارة الصحة لجميع أفراد الأسرة</p>
            </div>
          </div>
          {view === 'groups' && (
            <Button onClick={() => setShowGroupForm(!showGroupForm)} className="bg-green-600 hover:bg-green-700">
              <Plus size={18} className="ml-1" /> أسرة جديدة
            </Button>
          )}
          {view === 'members' && (
            <div className="flex gap-2">
              <Button onClick={() => setView('goals')} variant="outline" className="text-purple-600 border-purple-300">
                <Target size={16} className="ml-1" /> الأهداف
              </Button>
              <Button onClick={runAIAnalysis} disabled={aiLoading} variant="outline" className="text-blue-600 border-blue-300">
                {aiLoading ? '⏳' : '🤖'} تحليل ذكي
              </Button>
              <Button onClick={() => { setEditingMemberId(null); setShowMemberForm(!showMemberForm) }} className="bg-green-600 hover:bg-green-700">
                <Plus size={18} className="ml-1" /> إضافة فرد
              </Button>
            </div>
          )}
          {view === 'member-detail' && (
            <div className="flex gap-2">
              <Button onClick={loadMemberReport} variant="outline" className="text-blue-600 border-blue-300">
                <FileText size={16} className="ml-1" /> التقرير الشامل
              </Button>
              <Button onClick={() => { setEditingRecordId(null); setShowRecordForm(!showRecordForm) }} className="bg-blue-600 hover:bg-blue-700">
                <Plus size={18} className="ml-1" /> إضافة سجل
              </Button>
            </div>
          )}
          {view === 'goals' && (
            <Button onClick={() => setShowGoalForm(!showGoalForm)} className="bg-purple-600 hover:bg-purple-700">
              <Plus size={18} className="ml-1" /> هدف جديد
            </Button>
          )}
        </div>

        {msg && (
          <Alert className={`mb-4 ${msg.type === 'success' ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'}`}>
            <AlertDescription>{msg.text}</AlertDescription>
          </Alert>
        )}

        {/* AI Analysis */}
        {aiAnalysis && view === 'members' && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-5 mb-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-blue-800 flex items-center gap-2">
                <Brain size={20} /> تحليل الذكاء الاصطناعي لصحة الأسرة
              </h3>
              <button onClick={() => setAiAnalysis(null)} className="text-gray-400 hover:text-gray-600"><X size={16} /></button>
            </div>
            <div className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">{aiAnalysis}</div>
          </div>
        )}

        {/* ── Groups View ── */}
        {view === 'groups' && (
          <>
            {showGroupForm && (
              <div className="bg-white rounded-xl shadow-sm border p-5 mb-6">
                <h3 className="font-bold text-gray-800 mb-4">إنشاء مجموعة أسرة جديدة</h3>
                <form onSubmit={createGroup} className="space-y-3">
                  <div>
                    <Label>اسم الأسرة *</Label>
                    <Input value={groupForm.name} onChange={e => setGroupForm(p => ({ ...p, name: e.target.value }))}
                      placeholder="مثال: عائلة محمد" required />
                  </div>
                  <div>
                    <Label>وصف</Label>
                    <Input value={groupForm.description} onChange={e => setGroupForm(p => ({ ...p, description: e.target.value }))}
                      placeholder="وصف اختياري" />
                  </div>
                  <div className="flex gap-2">
                    <Button type="submit" className="bg-green-600 hover:bg-green-700">إنشاء</Button>
                    <Button type="button" variant="outline" onClick={() => setShowGroupForm(false)}>إلغاء</Button>
                  </div>
                </form>
              </div>
            )}
            {groups.length === 0 ? (
              <div className="bg-white rounded-xl p-12 text-center text-gray-400">
                <Users size={56} className="mx-auto mb-4 opacity-25" />
                <p className="text-lg font-medium">لا توجد مجموعات أسرة بعد</p>
                <p className="text-sm mt-2">أنشئ مجموعتك الأسرية لتتبع صحة جميع أفراد الأسرة</p>
                <Button onClick={() => setShowGroupForm(true)} className="mt-4 bg-green-600 hover:bg-green-700">
                  إنشاء أول مجموعة
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {groups.map(g => (
                  <div key={g.id} onClick={() => loadGroup(g)}
                    className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 cursor-pointer hover:border-green-300 hover:shadow-md transition-all">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                        <Users size={24} className="text-green-600" />
                      </div>
                      <div>
                        <h3 className="font-bold text-gray-800">{g.name}</h3>
                        {g.description && <p className="text-sm text-gray-500">{g.description}</p>}
                      </div>
                    </div>
                    <div className="flex items-center justify-between text-sm text-gray-400">
                      <span><User size={14} className="inline ml-1" />{g.members_count} فرد</span>
                      <span className="text-green-500">اضغط للعرض ←</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {/* ── Members View ── */}
        {view === 'members' && (
          <>
            {showMemberForm && (
              <div className="bg-white rounded-xl shadow-sm border p-5 mb-6">
                <h3 className="font-bold text-gray-800 mb-4">{editingMemberId ? 'تعديل بيانات الفرد' : 'إضافة فرد جديد'}</h3>
                <form onSubmit={addMember} className="space-y-3">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                      <Label>الاسم الأول *</Label>
                      <Input value={memberForm.first_name} onChange={e => setMemberForm(p => ({ ...p, first_name: e.target.value }))} required />
                    </div>
                    <div>
                      <Label>الاسم الأخير *</Label>
                      <Input value={memberForm.last_name} onChange={e => setMemberForm(p => ({ ...p, last_name: e.target.value }))} required />
                    </div>
                    <div>
                      <Label>صلة القرابة *</Label>
                      <select value={memberForm.relationship} onChange={e => setMemberForm(p => ({ ...p, relationship: e.target.value }))}
                        className="w-full border rounded-md px-3 py-2 text-sm" required>
                        <option value="">اختر الصلة</option>
                        {relationships.map(r => <option key={r} value={r}>{r}</option>)}
                      </select>
                    </div>
                    <div>
                      <Label>تاريخ الميلاد</Label>
                      <Input type="date" value={memberForm.date_of_birth}
                        onChange={e => setMemberForm(p => ({ ...p, date_of_birth: e.target.value }))} />
                    </div>
                    <div>
                      <Label>الجنس</Label>
                      <select value={memberForm.gender} onChange={e => setMemberForm(p => ({ ...p, gender: e.target.value }))}
                        className="w-full border rounded-md px-3 py-2 text-sm">
                        <option value="">اختر</option>
                        <option value="male">ذكر</option>
                        <option value="female">أنثى</option>
                      </select>
                    </div>
                    <div>
                      <Label>فصيلة الدم</Label>
                      <select value={memberForm.blood_type} onChange={e => setMemberForm(p => ({ ...p, blood_type: e.target.value }))}
                        className="w-full border rounded-md px-3 py-2 text-sm">
                        <option value="">غير محدد</option>
                        {['A+','A-','B+','B-','AB+','AB-','O+','O-'].map(bt => <option key={bt} value={bt}>{bt}</option>)}
                      </select>
                    </div>
                    <div>
                      <Label>رقم الهاتف</Label>
                      <Input value={memberForm.phone} onChange={e => setMemberForm(p => ({ ...p, phone: e.target.value }))} />
                    </div>
                  </div>
                  <div>
                    <Label>ملاحظات صحية</Label>
                    <Input value={memberForm.notes} onChange={e => setMemberForm(p => ({ ...p, notes: e.target.value }))}
                      placeholder="أمراض مزمنة، حساسية، ملاحظات..." />
                  </div>
                  <div className="flex gap-2">
                    <Button type="submit" className="bg-green-600 hover:bg-green-700">{editingMemberId ? 'حفظ التعديل' : 'إضافة'}</Button>
                    <Button type="button" variant="outline" onClick={() => { setShowMemberForm(false); setEditingMemberId(null) }}>إلغاء</Button>
                  </div>
                </form>
              </div>
            )}
            {members.length === 0 ? (
              <div className="bg-white rounded-xl p-10 text-center text-gray-400">
                <User size={48} className="mx-auto mb-3 opacity-25" />
                <p>لا يوجد أفراد في هذه المجموعة</p>
                <Button onClick={() => setShowMemberForm(true)} className="mt-3 bg-green-600 hover:bg-green-700">
                  إضافة أول فرد
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {members.map(m => (
                    <div key={m.id} onClick={() => loadMember(m)}
                    className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 cursor-pointer hover:border-blue-300 hover:shadow-md transition-all">
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <div className="flex items-center gap-3">
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${m.gender === 'female' ? 'bg-pink-100' : 'bg-blue-100'}`}>
                          <User size={24} className={m.gender === 'female' ? 'text-pink-600' : 'text-blue-600'} />
                        </div>
                        <div>
                          <h3 className="font-bold text-gray-800">{m.full_name}</h3>
                          <p className="text-sm text-gray-500">{m.relationship}{m.age ? ` — ${m.age} سنة` : ''}</p>
                        </div>
                      </div>
                      <div className="flex gap-1">
                        <button onClick={e => { e.stopPropagation(); editMember(m) }} className="rounded-lg p-2 text-gray-400 hover:bg-blue-50 hover:text-blue-600" title="تعديل"><Pencil size={16} /></button>
                        <button onClick={e => { e.stopPropagation(); deleteMember(m) }} className="rounded-lg p-2 text-gray-400 hover:bg-red-50 hover:text-red-600" title="حذف"><Trash2 size={16} /></button>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2 text-xs">
                      {m.blood_type && <span className="bg-red-100 text-red-600 px-2 py-1 rounded-full">{m.blood_type}</span>}
                      {m.chronic_diseases?.length > 0 && (
                        <span className="bg-orange-100 text-orange-600 px-2 py-1 rounded-full">
                          {m.chronic_diseases.length} أمراض مزمنة
                        </span>
                      )}
                      {m.current_medications?.length > 0 && (
                        <span className="bg-purple-100 text-purple-600 px-2 py-1 rounded-full">
                          {m.current_medications.length} دواء
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {/* ── Member Detail View ── */}
        {view === 'member-detail' && activeMember && (
          <>
            <div className="bg-white rounded-xl shadow-sm border p-5 mb-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div><span className="text-gray-400 block">العمر</span><span className="font-medium">{activeMember.age ? `${activeMember.age} سنة` : '—'}</span></div>
                <div><span className="text-gray-400 block">الجنس</span><span className="font-medium">{activeMember.gender === 'male' ? 'ذكر' : activeMember.gender === 'female' ? 'أنثى' : '—'}</span></div>
                <div><span className="text-gray-400 block">فصيلة الدم</span><span className="font-medium text-red-600">{activeMember.blood_type || '—'}</span></div>
                <div><span className="text-gray-400 block">الهاتف</span><span className="font-medium">{activeMember.phone || '—'}</span></div>
              </div>
              {activeMember.notes && <p className="mt-3 text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">📋 {activeMember.notes}</p>}
            </div>

            {showRecordForm && (
              <div className="bg-white rounded-xl shadow-sm border p-5 mb-6">
                <h3 className="font-bold text-gray-800 mb-4">{editingRecordId ? 'تعديل السجل الصحي' : 'إضافة سجل صحي'}</h3>
                <form onSubmit={addRecord} className="space-y-3">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                      <Label>نوع السجل *</Label>
                      <select value={recordForm.record_type} onChange={e => setRecordForm(p => ({ ...p, record_type: e.target.value }))}
                        className="w-full border rounded-md px-3 py-2 text-sm">
                        {recordTypes.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
                      </select>
                    </div>
                    <div>
                      <Label>العنوان *</Label>
                      <Input value={recordForm.title} onChange={e => setRecordForm(p => ({ ...p, title: e.target.value }))} required />
                    </div>
                    <div>
                      <Label>التاريخ *</Label>
                      <Input type="date" value={recordForm.date} onChange={e => setRecordForm(p => ({ ...p, date: e.target.value }))} required />
                    </div>
                    <div>
                      <Label>موعد المتابعة</Label>
                      <Input type="date" value={recordForm.next_due_date} onChange={e => setRecordForm(p => ({ ...p, next_due_date: e.target.value }))} />
                    </div>
                    <div>
                      <Label>اسم الطبيب</Label>
                      <Input value={recordForm.doctor_name} onChange={e => setRecordForm(p => ({ ...p, doctor_name: e.target.value }))} />
                    </div>
                    <div>
                      <Label>المستشفى / العيادة</Label>
                      <Input value={recordForm.hospital_name} onChange={e => setRecordForm(p => ({ ...p, hospital_name: e.target.value }))} />
                    </div>
                  </div>
                  <div>
                    <Label>الوصف / النتيجة</Label>
                    <Input value={recordForm.description} onChange={e => setRecordForm(p => ({ ...p, description: e.target.value }))} />
                  </div>
                  <div className="flex gap-2">
                    <Button type="submit" className="bg-blue-600 hover:bg-blue-700">حفظ</Button>
                    <Button type="button" variant="outline" onClick={() => { setShowRecordForm(false); setEditingRecordId(null) }}>إلغاء</Button>
                  </div>
                </form>
              </div>
            )}

            <h3 className="font-bold text-gray-700 mb-3 flex items-center gap-2">
              <FileText size={18} /> السجلات الصحية ({memberRecords.length})
            </h3>
            {memberRecords.length === 0 ? (
              <div className="bg-white rounded-xl p-8 text-center text-gray-400">
                <FileText size={40} className="mx-auto mb-3 opacity-25" />
                <p>لا توجد سجلات صحية</p>
              </div>
            ) : (
              <div className="space-y-3">
                {memberRecords.map(r => (
                  <div key={r.id} className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-xs bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full mr-2">
                          {recordTypes.find(t => t.value === r.record_type)?.label || r.record_type}
                        </span>
                        <span className="font-medium text-gray-800">{r.title}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-400">{r.date}</span>
                        <button onClick={() => editRecord(r)} className="rounded p-1 text-gray-400 hover:bg-blue-50 hover:text-blue-600" title="تعديل"><Pencil size={14} /></button>
                        <button onClick={() => deleteRecord(r)} className="rounded p-1 text-gray-400 hover:bg-red-50 hover:text-red-600" title="حذف"><Trash2 size={14} /></button>
                      </div>
                    </div>
                    {r.description && <p className="text-sm text-gray-600 mt-2">{r.description}</p>}
                    <div className="flex gap-4 mt-2 text-xs text-gray-400">
                      {r.doctor_name && <span>👨‍⚕️ {r.doctor_name}</span>}
                      {r.hospital_name && <span>🏥 {r.hospital_name}</span>}
                      {r.next_due_date && <span className="text-orange-500">📅 متابعة: {r.next_due_date}</span>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {/* ── Goals View ── */}
        {view === 'goals' && (
          <>
            {showGoalForm && (
              <div className="bg-white rounded-xl shadow-sm border p-5 mb-6">
                <h3 className="font-bold text-gray-800 mb-4">إضافة هدف صحي</h3>
                <form onSubmit={addGoal} className="space-y-3">
                  <div>
                    <Label>عنوان الهدف *</Label>
                    <Input value={goalForm.title} onChange={e => setGoalForm(p => ({ ...p, title: e.target.value }))}
                      placeholder="مثال: المشي 30 دقيقة يومياً" required />
                  </div>
                  <div>
                    <Label>الوصف</Label>
                    <Input value={goalForm.description} onChange={e => setGoalForm(p => ({ ...p, description: e.target.value }))} />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <Label>تاريخ الهدف</Label>
                      <Input type="date" value={goalForm.target_date} onChange={e => setGoalForm(p => ({ ...p, target_date: e.target.value }))} />
                    </div>
                    <div>
                      <Label>لفرد محدد (اختياري)</Label>
                      <select value={goalForm.member_id} onChange={e => setGoalForm(p => ({ ...p, member_id: e.target.value }))}
                        className="w-full border rounded-md px-3 py-2 text-sm">
                        <option value="">للأسرة كلها</option>
                        {members.map(m => <option key={m.id} value={m.id}>{m.full_name}</option>)}
                      </select>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button type="submit" className="bg-purple-600 hover:bg-purple-700">إضافة هدف</Button>
                    <Button type="button" variant="outline" onClick={() => setShowGoalForm(false)}>إلغاء</Button>
                  </div>
                </form>
              </div>
            )}
            {goals.length === 0 ? (
              <div className="bg-white rounded-xl p-10 text-center text-gray-400">
                <Target size={48} className="mx-auto mb-3 opacity-25" />
                <p>لا توجد أهداف صحية بعد</p>
              </div>
            ) : (
              <div className="space-y-3">
                {goals.map(g => (
                  <div key={g.id} className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h4 className="font-semibold text-gray-800">{g.title}</h4>
                        {g.description && <p className="text-sm text-gray-500">{g.description}</p>}
                      </div>
                      <span className={`text-xs px-2 py-1 rounded-full ${g.status === 'completed' ? 'bg-green-100 text-green-600' : 'bg-blue-100 text-blue-600'}`}>
                        {g.status === 'completed' ? '✓ مكتمل' : 'نشط'}
                      </span>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm text-gray-500">
                        <span>التقدم</span><span>{g.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-2">
                        <div className={`h-2 rounded-full ${g.progress >= 100 ? 'bg-green-500' : 'bg-blue-500'}`}
                          style={{ width: `${g.progress}%` }} />
                      </div>
                      {g.status !== 'completed' && (
                        <div className="flex gap-2 mt-2">
                          {[25, 50, 75, 100].map(p => (
                            <button key={p} onClick={() => updateGoalProgress(g.id, p, p === 100 ? 'completed' : 'active')}
                              className={`text-xs px-2 py-1 rounded border ${g.progress >= p ? 'bg-blue-500 text-white border-blue-500' : 'text-gray-400 border-gray-200'}`}>
                              {p}%
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                    {g.target_date && <p className="text-xs text-gray-400 mt-2">📅 الهدف بتاريخ: {g.target_date}</p>}
                  </div>
                ))}
              </div>
            )}
          </>
        )}

      </div>
      {memberReport && (
        <div className="fixed inset-0 z-[60] overflow-y-auto bg-black/50 p-4" dir="rtl">
          <div className="mx-auto my-8 max-w-2xl rounded-2xl bg-white p-6 shadow-2xl">
            <div className="mb-5 flex items-start justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold">التقرير الطبي الشامل</h2>
                <p className="text-sm text-gray-500">{memberReport.member.full_name} — {memberReport.member.relationship}</p>
              </div>
              <div className="flex gap-2">
                <button onClick={() => window.print()} className="rounded-lg border px-3 py-2 text-sm"><Printer size={15} className="ml-1 inline" /> طباعة</button>
                <button onClick={() => setMemberReport(null)}><X /></button>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3 rounded-xl bg-gray-50 p-4 text-sm md:grid-cols-4">
              <span>العمر: {memberReport.member.age || '—'}</span>
              <span>الهاتف: {memberReport.member.phone || '—'}</span>
              <span>الفصيلة: {memberReport.member.blood_type || '—'}</span>
              <span>الجنس: {memberReport.member.gender || '—'}</span>
            </div>
            <div className="mt-5 space-y-3">
              {memberReport.records.length ? memberReport.records.map(record => (
                <div key={record.id} className="rounded-xl border p-3 text-sm">
                  <div className="flex justify-between gap-3"><b>{record.title}</b><span className="text-gray-400">{record.date}</span></div>
                  {record.description && <p className="mt-1 text-gray-600">{record.description}</p>}
                  {record.next_due_date && <p className="mt-1 text-xs text-orange-600">المتابعة: {record.next_due_date}</p>}
                </div>
              )) : <p className="text-center text-gray-400">لا توجد سجلات صحية</p>}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
