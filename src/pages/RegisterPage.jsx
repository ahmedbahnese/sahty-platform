import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Building2, Heart, Lock, Mail, Phone, UserRound,
  Stethoscope, FlaskConical, Radio, Hospital, Pill,
  ChevronRight, ChevronLeft,
} from 'lucide-react'

const ROLES = [
  {
    value: 'patient',
    label: 'مريض / مستخدم',
    desc: 'للأفراد الراغبين في إدارة ملفاتهم الصحية',
    icon: UserRound,
    color: 'blue',
  },
  {
    value: 'doctor',
    label: 'طبيب',
    desc: 'للأطباء المرخصين لتقديم الاستشارات وإدارة المرضى',
    icon: Stethoscope,
    color: 'indigo',
  },
  {
    value: 'pharmacy',
    label: 'صيدلية',
    desc: 'لصيدليات الادوية وتنفيذ الوصفات الطبية',
    icon: Pill,
    color: 'emerald',
  },
  {
    value: 'lab',
    label: 'معمل تحاليل',
    desc: 'لمعامل الفحوصات والتحاليل الطبية',
    icon: FlaskConical,
    color: 'amber',
  },
  {
    value: 'radiology_center',
    label: 'مركز أشعة',
    desc: 'لمراكز الأشعة والتصوير الطبي',
    icon: Radio,
    color: 'purple',
  },
  {
    value: 'hospital',
    label: 'مستشفى / مركز طبي',
    desc: 'للمستشفيات والمراكز الطبية المتكاملة',
    icon: Hospital,
    color: 'rose',
  },
]

const ICON_COLORS = {
  blue: 'bg-blue-100 text-blue-600',
  indigo: 'bg-indigo-100 text-indigo-600',
  emerald: 'bg-emerald-100 text-emerald-600',
  amber: 'bg-amber-100 text-amber-600',
  purple: 'bg-purple-100 text-purple-600',
  rose: 'bg-rose-100 text-rose-600',
}
const BORDER_SELECTED = {
  blue: 'border-blue-500 bg-blue-50',
  indigo: 'border-indigo-500 bg-indigo-50',
  emerald: 'border-emerald-500 bg-emerald-50',
  amber: 'border-amber-500 bg-amber-50',
  purple: 'border-purple-500 bg-purple-50',
  rose: 'border-rose-500 bg-rose-50',
}

// ── حقول مشتركة لجميع الأنواع ────────────────────────────────────────────────
function CommonAuthFields({ data, onChange }) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <div>
        <Label htmlFor="email">البريد الإلكتروني *</Label>
        <div className="relative mt-1">
          <Input id="email" name="email" type="email" required
            value={data.email} onChange={onChange} placeholder="name@example.com" />
          <Mail className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
        </div>
      </div>
      <div>
        <Label htmlFor="phone">رقم الهاتف *</Label>
        <div className="relative mt-1">
          <Input id="phone" name="phone" required
            value={data.phone} onChange={onChange} placeholder="01xxxxxxxxx" />
          <Phone className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
        </div>
      </div>
      <div>
        <Label htmlFor="password">كلمة المرور *</Label>
        <div className="relative mt-1">
          <Input id="password" name="password" type="password" required
            value={data.password} onChange={onChange} placeholder="8 أحرف على الأقل" />
          <Lock className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
        </div>
      </div>
      <div>
        <Label htmlFor="confirmPassword">تأكيد كلمة المرور *</Label>
        <div className="relative mt-1">
          <Input id="confirmPassword" name="confirmPassword" type="password" required
            value={data.confirmPassword} onChange={onChange} placeholder="أعد كتابة كلمة المرور" />
          <Lock className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
        </div>
      </div>
    </div>
  )
}

// ── نموذج المريض ─────────────────────────────────────────────────────────────
function PatientForm({ data, onChange }) {
  return (
    <div className="space-y-5">
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <Label htmlFor="first_name">الاسم الأول *</Label>
          <Input id="first_name" name="first_name" required className="mt-1"
            value={data.first_name} onChange={onChange} placeholder="الاسم الأول" />
        </div>
        <div>
          <Label htmlFor="last_name">الاسم الأخير *</Label>
          <Input id="last_name" name="last_name" required className="mt-1"
            value={data.last_name} onChange={onChange} placeholder="الاسم الأخير" />
        </div>
      </div>
      <CommonAuthFields data={data} onChange={onChange} />
      <div className="grid gap-4 rounded-xl bg-gray-50 p-4 md:grid-cols-3">
        <div>
          <Label htmlFor="date_of_birth">تاريخ الميلاد</Label>
          <Input id="date_of_birth" name="date_of_birth" type="date" className="mt-1"
            value={data.date_of_birth} onChange={onChange} />
        </div>
        <div>
          <Label htmlFor="gender">النوع</Label>
          <select id="gender" name="gender" value={data.gender} onChange={onChange}
            className="mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm">
            <option value="">اختر</option>
            <option value="male">ذكر</option>
            <option value="female">أنثى</option>
          </select>
        </div>
        <div>
          <Label htmlFor="national_id">الرقم القومي</Label>
          <Input id="national_id" name="national_id" className="mt-1"
            value={data.national_id} onChange={onChange} placeholder="14 رقماً" />
        </div>
      </div>
    </div>
  )
}

