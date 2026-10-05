import './Forecasting.css';

const metricLabels = { mae: 'MAE', mse: 'MSE', rmse: 'RMSE', r2: 'R²' };
const metricColors = { mae: '#f59e0b', mse: '#ef4444', rmse: '#6c63ff', r2: '#10b981' };

function r2Label(r2) {
  if (r2 >= 0.85) return { text: 'Excellent', color: '#10b981' };
  if (r2 >= 0.70) return { text: 'Good',      color: '#10b981' };
  if (r2 >= 0.50) return { text: 'Fair',       color: '#f59e0b' };
  if (r2 >= 0.0)  return { text: 'Poor',       color: '#ef4444' };
  return           { text: 'Needs more data',  color: '#ef4444' };
}

export default function MetricsCard({ metrics, modelType }) {
  if (!metrics) return null;
  const quality = r2Label(metrics.r2);
  return (
    <div className="metrics-card">
      <div className="metrics-header">
        <h3 className="metrics-title">{modelType} — Evaluation Metrics</h3>
        <span className="r2-badge" style={{ background: quality.color + '22', color: quality.color }}>
          {quality.text}
        </span>
      </div>
      <div className="metrics-grid">
        {Object.entries(metricLabels).map(([key, label]) => (
          <div key={key} className="metric-item" style={{ borderTopColor: metricColors[key] }}>
            <span className="metric-label">{label}</span>
            <span className="metric-value">{metrics[key]?.toFixed(4)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
