import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button, Input } from '../components/ui';
import './Auth.css';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const me = await login(form);
      navigate(me?.role === 'admin' ? '/manager-dashboard' : '/member-dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-bg">
        <div className="auth-grid" />
      </div>
      <div className="auth-card animate-fade">
        <div className="auth-brand">
          <div className="auth-mark">T</div>
          <span>TaskFlow</span>
        </div>
        <div className="auth-heading">
          <h1>Welcome back</h1>
          <p>Sign in to your workspace</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <Input
            id="email" label="Email" type="email"
            value={form.email} onChange={set('email')}
            placeholder="you@company.com" required
          />
          <Input
            id="password" label="Password" type="password"
            value={form.password} onChange={set('password')}
            placeholder="••••••••" required
          />
          {error && <div className="auth-error">{error}</div>}
          <Button type="submit" loading={loading} size="lg" style={{ width: '100%', justifyContent: 'center' }}>
            Sign in
          </Button>
        </form>

        <div className="auth-footer">
          Don't have an account? <Link to="/signup">Create one</Link>
        </div>
      </div>
    </div>
  );
}
