import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Heart, 
  Eye, 
  EyeOff, 
  Mail, 
  Lock, 
  User, 
  Phone, 
  Calendar,
  IdCard,
  Stethoscope,
  Users
} from 'lucide-react'

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    user_type: 'patient',
    first_name: '',
    last_name: '',
    phone: '',
    date_of_birth: '',
    gender: '',
    national_id: '',
    // للأطباء
    license_number: '',
    specialization: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    setError('')
    setSuccess('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    // التحقق من تطابق كلمات المرور
    if (formData.password !== formData.confirmPassword) {
      setError('كلمات المرور غير متطابقة')
      setLoading(false)
      return
    }

    // التحقق من قوة كلمة المرور
    if (formData.password.length < 8) {
      setError('كلمة المرور يجب أن تكون 8 أحرف على الأقل')
      setLoading(false)
      return
    }

    try {
      const result = await register(formData)

      if (result.success) {
        setSuccess('تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول')
        setTimeout(() => {
          navigate('/login')
        }, 2000)
      } else {
        setError(result.message)
      }
    } catch (error) {
      setError('حدث خطأ غير متوقع')
    } finally {
      setLoading(false)
    }
  }

  const specializations = [
    'طب عام',
    'طب الأطفال',
    'طب النساء والتوليد',
    'طب القلب',
    'طب العظام',
    'طب الأعصاب',
    'طب العيون',
    'طب الأنف والأذن والحنجرة',
    'طب الجلدية',
    'طب النفسية',
    'طب الأسنان',
    'الجراحة العامة',
    'جراحة القلب',
    'جراحة المخ والأعصاب',
    'طب الطوارئ',
    'طب الأشعة',
    'طب المختبرات',
    'طب التخدير'
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* الرأس */}
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              <div className="bg-blue-100 p-3 rounded-full">
                <Heart className="h-8 w-8 text-blue-600" />
              </div>
            </div>
            <h2 className="text-3xl font-bold text-gray-900">
              إنشاء حساب جديد
            </h2>
            <p className="mt-2 text-gray-600">
              انضم إلى منصة صحتك في أمان واحصل على أفضل الخدمات الطبية
            </p>
          </div>

          {/* رسائل النجاح والخطأ */}
          {error && (
            <Alert className="mb-6 border-red-200 bg-red-50">
              <AlertDescription className="text-red-700">
                {error}
              </AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert className="mb-6 border-green-200 bg-green-50">
              <AlertDescription className="text-green-700">
                {success}
              </AlertDescription>
            </Alert>
          )}

          {/* النموذج */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* نوع المستخدم */}
            <div>
              <Label className="text-gray-700 mb-3 block">نوع الحساب</Label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <label className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                  formData.user_type === 'patient' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                }`}>
                  <input
                    type="radio"
                    name="user_type"
                    value="patient"
                    checked={formData.user_type === 'patient'}
                    onChange={handleChange}
                    className="sr-only"
                  />
                  <Users className="h-6 w-6 text-blue-600 ml-3" />
                  <span className="font-medium">مريض</span>
                </label>

                <label className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                  formData.user_type === 'doctor' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                }`}>
                  <input
                    type="radio"
                    name="user_type"
                    value="doctor"
                    checked={formData.user_type === 'doctor'}
                    onChange={handleChange}
                    className="sr-only"
                  />
                  <Stethoscope className="h-6 w-6 text-blue-600 ml-3" />
                  <span className="font-medium">طبيب</span>
                </label>

                <label className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                  formData.user_type === 'admin' ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
                }`}>
                  <input
                    type="radio"
                    name="user_type"
                    value="admin"
                    checked={formData.user_type === 'admin'}
                    onChange={handleChange}
                    className="sr-only"
                  />
                  <User className="h-6 w-6 text-blue-600 ml-3" />
                  <span className="font-medium">مدير</span>
                </label>
              </div>
            </div>

            {/* المعلومات الشخصية */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label htmlFor="first_name" className="text-gray-700">
                  الاسم الأول *
                </Label>
                <div className="mt-1 relative">
                  <Input
                    id="first_name"
                    name="first_name"
                    type="text"
                    required
                    value={formData.first_name}
                    onChange={handleChange}
                    className="pl-10"
                    placeholder="الاسم الأول"
                  />
                  <User className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                </div>
              </div>

              <div>
                <Label htmlFor="last_name" className="text-gray-700">
                  الاسم الأخير *
                </Label>
                <div className="mt-1 relative">
                  <Input
                    id="last_name"
                    name="last_name"
                    type="text"
                    required
                    value={formData.last_name}
                    onChange={handleChange}
                    className="pl-10"
                    placeholder="الاسم الأخير"
                  />
                  <User className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                </div>
              </div>
            </div>

            {/* البريد الإلكتروني والهاتف */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label htmlFor="email" className="text-gray-700">
                  البريد الإلكتروني *
                </Label>
                <div className="mt-1 relative">
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    required
                    value={formData.email}
                    onChange={handleChange}
                    className="pl-10"
                    placeholder="example@email.com"
                  />
                  <Mail className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                </div>
              </div>

              <div>
                <Label htmlFor="phone" className="text-gray-700">
                  رقم الهاتف *
                </Label>
                <div className="mt-1 relative">
                  <Input
                    id="phone"
                    name="phone"
                    type="tel"
                    required
                    value={formData.phone}
                    onChange={handleChange}
                    className="pl-10"
                    placeholder="01xxxxxxxxx"
                  />
                  <Phone className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                </div>
              </div>
            </div>

            {/* كلمات المرور */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label htmlFor="password" className="text-gray-700">
                  كلمة المرور *
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
                    placeholder="كلمة المرور"
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

              <div>
                <Label htmlFor="confirmPassword" className="text-gray-700">
                  تأكيد كلمة المرور *
                </Label>
                <div className="mt-1 relative">
                  <Input
                    id="confirmPassword"
                    name="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    required
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    className="pl-10 pr-10"
                    placeholder="تأكيد كلمة المرور"
                  />
                  <Lock className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
              </div>
            </div>

            {/* معلومات إضافية للمرضى */}
            {formData.user_type === 'patient' && (
              <>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <Label htmlFor="date_of_birth" className="text-gray-700">
                      تاريخ الميلاد
                    </Label>
                    <div className="mt-1 relative">
                      <Input
                        id="date_of_birth"
                        name="date_of_birth"
                        type="date"
                        value={formData.date_of_birth}
                        onChange={handleChange}
                        className="pl-10"
                      />
                      <Calendar className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="gender" className="text-gray-700">
                      الجنس
                    </Label>
                    <select
                      id="gender"
                      name="gender"
                      value={formData.gender}
                      onChange={handleChange}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">اختر الجنس</option>
                      <option value="male">ذكر</option>
                      <option value="female">أنثى</option>
                    </select>
                  </div>

                  <div>
                    <Label htmlFor="national_id" className="text-gray-700">
                      الرقم القومي
                    </Label>
                    <div className="mt-1 relative">
                      <Input
                        id="national_id"
                        name="national_id"
                        type="text"
                        value={formData.national_id}
                        onChange={handleChange}
                        className="pl-10"
                        placeholder="الرقم القومي"
                      />
                      <IdCard className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                    </div>
                  </div>
                </div>
              </>
            )}

            {/* معلومات إضافية للأطباء */}
            {formData.user_type === 'doctor' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="license_number" className="text-gray-700">
                    رقم الترخيص *
                  </Label>
                  <div className="mt-1 relative">
                    <Input
                      id="license_number"
                      name="license_number"
                      type="text"
                      required
                      value={formData.license_number}
                      onChange={handleChange}
                      className="pl-10"
                      placeholder="رقم ترخيص مزاولة المهنة"
                    />
                    <IdCard className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                  </div>
                </div>

                <div>
                  <Label htmlFor="specialization" className="text-gray-700">
                    التخصص *
                  </Label>
                  <select
                    id="specialization"
                    name="specialization"
                    required
                    value={formData.specialization}
                    onChange={handleChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">اختر التخصص</option>
                    {specializations.map((spec, index) => (
                      <option key={index} value={spec}>{spec}</option>
                    ))}
                  </select>
                </div>
              </div>
            )}

            {/* الموافقة على الشروط */}
            <div className="flex items-center">
              <input
                id="terms"
                name="terms"
                type="checkbox"
                required
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="terms" className="mr-2 block text-sm text-gray-700">
                أوافق على{' '}
                <a href="#" className="text-blue-600 hover:text-blue-500">
                  شروط الاستخدام
                </a>
                {' '}و{' '}
                <a href="#" className="text-blue-600 hover:text-blue-500">
                  سياسة الخصوصية
                </a>
              </label>
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={loading}
            >
              {loading ? 'جاري إنشاء الحساب...' : 'إنشاء حساب'}
            </Button>
          </form>

          {/* رابط تسجيل الدخول */}
          <div className="mt-6 text-center">
            <p className="text-gray-600">
              لديك حساب بالفعل؟{' '}
              <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500">
                تسجيل الدخول
              </Link>
            </p>
          </div>
        </div>

        {/* روابط إضافية */}
        <div className="text-center mt-6">
          <Link to="/" className="text-blue-600 hover:text-blue-500 text-sm">
            العودة إلى الصفحة الرئيسية
          </Link>
        </div>
      </div>
    </div>
  )
}

