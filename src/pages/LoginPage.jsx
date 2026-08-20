import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Heart, Eye, EyeOff, UserRound, Lock, Stethoscope, HeartPulse, Hospital, FlaskConical, Pill, ScanLine, Droplets } from 'lucide-react'
import { useNotifications } from '../contexts/NotificationContext'

export default function LoginPage() {
  const [formData, setFormData] = useState({
    identifier: '',
    password: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  const { login } = useAuth()
  const notifications = useNotifications()
  const navigate = useNavigate()
  const demoAccounts = [
    { email: 'doctor@sehaty.com', label: 'الطبيب', icon: Stethoscope, className: 'border-blue-100 text-blue-700' },
    { email: 'nurse@sehaty.com', label: 'التمريض', icon: HeartPulse, className: 'border-rose-100 text-rose-700' },
    { email: 'hospital@sehaty.com', label: 'المستشفى', icon: Hospital, className: 'border-indigo-100 text-indigo-700' },
    { email: 'lab@sehaty.com', label: 'المعمل', icon: FlaskConical, className: 'border-emerald-100 text-emerald-700' },
    { email: 'pharma@sehaty.com', label: 'الصيدلية', icon: Pill, className: 'border-amber-100 text-amber-700' },
    { email: 'rad@sehaty.com', label: 'مركز الأشعة', icon: ScanLine, className: 'border-violet-100 text-violet-700' },
    { email: 'bloodbank@sehaty.com', label: 'بنك الدم', icon: Droplets, className: 'border-red-100 text-red-700' },
  ]
  const showDemoAccounts = import.meta.env.VITE_ENABLE_DEMO_ACCOUNTS === 'true'
  const demoPassword = import.meta.env.VITE_DEMO_PASSWORD || ''
  const selectDemoAccount = (email) => {
    setFormData({ identifier: email, password: demoPassword })
    setError('')
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const result = await login(formData.identifier, formData.password)

      if (result.success) {
        notifications.success('تم تسجيل الدخول بنجاح. جارٍ فتح لوحة التحكم.', 'تم تسجيل الدخول')
        const type = result.user?.user_type
        if (type === 'admin' || type === 'super_admin') {
          navigate('/admin')
        } else {
          navigate('/dashboard')
        }
      } else if (result.pending_review) {
        // الحساب موجود لكنه بانتظار اعتماد الإدارة أو مرفوض
        navigate('/pending', { state: { status: result.provider_status || 'pending' } })
      } else {
        setError(result.message)
        notifications.error(result.message || 'تحقق من بيانات الدخول وحاول مرة أخرى.', 'لم يتم تسجيل الدخول')
      }
    } catch {
      setError('حدث خطأ غير متوقع')
      notifications.error('تعذر الاتصال بالخادم. تحقق من الاتصال وحاول مرة أخرى.', 'لم يتم تسجيل الدخول')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* الرأس */}
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              <div className="bg-blue-100 p-3 rounded-full">
                <Heart className="h-8 w-8 text-blue-600" />
              </div>
            </div>
            <h2 className="text-3xl font-bold text-gray-900">
              تسجيل الدخول
            </h2>
            <p className="mt-2 text-gray-600">
              أدخل اسم المستخدم أو رقم الهاتف أو البريد الإلكتروني وكلمة المرور
            </p>
          </div>

          <p className="sr-only" aria-live="assertive">{error}</p>

          {showDemoAccounts && <section className="mb-6 rounded-2xl border border-cyan-100 bg-cyan-50/70 p-4" aria-label="حسابات التجربة">
            <div className="mb-3 flex items-center justify-between"><div><h3 className="font-bold text-cyan-950">تجربة الخدمات حسب الدور</h3><p className="mt-1 text-xs text-cyan-700">اختر دورًا لملء بيانات الدخول تلقائيًا</p></div><span className="rounded-full bg-white px-2 py-1 text-[10px] font-bold text-cyan-700">بيئة اختبار</span></div>
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">{demoAccounts.map(({ email, label, icon: Icon, className }) => <button key={email} type="button" onClick={() => selectDemoAccount(email)} className={`flex min-h-16 flex-col items-center justify-center gap-1 rounded-xl border bg-white px-2 py-2 text-xs font-semibold transition hover:-translate-y-0.5 hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 ${className}`}><Icon className="h-5 w-5" aria-hidden="true"/><span>{label}</span></button>)}</div>
            <p className="mt-3 text-center text-[11px] text-cyan-800">كلمة مرور التجربة مضبوطة من Secret في بيئة الاختبار.</p>
          </section>}

          {/* النموذج */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <Label htmlFor="identifier" className="text-gray-700">
                اسم المستخدم أو الهاتف أو البريد الإلكتروني
              </Label>
              <div className="mt-1 relative">
                <Input
                  id="identifier"
                  name="identifier"
                  type="text"
                  required
                  value={formData.identifier}
                  onChange={handleChange}
                  className="pl-10"
                  placeholder="أدخل اسم المستخدم أو الهاتف أو البريد"
                />
                <UserRound className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
              </div>
            </div>

            <div>
              <Label htmlFor="password" className="text-gray-700">
                كلمة المرور
              </Label>
              <div className="mt-1 relative">
                <Input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="pl-10 pr-10"
                  placeholder="أدخل كلمة المرور"
                />
                <Lock className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="remember-me" className="mr-2 block text-sm text-gray-700">
                  تذكرني
                </label>
              </div>

              <div className="text-sm">
                <a href="#" className="font-medium text-blue-600 hover:text-blue-500">
                  نسيت كلمة المرور؟
                </a>
              </div>
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={loading}
            >
              {loading ? 'جاري تسجيل الدخول...' : 'تسجيل الدخول'}
            </Button>

          </form>

          {/* رابط التسجيل */}
          <div className="mt-6 text-center">
            <p className="text-gray-600">
              ليس لديك حساب؟{' '}
              <Link to="/register" className="font-medium text-blue-600 hover:text-blue-500">
                إنشاء حساب جديد
              </Link>
            </p>
          </div>
        </div>

        {/* روابط إضافية */}
        <div className="text-center">
          <Link to="/" className="text-blue-600 hover:text-blue-500 text-sm">
            العودة إلى الصفحة الرئيسية
          </Link>
        </div>
      </div>
    </div>
  )
}

