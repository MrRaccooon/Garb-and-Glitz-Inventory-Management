import { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import axios from '../../api/client';

const subcategories = {
  Saree: ['Silk', 'Cotton', 'Georgette', 'Chiffon', 'Banarasi'],
  Suit: ['Anarkali', 'Straight', 'Palazzo', 'A-Line'],
  Lehenga: ['Bridal', 'Party Wear', 'Festive'],
  Dupatta: ['Net', 'Silk', 'Georgette', 'Chiffon']
};

export default function ProductForm({ 
  productData = null, 
  mode = 'create',
  onSuccess,
  onCancel 
}) {
  
  const [formData, setFormData] = useState({
    sku: '',
    name: '',
    category: 'Saree',
    subcategory: '',
    brand: '',
    size: '',
    color: '',
    fabric: '',
    costPrice: '',
    sellPrice: '',
    reorderPoint: '',
    leadTimeDays: ''
  });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (productData && mode === 'edit') {
      setFormData({
        sku: productData.sku || '',
        name: productData.name || '',
        category: productData.category || 'Saree',
        subcategory: productData.subcategory || '',
        brand: productData.brand || '',
        size: productData.size || '',
        color: productData.color || '',
        fabric: productData.fabric || '',
        costPrice: productData.cost_price || productData.costPrice || '',
        sellPrice: productData.sell_price || productData.sellPrice || '',
        reorderPoint: productData.reorder_point || productData.reorderPoint || '',
        leadTimeDays: productData.lead_time_days || productData.leadTimeDays || ''
      });
    }
  }, [productData, mode]);

  const validateField = (name, value) => {
    switch (name) {
      case 'sku':
        if (!value) return 'SKU is required';
        if (!/^[A-Z]{3}[0-9]{3}$/.test(value)) {
          return 'SKU must be 3 uppercase letters followed by 3 digits (e.g., SAR001)';
        }
        return '';
      case 'name':
        return !value ? 'Name is required' : '';
      case 'costPrice':
      case 'sellPrice':
        if (!value) return `${name === 'costPrice' ? 'Cost' : 'Sell'} price is required`;
        if (parseFloat(value) < 0) return 'Price must be positive';
        return '';
      default:
        return '';
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    let finalValue = value;

    if (name === 'sku') {
      finalValue = value.toUpperCase();
    }

    if (name === 'category') {
      setFormData({
        ...formData,
        [name]: finalValue,
        subcategory: ''
      });
    } else {
      setFormData({
        ...formData,
        [name]: finalValue
      });
    }

    const error = validateField(name, finalValue);
    setErrors({
      ...errors,
      [name]: error
    });
  };

  const validateForm = () => {
    const newErrors = {};
    Object.keys(formData).forEach((key) => {
      const error = validateField(key, formData[key]);
      if (error) newErrors[key] = error;
    });
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      alert('Please fix all validation errors');
      return;
    }

    try {
      setSubmitting(true);
      const payload = {
        sku: formData.sku,
        name: formData.name,
        category: formData.category,
        subcategory: formData.subcategory || null,
        brand: formData.brand || null,
        size: formData.size || null,
        color: formData.color || null,
        fabric: formData.fabric || null,
        cost_price: parseFloat(formData.costPrice),
        sell_price: parseFloat(formData.sellPrice),
        reorder_point: parseInt(formData.reorderPoint) || 10,
        lead_time_days: parseInt(formData.leadTimeDays) || 7,
        supplier_id: null,
        season_tag: null,
        hsn_code: null,
        active: true
      };

      if (mode === 'create') {
        await axios.post('/products', payload);
        alert('Product created successfully');
        if (onSuccess) onSuccess();
      } else {
        await axios.put(`/products/${formData.sku}`, payload);
        alert('Product updated successfully');
        if (onSuccess) onSuccess();
      }

    } catch (err) {
      alert('Failed to save product: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancel = () => {
    if (onCancel) onCancel();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* SKU */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            SKU <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            name="sku"
            value={formData.sku}
            onChange={handleChange}
            disabled={mode === 'edit'}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
            placeholder="SAR001"
            maxLength={6}
          />
          {errors.sku && <p className="text-red-600 text-sm mt-1">{errors.sku}</p>}
        </div>

        {/* Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Product name"
          />
          {errors.name && <p className="text-red-600 text-sm mt-1">{errors.name}</p>}
        </div>

        {/* Category */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Category <span className="text-red-500">*</span>
          </label>
          <select
            name="category"
            value={formData.category}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="Saree">Saree</option>
            <option value="Suit">Suit</option>
            <option value="Lehenga">Lehenga</option>
            <option value="Dupatta">Dupatta</option>
          </select>
        </div>

        {/* Subcategory */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Subcategory</label>
          <select
            name="subcategory"
            value={formData.subcategory}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Select subcategory</option>
            {subcategories[formData.category]?.map((sub) => (
              <option key={sub} value={sub}>
                {sub}
              </option>
            ))}
          </select>
        </div>

        {/* Brand */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Brand</label>
          <input
            type="text"
            name="brand"
            value={formData.brand}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Brand name"
          />
        </div>

        {/* Size */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Size</label>
          <input
            type="text"
            name="size"
            value={formData.size}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Free Size / S / M / L"
          />
        </div>

        {/* Color */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Color</label>
          <input
            type="text"
            name="color"
            value={formData.color}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Red / Blue / Multi"
          />
        </div>

        {/* Fabric */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Fabric</label>
          <input
            type="text"
            name="fabric"
            value={formData.fabric}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Silk / Cotton / Georgette"
          />
        </div>

        {/* Cost Price */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Cost Price (₹) <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            name="costPrice"
            value={formData.costPrice}
            onChange={handleChange}
            min="0"
            step="0.01"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="0.00"
          />
          {errors.costPrice && <p className="text-red-600 text-sm mt-1">{errors.costPrice}</p>}
        </div>

        {/* Sell Price */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Sell Price (₹) <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            name="sellPrice"
            value={formData.sellPrice}
            onChange={handleChange}
            min="0"
            step="0.01"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="0.00"
          />
          {errors.sellPrice && <p className="text-red-600 text-sm mt-1">{errors.sellPrice}</p>}
        </div>

        {/* Reorder Point */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Reorder Point</label>
          <input
            type="number"
            name="reorderPoint"
            value={formData.reorderPoint}
            onChange={handleChange}
            min="0"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="10"
          />
        </div>

        {/* Lead Time Days */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Lead Time (Days)</label>
          <input
            type="number"
            name="leadTimeDays"
            value={formData.leadTimeDays}
            onChange={handleChange}
            min="0"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="7"
          />
        </div>
      </div>

      <div className="flex gap-4 justify-end pt-4 border-t">
        <Button type="button" onClick={handleCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={submitting}>
          {submitting ? 'Saving...' : mode === 'create' ? 'Create Product' : 'Update Product'}
        </Button>
      </div>
    </form>
  );
}