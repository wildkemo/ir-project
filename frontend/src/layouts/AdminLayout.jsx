import { useState } from 'react';
import { useNavigate, Outlet } from 'react-router-dom';
import { Moon, Sun, Menu } from 'lucide-react';
import AdminSidebar from '../components/layout/AdminSidebar';
import { useTheme } from '../hooks/useTheme';
import { useAuthStore } from '../stores/authStore';
import Avatar from '../components/ui/Avatar';
import './AdminLayout.css';

export default function AdminLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { theme, toggleTheme } = useTheme();
  const { user } = useAuthStore();
  const navigate = useNavigate();

  return (
    <div className="admin-layout">
      <header className="admin-topbar">
        <div className="admin-topbar__left">
          <button
            className="admin-topbar__menu-btn"
            onClick={() => setSidebarOpen((v) => !v)}
            aria-label="Toggle sidebar"
          >
            <Menu size={20} />
          </button>
          <span className="admin-topbar__brand">⬡ RepoMind Admin</span>
        </div>
        <div className="admin-topbar__right">
          <button className="admin-topbar__icon-btn" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          {user && (
            <button
              className="admin-topbar__user-btn"
              onClick={() => navigate('/profile')}
              aria-label="Profile"
            >
              <Avatar user={user} size="sm" />
            </button>
          )}
        </div>
      </header>

      <div className="admin-layout__body">
        <AdminSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main className="admin-layout__main">
          <div className="admin-layout__content page-enter">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
