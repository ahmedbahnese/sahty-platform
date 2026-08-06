import { useState, useEffect, useRef, useCallback } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog'
import {
  User, Calendar, Phone, Droplets, Activity, AlertTriangle,
  Pill, FlaskConical, Radio, Stethoscope, Printer, ChevronRight,
  Syringe, Building2, ClipboardList, FileText, Heart, Loader2,
  CheckCircle2, Clock, XCircle, ArrowLeft, Shield, Microscope,
  Thermometer, Eye, Brain, Bone, Wind
} from 'lucide-react'

const API = '/api/medical-record'

// ── Helpers ──────────────────────────────────────────────────────────────────

function authHeaders(token) {
  return { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
}

function calcAge(dob) {
  if (!dob) return null
  const today = new Date()
  const birth = new Date(dob)
  let age = today.getFullYear() - birth.getFullYear()
  if (today.getMonth() < birth.getMonth() ||
    (today.getMonth() === birth.getMonth() && today.getDate() < birth.getDate())) age--
  return age
}

function fmtDate(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleDateString('ar-EG', { year: 'numeric', month: 'long', day: 'numeric', calendar: 'gregory' })
  } catch { return iso }
}

function fmtDateTime(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleDateString('ar-EG', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', calendar: 'gregory' })
  } catch { return iso }
}

// ── Label maps ────────────────────────────────────────────────────────────────

const GENDER = { male: 'ذكر', female: 'أنثى' }
const DISEASE_STATUS = { active: 'نشط', chronic: 'مزمن', resolved: 'شُفي' }
const DISEASE_STATUS_COLOR = {
  active: 'bg-blue-100 text-blue-800',
  chronic: 'bg-purple-100 text-purple-800',
  resolved: 'bg-green-100 text-green-800'
}
const SEVERITY = { mild: 'خفيف', moderate: 'متوسط', severe: 'شديد' }
const SEVERITY_COLOR = {
  mild: 'bg-yellow-100 text-yellow-800',
  moderate: 'bg-orange-100 text-orange-800',
  severe: 'bg-red-100 text-red-800'
}
const LAB_STATUS = { normal: 'طبيعي', abnormal: 'غير طبيعي', critical: 'حرج', pending: 'قيد الانتظار' }
const LAB_STATUS_COLOR = {
  normal: 'bg-green-100 text-green-800',
  abnormal: 'bg-orange-100 text-orange-800',
  critical: 'bg-red-100 text-red-800',
  pending: 'bg-gray-100 text-gray-600'
}
const SCAN_TYPE = { xray: 'أشعة X', mri: 'رنين مغناطيسي', ct: 'أشعة مقطعية', ultrasound: 'موجات صوتية', pet: 'PET Scan', mammo: 'ماموجرام' }
const APPT_TYPE = { in_person: 'حضوري', telemedicine: 'عن بُعد' }

// ── Section anchor nav ────────────────────────────────────────────────────────

const SECTIONS = [
  { id: 'patient-info',  label: 'بيانات المريض',       icon: User },
  { id: 'history',       label: 'التاريخ المرضي',       icon: Activity },
  { id: 'surgeries',     label: 'العمليات الجراحية',    icon: Syringe },
  { id: 'allergies',     label: 'الحساسية',              icon: AlertTriangle },
  { id: 'medications',   label: 'الأدوية الحالية',       icon: Pill },
  { id: 'labs',          label: 'التحاليل المخبرية',    icon: FlaskConical },
  { id: 'radiology',     label: 'الأشعة والتصوير',      icon: Microscope },
  { id: 'visits',        label: 'زيارات الطبيب',         icon: Stethoscope },
]

// ── Sub-components ────────────────────────────────────────────────────────────

