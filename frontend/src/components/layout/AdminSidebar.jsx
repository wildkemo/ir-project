import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Users, BarChart2, Cpu, Activity,
  Settings, ChevronRight, ArrowLeft,
} from 'lucide-react';
import './Sidebar.css';
import './AdminSidebar.css';

const ADMIN_NAV = [
  { to: '/admin',           label: 'Overview',       icon: LayoutDashboard, end: true },
  { to: '/admin/users',     label: 'Users',          icon: Users },
  { to: '/admin/analytics', label: 'Analytics',      icon: BarChart2 },
  { to: '/admin/ai-usage',  label: 'AI Usage',       icon: Cpu },
  { to: '/admin/system',    label: 'System Health',  icon: Activity },
  { to: '/admin/settings',  label: 'Settings',       icon: Settings },
];

export default function AdminSidebar({ open, onClose }) {
  const navigate = useNavigate();

  return (
    <>
      {open && <div className="sidebar-backdrop" onClick={onClose} />}
      <aside className={`sidebar admin-sidebar ${open ? 'sidebar--open' : ''}`} aria-label="Admin navigation">
        <div className="sidebar__header">
          <span className="sidebar__logo">⬡ Admin</span>
        </div>

        <div className="admin-sidebar__back">
          <button
            className="admin-sidebar__back-btn"
            onClick={() => { navigate('/dashboard'); onClose?.(); }}
          >
            <ArrowLeft size={15} />
            Back to App
          </button>
        </div>

        <nav className="sidebar__nav">
          <p className="admin-sidebar__section-label">Administration</p>
          <ul className="sidebar__list">
            {ADMIN_NAV.map(({ to, label, icon: Icon, end }) => (
              <li key={to}>
                <NavLink
                  to={to}
                  end={end}
                  className={({ isActive }) =>
                    `sidebar__link ${isActive ? 'sidebar__link--active' : ''}`
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
      </aside>
    </>
  );
}
