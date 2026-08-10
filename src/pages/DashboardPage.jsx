import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '@/components/ui/button'
import {
  Activity, BarChart3, Building2, CheckCircle2, Clock3, FileText, Heart,
  Hospital, Languages, Loader2, LogOut, ShieldCheck, Stethoscope,
  TestTube2, Users, XCircle, ClipboardList, Pill, Syringe
} from 'lucide-react'

const providerLabels = {
  doctor: 'الأطباء',
  hospital: 'المستشفيات',
  pharmacy: 'الصيدليات',
  lab: 'المعامل',
  radiology_center: 'مراكز الأشعة',
}

const roleDescriptions = {
  patient: 'إدارة مواعيدك وملفك الصحي',
  doctor: 'إدارة المرضى والمواعيد والاستشارات',
  pharmacy: 'إدارة طلبات الصيدلية والخدمات',
  lab: 'إدارة الفحوصات والنتائج',
  radiology_center: 'إدارة الأشعة والتقارير',
  hospital: 'إدارة أقسام المستشفى والخدمات',
  nurse: 'إدارة طلبات الزيارات والرعاية التمريضية',
}

function StatCard({ label, value, icon: Icon, tone = 'blue' }) {
  const tones = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-emerald-50 text-emerald-600',
    amber: 'bg-amber-50 text-amber-600',
    purple: 'bg-purple-50 text-purple-600',
  }
  return (
    <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-4">
        <div className={`rounded-xl p-3 ${tones[tone]}`}><Icon className="h-6 w-6" /></div>
        <div><p className="text-sm text-gray-500">{label}</p><p className="mt-1 text-2xl font-bold text-gray-900">{value}</p></div>
      </div>
    </div>
  )
}

const PROVIDER_QUICK_LINKS = {
  doctor: [
    { label: 'المواعيد',          desc: 'استعرض وأدر مواعيد مرضاك',        icon: Clock3,       color: 'blue',   to: '/appointments' },
    { label: 'الوصفات الطبية',    desc: 'اكتب ووافق على الوصفات',           icon: ClipboardList, color: 'purple', to: '/prescriptions' },
    { label: 'طلبات التحاليل',    desc: 'راجع نتائج التحاليل',              icon: TestTube2,    color: 'green',  to: '/lab-requests' },
    { label: 'طلبات الأشعة',      desc: 'راجع طلبات الأشعة والتقارير',     icon: Languages,    color: 'amber',  to: '/radiology' },
  ],
  lab: [
    { label: 'طلبات التحاليل',    desc: 'ارفع النتائج وأدر الطلبات',        icon: TestTube2,    color: 'green',  to: '/lab-requests' },
    { label: 'المواعيد',          desc: 'جدولة المواعيد',                   icon: Clock3,       color: 'blue',   to: '/appointments' },
  ],
  radiology_center: [
    { label: 'طلبات الأشعة',      desc: 'ارفع الصور والتقارير',             icon: Languages,    color: 'amber',  to: '/radiology' },
    { label: 'المواعيد',          desc: 'جدولة المواعيد',                   icon: Clock3,       color: 'blue',   to: '/appointments' },
  ],
  pharmacy: [
    { label: 'الوصفات الطبية',    desc: 'استعرض الوصفات المرسلة إليك',      icon: ClipboardList, color: 'purple', to: '/prescriptions' },
    { label: 'متابعة الأدوية',    desc: 'سجل إخراج الأدوية',               icon: Activity,     color: 'green',  to: '/medications' },
  ],
  hospital: [
    { label: 'المواعيد',          desc: 'إدارة مواعيد المستشفى',            icon: Clock3,       color: 'blue',   to: '/appointments' },
    { label: 'التحاليل',          desc: 'إدارة طلبات التحاليل',             icon: TestTube2,    color: 'green',  to: '/lab-requests' },
    { label: 'الأشعة',            desc: 'إدارة طلبات الأشعة',              icon: Languages,    color: 'amber',  to: '/radiology' },
  ],
  nurse: [
    { label: 'طلبات التمريض', desc: 'راجع واقبل زيارات المرضى', icon: Heart, color: 'green', to: '/nursing' },
    { label: 'المواعيد', desc: 'راجع الزيارات المجدولة', icon: Clock3, color: 'blue', to: '/appointments' },
  ],
}

const LINK_COLORS = {
  blue:   'bg-blue-600',
  purple: 'bg-purple-600',
  green:  'bg-emerald-600',
  amber:  'bg-amber-500',
}

