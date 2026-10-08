import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider, useApp } from './context/AppContext';
import Layout from './components/Layout';
import SignInPage from './pages/SignInPage';
import StudentDashboardPage from './pages/StudentDashboardPage';
import ResumeReviewPage from './pages/ResumeReviewPage';
import StudentHistoryPage from './pages/StudentHistoryPage';
import PrivacyDataPage from './pages/PrivacyDataPage';
import TrainerDashboardPage from './pages/TrainerDashboardPage';
import AdminConsolePage from './pages/AdminConsolePage';
import AssignmentsPage from './pages/AssignmentsPage';
import LearningPage from './pages/LearningPage';
import CalendarPage from './pages/CalendarPage';
import NotificationsPage from './pages/NotificationsPage';

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { currentUser } = useApp();

  if (!currentUser) {
    return <Navigate to="/login" replace />;
  }

  // If role is specified and user role doesn't match, we allow it with fallback or redirect
  return children;
};

function AppRoutes() {
  const { currentUser } = useApp();

  return (
    <Routes>
      {/* If already signed in and visiting /login, redirect to appropriate dashboard */}
      <Route
        path="/login"
        element={
          currentUser
            ? <Navigate to={
                currentUser.role === 'trainer' ? '/trainer'
                : currentUser.role === 'admin' ? '/admin'
                : '/dashboard'
              } replace />
            : <SignInPage />
        }
      />
      
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={
          currentUser?.role === 'trainer' ? <Navigate to="/trainer" replace />
          : currentUser?.role === 'admin' ? <Navigate to="/admin" replace />
          : <Navigate to="/dashboard" replace />
        } />
        <Route path="dashboard" element={<StudentDashboardPage />} />
        <Route path="resume-review" element={<ResumeReviewPage />} />
        <Route path="history" element={<StudentHistoryPage />} />
        <Route path="privacy" element={<PrivacyDataPage />} />
        <Route path="assignments" element={<AssignmentsPage />} />
        <Route path="learning" element={<LearningPage />} />
        <Route path="calendar" element={<CalendarPage />} />
        <Route path="notifications" element={<NotificationsPage />} />

        {/* Trainer Routes */}
        <Route path="trainer" element={<TrainerDashboardPage />} />
        <Route path="trainer/directory" element={<TrainerDashboardPage />} />
        <Route path="trainer/rubrics" element={<TrainerDashboardPage />} />
        <Route path="trainer/mentorship" element={<TrainerDashboardPage />} />

        {/* Admin Routes */}
        <Route path="admin" element={<AdminConsolePage />} />
        <Route path="admin/directory" element={<AdminConsolePage />} />
        <Route path="admin/audit" element={<AdminConsolePage />} />
        <Route path="admin/policies" element={<AdminConsolePage />} />
        <Route path="admin/engine" element={<AdminConsolePage />} />
      </Route>

      {/* Catch-all: send unauthenticated to login, authenticated to dashboard */}
      <Route path="*" element={
        currentUser
          ? <Navigate to={
              currentUser.role === 'trainer' ? '/trainer'
              : currentUser.role === 'admin' ? '/admin'
              : '/dashboard'
            } replace />
          : <Navigate to="/login" replace />
      } />
    </Routes>
  );
}

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AppProvider>
  );
}
