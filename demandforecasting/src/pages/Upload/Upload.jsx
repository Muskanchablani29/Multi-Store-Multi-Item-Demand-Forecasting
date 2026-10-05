import { useState, useRef } from 'react';
import {
  FiUploadCloud, FiCheckCircle, FiAlertCircle,
  FiFile, FiDownload, FiDatabase,
} from 'react-icons/fi';
import { salesAPI } from '../../services/api';
import './Upload.css';

const REQUIRED_COLS = ['shop_name', 'product_name', 'date', 'quantity'];
const OPTIONAL_COLS = [
  'shop_id', 'shop_location', 'product_id', 'category', 'subcategory',
  'brand', 'gender', 'size', 'color', 'material',
  'unit_price', 'cost_price', 'discount_percent',
  'promotion', 'promotion_type', 'promotion_discount',
  'is_holiday', 'holiday_name', 'season',
  'supplier_id', 'supplier_name', 'lead_time_days',
];

export default function Upload() {
  const [file, setFile]           = useState(null);
  const [status, setStatus]       = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress]   = useState(0);
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
    setProgress(0);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await salesAPI.uploadCSV(formData, (evt) => {
        if (evt.total) setProgress(Math.round((evt.loaded / evt.total) * 100));
      });
      setStatus({
        type: 'success',
        message: `Successfully imported ${res.data.created.toLocaleString()} records.`,
        details: res.data.errors,
      });
      setFile(null);
      setProgress(0);
    } catch (err) {
      const errData = err.response?.data;
      setStatus({
        type: 'error',
        message: errData?.error || 'Upload failed.',
        details: errData?.errors || [],
      });
      setProgress(0);
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = (type) => {
    const url = salesAPI.downloadDataset(type);
    const a = document.createElement('a');
    a.href = url;
    a.download = type === 'full'
      ? 'thakur_footwear_sales_500k.csv'
      : 'thakur_footwear_sample.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Upload Sales Data</h1>
        <p>Download the Thakur Footwear dataset, then upload it to populate the system</p>
      </div>

      {/* ── Download Section ── */}
      <div className="download-section">
        <div className="download-header">
          <FiDatabase className="download-header-icon" />
          <div>
            <h3>Thakur Footwear Dataset</h3>
            <p>Jan 2025 – Dec 2025 · 65 products · realistic sales patterns</p>
          </div>
        </div>
        <div className="download-cards">
          <div className="download-card">
            <div className="download-card-info">
              <span className="download-badge full">Full Dataset</span>
              <strong>thakur_footwear_sales_500k.csv</strong>
              <span className="download-meta">~5,02,018 rows · 126 MB · 1 year</span>
              <span className="download-note">Use this for training LSTM/GRU models</span>
            </div>
            <button className="btn-download" onClick={() => handleDownload('full')}>
              <FiDownload /> Download Full
            </button>
          </div>

          <div className="download-card">
            <div className="download-card-info">
              <span className="download-badge sample">Sample</span>
              <strong>thakur_footwear_sample.csv</strong>
              <span className="download-meta">~1,000 rows · 251 KB · quick test</span>
              <span className="download-note">Use this to test the upload flow first</span>
            </div>
            <button className="btn-download btn-download-secondary" onClick={() => handleDownload('sample')}>
              <FiDownload /> Download Sample
            </button>
          </div>
        </div>
      </div>

      {/* ── Upload Section ── */}
      <div className="upload-layout">
        <div className="upload-card">
          <h3 className="upload-card-title">Upload CSV File</h3>

          <div
            className={`drop-zone ${file ? 'has-file' : ''}`}
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => !uploading && inputRef.current.click()}
          >
            <input
              ref={inputRef} type="file" accept=".csv" hidden
              onChange={(e) => setFile(e.target.files[0])}
            />
            {file ? (
              <>
                <FiFile className="drop-icon file-icon" />
                <p className="drop-filename">{file.name}</p>
                <span className="drop-meta">
                  {(file.size / 1024 / 1024).toFixed(1)} MB · Click to change
                </span>
              </>
            ) : (
              <>
                <FiUploadCloud className="drop-icon" />
                <p className="drop-text">Drag & drop your CSV here</p>
                <span className="drop-hint">or click to browse</span>
              </>
            )}
          </div>

          {/* Progress bar */}
          {uploading && (
            <div className="progress-wrap">
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${progress}%` }} />
              </div>
              <span className="progress-label">
                {progress < 100 ? `Uploading… ${progress}%` : 'Processing records…'}
              </span>
            </div>
          )}

          <button
            className="btn-primary"
            onClick={handleUpload}
            disabled={!file || uploading}
          >
            {uploading ? `Uploading… ${progress}%` : 'Upload CSV'}
          </button>

          {status && (
            <div className={`upload-status ${status.type}`}>
              {status.type === 'success' ? <FiCheckCircle /> : <FiAlertCircle />}
              <div>
                <p>{status.message}</p>
                {status.details?.length > 0 && (
                  <details className="error-details">
                    <summary>{status.details.length} row error(s) — click to expand</summary>
                    <ul className="error-list">
                      {status.details.map((e, i) => <li key={i}>{e}</li>)}
                    </ul>
                  </details>
                )}
              </div>
            </div>
          )}
        </div>

        {/* ── Format Guide ── */}
        <div className="upload-guide">
          <h3>CSV Format Guide</h3>

          <div className="guide-section">
            <p className="guide-label">Required columns:</p>
            <div className="col-tags">
              {REQUIRED_COLS.map((c) => (
                <span key={c} className="col-tag required-tag">{c}</span>
              ))}
            </div>
          </div>

          <div className="guide-section">
            <p className="guide-label">Optional columns (recommended for full features):</p>
            <div className="col-tags">
              {OPTIONAL_COLS.map((c) => (
                <span key={c} className="col-tag">{c}</span>
              ))}
            </div>
          </div>

          <ul className="guide-notes">
            <li>Date format: <strong>YYYY-MM-DD</strong></li>
            <li>quantity and prices must be ≥ 0</li>
            <li>discount_percent must be 0–100</li>
            <li>promotion: <code>1</code> / <code>0</code> or <code>true</code> / <code>false</code></li>
            <li>Shops and products are auto-created if they don't exist</li>
            <li>Duplicate rows are skipped automatically</li>
            <li>The full 500k file may take 2–5 minutes to process</li>
          </ul>

          <div className="guide-tip">
            <FiDownload />
            <span>
              Download <strong>thakur_footwear_sample.csv</strong> above to test the
              upload flow before uploading the full dataset.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
