import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button, Input } from '../components/ui';
import './Auth.css';

const SEEDED_COMPANIES = [
  { name: 'Acme Corp', manager: 'manager@acme.com', employee: 'bob@acme.com' },
  { name: 'Globex Systems', manager: 'manager@globex.com', employee: 'grace@globex.com' },
  { name: 'Initech Software', manager: 'manager@initech.com', employee: 'milton@initech.com' },
  { name: 'Umbrella Corp', manager: 'manager@umbrella.com', employee: 'jill@umbrella.com' },
];

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Clear any stale tokens on navigating to login page
  useEffect(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }, []);

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }));

  const quickFill = (email) => {
    setForm({ email, password: 'Test@Password123' });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const me = await login(form);
      navigate(me?.role === 'admin' ? '/manager-dashboard' : '/member-dashboard');
    } catch (err) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-bg">
        <div className="auth-grid" />
      </div>
      <div className="auth-card animate-fade" style={{ maxWidth: 440 }}>
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

        {/* Quick-fill Seeded Accounts Helper */}
        <div style={{ marginTop: 20, paddingTop: 16, borderTop: '1px solid var(--border)' }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-2)', marginBottom: 8 }}>
            Quick-Fill Seeded Accounts (Password: Test@Password123):
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
            {SEEDED_COMPANIES.map(c => (
              <div key={c.name} style={{ background: 'var(--bg-2, rgba(255,255,255,0.04))', padding: '8px 10px', borderRadius: 6, fontSize: 11 }}>
                <div style={{ fontWeight: 600, color: 'var(--text-1)', marginBottom: 4 }}>{c.name}</div>
                <div style={{ display: 'flex', gap: 6 }}>
                  <button
                    type="button"
                    onClick={() => quickFill(c.manager)}
                    style={{ background: 'none', border: 'none', padding: 0, color: 'var(--accent, #6366f1)', cursor: 'pointer', textDecoration: 'underline', fontSize: 11 }}
                  >
                    Manager
                  </button>
                  <span style={{ color: 'var(--text-3)' }}>|</span>
                  <button
                    type="button"
                    onClick={() => quickFill(c.employee)}
                    style={{ background: 'none', border: 'none', padding: 0, color: 'var(--text-2)', cursor: 'pointer', textDecoration: 'underline', fontSize: 11 }}
                  >
                    Employee
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="auth-footer" style={{ marginTop: 16 }}>
          Don't have an account? <Link to="/signup">Create one</Link>
        </div>
      </div>
    </div>
  );
}
