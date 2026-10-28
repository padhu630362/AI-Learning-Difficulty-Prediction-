import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import { ThemeProvider } from './context/ThemeContext';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import ProtectedRoute from './components/ProtectedRoute';

// Public Pages
import LandingPage from './pages/LandingPage';
import Login from './pages/Login';
import Register from './pages/Register';

// Student Pages
import StudentDashboard from './pages/student/StudentDashboard';
import StudentSubjects from './pages/student/StudentSubjects';
import StudentTopicAnalysis from './pages/student/StudentTopicAnalysis';
import StudentRecommendations from './pages/student/StudentRecommendations';
import StudentProgress from './pages/student/StudentProgress';

// Instructor Pages
import InstructorDashboard from './pages/instructor/InstructorDashboard';
import InstructorSubjects from './pages/instructor/InstructorSubjects';
import InstructorAssessments from './pages/instructor/InstructorAssessments';
import InstructorStudentDetail from './pages/instructor/InstructorStudentDetail';
import InstructorAlerts from './pages/instructor/InstructorAlerts';

// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminUsers from './pages/admin/AdminUsers';
import AdminDatasets from './pages/admin/AdminDatasets';
import AdminModelEvaluation from './pages/admin/AdminModelEvaluation';

// Authenticated layout wrapper with Sidebar and Navbar
const AppLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-ivory-50 text-forest-950 dark:bg-forest-980 dark:text-forest-100 flex flex-col transition-colors duration-300">
      <Navbar onToggleSidebar={() => setSidebarOpen((prev) => !prev)} />
      <div className="flex flex-1">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main className="flex-1 lg:pl-64 flex flex-col min-w-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <ToastProvider>
          <Router>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* Student Protected Routes */}
              <Route element={<ProtectedRoute allowedRoles={['student']} />}>
                <Route element={<AppLayout />}>
                  <Route path="/student/dashboard" element={<StudentDashboard />} />
                  <Route path="/student/subjects" element={<StudentSubjects />} />
                  <Route path="/student/analysis" element={<StudentTopicAnalysis />} />
                  <Route path="/student/recommendations" element={<StudentRecommendations />} />
                  <Route path="/student/progress" element={<StudentProgress />} />
                </Route>
              </Route>

              {/* Instructor Protected Routes */}
              <Route element={<ProtectedRoute allowedRoles={['instructor']} />}>
                <Route element={<AppLayout />}>
                  <Route path="/instructor/dashboard" element={<InstructorDashboard />} />
                  <Route path="/instructor/subjects" element={<InstructorSubjects />} />
                  <Route path="/instructor/assessments" element={<InstructorAssessments />} />
                  <Route path="/instructor/students/:studentId" element={<InstructorStudentDetail />} />
                  <Route path="/instructor/alerts" element={<InstructorAlerts />} />
                </Route>
              </Route>

              {/* Admin Protected Routes */}
              <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
                <Route element={<AppLayout />}>
                  <Route path="/admin/dashboard" element={<AdminDashboard />} />
                  <Route path="/admin/users" element={<AdminUsers />} />
                  <Route path="/admin/datasets" element={<AdminDatasets />} />
                  <Route path="/admin/models" element={<AdminModelEvaluation />} />
                </Route>
              </Route>

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Router>
        </ToastProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
