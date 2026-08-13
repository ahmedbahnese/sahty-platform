import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState } from 'react'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import DoctorsPage from './pages/DoctorsPage'
import ServicesPage from './pages/ServicesPage'
import BloodBankPage from './pages/BloodBankPage'
import EmergencyPage from './pages/EmergencyPage'
import MedicalRecordPage from './pages/MedicalRecordPage'
import AppointmentsPage from './pages/AppointmentsPage'
import PrescriptionsPage from './pages/PrescriptionsPage'
import AIAssistantPage from './pages/AIAssistantPage'
import MedicationTrackingPage from './pages/MedicationTrackingPage'
import FamilyHealthPage from './pages/FamilyHealthPage'
import AdminDashboardPage from './pages/AdminDashboardPage'
import LabRequestsPage from './pages/LabRequestsPage'
import RadiologyRequestsPage from './pages/RadiologyRequestsPage'
import MedicationOrderPage from './pages/MedicationOrderPage'
import HospitalsPage from './pages/HospitalsPage'
import DoctorProfilePage from './pages/DoctorProfilePage'
import PendingApprovalPage from './pages/PendingApprovalPage'
import VaccinationPage from './pages/VaccinationPage'
import SymptomCheckerPage from './pages/SymptomCheckerPage'
import ClinicalSummaryPage from './pages/ClinicalSummaryPage'
import MedicalReportPage from './pages/MedicalReportPage'
import PublicMedicalRecordPage from './pages/PublicMedicalRecordPage'
import PharmaciesPage from './pages/PharmaciesPage'
import LabsDirectoryPage from './pages/LabsDirectoryPage'
import RadiologyCentersPage from './pages/RadiologyCentersPage'
import HealthcareDirectoryPage from './pages/HealthcareDirectoryPage'
import AccountSettingsPage from './pages/AccountSettingsPage'
import NursingDashboardPage from './pages/NursingDashboardPage'
import FloatingAIChat from './components/FloatingAIChat'
import SplashScreen from './components/SplashScreen'
import './App.css'

const ADMIN_ROLES = ['admin', 'super_admin']
const PROFESSIONAL_ROLES = ['doctor', 'pharmacy', 'lab', 'radiology_center', 'hospital', 'nurse']

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

  if (splash) return <SplashScreen onDone={() => setSplash(false)} />

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="flex-1">
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
          <Route path="/medications" element={<RoleRoute roles={['patient', 'pharmacy']}><MedicationTrackingPage /></RoleRoute>} />
          <Route path="/medication-orders" element={<RoleRoute roles={['patient', 'pharmacy']}><MedicationOrderPage /></RoleRoute>} />

          {/* ── صفحات مشتركة (مرضى + مزودو الخدمة) ── */}
          <Route
            path="/appointments"
            element={
              <RoleRoute roles={['patient', 'doctor', 'lab', 'radiology_center', 'hospital', 'nurse']}>
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
      </main>
      <Footer />
      <FloatingAIChat />
    </div>
  )
}

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  )
}
