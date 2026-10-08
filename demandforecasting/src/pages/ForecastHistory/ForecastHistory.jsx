import { useState, useEffect } from 'react';
import { productsAPI, forecastsAPI } from '../../services/api';
import ForecastChart from '../../Components/charts/ForecastChart';
import DataTable from '../../Components/tables/DataTable';
import '../../Components/charts/charts.css';
import './ForecastHistory.css';

const columns = [
  { key: 'shop_name',     label: 'Shop' },
  { key: 'product_name',  label: 'Product' },
  { key: 'category',      label: 'Category' },
  { key: 'forecast_date', label: 'Forecast Date' },
  { key: 'predicted_qty', label: 'Predicted Qty', render: (v) => v?.toFixed(2) },
  { key: 'actual_qty',    label: 'Actual Qty',    render: (v) => v != null ? v.toFixed(2) : '—' },
  { key: 'created_at',    label: 'Created',       render: (v) => v ? new Date(v).toLocaleDateString() : '—' },
];

export default function ForecastHistory() {
  const [shops, setShops] = useState([]);
  const [products, setProducts] = useState([]);
  const [allProducts, setAllProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [forecasts, setForecasts] = useState([]);
  const [filters, setFilters] = useState({ product_id: '', category: '' });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    shopsAPI.getAll().then((r) => setShops(r.data));
    productsAPI.getAll().then((r) => {
      setAllProducts(r.data);
      setProducts(r.data);
      const cats = [...new Set(r.data.map((p) => p.category).filter(Boolean))].sort();
      setCategories(cats);
    });
    loadForecasts({});
  }, []);

  const loadForecasts = (params) => {
    setLoading(true);
    forecastsAPI.getResults(params).then((r) => setForecasts(r.data)).finally(() => setLoading(false));
  };

  const handleFilter = (e) => {
    const updated = { ...filters, [e.target.name]: e.target.value };
    if (e.target.name === 'category') {
      const filtered = e.target.value
        ? allProducts.filter((p) => p.category === e.target.value)
        : allProducts;
      setProducts(filtered);
      updated.product_id = '';
    }
    setFilters(updated);
    const params = Object.fromEntries(Object.entries(updated).filter(([k, v]) => v && k !== 'category'));
    loadForecasts(params);
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Forecast History</h1>
        <p>View all past LSTM forecasts</p>
      </div>

      <div className="history-filters">
        <select name="category" value={filters.category} onChange={handleFilter}>
          <option value="">All Categories</option>
          {categories.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <select name="product_id" value={filters.product_id} onChange={handleFilter}>
          <option value="">All Products</option>
          {products.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
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
