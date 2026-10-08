import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FiGrid, FiShoppingBag, FiTrendingUp, FiPackage, FiUpload, FiX, FiMenu, FiLogOut, FiUser } from 'react-icons/fi';
import { useAuth } from '../../context/AuthContext';
import './DashboardLayout.css';

const NAV_ITEMS = [
  { to: '/',            label: 'Dashboard',   icon: <FiGrid />,        color: '#6366f1' },
  { to: '/products',    label: 'Products',    icon: <FiShoppingBag />, color: '#10b981' },
  { to: '/upload',      label: 'Upload Data', icon: <FiUpload />,      color: '#0ea5e9' },
  { to: '/forecasting', label: 'Forecasting', icon: <FiTrendingUp />,  color: '#f59e0b' },
  { to: '/inventory',   label: 'Inventory',   icon: <FiPackage />,     color: '#ef4444' },
];

export default function DashboardLayout({ children }) {
  const [open, setOpen] = useState(false);
  const navigate  = useNavigate();
  const location  = useLocation();
  const { user, shop, logout } = useAuth();

  const handleNav = (to) => { navigate(to); setOpen(false); };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="app-shell">
      {/* Top bar */}
      <header className="top-bar">
        <div className="top-bar-left">
          <FiTrendingUp className="top-bar-logo" />
          <span className="top-bar-brand">SalesForecast AI</span>
          {shop && <span className="top-bar-shop">{shop.name}</span>}
        </div>
        <div className="top-bar-right">
          <div className="top-bar-user">
            <FiUser />
            <span>{user?.full_name || user?.username}</span>
          </div>
          <button className="logout-btn" onClick={handleLogout} title="Logout">
            <FiLogOut />
            <span>Logout</span>
          </button>
        </div>
      </header>

      <main className="app-main">{children}</main>

      {open && <div className="fab-backdrop" onClick={() => setOpen(false)} />}

      <div className={`fab-menu ${open ? 'open' : ''}`}>
        {[...NAV_ITEMS].reverse().map((item, i) => (
          <button
            key={item.to}
            className={`fab-item ${location.pathname === item.to ? 'fab-active' : ''}`}
            style={{ '--c': item.color, '--delay': `${i * 0.05}s` }}
            onClick={() => handleNav(item.to)}
          >
            <span className="fab-item-icon" style={{ background: item.color }}>{item.icon}</span>
            <span className="fab-item-label">{item.label}</span>
          </button>
        ))}
      </div>

      <button className="fab-trigger" onClick={() => setOpen(!open)}>
        {open ? <FiX /> : <FiMenu />}
      </button>
    </div>
  );
}
