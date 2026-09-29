import { useState, useEffect } from 'react';
import { shopsAPI, productsAPI, forecastsAPI } from '../../services/api';
import ForecastChart from '../../Components/charts/ForecastChart';
import DataTable from '../../Components/tables/DataTable';
import '../../Components/charts/charts.css';
import './ForecastHistory.css';

const columns = [
  { key: 'shop_name', label: 'Shop' },
  { key: 'product_name', label: 'Product' },
  { key: 'model_type', label: 'Model', render: (v) => <span className={`model-badge ${v?.toLowerCase()}`}>{v}</span> },
  { key: 'forecast_date', label: 'Forecast Date' },
  { key: 'predicted_qty', label: 'Predicted Qty', render: (v) => v?.toFixed(2) },
  { key: 'actual_qty', label: 'Actual Qty', render: (v) => v != null ? v.toFixed(2) : '—' },
  { key: 'created_at', label: 'Created', render: (v) => v ? new Date(v).toLocaleDateString() : '—' },
];

export default function ForecastHistory() {
  const [shops, setShops] = useState([]);
  const [products, setProducts] = useState([]);
  const [forecasts, setForecasts] = useState([]);
  const [filters, setFilters] = useState({ shop_id: '', product_id: '', model_type: '' });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    shopsAPI.getAll().then((r) => setShops(r.data));
    productsAPI.getAll().then((r) => setProducts(r.data));
    loadForecasts({});
  }, []);

  const loadForecasts = (params) => {
    setLoading(true);
    forecastsAPI.getResults(params).then((r) => setForecasts(r.data)).finally(() => setLoading(false));
  };

  const handleFilter = (e) => {
    const updated = { ...filters, [e.target.name]: e.target.value };
    setFilters(updated);
    const params = Object.fromEntries(Object.entries(updated).filter(([, v]) => v));
    loadForecasts(params);
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Forecast History</h1>
        <p>View all past forecasts and compare with actual sales</p>
      </div>

      <div className="history-filters">
        <select name="shop_id" value={filters.shop_id} onChange={handleFilter}>
          <option value="">All Shops</option>
          {shops.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
        <select name="product_id" value={filters.product_id} onChange={handleFilter}>
          <option value="">All Products</option>
          {products.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
        <select name="model_type" value={filters.model_type} onChange={handleFilter}>
          <option value="">All Models</option>
          <option value="LSTM">LSTM</option>
          <option value="GRU">GRU</option>
        </select>
      </div>

      {forecasts.length > 0 && (
        <ForecastChart forecasts={forecasts.slice(0, 60)} title="Forecast Trend" />
      )}

      {loading ? (
        <div className="page-loading">Loading forecasts...</div>
      ) : (
        <DataTable columns={columns} data={forecasts} emptyMessage="No forecasts found. Generate forecasts from the Forecasting page." />
      )}
    </div>
  );
}
