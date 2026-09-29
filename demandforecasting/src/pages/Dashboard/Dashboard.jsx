import { useEffect, useState } from 'react';
import { FiShoppingBag, FiPackage, FiTrendingUp, FiAlertTriangle } from 'react-icons/fi';
import StatCard from '../../Components/cards/StatCard';
import DataTable from '../../Components/tables/DataTable';
import { shopsAPI, productsAPI, salesAPI, inventoryAPI } from '../../services/api';
import './Dashboard.css';

const recentSalesCols = [
  { key: 'shop_name', label: 'Shop' },
  { key: 'product_name', label: 'Product' },
  { key: 'date', label: 'Date' },
  { key: 'quantity', label: 'Qty', render: (v) => v?.toFixed(0) },
];

const alertCols = [
  { key: 'shop_name', label: 'Shop' },
  { key: 'product_name', label: 'Product' },
  { key: 'current_stock', label: 'Stock', render: (v) => v?.toFixed(0) },
  { key: 'reorder_point', label: 'Reorder At', render: (v) => v?.toFixed(0) },
  { key: 'needs_reorder', label: 'Status', render: (v) => (
    <span className={`badge ${v ? 'badge-danger' : 'badge-success'}`}>
      {v ? 'Reorder Now' : 'OK'}
    </span>
  )},
];

export default function Dashboard() {
  const [stats, setStats] = useState({ shops: 0, products: 0, sales: 0, alerts: 0 });
  const [recentSales, setRecentSales] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      shopsAPI.getAll(),
      productsAPI.getAll(),
      salesAPI.getAll(),
      inventoryAPI.getReorderAlerts(),
    ]).then(([shops, products, sales, alertsRes]) => {
      setStats({
        shops: shops.data.length,
        products: products.data.length,
        sales: sales.data.length,
        alerts: alertsRes.data.length,
      });
      setRecentSales(sales.data.slice(-10).reverse());
      setAlerts(alertsRes.data);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page-loading">Loading dashboard...</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Overview of your demand forecasting system</p>
      </div>

      <div className="stats-row">
        <StatCard title="Total Shops" value={stats.shops} icon={<FiShoppingBag />} color="#6c63ff" />
        <StatCard title="Total Products" value={stats.products} icon={<FiPackage />} color="#10b981" />
        <StatCard title="Sales Records" value={stats.sales} icon={<FiTrendingUp />} color="#f59e0b" />
        <StatCard title="Reorder Alerts" value={stats.alerts} icon={<FiAlertTriangle />} color="#ef4444" />
      </div>

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
