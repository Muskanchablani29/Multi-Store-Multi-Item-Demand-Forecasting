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
import { shopsAPI, productsAPI, salesAPI, inventoryAPI } from '../../services/api';
import './Dashboard.css';

const COLORS = ['#6c63ff','#10b981','#f59e0b','#ef4444','#3b82f6','#8b5cf6','#ec4899','#14b8a6'];

const recentSalesCols = [
  { key: 'shop_name', label: 'Shop' },
  { key: 'product_name', label: 'Product' },
  { key: 'category', label: 'Category' },
  { key: 'date', label: 'Date' },
  { key: 'quantity', label: 'Qty', render: (v) => v?.toFixed(0) },
  { key: 'total_sales', label: 'Revenue', render: (v) => v ? `₹${v.toFixed(0)}` : '—' },
];

const alertCols = [
  { key: 'shop_name', label: 'Shop' },
  { key: 'product_name', label: 'Product' },
  { key: 'current_stock', label: 'Stock', render: (v) => v?.toFixed(0) },
  { key: 'reorder_point', label: 'Reorder At', render: (v) => v?.toFixed(0) },
  { key: 'inventory_status', label: 'Status', render: (v) => (
    <span className={`badge ${v === 'Sufficient Stock' ? 'badge-success' : 'badge-danger'}`}>{v}</span>
  )},
];

export default function Dashboard() {
  const [stats, setStats] = useState({ shops: 0, products: 0, alerts: 0 });
  const [salesStats, setSalesStats] = useState(null);
  const [recentSales, setRecentSales] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      shopsAPI.getAll(),
      productsAPI.getAll(),
      salesAPI.getAll(),
      inventoryAPI.getReorderAlerts(),
      salesAPI.getStats(),
    ]).then(([shops, products, sales, alertsRes, statsRes]) => {
      setStats({
        shops: shops.data.length,
        products: products.data.length,
        alerts: alertsRes.data.length,
      });
      setRecentSales(sales.data.slice(-10).reverse());
      setAlerts(alertsRes.data);
      setSalesStats(statsRes.data);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page-loading">Loading dashboard...</div>;

  const categorySalesData = (salesStats?.category_sales || []).map((c) => ({
    name: c.product__category || 'Unknown',
    units: Math.round(c.units || 0),
    revenue: Math.round(c.revenue || 0),
  }));

  const shopSalesData = (salesStats?.shop_sales || []).map((s) => ({
    name: (s.shop__name || '').replace('Pune Footwear - ', ''),
    revenue: Math.round(s.revenue || 0),
  }));

  const brandData = (salesStats?.brand_sales || []).slice(0, 8).map((b) => ({
    name: b.product__brand || 'Unknown',
    value: Math.round(b.units || 0),
  }));

  const seasonData = (salesStats?.season_sales || []).map((s) => ({
    name: s.season || 'Unknown',
    units: Math.round(s.units || 0),
  }));

  const promoData = (salesStats?.promo_sales || []).map((p) => ({
    name: p.promotion ? 'Promotion' : 'Normal',
    units: Math.round(p.units || 0),
    revenue: Math.round(p.revenue || 0),
  }));

  return (
    <div className="page">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Footwear retail demand forecasting overview</p>
      </div>

      <div className="stats-row">
        <StatCard title="Total Shops" value={stats.shops} icon={<FiShoppingBag />} color="#6c63ff" />
        <StatCard title="Total Products" value={stats.products} icon={<FiPackage />} color="#10b981" />
        <StatCard title="Total Revenue" value={salesStats ? `₹${(salesStats.total_revenue/100000).toFixed(1)}L` : '—'} icon={<FiDollarSign />} color="#f59e0b" />
        <StatCard title="Units Sold" value={salesStats ? salesStats.total_units.toLocaleString() : '—'} icon={<FiTrendingUp />} color="#3b82f6" />
        <StatCard title="Total Profit" value={salesStats ? `₹${(salesStats.total_profit/100000).toFixed(1)}L` : '—'} icon={<FiActivity />} color="#8b5cf6" />
        <StatCard title="Sales Records" value={salesStats ? salesStats.total_records.toLocaleString() : '—'} icon={<FiBarChart2 />} color="#14b8a6" />
        <StatCard title="Low Stock Items" value={stats.alerts} icon={<FiAlertTriangle />} color="#ef4444" />
        <StatCard title="Categories" value={categorySalesData.length} icon={<FiLayers />} color="#ec4899" />
      </div>

      {salesStats && (
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
            <h3>Shop Performance (Revenue)</h3>
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
                <Bar dataKey="units" fill="#ec4899" radius={[4,4,0,0]} name="Units" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-card">
            <h3>Top 10 Products</h3>
            <div className="top-products-list">
              {(salesStats.top_products || []).map((p, i) => (
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

      <div className="dashboard-grid">
        <div className="dashboard-section">
          <h2 className="section-title">Recent Sales</h2>
          <DataTable columns={recentSalesCols} data={recentSales} emptyMessage="No sales data yet. Upload a CSV." />
        </div>
        <div className="dashboard-section">
          <h2 className="section-title">Reorder Alerts</h2>
          <DataTable columns={alertCols} data={alerts} emptyMessage="No reorder alerts." />
        </div>
      </div>
    </div>
  );
}
