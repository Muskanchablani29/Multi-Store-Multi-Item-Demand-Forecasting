import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend
} from 'recharts';

export default function MetricsComparisonChart({ lstmMetrics, gruMetrics }) {
  if (!lstmMetrics && !gruMetrics) return null;

  const data = ['MAE', 'MSE', 'RMSE', 'R²'].map((metric) => {
    const key = metric.toLowerCase().replace('²', '2');
    return {
      metric,
      LSTM: lstmMetrics ? +lstmMetrics[key]?.toFixed(4) : null,
      GRU: gruMetrics ? +gruMetrics[key]?.toFixed(4) : null,
    };
  });

  return (
    <div className="chart-container">
      <h3 className="chart-title">LSTM vs GRU — Metrics Comparison</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2d3348" />
          <XAxis dataKey="metric" tick={{ fill: '#8892a4', fontSize: 12 }} />
          <YAxis tick={{ fill: '#8892a4', fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip contentStyle={{ background: '#1a1f2e', border: '1px solid #2d3348', borderRadius: 8 }} />
          <Legend />
          <Bar dataKey="LSTM" fill="#6c63ff" radius={[4, 4, 0, 0]} />
          <Bar dataKey="GRU" fill="#10b981" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
