import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import {
  Heart, User, Droplets, AlertTriangle, Pill, FlaskConical,
  RadioTower, Syringe, Activity, Loader2, Lock, History
} from 'lucide-react'

const severityLabels = { mild: 'خفيف', moderate: 'متوسط', severe: 'شديد' }
const statusLabels   = { active: 'نشط', chronic: 'مزمن', resolved: 'شُفي', normal: 'طبيعي', abnormal: 'غير طبيعي', critical: 'حرج' }
const scanTypeLabels = { xray: 'أشعة X', mri: 'رنين مغناطيسي', ct: 'أشعة مقطعية', ultrasound: 'موجات صوتية', pet: 'PET Scan', mammo: 'ماموجرام' }

function Section({ title, icon: Icon, color, children }) {
  const colorMap = {
    red: 'text-red-700 border-red-200 bg-red-50',
    blue: 'text-blue-700 border-blue-200 bg-blue-50',
    green: 'text-green-700 border-green-200 bg-green-50',
    purple: 'text-purple-700 border-purple-200 bg-purple-50',
    indigo: 'text-indigo-700 border-indigo-200 bg-indigo-50',
    teal: 'text-teal-700 border-teal-200 bg-teal-50',
    gray: 'text-gray-700 border-gray-200 bg-gray-50',
  }
  const cls = colorMap[color] || colorMap.blue
  return (
    <div className="mb-5">
      <div className={`flex items-center gap-2 mb-3 px-4 py-2 rounded-xl border ${cls}`}>
        <Icon className="w-4 h-4" />
        <h2 className="text-sm font-bold">{title}</h2>
        <span className="mr-auto text-xs opacity-60">للقراءة فقط</span>
      </div>
      <div className="px-1">{children}</div>
    </div>
  )
}

