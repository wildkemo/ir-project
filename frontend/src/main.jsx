import { StrictMode, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { ToastProvider } from './context/ToastContext';
import { useAuthStore } from './stores/authStore';
import { applyTheme, getStoredTheme } from './hooks/useTheme';
import App from './App';

/* Styles — order matters */
import './styles/global.css';
import './styles/toast.css';

/* Apply theme before first render to avoid flash */
applyTheme(getStoredTheme());

function Root() {
  const init = useAuthStore((s) => s.init);
  useEffect(() => { init(); }, [init]);

  return (
    <StrictMode>
      <ToastProvider>
        <App />
      </ToastProvider>
    </StrictMode>
  );
}

createRoot(document.getElementById('root')).render(<Root />);
