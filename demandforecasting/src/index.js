import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

// Clear stale tokens from old system (no JWT)
const TOKEN_VERSION = 'v2_jwt';
if (localStorage.getItem('token_version') !== TOKEN_VERSION) {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.setItem('token_version', TOKEN_VERSION);
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