// ── نموذج الطبيب ─────────────────────────────────────────────────────────────
function DoctorForm({ data, onChange }) {
  return (
    <div className="space-y-5">
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <Label htmlFor="first_name">الاسم الأول *</Label>
          <Input id="first_name" name="first_name" required className="mt-1"
            value={data.first_name} onChange={onChange} placeholder="الاسم الأول" />
        </div>
        <div>
          <Label htmlFor="last_name">الاسم الأخير *</Label>
          <Input id="last_name" name="last_name" required className="mt-1"
            value={data.last_name} onChange={onChange} placeholder="الاسم الأخير" />
        </div>
      </div>
      <CommonAuthFields data={data} onChange={onChange} />
      <div className="rounded-xl border border-indigo-100 bg-indigo-50/50 p-5 space-y-4">
        <h3 className="flex items-center gap-2 font-semibold text-indigo-900">
          <Stethoscope className="h-4 w-4" /> بيانات الترخيص المهني
        </h3>
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <Label htmlFor="doc_national_id">رقم الهوية الوطنية *</Label>
            <Input id="doc_national_id" name="doc_national_id" required className="mt-1"
              value={data.doc_national_id} onChange={onChange} placeholder="رقم الهوية" />
          </div>
          <div>
            <Label htmlFor="license_number">رقم ترخيص مزاولة المهنة *</Label>
            <Input id="license_number" name="license_number" required className="mt-1"
              value={data.license_number} onChange={onChange} placeholder="رقم الترخيص" />
          </div>
          <div>
            <Label htmlFor="syndicate_number">رقم السجل النقابي *</Label>
            <Input id="syndicate_number" name="syndicate_number" required className="mt-1"
              value={data.syndicate_number} onChange={onChange} placeholder="رقم النقابة" />
          </div>
          <div>
            <Label htmlFor="specialization">التخصص *</Label>
            <Input id="specialization" name="specialization" required className="mt-1"
              value={data.specialization} onChange={onChange} placeholder="مثال: طب الأطفال" />
          </div>
          <div>
            <Label htmlFor="city">المحافظة *</Label>
            <Input id="city" name="city" required className="mt-1"
              value={data.city} onChange={onChange} placeholder="القاهرة، الجيزة..." />
          </div>
          <div>
            <Label htmlFor="address">عنوان العيادة *</Label>
            <Input id="address" name="address" required className="mt-1"
              value={data.address} onChange={onChange} placeholder="الشارع والمنطقة" />
          </div>
        </div>
      </div>
    </div>
  )
}

// ── نموذج الصيدلية ───────────────────────────────────────────────────────────
function PharmacyForm({ data, onChange }) {
  return (
    <div className="space-y-5">
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <Label htmlFor="first_name">اسم الصيدلاني المسؤول *</Label>
          <Input id="first_name" name="first_name" required className="mt-1"
            value={data.first_name} onChange={onChange} placeholder="الاسم الأول" />
        </div>
        <div>
          <Label htmlFor="last_name">الاسم الأخير *</Label>
          <Input id="last_name" name="last_name" required className="mt-1"
            value={data.last_name} onChange={onChange} placeholder="الاسم الأخير" />
        </div>
      </div>
      <CommonAuthFields data={data} onChange={onChange} />
      <div className="rounded-xl border border-emerald-100 bg-emerald-50/50 p-5 space-y-4">
        <h3 className="flex items-center gap-2 font-semibold text-emerald-900">
          <Pill className="h-4 w-4" /> بيانات الصيدلية
        </h3>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="md:col-span-2">
            <Label htmlFor="legal_name">اسم الصيدلية *</Label>
            <Input id="legal_name" name="legal_name" required className="mt-1"
              value={data.legal_name} onChange={onChange} placeholder="الاسم الرسمي للصيدلية" />
          </div>
          <div>
            <Label htmlFor="license_number">رقم الترخيص *</Label>
            <Input id="license_number" name="license_number" required className="mt-1"
              value={data.license_number} onChange={onChange} placeholder="رقم ترخيص الصيدلية" />
          </div>
          <div>
            <Label htmlFor="city">المحافظة / المدينة *</Label>
            <Input id="city" name="city" required className="mt-1"
              value={data.city} onChange={onChange} placeholder="المدينة" />
          </div>
          <div className="md:col-span-2">
            <Label htmlFor="address">عنوان الصيدلية *</Label>
            <Input id="address" name="address" required className="mt-1"
              value={data.address} onChange={onChange} placeholder="الشارع والمنطقة والمبنى" />
          </div>
        </div>
      </div>
    </div>
  )
}

