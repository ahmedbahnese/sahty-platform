import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Heart, Loader2, Lock } from 'lucide-react'

export default function PublicMedicalRecordPage() {
  const { token } = useParams()
  const [record, setRecord] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`/api/medical-record/public/${token}`)
      .then(response => response.ok
        ? response.json()
        : response.json().then(data => { throw new Error(data.message || 'الرابط غير صالح') }))
      .then(setRecord)
      .catch(error => setError(error.message))
      .finally(() => setLoading(false))
  }, [token])

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center"><Loader2 className="w-10 h-10 animate-spin text-blue-500" /></div>
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50" dir="rtl">
        <div className="text-center space-y-3">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
            <Lock className="w-8 h-8 text-red-500" />
          </div>
          <p className="text-gray-700 font-medium">{error}</p>
          <p className="text-gray-400 text-sm">هذا الرابط غير صالح أو منتهي الصلاحية</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 text-center">
        <p className="text-xs text-amber-700 font-medium flex items-center justify-center gap-1.5">
          <Lock className="w-3.5 h-3.5" /> رابط تعريف محدود للقراءة فقط
        </p>
      </div>
      <main className="max-w-md mx-auto px-4 py-12">
        <section className="bg-gradient-to-l from-blue-600 to-blue-800 rounded-2xl p-7 text-white text-center shadow-lg">
          <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Heart className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold">{record?.patient?.name || 'مريض'}</h1>
          <p className="text-blue-100 text-sm mt-2">الاسم فقط متاح عبر هذا الرابط</p>
        </section>
        <p className="text-center text-xs text-gray-400 mt-8">
          لا يعرض هذا الرابط أي تشخيص أو دواء أو نتيجة طبية.
        </p>
      </main>
    </div>
  )
}