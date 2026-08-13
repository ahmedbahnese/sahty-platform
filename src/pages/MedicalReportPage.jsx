import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import {
  ArrowRight, Printer, User, Droplets, Ruler, Weight, Activity,
  AlertTriangle, Pill, FlaskConical, RadioTower, Syringe, History,
  Heart, FileText, Loader2, QrCode
} from 'lucide-react'

const API = '/api/medical-record'

const severityLabels = { mild: 'خفيف', moderate: 'متوسط', severe: 'شديد' }
const statusLabels   = { active: 'نشط', chronic: 'مزمن', resolved: 'شُفي', normal: 'طبيعي', abnormal: 'غير طبيعي', critical: 'حرج' }
const scanTypeLabels = { xray: 'أشعة X', mri: 'رنين مغناطيسي', ct: 'أشعة مقطعية', ultrasound: 'موجات صوتية', pet: 'PET Scan', mammo: 'ماموجرام' }

function Section({ title, icon: Icon, color = 'blue', children }) {
  return (
    <div className="mb-6 print:mb-4 break-inside-avoid">
      <div className={`flex items-center gap-2 mb-3 pb-2 border-b-2 border-${color}-200`}>
        <Icon className={`w-5 h-5 text-${color}-600`} />
        <h2 className={`text-base font-bold text-${color}-800`}>{title}</h2>
      </div>
      {children}
    </div>
  )
}

