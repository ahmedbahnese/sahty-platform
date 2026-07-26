import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Building2, Heart, Lock, Mail, Phone, UserRound } from 'lucide-react'

const accountTypes = [
  { value: 'patient', label: 'مستخدم / مريض' },
  { value: 'doctor', label: 'طبيب' },
  { value: 'pharmacy', label: 'صيدلية' },
  { value: 'lab', label: 'معمل' },
  { value: 'radiology_center', label: 'مركز أشعة' },
  { value: 'hospital', label: 'مستشفى' },
]

const professionalTypes = new Set(accountTypes.slice(1).map((type) => type.value))

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    username: '', email: '', password: '', confirmPassword: '',
    user_type: 'patient', first_name: '', last_name: '', phone: '',
    date_of_birth: '', gender: '', national_id: '', legal_name: '',
    license_number: '', specialization: '', address: '', city: '',
    website: '', services: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const { register } = useAuth()
  const navigate = useNavigate()
  const isProfessional = professionalTypes.has(formData.user_type)

  const handleChange = (event) => {
    setFormData((current) => ({ ...current, [event.target.name]: event.target.value }))
    setError('')
    setSuccess('')
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSuccess('')
    if (formData.password.length < 8) {
      setError('كلمة المرور يجب أن تكون 8 أحرف على الأقل')
      return
    }
    if (formData.password !== formData.confirmPassword) {
      setError('كلمات المرور غير متطابقة')
      return
    }
    setLoading(true)
    const result = await register(formData)
    setLoading(false)
    if (!result.success) {
      setError(result.message)
      return
    }
    if (isProfessional) {
      setSuccess(`${result.message} سيتم تحويلك لتسجيل الدخول بعد قليل.`)
      window.setTimeout(() => navigate('/login'), 2500)
    } else {
      navigate('/dashboard')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-12">
      <div className="mx-auto max-w-3xl rounded-2xl bg-white p-8 shadow-xl">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-blue-100">
            <Heart className="h-8 w-8 text-blue-600" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">إنشاء حساب جديد</h1>
          <p className="mt-2 text-gray-600">اختر نوع الحساب للوصول إلى لوحة التحكم المناسبة</p>
        </div>

        {error && <Alert className="mb-6 border-red-200 bg-red-50"><AlertDescription className="text-red-700">{error}</AlertDescription></Alert>}
        {success && <Alert className="mb-6 border-green-200 bg-green-50"><AlertDescription className="text-green-700">{success}</AlertDescription></Alert>}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <Label htmlFor="user_type">نوع الحساب</Label>
            <select id="user_type" name="user_type" value={formData.user_type} onChange={handleChange} className="mt-2 block w-full rounded-md border border-gray-300 bg-white px-3 py-2">
              {accountTypes.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}
            </select>
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            <div><Label htmlFor="first_name">الاسم الأول *</Label><Input id="first_name" name="first_name" required value={formData.first_name} onChange={handleChange} placeholder="الاسم الأول" /></div>
            <div><Label htmlFor="last_name">الاسم الأخير *</Label><Input id="last_name" name="last_name" required value={formData.last_name} onChange={handleChange} placeholder="الاسم الأخير" /></div>
            <div><Label htmlFor="username">اسم المستخدم *</Label><Input id="username" name="username" required value={formData.username} onChange={handleChange} placeholder="اسم الدخول" /></div>
            <div><Label htmlFor="email">البريد الإلكتروني *</Label><div className="relative"><Input id="email" name="email" type="email" required value={formData.email} onChange={handleChange} placeholder="name@example.com" /><Mail className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" /></div></div>
            <div><Label htmlFor="phone">رقم الهاتف *</Label><div className="relative"><Input id="phone" name="phone" required value={formData.phone} onChange={handleChange} placeholder="01xxxxxxxxx" /><Phone className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" /></div></div>
            <div><Label htmlFor="password">كلمة المرور *</Label><div className="relative"><Input id="password" name="password" type="password" required value={formData.password} onChange={handleChange} placeholder="8 أحرف على الأقل" /><Lock className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" /></div></div>
            <div><Label htmlFor="confirmPassword">تأكيد كلمة المرور *</Label><Input id="confirmPassword" name="confirmPassword" type="password" required value={formData.confirmPassword} onChange={handleChange} /></div>
          </div>

          {!isProfessional && (
            <div className="grid gap-5 rounded-xl bg-gray-50 p-5 md:grid-cols-3">
              <div><Label htmlFor="date_of_birth">تاريخ الميلاد</Label><Input id="date_of_birth" name="date_of_birth" type="date" value={formData.date_of_birth} onChange={handleChange} /></div>
              <div><Label htmlFor="gender">النوع</Label><select id="gender" name="gender" value={formData.gender} onChange={handleChange} className="mt-2 block w-full rounded-md border border-gray-300 px-3 py-2"><option value="">اختر</option><option value="male">ذكر</option><option value="female">أنثى</option></select></div>
              <div><Label htmlFor="national_id">الرقم القومي</Label><Input id="national_id" name="national_id" value={formData.national_id} onChange={handleChange} /></div>
            </div>
          )}

          {isProfessional && (
            <div className="space-y-5 rounded-xl border border-blue-100 bg-blue-50/60 p-5">
              <div className="flex items-center gap-2 text-blue-900"><Building2 className="h-5 w-5" /><h2 className="font-semibold">بيانات الجهة المطلوب اعتمادها</h2></div>
              <div className="grid gap-5 md:grid-cols-2">
                <div><Label htmlFor="legal_name">اسم الجهة *</Label><Input id="legal_name" name="legal_name" required value={formData.legal_name} onChange={handleChange} placeholder="اسم العيادة أو الجهة" /></div>
                <div><Label htmlFor="license_number">رقم الترخيص *</Label><Input id="license_number" name="license_number" required value={formData.license_number} onChange={handleChange} /></div>
                <div><Label htmlFor="city">المحافظة / المدينة *</Label><Input id="city" name="city" required value={formData.city} onChange={handleChange} /></div>
                <div><Label htmlFor="specialization">التخصص</Label><Input id="specialization" name="specialization" value={formData.specialization} onChange={handleChange} placeholder="للطبيب أو المعمل" /></div>
                <div className="md:col-span-2"><Label htmlFor="address">العنوان *</Label><Input id="address" name="address" required value={formData.address} onChange={handleChange} /></div>
                <div><Label htmlFor="website">الموقع الإلكتروني</Label><Input id="website" name="website" value={formData.website} onChange={handleChange} /></div>
                <div><Label htmlFor="services">الخدمات</Label><Input id="services" name="services" value={formData.services} onChange={handleChange} placeholder="افصل بين الخدمات بفاصلة" /></div>
              </div>
              <p className="text-sm text-blue-800">سيتم مراجعة الطلب من الإدارة. لا يمكن تسجيل الدخول إلى لوحة الجهة قبل الاعتماد.</p>
            </div>
          )}

          <label className="flex items-center gap-2 text-sm text-gray-700"><input type="checkbox" required /> أوافق على شروط الاستخدام وسياسة الخصوصية</label>
          <Button type="submit" className="w-full" disabled={loading}>{loading ? 'جاري إنشاء الحساب...' : 'إنشاء الحساب'}</Button>
        </form>

        <p className="mt-6 text-center text-gray-600">لديك حساب بالفعل؟ <Link to="/login" className="font-semibold text-blue-600">تسجيل الدخول</Link></p>
      </div>
    </div>
  )
}