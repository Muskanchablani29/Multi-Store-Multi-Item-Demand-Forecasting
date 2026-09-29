import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip
} from 'recharts';

export default function ForecastChart({ forecasts, title }) {
  const data = forecasts.map((f) => ({
    date: f.date || f.forecast_date,
    Forecast: +parseFloat(f.predicted_qty).toFixed(2),
  }));

  return (
    <div className="chart-container">
      {title && <h3 className="chart-title">{title}</h3>}
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="forecastGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6c63ff" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#6c63ff" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#2d3348" />
          <XAxis dataKey="date" tick={{ fill: '#8892a4', fontSize: 11 }} tickLine={false} />
          <YAxis tick={{ fill: '#8892a4', fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip contentStyle={{ background: '#1a1f2e', border: '1px solid #2d3348', borderRadius: 8 }} />
          <Area type="monotone" dataKey="Forecast" stroke="#6c63ff" fill="url(#forecastGrad)" strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