export default function MedicalReportPage() {
  const { token } = useAuth()
  const navigate  = useNavigate()
  const [report, setReport]   = useState(null)
  const [loading, setLoading] = useState(true)
  const [qrUrl, setQrUrl]     = useState(null)

  useEffect(() => {
    const headers = { Authorization: `Bearer ${token}` }
    Promise.all([
      fetch(`${API}/report`, { headers }).then(r => r.json()),
      fetch(`${API}/public-token`, { headers }).then(r => r.json()),
    ]).then(([rep, tok]) => {
      setReport(rep)
      if (tok.token) {
        const base = window.location.origin
        setQrUrl(`${base}/public-record/${tok.token}`)
      }
    }).finally(() => setLoading(false))
  }, [token])

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <Loader2 className="w-10 h-10 animate-spin text-blue-500" />
    </div>
  )
  if (!report) return (
    <div className="min-h-screen flex items-center justify-center text-gray-500">
      تعذّر تحميل التقرير
    </div>
  )

  const { patient, allergies, active_diseases, current_medications, vaccinations, recent_lab_tests, recent_radiology, surgeries = [], medical_history } = report

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      {/* شريط أدوات — مخفي عند الطباعة */}
      <div className="print:hidden sticky top-0 z-10 bg-white border-b shadow-sm px-4 py-3 flex items-center justify-between">
        <button onClick={() => navigate('/medical-record')} className="flex items-center gap-2 text-gray-600 hover:text-blue-600 text-sm font-medium">
          <ArrowRight className="w-4 h-4" /> العودة للملف الطبي
        </button>
        <div className="flex items-center gap-3">
          <h1 className="text-base font-bold text-gray-800 hidden sm:block">التقرير الطبي الشامل</h1>
          <button
            onClick={() => window.print()}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl text-sm font-medium"
          >
            <Printer className="w-4 h-4" /> طباعة / PDF
          </button>
        </div>
      </div>

      {/* محتوى التقرير */}
      <div className="max-w-4xl mx-auto px-4 py-8 print:py-0 print:px-0 print:max-w-full">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 print:rounded-none print:shadow-none print:border-0 print:p-6">

          {/* رأس التقرير */}
          <div className="flex items-start justify-between mb-8 pb-6 border-b-2 border-blue-100">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className="w-12 h-12 rounded-xl bg-blue-600 flex items-center justify-center">
                  <Heart className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">التقرير الطبي الشامل</h1>
                  <p className="text-sm text-gray-500">منصة صحتك في أمان</p>
                </div>
              </div>
              <p className="text-xs text-gray-400 mt-2">
                تاريخ الإنشاء: {new Date(report.generated_at).toLocaleString('ar-EG')}
              </p>
            </div>
            {/* QR Code */}
            {qrUrl && (
              <div className="text-center">
                <div className="w-24 h-24 bg-gray-100 rounded-xl flex items-center justify-center print:block">
                  <img
                    src={`https://api.qrserver.com/v1/create-qr-code/?size=96x96&data=${encodeURIComponent(qrUrl)}`}
                    alt="QR"
                    className="w-24 h-24 rounded-lg"
                  />
                </div>
                <p className="text-xs text-gray-400 mt-1">امسح للقراءة</p>
              </div>
            )}
          </div>

          {/* بيانات المريض */}
          <Section title="بيانات المريض" icon={User} color="blue">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
              {[
                ['الاسم الكامل', patient?.name],
                ['العمر',         patient?.age ? `${patient.age} سنة` : '—'],
                ['الجنس',         patient?.gender === 'male' ? 'ذكر' : patient?.gender === 'female' ? 'أنثى' : '—'],
                ['فصيلة الدم',    patient?.blood_type || '—'],
                ['الطول',         patient?.height ? `${patient.height} سم` : '—'],
                ['الوزن',         patient?.weight ? `${patient.weight} كجم` : '—'],
                ['مؤشر الكتلة BMI', patient?.bmi || '—'],
                ['الهاتف', patient?.phone || '—'],
                ['العنوان', patient?.address || '—'],
                ['طوارئ', patient?.emergency_contact_phone || '—'],
              ].map(([label, val]) => (
                <div key={label} className="bg-gray-50 rounded-xl p-3">
                  <p className="text-xs text-gray-400 mb-0.5">{label}</p>
                  <p className="font-semibold text-gray-800">{val}</p>
                </div>
              ))}
            </div>
          </Section>

          {surgeries.length > 0 && (
            <Section title="التاريخ الجراحي" icon={Activity} color="orange">
              <div className="space-y-2">
                {surgeries.map((s, i) => (
                  <div key={i} className="rounded-xl bg-orange-50 border border-orange-100 p-3 text-sm">
                    <div className="flex justify-between gap-3">
                      <span className="font-semibold">{s.name}</span>
                      <span className="text-xs text-gray-500">{s.surgery_date || '—'}</span>
                    </div>
                    {(s.hospital || s.surgeon || s.outcome) && (
                      <p className="mt-1 text-xs text-gray-600">
                        {[s.hospital, s.surgeon, s.outcome].filter(Boolean).join(' · ')}
                      </p>
                    )}
                    {s.notes && <p className="mt-1 text-xs text-gray-600">{s.notes}</p>}
                  </div>
                ))}
              </div>
            </Section>
          )}

          {/* الحساسية */}
          {allergies?.length > 0 && (
            <Section title="الحساسية" icon={AlertTriangle} color="red">
              <div className="flex flex-wrap gap-2">
                {allergies.map((a, i) => (
                  <span key={i} className="inline-flex items-center gap-1 bg-red-50 text-red-800 border border-red-200 rounded-xl px-3 py-1.5 text-sm font-medium">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    {a.allergen} — {severityLabels[a.severity] || a.severity}
                  </span>
                ))}
              </div>
            </Section>
          )}

          {/* الأمراض النشطة */}
          {active_diseases?.length > 0 && (
            <Section title="الأمراض والتشخيصات" icon={Activity} color="purple">
              <div className="space-y-2">
                {active_diseases.map((d, i) => (
                  <div key={i} className="flex items-center justify-between bg-purple-50 rounded-xl px-4 py-2.5 border border-purple-100">
                    <div>
                      <span className="font-medium text-gray-800 text-sm">{d.name}</span>
                      {d.treating_doctor && <span className="text-xs text-gray-500 mr-3">د. {d.treating_doctor}</span>}
                      {d.diagnosis_date   && <span className="text-xs text-gray-400 mr-2">{d.diagnosis_date}</span>}
                    </div>
                    <div className="flex gap-2">
                      {d.status   && <span className="text-xs bg-white border rounded-lg px-2 py-0.5 text-gray-700">{statusLabels[d.status] || d.status}</span>}
                      {d.severity && <span className="text-xs bg-white border rounded-lg px-2 py-0.5 text-gray-700">{severityLabels[d.severity]}</span>}
                    </div>
                  </div>
                ))}
              </div>
            </Section>
          )}

          {/* الأدوية الحالية */}
          {current_medications?.length > 0 && (
            <Section title="الأدوية الحالية" icon={Pill} color="green">
              <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="bg-green-50 text-green-800 text-xs">
                      <th className="text-right px-3 py-2 rounded-r-lg">الدواء</th>
                      <th className="text-right px-3 py-2">الجرعة</th>
                      <th className="text-right px-3 py-2">التكرار</th>
                      <th className="text-right px-3 py-2 rounded-l-lg">من / إلى</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {current_medications.map((m, i) => (
                      <tr key={i} className="hover:bg-gray-50">
                        <td className="px-3 py-2 font-medium">{m.name}</td>
                        <td className="px-3 py-2 text-gray-600">{m.dosage}</td>
                        <td className="px-3 py-2 text-gray-600">{m.frequency}</td>
                        <td className="px-3 py-2 text-gray-500 text-xs">{m.start_date} {m.end_date ? `← ${m.end_date}` : ''}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Section>
          )}

          {/* التحاليل الأخيرة */}
          {recent_lab_tests?.length > 0 && (
            <Section title="آخر التحاليل المخبرية" icon={FlaskConical} color="indigo">
              <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse">
                  <thead>
                    <tr className="bg-indigo-50 text-indigo-800 text-xs">
                      <th className="text-right px-3 py-2 rounded-r-lg">التحليل</th>
                      <th className="text-right px-3 py-2">التاريخ</th>
                      <th className="text-right px-3 py-2">النتيجة</th>
                      <th className="text-right px-3 py-2">المجال الطبيعي</th>
                      <th className="text-right px-3 py-2 rounded-l-lg">الحالة</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {recent_lab_tests.slice(0, 15).map((t, i) => (
                      <tr key={i} className={`hover:bg-gray-50 ${t.status === 'critical' ? 'bg-red-50' : t.status === 'abnormal' ? 'bg-orange-50' : ''}`}>
                        <td className="px-3 py-2 font-medium">{t.test_name}</td>
                        <td className="px-3 py-2 text-gray-500 text-xs">{t.test_date}</td>
                        <td className="px-3 py-2">{t.result_value} {t.unit}</td>
                        <td className="px-3 py-2 text-gray-500 text-xs">{t.reference_range}</td>
                        <td className="px-3 py-2">
                          <span className={`text-xs px-2 py-0.5 rounded-lg ${t.status === 'normal' ? 'bg-green-100 text-green-700' : t.status === 'abnormal' ? 'bg-orange-100 text-orange-700' : t.status === 'critical' ? 'bg-red-100 text-red-700' : 'bg-gray-100'}`}>
                            {statusLabels[t.status] || t.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Section>
          )}

          {/* الأشعة */}
          {recent_radiology?.length > 0 && (
            <Section title="الأشعة والتصوير الطبي" icon={RadioTower} color="indigo">
              <div className="space-y-3">
                {recent_radiology.slice(0, 8).map((r, i) => (
                  <div key={i} className="bg-indigo-50 rounded-xl p-3 border border-indigo-100">
                    <div className="flex items-start justify-between gap-3 mb-1.5">
                      <div>
                        <span className="font-medium text-sm text-gray-800">{scanTypeLabels[r.scan_type] || r.scan_type} — {r.body_part}</span>
                        {r.facility && <span className="text-xs text-gray-500 mr-2">({r.facility})</span>}
                      </div>
                      <span className="text-xs text-gray-400 whitespace-nowrap">{r.scan_date}</span>
                    </div>
                    {r.impression && <p className="text-xs text-gray-700 bg-white rounded-lg px-3 py-2 mt-1"><span className="font-medium">النتيجة:</span> {r.impression}</p>}
                    {r.findings   && !r.impression && <p className="text-xs text-gray-700">{r.findings}</p>}
                  </div>
                ))}
              </div>
            </Section>
          )}

          {/* التطعيمات */}
          {vaccinations?.length > 0 && (
            <Section title="سجل التطعيمات" icon={Syringe} color="teal">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {vaccinations.map((v, i) => (
                  <div key={i} className="bg-teal-50 border border-teal-100 rounded-xl px-3 py-2 text-sm">
                    <p className="font-medium text-gray-800 text-xs">{v.vaccine_name}</p>
                    {v.date_given && <p className="text-xs text-gray-400 mt-0.5">{v.date_given}</p>}
                    {v.provider   && <p className="text-xs text-gray-400">{v.provider}</p>}
                  </div>
                ))}
              </div>
            </Section>
          )}

          {/* التاريخ المرضي */}
          {medical_history && Object.keys(medical_history).some(k => medical_history[k]) && (
            <Section title="التاريخ المرضي العام" icon={History} color="gray">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                {medical_history.smoking_status  && <div className="bg-gray-50 rounded-xl p-3"><p className="text-xs text-gray-400">التدخين</p><p className="font-medium">{medical_history.smoking_status === 'never' ? 'لا يدخن' : medical_history.smoking_status === 'former' ? 'سبق له' : 'مدخن'}</p></div>}
                {medical_history.physical_activity && <div className="bg-gray-50 rounded-xl p-3"><p className="text-xs text-gray-400">النشاط البدني</p><p className="font-medium">{medical_history.physical_activity}</p></div>}
                {medical_history.chronic_conditions && <div className="bg-gray-50 rounded-xl p-3 col-span-full"><p className="text-xs text-gray-400">الأمراض المزمنة</p><p className="font-medium">{medical_history.chronic_conditions}</p></div>}
              </div>
              {medical_history.family_history?.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-semibold text-gray-600 mb-2">التاريخ العائلي:</p>
                  <div className="space-y-1">
                    {medical_history.family_history.map((f, i) => (
                      <div key={i} className="flex gap-3 text-sm text-gray-700 bg-gray-50 rounded-lg px-3 py-1.5">
                        <span className="font-medium">{f.disease}</span>
                        <span className="text-gray-400">{f.relation}</span>
                        {f.notes && <span className="text-gray-500 text-xs">{f.notes}</span>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </Section>
          )}

          {/* تذييل التقرير */}
          <div className="mt-8 pt-4 border-t border-gray-100 text-center text-xs text-gray-400">
            <p>هذا التقرير صادر من منصة <strong>صحتك في أمان</strong> — للأغراض المرجعية فقط</p>
            <p className="mt-1">تاريخ الطباعة: {new Date().toLocaleString('ar-EG')}</p>
          </div>
        </div>
      </div>

      {/* أنماط الطباعة */}
      <style>{`
        @media print {
          body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
          nav, footer, .print\\:hidden { display: none !important; }
          .min-h-screen { min-height: auto; }
          .bg-gray-50 { background: white; }
          .shadow-sm { box-shadow: none; }
        }
      `}</style>
    </div>
  )
}
