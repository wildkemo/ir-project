import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Search, Star, Clock, Cpu, GitCompare,
  Map, BookOpen, Settings, ChevronRight, Sparkles, X,
} from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import { formatRoleLabel } from '../../utils/userRole';
import Avatar from '../ui/Avatar';
import './Sidebar.css';

const NAV_ITEMS = [
  { to: '/dashboard',     label: 'Dashboard',      icon: LayoutDashboard },
  { to: '/search',        label: 'Search',         icon: Search, color: 'search' },
  { to: '/recommendations', label: 'Recommendations', icon: Sparkles, color: 'rec' },
  { to: '/favorites',     label: 'Favorites',      icon: Star,    color: 'fav' },
  { to: '/history',       label: 'History',        icon: Clock },
  { to: '/advisor',       label: 'AI Advisor',     icon: Cpu,     color: 'ai' },
  { to: '/compare',       label: 'Compare',        icon: GitCompare, color: 'compare' },
  { to: '/roadmap',       label: 'Roadmaps',       icon: Map,     color: 'roadmap' },
];

const BOTTOM_ITEMS = [
  { to: '/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar({ open, onClose }) {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  return (
    <>
      {open && <div className="sidebar-backdrop" onClick={onClose} />}
      <aside className={`sidebar ${open ? 'sidebar--open' : ''}`} aria-label="Main navigation">
        <div className="sidebar__header">
          <span className="sidebar__logo">⬡ RepoMind</span>
          <button className="sidebar__close-btn" onClick={onClose} aria-label="Close sidebar">
            <X size={16} />
          </button>
        </div>

        <nav className="sidebar__nav">
          <ul className="sidebar__list">
            {NAV_ITEMS.map(({ to, label, icon: Icon, color }) => (
              <li key={to}>
                <NavLink
                  to={to}
                  className={({ isActive }) =>
                    `sidebar__link ${isActive ? 'sidebar__link--active' : ''} ${color ? `sidebar__link--${color}` : ''}`
                  }
                  onClick={onClose}
                >
                  <Icon size={17} className="sidebar__link-icon" />
                  <span className="sidebar__link-label">{label}</span>
                  <ChevronRight size={14} className="sidebar__link-chevron" />
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="sidebar__footer">
          <div className="sidebar__divider" />
          <ul className="sidebar__list">
            {BOTTOM_ITEMS.map(({ to, label, icon: Icon }) => (
              <li key={to}>
                <NavLink
                  to={to}
                  className={({ isActive }) =>
                    `sidebar__link ${isActive ? 'sidebar__link--active' : ''}`
                  }
                  onClick={onClose}
                >
                  <Icon size={17} className="sidebar__link-icon" />
                  <span className="sidebar__link-label">{label}</span>
                </NavLink>
              </li>
            ))}
          </ul>

          {user && (
            <button
              className="sidebar__user"
              onClick={() => { navigate('/profile'); onClose(); }}
              aria-label="Go to profile"
            >
              <Avatar user={user} size="sm" />
              <div className="sidebar__user-info">
                <span className="sidebar__user-name">{user.username}</span>
                <span className="sidebar__user-role">{formatRoleLabel(user)}</span>
              </div>
              <ChevronRight size={14} className="sidebar__link-chevron" />
            </button>
          )}
        </div>
      </aside>
    </>
  );
}
