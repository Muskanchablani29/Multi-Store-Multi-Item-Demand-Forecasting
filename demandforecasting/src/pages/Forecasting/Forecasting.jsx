import { useState, useEffect } from 'react';
import { shopsAPI, productsAPI, mlAPI } from '../../services/api';
import ActualVsPredictedChart from '../../Components/charts/ActualVsPredictedChart';
import ForecastChart from '../../Components/charts/ForecastChart';
import MetricsCard from './MetricsCard';
import '../../Components/charts/charts.css';
import './Forecasting.css';

export default function Forecasting() {
  const [shops, setShops] = useState([]);
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState({ shop_id: '', product_id: '', model_type: 'LSTM', steps: 30 });
  const [trainResult, setTrainResult] = useState(null);
  const [forecastResult, setForecastResult] = useState(null);
  const [loading, setLoading] = useState({ train: false, forecast: false });
  const [error, setError] = useState('');

  useEffect(() => {
    shopsAPI.getAll().then((r) => setShops(r.data));
    productsAPI.getAll().then((r) => setProducts(r.data));
  }, []);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleTrain = async () => {
    setError('');
    setLoading({ ...loading, train: true });
    try {
      const res = await mlAPI.train(form);
      setTrainResult(res.data);
    } catch (e) {
      setError(e.response?.data?.error || 'Training failed.');
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
    } catch (e) {
      setError(e.response?.data?.error || 'Forecasting failed.');
    } finally {
      setLoading({ ...loading, forecast: false });
    }
  };

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
            <label>Product</label>
            <select name="product_id" value={form.product_id} onChange={handleChange}>
              <option value="">Select product...</option>
              {products.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>

          <div className="form-group">
            <label>Model Type</label>
            <div className="model-toggle">
              {['LSTM', 'GRU'].map((m) => (
                <button
                  key={m}
                  className={`toggle-btn ${form.model_type === m ? 'active' : ''}`}
                  onClick={() => setForm({ ...form, model_type: m })}
                >
                  {m}
                </button>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>Forecast Days: <strong>{form.steps}</strong></label>
            <input
              type="range" name="steps"
              min="7" max="90" step="1"
              value={form.steps}
              onChange={handleChange}
            />
          </div>

          {error && <div className="error-msg">{error}</div>}

          <button
            className="btn-primary"
            onClick={handleTrain}
            disabled={!form.shop_id || !form.product_id || loading.train}
          >
            {loading.train ? 'Training...' : `Train ${form.model_type} Model`}
          </button>

          <button
            className="btn-secondary"
            onClick={handleForecast}
            disabled={!form.shop_id || !form.product_id || loading.forecast}
          >
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
