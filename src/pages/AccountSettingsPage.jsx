import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { ArrowRight, LockKeyhole, Phone, Save, UserRound, LogOut, Stethoscope, Clock3 } from 'lucide-react'

const authHeaders = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('token')}`,
})

export default function AccountSettingsPage() {
  const { user, logout, switchRole } = useAuth()
  const navigate = useNavigate()
  const [phone, setPhone] = useState(user?.profile?.phone || '')
  const [passwords, setPasswords] = useState({ current_password: '', new_password: '', confirmation: '' })
  const [message, setMessage] = useState(null)
  const [busy, setBusy] = useState(false)
  const [doctorProfile, setDoctorProfile] = useState({ clinic_name: user?.profile?.clinic_name || '', clinic_address: user?.profile?.clinic_address || '', specialization: user?.profile?.specialization || '', consultation_duration: user?.profile?.consultation_duration || 30 })
  const [clinicLocations, setClinicLocations] = useState(user?.profile?.clinic_locations || [])
  const [profileImage, setProfileImage] = useState(null)
  const [availability, setAvailability] = useState([])

  const savePhone = async event => {
    event.preventDefault()
    setBusy(true)
    setMessage(null)
    try {
      const response = await fetch('/api/auth/profile', {
        method: 'PUT',
        headers: authHeaders(),
        body: JSON.stringify({ phone }),
      })
      const data = await response.json()
      setMessage({ ok: response.ok, text: data.message || (response.ok ? 'تم الحفظ' : 'تعذر الحفظ') })
    } catch {
      setMessage({ ok: false, text: 'تعذر الاتصال بالخادم' })
    } finally { setBusy(false) }
  }

  useEffect(() => {
    if (user?.user_type !== 'doctor') return
    fetch('/api/doctors/me', { headers: authHeaders() }).then(res => res.ok ? res.json() : null).then(data => setAvailability(data?.doctor?.availability || [])).catch(() => {})
  }, [user?.user_type])

  const saveDoctorProfile = async event => {
    event.preventDefault()
    setBusy(true)
    try {
      const response = await fetch('/api/doctors/me', { method: 'PUT', headers: authHeaders(), body: JSON.stringify({ ...doctorProfile, clinic_locations: clinicLocations }) })
      const data = await response.json()
      setMessage({ ok: response.ok, text: data.message || (response.ok ? 'تم تحديث الملف المهني' : 'تعذر تحديث الملف المهني') })
    } catch { setMessage({ ok: false, text: 'تعذر الاتصال بالخادم' }) } finally { setBusy(false) }
  }

  const uploadDoctorImage = async event => {
    const image = event.target.files?.[0]
    if (!image) return
    const formData = new FormData()
    formData.append('image', image)
    setProfileImage('uploading')
    try {
      const response = await fetch('/api/doctors/me/profile-image', { method: 'POST', headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }, body: formData })
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || 'تعذر رفع الصورة')
      setProfileImage(data.profile_image_url)
      setMessage({ ok: true, text: 'تم تحديث صورة الطبيب' })
    } catch (error) { setMessage({ ok: false, text: error.message }); setProfileImage(null) }
  }

  const changePassword = async event => {
    event.preventDefault()
    if (passwords.new_password.length < 8) {
      setMessage({ ok: false, text: 'كلمة المرور الجديدة يجب أن تكون 8 أحرف على الأقل' })
      return
    }
    if (passwords.new_password !== passwords.confirmation) {
      setMessage({ ok: false, text: 'تأكيد كلمة المرور غير مطابق' })
      return
    }
    setBusy(true)
    setMessage(null)
    try {
      const response = await fetch('/api/auth/change-password', {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({
          current_password: passwords.current_password,
          new_password: passwords.new_password,
        }),
      })
      const data = await response.json()
      setMessage({ ok: response.ok, text: data.message || 'تعذر تغيير كلمة المرور' })
      if (response.ok) setPasswords({ current_password: '', new_password: '', confirmation: '' })
    } catch {
      setMessage({ ok: false, text: 'تعذر الاتصال بالخادم' })
    } finally { setBusy(false) }
  }

  return (
    <div dir="rtl" className="min-h-screen bg-gray-50 py-8">
      <div className="mx-auto max-w-3xl px-4">
        <button onClick={() => navigate(-1)} className="mb-5 flex items-center gap-2 text-sm text-gray-500 hover:text-blue-600">
          <ArrowRight className="h-4 w-4" /> العودة
        </button>
        <div className="mb-6 flex items-center gap-3">
          <div className="rounded-2xl bg-blue-600 p-3 text-white"><UserRound className="h-6 w-6" /></div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">إعدادات الحساب</h1>
            <p className="text-sm text-gray-500">تعديل رقم الهاتف وتأمين حسابك</p>
          </div>
        </div>
        {message && <div className={`mb-5 rounded-xl border p-3 text-sm ${message.ok ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : 'border-red-200 bg-red-50 text-red-700'}`}>{message.text}</div>}
        {user?.user_type === 'doctor' && <div className="mb-5 grid gap-5 md:grid-cols-2">
          <form onSubmit={saveDoctorProfile} className="rounded-2xl border border-blue-100 bg-blue-50/50 p-5 shadow-sm md:col-span-2">
            <h2 className="mb-4 flex items-center gap-2 font-bold text-gray-800"><Stethoscope className="h-5 w-5 text-blue-600" /> الملف المهني للطبيب</h2>
            <div className="grid gap-3 md:grid-cols-4"><label className="text-sm text-gray-600">التخصص<input value={doctorProfile.specialization} onChange={e => setDoctorProfile(p => ({ ...p, specialization: e.target.value }))} className="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2.5" /></label><label className="text-sm text-gray-600">اسم العيادة<input value={doctorProfile.clinic_name} onChange={e => setDoctorProfile(p => ({ ...p, clinic_name: e.target.value }))} className="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2.5" /></label><label className="text-sm text-gray-600 md:col-span-2">عنوان العيادة<input value={doctorProfile.clinic_address} onChange={e => setDoctorProfile(p => ({ ...p, clinic_address: e.target.value }))} className="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2.5" /></label></div>
            <div className="mt-4"><p className="mb-2 text-sm font-semibold text-gray-700">عيادات إضافية</p>{clinicLocations.map((clinic, index) => <div key={index} className="mb-2 flex gap-2"><input value={clinic.name || ''} onChange={e => setClinicLocations(list => list.map((item, i) => i === index ? { ...item, name: e.target.value } : item))} placeholder="اسم العيادة" className="w-1/3 rounded-xl border border-gray-200 px-3 py-2" /><input value={clinic.address || ''} onChange={e => setClinicLocations(list => list.map((item, i) => i === index ? { ...item, address: e.target.value } : item))} placeholder="العنوان ومواعيد التواجد" className="flex-1 rounded-xl border border-gray-200 px-3 py-2" /><button type="button" onClick={() => setClinicLocations(list => list.filter((_, i) => i !== index))} className="rounded-xl px-3 text-red-600">حذف</button></div>)}<button type="button" onClick={() => setClinicLocations(list => [...list, { name: '', address: '', phone: '' }])} className="rounded-xl border border-blue-200 px-3 py-2 text-sm text-blue-700">+ إضافة عيادة</button></div>
            <label className="mt-4 block text-sm font-semibold text-gray-700">صورة الطبيب<input type="file" accept=".jpg,.jpeg,.png,.webp" onChange={uploadDoctorImage} className="mt-2 block w-full text-sm" />{profileImage === 'uploading' && <span className="text-xs text-blue-600">جارٍ الرفع...</span>}{profileImage && profileImage !== 'uploading' && <img src={profileImage} alt="صورة الطبيب" className="mt-2 h-16 w-16 rounded-full object-cover" />}</label>
            <button disabled={busy} className="mt-4 flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white"><Save className="h-4 w-4" /> حفظ الملف المهني</button>
          </form>
          <div className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm md:col-span-2"><h2 className="mb-3 flex items-center gap-2 font-bold text-gray-800"><Clock3 className="h-5 w-5 text-blue-600" /> ساعات العمل</h2><p className="text-sm text-gray-500">إدارة جدول التواجد متاحة عبر API الطبيب، وسيتم توسيعها في واجهة الجدول الأسبوعي التالية.</p>{availability.length > 0 && <div className="mt-3 flex flex-wrap gap-2">{availability.map(slot => <span key={slot.id} className="rounded-full bg-blue-50 px-3 py-1 text-xs text-blue-700">{slot.day_of_week}: {slot.start_time} - {slot.end_time}</span>)}</div>}</div>
        </div>}
        {user?.active_roles?.length > 1 && <div className="mb-5 rounded-2xl border border-indigo-100 bg-indigo-50 p-5"><h2 className="mb-3 font-bold text-indigo-950">التبديل بين الأدوار</h2><div className="flex flex-wrap gap-2">{user.active_roles.map(role => <button key={role} onClick={async () => { const result = await switchRole(role); if (result.success) window.location.reload() }} className={`rounded-xl px-3 py-2 text-sm font-semibold ${user.user_type === role ? 'bg-indigo-600 text-white' : 'bg-white text-indigo-700'}`}>{({ patient: 'مستخدم/مريض', doctor: 'طبيب', nurse: 'تمريض', pharmacy: 'صيدلية', lab: 'معمل', radiology_center: 'مركز أشعة', hospital: 'مستشفى' }[role] || role)}</button>)}</div></div>}
        <div className="grid gap-5 md:grid-cols-2">
          <form onSubmit={savePhone} className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
            <h2 className="mb-4 flex items-center gap-2 font-bold text-gray-800"><Phone className="h-5 w-5 text-blue-600" /> رقم الهاتف</h2>
            <label className="text-sm text-gray-600">رقم الهاتف
              <input type="tel" value={phone} onChange={e => setPhone(e.target.value)} className="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2.5 outline-none focus:border-blue-500" required />
            </label>
            <button disabled={busy} className="mt-5 flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60"><Save className="h-4 w-4" /> حفظ الرقم</button>
          </form>
          <form onSubmit={changePassword} className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
            <h2 className="mb-4 flex items-center gap-2 font-bold text-gray-800"><LockKeyhole className="h-5 w-5 text-blue-600" /> تغيير كلمة المرور</h2>
            {[
              ['current_password', 'كلمة المرور الحالية'],
              ['new_password', 'كلمة المرور الجديدة'],
              ['confirmation', 'تأكيد كلمة المرور الجديدة'],
            ].map(([key, label]) => <label key={key} className="mb-3 block text-sm text-gray-600">{label}
              <input type="password" value={passwords[key]} onChange={e => setPasswords(p => ({ ...p, [key]: e.target.value }))} className="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2.5 outline-none focus:border-blue-500" required />
            </label>)}
            <button disabled={busy} className="mt-1 flex items-center gap-2 rounded-xl bg-slate-800 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-900 disabled:opacity-60"><LockKeyhole className="h-4 w-4" /> تغيير كلمة المرور</button>
          </form>
        </div>
        <div className="mt-5 rounded-2xl border border-red-100 bg-red-50 p-5"><button type="button" onClick={async () => { await logout(); navigate('/login', { replace: true }) }} className="flex items-center gap-2 rounded-xl bg-red-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-red-700"><LogOut className="h-4 w-4" /> تسجيل الخروج</button></div>
      </div>
    </div>
  )
}