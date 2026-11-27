import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { lazy, Suspense, useState } from 'react'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
const DashboardPage = lazy(() => import('./pages/DashboardPage'))
const DoctorsPage = lazy(() => import('./pages/DoctorsPage'))
const ServicesPage = lazy(() => import('./pages/ServicesPage'))
const BloodBankPage = lazy(() => import('./pages/BloodBankPage'))
const EmergencyPage = lazy(() => import('./pages/EmergencyPage'))
const MedicalRecordPage = lazy(() => import('./pages/MedicalRecordPage'))
const AppointmentsPage = lazy(() => import('./pages/AppointmentsPage'))
const PrescriptionsPage = lazy(() => import('./pages/PrescriptionsPage'))
const AIAssistantPage = lazy(() => import('./pages/AIAssistantPage'))
const MedicationTrackingPage = lazy(() => import('./pages/MedicationTrackingPage'))
const FamilyHealthPage = lazy(() => import('./pages/FamilyHealthPage'))
const AdminDashboardPage = lazy(() => import('./pages/AdminDashboardPage'))
const LabRequestsPage = lazy(() => import('./pages/LabRequestsPage'))
const RadiologyRequestsPage = lazy(() => import('./pages/RadiologyRequestsPage'))
const MedicationOrderPage = lazy(() => import('./pages/MedicationOrderPage'))
const HospitalsPage = lazy(() => import('./pages/HospitalsPage'))
const DoctorProfilePage = lazy(() => import('./pages/DoctorProfilePage'))
const PendingApprovalPage = lazy(() => import('./pages/PendingApprovalPage'))
const VaccinationPage = lazy(() => import('./pages/VaccinationPage'))
const SymptomCheckerPage = lazy(() => import('./pages/SymptomCheckerPage'))
const ClinicalSummaryPage = lazy(() => import('./pages/ClinicalSummaryPage'))
const MedicalReportPage = lazy(() => import('./pages/MedicalReportPage'))
const PublicMedicalRecordPage = lazy(() => import('./pages/PublicMedicalRecordPage'))
const PharmaciesPage = lazy(() => import('./pages/PharmaciesPage'))
const LabsDirectoryPage = lazy(() => import('./pages/LabsDirectoryPage'))
const RadiologyCentersPage = lazy(() => import('./pages/RadiologyCentersPage'))
const HealthcareDirectoryPage = lazy(() => import('./pages/HealthcareDirectoryPage'))
const AccountSettingsPage = lazy(() => import('./pages/AccountSettingsPage'))
const NursingDashboardPage = lazy(() => import('./pages/NursingDashboardPage'))
const ConsultationsPage = lazy(() => import('./pages/ConsultationsPage'))
const DoctorPatientsPage = lazy(() => import('./pages/DoctorPatientsPage'))
import FloatingAIChat from './components/FloatingAIChat'
import ConnectivityBanner from './components/ConnectivityBanner'
import SplashScreen from './components/SplashScreen'
import { NotificationProvider } from './contexts/NotificationContext'
import './App.css'

const ADMIN_ROLES = ['admin', 'super_admin']
const PROFESSIONAL_ROLES = ['doctor', 'pharmacy', 'lab', 'radiology_center', 'hospital', 'nurse', 'blood_bank']

// ── Loading spinner ────────────────────────────────────────────────────────────
function Spinner() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600" />
    </div>
  )
}

// ── Redirect logged-in users away from auth pages ─────────────────────────────
function PublicRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <Spinner />
  if (!user) return children
  return <Navigate to={getDashboardPath(user)} replace />
}

// ── Require login ──────────────────────────────────────────────────────────────
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <Spinner />
  if (!user) return <Navigate to="/login" replace />
  return children
}

// ── Require specific roles — redirect others to their own dashboard ────────────
function RoleRoute({ children, roles }) {
  const { user, loading } = useAuth()
  if (loading) return <Spinner />
  if (!user) return <Navigate to="/login" replace />
  if (!roles.includes(user.user_type)) return <Navigate to={getDashboardPath(user)} replace />
  return children
}

// ── Determine the home dashboard path for a given user ────────────────────────
function getDashboardPath(user) {
  if (!user) return '/login'
  if (ADMIN_ROLES.includes(user.user_type)) return '/admin'
  return '/dashboard'
}

