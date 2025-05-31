import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// 页面组件
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import PapersList from './pages/PapersList';
import PaperUpload from './pages/PaperUpload';
import PaperDetail from './pages/PaperDetail';
import AnalysisDetail from './pages/AnalysisDetail';
import ReportDetail from './pages/ReportDetail';
import UserSettings from './pages/UserSettings';

// 布局组件
import MainLayout from './layouts/MainLayout';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* 公共路由 */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* 受保护路由 */}
          <Route path="/" element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
            <Route index element={<Dashboard />} />
            <Route path="papers" element={<PapersList />} />
            <Route path="papers/upload" element={<PaperUpload />} />
            <Route path="papers/:paperId" element={<PaperDetail />} />
            <Route path="analysis/:analysisId" element={<AnalysisDetail />} />
            <Route path="reports/:reportId" element={<ReportDetail />} />
            <Route path="settings" element={<UserSettings />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;