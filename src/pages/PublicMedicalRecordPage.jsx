import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Activity, AlertTriangle, FileText, Heart, Loader2, Lock, Pill, RadioTower, Syringe } from 'lucide-react'

const statusLabels = { active: 'نشط', chronic: 'مزمن', resolved: 'شُفي' }
const severityLabels = { mild: 'خفيف', moderate: 'متوسط', severe: 'شديد' }
const scanLabels = { xray: 'أشعة X', mri: 'رنين مغناطيسي', ct: 'أشعة مقطعية', ultrasound: 'موجات صوتية', pet: 'PET Scan', mammo: 'ماموجرام' }

function Section({ title, icon: Icon, children }) {
  return (
    <section className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
      <h2 className="mb-4 flex items-center gap-2 border-b border-gray-100 pb-3 text-base font-bold text-gray-800">
        <Icon className="h-5 w-5 text-blue-600" /> {title}
      </h2>
      {children}
    </section>
  )
}

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

  if (loading) return <div className="flex min-h-screen items-center justify-center"><Loader2 className="h-10 w-10 animate-spin text-blue-500" /></div>
  if (error) return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 p-4" dir="rtl">
      <div className="text-center">
        <Lock className="mx-auto mb-3 h-10 w-10 text-red-500" />
        <p className="font-medium text-gray-700">{error}</p>
        <p className="mt-2 text-sm text-gray-400">هذا الرابط غير صالح أو منتهي الصلاحية</p>
      </div>
    </div>
  )

  const { patient, allergies = [], active_diseases = [], current_medications = [], vaccinations = [], recent_lab_tests = [], recent_radiology = [] } = record
  return (
    <div className="min-h-screen bg-gray-50 px-4 py-6" dir="rtl">
      <div className="mx-auto max-w-4xl space-y-4">
        <div className="rounded-2xl bg-gradient-to-l from-blue-700 to-indigo-700 p-6 text-white shadow-lg">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="mb-3 flex items-center gap-2 text-blue-100"><Heart className="h-5 w-5" /> صحتك في أمان</div>
              <h1 className="text-2xl font-bold">التقرير الطبي الشامل</h1>
              <p className="mt-2 text-sm text-blue-100">للقراءة فقط — تمت مشاركته عبر رمز QR</p>
            </div>
            <FileText className="h-10 w-10 text-blue-200" />
          </div>
          <p className="mt-5 border-t border-white/20 pt-4 text-lg font-semibold">{patient?.name || 'مريض'}</p>
        </div>

        <Section title="بيانات المريض" icon={FileText}>
          <div className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
            {[['العمر', patient?.age ? `${patient.age} سنة` : '—'], ['الجنس', patient?.gender === 'male' ? 'ذكر' : patient?.gender === 'female' ? 'أنثى' : '—'], ['فصيلة الدم', patient?.blood_type || '—'], ['BMI', patient?.bmi || '—']].map(([label, value]) => (
              <div key={label} className="rounded-xl bg-gray-50 p-3"><p className="text-xs text-gray-400">{label}</p><p className="mt-1 font-semibold">{value}</p></div>
            ))}
          </div>
        </Section>

        {allergies.length > 0 && <Section title="الحساسية" icon={AlertTriangle}><div className="flex flex-wrap gap-2">{allergies.map(item => <span key={item.id || item.allergen} className="rounded-full bg-red-50 px-3 py-1.5 text-sm text-red-700">{item.allergen} — {severityLabels[item.severity] || item.severity || 'غير محدد'}</span>)}</div></Section>}
        {active_diseases.length > 0 && <Section title="الأمراض والتشخيصات" icon={Activity}><div className="space-y-2">{active_diseases.map(item => <div key={item.id || item.name} className="rounded-xl bg-purple-50 p-3 text-sm"><span className="font-semibold">{item.name}</span><span className="mr-2 text-gray-500">{statusLabels[item.status] || item.status || ''}</span></div>)}</div></Section>}
        {current_medications.length > 0 && <Section title="الأدوية الحالية" icon={Pill}><div className="space-y-2">{current_medications.map(item => <div key={item.id || item.name} className="rounded-xl bg-green-50 p-3 text-sm"><p className="font-semibold">{item.name}</p><p className="mt-1 text-gray-600">{item.dosage} · {item.frequency}{item.instructions ? ` · ${item.instructions}` : ''}</p></div>)}</div></Section>}
        {recent_lab_tests.length > 0 && <Section title="التحاليل المخبرية" icon={Activity}><div className="space-y-2">{recent_lab_tests.map(item => <div key={item.id || item.test_name} className="flex justify-between gap-3 rounded-xl bg-gray-50 p-3 text-sm"><span className="font-medium">{item.test_name || item.name}</span><span className="text-gray-600">{item.result_value || item.status || '—'}{item.unit ? ` ${item.unit}` : ''}</span></div>)}</div></Section>}
        {recent_radiology.length > 0 && <Section title="الأشعة" icon={RadioTower}><div className="space-y-2">{recent_radiology.map(item => <div key={item.id || item.body_part} className="rounded-xl bg-blue-50 p-3 text-sm"><p className="font-semibold">{scanLabels[item.scan_type] || item.scan_type} — {item.body_part}</p><p className="mt-1 text-gray-600">{item.impression || item.findings || 'لا توجد ملاحظات'}</p></div>)}</div></Section>}
        {vaccinations.length > 0 && <Section title="التطعيمات" icon={Syringe}><div className="flex flex-wrap gap-2">{vaccinations.map(item => <span key={item.id || item.vaccine_name} className="rounded-full bg-amber-50 px-3 py-1.5 text-sm text-amber-800">{item.vaccine_name || item.name}</span>)}</div></Section>}
        <p className="pb-4 text-center text-xs text-gray-400">هذا التقرير للقراءة فقط ولا يسمح بتعديل السجلات الطبية.</p>
      </div>
    </div>
  )
}