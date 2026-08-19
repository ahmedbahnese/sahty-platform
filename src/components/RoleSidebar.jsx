import { useMemo, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Beaker,
  Bot,
  CalendarDays,
  ChevronLeft,
  ClipboardList,
  FileText,
  Heart,
  Home,
  LayoutDashboard,
  Pill,
  Search,
  Settings,
  ShieldCheck,
  Stethoscope,
  Users,
  X,
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

const ROLE_LABELS = {
  patient: 'حساب المريض',
  doctor: 'حساب الطبيب',
  nurse: 'حساب التمريض',
  pharmacy: 'حساب الصيدلية',
  lab: 'حساب المعمل',
  radiology_center: 'حساب مركز الأشعة',
  hospital: 'حساب المستشفى',
  admin: 'لوحة الإدارة',
  super_admin: 'لوحة مدير النظام',
}

const NAVIGATION = {
  patient: [
    ['dashboard', '/dashboard', 'لوحة التحكم', Home],
    ['doctors', '/doctors', 'الأطباء', Stethoscope],
    ['appointments', '/appointments', 'المواعيد', CalendarDays],
    ['medical-record', '/medical-record', 'الملف الطبي', ClipboardList],
    ['clinical-summary', '/clinical-summary', 'الملخص السريري', FileText],
    ['prescriptions', '/prescriptions', 'الوصفات الدوائية', Pill],
    ['medications', '/medications', 'الأدوية', Pill],
    ['lab-requests', '/lab-requests', 'نتائج التحاليل', Beaker],
    ['radiology', '/radiology', 'الأشعة', Activity],
    ['family-health', '/family-health', 'صحة الأسرة', Users],
    ['blood-bank', '/blood-bank', 'بنك الدم', Heart],
    ['emergency', '/emergency', 'الطوارئ', AlertTriangle],
    ['ai-assistant', '/ai-assistant', 'المساعد الذكي', Bot],
    ['notifications', '/dashboard', 'الإشعارات', Activity],
    ['settings', '/account-settings', 'الإعدادات', Settings],
  ],
  doctor: [
    ['dashboard', '/dashboard', 'لوحة التحكم', Home],
    ['appointments', '/appointments', 'مواعيد المرضى', CalendarDays],
    ['prescriptions', '/prescriptions', 'الوصفات الدوائية', Pill],
    ['ai-assistant', '/ai-assistant', 'المساعد الذكي', Bot],
    ['settings', '/account-settings', 'إعدادات الحساب', Settings],
  ],
  nurse: [
    ['dashboard', '/dashboard', 'لوحة التحكم', Home],
    ['appointments', '/appointments', 'المواعيد', CalendarDays],
    ['nursing', '/nursing', 'خدمات التمريض', Heart],
    ['settings', '/account-settings', 'إعدادات الحساب', Settings],
  ],
  pharmacy: [
    ['dashboard', '/dashboard', 'لوحة التحكم', Home],
    ['prescriptions', '/prescriptions', 'الوصفات الدوائية', Pill],
    ['medications', '/medications', 'متابعة الأدوية', Activity],
    ['settings', '/account-settings', 'إعدادات الحساب', Settings],
  ],
  lab: [
    ['dashboard', '/dashboard', 'لوحة التحكم', Home],
    ['appointments', '/appointments', 'المواعيد', CalendarDays],
    ['lab-requests', '/lab-requests', 'طلبات التحاليل', Beaker],
    ['settings', '/account-settings', 'إعدادات الحساب', Settings],
  ],
  radiology_center: [
    ['dashboard', '/dashboard', 'لوحة التحكم', Home],
    ['appointments', '/appointments', 'المواعيد', CalendarDays],
    ['radiology', '/radiology', 'طلبات الأشعة', Activity],
    ['settings', '/account-settings', 'إعدادات الحساب', Settings],
  ],
  hospital: [
    ['dashboard', '/dashboard', 'لوحة التحكم', Home],
    ['appointments', '/appointments', 'المواعيد', CalendarDays],
    ['lab-requests', '/lab-requests', 'طلبات التحاليل', Beaker],
    ['radiology', '/radiology', 'طلبات الأشعة', Activity],
    ['settings', '/account-settings', 'إعدادات الحساب', Settings],
  ],
  admin: [
    ['dashboard', '/admin', 'لوحة الإدارة', LayoutDashboard],
    ['users', '/admin', 'إدارة المستخدمين', Users],
    ['reports', '/admin', 'التقارير', BarChart3],
    ['settings', '/account-settings', 'إعدادات الحساب', Settings],
  ],
  super_admin: [
    ['dashboard', '/admin', 'لوحة الإدارة', LayoutDashboard],
    ['users', '/admin', 'إدارة المستخدمين', Users],
    ['reports', '/admin', 'التقارير', BarChart3],
    ['settings', '/account-settings', 'إعدادات الحساب', Settings],
  ],
}

function SidebarContent({ collapsed, onClose, mobile = false }) {
  const { user, roleLabel } = useAuth()
  const location = useLocation()
  const [query, setQuery] = useState('')
  const role = user?.user_type || 'patient'
  const links = NAVIGATION[role] || NAVIGATION.patient
  const filteredLinks = useMemo(
    () => links.filter(([, , label]) => label.includes(query.trim())),
    [links, query],
  )

  const isActive = path => location.pathname === path || (path === '/admin' && location.pathname.startsWith('/admin/'))
  const name = [user?.profile?.first_name, user?.profile?.last_name].filter(Boolean).join(' ') || user?.email?.split('@')[0] || 'المستخدم'
  const initial = name.charAt(0).toUpperCase()

  return (
    <div className="flex h-full flex-col bg-white text-slate-700" dir="rtl">
      <div className={`flex items-center border-b border-slate-100 px-4 py-4 ${collapsed ? 'justify-center' : 'justify-between'}`}>
        {!collapsed && (
          <Link to="/" onClick={onClose} className="flex items-center gap-2.5">
            <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-[#0f2444] to-[#2563eb] text-white shadow-sm">
              <Heart className="h-5 w-5 fill-current" />
            </span>
            <span>
              <span className="block text-base font-extrabold text-[#0f2444]">صحتي</span>
              <span className="block text-[10px] font-medium text-slate-400">رعايتك تبدأ هنا</span>
            </span>
          </Link>
        )}
        {mobile && (
          <button type="button" onClick={onClose} className="rounded-xl p-2 text-slate-400 hover:bg-slate-100" aria-label="إغلاق القائمة">
            <X className="h-5 w-5" />
          </button>
        )}
        {!mobile && (
          <button type="button" onClick={onClose} className="rounded-xl p-2 text-slate-400 hover:bg-slate-100" aria-label={collapsed ? 'توسيع القائمة' : 'تصغير القائمة'}>
            <ChevronLeft className={`h-4 w-4 transition-transform ${collapsed ? 'rotate-180' : ''}`} />
          </button>
        )}
      </div>

      {!collapsed && (
        <div className="px-4 pt-4">
          <label className="relative block">
            <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              value={query}
              onChange={event => setQuery(event.target.value)}
              placeholder="بحث في القائمة"
              aria-label="بحث في القائمة"
              className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2.5 pr-9 pl-3 text-sm outline-none transition focus:border-blue-400 focus:bg-white"
            />
          </label>
        </div>
      )}

      <nav className="flex-1 overflow-y-auto px-3 py-4" aria-label="التنقل الرئيسي">
        {!collapsed && <p className="mb-2 px-3 text-[11px] font-bold uppercase tracking-wider text-slate-400">{ROLE_LABELS[role] || roleLabel}</p>}
        <div className="space-y-1">
          {filteredLinks.map(([key, path, label, Icon]) => (
            <Link
              key={key}
              to={path}
              onClick={onClose}
              title={collapsed ? label : undefined}
              className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold transition ${
                isActive(path)
                  ? 'bg-blue-50 text-blue-700 shadow-sm'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-blue-700'
              } ${collapsed ? 'justify-center' : ''}`}
              aria-current={isActive(path) ? 'page' : undefined}
            >
              <Icon className={`h-[18px] w-[18px] shrink-0 ${isActive(path) ? 'text-blue-600' : 'text-slate-400'}`} />
              {!collapsed && <span>{label}</span>}
            </Link>
          ))}
          {filteredLinks.length === 0 && <p className="px-3 py-4 text-center text-xs text-slate-400">لا توجد نتائج</p>}
        </div>
      </nav>

      {!collapsed && (
        <div className="border-t border-slate-100 p-3">
          <Link to="/account-settings" onClick={onClose} className="flex items-center gap-3 rounded-xl p-2 hover:bg-slate-50">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-[#0f2444] to-[#2563eb] text-sm font-bold text-white">{initial}</span>
            <span className="min-w-0">
              <span className="block truncate text-sm font-bold text-slate-800">{name}</span>
              <span className="block truncate text-xs text-slate-400">{roleLabel}</span>
            </span>
          </Link>
        </div>
      )}
    </div>
  )
}

function MobileBottomNavigation() {
  const { user } = useAuth()
  const location = useLocation()
  const role = user?.user_type || 'patient'
  const links = (NAVIGATION[role] || NAVIGATION.patient).slice(0, 5)
  const isActive = path => location.pathname === path || (path === '/admin' && location.pathname.startsWith('/admin/'))

  return (
    <nav className="fixed inset-x-0 bottom-0 z-50 border-t border-slate-200 bg-white/95 px-2 pb-[max(0.5rem,env(safe-area-inset-bottom))] pt-2 shadow-[0_-8px_24px_rgba(15,36,68,0.08)] backdrop-blur lg:hidden" aria-label="التنقل السريع">
      <div className="mx-auto grid max-w-xl grid-cols-5 gap-1">
        {links.map(([key, path, label, Icon]) => (
          <Link
            key={key}
            to={path}
            className={`flex min-w-0 flex-col items-center gap-1 rounded-xl px-1 py-1.5 text-[10px] font-bold transition active:scale-95 ${isActive(path) ? 'bg-blue-50 text-blue-700' : 'text-slate-400 hover:bg-slate-50 hover:text-blue-600'}`}
            aria-current={isActive(path) ? 'page' : undefined}
          >
            <Icon className={`h-5 w-5 ${isActive(path) ? 'text-blue-600' : 'text-slate-400'}`} />
            <span className="max-w-full truncate">{label}</span>
          </Link>
        ))}
      </div>
    </nav>
  )
}

export default function RoleSidebar({ open, onClose }) {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <>
      <aside className={`fixed bottom-0 left-0 top-16 z-40 hidden border-r border-slate-200 shadow-sm transition-all duration-200 lg:block ${collapsed ? 'w-20' : 'w-72'}`}>
        <SidebarContent collapsed={collapsed} onClose={() => setCollapsed(value => !value)} />
      </aside>
      {open && (
        <div className="fixed inset-0 top-16 z-[60] lg:hidden">
          <button type="button" className="absolute inset-0 bg-slate-950/40" aria-label="إغلاق القائمة" onClick={onClose} />
          <aside className="relative h-full w-[min(86vw,21rem)] border-r border-slate-200 shadow-2xl">
            <SidebarContent onClose={onClose} mobile />
          </aside>
        </div>
      )}
      <MobileBottomNavigation />
    </>
  )
}
