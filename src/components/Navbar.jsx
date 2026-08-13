import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import NotificationBell from './NotificationBell'
import { 
  Menu, 
  X, 
  Heart, 
  User, 
  LogOut, 
  Settings,
  Stethoscope,
  Shield,
  Phone,
  Droplets,
  ClipboardList,
  Calendar,
  FileText,
  FlaskConical,
  Scan,
  Bot,
  Pill,
  Users,
  ChevronDown,
  LayoutDashboard,
  Sun,
  Moon
} from 'lucide-react'

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [shortcutsOpen, setShortcutsOpen] = useState(false)
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('sahty-theme') === 'dark')
  const { user, logout, switchRole, applyRole, isAuthenticated, isAdmin } = useAuth()
  const [roleFormOpen, setRoleFormOpen] = useState(false)
  const [roleForm, setRoleForm] = useState({ role: 'doctor', full_name: '', license_number: '', qualification: '', specialization: '' })
  const [roleMessage, setRoleMessage] = useState(null)
  const location = useLocation()

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode)
    localStorage.setItem('sahty-theme', darkMode ? 'dark' : 'light')
  }, [darkMode])

  const handleLogout = async () => {
    await logout()
    setUserMenuOpen(false)
  }

  const submitRoleApplication = async (event) => {
    event.preventDefault()
    const result = await applyRole(roleForm.role, roleForm)
    setRoleMessage({ type: result.success ? 'success' : 'error', text: result.message })
    if (result.success) setRoleFormOpen(false)
  }

  const isActive = (path) => location.pathname === path

  const navLinks = [
    { path: '/doctors', label: 'الأطباء', icon: Stethoscope },
    { path: '/hospitals', label: 'الدليل الطبي', icon: LayoutDashboard },
    { path: '/services', label: 'الخدمات', icon: Shield },
    { path: '/blood-bank', label: 'بنك الدم', icon: Droplets },
    { path: '/emergency', label: 'الطوارئ', icon: Phone }
  ]

  const userMenuItems = [
    { path: '/dashboard', label: 'لوحة التحكم', icon: LayoutDashboard },
    { path: '/medical-record', label: 'الملف الطبي', icon: ClipboardList },
    { path: '/clinical-summary', label: 'التقرير الطبي الشامل', icon: FileText },
    { path: '/appointments', label: 'المواعيد', icon: Calendar },
    { path: '/prescriptions', label: 'الوصفات الدوائية', icon: FileText },
    { path: '/lab-requests', label: 'طلبات التحاليل', icon: FlaskConical },
    { path: '/radiology', label: 'طلبات الأشعة', icon: Scan },
    { path: '/medications', label: 'متابعة الأدوية', icon: Pill },
    { path: '/family-health', label: 'صحة الأسرة', icon: Users },
    { path: '/account-settings', label: 'إعدادات الحساب', icon: Settings },
    { path: '/vaccinations', label: 'التطعيمات', icon: Shield },
    { path: '/pharmacies', label: 'الصيدليات', icon: Pill },
    { path: '/labs-directory', label: 'المعامل', icon: FlaskConical },
    { path: '/radiology-centers', label: 'مراكز الأشعة', icon: Scan },
    { path: '/nursing', label: 'خدمات التمريض', icon: Heart },
    { path: '/symptom-checker', label: 'فاحص الأعراض', icon: Stethoscope },
  ]

  const serviceShortcuts = [
    { path: '/lab-requests', label: 'التحاليل', icon: FlaskConical },
    { path: '/radiology', label: 'الأشعة', icon: Scan },
    { path: '/medication-orders', label: 'الأدوية', icon: Pill },
    { path: '/blood-bank', label: 'بنك الدم', icon: Droplets },
  ]

  return (
    <nav className="sticky top-0 z-50 shadow-sm bg-white dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">

          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 flex-shrink-0">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, #0f2444 0%, #2563eb 100%)' }}>
              <Heart className="h-5 w-5 text-white" />
            </div>
            <span className="text-lg font-bold" style={{ color: '#0f2444' }}>صحتي</span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                    isActive(link.path)
                      ? 'text-white'
                      : 'text-gray-600 hover:text-blue-700 hover:bg-blue-50'
                  }`}
                  style={isActive(link.path) ? { background: 'linear-gradient(135deg, #0f2444 0%, #2563eb 100%)' } : {}}
                >
                  <Icon className="h-4 w-4" />
                  <span>{link.label}</span>
                </Link>
              )
            })}
            <div className="relative">
              <button
                onClick={() => setShortcutsOpen(value => !value)}
                className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-medium text-gray-600 dark:text-gray-200 hover:text-blue-700 hover:bg-blue-50 dark:hover:bg-slate-800"
                aria-expanded={shortcutsOpen}
              >
                <ClipboardList className="h-4 w-4" /> الخدمات الطبية
                <ChevronDown className="h-3.5 w-3.5" />
              </button>
              {shortcutsOpen && (
                <div className="absolute left-0 top-11 w-48 rounded-xl border border-gray-100 dark:border-slate-700 bg-white dark:bg-slate-900 p-1 shadow-xl">
                  {serviceShortcuts.map(({ path, label, icon: Icon }) => (
                    <Link key={path} to={path} onClick={() => setShortcutsOpen(false)}
                      className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-gray-700 dark:text-gray-100 hover:bg-blue-50 dark:hover:bg-slate-800">
                      <Icon className="h-4 w-4 text-blue-600" /> {label}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Desktop User */}
          <div className="hidden md:flex items-center gap-2">
            <button type="button" onClick={() => setDarkMode(value => !value)}
              aria-label={darkMode ? 'تفعيل الوضع الفاتح' : 'تفعيل الوضع الداكن'}
              title={darkMode ? 'الوضع الفاتح' : 'الوضع الداكن'}
              className="rounded-xl p-2 text-gray-600 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-slate-800">
              {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
            {/* Notification Bell — shows only when logged in */}
            <NotificationBell />

            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 border border-gray-200 transition-all"
                >
                  <div className="w-7 h-7 rounded-lg flex items-center justify-center text-white text-xs font-bold"
                    style={{ background: 'linear-gradient(135deg, #0f2444 0%, #2563eb 100%)' }}>
                    {(user?.profile?.first_name || user?.email || 'U').charAt(0).toUpperCase()}
                  </div>
                  <span className="max-w-[120px] truncate">
                    {user?.profile?.first_name || user?.email?.split('@')[0] || 'المستخدم'}
                  </span>
                  <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} />
                </button>

                {userMenuOpen && (
                  <>
                    <div className="fixed inset-0 z-10" onClick={() => setUserMenuOpen(false)} />
                    <div className="absolute left-0 rtl:right-0 rtl:left-auto mt-2 w-56 bg-white rounded-2xl shadow-xl py-2 z-20 border border-gray-100">
                      <div className="px-4 py-3 border-b border-gray-100">
                        <p className="text-sm font-semibold text-gray-900 truncate">
                          {user?.profile?.first_name} {user?.profile?.last_name}
                        </p>
                        <p className="text-xs text-gray-400 truncate">{user?.email}</p>
                      </div>
                      <div className="max-h-[calc(100vh-9rem)] overflow-y-auto py-1">
                        {user?.active_roles?.length > 1 && (
                          <div className="border-b border-gray-100 px-4 py-2">
                            <p className="mb-2 text-xs font-semibold text-gray-400">تبديل الدور</p>
                            <div className="flex flex-wrap gap-1">
                              {user.active_roles.map(role => (
                                <button
                                  key={role}
                                  onClick={async () => { await switchRole(role); setUserMenuOpen(false) }}
                                  className={`rounded-lg px-2 py-1 text-xs ${user.user_type === role ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-blue-50'}`}
                                >
                                  {{ patient: 'مستخدم', doctor: 'طبيب', nurse: 'ممرض', pharmacy: 'صيدلية', lab: 'معمل', radiology_center: 'أشعة', hospital: 'مستشفى' }[role] || role}
                                </button>
                              ))}
                            </div>
                          </div>
                        )}
                        {user?.user_type === 'patient' && (
                          <button
                            onClick={() => { setRoleFormOpen(true); setUserMenuOpen(false); setRoleMessage(null) }}
                            className="mx-3 mb-2 w-[calc(100%-1.5rem)] rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-right text-xs font-semibold text-blue-700 hover:bg-blue-100"
                          >
                            تقديم كطبيب أو تمريض
                          </button>
                        )}
                        {userMenuItems.map(item => {
                          const Icon = item.icon
                          return (
                            <Link
                              key={item.path}
                              to={item.path}
                              className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                              onClick={() => setUserMenuOpen(false)}
                            >
                              <Icon className="h-4 w-4 text-gray-400" />
                              {item.label}
                            </Link>
                          )
                        })}
                        {isAdmin && (
                          <Link
                            to="/admin"
                            className="flex items-center gap-3 px-4 py-2.5 text-sm text-indigo-700 hover:bg-indigo-50 transition-colors"
                            onClick={() => setUserMenuOpen(false)}
                          >
                            <Settings className="h-4 w-4" />
                            لوحة الإدارة
                          </Link>
                        )}
                        <Link
                          to="/ai-assistant"
                          className="flex items-center gap-3 px-4 py-2.5 text-sm font-medium hover:bg-blue-50 transition-colors"
                          style={{ color: '#2563eb' }}
                          onClick={() => setUserMenuOpen(false)}
                        >
                          <Bot className="h-4 w-4" />
                          المساعد الذكي
                        </Link>
                      </div>
                      <div className="border-t border-gray-100 pt-1">
                        <button
                          onClick={handleLogout}
                          className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors"
                        >
                          <LogOut className="h-4 w-4" />
                          تسجيل الخروج
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link to="/login">
                  <button className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-blue-700 hover:bg-blue-50 rounded-xl transition-all">
                    تسجيل الدخول
                  </button>
                </Link>
                <Link to="/register">
                  <button className="px-5 py-2 text-sm font-semibold text-white rounded-xl transition-all hover:opacity-90 shadow-sm"
                    style={{ background: 'linear-gradient(135deg, #0f2444 0%, #2563eb 100%)' }}>
                    إنشاء حساب
                  </button>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile toggle */}
          <button
            className="md:hidden p-2 rounded-xl text-gray-600 hover:bg-gray-100 transition-colors"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden bg-white border-t border-gray-100 px-4 pt-3 pb-4 space-y-1">
          {navLinks.map((link) => {
            const Icon = link.icon
            return (
              <Link
                key={link.path}
                to={link.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  isActive(link.path)
                    ? 'text-white'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
                style={isActive(link.path) ? { background: 'linear-gradient(135deg, #0f2444 0%, #2563eb 100%)' } : {}}
                onClick={() => setIsOpen(false)}
              >
                <Icon className="h-5 w-5" />
                <span>{link.label}</span>
              </Link>
            )
          })}
          <div className="border-t border-gray-100 pt-3 mt-2">
            {isAuthenticated ? (
              <div className="space-y-1">
                <div className="px-4 py-2 flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-sm font-bold"
                    style={{ background: 'linear-gradient(135deg, #0f2444 0%, #2563eb 100%)' }}>
                    {(user?.profile?.first_name || 'U').charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-900">
                      {user?.profile?.first_name} {user?.profile?.last_name}
                    </p>
                    <p className="text-xs text-gray-400">{user?.email}</p>
                  </div>
                </div>
                {userMenuItems.slice(0, 4).map(item => {
                  const Icon = item.icon
                  return (
                    <Link key={item.path} to={item.path}
                      className="flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm text-gray-700 hover:bg-gray-50"
                      onClick={() => setIsOpen(false)}>
                      <Icon className="h-4 w-4 text-gray-400" />
                      {item.label}
                    </Link>
                  )
                })}
                <button
                  onClick={() => { handleLogout(); setIsOpen(false) }}
                  className="flex items-center gap-3 w-full px-4 py-2.5 rounded-xl text-sm text-red-600 hover:bg-red-50"
                >
                  <LogOut className="h-4 w-4" />
                  تسجيل الخروج
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <Link to="/login" onClick={() => setIsOpen(false)}
                  className="block px-4 py-3 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 text-center border border-gray-200">
                  تسجيل الدخول
                </Link>
                <Link to="/register" onClick={() => setIsOpen(false)}
                  className="block px-4 py-3 rounded-xl text-sm font-semibold text-white text-center"
                  style={{ background: 'linear-gradient(135deg, #0f2444 0%, #2563eb 100%)' }}>
                  إنشاء حساب جديد
                </Link>
              </div>
            )}
          </div>
        </div>
      )}

      {roleFormOpen && (
        <div className="fixed inset-0 z-[70] flex items-center justify-center bg-slate-950/40 p-4" dir="rtl">
          <form onSubmit={submitRoleApplication} className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl">
            <div className="mb-5 flex items-start justify-between gap-4">
              <div>
                <h2 className="text-lg font-bold text-gray-900">التقديم لدور مهني</h2>
                <p className="mt-1 text-xs text-gray-500">سيظل حساب المريض متاحاً حتى اعتماد الطلب.</p>
              </div>
              <button type="button" onClick={() => setRoleFormOpen(false)} className="text-gray-400 hover:text-gray-700"><X className="h-5 w-5" /></button>
            </div>
            {roleMessage && <div className={`mb-4 rounded-lg p-3 text-sm ${roleMessage.type === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'}`}>{roleMessage.text}</div>}
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="text-sm text-gray-700 sm:col-span-2">الدور المطلوب
                <select value={roleForm.role} onChange={e => setRoleForm(f => ({ ...f, role: e.target.value }))} className="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2">
                  <option value="doctor">طبيب</option>
                  <option value="nurse">تمريض</option>
                </select>
              </label>
              <label className="text-sm text-gray-700 sm:col-span-2">الاسم المهني
                <input required value={roleForm.full_name} onChange={e => setRoleForm(f => ({ ...f, full_name: e.target.value }))} className="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2" />
              </label>
              <label className="text-sm text-gray-700">رقم الترخيص
                <input required value={roleForm.license_number} onChange={e => setRoleForm(f => ({ ...f, license_number: e.target.value }))} className="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2" />
              </label>
              <label className="text-sm text-gray-700">المؤهل
                <input required value={roleForm.qualification} onChange={e => setRoleForm(f => ({ ...f, qualification: e.target.value }))} className="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2" />
              </label>
              {roleForm.role === 'doctor' && <label className="text-sm text-gray-700 sm:col-span-2">التخصص
                <input value={roleForm.specialization} onChange={e => setRoleForm(f => ({ ...f, specialization: e.target.value }))} className="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2" />
              </label>}
            </div>
            <div className="mt-6 flex justify-end gap-2">
              <button type="button" onClick={() => setRoleFormOpen(false)} className="rounded-lg px-4 py-2 text-sm text-gray-600 hover:bg-gray-50">إلغاء</button>
              <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">إرسال الطلب</button>
            </div>
          </form>
        </div>
      )}
    </nav>
  )
}
