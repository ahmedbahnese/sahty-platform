import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '@/components/ui/button'
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
  Scan
} from 'lucide-react'

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const { user, logout, isAuthenticated } = useAuth()
  const location = useLocation()

  const handleLogout = async () => {
    await logout()
    setUserMenuOpen(false)
  }

  const isActive = (path) => {
    return location.pathname === path
  }

  const navLinks = [
    { path: '/', label: 'الرئيسية', icon: Heart },
    { path: '/doctors', label: 'الأطباء', icon: Stethoscope },
    { path: '/services', label: 'الخدمات', icon: Shield },
    { path: '/blood-bank', label: 'بنك الدم', icon: Droplets },
    { path: '/emergency', label: 'الطوارئ', icon: Phone }
  ]

  return (
    <nav className="bg-white shadow-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* الشعار */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2 rtl:space-x-reverse">
              <Heart className="h-8 w-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-900">صحتك في أمان</span>
            </Link>
          </div>

          {/* روابط التنقل - سطح المكتب */}
          <div className="hidden md:flex items-center space-x-8 rtl:space-x-reverse">
            {navLinks.map((link) => {
              const IconComponent = link.icon
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center space-x-1 rtl:space-x-reverse px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive(link.path)
                      ? 'text-blue-600 bg-blue-50'
                      : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                  }`}
                >
                  <IconComponent className="h-4 w-4" />
                  <span>{link.label}</span>
                </Link>
              )
            })}
          </div>

          {/* أزرار المستخدم */}
          <div className="hidden md:flex items-center space-x-4 rtl:space-x-reverse">
            {isAuthenticated ? (
              <div className="relative">
                <Button
                  variant="ghost"
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center space-x-2 rtl:space-x-reverse"
                >
                  <User className="h-4 w-4" />
                  <span>{user?.profile?.first_name || user?.email}</span>
                </Button>

                {userMenuOpen && (
                  <div className="absolute left-0 rtl:right-0 mt-2 w-56 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-100">
                    <Link
                      to="/dashboard"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <Settings className="h-4 w-4 ml-2" />
                      لوحة التحكم
                    </Link>
                    <Link
                      to="/medical-record"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <ClipboardList className="h-4 w-4 ml-2" />
                      الملف الطبي
                    </Link>
                    <Link
                      to="/appointments"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <Calendar className="h-4 w-4 ml-2" />
                      المواعيد
                    </Link>
                    <Link
                      to="/prescriptions"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <FileText className="h-4 w-4 ml-2" />
                      الوصفات الطبية
                    </Link>
                    <Link
                      to="/lab-requests"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <FlaskConical className="h-4 w-4 ml-2" />
                      التحاليل المخبرية
                    </Link>
                    <Link
                      to="/radiology"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <Scan className="h-4 w-4 ml-2" />
                      الأشعة والتصوير
                    </Link>
                    <div className="border-t my-1" />
                    <button
                      onClick={handleLogout}
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      <LogOut className="h-4 w-4 ml-2" />
                      تسجيل الخروج
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-2 rtl:space-x-reverse">
                <Link to="/login">
                  <Button variant="ghost">تسجيل الدخول</Button>
                </Link>
                <Link to="/register">
                  <Button>إنشاء حساب</Button>
                </Link>
              </div>
            )}
          </div>

          {/* زر القائمة - الجوال */}
          <div className="md:hidden flex items-center">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsOpen(!isOpen)}
            >
              {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </Button>
          </div>
        </div>
      </div>

      {/* القائمة المنسدلة - الجوال */}
      {isOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-white border-t">
            {navLinks.map((link) => {
              const IconComponent = link.icon
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center space-x-2 rtl:space-x-reverse px-3 py-2 rounded-md text-base font-medium ${
                    isActive(link.path)
                      ? 'text-blue-600 bg-blue-50'
                      : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                  }`}
                  onClick={() => setIsOpen(false)}
                >
                  <IconComponent className="h-5 w-5" />
                  <span>{link.label}</span>
                </Link>
              )
            })}

            {/* أزرار المستخدم - الجوال */}
            <div className="border-t pt-4 mt-4">
              {isAuthenticated ? (
                <div className="space-y-2">
                  <Link
                    to="/dashboard"
                    className="flex items-center space-x-2 rtl:space-x-reverse px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50"
                    onClick={() => setIsOpen(false)}
                  >
                    <Settings className="h-5 w-5" />
                    <span>لوحة التحكم</span>
                  </Link>
                  <button
                    onClick={() => {
                      handleLogout()
                      setIsOpen(false)
                    }}
                    className="flex items-center space-x-2 rtl:space-x-reverse px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50 w-full text-right"
                  >
                    <LogOut className="h-5 w-5" />
                    <span>تسجيل الخروج</span>
                  </button>
                </div>
              ) : (
                <div className="space-y-2">
                  <Link
                    to="/login"
                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-50"
                    onClick={() => setIsOpen(false)}
                  >
                    تسجيل الدخول
                  </Link>
                  <Link
                    to="/register"
                    className="block px-3 py-2 rounded-md text-base font-medium bg-blue-600 text-white hover:bg-blue-700"
                    onClick={() => setIsOpen(false)}
                  >
                    إنشاء حساب
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </nav>
  )
}