function AppContent() {
  const [splash, setSplash] = useState(true)
  const { isAuthenticated } = useAuth()

  if (splash) return <SplashScreen onDone={() => setSplash(false)} />

  return (
    <div className={`min-h-screen min-w-0 bg-slate-50 ${isAuthenticated ? 'lg:pl-72' : ''}`}>
      <ConnectivityBanner />
      <Navbar />
      <main className="min-w-0 pb-20 lg:pb-0">
        <Suspense fallback={<Spinner />}>
          <Routes>
          {/* ── العامة ── */}
          <Route path="/" element={<HomePage />} />
          <Route path="/doctors" element={<DoctorsPage />} />
          <Route path="/doctors/:id" element={<DoctorProfilePage />} />
          <Route path="/services" element={<ServicesPage />} />
          <Route path="/blood-bank" element={<BloodBankPage />} />
          <Route path="/emergency" element={<EmergencyPage />} />
          <Route path="/hospitals" element={<HealthcareDirectoryPage />} />
          <Route path="/directory" element={<HealthcareDirectoryPage />} />
          <Route path="/ai-assistant" element={<AIAssistantPage />} />
          <Route path="/consultations" element={<ProtectedRoute><ConsultationsPage /></ProtectedRoute>} />
          <Route path="/consultations/:id" element={<ProtectedRoute><ConsultationsPage /></ProtectedRoute>} />
          <Route path="/doctor/patients" element={<RoleRoute roles={['doctor']}><DoctorPatientsPage /></RoleRoute>} />
          <Route path="/pharmacies" element={<PharmaciesPage />} />
          <Route path="/labs-directory" element={<LabsDirectoryPage />} />
          <Route path="/radiology-centers" element={<RadiologyCentersPage />} />
          <Route path="/public-record/:token" element={<PublicMedicalRecordPage />} />

          {/* ── المصادقة (عامة فقط) ── */}
          <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />

          {/* ── صفحة انتظار الاعتماد (عامة — المهنيون لا يحصلون على token حتى الاعتماد) ── */}
          <Route path="/pending" element={<PendingApprovalPage />} />

          {/* ── لوحة المريض والمزودين ── */}
          <Route
            path="/dashboard"
            element={
              <RoleRoute roles={['patient', ...PROFESSIONAL_ROLES]}>
                <DashboardPage />
              </RoleRoute>
            }
          />

          {/* ── لوحة الإدارة (مدير ومدير النظام فقط) ── */}
          <Route
            path="/admin"
            element={
              <RoleRoute roles={ADMIN_ROLES}>
                <AdminDashboardPage />
              </RoleRoute>
            }
          />

          {/* ── صفحات المريض ── */}
          <Route path="/medical-record" element={<RoleRoute roles={['patient']}><MedicalRecordPage /></RoleRoute>} />
          <Route path="/clinical-summary" element={<RoleRoute roles={['patient']}><ClinicalSummaryPage /></RoleRoute>} />
          <Route path="/medical-record/report" element={<RoleRoute roles={['patient']}><MedicalReportPage /></RoleRoute>} />
          <Route path="/family-health" element={<RoleRoute roles={['patient']}><FamilyHealthPage /></RoleRoute>} />
          <Route path="/account-settings" element={<ProtectedRoute><AccountSettingsPage /></ProtectedRoute>} />
          <Route path="/vaccinations" element={<RoleRoute roles={['patient']}><VaccinationPage /></RoleRoute>} />
          <Route path="/symptom-checker" element={<SymptomCheckerPage />} />
          <Route path="/nursing" element={<RoleRoute roles={['patient', 'doctor', 'nurse']}><NursingDashboardPage /></RoleRoute>} />
          <Route path="/medication-orders" element={<RoleRoute roles={['patient', 'pharmacy']}><MedicationOrderPage /></RoleRoute>} />
          <Route path="/medications" element={<RoleRoute roles={['patient', 'doctor', 'pharmacy']}><MedicationTrackingPage /></RoleRoute>} />

          {/* ── صفحات مشتركة (مرضى + مزودو الخدمة) ── */}
          <Route
            path="/appointments"
            element={
              <RoleRoute roles={['patient', 'doctor', 'lab', 'radiology_center', 'hospital', 'nurse', 'blood_bank']}>
                <AppointmentsPage />
              </RoleRoute>
            }
          />
          <Route
            path="/prescriptions"
            element={
              <RoleRoute roles={['patient', 'doctor', 'pharmacy']}>
                <PrescriptionsPage />
              </RoleRoute>
            }
          />
          <Route
            path="/lab-requests"
            element={
              <RoleRoute roles={['patient', 'doctor', 'lab', 'hospital']}>
                <LabRequestsPage />
              </RoleRoute>
            }
          />
          <Route
            path="/radiology"
            element={
              <RoleRoute roles={['patient', 'doctor', 'radiology_center', 'hospital']}>
                <RadiologyRequestsPage />
              </RoleRoute>
            }
          />
          <Route
            path="/nursing"
            element={
              <RoleRoute roles={['patient', 'nurse']}>
                <NursingDashboardPage />
              </RoleRoute>
            }
          />

          {/* ── توجيه افتراضي ── */}
          <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </main>
      <Footer />
      <FloatingAIChat />
    </div>
  )
}

