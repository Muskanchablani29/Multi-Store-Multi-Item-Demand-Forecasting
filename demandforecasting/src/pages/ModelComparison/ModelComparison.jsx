import { useState, useEffect } from 'react';
import { shopsAPI, productsAPI, mlAPI, forecastsAPI } from '../../services/api';
import MetricsComparisonChart from '../../Components/charts/MetricsComparisonChart';
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
  const [results, setResults] = useState({ lstm: null, gru: null });
  const [evaluations, setEvaluations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    shopsAPI.getAll().then((r) => setShops(r.data));
    productsAPI.getAll().then((r) => setProducts(r.data));
    forecastsAPI.getEvaluations().then((r) => setEvaluations(r.data));
  }, []);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleCompare = async () => {
    if (!form.shop_id || !form.product_id) return;
    setError('');
    setLoading(true);
    try {
      const [lstmRes, gruRes] = await Promise.all([
        mlAPI.train({ ...form, model_type: 'LSTM' }),
        mlAPI.train({ ...form, model_type: 'GRU' }),
      ]);
      setResults({ lstm: lstmRes.data, gru: gruRes.data });
      const evalsRes = await forecastsAPI.getEvaluations({ shop_id: form.shop_id, product_id: form.product_id });
      setEvaluations(evalsRes.data);
    } catch (e) {
      setError(e.response?.data?.error || 'Comparison failed.');
    } finally {
      setLoading(false);
    }
  };

  const lstmMetrics = results.lstm?.metrics;
  const gruMetrics = results.gru?.metrics;

  return (
    <div className="page">
      <div className="page-header">
        <h1>Model Comparison</h1>
        <p>Compare LSTM vs GRU performance on the same shop-product combination</p>
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
        <button className="btn-primary" onClick={handleCompare} disabled={loading || !form.shop_id || !form.product_id}>
          {loading ? 'Comparing...' : 'Compare Models'}
        </button>
      </div>

      {error && <div className="error-msg">{error}</div>}

      {(lstmMetrics || gruMetrics) && (
        <>
          <MetricsComparisonChart lstmMetrics={lstmMetrics} gruMetrics={gruMetrics} />

          <div className="comparison-charts">
            {results.lstm && (
              <ActualVsPredictedChart
                dates={results.lstm.dates}
                actual={results.lstm.actual}
                predicted={results.lstm.predicted}
                title="LSTM — Actual vs Predicted"
              />
            )}
            {results.gru && (
              <ActualVsPredictedChart
                dates={results.gru.dates}
                actual={results.gru.actual}
                predicted={results.gru.predicted}
                title="GRU — Actual vs Predicted"
              />
            )}
          </div>

          <div className="winner-banner">
            {lstmMetrics && gruMetrics && (() => {
              const lstmScore = lstmMetrics.rmse;
              const gruScore = gruMetrics.rmse;
              const winner = lstmScore < gruScore ? 'LSTM' : 'GRU';
              const diff = Math.abs(lstmScore - gruScore).toFixed(4);
              return (
                <p>
                  🏆 <strong>{winner}</strong> performs better with a lower RMSE by <strong>{diff}</strong>
                </p>
              );
            })()}
          </div>
        </>
      )}

      <div className="section-title-row">
        <h2 className="section-title">All Evaluations History</h2>
      </div>
      <DataTable columns={evalCols} data={evaluations} emptyMessage="No evaluations yet. Run a comparison." />
    </div>
  );
}
