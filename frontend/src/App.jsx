import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Layout from './components/layout/Layout'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import CancerPage from './pages/CancerPage'
import ChatbotPage from './pages/ChatbotPage'
import PeriodPage from './pages/PeriodPage'

function PrivateRoute({ children }) {
  const { user } = useAuth()
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<PrivateRoute><DashboardPage /></PrivateRoute>} />
          <Route path="/cancer" element={<PrivateRoute><CancerPage /></PrivateRoute>} />
          <Route path="/chatbot" element={<PrivateRoute><ChatbotPage /></PrivateRoute>} />
          <Route path="/period" element={<PrivateRoute><PeriodPage /></PrivateRoute>} />
        </Route>
      </Routes>
    </AuthProvider>
  )
}