export default function App() {
  if (import.meta.env.VITE_SAHTY_STATIC_PREVIEW === 'true') {
    return (
      <main dir="rtl" lang="ar" className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-teal-50 px-5 py-10 text-slate-800 sm:px-8">
        <section className="mx-auto flex min-h-[80vh] max-w-4xl flex-col justify-center">
          <div className="mb-8 flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-sky-700 text-xl font-bold text-white">ص</div>
            <div>
              <p className="text-2xl font-bold text-sky-950">صحتي</p>
              <p className="text-sm text-slate-500">منصة الرعاية الصحية</p>
            </div>
          </div>

          <div className="rounded-3xl border border-amber-300 bg-amber-50 p-5 text-amber-950 shadow-sm sm:p-7" role="status">
            <p className="mb-2 font-bold">نسخة معاينة للواجهة فقط</p>
            <p className="leading-7">هذه المعاينة لا تتصل بخادم التطبيق أو قاعدة البيانات. تسجيل الدخول والبحث والسجلات والطلبات والملفات والخدمات الطبية غير مفعّلة هنا.</p>
            <p className="mt-3 font-semibold">لا تُدخل معلومات شخصية أو صحية، ولا تعتمد على هذه الصفحة للرعاية أو الطوارئ.</p>
          </div>

          <h1 className="mt-10 text-3xl font-extrabold leading-tight text-slate-950 sm:text-5xl">رعاية صحية مترابطة، في مكان واحد.</h1>
          <p className="mt-4 max-w-2xl text-lg leading-8 text-slate-600">تستعرض هذه الصفحة فكرة المنصة وتجربة الواجهة. تفعيل الوظائف يتطلب إعداد الخادم وقاعدة البيانات والتخزين ومراجعة ضوابط الخصوصية قبل الإطلاق.</p>

          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            {[
              ['الخدمات والمواعيد', 'عرض تصميمي فقط؛ لا توجد حجوزات أو بيانات حية.'],
              ['السجلات الصحية', 'غير متاحة حتى ربط قاعدة البيانات والتخزين الآمن.'],
              ['الدليل الصحي', 'لا يجري البحث عن أطباء أو مراكز في هذه المعاينة.'],
              ['المساعدة الذكية', 'غير متصلة؛ لا تقدّم تشخيصًا أو نصيحة طبية.'],
            ].map(([title, detail]) => (
              <article key={title} className="rounded-2xl border border-slate-200 bg-white/90 p-5 shadow-sm">
                <h2 className="font-bold text-slate-900">{title}</h2>
                <p className="mt-2 text-sm leading-6 text-slate-600">{detail}</p>
              </article>
            ))}
          </div>

          <p className="mt-8 text-sm text-slate-500">للطوارئ اتصل بخدمات الطوارئ المحلية. هذه الصفحة ليست خدمة طبية.</p>
        </section>
      </main>
    )
  }

  return (
    <Router>
      <NotificationProvider>
        <AuthProvider>
          <AppContent />
        </AuthProvider>
      </NotificationProvider>
    </Router>
  )
}
