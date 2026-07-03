import { createBrowserRouter } from 'react-router-dom';
import { RequireAuth, RequireAdmin, RequireGuest } from './router/guards';

/* Layouts */
import AppLayout   from './layouts/AppLayout';
import AdminLayout from './layouts/AdminLayout';

/* Auth pages */
import LoginPage      from './pages/auth/LoginPage';
import RegisterPage   from './pages/auth/RegisterPage';
import OnboardingPage from './pages/auth/OnboardingPage';

/* App pages */
import LandingPage         from './pages/LandingPage';
import DashboardPage       from './pages/DashboardPage';
import SearchPage          from './pages/SearchPage';
import RecommendationsPage from './pages/RecommendationsPage';
import FavoritesPage       from './pages/FavoritesPage';
import HistoryPage         from './pages/HistoryPage';
import AdvisorPage         from './pages/AdvisorPage';
import ComparePage         from './pages/ComparePage';
import RoadmapPage         from './pages/RoadmapPage';
import ProfilePage         from './pages/ProfilePage';
import RepositoryDetailsPage from './pages/RepositoryDetailsPage';
import SettingsPage        from './pages/SettingsPage';
import NotFoundPage        from './pages/NotFoundPage';

/* Admin pages */
import AdminDashboardPage from './pages/admin/AdminDashboardPage';
import AdminUsersPage     from './pages/admin/AdminUsersPage';
import AdminAnalyticsPage from './pages/admin/AdminAnalyticsPage';
import AdminAIUsagePage   from './pages/admin/AdminAIUsagePage';
import AdminSystemPage    from './pages/admin/AdminSystemPage';

export const router = createBrowserRouter([
  /* ── Public ──────────────────────────── */
  { path: '/', element: <LandingPage /> },

  {
    path: '/login',
    element: <RequireGuest><LoginPage /></RequireGuest>,
  },
  {
    path: '/register',
    element: <RequireGuest><RegisterPage /></RequireGuest>,
  },
  {
    path: '/onboarding',
    element: <RequireAuth><OnboardingPage /></RequireAuth>,
  },

  /* ── App shell (topbar + sidebar) ───── */
  {
    element: <AppLayout />,
    children: [
      { path: '/dashboard',       element: <RequireAuth><DashboardPage /></RequireAuth> },
      { path: '/search',          element: <SearchPage /> },
      { path: '/repository/:owner/:repo', element: <RepositoryDetailsPage /> },
      { path: '/recommendations', element: <RequireAuth><RecommendationsPage /></RequireAuth> },
      { path: '/favorites',       element: <RequireAuth><FavoritesPage /></RequireAuth> },
      { path: '/history',         element: <RequireAuth><HistoryPage /></RequireAuth> },
      { path: '/advisor',         element: <AdvisorPage /> },
      { path: '/compare',         element: <ComparePage /> },
      { path: '/roadmap',         element: <RoadmapPage /> },
      { path: '/profile',         element: <RequireAuth><ProfilePage /></RequireAuth> },
      { path: '/settings',        element: <SettingsPage /> },
    ],
  },

  /* ── Admin shell ─────────────────────── */
  {
    element: <RequireAdmin><AdminLayout /></RequireAdmin>,
    children: [
      { path: '/admin',            element: <AdminDashboardPage /> },
      { path: '/admin/users',      element: <AdminUsersPage /> },
      { path: '/admin/analytics',  element: <AdminAnalyticsPage /> },
      { path: '/admin/ai-usage',   element: <AdminAIUsagePage /> },
      { path: '/admin/system',     element: <AdminSystemPage /> },
      { path: '/admin/settings',   element: <SettingsPage /> },
    ],
  },

  /* ── 404 ─────────────────────────────── */
  { path: '*', element: <NotFoundPage /> },
]);
