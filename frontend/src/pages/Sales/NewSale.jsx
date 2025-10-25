import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import api from '../../api/client';

const NewSale = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [cart, setCart] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [discount, setDiscount] = useState(0);
  const [paymentMode, setPaymentMode] = useState('Cash');
  const [loading, setLoading] = useState(false);
  const [saleSuccess, setSaleSuccess] = useState(false);
  const [lastSaleData, setLastSaleData] = useState(null);

  useEffect(() => {
    const debounce = setTimeout(() => {
      if (searchTerm.length >= 2) {
        searchProducts();
      } else {
        setSearchResults([]);
        setShowDropdown(false);
      }
    }, 300);

    return () => clearTimeout(debounce);
  }, [searchTerm]);

  const searchProducts = async () => {
    try {
      const response = await api.get('/api/v1/inventory', {
        params: { search: searchTerm }
      });
      setSearchResults(response.data.slice(0, 10));
      setShowDropdown(true);
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  const selectProduct = (product) => {
    setSelectedProduct(product);
    setSearchTerm('');
    setShowDropdown(false);
    setQuantity(1);
    setDiscount(0);
  };

  const addToCart = () => {
    if (!selectedProduct) return;
    
    if (quantity > selectedProduct.available_stock) {
      alert('Quantity exceeds available stock');
      return;
    }

    const existingIndex = cart.findIndex(item => item.sku === selectedProduct.sku);
    
    if (existingIndex >= 0) {
      const newCart = [...cart];
      newCart[existingIndex].quantity += quantity;
      newCart[existingIndex].discount = discount;
      setCart(newCart);
    } else {
      setCart([...cart, {
        ...selectedProduct,
        quantity,
        discount
      }]);
    }

    setSelectedProduct(null);
    setQuantity(1);
    setDiscount(0);
  };

  const removeFromCart = (sku) => {
    setCart(cart.filter(item => item.sku !== sku));
  };

  const calculateSubtotal = () => {
    return cart.reduce((sum, item) => {
      const itemTotal = item.sell_price * item.quantity;
      const discountAmount = (itemTotal * item.discount) / 100;
      return sum + (itemTotal - discountAmount);
    }, 0);
  };

  const subtotal = calculateSubtotal();
  const gst = subtotal * 0.18;
  const total = subtotal + gst;

  const submitSale = async () => {
    if (cart.length === 0) {
      alert('Cart is empty');
      return;
    }

    setLoading(true);
    try {
      const saleData = {
        items: cart.map(item => ({
          sku: item.sku,
          quantity: item.quantity,
          price: item.sell_price,
          discount: item.discount
        })),
        payment_mode: paymentMode,
        subtotal,
        gst,
        total
      };

      const response = await api.post('/api/v1/sales', saleData);
      setLastSaleData(response.data);
      setSaleSuccess(true);
      setCart([]);
      alert('Sale completed successfully!');
    } catch (error) {
      alert('Sale failed: ' + (error.response?.data?.message || error.message));
    } finally {
      setLoading(false);
    }
  };

  const printInvoice = () => {
    if (lastSaleData) {
      window.print();
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">New Sale</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <Card className="p-6 mb-4">
            <h2 className="text-xl font-semibold mb-4">Product Search</h2>
            <div className="relative">
              <Input
                type="text"
                placeholder="Search by SKU or product name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
              {showDropdown && searchResults.length > 0 && (
                <div className="absolute z-10 w-full mt-1 bg-white border rounded-lg shadow-lg max-h-60 overflow-y-auto">
                  {searchResults.map(product => (
                    <div
                      key={product.sku}
                      className="p-3 hover:bg-gray-100 cursor-pointer border-b"
                      onClick={() => selectProduct(product)}
                    >
                      <div className="font-medium">{product.name}</div>
                      <div className="text-sm text-gray-600">
                        SKU: {product.sku} | Stock: {product.available_stock} | ₹{product.sell_price}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Card>

          {selectedProduct && (
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Add to Cart</h2>
              <div className="space-y-4">
                <div>
                  <div className="font-medium text-lg">{selectedProduct.name}</div>
                  <div className="text-sm text-gray-600">SKU: {selectedProduct.sku}</div>
                  <div className="text-sm text-gray-600">Available Stock: {selectedProduct.available_stock}</div>
                  <div className="text-lg font-semibold text-green-600 mt-2">₹{selectedProduct.sell_price}</div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Quantity</label>
                    <Input
                      type="number"
                      min="1"
                      max={selectedProduct.available_stock}
                      value={quantity}
                      onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Discount (%)</label>
                    <Input
                      type="number"
                      min="0"
                      max="100"
                      value={discount}
                      onChange={(e) => setDiscount(parseFloat(e.target.value) || 0)}
                    />
                  </div>
                </div>

                <Button onClick={addToCart} className="w-full">
                  Add to Cart
                </Button>
              </div>
            </Card>
          )}
        </div>

        <div>
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Cart</h2>
            
            {cart.length === 0 ? (
              <p className="text-gray-500 text-center py-8">Cart is empty</p>
            ) : (
              <>
                <div className="overflow-x-auto mb-4">
                  <table className="w-full">
                    <thead className="border-b">
                      <tr>
                        <th className="text-left py-2">Product</th>
                        <th className="text-right py-2">Qty</th>
                        <th className="text-right py-2">Price</th>
                        <th className="text-right py-2">Disc%</th>
                        <th className="text-right py-2">Subtotal</th>
                        <th className="text-right py-2">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {cart.map(item => {
                        const itemTotal = item.sell_price * item.quantity;
                        const discountAmount = (itemTotal * item.discount) / 100;
                        const itemSubtotal = itemTotal - discountAmount;
                        
                        return (
                          <tr key={item.sku} className="border-b">
                            <td className="py-2">
                              <div className="font-medium">{item.name}</div>
                              <div className="text-xs text-gray-600">{item.sku}</div>
                            </td>
                            <td className="text-right">{item.quantity}</td>
                            <td className="text-right">₹{item.sell_price}</td>
                            <td className="text-right">{item.discount}%</td>
                            <td className="text-right font-medium">₹{itemSubtotal.toFixed(2)}</td>
                            <td className="text-right">
                              <button
                                onClick={() => removeFromCart(item.sku)}
                                className="text-red-600 hover:text-red-800 text-sm"
                              >
                                Remove
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                <div className="space-y-2 border-t pt-4">
                  <div className="flex justify-between">
                    <span>Subtotal:</span>
                    <span className="font-medium">₹{subtotal.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-sm text-gray-600">
                    <span>GST (18%):</span>
                    <span>₹{gst.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-xl font-bold border-t pt-2">
                    <span>Total:</span>
                    <span>₹{total.toFixed(2)}</span>
                  </div>
                </div>

                <div className="mt-6">
                  <label className="block text-sm font-medium mb-2">Payment Mode</label>
                  <div className="flex gap-4">
                    {['Cash', 'UPI', 'Card'].map(mode => (
                      <label key={mode} className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="radio"
                          name="paymentMode"
                          value={mode}
                          checked={paymentMode === mode}
                          onChange={(e) => setPaymentMode(e.target.value)}
                          className="w-4 h-4"
                        />
                        <span>{mode}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="mt-6 space-y-2">
                  <Button
                    onClick={submitSale}
                    disabled={loading}
                    className="w-full bg-green-600 hover:bg-green-700"
                  >
                    {loading ? 'Processing...' : 'Complete Sale'}
                  </Button>
                  
                  {saleSuccess && lastSaleData && (
                    <Button
                      onClick={printInvoice}
                      className="w-full"
                      variant="outline"
                    >
                      Print Invoice
                    </Button>
                  )}
                </div>
              </>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};

export default NewSale;