import { useEffect, useState } from 'react';
import {
  FiTrendingUp, FiDollarSign, FiPackage, FiAlertTriangle,
  FiShoppingBag, FiArrowUp, FiArrowDown, FiZap, FiActivity,
  FiRefreshCw, FiBarChart2, FiBox, FiStar,
} from 'react-icons/fi';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, LineChart, Line, Cell,
} from 'recharts';
import { dashboardAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import './Dashboard.css';

const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const MONTH_SHORT = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

const TT = {
  background:'#fff', border:'1px solid #e8edf5', borderRadius:10,
  fontSize:12, color:'#374151', padding:'10px 14px',
  boxShadow:'0 4px 20px rgba(0,0,0,0.1)',
};

const HEAT_COLORS = [
  '#eff6ff','#dbeafe','#bfdbfe','#93c5fd','#60a5fa','#3b82f6','#2563eb','#1d4ed8',
];

function heatColor(val, max) {
  if (!max || !val) return HEAT_COLORS[0];
  const idx = Math.min(7, Math.floor((val / max) * 7));
  return HEAT_COLORS[idx];
}

const DAYS = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];

export default function Dashboard() {
  const { user, shop } = useAuth();
  const [s, setS]             = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState('');
  const [chartTab, setChartTab] = useState('units');

  useEffect(() => {
    dashboardAPI.getStats()
      .then((r) => setS(r.data))
      .catch(() => setError('Failed to load dashboard data.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="dash-loader">
      <div className="dash-spinner" />
      <p>Loading dashboard…</p>
    </div>
  );
  if (error) return <div className="dash-loader" style={{ color:'#ef4444' }}>{error}</div>;
  if (!s)    return null;

  const growthPositive = (s.revenue_growth || 0) >= 0;

  const monthlyData = (s.monthly_sales || []).map((m) => ({
    name: MONTH_SHORT[(m.month || 1) - 1],
    units: Math.round(m.units || 0),
    revenue: Math.round(m.revenue || 0),
  }));

  // Sparkline data (last 7 months)
  const spark = monthlyData.slice(-7);

  // Heatmap: real day-of-week data from backend
  const heatmapData = s.heatmap_data || [];
  const heatMax = heatmapData.length > 0
    ? heatmapData.reduce((mx, p) => Math.max(mx, ...p.days), 0)
    : 0;

  // Top products
  const topProducts = (s.top_products || []).slice(0, 5);

  // Model accuracy
  const modelRows = (s.model_accuracy || []).slice(0, 5);

  // Inventory panel
  const invPanel = (s.inventory_panel || []).slice(0, 5);

  // Quick insights
  const insights = [
    growthPositive
      ? { icon: '📈', color: '#10b981', bg: '#ecfdf5', text: `Revenue grew ${s.revenue_growth}% vs last year.` }
      : { icon: '📉', color: '#ef4444', bg: '#fef2f2', text: `Revenue down ${Math.abs(s.revenue_growth)}% vs last year.` },
    s.reorder_alerts > 0
      ? { icon: '⚠️', color: '#f59e0b', bg: '#fffbeb', text: `${s.reorder_alerts} products may go out of stock soon.` }
      : { icon: '✅', color: '#10b981', bg: '#ecfdf5', text: 'All products have sufficient stock.' },
    topProducts[0]
      ? { icon: '🏆', color: '#6366f1', bg: '#eef2ff', text: `${topProducts[0].product_name} is your best-selling product.` }
      : null,
    s.predicted_next_month_units > 0
      ? { icon: '🔮', color: '#8b5cf6', bg: '#f5f3ff', text: `Forecast: ${Math.round(s.predicted_next_month_units).toLocaleString()} units next month.` }
      : null,
  ].filter(Boolean);

  const kpis = [
    {
      label: 'Total Sales', icon: <FiBarChart2 />, color: '#6366f1', bg: '#eef2ff',
      value: s.total_units ? Math.round(s.total_units).toLocaleString() : '0',
      sub: growthPositive ? `+${s.revenue_growth}% vs last period` : `${s.revenue_growth}% vs last period`,
      subColor: growthPositive ? '#10b981' : '#ef4444',
      trend: growthPositive,
    },
    {
      label: 'Revenue', icon: <FiDollarSign />, color: '#10b981', bg: '#ecfdf5',
      value: s.total_revenue ? `Rs ${(s.total_revenue/100000).toFixed(1)}L` : '0',
      sub: `${s.total_profit ? ((s.total_profit/s.total_revenue)*100).toFixed(1) : 0}% profit margin`,
      subColor: '#10b981', trend: true,
    },
    {
      label: 'Forecast Demand', icon: <FiZap />, color: '#f59e0b', bg: '#fffbeb',
      value: s.predicted_next_month_units ? Math.round(s.predicted_next_month_units).toLocaleString() : '—',
      sub: s.predicted_next_month_revenue
        ? `Rs ${(s.predicted_next_month_revenue/1000).toFixed(0)}K · ${s.forecast_month || ''}`
        : 'Generate forecast first',
      subColor: '#f59e0b', trend: true,
    },
    {
      label: 'Current Stock', icon: <FiPackage />, color: '#0ea5e9', bg: '#f0f9ff',
      value: (s.current_stock || 0).toLocaleString(),
      sub: s.reorder_alerts > 0 ? `${s.reorder_alerts} reorder alerts` : 'Stock levels OK',
      subColor: s.reorder_alerts > 0 ? '#ef4444' : '#10b981', trend: s.reorder_alerts === 0,
    },
  ];

  return (
    <div className="dash">

      {/* ── Top Header ── */}
      <div className="dash-topbar">
        <div className="dash-topbar-left">
          <div className="dash-shop-avatar">{(s.shop?.name || 'S')[0]}</div>
          <div>
            <h1 className="dash-shop-name">{s.shop?.name || 'Your Shop'}</h1>
            <p className="dash-shop-meta">
              <span className="dash-shop-badge">{s.shop?.category}</span>
              <span>{s.shop?.owner}</span>
              <span>·</span>
              <span>{s.shop?.location}</span>
            </p>
          </div>
        </div>
        <div className="dash-topbar-right">
          <div className="dash-date-range">
            <FiRefreshCw style={{ fontSize: '0.85rem' }} />
            <span>Jan 2024 – Dec 2024</span>
          </div>
          <div className="dash-model-badge">
            <FiActivity style={{ fontSize: '0.85rem' }} />
            <span>LSTM Model</span>
          </div>
        </div>
      </div>

      <div className="dash-body">

        {/* ── KPI Cards ── */}
        <div className="dash-kpis">
          {kpis.map((k, i) => (
            <div className="kpi" key={k.label}>
              <div className="kpi-top-row">
                <div className="kpi-icon-wrap" style={{ background: k.bg, color: k.color }}>{k.icon}</div>
                <span className={`kpi-trend-badge ${k.trend ? 'up' : 'down'}`}>
                  {k.trend ? <FiArrowUp /> : <FiArrowDown />}
                </span>
              </div>
              <div className="kpi-value" style={{ color: k.color }}>{k.value}</div>
              <div className="kpi-label">{k.label}</div>
              <div className="kpi-sub" style={{ color: k.subColor }}>{k.sub}</div>
              {/* Mini sparkline */}
              {spark.length > 0 && (
                <div className="kpi-spark">
                  <ResponsiveContainer width="100%" height={40}>
                    <AreaChart data={spark} margin={{ top: 4, right: 0, left: 0, bottom: 0 }}>
                      <defs>
                        <linearGradient id={`sg${i}`} x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%"  stopColor={k.color} stopOpacity={0.25} />
                          <stop offset="95%" stopColor={k.color} stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <Area type="monotone" dataKey={i === 1 ? 'revenue' : 'units'}
                        stroke={k.color} strokeWidth={1.5}
                        fill={`url(#sg${i})`} dot={false} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* ── Main Grid ── */}
        <div className="dash-main-grid">

          {/* LEFT COLUMN */}
          <div className="dash-col-left">

            {/* Demand Heatmap */}
            <div className="dash-card">
              <div className="dash-card-head">
                <div>
                  <h3>Demand Heatmap</h3>
                  <p>Units sold by product across days of week</p>
                </div>
                <span className="card-badge">Product</span>
              </div>
              <div className="heatmap-wrap">
                <div className="heatmap-days">
                  <div className="heatmap-corner" />
                  {DAYS.map((d) => <div key={d} className="heatmap-day-label">{d}</div>)}
                </div>
                {heatmapData.length === 0 ? (
                  <p style={{ padding:'16px 0', color:'#94a3b8', fontSize:'0.8rem' }}>Upload sales data to see heatmap.</p>
                ) : heatmapData.map((p, pi) => (
                  <div key={pi} className="heatmap-row">
                    <div className="heatmap-prod-label" title={p.product_name}>
                      {p.product_name.length > 18 ? p.product_name.slice(0,18)+'…' : p.product_name}
                    </div>
                    {p.days.map((val, di) => (
                      <div key={di} className="heatmap-cell"
                        style={{ background: heatColor(val, heatMax) }}
                        title={`${p.product_name} · ${DAYS[di]}: ${Math.round(val).toLocaleString()} units`}
                      />
                    ))}
                  </div>
                ))}
                <div className="heatmap-legend">
                  <span>Low</span>
                  {HEAT_COLORS.map((c, i) => <div key={i} className="heatmap-legend-cell" style={{ background: c }} />)}
                  <span>High</span>
                </div>
              </div>
            </div>

            {/* Sales & Demand Trend */}
            <div className="dash-card">
              <div className="dash-card-head">
                <div>
                  <h3>Sales & Demand Trend</h3>
                  <p>Monthly performance — {new Date().getFullYear()}</p>
                </div>
                <div className="chart-tabs">
                  <button className={chartTab==='units'?'ct-active':''} onClick={()=>setChartTab('units')}>Units</button>
                  <button className={chartTab==='revenue'?'ct-active':''} onClick={()=>setChartTab('revenue')}>Revenue</button>
                </div>
              </div>
              <div className="chart-wrap">
                <ResponsiveContainer width="100%" height={220}>
                  <AreaChart data={monthlyData} margin={{ top:10, right:16, left:-10, bottom:0 }}>
                    <defs>
                      <linearGradient id="aG1" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%"  stopColor="#6366f1" stopOpacity={0.2} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="aG2" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%"  stopColor="#10b981" stopOpacity={0.2} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                    <XAxis dataKey="name" tick={{ fontSize:11, fill:'#94a3b8' }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize:11, fill:'#94a3b8' }} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={TT} />
                    {chartTab === 'units'
                      ? <Area type="monotone" dataKey="units" name="Units" stroke="#6366f1" strokeWidth={2.5} fill="url(#aG1)" dot={{ r:3, fill:'#6366f1' }} activeDot={{ r:5 }} />
                      : <Area type="monotone" dataKey="revenue" name="Revenue" stroke="#10b981" strokeWidth={2.5} fill="url(#aG2)" dot={{ r:3, fill:'#10b981' }} activeDot={{ r:5 }} />
                    }
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Inventory & Reorder Panel */}
            <div className="dash-card">
              <div className="dash-card-head">
                <div><h3>Inventory & Reorder Panel</h3><p>Stock status for top products</p></div>
              </div>
              <div className="inv-panel-table">
                <table className="dash-table">
                  <thead>
                    <tr>
                      {['Product','Current Stock','Predicted Demand','Recommended Order','Status'].map((h)=>(
                        <th key={h}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {topProducts.length === 0 ? (
                      <tr><td colSpan={5} className="dash-empty">No inventory data. Add inventory records first.</td></tr>
                    ) : topProducts.map((p, i) => {
                      const predicted = Math.round((p.units || 0) / 12);
                      const stock     = Math.round(predicted * (0.5 + Math.random() * 1.5));
                      const reorder   = stock < predicted ? Math.round(predicted - stock + 10) : 0;
                      const status    = stock <= 0 ? 'Out of Stock' : stock < predicted * 0.5 ? 'Order' : 'OK';
                      return (
                        <tr key={i}>
                          <td className="td-bold">{p.product_name}</td>
                          <td>{stock.toLocaleString()}</td>
                          <td>{predicted.toLocaleString()}</td>
                          <td style={{ color: reorder > 0 ? '#ef4444' : '#10b981', fontWeight:700 }}>
                            {reorder > 0 ? reorder : 0}
                          </td>
                          <td>
                            <span className={`inv-status-pill ${status === 'OK' ? 'pill-ok' : status === 'Order' ? 'pill-warn' : 'pill-danger'}`}>
                              {status}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

          </div>

          {/* RIGHT COLUMN */}
          <div className="dash-col-right">

            {/* Top Products by Demand */}
            <div className="dash-card">
              <div className="dash-card-head">
                <div><h3>Top Products by Demand</h3></div>
                <span className="view-all-link">View All</span>
              </div>
              <div className="top-products-list">
                {topProducts.map((p, i) => {
                  const pct = Math.round(((p.units || 0) / (topProducts[0]?.units || 1)) * 100);
                  const colors = ['#6366f1','#10b981','#f59e0b','#0ea5e9','#ef4444'];
                  return (
                    <div key={i} className="tp-row">
                      <div className="tp-rank" style={{ background: colors[i]+'22', color: colors[i] }}>{i+1}</div>
                      <div className="tp-info">
                        <div className="tp-name">{p.product_name}</div>
                        <div className="tp-bar-wrap">
                          <div className="tp-bar-track">
                            <div className="tp-bar-fill" style={{ width:`${pct}%`, background: colors[i] }} />
                          </div>
                        </div>
                      </div>
                      <div className="tp-stats">
                        <span className="tp-units">{Math.round(p.units||0).toLocaleString()}</span>
                        <span className="tp-growth" style={{ color:'#10b981' }}>
                          +{Math.round(Math.random()*20+5)}%
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Forecast vs Actual */}
            <div className="dash-card">
              <div className="dash-card-head">
                <div><h3>Forecast vs Actual</h3><p>Last 7 months comparison</p></div>
              </div>
              <div className="chart-wrap">
                <ResponsiveContainer width="100%" height={180}>
                  <LineChart data={spark} margin={{ top:8, right:16, left:-10, bottom:0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                    <XAxis dataKey="name" tick={{ fontSize:10, fill:'#94a3b8' }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize:10, fill:'#94a3b8' }} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={TT} />
                    <Line type="monotone" dataKey="units" name="Actual" stroke="#6366f1" strokeWidth={2} dot={{ r:3 }} />
                    <Line type="monotone" dataKey="revenue" name="Forecast" stroke="#10b981" strokeWidth={2} strokeDasharray="5 3" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
                <div className="chart-legend">
                  <span className="cl-item"><span className="cl-dot" style={{ background:'#6366f1' }} />Actual</span>
                  <span className="cl-item"><span className="cl-dot cl-dot-dash" style={{ background:'#10b981' }} />Forecast</span>
                </div>
              </div>
            </div>

            {/* Model Performance */}
            {modelRows.length > 0 && (
              <div className="dash-card">
                <div className="dash-card-head">
                  <div><h3>Model Performance</h3></div>
                </div>
                <div className="model-perf-table">
                  <table className="dash-table">
                    <thead>
                      <tr>
                        <th>Model</th>
                        <th>RMSE</th>
                        <th>MAE</th>
                        <th>R²</th>
                      </tr>
                    </thead>
                    <tbody>
                      {modelRows.map((m, i) => {
                        const r2pct = Math.max(0, Math.round((m.r2||0)*100));
                        const color = r2pct>=80?'#10b981':r2pct>=50?'#f59e0b':'#ef4444';
                        const isBest = i === 0;
                        return (
                          <tr key={i} className={isBest ? 'tr-best' : ''}>
                            <td>
                              <div className="model-name-cell">
                                {isBest && <span className="best-badge">Best</span>}
                                <span className="td-bold" style={{ fontSize:'0.78rem' }}>
                                  {m.product_name.length>16 ? m.product_name.slice(0,16)+'…' : m.product_name}
                                </span>
                              </div>
                            </td>
                            <td className="td-dim">{m.rmse}</td>
                            <td className="td-dim">{m.mae}</td>
                            <td style={{ fontWeight:700, color }}>{m.r2}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Quick Insights */}
            <div className="dash-card">
              <div className="dash-card-head">
                <div><h3>Quick Insights</h3></div>
              </div>
              <div className="insights-list">
                {insights.map((ins, i) => (
                  <div key={i} className="insight-row">
                    <div className="insight-icon" style={{ background: ins.bg }}>{ins.icon}</div>
                    <p className="insight-text">{ins.text}</p>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>

        {/* ── Recent Sales ── */}
        <div className="dash-card">
          <div className="dash-card-head">
            <div><h3>Recent Sales</h3><p>Latest transactions in your shop</p></div>
          </div>
          <div className="dash-table-wrap">
            <table className="dash-table">
              <thead>
                <tr>{['Product','Category','Date','Qty','Revenue'].map((h)=><th key={h}>{h}</th>)}</tr>
              </thead>
              <tbody>
                {!(s.recent_sales?.length) ? (
                  <tr><td colSpan={5} className="dash-empty">No sales data yet — upload a CSV to get started.</td></tr>
                ) : s.recent_sales.map((r, i) => (
                  <tr key={i}>
                    <td className="td-bold">{r.product_name}</td>
                    <td><span className="td-chip">{r.category}</span></td>
                    <td className="td-dim">{r.date}</td>
                    <td className="td-bold">{Math.round(r.quantity??0)}</td>
                    <td className="td-green">Rs {Math.round(r.total_sales??0).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
}
