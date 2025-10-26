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