function SectionCard({ id, icon: Icon, title, count, children, className = '' }) {
  return (
    <section id={id} className={`scroll-mt-20 ${className}`}>
      <Card className="shadow-sm border-0 ring-1 ring-gray-200">
        <CardHeader className="bg-gradient-to-l from-blue-50 to-white border-b border-gray-100 py-4">
          <CardTitle className="flex items-center gap-3 text-gray-800 text-base font-semibold">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
              <Icon size={16} className="text-white" />
            </div>
            <span>{title}</span>
            {count !== undefined && (
              <Badge variant="secondary" className="mr-auto text-xs">{count}</Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4">{children}</CardContent>
      </Card>
    </section>
  )
}

function InfoGrid({ items }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
      {items.map(({ label, value }) => (
        <div key={label} className="flex flex-col gap-1">
          <span className="text-xs font-medium text-gray-500">{label}</span>
          <span className="text-sm font-semibold text-gray-800">{value || '—'}</span>
        </div>
      ))}
    </div>
  )
}

function EmptyState({ message }) {
  return (
    <div className="text-center py-8 text-gray-400">
      <ClipboardList size={32} className="mx-auto mb-2 opacity-40" />
      <p className="text-sm">{message}</p>
    </div>
  )
}

// ── Encounter Modal ───────────────────────────────────────────────────────────

function EncounterModal({ appointmentId, token, open, onClose }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!open || !appointmentId) return
    setLoading(true)
    setData(null)
    fetch(`${API}/visits/${appointmentId}`, { headers: authHeaders(token) })
      .then(r => r.json())
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [open, appointmentId, token])

  const vitalSigns = data?.medical_record?.vital_signs || {}
  const doc = data?.doctor

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto" dir="rtl">
        <DialogHeader className="border-b pb-3">
          <DialogTitle className="flex items-center gap-2 text-base">
            <Stethoscope size={18} className="text-blue-600" />
            تفاصيل الزيارة الطبية
          </DialogTitle>
        </DialogHeader>

        {loading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="animate-spin text-blue-600" size={32} />
          </div>
        )}

        {data && !loading && (
          <div className="space-y-5 py-2">
            {/* Doctor + Date */}
            <div className="grid grid-cols-2 gap-4 p-4 bg-blue-50 rounded-xl">
              <div>
                <p className="text-xs text-gray-500">الطبيب</p>
                <p className="font-semibold text-gray-800">{doc?.name || '—'}</p>
                <p className="text-sm text-gray-500">{doc?.specialization || ''}</p>
                {doc?.sub_specialization && <p className="text-xs text-gray-400">{doc.sub_specialization}</p>}
              </div>
              <div>
                <p className="text-xs text-gray-500">تاريخ الزيارة</p>
                <p className="font-semibold text-gray-800">{fmtDateTime(data.appointment_date)}</p>
                <p className="text-sm text-gray-500">{APPT_TYPE[data.appointment_type] || data.appointment_type}</p>
                {doc?.clinic_name && <p className="text-xs text-gray-400">{doc.clinic_name}</p>}
              </div>
            </div>

            {/* Chief Complaint / Reason */}
            {data.reason && (
              <EncounterSection title="الشكوى الرئيسية" icon={<Heart size={14} />}>
                <p className="text-sm text-gray-700 leading-relaxed">{data.reason}</p>
              </EncounterSection>
            )}

            {/* Symptoms / HPI */}
            {(data.symptoms || data.medical_record?.symptoms) && (
              <EncounterSection title="تاريخ المرض الحالي والأعراض" icon={<Activity size={14} />}>
                <p className="text-sm text-gray-700 leading-relaxed">
                  {data.medical_record?.symptoms || data.symptoms}
                </p>
              </EncounterSection>
            )}

            {/* Vital Signs */}
            {Object.keys(vitalSigns).length > 0 && (
              <EncounterSection title="العلامات الحيوية" icon={<Thermometer size={14} />}>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {Object.entries(vitalSigns).map(([key, val]) => (
                    <div key={key} className="bg-gray-50 rounded-lg p-3 text-center">
                      <p className="text-xs text-gray-500 capitalize">{key.replace(/_/g, ' ')}</p>
                      <p className="font-semibold text-gray-800 text-sm">{val}</p>
                    </div>
                  ))}
                </div>
              </EncounterSection>
            )}

            {/* Diagnosis / Assessment */}
            {data.medical_record?.diagnosis && (
              <EncounterSection title="التشخيص والتقييم" icon={<Brain size={14} />}>
                <p className="text-sm text-gray-700 leading-relaxed">{data.medical_record.diagnosis}</p>
              </EncounterSection>
            )}

            {/* Treatment Plan */}
            {data.medical_record?.treatment && (
              <EncounterSection title="خطة العلاج" icon={<Pill size={14} />}>
                <p className="text-sm text-gray-700 leading-relaxed">{data.medical_record.treatment}</p>
              </EncounterSection>
            )}

            {/* Lab Results from encounter */}
            {data.medical_record?.lab_results && Object.keys(data.medical_record.lab_results).length > 0 && (
              <EncounterSection title="نتائج التحاليل المطلوبة" icon={<FlaskConical size={14} />}>
                <div className="space-y-2">
                  {Object.entries(data.medical_record.lab_results).map(([k, v]) => (
                    <div key={k} className="flex justify-between text-sm border-b border-gray-50 pb-1">
                      <span className="text-gray-600">{k}</span>
                      <span className="font-medium text-gray-800">{String(v)}</span>
                    </div>
                  ))}
                </div>
              </EncounterSection>
            )}

            {/* Notes / Follow-up */}
            {data.medical_record?.notes && (
              <EncounterSection title="ملاحظات وخطة المتابعة" icon={<FileText size={14} />}>
                <p className="text-sm text-gray-700 leading-relaxed">{data.medical_record.notes}</p>
              </EncounterSection>
            )}

            {/* Electronic Signature */}
            {doc && (
              <div className="border-t pt-4 flex items-start justify-between">
                <div>
                  <p className="text-xs text-gray-500">التوقيع الإلكتروني</p>
                  <p className="font-semibold text-gray-800 mt-1">{doc.name}</p>
                  <p className="text-xs text-gray-500">{doc.specialization}</p>
                  {doc.license_number && (
                    <p className="text-xs text-gray-400">رقم الترخيص: {doc.license_number}</p>
                  )}
                </div>
                <div className="text-left text-xs text-gray-400">
                  <Shield size={14} className="inline ml-1" />
                  موثّق إلكترونياً
                </div>
              </div>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}

function EncounterSection({ title, icon, children }) {
  return (
    <div className="border border-gray-100 rounded-lg overflow-hidden">
      <div className="bg-gray-50 px-4 py-2 flex items-center gap-2 text-gray-700 text-sm font-medium">
        {icon}
        {title}
      </div>
      <div className="p-4">{children}</div>
    </div>
  )
}

// ── Print Styles ──────────────────────────────────────────────────────────────

const printStyles = `
@page {
  size: A4;
  margin: 18mm 15mm 20mm 15mm;
  @bottom-center {
    content: "صفحة " counter(page) " من " counter(pages);
    font-size: 10px;
    color: #666;
    font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
  }
}
@media print {
  body * { visibility: hidden !important; }
  #clinical-summary-print, #clinical-summary-print * { visibility: visible !important; }
  #clinical-summary-print { position: absolute; top: 0; left: 0; width: 100%; direction: rtl; }
  .no-print { display: none !important; }
  .print-break { page-break-before: always; }
  #print-patient-header { display: block !important; }
  .print-page-break-avoid { page-break-inside: avoid; }
  table { page-break-inside: auto; }
  tr { page-break-inside: avoid; page-break-after: auto; }
  thead { display: table-header-group; }
  tfoot { display: table-footer-group; }
}
`

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function ClinicalSummaryPage() {
  const { token } = useAuth()
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedVisit, setSelectedVisit] = useState(null)
  const [encounterOpen, setEncounterOpen] = useState(false)
  const printRef = useRef()

  useEffect(() => {
    if (!token) return
    fetch(`${API}/clinical-summary`, { headers: authHeaders(token) })
      .then(async r => {
        if (!r.ok) throw new Error((await r.json()).message || 'خطأ في الجلب')
        return r.json()
      })
      .then(setSummary)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [token])

  const handlePrint = useCallback(() => {
    window.print()
  }, [])

  const handleVisitClick = useCallback((visit) => {
    setSelectedVisit(visit.id)
    setEncounterOpen(true)
  }, [])

  // ── Loading ──
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen" dir="rtl">
        <div className="text-center">
          <Loader2 className="animate-spin text-blue-600 mx-auto mb-3" size={40} />
          <p className="text-gray-500">جاري تحميل التقرير الطبي الشامل...</p>
        </div>
      </div>
    )
  }

  // ── Error ──
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen" dir="rtl">
        <div className="text-center text-red-500">
          <XCircle size={40} className="mx-auto mb-3" />
          <p>{error}</p>
        </div>
      </div>
    )
  }

  if (!summary) return null

  const { patient, diseases = [], surgeries = [], allergies = [], current_medications = [],
    lab_tests = [], radiology = [], visits = [] } = summary

  const age = patient.age ?? calcAge(patient.date_of_birth)

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      <style>{printStyles}</style>

      {/* ── Sticky header ── */}
      <div className="sticky top-0 z-30 bg-white border-b border-gray-200 shadow-sm no-print">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center">
              <ClipboardList size={18} className="text-white" />
            </div>
            <div>
              <h1 className="text-base font-bold text-gray-900">التقرير الطبي الشامل</h1>
              <p className="text-xs text-gray-500">Comprehensive Medical Report</p>
            </div>
          </div>
          <Button onClick={handlePrint} className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-sm">
            <Printer size={15} />
            طباعة التقرير
          </Button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-6 flex gap-6">

        {/* ── Sidebar nav ── */}
        <aside className="no-print hidden lg:block w-52 flex-shrink-0">
          <div className="sticky top-24 space-y-1">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide px-2 mb-3">الأقسام</p>
            {SECTIONS.map(({ id, label, icon: Icon }) => (
              <a
                key={id}
                href={`#${id}`}
                className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-600 hover:bg-blue-50 hover:text-blue-700 transition-colors"
              >
                <Icon size={14} />
                {label}
              </a>
            ))}
          </div>
        </aside>

        {/* ── Main content ── */}
        <div id="clinical-summary-print" className="flex-1 space-y-5 min-w-0">

          {/* ══ 1. Patient Information ══ */}
          <SectionCard id="patient-info" icon={User} title="بيانات المريض">
            <div className="flex items-start gap-4 mb-5">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center flex-shrink-0">
                <User size={28} className="text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  {patient.first_name} {patient.last_name}
                </h2>
                <p className="text-gray-500 text-sm">
                  {GENDER[patient.gender] || patient.gender}
                  {age ? ` · ${age} سنة` : ''}
                </p>
              </div>
            </div>
            <InfoGrid items={[
              { label: 'رقم الملف (MRN)', value: patient.national_id },
              { label: 'تاريخ الميلاد', value: fmtDate(patient.date_of_birth) },
              { label: 'العمر', value: age ? `${age} سنة` : null },
              { label: 'الجنس', value: GENDER[patient.gender] || patient.gender },
              { label: 'فصيلة الدم', value: patient.blood_type },
              { label: 'رقم الجوال', value: patient.phone },
              { label: 'البريد الإلكتروني', value: patient.email },
              { label: 'التأمين الصحي', value: patient.insurance_provider },
            ]} />
          </SectionCard>

          {/* ══ 2. Past Medical History ══ */}
          <SectionCard id="history" icon={Activity} title="التاريخ المرضي السابق" count={diseases.length}>
            {diseases.length === 0 ? (
              <EmptyState message="لا توجد أمراض مسجلة" />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-100 text-gray-500 text-xs">
                      <th className="text-right py-2 font-medium">المرض</th>
                      <th className="text-right py-2 font-medium">تاريخ التشخيص</th>
                      <th className="text-right py-2 font-medium">الحالة</th>
                      <th className="text-right py-2 font-medium">الطبيب المعالج</th>
                      <th className="text-right py-2 font-medium">ملاحظات</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {diseases.map(d => (
                      <tr key={d.id} className="hover:bg-gray-50 transition-colors">
                        <td className="py-3 font-medium text-gray-800">
                          {d.name}
                          {d.icd_code && <span className="text-xs text-gray-400 mr-1">({d.icd_code})</span>}
                        </td>
                        <td className="py-3 text-gray-600">{fmtDate(d.diagnosis_date)}</td>
                        <td className="py-3">
                          <Badge className={`text-xs ${DISEASE_STATUS_COLOR[d.status] || 'bg-gray-100 text-gray-600'}`}>
                            {DISEASE_STATUS[d.status] || d.status}
                          </Badge>
                        </td>
                        <td className="py-3 text-gray-600">{d.treating_doctor || '—'}</td>
                        <td className="py-3 text-gray-500 max-w-xs truncate">{d.notes || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </SectionCard>

          {/* ══ 3. Past Surgical History ══ */}
          <SectionCard id="surgeries" icon={Syringe} title="التاريخ الجراحي السابق" count={surgeries.length}>
            {surgeries.length === 0 ? (
              <EmptyState message="لا توجد عمليات جراحية مسجلة" />
            ) : (
              <div className="space-y-3">
                {surgeries.map(s => (
                  <div key={s.id} className="border border-gray-100 rounded-xl p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h4 className="font-semibold text-gray-800">{s.name}</h4>
                        {s.surgery_type && <p className="text-xs text-gray-500">{s.surgery_type}</p>}
                      </div>
                      <span className="text-sm text-gray-500">{fmtDate(s.surgery_date)}</span>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
                      {s.hospital && (
                        <div>
                          <p className="text-xs text-gray-400">المستشفى</p>
                          <p className="text-gray-700">{s.hospital}</p>
                        </div>
                      )}
                      {s.surgeon && (
                        <div>
                          <p className="text-xs text-gray-400">الجراح</p>
                          <p className="text-gray-700">{s.surgeon}</p>
                        </div>
                      )}
                      {s.outcome && (
                        <div>
                          <p className="text-xs text-gray-400">النتيجة</p>
                          <p className="text-gray-700">{s.outcome}</p>
                        </div>
                      )}
                    </div>
                    {(s.post_op_notes || s.complications) && (
                      <div className="mt-3 pt-3 border-t border-gray-100 text-sm text-gray-600">
                        {s.complications && <p><span className="font-medium">المضاعفات:</span> {s.complications}</p>}
                        {s.post_op_notes && <p><span className="font-medium">ملاحظات ما بعد العملية:</span> {s.post_op_notes}</p>}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </SectionCard>

          {/* ══ 4. Allergies ══ */}
          <SectionCard id="allergies" icon={AlertTriangle} title="الحساسية" count={allergies.length}>
            {allergies.length === 0 ? (
              <EmptyState message="لا توجد حساسية مسجلة" />
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {allergies.map(a => (
                  <div key={a.id} className={`rounded-xl p-4 border ${a.severity === 'severe' ? 'border-red-200 bg-red-50' : a.severity === 'moderate' ? 'border-orange-200 bg-orange-50' : 'border-yellow-200 bg-yellow-50'}`}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-gray-800">{a.allergen}</span>
                      {a.severity && (
                        <Badge className={`text-xs ${SEVERITY_COLOR[a.severity] || 'bg-gray-100 text-gray-600'}`}>
                          {SEVERITY[a.severity] || a.severity}
                        </Badge>
                      )}
                    </div>
                    {a.reaction && <p className="text-sm text-gray-600"><span className="font-medium">التفاعل:</span> {a.reaction}</p>}
                    {a.notes && <p className="text-xs text-gray-500 mt-1">{a.notes}</p>}
                  </div>
                ))}
              </div>
            )}
          </SectionCard>

          {/* ══ 5. Current Medications ══ */}
          <SectionCard id="medications" icon={Pill} title="الأدوية الحالية" count={current_medications.length}>
            {current_medications.length === 0 ? (
              <EmptyState message="لا توجد أدوية حالية مسجلة" />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-100 text-gray-500 text-xs">
                      <th className="text-right py-2 font-medium">الدواء</th>
                      <th className="text-right py-2 font-medium">الجرعة</th>
                      <th className="text-right py-2 font-medium">التكرار</th>
                      <th className="text-right py-2 font-medium">تاريخ البداية</th>
                      <th className="text-right py-2 font-medium">تاريخ النهاية</th>
                      <th className="text-right py-2 font-medium">الطبيب الواصف</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {current_medications.map(m => (
                      <tr key={m.id} className="hover:bg-gray-50 transition-colors">
                        <td className="py-3">
                          <p className="font-medium text-gray-800">{m.name}</p>
                          {m.generic_name && <p className="text-xs text-gray-400">{m.generic_name}</p>}
                        </td>
                        <td className="py-3 text-gray-700">{m.dosage} {m.form || ''}</td>
                        <td className="py-3 text-gray-700">{m.frequency}</td>
                        <td className="py-3 text-gray-600">{fmtDate(m.start_date)}</td>
                        <td className="py-3 text-gray-600">{fmtDate(m.end_date)}</td>
                        <td className="py-3 text-gray-600">—</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </SectionCard>

          {/* ══ 6. Lab Results Timeline ══ */}
          <SectionCard id="labs" icon={FlaskConical} title="نتائج التحاليل المخبرية" count={lab_tests.length}>
            {lab_tests.length === 0 ? (
              <EmptyState message="لا توجد تحاليل مكتملة مسجلة" />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-100 text-gray-500 text-xs">
                      <th className="text-right py-2 font-medium">اسم التحليل</th>
                      <th className="text-right py-2 font-medium">التاريخ</th>
                      <th className="text-right py-2 font-medium">النتيجة</th>
                      <th className="text-right py-2 font-medium">المرجع</th>
                      <th className="text-right py-2 font-medium">الحالة</th>
                      <th className="text-right py-2 font-medium">الطبيب الطالب</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {lab_tests.map(l => (
                      <tr key={l.id} className="hover:bg-gray-50 transition-colors">
                        <td className="py-3">
                          <p className="font-medium text-gray-800">{l.test_name}</p>
                          {l.test_category && <p className="text-xs text-gray-400">{l.test_category}</p>}
                        </td>
                        <td className="py-3 text-gray-600">{fmtDate(l.test_date)}</td>
                        <td className="py-3 font-medium text-gray-800">
                          {l.result_value} {l.unit || ''}
                        </td>
                        <td className="py-3 text-gray-500">{l.reference_range || '—'}</td>
                        <td className="py-3">
                          <Badge className={`text-xs ${LAB_STATUS_COLOR[l.status] || 'bg-gray-100 text-gray-600'}`}>
                            {LAB_STATUS[l.status] || l.status}
                          </Badge>
                        </td>
                        <td className="py-3 text-gray-600">{l.ordering_doctor || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </SectionCard>

          {/* ══ 7. Radiology Timeline ══ */}
          <SectionCard id="radiology" icon={Microscope} title="الأشعة والتصوير الطبي" count={radiology.length}>
            {radiology.length === 0 ? (
              <EmptyState message="لا توجد أشعة مكتملة مسجلة" />
            ) : (
              <div className="space-y-4">
                {radiology.map(r => (
                  <div key={r.id} className="border border-gray-100 rounded-xl p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant="outline" className="text-xs">
                            {SCAN_TYPE[r.scan_type] || r.scan_type}
                          </Badge>
                          {r.body_part && (
                            <span className="text-sm text-gray-600">{r.body_part}</span>
                          )}
                        </div>
                        {r.facility && <p className="text-xs text-gray-400">{r.facility}</p>}
                      </div>
                      <span className="text-sm text-gray-500 flex-shrink-0">{fmtDate(r.scan_date)}</span>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                      {r.radiologist && (
                        <div>
                          <p className="text-xs text-gray-400">الأخصائي</p>
                          <p className="text-gray-700">{r.radiologist}</p>
                        </div>
                      )}
                      {r.ordering_doctor && (
                        <div>
                          <p className="text-xs text-gray-400">الطبيب الطالب</p>
                          <p className="text-gray-700">{r.ordering_doctor}</p>
                        </div>
                      )}
                    </div>
                    {r.findings && (
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <p className="text-xs text-gray-400 mb-1">النتائج</p>
                        <p className="text-sm text-gray-700 leading-relaxed">{r.findings}</p>
                      </div>
                    )}
                    {r.impression && (
                      <div className="mt-2">
                        <p className="text-xs text-gray-400 mb-1">الانطباع</p>
                        <p className="text-sm text-gray-700 leading-relaxed">{r.impression}</p>
                      </div>
                    )}
                    {r.recommendation && (
                      <div className="mt-2">
                        <p className="text-xs text-gray-400 mb-1">التوصية</p>
                        <p className="text-sm text-gray-700">{r.recommendation}</p>
                      </div>
                    )}
                    {r.attachment_data && (
                      <div className="mt-3">
                        <img
                          src={r.attachment_data}
                          alt="صورة الأشعة"
                          className="max-h-48 rounded-lg object-contain border border-gray-200"
                        />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </SectionCard>

          {/* ══ 8. Doctor Visits Timeline ══ */}
          <SectionCard id="visits" icon={Stethoscope} title="زيارات الطبيب" count={visits.length}>
            {visits.length === 0 ? (
              <EmptyState message="لا توجد زيارات طبية مكتملة مسجلة" />
            ) : (
              <div className="space-y-3">
                {visits.map(v => (
                  <button
                    key={v.id}
                    onClick={() => handleVisitClick(v)}
                    className="w-full text-right border border-gray-100 rounded-xl p-4 hover:bg-blue-50 hover:border-blue-200 transition-all group"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center flex-shrink-0">
                          <Stethoscope size={18} className="text-blue-600" />
                        </div>
                        <div>
                          <p className="font-semibold text-gray-800 group-hover:text-blue-700">
                            {v.doctor?.name || 'طبيب'}
                          </p>
                          <p className="text-sm text-gray-500">{v.doctor?.specialization || ''}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant="outline" className="text-xs">
                              {APPT_TYPE[v.appointment_type] || v.appointment_type}
                            </Badge>
                            {v.reason && (
                              <span className="text-xs text-gray-400 truncate max-w-xs">{v.reason}</span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 flex-shrink-0">
                        <div className="text-left">
                          <p className="text-sm font-medium text-gray-700">{fmtDate(v.appointment_date)}</p>
                          <p className="text-xs text-gray-400">{v.doctor?.clinic_name || ''}</p>
                        </div>
                        <ChevronRight size={16} className="text-gray-300 group-hover:text-blue-500 transition-colors" />
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </SectionCard>

          {/* ══ Print footer ══ */}
          <div className="hidden print:block border-t-2 border-gray-300 pt-4 mt-8">
            <div className="flex items-start justify-between gap-4">
              <div className="text-xs text-gray-500">
                <p className="font-semibold text-gray-700 mb-1">التقرير الطبي الشامل — منصة صحتي</p>
                <p>تاريخ الطباعة: {new Date().toLocaleDateString('ar-EG', { year: 'numeric', month: 'long', day: 'numeric' })}</p>
                <p className="mt-1 text-gray-400">هذا التقرير سري وخاص بالمريض — لا يُستخدم إلا للأغراض الطبية</p>
              </div>
              {/* QR code pointing to the clinical summary page */}
              <div className="flex flex-col items-center gap-1">
                <img
                  src={`https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=${encodeURIComponent(window.location.origin + '/clinical-summary')}&bgcolor=ffffff&color=0f2444&margin=4`}
                  alt="QR التقرير الطبي"
                  className="w-24 h-24 border border-gray-200 rounded"
                />
                <p className="text-xs text-gray-400">افتح التقرير الرقمي</p>
              </div>
            </div>
          </div>

        </div>{/* end main */}
      </div>{/* end flex */}

      {/* ── Encounter Modal ── */}
      <EncounterModal
        appointmentId={selectedVisit}
        token={token}
        open={encounterOpen}
        onClose={() => setEncounterOpen(false)}
      />
    </div>
  )
}
