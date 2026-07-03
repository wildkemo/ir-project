/**
 * Route guard components — kept in a separate file so router.jsx
 * (which exports non-component values) doesn't break Vite Fast Refresh.
 */
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { loadAccessToken } from '../utils/authStorage';
import { isAdmin } from '../utils/userRole';
import Spinner from '../components/ui/Spinner';

/** Redirect unauthenticated users to /login. */
export function RequireAuth({ children }) {
  const user    = useAuthStore((s) => s.user);
  const loading = useAuthStore((s) => s.loading);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '40vh' }}>
        <Spinner size="lg" />
      </div>
    );
  }
  if (!user || !loadAccessToken()) return <Navigate to="/login" replace />;
  return children;
}

/** Redirect non-admin users away from admin routes. */
export function RequireAdmin({ children }) {
  const user    = useAuthStore((s) => s.user);
  const loading = useAuthStore((s) => s.loading);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '40vh' }}>
        <Spinner size="lg" />
      </div>
    );
  }
  if (!user || !loadAccessToken()) return <Navigate to="/login" replace />;
  if (!isAdmin(user)) return <Navigate to="/dashboard" replace />;
  return children;
}

/** Redirect already-authenticated users away from auth pages. */
export function RequireGuest({ children }) {
  const user = useAuthStore((s) => s.user);
  if (user && loadAccessToken()) return <Navigate to="/dashboard" replace />;
  return children;
}
