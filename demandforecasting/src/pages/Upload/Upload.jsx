import { useState, useRef } from 'react';
import { FiUploadCloud, FiCheckCircle, FiAlertCircle, FiFile } from 'react-icons/fi';
import { salesAPI } from '../../services/api';
import './Upload.css';

export default function Upload() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState(null); // { type: 'success'|'error', message, details }
  const [uploading, setUploading] = useState(false);
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
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await salesAPI.uploadCSV(formData);
      setStatus({
        type: 'success',
        message: `Successfully imported ${res.data.created} records.`,
        details: res.data.errors,
      });
      setFile(null);
    } catch (err) {
      setStatus({ type: 'error', message: err.response?.data?.error || 'Upload failed.' });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Upload Sales Data</h1>
        <p>Import historical sales data via CSV file</p>
      </div>

      <div className="upload-layout">
        <div className="upload-card">
          <div
            className={`drop-zone ${file ? 'has-file' : ''}`}
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => inputRef.current.click()}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".csv"
              hidden
              onChange={(e) => setFile(e.target.files[0])}
            />
            {file ? (
              <>
                <FiFile className="drop-icon file-icon" />
                <p className="drop-filename">{file.name}</p>
                <span className="drop-hint">Click to change file</span>
              </>
            ) : (
              <>
                <FiUploadCloud className="drop-icon" />
                <p className="drop-text">Drag & drop your CSV here</p>
                <span className="drop-hint">or click to browse</span>
              </>
            )}
          </div>

          <button
            className="btn-primary"
            onClick={handleUpload}
            disabled={!file || uploading}
          >
            {uploading ? 'Uploading...' : 'Upload CSV'}
          </button>

          {status && (
            <div className={`upload-status ${status.type}`}>
              {status.type === 'success' ? <FiCheckCircle /> : <FiAlertCircle />}
              <div>
                <p>{status.message}</p>
                {status.details?.length > 0 && (
                  <ul className="error-list">
                    {status.details.map((e, i) => <li key={i}>{e}</li>)}
                  </ul>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="upload-guide">
          <h3>CSV Format Guide</h3>
          <p>Your CSV file must have the following columns:</p>
          <div className="csv-preview">
            <code>shop_name, item_name, date, quantity</code>
          </div>
          <div className="csv-example">
            <p className="guide-label">Example:</p>
            <table className="guide-table">
              <thead>
                <tr><th>shop_name</th><th>item_name</th><th>date</th><th>quantity</th></tr>
              </thead>
              <tbody>
                <tr><td>Shop A</td><td>Product 1</td><td>2024-01-01</td><td>120</td></tr>
                <tr><td>Shop A</td><td>Product 1</td><td>2024-01-02</td><td>95</td></tr>
                <tr><td>Shop B</td><td>Product 2</td><td>2024-01-01</td><td>200</td></tr>
              </tbody>
            </table>
          </div>
          <ul className="guide-notes">
            <li>Date format: <strong>YYYY-MM-DD</strong></li>
            <li>Shops and products are auto-created if they don't exist</li>
            <li>Duplicate entries will be added as new records</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
