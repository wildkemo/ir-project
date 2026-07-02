import { useState } from 'react';
import { UserPlus } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { getApiErrorMessage } from '../api/auth';

export default function RegisterPage({ onSwitchToLogin, onSuccess }) {
  const { register } = useAuth();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await register({ username, email, password });
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
        <UserPlus size={22} aria-hidden />
        <h2>Create account</h2>
        <p>Save favorites and sync your preferences across sessions.</p>
      </header>

      <form className="auth-form" onSubmit={handleSubmit}>
        {error && (
          <div className="alert alert--error" role="alert">
            {error}
          </div>
        )}

        <label className="auth-form__field">
          <span>Username</span>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoComplete="username"
            minLength={3}
            maxLength={50}
            pattern="[a-zA-Z0-9_]{3,50}"
          />
        </label>

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
            autoComplete="new-password"
            minLength={8}
          />
        </label>

        <button type="submit" className="btn btn--primary" disabled={loading}>
          {loading ? 'Creating account…' : 'Register'}
        </button>
      </form>

      <p className="auth-panel__footer">
        Already have an account?{' '}
        <button type="button" className="btn btn--link" onClick={onSwitchToLogin}>
          Sign in
        </button>
      </p>
    </section>
  );
}
