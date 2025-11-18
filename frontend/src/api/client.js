import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log('🚀 API Request:', config.method.toUpperCase(), config.baseURL + config.url);
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.config.url, response.status);
    return response;
  },
  (error) => {
    console.error('❌ API Error:', error.response?.status, error.message);
    if (error.response) {
      const { status } = error.response;

      if (status === 401) {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        console.error('Unauthorized - redirecting to login');
      } else if (status === 500) {
        console.error('Server error:', error.response.data);
        // Show error toast notification
        if (window.showToast) {
          window.showToast('Server error occurred. Please try again later.', 'error');
        }
      }
    }

    return Promise.reject(error);
  }
);

const api = {
  get: (url, config) => apiClient.get(url, config),
  post: (url, data, config) => apiClient.post(url, data, config),
  put: (url, data, config) => apiClient.put(url, data, config),
  delete: (url, config) => apiClient.delete(url, config),
};

// Products API
export const productsAPI = {
  getAll: (params) => api.get('/products', { params }),
  getById: (sku) => api.get(`/products/${sku}`),
  create: (data) => api.post('/products', data),
  update: (sku, data) => api.put(`/products/${sku}`, data),
  delete: (sku) => api.delete(`/products/${sku}`),
};

// Sales API
export const salesAPI = {
  getAll: (params) => api.get('/sales', { params }),
  getById: (id) => api.get(`/sales/${id}`),
  create: (data) => api.post('/sales', data),
};

// Inventory API
export const inventoryAPI = {
  getAll: (params) => api.get('/inventory', { params }),
  getLowStock: () => api.get('/inventory/low-stock'),
};

// Analytics API
export const analyticsAPI = {
  getSummary: (params) => api.get('/summary', { params }),
  getTopProducts: (params) => api.get('/top-products', { params }),
  getRevenueTrend: (params) => api.get('/revenue-trend', { params }),
  getCategoryBreakdown: (params) => api.get('/category-breakdown', { params }),
  getABCAnalysis: (params) => api.get('/abc-analysis', { params }),
};

// Forecasting API
export const forecastingAPI = {
  getForecast: (params) => api.get('/forecast', { params }),
};

export default api;