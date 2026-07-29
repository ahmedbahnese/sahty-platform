import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
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
import './App.css'

// مكون للحماية - يتطلب تسجيل الدخول
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }
  
  return user ? children : <Navigate to="/login" />
}

// مكون للصفحات العامة - إعادة توجيه إذا كان مسجل دخول
function PublicRoute({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }
  
  return user ? <Navigate to="/dashboard" /> : children
}

function AppContent() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="flex-1">
        <Routes>
          {/* الصفحات العامة */}
          <Route path="/" element={<HomePage />} />
          <Route path="/doctors" element={<DoctorsPage />} />
          <Route path="/services" element={<ServicesPage />} />
          <Route path="/blood-bank" element={<BloodBankPage />} />
          <Route path="/emergency" element={<EmergencyPage />} />
          <Route path="/ai-assistant" element={<AIAssistantPage />} />
          
          {/* صفحات المصادقة */}
          <Route 
            path="/login" 
            element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            } 
          />
          <Route 
            path="/register" 
            element={
              <PublicRoute>
                <RegisterPage />
              </PublicRoute>
            } 
          />
          
          {/* الصفحات المحمية */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/medical-record" 
            element={
              <ProtectedRoute>
                <MedicalRecordPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/appointments" 
            element={
              <ProtectedRoute>
                <AppointmentsPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/prescriptions" 
            element={
              <ProtectedRoute>
                <PrescriptionsPage />
              </ProtectedRoute>
            } 
          />
          
          {/* صفحات الذكاء الاصطناعي والصحة */}
          <Route
            path="/medications"
            element={
              <ProtectedRoute>
                <MedicationTrackingPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/family-health"
            element={
              <ProtectedRoute>
                <FamilyHealthPage />
              </ProtectedRoute>
            }
          />

          {/* إعادة توجيه للصفحة الرئيسية */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  )
}

export default App