// ── نموذج المعمل ─────────────────────────────────────────────────────────────
function LabForm({ data, onChange }) {
  return (
    <div className="space-y-5">
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <Label htmlFor="first_name">اسم المسؤول / المدير *</Label>
          <Input id="first_name" name="first_name" required className="mt-1"
            value={data.first_name} onChange={onChange} placeholder="الاسم الأول" />
        </div>
        <div>
          <Label htmlFor="last_name">الاسم الأخير *</Label>
          <Input id="last_name" name="last_name" required className="mt-1"
            value={data.last_name} onChange={onChange} placeholder="الاسم الأخير" />
        </div>
      </div>
      <CommonAuthFields data={data} onChange={onChange} />
      <div className="rounded-xl border border-amber-100 bg-amber-50/50 p-5 space-y-4">
        <h3 className="flex items-center gap-2 font-semibold text-amber-900">
          <FlaskConical className="h-4 w-4" /> بيانات المعمل
        </h3>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="md:col-span-2">
            <Label htmlFor="legal_name">اسم المعمل *</Label>
            <Input id="legal_name" name="legal_name" required className="mt-1"
              value={data.legal_name} onChange={onChange} placeholder="الاسم الرسمي للمعمل" />
          </div>
          <div>
            <Label htmlFor="license_number">رقم الترخيص *</Label>
            <Input id="license_number" name="license_number" required className="mt-1"
              value={data.license_number} onChange={onChange} placeholder="رقم ترخيص المعمل" />
          </div>
          <div>
            <Label htmlFor="city">المحافظة / المدينة *</Label>
            <Input id="city" name="city" required className="mt-1"
              value={data.city} onChange={onChange} placeholder="المدينة" />
          </div>
          <div className="md:col-span-2">
            <Label htmlFor="address">العنوان *</Label>
            <Input id="address" name="address" required className="mt-1"
              value={data.address} onChange={onChange} placeholder="الشارع والمنطقة" />
          </div>
        </div>
      </div>
    </div>
  )
}

// ── نموذج مركز الأشعة ────────────────────────────────────────────────────────
function RadiologyForm({ data, onChange }) {
  return (
    <div className="space-y-5">
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <Label htmlFor="first_name">اسم المسؤول *</Label>
          <Input id="first_name" name="first_name" required className="mt-1"
            value={data.first_name} onChange={onChange} placeholder="الاسم الأول" />
        </div>
        <div>
          <Label htmlFor="last_name">الاسم الأخير *</Label>
          <Input id="last_name" name="last_name" required className="mt-1"
            value={data.last_name} onChange={onChange} placeholder="الاسم الأخير" />
        </div>
      </div>
      <CommonAuthFields data={data} onChange={onChange} />
      <div className="rounded-xl border border-purple-100 bg-purple-50/50 p-5 space-y-4">
        <h3 className="flex items-center gap-2 font-semibold text-purple-900">
          <Radio className="h-4 w-4" /> بيانات مركز الأشعة
        </h3>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="md:col-span-2">
            <Label htmlFor="legal_name">اسم المركز *</Label>
            <Input id="legal_name" name="legal_name" required className="mt-1"
              value={data.legal_name} onChange={onChange} placeholder="الاسم الرسمي لمركز الأشعة" />
          </div>
          <div>
            <Label htmlFor="license_number">رقم الترخيص *</Label>
            <Input id="license_number" name="license_number" required className="mt-1"
              value={data.license_number} onChange={onChange} placeholder="رقم الترخيص" />
          </div>
          <div>
            <Label htmlFor="city">المحافظة / المدينة *</Label>
            <Input id="city" name="city" required className="mt-1"
              value={data.city} onChange={onChange} placeholder="المدينة" />
          </div>
          <div className="md:col-span-2">
            <Label htmlFor="address">العنوان *</Label>
            <Input id="address" name="address" required className="mt-1"
              value={data.address} onChange={onChange} placeholder="الشارع والمنطقة" />
          </div>
        </div>
      </div>
    </div>
  )
}

