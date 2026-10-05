import { useState, useEffect } from 'react';
import { shopsAPI, productsAPI, mlAPI, inventoryAPI } from '../../services/api';
import ActualVsPredictedChart from '../../Components/charts/ActualVsPredictedChart';
import ForecastChart from '../../Components/charts/ForecastChart';
import MetricsCard from './MetricsCard';
import '../../Components/charts/charts.css';
import './Forecasting.css';

export default function Forecasting() {
  const [shops, setShops] = useState([]);
  const [allProducts, setAllProducts] = useState([]);
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState({ shop_id: '', product_id: '', model_type: 'LSTM', steps: 30, category: '' });
  const [trainResult, setTrainResult] = useState(null);
  const [forecastResult, setForecastResult] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState({ train: false, forecast: false });
  const [error, setError] = useState('');
  const [dataInfo, setDataInfo] = useState(null);

  useEffect(() => {
    shopsAPI.getAll().then((r) => setShops(r.data));
    productsAPI.getAll().then((r) => {
      setAllProducts(r.data);
      const cats = [...new Set(r.data.map((p) => p.category).filter(Boolean))].sort();
      setCategories(cats);
      setProducts(r.data);
    });
  }, []);

  const handleChange = (e) => {
    const updated = { ...form, [e.target.name]: e.target.value };
    if (e.target.name === 'category') {
      const filtered = e.target.value
        ? allProducts.filter((p) => p.category === e.target.value)
        : allProducts;
      setProducts(filtered);
      updated.product_id = '';
    }
    setForm(updated);
  };

  const handleTrain = async () => {
    setError('');
    setLoading({ ...loading, train: true });
    try {
      const res = await mlAPI.train(form);
      setTrainResult(res.data);
      setDataInfo({
        total_days: res.data.total_days,
        train_days: res.data.train_days,
        test_days:  res.data.test_days,
      });
    } catch (e) {
      setError(e.friendlyMessage || e.response?.data?.error || 'Training failed.');
    } finally {
      setLoading({ ...loading, train: false });
    }
  };

  const handleForecast = async () => {
    setError('');
    setLoading({ ...loading, forecast: true });
    try {
      const res = await mlAPI.forecast(form);
      setForecastResult(res.data.forecasts);
      // Fetch inventory recommendation
      try {
        const rec = await inventoryAPI.getRecommendation({
          shop_id: form.shop_id,
          product_id: form.product_id,
          model_type: form.model_type,
        });
        setRecommendation(rec.data);
      } catch (_) {
        setRecommendation(null);
      }
    } catch (e) {
      setError(e.friendlyMessage || e.response?.data?.error || 'Forecasting failed.');
    } finally {
      setLoading({ ...loading, forecast: false });
    }
  };

  const selectedProduct = allProducts.find((p) => String(p.id) === String(form.product_id));

  return (
    <div className="page">
      <div className="page-header">
        <h1>Demand Forecasting</h1>
        <p>Train LSTM/GRU models and generate future demand forecasts</p>
      </div>

      <div className="forecasting-layout">
        <div className="forecast-controls">
          <h3>Configuration</h3>

          <div className="form-group">
            <label>Shop</label>
            <select name="shop_id" value={form.shop_id} onChange={handleChange}>
              <option value="">Select shop...</option>
              {shops.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
          </div>

          <div className="form-group">
            <label>Category</label>
            <select name="category" value={form.category} onChange={handleChange}>
              <option value="">All Categories</option>
              {categories.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>

          <div className="form-group">
            <label>Product</label>
            <select name="product_id" value={form.product_id} onChange={handleChange}>
              <option value="">Select product...</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>{p.name} {p.brand ? `(${p.brand})` : ''}</option>
              ))}
            </select>
          </div>

          {selectedProduct && (
            <div className="product-info-box">
              <div className="pi-row"><span>Brand</span><strong>{selectedProduct.brand || '—'}</strong></div>
              <div className="pi-row"><span>Gender</span><strong>{selectedProduct.gender || '—'}</strong></div>
              <div className="pi-row"><span>Size</span><strong>{selectedProduct.size || '—'}</strong></div>
              <div className="pi-row"><span>Price</span><strong>₹{selectedProduct.unit_price || '—'}</strong></div>
            </div>
          )}

          <div className="form-group">
            <label>Model Type</label>
            <div className="model-toggle">
              {['LSTM', 'GRU'].map((m) => (
                <button key={m}
                  className={`toggle-btn ${form.model_type === m ? 'active' : ''}`}
                  onClick={() => setForm({ ...form, model_type: m })}>{m}</button>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>Forecast Days: <strong>{form.steps}</strong></label>
            <input type="range" name="steps" min="7" max="90" step="1"
              value={form.steps} onChange={handleChange} />
          </div>

          {error && <div className="error-msg">{error}</div>}

          {dataInfo && (
            <div className="data-info-box">
              <div className="di-row"><span>Total Days</span><strong>{dataInfo.total_days}</strong></div>
              <div className="di-row"><span>Train Days</span><strong>{dataInfo.train_days}</strong></div>
              <div className="di-row"><span>Test Days</span><strong>{dataInfo.test_days}</strong></div>
              {dataInfo.total_days < 180 && (
                <p className="di-warn">Upload the full 365-day dataset for best accuracy.</p>
              )}
            </div>
          )}

          <button className="btn-primary" onClick={handleTrain}
            disabled={!form.shop_id || !form.product_id || loading.train}>
            {loading.train ? 'Training...' : `Train ${form.model_type} Model`}
          </button>

          <button className="btn-secondary" onClick={handleForecast}
            disabled={!form.shop_id || !form.product_id || loading.forecast}>
            {loading.forecast ? 'Forecasting...' : 'Generate Forecast'}
          </button>
        </div>

        <div className="forecast-results">
          {trainResult && (
            <>
              <MetricsCard metrics={trainResult.metrics} modelType={form.model_type} />
              <ActualVsPredictedChart
                dates={trainResult.dates}
                actual={trainResult.actual}
                predicted={trainResult.predicted}
                title={`${form.model_type} — Actual vs Predicted`}
              />
            </>
          )}
          {forecastResult && (
            <ForecastChart
              forecasts={forecastResult}
              title={`${form.model_type} — ${form.steps}-Day Forecast`}
            />
          )}
          {recommendation && (
            <div className="recommendation-card">
              <h3>Inventory Recommendation</h3>
              <div className="rec-grid">
                <div className="rec-item"><span>Current Stock</span><strong>{recommendation.current_stock}</strong></div>
                <div className="rec-item"><span>Predicted Demand</span><strong>{recommendation.predicted_demand}</strong></div>
                <div className="rec-item"><span>Safety Stock</span><strong>{recommendation.safety_stock}</strong></div>
                <div className="rec-item"><span>Reorder Point</span><strong>{recommendation.reorder_point}</strong></div>
                <div className="rec-item"><span>Lead Time</span><strong>{recommendation.lead_time_days} days</strong></div>
                <div className="rec-item"><span>Recommended Order</span><strong className="highlight">{recommendation.recommended_order_qty} units</strong></div>
              </div>
              <div className={`inv-status-badge status-${recommendation.inventory_status?.toLowerCase().replace(/ /g, '-')}`}>
                {recommendation.inventory_status}
              </div>
            </div>
          )}
          {!trainResult && !forecastResult && (
            <div className="empty-state">
              <p>Configure and train a model to see results here.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
