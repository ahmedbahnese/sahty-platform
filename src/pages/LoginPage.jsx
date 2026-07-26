import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Heart, Eye, EyeOff, UserRound, Lock } from 'lucide-react'

export default function LoginPage() {
  const [formData, setFormData] = useState({
    identifier: '',
    password: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  const { login } = useAuth()
  const navigate = useNavigate()

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
        navigate('/dashboard')
      } else {
        setError(result.message)
      }
    } catch (error) {
      setError('حدث خطأ غير متوقع')
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

          {/* رسالة الخطأ */}
          {error && (
            <Alert className="mb-6 border-red-200 bg-red-50">
              <AlertDescription className="text-red-700">
                {error}
              </AlertDescription>
            </Alert>
          )}

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

