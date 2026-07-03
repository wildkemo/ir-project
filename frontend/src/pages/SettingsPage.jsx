import { Settings, Moon, Sun, Monitor } from 'lucide-react';
import { useTheme } from '../hooks/useTheme';
import './SettingsPage.css';

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();

  const THEME_OPTIONS = [
    { value: 'dark',  label: 'Dark',   icon: Moon },
    { value: 'light', label: 'Light',  icon: Sun },
  ];

  return (
    <div className="settings-page page-enter">
      <div className="page-header">
        <Settings size={20} className="page-header__icon page-header__icon--search" />
        <div>
          <h1 className="page-header__title">Settings</h1>
          <p className="page-header__subtitle">Preferences and application configuration</p>
        </div>
      </div>

      <div className="settings-grid">
        <section className="settings-section">
          <h2 className="settings-section__title">Appearance</h2>
          <div className="settings-section__desc">
            Choose how RepoMind AI looks. Design tokens ensure consistency across both themes.
          </div>

          <div className="theme-selector">
            {THEME_OPTIONS.map(({ value, label, icon: Icon }) => (
              <button
                key={value}
                className={`theme-option ${theme === value ? 'theme-option--active' : ''}`}
                onClick={() => setTheme(value)}
                aria-pressed={theme === value}
              >
                <Icon size={22} className="theme-option__icon" />
                <span className="theme-option__label">{label}</span>
                {theme === value && (
                  <span className="theme-option__active-badge">Active</span>
                )}
              </button>
            ))}
          </div>
        </section>

        <section className="settings-section">
          <h2 className="settings-section__title">About</h2>
          <div className="settings-about">
            <div className="settings-about__row">
              <span>Platform</span>
              <span>RepoMind AI</span>
            </div>
            <div className="settings-about__row">
              <span>Frontend</span>
              <span>React 19 + Vite</span>
            </div>
            <div className="settings-about__row">
              <span>Search Engine</span>
              <span>BM25 + Semantic (Hybrid)</span>
            </div>
            <div className="settings-about__row">
              <span>AI</span>
              <span>Ollama RAG + Rule-based</span>
            </div>
            <div className="settings-about__row">
              <span>Database</span>
              <span>PostgreSQL + Qdrant</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
