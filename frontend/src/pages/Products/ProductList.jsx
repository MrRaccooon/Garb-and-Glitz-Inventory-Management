import { useState, useEffect, useCallback } from 'react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import api from '../../api/client';

// Mock useNavigate for demo purposes - replace with actual react-router-dom in your app
const useNavigate = () => (path) => console.log('Navigate to:', path);

export default function ProductList() {
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [productToDelete, setProductToDelete] = useState(null);
  const itemsPerPage = 10;

  useEffect(() => {
    fetchProducts();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      filterProducts();
    }, 300);
    return () => clearTimeout(timer);
  }, [searchTerm, categoryFilter, products]);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('🔄 Fetching products...');
      const response = await api.get('/products');
      console.log('✅ Products fetched:', response.data);
      setProducts(response.data);
      setFilteredProducts(response.data);
    } catch (err) {
      console.error('❌ Products fetch error:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to fetch products');
    } finally {
      setLoading(false);
    }
  };

  const filterProducts = useCallback(() => {
    let filtered = [...products];

    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(
        (p) =>
          p.name.toLowerCase().includes(search) ||
          p.sku.toLowerCase().includes(search)
      );
    }

    if (categoryFilter !== 'All') {
      filtered = filtered.filter((p) => p.category === categoryFilter);
    }

    setFilteredProducts(filtered);
    setCurrentPage(1);
  }, [searchTerm, categoryFilter, products]);

  const handleDelete = async () => {
    if (!productToDelete) return;

    try {
      console.log('🗑️ Deleting product:', productToDelete.sku);
      await api.delete(`/products/${productToDelete.sku}`);
      setProducts(products.filter((p) => p.sku !== productToDelete.sku));
      setShowDeleteModal(false);
      setProductToDelete(null);
      alert('Product deleted successfully');
    } catch (err) {
      console.error('❌ Delete error:', err);
      alert('Failed to delete product: ' + (err.response?.data?.detail || err.message));
    }
  };

  const openDeleteModal = (product) => {
    setProductToDelete(product);
    setShowDeleteModal(true);
  };

  const totalPages = Math.ceil(filteredProducts.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentProducts = filteredProducts.slice(startIndex, endIndex);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Products</h1>
        <Button onClick={() => navigate('/products/new')}>Add Product</Button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
          Error: {error}
        </div>
      )}

      <Card className="p-6">
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <input
            type="text"
            placeholder="Search by name or SKU..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="All">All Categories</option>
            <option value="Saree">Saree</option>
            <option value="Suit">Suit</option>
            <option value="Lehenga">Lehenga</option>
            <option value="Dupatta">Dupatta</option>
          </select>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SKU</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Size</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Color</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {currentProducts.map((product) => (
                <tr
                  key={product.sku}
                  onClick={() => navigate(`/products/${product.sku}`)}
                  className="hover:bg-gray-50 cursor-pointer"
                >
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">{product.sku}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{product.name}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{product.category}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{product.size || 'N/A'}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{product.color || 'N/A'}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{formatCurrency(product.sell_price)}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    <span className={product.stock_quantity < product.reorder_point ? 'text-red-600 font-semibold' : ''}>
                      {product.stock_quantity}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => navigate(`/products/${product.sku}/edit`)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => openDeleteModal(product)}
                        className="text-red-600 hover:text-red-800"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredProducts.length === 0 && (
          <div className="text-center py-8 text-gray-500">No products found</div>
        )}

        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-6">
            <Button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              Previous
            </Button>
            <span className="text-sm text-gray-700">
              Page {currentPage} of {totalPages}
            </span>
            <Button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
            >
              Next
            </Button>
          </div>
        )}
      </Card>

      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Confirm Delete</h3>
            <p className="text-gray-700 mb-6">
              Are you sure you want to delete {productToDelete?.name}? This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <Button onClick={() => setShowDeleteModal(false)}>Cancel</Button>
              <Button onClick={handleDelete} className="bg-red-600 hover:bg-red-700">
                Delete
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}