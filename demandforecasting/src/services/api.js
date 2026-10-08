import axios from 'axios';

const API = axios.create({ baseURL: 'http://localhost:8000/api' });

// Attach JWT token to every request
API.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auto-refresh on 401, but only for non-auth endpoints
API.interceptors.response.use(
  (res) => res,
  async (err) => {
    const original = err.config;
    const isAuthEndpoint = original.url?.includes('/auth/login') || original.url?.includes('/auth/refresh');

    if (err.response?.status === 401 && !original._retry && !isAuthEndpoint) {
      original._retry = true;
      const refresh = localStorage.getItem('refresh_token');
      if (refresh) {
        try {
          const res = await axios.post('http://localhost:8000/api/auth/refresh/', { refresh });
          localStorage.setItem('access_token', res.data.access);
          original.headers.Authorization = `Bearer ${res.data.access}`;
          return API(original);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      } else {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(err);
  }
);

export const authAPI = {
  login:    (data) => API.post('/auth/login/', data),
  register: (data) => API.post('/auth/register/', data),
  me:       ()     => API.get('/auth/me/'),
};

export const shopsAPI = {
  getAll: () => API.get('/shops/'),
};

export const productsAPI = {
  getAll: (params) => API.get('/products/', { params }),
};

export const salesAPI = {
  uploadCSV: (formData, onProgress) => API.post('/sales/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress,
  }),
};

export const dashboardAPI = {
  getStats: () => API.get('/dashboard/stats/'),
};

export const inventoryAPI = {
  getAll:           ()          => API.get('/inventory/'),
  update:           (id, data)  => API.patch(`/inventory/${id}/`, data),
  create:           (data)      => API.post('/inventory/', data),
  getReorderAlerts: ()          => API.get('/inventory/reorder-alerts/'),
  getRecommendation:(params)    => API.get('/inventory/recommendation/', { params }),
};

export const forecastsAPI = {
  getResults:     (params) => API.get('/forecasts/results/', { params }),
  getEvaluations: (params) => API.get('/forecasts/evaluations/', { params }),
};

export const mlAPI = {
  train:           (data) => API.post('/ml/train/', data),
  forecast:        (data) => API.post('/ml/forecast/', data),
  autoTrain:       (data) => API.post('/ml/auto-train/', data),
  octoberForecast: (data) => API.post('/ml/october-forecast/', data),
};

export default API;
