import './StatCard.css';

export default function StatCard({ title, value, subtitle, icon, color = '#6c63ff' }) {
  return (
    <div className="stat-card" style={{ borderTopColor: color }}>
      <div className="stat-card-header">
        <span className="stat-card-title">{title}</span>
        <span className="stat-card-icon" style={{ color }}>{icon}</span>
      </div>
      <div className="stat-card-value">{value}</div>
      {subtitle && <div className="stat-card-subtitle">{subtitle}</div>}
    </div>
  );
}