// ── نموذج المستشفى ───────────────────────────────────────────────────────────
function HospitalForm({ data, onChange }) {
  return (
    <div className="space-y-5">
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <Label htmlFor="first_name">اسم المدير المسؤول *</Label>
          <Input id="first_name" name="first_name" required className="mt-1"
            value={data.first_name} onChange={onChange} placeholder="الاسم الأول" />
        </div>
        <div>
          <Label htmlFor="last_name">الاسم الأخير *</Label>
          <Input id="last_name" name="last_name" required className="mt-1"
            value={data.last_name} onChange={onChange} placeholder="الاسم الأخير" />
        </div>
      </div>
      <CommonAuthFields data={data} onChange={onChange} />
      <div className="rounded-xl border border-rose-100 bg-rose-50/50 p-5 space-y-4">
        <h3 className="flex items-center gap-2 font-semibold text-rose-900">
          <Hospital className="h-4 w-4" /> بيانات المستشفى
        </h3>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="md:col-span-2">
            <Label htmlFor="legal_name">اسم المستشفى / المركز الطبي *</Label>
            <Input id="legal_name" name="legal_name" required className="mt-1"
              value={data.legal_name} onChange={onChange} placeholder="الاسم الرسمي" />
          </div>
          <div>
            <Label htmlFor="license_number">رقم الترخيص *</Label>
            <Input id="license_number" name="license_number" required className="mt-1"
              value={data.license_number} onChange={onChange} placeholder="رقم الترخيص الصادر من الوزارة" />
          </div>
          <div>
            <Label htmlFor="city">المحافظة / المدينة *</Label>
            <Input id="city" name="city" required className="mt-1"
              value={data.city} onChange={onChange} placeholder="المدينة" />
          </div>
          <div className="md:col-span-2">
            <Label htmlFor="address">العنوان *</Label>
            <Input id="address" name="address" required className="mt-1"
              value={data.address} onChange={onChange} placeholder="الشارع والمنطقة" />
          </div>
        </div>
      </div>
    </div>
  )
}

const FORMS = {
  patient: PatientForm,
  doctor: DoctorForm,
  pharmacy: PharmacyForm,
  lab: LabForm,
  radiology_center: RadiologyForm,
  hospital: HospitalForm,
}

const PROFESSIONAL_TYPES = new Set(['doctor', 'pharmacy', 'lab', 'radiology_center', 'hospital'])

