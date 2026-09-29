import axios from 'axios';

const API = axios.create({ baseURL: 'http://localhost:8000/api' });

export const shopsAPI = {
  getAll: () => API.get('/shops/'),
  create: (data) => API.post('/shops/', data),
};

export const productsAPI = {
  getAll: () => API.get('/products/'),
  create: (data) => API.post('/products/', data),
};

export const salesAPI = {
  getAll: (params) => API.get('/sales/', { params }),
  uploadCSV: (formData) => API.post('/sales/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
};

export const inventoryAPI = {
  getAll: (params) => API.get('/inventory/', { params }),
  update: (id, data) => API.patch(`/inventory/${id}/`, data),
  create: (data) => API.post('/inventory/', data),
  getReorderAlerts: () => API.get('/inventory/reorder-alerts/'),
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
