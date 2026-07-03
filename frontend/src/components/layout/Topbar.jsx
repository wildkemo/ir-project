import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Search, Moon, Sun, LogOut, User, Heart, Clock, LayoutDashboard, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { loadAccessToken } from '../../utils/authStorage';
import { isAdmin } from '../../utils/userRole';
import { useTheme } from '../../hooks/useTheme';
import Avatar from '../ui/Avatar';
import './Topbar.css';

export default function Topbar({ onMenuToggle, menuOpen }) {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const isAuthenticated = Boolean(user && loadAccessToken());
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const handleLogout = async () => {
    setUserMenuOpen(false);
    await logout();
    navigate('/');
  };

  const navLinks = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/search',    label: 'Search',    icon: Search },
    { to: '/favorites', label: 'Favorites', icon: Heart },
    { to: '/history',   label: 'History',   icon: Clock },
  ];

  return (
    <header className="topbar">
      <div className="topbar__left">
        <button className="topbar__menu-btn" onClick={onMenuToggle} aria-label="Toggle sidebar">
          {menuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
        <Link to={isAuthenticated ? '/dashboard' : '/'} className="topbar__brand">
          <span className="topbar__brand-icon">⬡</span>
          <span className="topbar__brand-name">RepoMind AI</span>
        </Link>
      </div>

      <nav className="topbar__nav" aria-label="Primary">
        {isAuthenticated && navLinks.map(({ to, label }) => (
          <Link
            key={to}
            to={to}
            className={`topbar__nav-link ${location.pathname.startsWith(to) ? 'topbar__nav-link--active' : ''}`}
          >
            {label}
          </Link>
        ))}
      </nav>

      <div className="topbar__right">
        {isAuthenticated && (
          <button
            className="topbar__search-btn"
            onClick={() => navigate('/search')}
            aria-label="Open search"
          >
            <Search size={16} />
            <span className="topbar__search-hint">Search repos…</span>
            <kbd className="topbar__kbd">⌘K</kbd>
          </button>
        )}

        <button
          className="topbar__icon-btn"
          onClick={toggleTheme}
          aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        {isAuthenticated ? (
          <div className="topbar__user-menu-wrap">
            <button
              className="topbar__user-btn"
              onClick={() => setUserMenuOpen((v) => !v)}
              aria-haspopup="true"
              aria-expanded={userMenuOpen}
            >
              <Avatar user={user} size="sm" />
              <span className="topbar__username">{user?.username}</span>
            </button>

            {userMenuOpen && (
              <>
                <div className="topbar__backdrop" onClick={() => setUserMenuOpen(false)} />
                <div className="topbar__dropdown">
                  <div className="topbar__dropdown-header">
                    <p className="topbar__dropdown-name">{user?.username}</p>
                    <p className="topbar__dropdown-email">{user?.email}</p>
                  </div>
                  <div className="topbar__dropdown-divider" />
                  <Link
                    to="/profile"
                    className="topbar__dropdown-item"
                    onClick={() => setUserMenuOpen(false)}
                  >
                    <User size={15} /> Profile
                  </Link>
                  {isAdmin(user) && (
                    <Link
                      to="/admin"
                      className="topbar__dropdown-item"
                      onClick={() => setUserMenuOpen(false)}
                    >
                      <LayoutDashboard size={15} /> Admin Panel
                    </Link>
                  )}
                  <div className="topbar__dropdown-divider" />
                  <button className="topbar__dropdown-item topbar__dropdown-item--danger" onClick={handleLogout}>
                    <LogOut size={15} /> Sign out
                  </button>
                </div>
              </>
            )}
          </div>
        ) : (
          <div className="topbar__auth-links">
            <Link to="/login" className="topbar__auth-link">Sign in</Link>
            <Link to="/register" className="topbar__auth-link topbar__auth-link--primary">Get started</Link>
          </div>
        )}
      </div>
    </header>
  );
}
