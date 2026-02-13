import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import AppShell from '@/components/layout/AppShell';
import LoginPage from '@/pages/LoginPage';
import DashboardPage from '@/pages/DashboardPage';
import DocumentLibraryPage from '@/pages/DocumentLibraryPage';
import DocumentReviewPage from '@/pages/DocumentReviewPage';
import LineItemExplorerPage from '@/pages/LineItemExplorerPage';
import ChatPage from '@/pages/ChatPage';
import ProductCatalogPage from '@/pages/ProductCatalogPage';
import SettingsPage from '@/pages/SettingsPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="documents" element={<DocumentLibraryPage />} />
        <Route path="documents/:id" element={<DocumentReviewPage />} />
        <Route path="line-items" element={<LineItemExplorerPage />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="products" element={<ProductCatalogPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
