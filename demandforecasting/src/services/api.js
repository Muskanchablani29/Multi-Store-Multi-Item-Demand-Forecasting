import axios from 'axios';

const API = axios.create({ baseURL: 'http://localhost:8000/api' });

API.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

API.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    // ERR_NETWORK_IO_SUSPENDED — browser bfcache suspended the request.
    // Attach a human-readable message so UI can show it clearly.
    if (!err.response && err.message === 'Network Error') {
      err.friendlyMessage =
        'Request was interrupted (browser navigation). Please stay on this page while training runs.';
    }
    return Promise.reject(err);
  }
);

export const shopsAPI = {
  getAll: () => API.get('/shops/'),
  create: (data) => API.post('/shops/', data),
};

export const productsAPI = {
  getAll: (params) => API.get('/products/', { params }),
  create: (data) => API.post('/products/', data),
};

export const salesAPI = {
  getAll: (params) => API.get('/sales/', { params }),
  getStats: () => API.get('/sales/stats/'),
  uploadCSV: (formData, onProgress) => API.post('/sales/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress,
  }),
  downloadDataset: (type) =>
    `http://localhost:8000/api/sales/download/?type=${type}`,
};

export const inventoryAPI = {
  getAll: (params) => API.get('/inventory/', { params }),
  update: (id, data) => API.patch(`/inventory/${id}/`, data),
  create: (data) => API.post('/inventory/', data),
  getReorderAlerts: () => API.get('/inventory/reorder-alerts/'),
  getRecommendation: (params) => API.get('/inventory/recommendation/', { params }),
};

export const forecastsAPI = {
  getResults: (params) => API.get('/forecasts/results/', { params }),
  getEvaluations: (params) => API.get('/forecasts/evaluations/', { params }),
};

export const mlAPI = {
  train: (data) => API.post('/ml/train/', data),
  forecast: (data) => API.post('/ml/forecast/', data),
};

export default API;
