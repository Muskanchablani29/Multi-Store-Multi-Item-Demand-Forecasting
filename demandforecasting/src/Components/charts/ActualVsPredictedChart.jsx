import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend
} from 'recharts';

export default function ActualVsPredictedChart({ dates, actual, predicted, title }) {
  const data = dates.map((d, i) => ({
    date: d,
    Actual: actual[i] !== undefined ? +actual[i].toFixed(2) : null,
    Predicted: predicted[i] !== undefined ? +predicted[i].toFixed(2) : null,
  }));

  return (
    <div className="chart-container">
      {title && <h3 className="chart-title">{title}</h3>}
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2d3348" />
          <XAxis dataKey="date" tick={{ fill: '#8892a4', fontSize: 11 }} tickLine={false} />
          <YAxis tick={{ fill: '#8892a4', fontSize: 11 }} tickLine={false} axisLine={false} />
          <Tooltip contentStyle={{ background: '#1a1f2e', border: '1px solid #2d3348', borderRadius: 8 }} />
          <Legend />
          <Line type="monotone" dataKey="Actual" stroke="#6c63ff" dot={false} strokeWidth={2} />
          <Line type="monotone" dataKey="Predicted" stroke="#f59e0b" dot={false} strokeWidth={2} strokeDasharray="5 5" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
