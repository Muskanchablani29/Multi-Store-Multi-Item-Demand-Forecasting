import './StatCard.css';

export default function StatCard({ title, value, subtitle, icon, color = '#6366f1' }) {
  return (
    <div className="stat-card">
      <div className="stat-card-header">
        <span className="stat-card-title">{title}</span>
        <span className="stat-card-icon" style={{ background: `${color}18`, color }}>{icon}</span>
      </div>
      <div className="stat-card-value">{value}</div>
      {subtitle && <div className="stat-card-subtitle">{subtitle}</div>}
    </div>
  );
}
