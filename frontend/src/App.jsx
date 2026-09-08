import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastContainer, setToastFn } from './components/ui';
import { useState, useEffect } from 'react';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import DashboardPage from './pages/DashboardPage';
import MemberDashboardPage from './pages/MemberDashboardPage';
import ProjectsPage from './pages/ProjectsPage';
import ProjectDetailPage from './pages/ProjectDetailPage';
import './components/ui.css';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 32, marginBottom: 12 }}>T</div>
        <div style={{ color: 'var(--text-2)', fontSize: 13 }}>Loading…</div>
      </div>
    </div>
  );
  if (!user) return <Navigate to="/login" replace />;
  return <Layout>{children}</Layout>;
}

function RoleHomeRedirect() {
  const { user } = useAuth();
  return <Navigate to={user?.role === 'admin' ? '/manager-dashboard' : '/member-dashboard'} replace />;
}

function ToastSetup() {
  const [, rerender] = useState(0);
  useEffect(() => {
    setToastFn((msg, type) => {
      // handled by ToastContainer
    });
  }, []);
  return null;
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastContainer />
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/dashboard" element={<ProtectedRoute><RoleHomeRedirect /></ProtectedRoute>} />
          <Route path="/manager-dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/member-dashboard" element={<ProtectedRoute><MemberDashboardPage /></ProtectedRoute>} />
          <Route path="/projects" element={<ProtectedRoute><ProjectsPage /></ProtectedRoute>} />
          <Route path="/projects/:id" element={<ProtectedRoute><ProjectDetailPage /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
