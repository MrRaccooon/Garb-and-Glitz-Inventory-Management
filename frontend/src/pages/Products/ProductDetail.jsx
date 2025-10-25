import { useState, useEffect } from 'react';
import { Card } from '../../components/Card';
import { Button } from '../../components/Button';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from '../../api/client';

// Mock useNavigate and useParams for demo - replace with actual react-router-dom in your app
const useNavigate = () => (path) => console.log('Navigate to:', path);
const useParams = () => ({ sku: 'SAR001' });

export default function ProductDetail() {
  const navigate = useNavigate();
  const { sku } = useParams();
  const [product, setProduct] = useState(null);
  const [stockHistory, setStockHistory] = useState([]);
  const [recentSales, setRecentSales] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProductDetails();
  }, [sku]);

  const fetchProductDetails = async () => {
    try {
      setLoading(true);
      setError(null);

      const [productRes, historyRes, salesRes] = await Promise.all([
        axios.get(`/api/v1/products/${sku}`),
        axios.get(`/api/v1/products/${sku}/stock-history?days=90`),
        axios.get(`/api/v1/products/${sku}/sales?limit=10`)
      ]);

      setProduct(productRes.data);
      setStockHistory(historyRes.data);
      setRecentSales(salesRes.data);
    } catch (err) {
      setError(err.message || 'Failed to fetch product details');
      console.error('Product detail error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
          Error: {error || 'Product not found'}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">{product.name}</h1>
        <Button onClick={() => navigate(`/products/${sku}/edit`)}>Edit Product</Button>
      </div>

      {/* Product Info Card */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Product Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <div className="text-sm font-medium text-gray-500">SKU</div>
            <div className="text-base text-gray-900 mt-1">{product.sku}</div>
          </div>
          <div>
            <div className="text-sm font-medium text-gray-500">Category</div>
            <div className="text-base text-gray-900 mt-1">{product.category}</div>
          </div>
          <div>
            <div className="text-sm font-medium text-gray-500">Subcategory</div>
            <div className="text-base text-gray-900 mt-1">{product.subcategory || '-'}</div>
          </div>
          <div>
            <div className="text-sm font-medium text-gray-500">Brand</div>
            <div className="text-base text-gray-900 mt-1">{product.brand || '-'}</div>
          </div>
          <div>
            <div className="text-sm font-medium text-gray-500">Size</div>
            <div className="text-base text-gray-900 mt-1">{product.size || '-'}</div>
          </div>
          <div>
            <div className="text-sm font-medium text-gray-500">Color</div>
            <div className="text-base text-gray-900 mt-1">{product.color || '-'}</div>
          </div>
          <div>
            <div className="text-sm font-medium text-gray-500">Fabric</div>
            <div className="text-base text-gray-900 mt-1">{product.fabric || '-'}</div>
          </div>
          <div>
            <div className="text-sm font-medium text-gray-500">Cost Price</div>
            <div className="text-base text-gray-900 mt-1">{formatCurrency(product.costPrice)}</div>
          </div>
          <div>
            <div className="text-sm font-medium text-gray-500">Sell Price</div>
            <div className="text-base text-gray-900 mt-1 font-semibold">{formatCurrency(product.sellPrice)}</div>
          </div>
          <div>
            <div className="text-sm font-medium text-gray-500">Current Stock</div>
            <div className={`text-base mt-1 font-semibold ${product.stock < product.reorderPoint ? 'text-red-600' : 'text-green-600'}`}>
              {product.stock} units
            </div>
          </div>
          <div>
            <div className="text-sm font-medium text-gray-500">Reorder Point</div>
            <div className="text-base text-gray-900 mt-1">{product.reorderPoint} units</div>
          </div>
          <div>
            <div className="text-sm font-medium text-gray-500">Lead Time</div>
            <div className="text-base text-gray-900 mt-1">{product.leadTimeDays} days</div>
          </div>
        </div>
      </Card>

      {/* Stock History Chart */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Stock History (Last 90 Days)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={stockHistory}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="date" 
              tickFormatter={(date) => {
                const d = new Date(date);
                return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
              }}
              stroke="#6b7280"
            />
            <YAxis stroke="#6b7280" />
            <Tooltip 
              labelFormatter={(date) => formatDate(date)}
              formatter={(value) => [`${value} units`, 'Stock']}
            />
            <Line 
              type="monotone" 
              dataKey="stock" 
              stroke="#3b82f6" 
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      {/* Recent Sales */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Sales (Last 10 Transactions)</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order ID</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recentSales.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-4 py-8 text-center text-gray-500">
                    No sales recorded
                  </td>
                </tr>
              ) : (
                recentSales.map((sale) => (
                  <tr key={sale.orderId} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">{formatDate(sale.date)}</td>
                    <td className="px-4 py-3 text-sm text-gray-900">{sale.orderId}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{sale.customerName}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{sale.quantity}</td>
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {formatCurrency(sale.amount)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}