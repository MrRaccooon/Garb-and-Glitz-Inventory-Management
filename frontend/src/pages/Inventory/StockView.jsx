import React, { useState, useEffect } from 'react';
import Card from "../../components/common/Card";
import Button from "../../components/common/Button";
import Input from "../../components/common/Input";
import Modal from "../../components/common/Modal";
import api from '../../api/client';

const StockView = () => {
  const [inventory, setInventory] = useState([]);
  const [filteredInventory, setFilteredInventory] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [lowStockOnly, setLowStockOnly] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [showAdjustModal, setShowAdjustModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [adjustment, setAdjustment] = useState({ quantity: '', reason: 'Correction' });

  useEffect(() => {
    fetchCategories(); // Fetch categories from Products
    fetchInventory();
  }, [lowStockOnly]);

  useEffect(() => {
    applyFilters();
  }, [inventory, selectedCategory, searchTerm]);

  // Fetch categories from Products API (single source of truth)
  const fetchCategories = async () => {
    try {
      const response = await api.get('/products');
      const uniqueCategories = [...new Set(response.data.map(p => p.category))].sort();
      setCategories(uniqueCategories);
      console.log('📦 Categories loaded from Products:', uniqueCategories);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  const fetchInventory = async () => {
    setLoading(true);
    try {
      const endpoint = lowStockOnly ? '/inventory/low-stock' : '/inventory';
      
      const response = await api.get(endpoint);
      setInventory(response.data);
      console.log('📦 Inventory items:', response.data);
    } catch (error) {
      console.error('Failed to fetch inventory:', error);
      alert('Failed to fetch inventory: ' + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...inventory];

    if (selectedCategory) {
      filtered = filtered.filter(item => item.category === selectedCategory);
    }

    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(item =>
        item.name.toLowerCase().includes(search) ||
        item.sku.toLowerCase().includes(search)
      );
    }

    setFilteredInventory(filtered);
  };

  const getStatusBadge = (item) => {
    if (item.balance_qty === 0) {
      return <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-sm font-medium">Out</span>;
    } else if (item.balance_qty < item.reorder_point) {
      return <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-sm font-medium">Low</span>;
    } else {
      return <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm font-medium">OK</span>;
    }
  };

  const openAdjustModal = (item) => {
    setSelectedItem(item);
    setAdjustment({ quantity: '', reason: 'Correction' });
    setShowAdjustModal(true);
  };

  const submitAdjustment = async () => {
    if (!adjustment.quantity || adjustment.quantity === '0') {
      alert('Please enter a valid quantity');
      return;
    }

    try {
      await api.post('/inventory/adjust', {
        sku: selectedItem.sku,
        change_qty: parseInt(adjustment.quantity),
        reason: adjustment.reason
      });

      alert('Stock adjusted successfully');
      setShowAdjustModal(false);
      fetchInventory();
    } catch (error) {
      alert('Failed to adjust stock: ' + (error.response?.data?.message || error.message));
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Stock View</h1>

      <Card className="p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Filters</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full border rounded px-3 py-2"
            >
              <option value="">All Categories</option>
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Search</label>
            <Input
              type="text"
              placeholder="Search by SKU or name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="flex items-end">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={lowStockOnly}
                onChange={(e) => setLowStockOnly(e.target.checked)}
                className="w-4 h-4"
              />
              <span className="text-sm font-medium">Low Stock Only</span>
            </label>
          </div>

          <div className="flex items-end">
            <Button onClick={fetchInventory} disabled={loading} className="w-full">
              {loading ? 'Loading...' : 'Refresh'}
            </Button>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">
          Inventory ({filteredInventory.length} items)
        </h2>
        {loading ? (
          <div className="text-center py-8 text-gray-500">Loading inventory...</div>
        ) : filteredInventory.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            {selectedCategory 
              ? `No inventory items found for category "${selectedCategory}". This category may not have any stock yet.`
              : 'No items found'
            }
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b bg-gray-50">
                <tr>
                  <th className="text-left py-3 px-4">SKU</th>
                  <th className="text-left py-3 px-4">Name</th>
                  <th className="text-left py-3 px-4">Category</th>
                  <th className="text-right py-3 px-4">Current Stock</th>
                  <th className="text-right py-3 px-4">Reorder Point</th>
                  <th className="text-center py-3 px-4">Status</th>
                  <th className="text-center py-3 px-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredInventory.map((item) => (
                  <tr key={item.sku} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium">{item.sku}</td>
                    <td className="py-3 px-4">{item.name}</td>
                    <td className="py-3 px-4">{item.category}</td>
                    <td className="py-3 px-4 text-right font-medium">
                      {item.balance_qty}
                    </td>
                    <td className="py-3 px-4 text-right">{item.reorder_point}</td>
                    <td className="py-3 px-4 text-center">
                      {getStatusBadge(item)}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <button
                        onClick={() => openAdjustModal(item)}
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                      >
                        Adjust Stock
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <Modal 
        isOpen={showAdjustModal} 
        onClose={() => setShowAdjustModal(false)}
        title="Adjust Stock"
        size="md"
      >
        {selectedItem && (
          <div>
            <div className="mb-6">
              <div className="text-sm text-gray-600">Product</div>
              <div className="font-medium text-lg">{selectedItem.name}</div>
              <div className="text-sm text-gray-600">SKU: {selectedItem.sku}</div>
              <div className="text-sm text-gray-600 mt-2">
                Current Stock: <span className="font-medium">{selectedItem.balance_qty}</span>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  Quantity Change (use - for decrease, + for increase)
                </label>
                <Input
                  type="number"
                  placeholder="e.g., 10 or -5"
                  value={adjustment.quantity}
                  onChange={(e) => setAdjustment({ ...adjustment, quantity: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Reason</label>
                <select
                  value={adjustment.reason}
                  onChange={(e) => setAdjustment({ ...adjustment, reason: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="Correction">Correction</option>
                  <option value="Found">Found</option>
                  <option value="Damaged">Damaged</option>
                </select>
              </div>

              {adjustment.quantity && (
                <div className="p-3 bg-blue-50 rounded">
                  <div className="text-sm">
                    New stock will be:{' '}
                    <span className="font-bold">
                      {selectedItem.balance_qty + parseInt(adjustment.quantity || 0)}
                    </span>
                  </div>
                </div>
              )}
            </div>

            <div className="mt-6 flex gap-2">
              <Button onClick={submitAdjustment} className="flex-1 bg-green-600 hover:bg-green-700">
                Submit
              </Button>
              <Button onClick={() => setShowAdjustModal(false)} variant="outline" className="flex-1">
                Cancel
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default StockView;