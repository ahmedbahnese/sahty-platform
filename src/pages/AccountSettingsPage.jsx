import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { ArrowRight, LockKeyhole, Phone, Save, UserRound } from 'lucide-react'

const authHeaders = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('token')}`,
})

export default function AccountSettingsPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [phone, setPhone] = useState(user?.profile?.phone || '')
  const [passwords, setPasswords] = useState({ current_password: '', new_password: '', confirmation: '' })
  const [message, setMessage] = useState(null)
  const [busy, setBusy] = useState(false)

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
      </div>
    </div>
  )
}