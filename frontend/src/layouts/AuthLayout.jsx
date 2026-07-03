import { Link } from 'react-router-dom';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../hooks/useTheme';
import './AuthLayout.css';

export default function AuthLayout({ children }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="auth-layout">
      <header className="auth-layout__header">
        <Link to="/" className="auth-layout__brand">
          <span className="auth-layout__brand-icon">⬡</span>
          <span>RepoMind AI</span>
        </Link>
        <button
          className="auth-layout__theme-btn"
          onClick={toggleTheme}
          aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </header>

      <main className="auth-layout__main">
        <div className="auth-layout__card page-enter">{children}</div>
      </main>

      <footer className="auth-layout__footer">
        <p>© {new Date().getFullYear()} RepoMind AI. Developer Intelligence Platform.</p>
      </footer>
    </div>
  );
}
