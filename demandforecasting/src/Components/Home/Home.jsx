import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiTrendingUp } from 'react-icons/fi';
import API from '../../services/api';
import './Home.css';

export default function Home() {
  const [isLogin, setIsLogin] = useState(true);
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isLogin) {
        const res = await API.post('/auth/login/', { username: form.username, password: form.password });
        localStorage.setItem('token', res.data.access);
        localStorage.setItem('user', JSON.stringify({ username: form.username }));
        navigate('/');
      } else {
        await API.post('/auth/register/', form);
        setIsLogin(true);
        setError('Registered! Please login.');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-container">
      <div className="home-card">
        <div className="home-brand">
          <FiTrendingUp />
          <h1>DemandAI</h1>
        </div>
        <p className="home-subtitle">Multi-Store Multi-Item Demand Forecasting</p>

        <div className="home-tabs">
          <button className={isLogin ? 'active' : ''} onClick={() => setIsLogin(true)}>Login</button>
          <button className={!isLogin ? 'active' : ''} onClick={() => setIsLogin(false)}>Register</button>
        </div>

        <form onSubmit={handleSubmit} className="home-form">
          <input
            type="text" placeholder="Username" required
            value={form.username} onChange={e => setForm({ ...form, username: e.target.value })}
          />
          {!isLogin && (
            <input
              type="email" placeholder="Email"
              value={form.email} onChange={e => setForm({ ...form, email: e.target.value })}
            />
          )}
          <input
            type="password" placeholder="Password" required
            value={form.password} onChange={e => setForm({ ...form, password: e.target.value })}
          />
          {error && <p className={`home-msg ${error.includes('Registered') ? 'success' : 'error'}`}>{error}</p>}
          <button type="submit" className="home-submit" disabled={loading}>
            {loading ? 'Please wait...' : isLogin ? 'Login' : 'Register'}
          </button>
        </form>
      </div>
    </div>
  );
}