export default function RegisterPage() {
  const [step, setStep] = useState(1) // 1 = اختر نوع الحساب, 2 = ملء البيانات
  const [selectedRole, setSelectedRole] = useState(null)
  const [formData, setFormData] = useState({
    first_name: '', last_name: '', email: '', phone: '',
    password: '', confirmPassword: '',
    // patient
    date_of_birth: '', gender: '', national_id: '',
    // doctor
    doc_national_id: '', license_number: '', syndicate_number: '',
    specialization: '', city: '', address: '',
    // institutions
    legal_name: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const { register } = useAuth()
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }))
    setError('')
  }

  const handleRoleSelect = (role) => {
    setSelectedRole(role)
    setStep(2)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (formData.password.length < 8) {
      setError('كلمة المرور يجب أن تكون 8 أحرف على الأقل')
      return
    }
    if (formData.password !== formData.confirmPassword) {
      setError('كلمات المرور غير متطابقة')
      return
    }

    setLoading(true)

    // Build payload — map role-specific fields to what the backend expects
    const payload = {
      user_type: selectedRole,
      first_name: formData.first_name,
      last_name: formData.last_name,
      email: formData.email,
      phone: formData.phone,
      password: formData.password,
    }

    if (selectedRole === 'patient') {
      payload.date_of_birth = formData.date_of_birth || undefined
      payload.gender = formData.gender || undefined
      payload.national_id = formData.national_id || undefined
    }

    if (selectedRole === 'doctor') {
      payload.legal_name = `${formData.first_name} ${formData.last_name}`
      payload.license_number = formData.license_number
      payload.specialization = formData.specialization
      payload.city = formData.city
      payload.address = formData.address
      // extra doctor fields stored in details
      payload.national_id_doc = formData.doc_national_id
      payload.syndicate_number = formData.syndicate_number
    }

    if (['pharmacy', 'lab', 'radiology_center', 'hospital'].includes(selectedRole)) {
      payload.legal_name = formData.legal_name
      payload.license_number = formData.license_number
      payload.city = formData.city
      payload.address = formData.address
    }

    const result = await register(payload)
    setLoading(false)

    if (!result.success) {
      setError(result.message)
      return
    }

    if (PROFESSIONAL_TYPES.has(selectedRole)) {
      navigate('/pending')
    } else {
      navigate('/dashboard')
    }
  }

  const roleInfo = ROLES.find(r => r.value === selectedRole)
  const FormComponent = selectedRole ? FORMS[selectedRole] : null

  // ── الخطوة 1: اختيار نوع الحساب ─────────────────────────────────────────
  if (step === 1) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-12" dir="rtl">
        <div className="mx-auto max-w-4xl">
          <div className="mb-10 text-center">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-blue-100">
              <Heart className="h-8 w-8 text-blue-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">إنشاء حساب جديد</h1>
            <p className="mt-2 text-gray-600">اختر نوع حسابك للبدء</p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {ROLES.map((role) => {
              const Icon = role.icon
              return (
                <button
                  key={role.value}
                  onClick={() => handleRoleSelect(role.value)}
                  className="group rounded-2xl border-2 border-gray-200 bg-white p-6 text-right shadow-sm transition-all hover:border-blue-400 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <div className={`mb-4 flex h-12 w-12 items-center justify-center rounded-xl ${ICON_COLORS[role.color]}`}>
                    <Icon className="h-6 w-6" />
                  </div>
                  <h3 className="font-bold text-gray-900">{role.label}</h3>
                  <p className="mt-1 text-sm text-gray-500">{role.desc}</p>
                  <div className="mt-4 flex items-center text-sm font-semibold text-blue-600">
                    <span>ابدأ التسجيل</span>
                    <ChevronLeft className="mr-1 h-4 w-4 transition-transform group-hover:-translate-x-1" />
                  </div>
                </button>
              )
            })}
          </div>

          <p className="mt-8 text-center text-gray-600">
            لديك حساب بالفعل؟{' '}
            <Link to="/login" className="font-semibold text-blue-600 hover:underline">تسجيل الدخول</Link>
          </p>
        </div>
      </div>
    )
  }

  // ── الخطوة 2: ملء بيانات التسجيل ────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-12" dir="rtl">
      <div className="mx-auto max-w-3xl rounded-2xl bg-white p-8 shadow-xl">
        {/* رأس الصفحة */}
        <div className="mb-8 flex items-center gap-4">
          <button onClick={() => setStep(1)}
            className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700">
            <ChevronRight className="h-4 w-4" /> تغيير نوع الحساب
          </button>
          <div className="flex items-center gap-2">
            {roleInfo && (
              <>
                <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${ICON_COLORS[roleInfo.color]}`}>
                  <roleInfo.icon className="h-4 w-4" />
                </div>
                <span className="font-semibold text-gray-900">{roleInfo.label}</span>
              </>
            )}
          </div>
        </div>

        <h1 className="mb-2 text-2xl font-bold text-gray-900">
          {selectedRole === 'patient' ? 'بيانات التسجيل' : 'طلب اعتماد حساب مهني'}
        </h1>
        {PROFESSIONAL_TYPES.has(selectedRole) && (
          <p className="mb-6 rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800 border border-amber-200">
            ⏳ سيتم مراجعة بياناتك من الإدارة الطبية قبل تفعيل الحساب. لا يمكن تسجيل الدخول حتى يتم الاعتماد.
          </p>
        )}

        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50">
            <AlertDescription className="text-red-700">{error}</AlertDescription>
          </Alert>
        )}
        {success && (
          <Alert className="mb-6 border-green-200 bg-green-50">
            <AlertDescription className="text-green-700">{success}</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {FormComponent && <FormComponent data={formData} onChange={handleChange} />}

          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input type="checkbox" required className="h-4 w-4 rounded border-gray-300 text-blue-600" />
            أوافق على شروط الاستخدام وسياسة الخصوصية
          </label>

          <Button type="submit" className="w-full" disabled={loading}>
            {loading
              ? 'جاري إرسال الطلب...'
              : selectedRole === 'patient' ? 'إنشاء الحساب' : 'إرسال طلب الاعتماد'
            }
          </Button>
        </form>

        <p className="mt-6 text-center text-gray-600">
          لديك حساب بالفعل؟{' '}
          <Link to="/login" className="font-semibold text-blue-600 hover:underline">تسجيل الدخول</Link>
        </p>
      </div>
    </div>
  )
}
