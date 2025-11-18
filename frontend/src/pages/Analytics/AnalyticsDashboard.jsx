import React, { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import api from '../../api/client';

const AnalyticsDashboard = () => {
  const [summary, setSummary] = useState(null);
  const [topProducts, setTopProducts] = useState([]);
  const [categoryBreakdown, setCategoryBreakdown] = useState([]);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAnalytics();
  }, [days]);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      // Fetch summary
      const summaryRes = await api.get('/summary', {
        params: { days }
      });
      setSummary(summaryRes.data);

      // Fetch top products
      const topProductsRes = await api.get('/top-products', {
        params: { days, limit: 10, sort_by: 'revenue' }
      });
      setTopProducts(topProductsRes.data);

      // Fetch category breakdown
      const categoryRes = await api.get('/category-breakdown', {
        params: { days }
      });
      setCategoryBreakdown(categoryRes.data);

    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      alert('Failed to fetch analytics: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Analytics & Reports</h1>
        <div className="flex gap-2">
          {[7, 30, 90].map(d => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-4 py-2 rounded font-medium transition-colors ${
                days === d
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 hover:bg-gray-300'
              }`}
            >
              {d} Days
            </button>
          ))}
        </div>
      </div>

      {loading && (
        <div className="text-center py-12">
          <div className="text-lg text-gray-600">Loading analytics...</div>
        </div>
      )}

      {!loading && summary && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <Card className="p-6">
              <div className="text-sm text-gray-600 mb-1">Total Revenue</div>
              <div className="text-3xl font-bold text-green-600">
                {formatCurrency(summary.total_revenue)}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Avg: {formatCurrency(summary.avg_daily_revenue)}/day
              </div>
            </Card>

            <Card className="p-6">
              <div className="text-sm text-gray-600 mb-1">Units Sold</div>
              <div className="text-3xl font-bold text-blue-600">
                {summary.total_units_sold}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {summary.unique_products_sold} unique products
              </div>
            </Card>

            <Card className="p-6">
              <div className="text-sm text-gray-600 mb-1">Transactions</div>
              <div className="text-3xl font-bold text-purple-600">
                {summary.total_transactions}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Avg Order: {formatCurrency(summary.avg_order_value)}
              </div>
            </Card>

            <Card className="p-6">
              <div className="text-sm text-gray-600 mb-1">Best Seller</div>
              <div className="text-lg font-bold text-orange-600">
                {summary.best_selling_product?.name || 'N/A'}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {summary.best_selling_product?.quantity || 0} units sold
              </div>
            </Card>
          </div>

          {/* Top Products */}
          <Card className="p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Top 10 Products by Revenue</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-4">Rank</th>
                    <th className="text-left py-2 px-4">SKU</th>
                    <th className="text-left py-2 px-4">Product Name</th>
                    <th className="text-left py-2 px-4">Category</th>
                    <th className="text-right py-2 px-4">Revenue</th>
                    <th className="text-right py-2 px-4">Quantity</th>
                    <th className="text-right py-2 px-4">Transactions</th>
                  </tr>
                </thead>
                <tbody>
                  {topProducts.map((product, idx) => (
                    <tr key={product.sku} className="border-b hover:bg-gray-50">
                      <td className="py-2 px-4 font-semibold">{idx + 1}</td>
                      <td className="py-2 px-4 font-mono text-sm">{product.sku}</td>
                      <td className="py-2 px-4">{product.name}</td>
                      <td className="py-2 px-4">
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                          {product.category}
                        </span>
                      </td>
                      <td className="py-2 px-4 text-right font-semibold">
                        {formatCurrency(product.total_revenue)}
                      </td>
                      <td className="py-2 px-4 text-right">{product.total_quantity}</td>
                      <td className="py-2 px-4 text-right">{product.transaction_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Category Breakdown */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Sales by Category</h2>
            <div className="space-y-4">
              {categoryBreakdown.map((category) => (
                <div key={category.category} className="border-b pb-4 last:border-b-0">
                  <div className="flex justify-between items-center mb-2">
                    <div>
                      <span className="font-semibold text-lg">{category.category}</span>
                      <span className="text-sm text-gray-500 ml-2">
                        ({category.unique_products} products, {category.transaction_count} transactions)
                      </span>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-lg">{formatCurrency(category.revenue)}</div>
                      <div className="text-sm text-gray-600">{category.revenue_percentage}% of total</div>
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-blue-600 h-3 rounded-full transition-all"
                      style={{ width: `${category.revenue_percentage}%` }}
                    ></div>
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    {category.quantity} units sold
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </>
      )}

      {!loading && !summary && (
        <Card className="p-12">
          <div className="text-center text-gray-500">
            <div className="text-6xl mb-4">📊</div>
            <p className="text-lg">No data available for the selected period</p>
          </div>
        </Card>
      )}
    </div>
  );
};

export default AnalyticsDashboard;
