// hooks/useProducts.js
import { useState, useCallback } from 'react';
import api from '../api/client';

export function useProducts() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchProducts = useCallback(async (filters = {}) => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams();
      if (filters.category) params.append('category', filters.category);
      if (filters.search) params.append('search', filters.search);
      if (filters.lowStock) params.append('lowStock', 'true');
      
      const response = await axios.get(`/api/v1/products?${params.toString()}`);
      setProducts(response.data);
      return response.data;
    } catch (err) {
      const errorMsg = err.response?.data?.message || err.message || 'Failed to fetch products';
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const createProduct = useCallback(async (productData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.post('/api/v1/products', productData);
      setProducts((prev) => [...prev, response.data]);
      return response.data;
    } catch (err) {
      const errorMsg = err.response?.data?.message || err.message || 'Failed to create product';
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateProduct = useCallback(async (sku, productData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.put(`/api/v1/products/${sku}`, productData);
      setProducts((prev) => 
        prev.map((p) => (p.sku === sku ? response.data : p))
      );
      return response.data;
    } catch (err) {
      const errorMsg = err.response?.data?.message || err.message || 'Failed to update product';
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteProduct = useCallback(async (sku) => {
    try {
      setLoading(true);
      setError(null);
      await axios.delete(`/api/v1/products/${sku}`);
      setProducts((prev) => prev.filter((p) => p.sku !== sku));
      return true;
    } catch (err) {
      const errorMsg = err.response?.data?.message || err.message || 'Failed to delete product';
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    products,
    loading,
    error,
    fetchProducts,
    createProduct,
    updateProduct,
    deleteProduct
  };
}

// hooks/useDashboardStats.js
import { useState, useCallback } from 'react';
import api from '../api/client';

export function useDashboardStats() {
  const [stats, setStats] = useState({
    todayRevenue: 0,
    totalSKUs: 0,
    lowStockCount: 0,
    pendingPOs: 0
  });
  const [topProducts, setTopProducts] = useState([]);
  const [revenueTrend, setRevenueTrend] = useState([]);
  const [lowStockAlerts, setLowStockAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all required data in parallel
      const [productsRes, topProductsRes, revenueRes, lowStockRes] = await Promise.all([
        api.get('/products'),
        api.get('/analytics/top-products?days=30'),
        api.get('/analytics/revenue-trend?days=90'),
        api.get('/inventory/low-stock')
      ]);

      // Process revenue trend data (last 30 days)
      const last30Days = revenueRes.data.slice(-30);
      setRevenueTrend(last30Days);

      // Calculate today's revenue (last entry)
      const todayRevenue = last30Days[last30Days.length - 1]?.revenue || 0;

      // Set stats
      setStats({
        todayRevenue,
        totalSKUs: productsRes.data.length,
        lowStockCount: lowStockRes.data.length,
        pendingPOs: 0 // This would come from a PO endpoint
      });

      // Set top products
      setTopProducts(topProductsRes.data);

      // Set low stock alerts
      setLowStockAlerts(lowStockRes.data);

      return {
        stats: {
          todayRevenue,
          totalSKUs: productsRes.data.length,
          lowStockCount: lowStockRes.data.length,
          pendingPOs: 0
        },
        topProducts: topProductsRes.data,
        revenueTrend: last30Days,
        lowStockAlerts: lowStockRes.data
      };
    } catch (err) {
      const errorMsg = err.response?.data?.message || err.message || 'Failed to fetch dashboard data';
      setError(errorMsg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshStats = useCallback(async () => {
    return fetchDashboardData();
  }, [fetchDashboardData]);

  return {
    stats,
    topProducts,
    revenueTrend,
    lowStockAlerts,
    loading,
    error,
    fetchDashboardData,
    refreshStats
  };
}