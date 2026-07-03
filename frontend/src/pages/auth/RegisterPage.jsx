import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { User, Mail, Lock, AlertCircle } from 'lucide-react';
import AuthLayout from '../../layouts/AuthLayout';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import { useAuthStore } from '../../stores/authStore';
import { getErrorMessage } from '../../services/api';
import './AuthPage.css';

export default function RegisterPage() {
  const { register } = useAuthStore();
  const navigate = useNavigate();

  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const set = (field) => (e) => {
    setForm((f) => ({ ...f, [field]: e.target.value }));
    if (error) setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.username || !form.email || !form.password) return;
    setLoading(true);
    setError(null);
    try {
      await register(form);
      navigate('/onboarding', { replace: true });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <div className="auth-card">
        <div className="auth-card__header">
          <h1 className="auth-card__title">Create your account</h1>
          <p className="auth-card__subtitle">Start discovering repositories tailored to you</p>
        </div>

        {error && (
          <div className="auth-card__error" role="alert">
            <AlertCircle size={15} />
            <span>{error}</span>
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <Input
            label="Username"
            type="text"
            value={form.username}
            onChange={set('username')}
            placeholder="your-username"
            icon={<User size={16} />}
            autoComplete="username"
            required
          />
          <Input
            label="Email address"
            type="email"
            value={form.email}
            onChange={set('email')}
            placeholder="you@example.com"
            icon={<Mail size={16} />}
            autoComplete="email"
            required
          />
          <Input
            label="Password"
            type="password"
            value={form.password}
            onChange={set('password')}
            placeholder="At least 8 characters"
            icon={<Lock size={16} />}
            autoComplete="new-password"
            required
            hint="Use a strong password with letters, numbers, and symbols."
          />
          <Button type="submit" variant="primary" fullWidth loading={loading} size="lg">
            Create account
          </Button>
        </form>

        <div className="auth-card__footer">
          <p>
            Already have an account?{' '}
            <Link to="/login" className="auth-card__link">Sign in</Link>
          </p>
        </div>
      </div>
    </AuthLayout>
  );
}
