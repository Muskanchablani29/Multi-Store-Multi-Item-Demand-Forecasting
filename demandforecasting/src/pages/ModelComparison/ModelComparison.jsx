import { useState, useEffect } from 'react';
import { shopsAPI, productsAPI, mlAPI, forecastsAPI } from '../../services/api';
import ActualVsPredictedChart from '../../Components/charts/ActualVsPredictedChart';
import DataTable from '../../Components/tables/DataTable';
import '../../Components/charts/charts.css';
import './ModelComparison.css';

const evalCols = [
  { key: 'shop_name', label: 'Shop' },
  { key: 'product_name', label: 'Product' },
  { key: 'model_type', label: 'Model' },
  { key: 'mae', label: 'MAE', render: (v) => v?.toFixed(4) },
  { key: 'mse', label: 'MSE', render: (v) => v?.toFixed(4) },
  { key: 'rmse', label: 'RMSE', render: (v) => v?.toFixed(4) },
  { key: 'r2', label: 'R²', render: (v) => v?.toFixed(4) },
];

export default function ModelComparison() {
  const [shops, setShops] = useState([]);
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState({ shop_id: '', product_id: '' });
  const [result, setResult] = useState(null);
  const [evaluations, setEvaluations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    shopsAPI.getAll().then((r) => setShops(r.data));
    productsAPI.getAll().then((r) => setProducts(r.data));
    forecastsAPI.getEvaluations().then((r) => setEvaluations(r.data));
  }, []);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleEvaluate = async () => {
    if (!form.shop_id || !form.product_id) return;
    setError('');
    setLoading(true);
    try {
      const res = await mlAPI.train({ ...form, model_type: 'LSTM' });
      setResult(res.data);
      const evalsRes = await forecastsAPI.getEvaluations({ shop_id: form.shop_id, product_id: form.product_id });
      setEvaluations(evalsRes.data);
    } catch (e) {
      setError(e.response?.data?.error || 'Evaluation failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Model Evaluation</h1>
        <p>Evaluate LSTM model performance for a shop-product combination</p>
      </div>

      <div className="comparison-controls">
        <select name="shop_id" value={form.shop_id} onChange={handleChange}>
          <option value="">Select shop...</option>
          {shops.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
        <select name="product_id" value={form.product_id} onChange={handleChange}>
          <option value="">Select product...</option>
          {products.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
        <button className="btn-primary" onClick={handleEvaluate} disabled={loading || !form.shop_id || !form.product_id}>
          {loading ? 'Evaluating...' : 'Evaluate LSTM'}
        </button>
      </div>

      {error && <div className="error-msg">{error}</div>}

      {result && (
        <>
          <div className="metrics-summary">
            {['mae', 'mse', 'rmse', 'r2'].map((k) => (
              <div key={k} className="metric-box">
                <span>{k.toUpperCase()}</span>
                <strong>{result.metrics?.[k]?.toFixed(4)}</strong>
              </div>
            ))}
          </div>
          <ActualVsPredictedChart
            dates={result.dates}
            actual={result.actual}
            predicted={result.predicted}
            title="LSTM — Actual vs Predicted"
          />
        </>
      )}

      <div className="section-title-row">
        <h2 className="section-title">Evaluation History</h2>
      </div>
      <DataTable columns={evalCols} data={evaluations} emptyMessage="No evaluations yet. Run an evaluation." />
    </div>
  );
}
