import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { FiUser, FiLock, FiTrendingUp } from 'react-icons/fi';
import './Login.css';

export default function Login() {
  const { login } = useAuth();
  const navigate  = useNavigate();
  const [form, setForm]     = useState({ username: '', password: '' });
  const [error, setError]   = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(form.username, form.password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Invalid username or password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-brand">
          <FiTrendingUp className="login-brand-icon" />
          <span>SalesForecast AI</span>
        </div>
        <h2>Welcome back</h2>
        <p className="login-sub">Sign in to your shop dashboard</p>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="login-field">
            <FiUser className="field-icon" />
            <input
              type="text"
              placeholder="Username"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              required
              autoFocus
            />
          </div>
          <div className="login-field">
            <FiLock className="field-icon" />
            <input
              type="password"
              placeholder="Password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
            />
          </div>

          {error && <div className="login-error">{error}</div>}

          <button type="submit" className="login-btn" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="login-demo">
          <p>Demo accounts:</p>
          <div className="demo-accounts">
            {[
              { u: 'muskan', p: 'muskan123', shop: 'Thakur Footwear' },
              { u: 'ritesh', p: 'ritesh123', shop: 'Ritesh Fashion' },
              { u: 'priya',  p: 'priya123',  shop: 'Priya Shoe House' },
            ].map((a) => (
              <button
                key={a.u}
                className="demo-btn"
                onClick={() => setForm({ username: a.u, password: a.p })}
              >
                <strong>{a.u}</strong>
                <span>{a.shop}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
