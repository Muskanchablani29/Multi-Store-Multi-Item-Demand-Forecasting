import { NavLink } from 'react-router-dom';
import { FiBarChart2, FiUpload, FiTrendingUp, FiActivity, FiPackage, FiClock, FiShoppingBag } from 'react-icons/fi';
import './Sidebar.css';

const links = [
  { to: '/', label: 'Dashboard', icon: <FiBarChart2 /> },
  { to: '/products', label: 'Products', icon: <FiShoppingBag /> },
  { to: '/upload', label: 'Upload Data', icon: <FiUpload /> },
  { to: '/forecasting', label: 'Forecasting', icon: <FiTrendingUp /> },
  { to: '/model-comparison', label: 'Model Comparison', icon: <FiActivity /> },
  { to: '/inventory', label: 'Inventory', icon: <FiPackage /> },
  { to: '/forecast-history', label: 'Forecast History', icon: <FiClock /> },
];

export default function Sidebar() {
  return (
    <nav className="sidebar">
      <div className="sidebar-brand">
        <FiTrendingUp className="brand-icon" />
        <span>DemandAI</span>
      </div>
      <ul className="sidebar-links">
        {links.map(({ to, label, icon }) => (
          <li key={to}>
            <NavLink to={to} end className={({ isActive }) => isActive ? 'active' : ''}>
              {icon} <span>{label}</span>
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
