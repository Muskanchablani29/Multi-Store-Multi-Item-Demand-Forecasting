import './Forecasting.css';

const metricLabels = { mae: 'MAE', mse: 'MSE', rmse: 'RMSE', r2: 'R²' };
const metricColors = { mae: '#f59e0b', mse: '#ef4444', rmse: '#6c63ff', r2: '#10b981' };

export default function MetricsCard({ metrics, modelType }) {
  if (!metrics) return null;
  return (
    <div className="metrics-card">
      <h3 className="metrics-title">{modelType} — Evaluation Metrics</h3>
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
