import { Box, CircularProgress } from '@mui/material'
import { Navigate, Route, Routes } from 'react-router-dom'

import { AuthProvider, useAuth } from './state/auth'
import AnalyticsPage from './pages/AnalyticsPage'
import DoctorDashboard from './pages/DoctorDashboard'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import PatientDashboard from './pages/PatientDashboard'

function FullPageLoader() {
  return (
    <Box sx={{ height: '70vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <CircularProgress />
    </Box>
  )
}

function Protected({ children, role }: { children: JSX.Element; role?: 'doctor' | 'patient' }) {
  const { me, token, loadingMe } = useAuth()

  if (!token) return <Navigate to="/login" replace />
  if (loadingMe || !me) return <FullPageLoader />
  if (role && me.role !== role) return <Navigate to="/" replace />

  return children
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/patient"
          element={
            <Protected role="patient">
              <PatientDashboard />
            </Protected>
          }
        />
        <Route
          path="/doctor"
          element={
            <Protected role="doctor">
              <DoctorDashboard />
            </Protected>
          }
        />
        <Route
          path="/analytics"
          element={
            <Protected role="doctor">
              <AnalyticsPage />
            </Protected>
          }
        />
      </Routes>
    </AuthProvider>
  )
}
