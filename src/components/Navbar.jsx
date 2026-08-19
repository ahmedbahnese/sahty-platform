import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useNotifications } from '../contexts/NotificationContext'
import NotificationBell from './NotificationBell'
import RoleSidebar from './RoleSidebar'
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
  Bell,
  Pill,
  Users,
  ChevronDown,
  LayoutDashboard,
  Building2,
  Sun,
  Moon
} from 'lucide-react'

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [shortcutsOpen, setShortcutsOpen] = useState(false)
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('sahty-theme') === 'dark')
  const { user, logout, switchRole, applyRole, isAuthenticated, isAdmin, roleLabel } = useAuth()
  const notifications = useNotifications()
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
    notifications.success('تم إنهاء الجلسة وحذف بيانات الدخول من هذا الجهاز.', 'تم تسجيل الخروج')
    setUserMenuOpen(false)
  }

  const submitRoleApplication = async (event) => {
    event.preventDefault()
    const result = await applyRole(roleForm.role, roleForm)
    setRoleMessage({ type: result.success ? 'success' : 'error', text: result.message })
    if (result.success) {
      notifications.success(result.message || 'تم إرسال الطلب للمراجعة.', 'تم إرسال الطلب')
    } else {
      notifications.error(result.message || 'تعذر إرسال الطلب. راجع البيانات وحاول مرة أخرى.', 'لم يتم إرسال الطلب')
    }
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

  const roleTopLinks = {
    patient: [
      { path: '/dashboard', label: 'لوحتي', icon: LayoutDashboard },
      { path: '/appointments', label: 'المواعيد', icon: Calendar },
      { path: '/medical-record', label: 'الملف الطبي', icon: FileText },
    ],
    doctor: [
      { path: '/dashboard', label: 'لوحتي', icon: LayoutDashboard },
      { path: '/appointments', label: 'مواعيد المرضى', icon: Calendar },
      { path: '/prescriptions', label: 'الوصفات', icon: ClipboardList },
    ],
    nurse: [
      { path: '/dashboard', label: 'لوحتي', icon: LayoutDashboard },
      { path: '/appointments', label: 'المواعيد', icon: Calendar },
      { path: '/nursing', label: 'خدمات التمريض', icon: Heart },
    ],
    pharmacy: [
      { path: '/dashboard', label: 'لوحتي', icon: LayoutDashboard },
      { path: '/prescriptions', label: 'الوصفات', icon: ClipboardList },
      { path: '/medications', label: 'الأدوية', icon: Pill },
    ],
    lab: [
      { path: '/dashboard', label: 'لوحتي', icon: LayoutDashboard },
      { path: '/appointments', label: 'المواعيد', icon: Calendar },
      { path: '/lab-requests', label: 'التحاليل', icon: FlaskConical },
    ],
    radiology_center: [
      { path: '/dashboard', label: 'لوحتي', icon: LayoutDashboard },
      { path: '/appointments', label: 'المواعيد', icon: Calendar },
      { path: '/radiology', label: 'الأشعة', icon: Scan },
    ],
    hospital: [
      { path: '/dashboard', label: 'لوحتي', icon: LayoutDashboard },
      { path: '/appointments', label: 'المواعيد', icon: Calendar },
      { path: '/lab-requests', label: 'التحاليل', icon: FlaskConical },
    ],
    admin: [
      { path: '/admin', label: 'لوحة الإدارة', icon: LayoutDashboard },
      { path: '/directory', label: 'الجهات الطبية', icon: Building2 },
      { path: '/account-settings', label: 'الإعدادات', icon: Settings },
    ],
    super_admin: [
      { path: '/admin', label: 'لوحة الإدارة', icon: LayoutDashboard },
      { path: '/directory', label: 'الجهات الطبية', icon: Building2 },
      { path: '/account-settings', label: 'الإعدادات', icon: Settings },
    ],
  }

  const topLinks = isAuthenticated ? (roleTopLinks[user?.user_type] || roleTopLinks.patient) : navLinks

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

          {/* Shared desktop top navigation. Authenticated users receive role-aware links. */}
          <div className="hidden min-w-0 flex-1 justify-center gap-1 lg:flex">
            {topLinks.map((link) => {
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
          <div className="hidden lg:flex items-center gap-2">
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
                        <p className="mt-1 text-xs font-semibold text-blue-600">{roleLabel}</p>
                      </div>
                      <div className="max-h-[calc(100vh-9rem)] overflow-y-auto py-1">
                         {user?.active_roles?.length > 1 && (
                          <div className="border-b border-gray-100 px-4 py-2">
                            <p className="mb-2 text-xs font-semibold text-gray-400">تبديل الدور</p>
                            <div className="flex flex-wrap gap-1">
                              {user.active_roles.map(role => (
                                <button
                                  key={role}
                                  onClick={async () => {
                                    const result = await switchRole(role)
                                    if (result.success) {
                                      notifications.success('تم تبديل الدور وتحديث الصلاحيات.', 'تم تبديل الدور')
                                      setUserMenuOpen(false)
                                    } else {
                                      notifications.error(result.message || 'تعذر تبديل الدور.', 'لم يتم تبديل الدور')
                                    }
                                  }}
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
                         {[
                           { path: '/account-settings', label: 'الملف الشخصي', icon: User },
                           { path: '/account-settings#settings', label: 'الإعدادات', icon: Settings },
                           { path: '/account-settings#password', label: 'تغيير كلمة المرور', icon: Settings },
                           { path: '/dashboard', label: 'الإشعارات', icon: Bell },
                           { path: '/services', label: 'المساعدة', icon: Bot },
                         ].map(item => {
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
            type="button"
            className="lg:hidden p-2 rounded-xl text-gray-600 hover:bg-gray-100 transition-colors"
            onClick={() => setIsOpen(!isOpen)}
            aria-label={isOpen ? 'إغلاق القائمة' : 'فتح القائمة'}
            aria-expanded={isOpen}
          >
            {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

       {isAuthenticated && <RoleSidebar open={isOpen} onClose={() => setIsOpen(false)} />}

       {/* Public mobile navigation remains available when no account is active. */}
       {!isAuthenticated && isOpen && (
         <div className="border-t border-gray-100 bg-white px-4 pb-4 pt-3 lg:hidden">
           <div className="space-y-1">
             {navLinks.map(link => {
               const Icon = link.icon
               return (
                 <Link
                   key={link.path}
                   to={link.path}
                   onClick={() => setIsOpen(false)}
                   className={`flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-semibold ${
                     isActive(link.path) ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-slate-50'
                   }`}
                 >
                   <Icon className="h-5 w-5" />
                   {link.label}
                 </Link>
               )
             })}
           </div>
           <div className="mt-3 grid gap-2 border-t border-gray-100 pt-3">
             <Link to="/login" onClick={() => setIsOpen(false)} className="rounded-xl border border-slate-200 px-4 py-3 text-center text-sm font-semibold text-slate-700">
               تسجيل الدخول
             </Link>
             <Link to="/register" onClick={() => setIsOpen(false)} className="rounded-xl bg-blue-700 px-4 py-3 text-center text-sm font-semibold text-white">
               إنشاء حساب جديد
             </Link>
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