export default function PublicMedicalRecordPage() {
  const { token } = useParams()
  const [report, setReport]   = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  useEffect(() => {
    fetch(`/api/medical-record/public/${token}`)
      .then(r => r.ok ? r.json() : r.json().then(d => { throw new Error(d.message) }))
      .then(setReport)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [token])

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <Loader2 className="w-10 h-10 animate-spin text-blue-500" />
    </div>
  )
  if (error) return (
    <div className="min-h-screen flex items-center justify-center" dir="rtl">
      <div className="text-center space-y-3">
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
          <Lock className="w-8 h-8 text-red-500" />
        </div>
        <p className="text-gray-700 font-medium">{error}</p>
        <p className="text-gray-400 text-sm">هذا الرابط غير صالح أو منتهي الصلاحية</p>
      </div>
    </div>
  )
  if (!report) return null

  const { patient, allergies, active_diseases, current_medications, vaccinations, recent_lab_tests, recent_radiology } = report

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      {/* شريط للقراءة فقط */}
      <div className="bg-amber-50 border-b border-amber-200 px-4 py-2 text-center">
        <p className="text-xs text-amber-700 font-medium flex items-center justify-center gap-1.5">
          <Lock className="w-3.5 h-3.5" />
          هذه نسخة للقراءة فقط — تُعرض عبر رمز QR طوارئ
        </p>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-6">
        {/* رأس الصفحة */}
        <div className="bg-gradient-to-l from-blue-600 to-blue-800 rounded-2xl p-5 mb-6 text-white">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <Heart className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-lg font-bold">{patient?.name}</h1>
              <p className="text-blue-100 text-sm">
                {patient?.age ? `${patient.age} سنة` : ''}{patient?.gender === 'male' ? ' — ذكر' : patient?.gender === 'female' ? ' — أنثى' : ''}
              </p>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            {patient?.blood_type && (
              <span className="bg-white/20 border border-white/30 rounded-lg px-3 py-1.5 text-sm font-bold flex items-center gap-1">
                <Droplets className="w-3.5 h-3.5" /> {patient.blood_type}
              </span>
            )}
            {patient?.height && <span className="bg-white/15 rounded-lg px-3 py-1.5 text-sm">{patient.height} سم</span>}
            {patient?.weight && <span className="bg-white/15 rounded-lg px-3 py-1.5 text-sm">{patient.weight} كجم</span>}
          </div>
          <p className="text-blue-200 text-xs mt-3">
            تقرير بتاريخ: {new Date(report.generated_at).toLocaleString('ar-EG')}
          </p>
        </div>

        {/* الحساسية — أول شيء في الطوارئ */}
        {allergies?.length > 0 && (
          <div className="bg-red-50 border-2 border-red-300 rounded-2xl p-4 mb-5">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle className="w-5 h-5 text-red-600" />
              <h2 className="font-bold text-red-800">⚠ تحذير: حساسية</h2>
            </div>
            <div className="space-y-2">
              {allergies.map((a, i) => (
                <div key={i} className="bg-white rounded-xl px-4 py-2.5 border border-red-200 flex items-center justify-between">
                  <span className="font-semibold text-red-800">{a.allergen}</span>
                  {a.severity && <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-lg">{severityLabels[a.severity]}</span>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* الأمراض */}
        {active_diseases?.length > 0 && (
          <Section title="الأمراض والتشخيصات" icon={Activity} color="purple">
            <div className="space-y-2">
              {active_diseases.map((d, i) => (
                <div key={i} className="bg-white border border-gray-100 rounded-xl px-4 py-2.5 flex items-center justify-between shadow-sm">
                  <div>
                    <p className="font-medium text-gray-800 text-sm">{d.name}</p>
                    {d.diagnosis_date && <p className="text-xs text-gray-400">تشخيص: {d.diagnosis_date}</p>}
                  </div>
                  <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-lg">{statusLabels[d.status] || d.status}</span>
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* الأدوية */}
        {current_medications?.length > 0 && (
          <Section title="الأدوية الحالية" icon={Pill} color="green">
            <div className="space-y-2">
              {current_medications.map((m, i) => (
                <div key={i} className="bg-white border border-gray-100 rounded-xl px-4 py-2.5 shadow-sm">
                  <p className="font-medium text-gray-800 text-sm">{m.name}</p>
                  <p className="text-xs text-gray-500">{m.dosage} — {m.frequency}</p>
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* التحاليل */}
        {recent_lab_tests?.length > 0 && (
          <Section title="آخر التحاليل" icon={FlaskConical} color="indigo">
            <div className="overflow-x-auto">
              <table className="w-full text-xs border-collapse">
                <thead>
                  <tr className="bg-indigo-50 text-indigo-700">
                    <th className="text-right px-3 py-2">التحليل</th>
                    <th className="text-right px-3 py-2">النتيجة</th>
                    <th className="text-right px-3 py-2">التاريخ</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {recent_lab_tests.slice(0, 10).map((t, i) => (
                    <tr key={i} className="bg-white">
                      <td className="px-3 py-2 font-medium">{t.test_name}</td>
                      <td className="px-3 py-2">{t.result_value} {t.unit}</td>
                      <td className="px-3 py-2 text-gray-400">{t.test_date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Section>
        )}

        {/* الأشعة */}
        {recent_radiology?.length > 0 && (
          <Section title="الأشعة والتصوير" icon={RadioTower} color="indigo">
            <div className="space-y-2">
              {recent_radiology.slice(0, 5).map((r, i) => (
                <div key={i} className="bg-white border border-gray-100 rounded-xl px-4 py-2.5 shadow-sm">
                  <div className="flex items-center justify-between">
                    <p className="font-medium text-gray-800 text-sm">{scanTypeLabels[r.scan_type] || r.scan_type} — {r.body_part}</p>
                    <p className="text-xs text-gray-400">{r.scan_date}</p>
                  </div>
                  {r.impression && <p className="text-xs text-gray-600 mt-1">{r.impression}</p>}
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* التطعيمات */}
        {vaccinations?.length > 0 && (
          <Section title="التطعيمات" icon={Syringe} color="teal">
            <div className="flex flex-wrap gap-2">
              {vaccinations.map((v, i) => (
                <span key={i} className="bg-white border border-teal-100 rounded-xl px-3 py-1.5 text-xs font-medium text-gray-700 shadow-sm">
                  {v.vaccine_name} {v.date_given ? `(${v.date_given})` : ''}
                </span>
              ))}
            </div>
          </Section>
        )}

        <div className="text-center text-xs text-gray-400 mt-8 pb-4">
          <p>هذا التقرير للقراءة فقط — منصة صحتك في أمان</p>
        </div>
      </div>
    </div>
  )
}
