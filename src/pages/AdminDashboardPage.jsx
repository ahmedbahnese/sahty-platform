import { useEffect, useMemo, useState, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Navigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import {
  Activity, AlertCircle, BarChart3, Building2, CheckCircle2,
  ChevronRight, Clock3, FileText, FlaskConical, Heart,
  Hospital, Loader2, LogOut, Radio, RefreshCw, Search,
  ShieldCheck, Stethoscope, Pill, Users, XCircle, Eye,
  TrendingUp, UserCheck, UserX, AlertTriangle, Filter,
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, Legend,
} from 'recharts'

// ─── constants ────────────────────────────────────────────────────────────────
const PROVIDER_META = {
  doctor:          { label: 'الأطباء',          icon: Stethoscope, color: 'blue'   },
  hospital:        { label: 'المستشفيات',        icon: Hospital,    color: 'indigo' },
  pharmacy:        { label: 'الصيدليات',         icon: Pill,        color: 'emerald'},
  lab:             { label: 'المعامل',           icon: FlaskConical,color: 'amber'  },
  radiology_center:{ label: 'مراكز الأشعة',     icon: Radio,       color: 'purple' },
}

const STATUS_LABELS = { pending: 'قيد المراجعة', approved: 'معتمد', rejected: 'مرفوض', more_information: 'استكمال معلومات' }
const STATUS_COLORS = { pending: 'amber', approved: 'emerald', rejected: 'red', more_information: 'blue' }

const PIE_COLORS = ['#3B82F6','#6366F1','#10B981','#F59E0B','#8B5CF6','#EF4444']

const NAV = [
  { id: 'overview',   label: 'الرئيسية',        icon: BarChart3    },
  { id: 'approvals',  label: 'اعتماد الجهات',   icon: CheckCircle2 },
  { id: 'users',      label: 'المستخدمون',      icon: Users        },
  { id: 'audit',      label: 'سجل النشاط',      icon: FileText     },
]

// ─── helpers ──────────────────────────────────────────────────────────────────
function Badge({ status }) {
  const color = STATUS_COLORS[status] || 'gray'
  const cls = {
    amber:   'bg-amber-50 text-amber-700 border-amber-200',
    emerald: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    red:     'bg-red-50 text-red-700 border-red-200',
    blue:    'bg-blue-50 text-blue-700 border-blue-200',
    gray:    'bg-gray-50 text-gray-700 border-gray-200',
  }
  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${cls[color]}`}>
      {STATUS_LABELS[status] || status}
    </span>
  )
}

function StatCard({ label, value, icon: Icon, tone = 'blue', sub }) {
  const tones = {
    blue:   'bg-blue-50 text-blue-600',
    green:  'bg-emerald-50 text-emerald-600',
    amber:  'bg-amber-50 text-amber-600',
    purple: 'bg-purple-50 text-purple-600',
    red:    'bg-red-50 text-red-600',
    indigo: 'bg-indigo-50 text-indigo-600',
  }
  return (
    <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
      <div className="flex items-start gap-4">
        <div className={`rounded-xl p-3 ${tones[tone]}`}><Icon className="h-6 w-6" /></div>
        <div className="flex-1 min-w-0">
          <p className="text-sm text-gray-500 truncate">{label}</p>
          <p className="mt-1 text-2xl font-bold text-gray-900">{value ?? '—'}</p>
          {sub && <p className="mt-0.5 text-xs text-gray-400">{sub}</p>}
        </div>
      </div>
    </div>
  )
}

function Alert({ message, type = 'info', onClose }) {
  if (!message) return null
  const styles = {
    info:    'bg-blue-50 border-blue-200 text-blue-800',
    success: 'bg-emerald-50 border-emerald-200 text-emerald-800',
    error:   'bg-red-50 border-red-200 text-red-800',
  }
  return (
    <div className={`flex items-center justify-between rounded-xl border p-4 ${styles[type]}`}>
      <span className="text-sm font-medium">{message}</span>
      {onClose && <button onClick={onClose} className="ml-3 text-current opacity-60 hover:opacity-100">✕</button>}
    </div>
  )
}

// ─── Overview Section ─────────────────────────────────────────────────────────
function OverviewSection({ stats, loading }) {
  if (loading) return <Skeleton />

  const roleData = Object.entries(stats?.users_by_role || {}).map(([k, v]) => ({
    name: { patient:'مريض', doctor:'طبيب', pharmacy:'صيدلية', lab:'معمل',
            radiology_center:'أشعة', hospital:'مستشفى', admin:'مدير', super_admin:'مدير عام' }[k] || k,
    value: v,
  })).filter(d => d.value > 0)

  const providerData = Object.entries(stats?.providers || {}).map(([k, v]) => ({
    name: PROVIDER_META[k]?.label || k,
    pending: v.pending,
    approved: v.approved,
    rejected: v.rejected,
  }))

  return (
    <div className="space-y-6">
      {/* KPI cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="إجمالي المستخدمين"        value={stats?.total_users}        icon={Users}         tone="blue"   />
        <StatCard label="الحسابات النشطة"          value={stats?.active_users}       icon={UserCheck}     tone="green"  />
        <StatCard label="طلبات بانتظار الاعتماد"   value={stats?.pending_approvals}  icon={Clock3}        tone="amber"  />
        <StatCard label="إجمالي الجهات المعتمدة"
          value={Object.values(stats?.providers || {}).reduce((s,p)=>s+p.approved,0)}
          icon={ShieldCheck} tone="purple" />
      </div>

      {/* Provider breakdown cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {Object.entries(PROVIDER_META).map(([key, meta]) => {
          const p = stats?.providers?.[key] || {}
          const Icon = meta.icon
          return (
            <div key={key} className="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
              <div className="flex items-center gap-2 mb-3">
                <div className={`rounded-lg p-2 bg-${meta.color}-50`}>
                  <Icon className={`h-4 w-4 text-${meta.color}-600`} />
                </div>
                <span className="text-sm font-semibold text-gray-700">{meta.label}</span>
              </div>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between"><span className="text-gray-500">معتمد</span><span className="font-bold text-emerald-600">{p.approved ?? 0}</span></div>
                <div className="flex justify-between"><span className="text-gray-500">بانتظار</span><span className="font-bold text-amber-600">{p.pending ?? 0}</span></div>
                <div className="flex justify-between"><span className="text-gray-500">مرفوض</span><span className="font-bold text-red-500">{p.rejected ?? 0}</span></div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
          <h3 className="mb-4 text-base font-bold text-gray-900">توزيع المستخدمين حسب الدور</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={roleData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({name,value})=>`${name}: ${value}`}>
                {roleData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
          <h3 className="mb-4 text-base font-bold text-gray-900">حالة طلبات الجهات الطبية</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={providerData} margin={{top:0,right:0,left:-20,bottom:0}}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" tick={{fontSize:11}} />
              <YAxis tick={{fontSize:11}} allowDecimals={false} />
              <Tooltip />
              <Legend wrapperStyle={{fontSize:12}} />
              <Bar dataKey="approved" name="معتمد"   fill="#10B981" radius={[4,4,0,0]} />
              <Bar dataKey="pending"  name="بانتظار" fill="#F59E0B" radius={[4,4,0,0]} />
              <Bar dataKey="rejected" name="مرفوض"  fill="#EF4444" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}

// ─── Approvals Section ────────────────────────────────────────────────────────
function ApprovalsSection({ headers, onMessage }) {
  const [typeFilter, setTypeFilter]     = useState('all')
  const [statusFilter, setStatusFilter] = useState('pending')
  const [providers, setProviders]       = useState([])
  const [loading, setLoading]           = useState(true)
  const [search, setSearch]             = useState('')
  const [reviewNote, setReviewNote]     = useState({})

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams({ status: statusFilter })
      if (typeFilter !== 'all') params.set('provider_type', typeFilter)
      const res = await fetch(`/api/admin/providers?${params}`, { headers })
      if (!res.ok) throw new Error()
      setProviders(await res.json())
    } catch { onMessage('تعذر تحميل الطلبات', 'error') }
    finally { setLoading(false) }
  }, [typeFilter, statusFilter, headers])

  useEffect(() => { load() }, [load])

  const review = async (id, status) => {
    const res = await fetch(`/api/admin/providers/${id}/review`, {
      method: 'PATCH',
      headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, review_note: reviewNote[id] || '' }),
    })
    const data = await res.json()
    if (!res.ok) { onMessage(data.message || 'تعذر تحديث الطلب', 'error'); return }
    onMessage(status === 'approved' ? '✅ تم اعتماد الجهة وتفعيل حسابها' : '❌ تم رفض الطلب', status === 'approved' ? 'success' : 'info')
    load()
  }

  const filtered = providers.filter(p =>
    !search || p.legal_name?.includes(search) || p.license_number?.includes(search) || p.city?.includes(search)
  )

  return (
    <div className="space-y-5">
      {/* Filters */}
      <div className="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
        <div className="flex flex-wrap gap-3">
          {/* Type tabs */}
          <div className="flex flex-wrap gap-1">
            <button
              onClick={() => setTypeFilter('all')}
              className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${typeFilter==='all' ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
            >الكل</button>
            {Object.entries(PROVIDER_META).map(([key, meta]) => (
              <button
                key={key}
                onClick={() => setTypeFilter(key)}
                className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${typeFilter===key ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
              >
                <meta.icon className="h-3.5 w-3.5" />{meta.label}
              </button>
            ))}
          </div>

          <div className="flex-1" />

          {/* Status */}
          <div className="flex gap-1 rounded-lg border border-gray-200 p-1">
            {['pending','approved','rejected','more_information'].map(s => (
              <button key={s}
                onClick={() => setStatusFilter(s)}
                className={`rounded-md px-3 py-1 text-sm font-medium transition-colors ${statusFilter===s ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
              >{STATUS_LABELS[s]}</button>
            ))}
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input
              value={search} onChange={e => setSearch(e.target.value)}
              placeholder="بحث بالاسم أو الترخيص..."
              className="rounded-lg border border-gray-200 py-1.5 pr-9 pl-3 text-sm outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 w-52"
            />
          </div>
        </div>
      </div>

      {/* List */}
      <div className="space-y-3">
        {loading && <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-blue-600" /></div>}
        {!loading && filtered.length === 0 && (
          <div className="rounded-2xl border border-dashed border-gray-200 bg-white p-12 text-center text-gray-400">
            <CheckCircle2 className="mx-auto h-10 w-10 mb-3 opacity-30" />
            <p className="font-medium">لا توجد طلبات في هذه القائمة</p>
          </div>
        )}
        {!loading && filtered.map(provider => {
          const meta = PROVIDER_META[provider.provider_type] || {}
          const Icon = meta.icon || Building2
          return (
            <div key={provider.id} className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
              <div className="flex flex-col gap-4 md:flex-row md:items-start">
                {/* Info */}
                <div className="flex flex-1 items-start gap-4">
                  <div className={`rounded-xl p-3 bg-${meta.color || 'blue'}-50 shrink-0`}>
                    <Icon className={`h-6 w-6 text-${meta.color || 'blue'}-600`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-base font-bold text-gray-900">{provider.legal_name}</h3>
                      <Badge status={provider.status} />
                      <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">{meta.label}</span>
                    </div>
                    <div className="mt-1.5 flex flex-wrap gap-x-4 gap-y-1 text-sm text-gray-500">
                      <span>📋 {provider.license_number}</span>
                      <span>📍 {provider.city}</span>
                      <span>✉️ {provider.user?.email}</span>
                      {provider.phone && <span>📞 {provider.phone}</span>}
                    </div>
                    {provider.review_note && (
                      <p className="mt-2 text-xs text-gray-400 bg-gray-50 rounded-lg px-3 py-2">
                        <span className="font-medium">ملاحظة الاعتماد:</span> {provider.review_note}
                      </p>
                    )}
                    {provider.reviewed_at && (
                      <p className="mt-1 text-xs text-gray-400">
                        تمت المراجعة: {new Date(provider.reviewed_at).toLocaleDateString('ar-EG')}
                      </p>
                    )}
                  </div>
                </div>

                {/* Actions */}
                {statusFilter === 'pending' && (
                  <div className="flex flex-col gap-2 shrink-0 md:w-64">
                    <textarea
                      rows={2}
                      placeholder="ملاحظة للجهة (اختياري)..."
                      value={reviewNote[provider.id] || ''}
                      onChange={e => setReviewNote(prev => ({...prev, [provider.id]: e.target.value}))}
                      className="w-full rounded-lg border border-gray-200 p-2 text-sm resize-none outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
                    />
                    <div className="flex gap-2">
                      <Button className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white" size="sm" onClick={() => review(provider.id, 'approved')}>
                        <CheckCircle2 className="ml-1 h-4 w-4" /> اعتماد
                      </Button>
                      <Button className="flex-1" variant="outline" size="sm" onClick={() => review(provider.id, 'rejected')}>
                        <XCircle className="ml-1 h-4 w-4 text-red-500" /> رفض
                      </Button>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => review(provider.id, 'more_information')}>
                      طلب استكمال المعلومات
                    </Button>
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ─── Users Section ────────────────────────────────────────────────────────────
function UsersSection({ headers, onMessage }) {
  const [users, setUsers]     = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch]   = useState('')
  const [roleFilter, setRole] = useState('all')

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/admin/users', { headers })
      if (!res.ok) throw new Error()
      setUsers(await res.json())
    } catch { onMessage('تعذر تحميل المستخدمين', 'error') }
    finally { setLoading(false) }
  }, [headers])

  useEffect(() => { load() }, [load])

  const toggle = async (user) => {
    const res = await fetch(`/api/admin/users/${user.id}/status`, {
      method: 'PATCH',
      headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_active: !user.is_active }),
    })
    if (res.ok) {
      onMessage(user.is_active ? 'تم تعطيل الحساب' : 'تم تفعيل الحساب', 'success')
      load()
    } else {
      const d = await res.json()
      onMessage(d.message || 'تعذر تحديث الحساب', 'error')
    }
  }

  const ROLE_LABELS_MAP = {
    patient:'مريض', doctor:'طبيب', pharmacy:'صيدلية', lab:'معمل',
    radiology_center:'مركز أشعة', hospital:'مستشفى', admin:'مدير', super_admin:'مدير عام',
  }

  const filtered = users.filter(u => {
    const matchRole = roleFilter === 'all' || u.user_type === roleFilter
    const matchSearch = !search || u.email?.includes(search) || u.username?.includes(search)
    return matchRole && matchSearch
  })

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
        <div className="flex flex-wrap gap-3">
          <div className="flex flex-wrap gap-1">
            {['all','patient','doctor','pharmacy','lab','radiology_center','hospital','admin','super_admin'].map(r => (
              <button key={r}
                onClick={() => setRole(r)}
                className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${roleFilter===r ? 'bg-gray-900 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
              >{r === 'all' ? 'الكل' : ROLE_LABELS_MAP[r]}</button>
            ))}
          </div>
          <div className="flex-1" />
          <div className="relative">
            <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input value={search} onChange={e => setSearch(e.target.value)}
              placeholder="بحث بالبريد أو الاسم..."
              className="rounded-lg border border-gray-200 py-1.5 pr-9 pl-3 text-sm outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 w-52"
            />
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-2xl border border-gray-100 bg-white shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-blue-600" /></div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-right">
              <thead className="border-b border-gray-100 bg-gray-50">
                <tr>
                  <th className="px-5 py-3 font-semibold text-gray-600">المستخدم</th>
                  <th className="px-5 py-3 font-semibold text-gray-600">الدور</th>
                  <th className="px-5 py-3 font-semibold text-gray-600">الحالة</th>
                  <th className="px-5 py-3 font-semibold text-gray-600">آخر دخول</th>
                  <th className="px-5 py-3 font-semibold text-gray-600">إجراء</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {filtered.length === 0 && (
                  <tr><td colSpan={5} className="py-12 text-center text-gray-400">لا توجد نتائج</td></tr>
                )}
                {filtered.map(u => (
                  <tr key={u.id} className="hover:bg-gray-50/50 transition-colors">
                    <td className="px-5 py-3">
                      <div className="font-semibold text-gray-900">{u.username || '—'}</div>
                      <div className="text-xs text-gray-500">{u.email}</div>
                    </td>
                    <td className="px-5 py-3">
                      <span className="rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700">
                        {ROLE_LABELS_MAP[u.user_type] || u.user_type}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      <span className={`inline-flex items-center gap-1 text-xs font-semibold ${u.is_active ? 'text-emerald-600' : 'text-red-500'}`}>
                        {u.is_active ? <><UserCheck className="h-3.5 w-3.5" />نشط</> : <><UserX className="h-3.5 w-3.5" />معطل</>}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-xs text-gray-500">
                      {u.last_login ? new Date(u.last_login).toLocaleDateString('ar-EG') : '—'}
                    </td>
                    <td className="px-5 py-3">
                      <Button
                        size="sm" variant="outline"
                        disabled={u.user_type === 'super_admin'}
                        onClick={() => toggle(u)}
                        className={u.is_active ? 'text-red-600 hover:bg-red-50 border-red-200' : 'text-emerald-600 hover:bg-emerald-50 border-emerald-200'}
                      >
                        {u.is_active ? 'تعطيل' : 'تفعيل'}
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <div className="border-t border-gray-100 px-5 py-3 text-xs text-gray-400">
          {filtered.length} مستخدم من أصل {users.length}
        </div>
      </div>
    </div>
  )
}

// ─── Audit Log Section ────────────────────────────────────────────────────────
function AuditSection({ headers }) {
  const [logs, setLogs]       = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch('/api/admin/audit-logs', { headers })
        if (!res.ok) return
        setLogs(await res.json())
      } catch { /* silent */ }
      finally { setLoading(false) }
    }
    load()
  }, [headers])

  const ACTION_ICON = {
    provider_approved: '✅',
    provider_rejected: '❌',
    user_status_changed: '👤',
    user_registration: '📋',
    user_logout: '🚪',
  }

  return (
    <div className="rounded-2xl border border-gray-100 bg-white shadow-sm overflow-hidden">
      <div className="border-b border-gray-100 px-6 py-4">
        <h2 className="text-base font-bold text-gray-900">سجل نشاط الإدارة</h2>
        <p className="text-sm text-gray-500">جميع الإجراءات الإدارية مسجلة ومؤرشفة</p>
      </div>
      {loading ? (
        <div className="flex justify-center py-16"><Loader2 className="h-8 w-8 animate-spin text-blue-600" /></div>
      ) : logs.length === 0 ? (
        <div className="py-16 text-center text-gray-400">
          <FileText className="mx-auto h-10 w-10 mb-3 opacity-30" />
          <p>لا يوجد سجل نشاط بعد</p>
        </div>
      ) : (
        <div className="divide-y divide-gray-50">
          {logs.map(log => (
            <div key={log.id} className="flex items-start gap-4 px-6 py-4 hover:bg-gray-50/50">
              <span className="text-xl shrink-0 mt-0.5">{ACTION_ICON[log.action] || '📌'}</span>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">{log.description}</p>
                <p className="mt-0.5 text-xs text-gray-500">{log.user_email} · {log.action}</p>
              </div>
              <time className="text-xs text-gray-400 shrink-0">
                {log.created_at ? new Date(log.created_at).toLocaleString('ar-EG') : '—'}
              </time>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function Skeleton() {
  return (
    <div className="space-y-4 animate-pulse">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_,i)=><div key={i} className="h-24 rounded-2xl bg-gray-100" />)}
      </div>
      <div className="h-64 rounded-2xl bg-gray-100" />
    </div>
  )
}

// ─── Main Component ───────────────────────────────────────────────────────────
export default function AdminDashboardPage() {
  const { user, token, isAdmin, logout } = useAuth()
  const [section, setSection]   = useState('overview')
  const [stats, setStats]       = useState(null)
  const [statsLoading, setStatsLoading] = useState(true)
  const [alert, setAlert]       = useState(null)

  const headers = useMemo(() => ({ Authorization: `Bearer ${token}` }), [token])

  const loadStats = useCallback(async () => {
    setStatsLoading(true)
    try {
      const res = await fetch('/api/admin/stats', { headers })
      if (res.ok) setStats(await res.json())
    } catch { /* silent */ }
    finally { setStatsLoading(false) }
  }, [headers])

  useEffect(() => { loadStats() }, [loadStats])

  const showAlert = (message, type = 'info') => {
    setAlert({ message, type })
    setTimeout(() => setAlert(null), 5000)
  }

  if (!isAdmin) return <Navigate to="/dashboard" replace />

  const adminName = user?.profile?.first_name
    ? `${user.profile.first_name} ${user.profile.last_name || ''}`.trim()
    : user?.email

  return (
    <div className="min-h-screen bg-gray-50 flex" dir="rtl">
      {/* ── Sidebar ── */}
      <aside className="hidden md:flex w-64 flex-col shrink-0 border-l border-gray-200 bg-white">
        {/* Logo */}
        <div className="flex items-center gap-3 border-b border-gray-100 px-5 py-5">
          <div className="rounded-xl bg-blue-600 p-2">
            <ShieldCheck className="h-5 w-5 text-white" />
          </div>
          <div>
            <p className="text-sm font-bold text-gray-900">لوحة الإدارة</p>
            <p className="text-xs text-gray-500">صحتك في أمان</p>
          </div>
        </div>

        {/* Admin info */}
        <div className="border-b border-gray-100 px-5 py-4">
          <p className="text-xs text-gray-400 mb-1">مرحباً،</p>
          <p className="text-sm font-semibold text-gray-900 truncate">{adminName}</p>
          <span className="mt-1 inline-block rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700">
            {user?.user_type === 'super_admin' ? 'مدير عام' : 'مدير'}
          </span>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV.map(item => (
            <button key={item.id}
              onClick={() => setSection(item.id)}
              className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors text-right
                ${section === item.id
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-gray-600 hover:bg-gray-100'}`}
            >
              <item.icon className="h-4 w-4 shrink-0" />
              {item.label}
              {item.id === 'approvals' && stats?.pending_approvals > 0 && (
                <span className={`mr-auto rounded-full px-1.5 py-0.5 text-xs font-bold ${section===item.id ? 'bg-white text-blue-700' : 'bg-amber-100 text-amber-700'}`}>
                  {stats.pending_approvals}
                </span>
              )}
            </button>
          ))}
        </nav>

        {/* Bottom actions */}
        <div className="border-t border-gray-100 p-3 space-y-1">
          <button onClick={loadStats} className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-gray-500 hover:bg-gray-100 transition-colors">
            <RefreshCw className="h-4 w-4" /> تحديث البيانات
          </button>
          <button onClick={logout} className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-red-500 hover:bg-red-50 transition-colors">
            <LogOut className="h-4 w-4" /> تسجيل الخروج
          </button>
        </div>
      </aside>

      {/* ── Mobile nav bar ── */}
      <div className="md:hidden fixed bottom-0 inset-x-0 z-50 border-t border-gray-200 bg-white flex justify-around px-2 py-2">
        {NAV.map(item => (
          <button key={item.id} onClick={() => setSection(item.id)}
            className={`flex flex-col items-center gap-1 rounded-xl px-3 py-1.5 text-xs font-medium transition-colors
              ${section === item.id ? 'text-blue-600' : 'text-gray-500'}`}
          >
            <item.icon className="h-5 w-5" />
            {item.label}
          </button>
        ))}
      </div>

      {/* ── Main content ── */}
      <main className="flex-1 min-w-0 overflow-auto pb-20 md:pb-0">
        {/* Header */}
        <div className="sticky top-0 z-10 border-b border-gray-200 bg-white/90 backdrop-blur px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                {NAV.find(n => n.id === section)?.label}
              </h1>
              <p className="text-sm text-gray-500">
                {section === 'overview'  && 'نظرة عامة على حالة المنصة'}
                {section === 'approvals' && 'مراجعة واعتماد الجهات الطبية'}
                {section === 'users'     && 'إدارة حسابات المستخدمين'}
                {section === 'audit'     && 'سجل الإجراءات الإدارية'}
              </p>
            </div>
            {section === 'overview' && (
              <Button size="sm" variant="outline" onClick={loadStats} className="hidden md:flex gap-2">
                <RefreshCw className="h-4 w-4" /> تحديث
              </Button>
            )}
          </div>
        </div>

        <div className="p-6 space-y-5">
          {/* Alert */}
          {alert && <Alert message={alert.message} type={alert.type} onClose={() => setAlert(null)} />}

          {/* Content */}
          {section === 'overview'  && <OverviewSection  stats={stats} loading={statsLoading} />}
          {section === 'approvals' && <ApprovalsSection headers={headers} onMessage={showAlert} />}
          {section === 'users'     && <UsersSection     headers={headers} onMessage={showAlert} />}
          {section === 'audit'     && <AuditSection     headers={headers} />}
        </div>
      </main>
    </div>
  )
}
