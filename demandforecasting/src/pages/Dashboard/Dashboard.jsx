import { useEffect, useState } from 'react';
import {
  FiShoppingBag, FiPackage, FiTrendingUp, FiAlertTriangle,
  FiDollarSign, FiBarChart2, FiLayers, FiActivity
} from 'react-icons/fi';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import StatCard from '../../Components/cards/StatCard';
import DataTable from '../../Components/tables/DataTable';
import { salesAPI, inventoryAPI } from '../../services/api';
import './Dashboard.css';

const COLORS = ['#6c63ff','#10b981','#f59e0b','#ef4444','#3b82f6','#8b5cf6','#ec4899','#14b8a6'];

const recentSalesCols = [
  { key: 'shop_name',    label: 'Shop' },
  { key: 'product_name', label: 'Product' },
  { key: 'category',     label: 'Category' },
  { key: 'date',         label: 'Date' },
  { key: 'quantity',     label: 'Qty',     render: (v) => Math.round(v ?? 0) },
  { key: 'total_sales',  label: 'Revenue', render: (v) => v ? `₹${Math.round(v).toLocaleString()}` : '—' },
];

const alertCols = [
  { key: 'shop_name',        label: 'Shop' },
  { key: 'product_name',     label: 'Product' },
  { key: 'current_stock',    label: 'Stock',      render: (v) => Math.round(v ?? 0) },
  { key: 'reorder_point',    label: 'Reorder At', render: (v) => Math.round(v ?? 0) },
  { key: 'inventory_status', label: 'Status',     render: (v) => (
    <span className={`badge ${v === 'Sufficient Stock' ? 'badge-success' : 'badge-danger'}`}>{v}</span>
  )},
];

export default function Dashboard() {
  const [salesStats, setSalesStats] = useState(null);
  const [alerts, setAlerts]         = useState([]);
  const [loading, setLoading]       = useState(true);
  const [error, setError]           = useState('');

  useEffect(() => {
    // Only 2 API calls — stats includes shops/products/recent_sales counts
    Promise.all([
      salesAPI.getStats(),
      inventoryAPI.getReorderAlerts(),
    ])
      .then(([statsRes, alertsRes]) => {
        setSalesStats(statsRes.data);
        setAlerts(alertsRes.data);
      })
      .catch(() => setError('Failed to load dashboard data.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page-loading">Loading dashboard...</div>;
  if (error)   return <div className="page-loading" style={{ color: '#ef4444' }}>{error}</div>;

  const s = salesStats || {};

  const categorySalesData = (s.category_sales || []).map((c) => ({
    name:    c.product__category || 'Unknown',
    units:   Math.round(c.units   || 0),
    revenue: Math.round(c.revenue || 0),
  }));

  const shopSalesData = (s.shop_sales || []).map((sh) => ({
    name:    (sh.shop__name || '').replace('Thakur Footwear', 'TF').replace('Pune Footwear - ', ''),
    revenue: Math.round(sh.revenue || 0),
  }));

  const brandData = (s.brand_sales || []).slice(0, 8).map((b) => ({
    name:  b.product__brand || 'Unknown',
    value: Math.round(b.units || 0),
  }));

  const seasonData = (s.season_sales || []).map((se) => ({
    name:  se.season || 'Unknown',
    units: Math.round(se.units || 0),
  }));

  const promoData = (s.promo_sales || []).map((p) => ({
    name:  p.promotion ? 'Promotion' : 'Normal',
    units: Math.round(p.units || 0),
  }));

  return (
    <div className="page">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Thakur Footwear — demand forecasting overview</p>
      </div>

      {/* Stat cards */}
      <div className="stats-row">
        <StatCard title="Total Shops"    value={s.total_shops    ?? 0} icon={<FiShoppingBag />} color="#6c63ff" />
        <StatCard title="Total Products" value={s.total_products ?? 0} icon={<FiPackage />}     color="#10b981" />
        <StatCard title="Total Revenue"  value={s.total_revenue  ? `₹${(s.total_revenue/100000).toFixed(1)}L` : '—'} icon={<FiDollarSign />}  color="#f59e0b" />
        <StatCard title="Units Sold"     value={s.total_units    ? Math.round(s.total_units).toLocaleString() : '—'} icon={<FiTrendingUp />}  color="#3b82f6" />
        <StatCard title="Total Profit"   value={s.total_profit   ? `₹${(s.total_profit/100000).toFixed(1)}L` : '—'} icon={<FiActivity />}    color="#8b5cf6" />
        <StatCard title="Sales Records"  value={s.total_records  ? s.total_records.toLocaleString() : '—'}           icon={<FiBarChart2 />}   color="#14b8a6" />
        <StatCard title="Low Stock"      value={alerts.length}   icon={<FiAlertTriangle />} color="#ef4444" />
        <StatCard title="Categories"     value={categorySalesData.length} icon={<FiLayers />} color="#ec4899" />
      </div>

      {/* Charts */}
      {s.category_sales && (
        <div className="dashboard-charts">
          <div className="chart-card">
            <h3>Sales by Category</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={categorySalesData}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v) => v.toLocaleString()} />
                <Bar dataKey="units" fill="#6c63ff" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3>Shop Revenue</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={shopSalesData} layout="vertical">
                <XAxis type="number" tick={{ fontSize: 10 }} />
                <YAxis dataKey="name" type="category" width={80} tick={{ fontSize: 10 }} />
                <Tooltip formatter={(v) => `₹${v.toLocaleString()}`} />
                <Bar dataKey="revenue" fill="#10b981" radius={[0,4,4,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3>Brand Share (Units)</h3>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={brandData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name }) => name}>
                  {brandData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3>Seasonal Sales</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={seasonData}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v) => v.toLocaleString()} />
                <Bar dataKey="units" fill="#f59e0b" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3>Promotion Impact</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={promoData}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v) => v.toLocaleString()} />
                <Bar dataKey="units" fill="#ec4899" radius={[4,4,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3>Top 10 Products</h3>
            <div className="top-products-list">
              {(s.top_products || []).map((p, i) => (
                <div key={i} className="top-product-row">
                  <span className="rank">#{i + 1}</span>
                  <span className="prod-name">{p.product__name}</span>
                  <span className="prod-cat">{p.product__category}</span>
                  <span className="prod-units">{Math.round(p.units).toLocaleString()} units</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tables */}
      <div className="dashboard-grid">
        <div className="dashboard-section">
          <h2 className="section-title">Recent Sales</h2>
          <DataTable
            columns={recentSalesCols}
            data={s.recent_sales || []}
            emptyMessage="No sales data yet. Upload a CSV."
          />
        </div>
        <div className="dashboard-section">
          <h2 className="section-title">Reorder Alerts</h2>
          <DataTable
            columns={alertCols}
            data={alerts}
            emptyMessage="No reorder alerts."
          />
        </div>
      </div>
    </div>
  );
}
