import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Modal } from '@/components/ui/modal';
import api from '../../api/client';

const SalesHistory = () => {
  const [sales, setSales] = useState([]);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedSale, setSelectedSale] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    fetchSales();
  }, []);

  const fetchSales = async () => {
    setLoading(true);
    try {
      const params = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;

      const response = await api.get('/api/v1/sales', { params });
      setSales(response.data);
    } catch (error) {
      alert('Failed to fetch sales: ' + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleFilter = () => {
    if (startDate && endDate && startDate > endDate) {
      alert('Start date must be before end date');
      return;
    }
    fetchSales();
  };

  const viewDetails = (sale) => {
    setSelectedSale(sale);
    setShowModal(true);
  };

  const exportCSV = () => {
    if (sales.length === 0) {
      alert('No sales data to export');
      return;
    }

    const headers = ['Invoice #', 'Date', 'Total', 'Payment Mode', 'Items Count'];
    const rows = sales.map(sale => [
      sale.invoice_number || sale.id,
      new Date(sale.date).toLocaleDateString(),
      sale.total,
      sale.payment_mode,
      sale.items?.length || 0
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sales_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Sales History</h1>
        <Button onClick={exportCSV} className="bg-green-600 hover:bg-green-700">
          Export CSV
        </Button>
      </div>

      <Card className="p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Filter by Date Range</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Start Date</label>
            <Input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">End Date</label>
            <Input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>
          <div className="flex items-end">
            <Button onClick={handleFilter} disabled={loading} className="w-full">
              {loading ? 'Loading...' : 'Apply Filter'}
            </Button>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Sales Records</h2>
        {loading ? (
          <div className="text-center py-8 text-gray-500">Loading sales data...</div>
        ) : sales.length === 0 ? (
          <div className="text-center py-8 text-gray-500">No sales found</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b bg-gray-50">
                <tr>
                  <th className="text-left py-3 px-4">Invoice #</th>
                  <th className="text-left py-3 px-4">Date</th>
                  <th className="text-right py-3 px-4">Total</th>
                  <th className="text-left py-3 px-4">Payment Mode</th>
                  <th className="text-center py-3 px-4">Items Count</th>
                  <th className="text-center py-3 px-4">Action</th>
                </tr>
              </thead>
              <tbody>
                {sales.map((sale) => (
                  <tr
                    key={sale.id}
                    className="border-b hover:bg-gray-50 cursor-pointer"
                    onClick={() => viewDetails(sale)}
                  >
                    <td className="py-3 px-4 font-medium">
                      {sale.invoice_number || `INV-${sale.id}`}
                    </td>
                    <td className="py-3 px-4">
                      {new Date(sale.date).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4 text-right font-medium">
                      ₹{sale.total.toFixed(2)}
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                        {sale.payment_mode}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      {sale.items?.length || 0}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          viewDetails(sale);
                        }}
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {showModal && selectedSale && (
        <Modal onClose={() => setShowModal(false)}>
          <div className="p-6">
            <h2 className="text-2xl font-bold mb-4">Sale Details</h2>
            
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <span className="text-sm text-gray-600">Invoice Number:</span>
                <div className="font-medium">{selectedSale.invoice_number || `INV-${selectedSale.id}`}</div>
              </div>
              <div>
                <span className="text-sm text-gray-600">Date:</span>
                <div className="font-medium">{new Date(selectedSale.date).toLocaleString()}</div>
              </div>
              <div>
                <span className="text-sm text-gray-600">Payment Mode:</span>
                <div className="font-medium">{selectedSale.payment_mode}</div>
              </div>
              <div>
                <span className="text-sm text-gray-600">Total Amount:</span>
                <div className="font-medium text-lg">₹{selectedSale.total.toFixed(2)}</div>
              </div>
            </div>

            <h3 className="text-lg font-semibold mb-3">Items</h3>
            <div className="border rounded-lg overflow-hidden mb-4">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="text-left py-2 px-3">Product</th>
                    <th className="text-right py-2 px-3">Qty</th>
                    <th className="text-right py-2 px-3">Price</th>
                    <th className="text-right py-2 px-3">Discount</th>
                    <th className="text-right py-2 px-3">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedSale.items?.map((item, index) => {
                    const itemTotal = item.price * item.quantity;
                    const discountAmount = (itemTotal * (item.discount || 0)) / 100;
                    const finalTotal = itemTotal - discountAmount;
                    
                    return (
                      <tr key={index} className="border-b">
                        <td className="py-2 px-3">
                          <div className="font-medium">{item.name || item.product_name}</div>
                          <div className="text-xs text-gray-600">{item.sku}</div>
                        </td>
                        <td className="text-right py-2 px-3">{item.quantity}</td>
                        <td className="text-right py-2 px-3">₹{item.price}</td>
                        <td className="text-right py-2 px-3">{item.discount || 0}%</td>
                        <td className="text-right py-2 px-3 font-medium">₹{finalTotal.toFixed(2)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <div className="space-y-2 border-t pt-4">
              <div className="flex justify-between">
                <span>Subtotal:</span>
                <span className="font-medium">₹{selectedSale.subtotal?.toFixed(2) || '0.00'}</span>
              </div>
              <div className="flex justify-between text-sm text-gray-600">
                <span>GST (18%):</span>
                <span>₹{selectedSale.gst?.toFixed(2) || '0.00'}</span>
              </div>
              <div className="flex justify-between text-xl font-bold border-t pt-2">
                <span>Grand Total:</span>
                <span>₹{selectedSale.total.toFixed(2)}</span>
              </div>
            </div>

            <div className="mt-6">
              <Button onClick={() => setShowModal(false)} className="w-full">
                Close
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default SalesHistory;