import { useState } from 'react';
import { LogIn } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getApiErrorMessage } from '../api/auth';

export default function LoginPage({ onSwitchToRegister, onSuccess }) {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await login({ email, password });
      onSuccess?.();
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="auth-panel">
      <header className="auth-panel__header">
        <LogIn size={22} aria-hidden />
        <h2>Sign in</h2>
        <p>Access your profile, favorites, and history.</p>
      </header>

      <form className="auth-form" onSubmit={handleSubmit}>
        {error && (
          <div className="alert alert--error" role="alert">
            {error}
          </div>
        )}

        <label className="auth-form__field">
          <span>Email</span>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
          />
        </label>

        <label className="auth-form__field">
          <span>Password</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
            minLength={8}
          />
        </label>

        <button type="submit" className="btn btn--primary" disabled={loading}>
          {loading ? 'Signing in…' : 'Sign in'}
        </button>
      </form>

      <p className="auth-panel__footer">
        No account?{' '}
        <button type="button" className="btn btn--link" onClick={onSwitchToRegister}>
          Create one
        </button>
      </p>
    </section>
  );
}
