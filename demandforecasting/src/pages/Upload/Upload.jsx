import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiUploadCloud, FiCheckCircle, FiAlertCircle, FiFile, FiCpu } from 'react-icons/fi';
import { salesAPI, mlAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import './Upload.css';

export default function Upload() {
  const { shop } = useAuth();
  const navigate = useNavigate();
  const [file, setFile]             = useState(null);
  const [status, setStatus]         = useState(null);
  const [uploading, setUploading]   = useState(false);
  const [training, setTraining]     = useState(false);
  const [trainSummary, setTrainSummary] = useState(null);
  const [progress, setProgress]     = useState(0);
  const inputRef = useRef();

  const handleDrop = (e) => {
    e.preventDefault();
    const dropped = e.dataTransfer.files[0];
    if (dropped?.name.endsWith('.csv')) setFile(dropped);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setStatus(null);
    setTrainSummary(null);
    setProgress(0);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await salesAPI.uploadCSV(formData, (evt) => {
        if (evt.total) setProgress(Math.round((evt.loaded / evt.total) * 100));
      });
      setStatus({
        type: 'success',
        message: `Successfully imported ${res.data.created.toLocaleString()} records into ${shop?.name}.`,
        details: res.data.errors,
      });
      setFile(null);
      setProgress(0);
      setUploading(false);

      // Auto-train all products on new data
      setTraining(true);
      try {
        const trainRes = await mlAPI.autoTrain({ model_type: 'LSTM', steps: 30 });
        setTrainSummary(trainRes.data.summary);
      } catch (trainErr) {
        setTrainSummary({ error: trainErr.response?.data?.error || 'Auto-training failed.' });
      } finally {
        setTraining(false);
      }
    } catch (err) {
      const errData = err.response?.data;
      setStatus({
        type: 'error',
        message: errData?.error || 'Upload failed.',
        details: errData?.errors || [],
      });
      setProgress(0);
      setUploading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Upload Monthly Sales Data</h1>
        <p>Upload your monthly CSV for <strong>{shop?.name || 'your shop'}</strong>. Models are automatically retrained on new data.</p>
      </div>

      <div className="upload-layout">
        <div className="upload-card">
          <h3 className="upload-card-title">Upload CSV File</h3>

          <div
            className={`drop-zone ${file ? 'has-file' : ''}`}
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => !uploading && !training && inputRef.current.click()}
          >
            <input ref={inputRef} type="file" accept=".csv" hidden
              onChange={(e) => setFile(e.target.files[0])} />
            {file ? (
              <>
                <FiFile className="drop-icon file-icon" />
                <p className="drop-filename">{file.name}</p>
                <span className="drop-meta">{(file.size / 1024 / 1024).toFixed(1)} MB · Click to change</span>
              </>
            ) : (
              <>
                <FiUploadCloud className="drop-icon" />
                <p className="drop-text">Drag & drop your CSV here</p>
                <span className="drop-hint">or click to browse</span>
              </>
            )}
          </div>

          {uploading && (
            <div className="progress-wrap">
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${progress}%` }} />
              </div>
              <span className="progress-label">
                {progress < 100 ? `Uploading... ${progress}%` : 'Processing records...'}
              </span>
            </div>
          )}

          {training && (
            <div className="training-status">
              <FiCpu className="spin-icon" />
              <span>Auto-training models on new data... this may take a few minutes.</span>
            </div>
          )}

          <button className="btn-primary" onClick={handleUpload} disabled={!file || uploading || training}>
            {uploading ? `Uploading... ${progress}%` : training ? 'Training models...' : 'Upload & Train'}
          </button>

          {status && (
            <div className={`upload-status ${status.type}`}>
              {status.type === 'success' ? <FiCheckCircle /> : <FiAlertCircle />}
              <div>
                <p>{status.message}</p>
                {status.details?.length > 0 && (
                  <details className="error-details">
                    <summary>{status.details.length} row error(s)</summary>
                    <ul className="error-list">
                      {status.details.map((e, i) => <li key={i}>{e}</li>)}
                    </ul>
                  </details>
                )}
              </div>
            </div>
          )}

          {trainSummary && !trainSummary.error && (
            <div className="upload-status success">
              <FiCpu />
              <div>
                <p>
                  Models trained: <strong>{trainSummary.trained}</strong> products ·
                  Skipped: <strong>{trainSummary.skipped}</strong>
                </p>
                <button className="btn-link" onClick={() => navigate('/forecasting')}>
                  View Forecasts →
                </button>
              </div>
            </div>
          )}

          {trainSummary?.error && (
            <div className="upload-status error">
              <FiAlertCircle />
              <p>{trainSummary.error}</p>
            </div>
          )}
        </div>

        <div className="upload-guide">
          <h3>CSV Format Guide</h3>
          <div className="guide-section">
            <p className="guide-label">Required columns:</p>
            <div className="col-tags">
              {['date', 'quantity', 'product_name'].map((c) => (
                <span key={c} className="col-tag required-tag">{c}</span>
              ))}
            </div>
          </div>
          <div className="guide-section">
            <p className="guide-label">Optional columns:</p>
            <div className="col-tags">
              {['product_id','category','subcategory','brand','gender','size','color','material',
                'unit_price','cost_price','discount_percent','promotion','promotion_type',
                'is_holiday','holiday_name','season','supplier_id','supplier_name','lead_time_days'
              ].map((c) => (
                <span key={c} className="col-tag">{c}</span>
              ))}
            </div>
          </div>
          <ul className="guide-notes">
            <li>Date format: <strong>YYYY-MM-DD</strong></li>
            <li>Data is automatically linked to <strong>{shop?.name}</strong></li>
            <li>Products are auto-created if they don't exist</li>
            <li>promotion: <code>1</code> / <code>0</code></li>
          </ul>
        </div>
      </div>
    </div>
  );
}