function ProviderDashboard({ user }) {
  const typeLabel = {
    doctor: 'الطبيب', pharmacy: 'الصيدلية',
    lab: 'المعمل', radiology_center: 'مركز الأشعة', hospital: 'المستشفى',
  }[user.user_type] || 'مزود الخدمة'

  const quickLinks = PROVIDER_QUICK_LINKS[user.user_type] || []

  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-gradient-to-l from-blue-700 to-indigo-600 p-7 text-white">
        <p className="text-blue-100">لوحة {typeLabel}</p>
        <h2 className="mt-2 text-2xl font-bold">{user.profile?.legal_name || user.profile?.first_name || user.email}</h2>
        <p className="mt-2 text-sm text-blue-100">استخدم الروابط أدناه لأداء عملك مباشرة.</p>
      </div>

      {quickLinks.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {quickLinks.map(l => (
            <Link key={l.to} to={l.to}
              className="group rounded-2xl border border-gray-100 bg-white p-6 shadow-sm hover:shadow-md hover:border-blue-200 transition-all">
              <div className={`w-12 h-12 rounded-xl ${LINK_COLORS[l.color]} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                <l.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-bold text-gray-900">{l.label}</h3>
              <p className="text-sm text-gray-500 mt-1">{l.desc}</p>
            </Link>
          ))}
        </div>
      )}

      <div className="grid gap-5 md:grid-cols-3">
        <StatCard label="الطلبات الجديدة" value="0" icon={Clock3} tone="amber" />
        <StatCard label="الخدمات النشطة" value="0" icon={Activity} tone="green" />
        <StatCard label="التقييم العام" value="—" icon={Heart} tone="purple" />
      </div>

      <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-bold text-gray-900">بيانات الاعتماد</h3>
        <div className="mt-4 grid gap-4 text-sm text-gray-600 md:grid-cols-2">
          <p><span className="font-semibold text-gray-900">الترخيص:</span> {user.profile?.license_number || 'غير متاح'}</p>
          <p><span className="font-semibold text-gray-900">الحالة:</span> <span className="text-emerald-600">معتمد</span></p>
          <p><span className="font-semibold text-gray-900">العنوان:</span> {user.profile?.address || 'غير متاح'}</p>
          <p><span className="font-semibold text-gray-900">المدينة:</span> {user.profile?.city || 'غير متاح'}</p>
        </div>
      </div>
    </div>
  )
}

function PatientDashboard() {
  const quickLinks = [
    { label: 'الملف الطبي الإلكتروني', desc: 'الأمراض، العمليات، التحاليل، الأشعة والمزيد', icon: ClipboardList, color: 'blue', to: '/medical-record' },
    { label: 'التقرير الطبي الشامل', desc: 'تقرير طبي شامل قابل للطباعة', icon: FileText, color: 'teal', to: '/clinical-summary' },
    { label: 'الأطباء', desc: 'ابحث عن طبيب وحجز موعد', icon: Stethoscope, color: 'purple', to: '/doctors' },
    { label: 'بنك الدم', desc: 'التبرع بالدم وطلبات الدم', icon: Heart, color: 'red', to: '/blood-bank' },
  ]
  const tones = { blue: 'bg-blue-600', teal: 'bg-teal-600', purple: 'bg-purple-600', red: 'bg-rose-600' }
  return (
    <div className="space-y-6">
      <div className="grid gap-5 md:grid-cols-3">
        <StatCard label="المواعيد القادمة" value="0" icon={Clock3} />
        <StatCard label="الأدوية النشطة" value="0" icon={Pill} tone="green" />
        <StatCard label="التطعيمات" value="0" icon={Syringe} tone="purple" />
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {quickLinks.map(l => (
          <Link key={l.to} to={l.to} className="group rounded-2xl border border-gray-100 bg-white p-6 shadow-sm hover:shadow-md hover:border-blue-200 transition-all">
            <div className={`w-12 h-12 rounded-xl ${tones[l.color]} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
              <l.icon className="w-6 h-6 text-white" />
            </div>
            <h3 className="font-bold text-gray-900">{l.label}</h3>
            <p className="text-sm text-gray-500 mt-1">{l.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}

function AdminDashboard({ token }) {
  const [stats, setStats] = useState(null)
  const [providers, setProviders] = useState([])
  const [users, setUsers] = useState([])
  const [filter, setFilter] = useState('pending')
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')

  const headers = useMemo(() => ({ Authorization: `Bearer ${token}` }), [token])
  const load = async () => {
    setLoading(true)
    try {
      const [statsResponse, providersResponse, usersResponse] = await Promise.all([
        fetch('/api/admin/stats', { headers }),
        fetch(`/api/admin/providers?status=${filter}`, { headers }),
        fetch('/api/admin/users', { headers }),
      ])
      if (!statsResponse.ok || !providersResponse.ok || !usersResponse.ok) throw new Error('تعذر تحميل بيانات الإدارة')
      setStats(await statsResponse.json())
      setProviders(await providersResponse.json())
      setUsers(await usersResponse.json())
    } catch (error) {
      setMessage(error.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [filter])

  const review = async (id, status) => {
    const response = await fetch(`/api/admin/providers/${id}/review`, {
      method: 'PATCH', headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    })
    const data = await response.json()
    if (!response.ok) { setMessage(data.message || 'تعذر تحديث الطلب'); return }
    setMessage(status === 'approved' ? 'تم اعتماد الطلب وتفعيل الحساب' : 'تم رفض الطلب وتعطيل الحساب')
    load()
  }

  const toggleUser = async (user) => {
    const response = await fetch(`/api/admin/users/${user.id}/status`, {
      method: 'PATCH', headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_active: !user.is_active }),
    })
    if (response.ok) load()
    else { const data = await response.json(); setMessage(data.message || 'تعذر تحديث المستخدم') }
  }

  return (
    <div className="space-y-6">
      {message && <div className="rounded-xl border border-blue-200 bg-blue-50 p-4 text-blue-800">{message}</div>}
      {loading && !stats ? <div className="flex items-center justify-center rounded-2xl bg-white p-16"><Loader2 className="h-8 w-8 animate-spin text-blue-600" /></div> : (
        <>
          <div className="grid gap-5 md:grid-cols-4">
            <StatCard label="إجمالي المستخدمين" value={stats?.total_users || 0} icon={Users} />
            <StatCard label="الحسابات النشطة" value={stats?.active_users || 0} icon={CheckCircle2} tone="green" />
            <StatCard label="طلبات بانتظار الاعتماد" value={stats?.pending_approvals || 0} icon={Clock3} tone="amber" />
            <StatCard label="أنواع الجهات" value="5" icon={BarChart3} tone="purple" />
          </div>

          <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div><h2 className="text-xl font-bold text-gray-900">اعتماد الجهات الطبية</h2><p className="text-sm text-gray-500">مراجعة طلبات الأطباء والمنشآت قبل تفعيل حساباتهم</p></div>
              <div className="flex flex-wrap gap-2">
                {['pending', 'approved', 'rejected'].map((status) => <Button key={status} size="sm" variant={filter === status ? 'default' : 'outline'} onClick={() => setFilter(status)}>{status === 'pending' ? 'قيد المراجعة' : status === 'approved' ? 'معتمدة' : 'مرفوضة'}</Button>)}
              </div>
            </div>
            <div className="mt-5 space-y-3">
              {providers.length === 0 && <p className="rounded-xl bg-gray-50 p-6 text-center text-gray-500">لا توجد طلبات في هذه القائمة.</p>}
              {providers.map((provider) => (
                <div key={provider.id} className="flex flex-col gap-4 rounded-xl border border-gray-100 p-4 md:flex-row md:items-center">
                  <div className="flex-1"><div className="flex items-center gap-2"><Building2 className="h-5 w-5 text-blue-600" /><h3 className="font-bold text-gray-900">{provider.legal_name}</h3><span className="rounded-full bg-blue-50 px-2 py-1 text-xs text-blue-700">{provider.provider_label}</span></div><p className="mt-1 text-sm text-gray-500">{provider.license_number} · {provider.city} · {provider.user?.email}</p></div>
                  {filter === 'pending' && <div className="flex gap-2"><Button size="sm" onClick={() => review(provider.id, 'approved')}><CheckCircle2 className="ml-1 h-4 w-4" /> اعتماد</Button><Button size="sm" variant="outline" onClick={() => review(provider.id, 'rejected')}><XCircle className="ml-1 h-4 w-4" /> رفض</Button></div>}
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
            <h2 className="text-xl font-bold text-gray-900">إدارة المستخدمين</h2>
            <div className="mt-4 overflow-x-auto"><table className="w-full text-right text-sm"><thead><tr className="border-b text-gray-500"><th className="p-3">المستخدم</th><th className="p-3">الدور</th><th className="p-3">الحالة</th><th className="p-3">إجراء</th></tr></thead><tbody>{users.map((user) => <tr key={user.id} className="border-b last:border-0"><td className="p-3"><div className="font-semibold">{user.username || '—'}</div><div className="text-gray-500">{user.email}</div></td><td className="p-3">{user.user_type}</td><td className="p-3"><span className={user.is_active ? 'text-emerald-600' : 'text-red-600'}>{user.is_active ? 'نشط' : 'غير نشط'}</span></td><td className="p-3"><Button size="sm" variant="outline" disabled={user.user_type === 'super_admin'} onClick={() => toggleUser(user)}>{user.is_active ? 'تعطيل' : 'تفعيل'}</Button></td></tr>)}</tbody></table></div>
          </div>
        </>
      )}
    </div>
  )
}

export default function DashboardPage() {
  const { user, token, isAdmin, roleLabel } = useAuth()
  const role = user?.user_type
  const name = user?.profile?.first_name || user?.profile?.legal_name || user?.email
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mb-8 flex flex-col justify-between gap-4 md:flex-row md:items-center">
          <div><p className="text-sm font-semibold text-blue-600">{roleLabel}</p><h1 className="mt-1 text-3xl font-bold text-gray-900">مرحباً، {name}</h1><p className="mt-1 text-gray-500">{roleDescriptions[role] || 'إدارة المنصة والصلاحيات'}</p></div>
          {isAdmin && <div className="flex items-center gap-2 rounded-xl bg-blue-50 px-4 py-3 text-sm text-blue-800"><ShieldCheck className="h-5 w-5" /> صلاحيات الإدارة مفعلة</div>}
        </div>
        {isAdmin ? <AdminDashboard token={token} /> : role === 'patient' ? <PatientDashboard /> : <ProviderDashboard user={user} />}
      </div>
    </div>
  )
}