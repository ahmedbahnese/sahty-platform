import { useState } from 'react'
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
  LayoutDashboard
} from 'lucide-react'

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const { user, logout, isAuthenticated, isAdmin } = useAuth()
  const location = useLocation()

  const handleLogout = async () => {
    await logout()
    setUserMenuOpen(false)
  }

  const isActive = (path) => location.pathname === path

  const navLinks = [
    { path: '/', label: 'الرئيسية', icon: Heart },
    { path: '/doctors', label: 'الأطباء', icon: Stethoscope },
    { path: '/hospitals', label: 'المستشفيات', icon: LayoutDashboard },
    { path: '/services', label: 'الخدمات', icon: Shield },
    { path: '/blood-bank', label: 'بنك الدم', icon: Droplets },
    { path: '/emergency', label: 'الطوارئ', icon: Phone }
  ]

  const userMenuItems = [
    { path: '/dashboard', label: 'لوحة التحكم', icon: LayoutDashboard },
    { path: '/medical-record', label: 'الملف الطبي', icon: ClipboardList },
    { path: '/clinical-summary', label: 'التقرير الطبي الشامل', icon: FileText },
    { path: '/appointments', label: 'المواعيد', icon: Calendar },
    { path: '/prescriptions', label: 'الوصفات الطبية', icon: FileText },
    { path: '/lab-requests', label: 'التحاليل المخبرية', icon: FlaskConical },
    { path: '/radiology', label: 'الأشعة والتصوير', icon: Scan },
    { path: '/medications', label: 'متابعة الأدوية', icon: Pill },
    { path: '/family-health', label: 'صحة الأسرة', icon: Users },
    { path: '/vaccinations', label: 'التطعيمات', icon: Shield },
    { path: '/symptom-checker', label: 'فاحص الأعراض', icon: Stethoscope },
  ]

  return (
    <nav className="sticky top-0 z-50 shadow-sm" style={{ background: '#ffffff', borderBottom: '1px solid #e2e8f0' }}>
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
          </div>

          {/* Desktop User */}
          <div className="hidden md:flex items-center gap-3">
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
                      <div className="py-1">
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
    </nav>
  )
}
