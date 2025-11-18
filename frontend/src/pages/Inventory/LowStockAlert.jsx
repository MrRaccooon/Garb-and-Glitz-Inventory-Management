import React, { useState, useEffect } from 'react';
import Card from "../../components/common/Card";
import Button from "../../components/common/Button";
import api from '../../api/client';

const LowStockAlerts = () => {
  const [lowStockItems, setLowStockItems] = useState([]);
  const [selectedItems, setSelectedItems] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchLowStockItems();
  }, []);

  const fetchLowStockItems = async () => {
    setLoading(true);
    try {
      const response = await api.get('/inventory/low-stock');
      setLowStockItems(response.data);
    } catch (error) {
      alert('Failed to fetch low stock items: ' + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
    }
  };

  const calculateSuggestedOrder = (item) => {
    const deficit = item.reorder_point - item.current_stock;
    const buffer = Math.ceil(item.reorder_point * 0.5);
    return Math.max(deficit + buffer, item.reorder_point);
  };

  const toggleItemSelection = (sku) => {
    if (selectedItems.includes(sku)) {
      setSelectedItems(selectedItems.filter(s => s !== sku));
    } else {
      setSelectedItems([...selectedItems, sku]);
    }
  };

  const createPO = async (item) => {
    const suggestedQty = calculateSuggestedOrder(item);
    const confirmed = window.confirm(
      `Create Purchase Order for:\n${item.name} (${item.sku})\nQuantity: ${suggestedQty} units`
    );

    if (confirmed) {
      try {
        await api.post('/api/v1/purchase-orders', {
          items: [{
            sku: item.sku,
            quantity: suggestedQty
          }]
        });
        alert('Purchase Order created successfully!');
      } catch (error) {
        alert('Failed to create PO: ' + (error.response?.data?.message || error.message));
      }
    }
  };

  const createBulkPO = async () => {
    if (selectedItems.length === 0) {
      alert('Please select at least one item');
      return;
    }

    const items = lowStockItems
      .filter(item => selectedItems.includes(item.sku))
      .map(item => ({
        sku: item.sku,
        name: item.name,
        quantity: calculateSuggestedOrder(item)
      }));

    const itemsList = items.map(i => `${i.name}: ${i.quantity} units`).join('\n');
    const confirmed = window.confirm(
      `Create Bulk Purchase Order for ${items.length} items:\n\n${itemsList}`
    );

    if (confirmed) {
      try {
        await api.post('/api/v1/purchase-orders', {
          items: items.map(i => ({ sku: i.sku, quantity: i.quantity }))
        });
        alert('Bulk Purchase Order created successfully!');
        setSelectedItems([]);
      } catch (error) {
        alert('Failed to create bulk PO: ' + (error.response?.data?.message || error.message));
      }
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Low Stock Alerts</h1>
        {selectedItems.length > 0 && (
          <Button onClick={createBulkPO} className="bg-purple-600 hover:bg-purple-700">
            Bulk Reorder ({selectedItems.length} items)
          </Button>
        )}
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="text-gray-500">Loading low stock items...</div>
        </div>
      ) : lowStockItems.length === 0 ? (
        <Card className="p-12">
          <div className="text-center">
            <div className="text-6xl mb-4">✓</div>
            <h2 className="text-2xl font-bold text-green-600 mb-2">All Good!</h2>
            <p className="text-gray-600">No items are running low on stock</p>
          </div>
        </Card>
      ) : (
        <>
          <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center gap-2">
              <span className="text-2xl">⚠️</span>
              <div>
                <div className="font-semibold text-yellow-800">
                  {lowStockItems.length} {lowStockItems.length === 1 ? 'item' : 'items'} below reorder point
                </div>
                <div className="text-sm text-yellow-700">
                  Review and create purchase orders to restock
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {lowStockItems.map((item) => {
              const suggestedOrder = calculateSuggestedOrder(item);
              const isSelected = selectedItems.includes(item.sku);
              
              return (
                <Card
                  key={item.sku}
                  className={`p-5 hover:shadow-lg transition-shadow ${
                    isSelected ? 'ring-2 ring-blue-500' : ''
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg mb-1">{item.name}</h3>
                      <div className="text-sm text-gray-600 mb-2">SKU: {item.sku}</div>
                      <div className="text-xs text-gray-500">{item.category}</div>
                    </div>
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggleItemSelection(item.sku)}
                      className="w-5 h-5 mt-1"
                    />
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Current Stock:</span>
                      <span className="font-bold text-red-600">{item.current_stock}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Reorder at:</span>
                      <span className="font-medium">{item.reorder_point}</span>
                    </div>
                    <div className="flex justify-between items-center pt-2 border-t">
                      <span className="text-sm font-medium text-gray-700">Suggested Order:</span>
                      <span className="font-bold text-green-600 text-lg">
                        {suggestedOrder} units
                      </span>
                    </div>
                  </div>

                  <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                    <div
                      className="bg-red-500 h-2 rounded-full"
                      style={{
                        width: `${Math.min((item.current_stock / item.reorder_point) * 100, 100)}%`
                      }}
                    ></div>
                  </div>

                  <Button
                    onClick={() => createPO(item)}
                    className="w-full bg-blue-600 hover:bg-blue-700"
                  >
                    Create PO
                  </Button>
                </Card>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
};

export default LowStockAlerts;