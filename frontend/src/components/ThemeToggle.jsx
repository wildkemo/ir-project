import { Moon, Sun } from 'lucide-react';

export default function ThemeToggle({ theme, onToggle }) {
  const isDark = theme === 'dark';

  return (
    <button
      type="button"
      className="theme-toggle"
      onClick={onToggle}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      title={isDark ? 'Light mode' : 'Dark mode'}
    >
      <span className="theme-toggle__track" aria-hidden>
        <span className={`theme-toggle__thumb ${isDark ? '' : 'theme-toggle__thumb--light'}`} />
      </span>
      <Sun className="theme-toggle__icon theme-toggle__icon--sun" size={15} aria-hidden />
      <Moon className="theme-toggle__icon theme-toggle__icon--moon" size={15} aria-hidden />
    </button>
  );
}
