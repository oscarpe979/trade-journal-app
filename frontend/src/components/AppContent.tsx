import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import SignUpPage from '../pages/SignUpPage';
import LoginPage from '../pages/LoginPage';
import DashboardPage from '../pages/DashboardPage';
import CalendarPage from '../pages/CalendarPage';
import ReportsPage from '../pages/ReportsPage';
import { useAuth } from '../contexts/AuthContext';
import ProtectedRoute from './ProtectedRoute';
import SideNavbar from './SideNavbar';

function AppContent() {
  const location = useLocation();
  const { isAuthenticated } = useAuth();
  const showNavbar = isAuthenticated && !['/login', '/signup'].includes(location.pathname);

  return (
    <div className={showNavbar ? "app-container" : ""}>
      {showNavbar && <SideNavbar />}
      <main className={showNavbar ? "main-content" : ""}>
        <Routes>
          <Route path="/signup" element={<SignUpPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<AuthRedirect />} />
          <Route path="/dashboard"element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route path="/calendar"element={
              <ProtectedRoute>
                <CalendarPage />
              </ProtectedRoute>
            }
          />
          <Route path="/reports"element={
              <ProtectedRoute>
                <ReportsPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
    </div>
  );
}

const AuthRedirect: React.FC = () => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Navigate to="/dashboard" /> : <Navigate to="/login" />;
};

export default AppContent;