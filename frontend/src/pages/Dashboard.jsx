import { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../api/client';

// Simple Card component
const Card = ({ children, className = '' }) => (
  <div className={`bg-white rounded-lg shadow ${className}`}>
    {children}
  </div>
);

// Simple Button component
const Button = ({ children, onClick, disabled, className = '' }) => (
  <button
    onClick={onClick}
    disabled={disabled}
    className={`px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed ${className}`}
  >
    {children}
  </button>
);

// Simple LoadingSpinner component
const LoadingSpinner = () => (
  <div className="flex items-center justify-center">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
  </div>
);

// RevenueChart component
const RevenueChart = ({ data }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const formatRevenue = (value) => {
    if (value >= 10000000) {
      return `₹${(value / 10000000).toFixed(1)}Cr`;
    } else if (value >= 100000) {
      return `₹${(value / 100000).toFixed(1)}L`;
    } else if (value >= 1000) {
      return `₹${(value / 1000).toFixed(1)}K`;
    }
    return `₹${value}`;
  };

  const formatTooltipValue = (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(value);
  };

  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis 
          dataKey="date" 
          tickFormatter={formatDate}
          stroke="#6b7280"
          style={{ fontSize: '12px' }}
        />
        <YAxis 
          tickFormatter={formatRevenue}
          stroke="#6b7280"
          style={{ fontSize: '12px' }}
        />
        <Tooltip 
          labelFormatter={formatDate}
          formatter={(value) => [formatTooltipValue(value), 'Revenue']}
          contentStyle={{
            backgroundColor: 'white',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            padding: '8px 12px'
          }}
        />
        <Area 
          type="monotone" 
          dataKey="revenue" 
          stroke="#3b82f6" 
          strokeWidth={2}
          fill="url(#revenueGradient)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
};

export default function Dashboard() {
  const [stats, setStats] = useState({
    todayRevenue: 0,
    totalSKUs: 0,
    lowStockCount: 0,
    pendingPOs: 0
  });
  const [revenueTrend, setRevenueTrend] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [lowStockAlerts, setLowStockAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all data in parallel
      const [productsRes, salesRes, lowStockRes] = await Promise.all([
        api.get('/products'),
        api.get('/sales'),
        api.get('/inventory/low-stock')
      ]);

      const products = productsRes.data;
      const sales = salesRes.data;
      const lowStock = lowStockRes.data;

      // Calculate today's revenue
      const today = new Date().toISOString().split('T')[0];
      const todaySales = sales.filter(sale => {
        const saleDate = new Date(sale.timestamp || sale.date).toISOString().split('T')[0];
        return saleDate === today;
      });
      const todayRevenue = todaySales.reduce((sum, sale) => sum + Number(sale.total), 0);

      // Calculate revenue trend (last 30 days)
      const revenueTrendData = calculateRevenueTrend(sales, 30);

      // Calculate top products
      const topProductsData = calculateTopProducts(sales, products);

      setStats({
        todayRevenue,
        totalSKUs: products.length,
        lowStockCount: lowStock.length,
        pendingPOs: 0 // Set to 0 if no PO system yet
      });

      setRevenueTrend(revenueTrendData);
      setTopProducts(topProductsData);
      setLowStockAlerts(lowStock);
    } catch (err) {
      setError(err.message || 'Failed to fetch dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateRevenueTrend = (sales, days) => {
    const trendMap = {};
    const today = new Date();

    // Initialize all days with 0
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateKey = date.toISOString().split('T')[0];
      trendMap[dateKey] = 0;
    }

    // Aggregate sales by date
    sales.forEach(sale => {
      const saleDate = new Date(sale.timestamp || sale.date).toISOString().split('T')[0];
      if (trendMap.hasOwnProperty(saleDate)) {
        trendMap[saleDate] += Number(sale.total);
      }
    });

    // Convert to array format for chart
    return Object.entries(trendMap).map(([date, revenue]) => ({
      date,
      revenue
    }));
  };

  const calculateTopProducts = (sales, products) => {
    // Aggregate sales by SKU
    const skuMap = {};
    
    sales.forEach(sale => {
      if (!skuMap[sale.sku]) {
        skuMap[sale.sku] = {
          sku: sale.sku,
          qtySold: 0,
          revenue: 0
        };
      }
      skuMap[sale.sku].qtySold += Number(sale.quantity);
      skuMap[sale.sku].revenue += Number(sale.total);
    });

    // Add product names
    const productMap = {};
    products.forEach(p => {
      productMap[p.sku] = p.name;
    });

    const topProducts = Object.values(skuMap).map(item => ({
      ...item,
      name: productMap[item.sku] || item.sku
    }));

    // Sort by revenue and return top 5
    return topProducts
      .sort((a, b) => b.revenue - a.revenue)
      .slice(0, 5);
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const handleReorder = (product) => {
    alert(`Reorder feature coming soon for ${product.name}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
          Error: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-6">
          <div className="text-sm font-medium text-gray-600">Today's Revenue</div>
          <div className="text-2xl font-bold text-gray-900 mt-2">
            {formatCurrency(stats.todayRevenue)}
          </div>
        </Card>
        <Card className="p-6">
          <div className="text-sm font-medium text-gray-600">Total SKUs</div>
          <div className="text-2xl font-bold text-gray-900 mt-2">{stats.totalSKUs}</div>
        </Card>
        <Card className="p-6">
          <div className="text-sm font-medium text-gray-600">Low Stock Alerts</div>
          <div className="text-2xl font-bold text-red-600 mt-2">{stats.lowStockCount}</div>
        </Card>
        <Card className="p-6">
          <div className="text-sm font-medium text-gray-600">Pending POs</div>
          <div className="text-2xl font-bold text-gray-900 mt-2">{stats.pendingPOs}</div>
        </Card>
      </div>

      {/* Revenue Trend Chart */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Revenue Trend (Last 30 Days)</h2>
        {revenueTrend.length === 0 ? (
          <div className="h-[300px] flex items-center justify-center text-gray-500">
            No revenue data available
          </div>
        ) : (
          <RevenueChart data={revenueTrend} />
        )}
      </Card>

      {/* Top 5 Products */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Top 5 Products</h2>
        {topProducts.length === 0 ? (
          <p className="text-gray-500">No sales data available</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SKU</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Qty Sold</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Revenue</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {topProducts.map((product) => (
                  <tr key={product.sku} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{product.sku}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{product.name}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{product.qtySold}</td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {formatCurrency(product.revenue)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Low Stock Alerts */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Low Stock Alerts</h2>
        <div className="space-y-3">
          {lowStockAlerts.length === 0 ? (
            <p className="text-gray-500">No low stock alerts</p>
          ) : (
            lowStockAlerts.map((product) => (
              <div key={product.sku} className="flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{product.name}</div>
                  <div className="text-sm text-gray-600">
                    SKU: {product.sku} | Current Stock: <span className="font-semibold text-red-600">{product.balance_qty}</span> units
                  </div>
                </div>
                <Button onClick={() => handleReorder(product)} className="ml-4">
                  Reorder
                </Button>
              </div>
            ))
          )}
        </div>
      </Card>
    </div>
  );
}