import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { productsAPI, mlAPI, inventoryAPI, forecastsAPI } from '../../services/api';
import ActualVsPredictedChart from '../../Components/charts/ActualVsPredictedChart';
import ForecastChart from '../../Components/charts/ForecastChart';
import MetricsCard from './MetricsCard';
import { FiTrendingUp, FiAward } from 'react-icons/fi';
import '../../Components/charts/charts.css';
import './Forecasting.css';

export default function Forecasting() {
  const location = useLocation();
  const [products, setProducts]       = useState([]);
  const [categories, setCategories]   = useState([]);
  const [form, setForm] = useState({ product_id: '', model_type: 'LSTM', steps: 30, category: '' });
  const [trainResult, setTrainResult]         = useState(null);
  const [forecastResult, setForecastResult]   = useState(null);
  const [recommendation, setRecommendation]   = useState(null);
  const [octResult, setOctResult]             = useState(null);
  const [loading, setLoading] = useState({ train: false, forecast: false, october: false });
  const [error, setError]     = useState('');
  const [dataInfo, setDataInfo] = useState(null);

  useEffect(() => {
    productsAPI.getAll().then((r) => {
      setProducts(r.data);
      const cats = [...new Set(r.data.map((p) => p.category).filter(Boolean))].sort();
      setCategories(cats);
    });
  }, []);

  useEffect(() => {
    if (!form.product_id) return;
    forecastsAPI.getResults({ product_id: form.product_id, model_type: form.model_type })
      .then((r) => {
        if (r.data?.length > 0) {
          setForecastResult(r.data.map((f) => ({ date: f.forecast_date, predicted_qty: f.predicted_qty })));
        } else {
          setForecastResult(null);
        }
      })
      .catch(() => setForecastResult(null));
  }, [form.product_id, form.model_type]);

  const filteredProducts = form.category
    ? products.filter((p) => p.category === form.category)
    : products;

  const handleChange = (e) => {
    const updated = { ...form, [e.target.name]: e.target.value };
    if (e.target.name === 'category') updated.product_id = '';
    setForm(updated);
  };

  const handleTrain = async () => {
    setError('');
    setLoading((l) => ({ ...l, train: true }));
    try {
      const res = await mlAPI.train({ product_id: form.product_id, model_type: form.model_type });
      setTrainResult(res.data);
      setDataInfo({ total_days: res.data.total_days, train_days: res.data.train_days, test_days: res.data.test_days });
    } catch (e) {
      setError(e.response?.data?.error || 'Training failed.');
    } finally {
      setLoading((l) => ({ ...l, train: false }));
    }
  };

  const handleForecast = async () => {
    setError('');
    setLoading((l) => ({ ...l, forecast: true }));
    try {
      const res = await mlAPI.forecast({ product_id: form.product_id, model_type: form.model_type, steps: form.steps });
      setForecastResult(res.data.forecasts);
      try {
        const rec = await inventoryAPI.getRecommendation({ product_id: form.product_id, model_type: form.model_type });
        setRecommendation(rec.data);
      } catch (_) { setRecommendation(null); }
    } catch (e) {
      setError(e.response?.data?.error || 'Forecasting failed.');
    } finally {
      setLoading((l) => ({ ...l, forecast: false }));
    }
  };

  const handleOctoberForecast = async () => {
    setError('');
    setOctResult(null);
    setLoading((l) => ({ ...l, october: true }));
    try {
      const res = await mlAPI.octoberForecast({ model_type: form.model_type });
      const data = res.data;
      if (data.summary.trained === 0) {
        setError(
          `No products could be forecasted. Skipped: ${data.skipped.slice(0, 3).join(' | ')}${
            data.skipped.length > 3 ? ` ...+${data.skipped.length - 3} more` : ''
          }. Train models first using "Train ${form.model_type} (3 months)".`
        );
      } else {
        setOctResult(data);
      }
    } catch (e) {
      setError(e.response?.data?.error || 'October forecast failed.');
    } finally {
      setLoading((l) => ({ ...l, october: false }));
    }
  };

  const selectedProduct = products.find((p) => String(p.id) === String(form.product_id));

  // Pick the selected product's daily forecasts from octResult if available
  const octProductForecast = octResult?.top_demand_products?.find(
    (p) => String(p.product_id) === String(form.product_id)
  );

  return (
    <div className="page">
      <div className="page-header">
        <h1>Demand Forecasting</h1>
        <p>Train on last 3 months · Forecast October sales · Rank top demand products</p>
      </div>

      <div className="forecasting-layout">
        <div className="forecast-controls">
          <h3>Configuration</h3>

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
              {filteredProducts.map((p) => (
                <option key={p.id} value={p.id}>{p.name}{p.brand ? ` (${p.brand})` : ''}</option>
              ))}
            </select>
          </div>

          {selectedProduct && (
            <div className="product-info-box">
              <div className="pi-row"><span>Brand</span><strong>{selectedProduct.brand || '—'}</strong></div>
              <div className="pi-row"><span>Category</span><strong>{selectedProduct.category || '—'}</strong></div>
              <div className="pi-row"><span>Price</span><strong>Rs {selectedProduct.unit_price || '—'}</strong></div>
            </div>
          )}

          <div className="form-group">
            <label>Forecast Days: <strong>{form.steps}</strong></label>
            <input type="range" name="steps" min="7" max="90" step="1"
              value={form.steps} onChange={handleChange} />
          </div>

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

          {error && <div className="error-msg">{error}</div>}

          {dataInfo && (
            <div className="data-info-box">
              <div className="di-row"><span>Total Days</span><strong>{dataInfo.total_days}</strong></div>
              <div className="di-row"><span>Train Days</span><strong>{dataInfo.train_days}</strong></div>
              <div className="di-row"><span>Test Days</span><strong>{dataInfo.test_days}</strong></div>
            </div>
          )}

          <button className="btn-primary" onClick={handleTrain}
            disabled={!form.product_id || loading.train}>
            {loading.train ? 'Training...' : `Train ${form.model_type} (3 months)`}
          </button>

          <button className="btn-secondary" onClick={handleForecast}
            disabled={!form.product_id || loading.forecast}>
            {loading.forecast ? 'Forecasting...' : 'Generate Forecast'}
          </button>

          <button className="btn-october" onClick={handleOctoberForecast}
            disabled={loading.october}>
            {loading.october ? 'Forecasting...' : '📅 Forecast Next Month (All Products)'}
          </button>
        </div>

        <div className="forecast-results">
          {loading.october && (
            <div className="oct-loading">
              <div className="oct-spinner" />
              <p>Forecasting October sales for all products...<br/><small>First run trains models — this may take a few minutes.</small></p>
            </div>
          )}
          {trainResult && (
            <>
              <MetricsCard metrics={trainResult.metrics} modelType={form.model_type} />
              <ActualVsPredictedChart
                dates={trainResult.dates}
                actual={trainResult.actual}
                predicted={trainResult.predicted}
                title={`${form.model_type} — Actual vs Predicted (last 3 months)`}
              />
            </>
          )}

          {forecastResult && (
            <ForecastChart
              forecasts={forecastResult}
              title={`${form.model_type} — ${form.steps}-Day Forecast`}
            />
          )}

          {/* October forecast for selected product */}
          {octProductForecast && (
            <ForecastChart
              forecasts={octProductForecast.daily_forecasts}
              title={`October Forecast — ${octProductForecast.product_name}`}
            />
          )}

          {/* Top demand products for October */}
          {octResult && (
            <div className="oct-demand-card">
              <div className="oct-demand-header">
                <FiTrendingUp />
                <h3>{octResult.forecast_month} Top Demand Products</h3>
                <span className="oct-badge">Trained on last 3 months · {octResult.model_type}</span>
              </div>
              <div className="oct-summary">
                <span>Trained: <strong>{octResult.summary.trained}</strong></span>
                <span>Skipped: <strong>{octResult.summary.skipped}</strong></span>
              </div>
              <div className="oct-table-wrap">
                <table className="oct-table">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Product</th>
                      <th>Category</th>
                      <th>Brand</th>
                      <th>Oct Predicted Qty</th>
                      <th>Est. Revenue</th>
                      <th>RMSE</th>
                    </tr>
                  </thead>
                  <tbody>
                    {octResult.top_demand_products.map((p, i) => (
                      <tr key={p.product_id} className={i < 3 ? 'top-row' : ''}>
                        <td>
                          {i === 0 ? <FiAward className="rank-gold" /> :
                           i === 1 ? <FiAward className="rank-silver" /> :
                           i === 2 ? <FiAward className="rank-bronze" /> : i + 1}
                        </td>
                        <td className="prod-name">{p.product_name}</td>
                        <td>{p.category || '—'}</td>
                        <td>{p.brand || '—'}</td>
                        <td className="qty-cell"><strong>{Math.round(p.oct_predicted_qty)}</strong></td>
                        <td>Rs {Math.round(p.oct_predicted_qty * (p.unit_price || 0)).toLocaleString()}</td>
                        <td className="rmse-cell">{p.rmse}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
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

          {!trainResult && !forecastResult && !octResult && (
            <div className="empty-state">
              <p>Select a product and train a model, or click <strong>Forecast October</strong> to rank all products.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
