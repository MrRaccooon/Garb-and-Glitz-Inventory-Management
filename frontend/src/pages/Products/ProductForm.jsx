import { useState, useEffect } from 'react';
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
    reorderPoint: '10',
    leadTimeDays: '7',
    supplierId: ''  // ✅ ADDED: Supplier ID field
  });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [suppliers, setSuppliers] = useState([]);  // ✅ ADDED: Suppliers list
  const [loadingSuppliers, setLoadingSuppliers] = useState(false);

  // ✅ ADDED: Fetch suppliers on component mount
  useEffect(() => {
    const fetchSuppliers = async () => {
      try {
        setLoadingSuppliers(true);
        const response = await axios.get('/suppliers');
        setSuppliers(response.data);
      } catch (error) {
        console.error('Failed to fetch suppliers:', error);
        // Continue without suppliers - field is optional
      } finally {
        setLoadingSuppliers(false);
      }
    };

    fetchSuppliers();
  }, []);

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
        reorderPoint: productData.reorder_point || productData.reorderPoint || '10',
        leadTimeDays: productData.lead_time_days || productData.leadTimeDays || '7',
        supplierId: productData.supplier_id || productData.supplierId || ''  // ✅ ADDED
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
      case 'category':
        return !value ? 'Category is required' : '';
      case 'costPrice':
      case 'sellPrice':
        if (!value) return `${name === 'costPrice' ? 'Cost' : 'Sell'} price is required`;
        if (parseFloat(value) <= 0) return 'Price must be greater than 0';
        return '';
      case 'reorderPoint':
      case 'leadTimeDays':
        if (value && parseInt(value) < 0) return 'Must be a positive number';
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
      const error = validateField(name, finalValue);
      setErrors({
        ...errors,
        [name]: error
      });
    } else {
      setFormData({
        ...formData,
        [name]: finalValue
      });
      
      const error = validateField(name, finalValue);
      setErrors({
        ...errors,
        [name]: error
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    // Validate required fields
    const requiredFields = ['sku', 'name', 'category', 'costPrice', 'sellPrice'];
    requiredFields.forEach((key) => {
      const error = validateField(key, formData[key]);
      if (error) newErrors[key] = error;
    });
    
    // Additional validation: sell price >= cost price
    if (formData.sellPrice && formData.costPrice) {
      if (parseFloat(formData.sellPrice) < parseFloat(formData.costPrice)) {
        newErrors.sellPrice = 'Sell price cannot be less than cost price';
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      alert('Please fix all validation errors before submitting');
      return;
    }

    try {
      setSubmitting(true);
      
      // Build payload - only send fields with actual values
      const payload = {
        sku: formData.sku.trim(),
        name: formData.name.trim(),
        category: formData.category,
        cost_price: parseFloat(formData.costPrice),
        sell_price: parseFloat(formData.sellPrice),
        reorder_point: parseInt(formData.reorderPoint) || 10,
        lead_time_days: parseInt(formData.leadTimeDays) || 7,
        active: true
      };

      // Add optional fields only if they have values
      if (formData.subcategory && formData.subcategory.trim()) {
        payload.subcategory = formData.subcategory.trim();
      }
      
      if (formData.brand && formData.brand.trim()) {
        payload.brand = formData.brand.trim();
      }
      
      if (formData.size && formData.size.trim()) {
        payload.size = formData.size.trim();
      }
      
      if (formData.color && formData.color.trim()) {
        payload.color = formData.color.trim();
      }
      
      if (formData.fabric && formData.fabric.trim()) {
        payload.fabric = formData.fabric.trim();
      }

      // ✅ ADDED: Include supplier_id if selected
      if (formData.supplierId) {
        payload.supplier_id = formData.supplierId;
      }

      console.log('=== SUBMITTING PRODUCT ===');
      console.log('Mode:', mode);
      console.log('Payload:', JSON.stringify(payload, null, 2));

      let response;
      if (mode === 'create') {
        console.log('POST /products');
        response = await axios.post('/products', payload);
      } else {
        console.log(`PUT /products/${formData.sku}`);
        response = await axios.put(`/products/${formData.sku}`, payload);
      }

      console.log('=== SUCCESS ===');
      console.log('Response:', response.data);
      
      alert(`Product ${mode === 'create' ? 'created' : 'updated'} successfully!`);
      if (onSuccess) onSuccess();

    } catch (err) {
      console.error('=== ERROR SUBMITTING PRODUCT ===');
      console.error('Error object:', err);
      
      let errorMessage = `Failed to ${mode === 'create' ? 'create' : 'update'} product:\n\n`;
      
      if (err.response) {
        console.error('Response status:', err.response.status);
        console.error('Response data:', err.response.data);
        
        // Handle different error formats
        if (err.response.data?.detail) {
          const detail = err.response.data.detail;
          
          // Pydantic validation errors (array format)
          if (Array.isArray(detail)) {
            errorMessage += 'Validation errors:\n';
            detail.forEach(error => {
              const field = error.loc.join(' → ');
              errorMessage += `• ${field}: ${error.msg}\n`;
            });
          } 
          // String error message
          else if (typeof detail === 'string') {
            errorMessage += detail;
          }
          // Object error message
          else {
            errorMessage += JSON.stringify(detail, null, 2);
          }
        } 
        // Generic error response
        else {
          errorMessage += JSON.stringify(err.response.data, null, 2);
        }
      } else if (err.request) {
        console.error('No response received:', err.request);
        errorMessage += 'No response from server. Please check your connection.';
      } else {
        console.error('Error message:', err.message);
        errorMessage += err.message;
      }
      
      alert(errorMessage);
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
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            placeholder="SAR001"
            maxLength={6}
            required
          />
          {errors.sku && <p className="text-red-600 text-sm mt-1">{errors.sku}</p>}
          <p className="text-xs text-gray-500 mt-1">Format: 3 letters + 3 digits (e.g., SAR001)</p>
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
            required
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
            required
          >
            <option value="Saree">Saree</option>
            <option value="Suit">Suit</option>
            <option value="Lehenga">Lehenga</option>
            <option value="Dupatta">Dupatta</option>
          </select>
          {errors.category && <p className="text-red-600 text-sm mt-1">{errors.category}</p>}
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
            min="0.01"
            step="0.01"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="1000.00"
            required
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
            min="0.01"
            step="0.01"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="1500.00"
            required
          />
          {errors.sellPrice && <p className="text-red-600 text-sm mt-1">{errors.sellPrice}</p>}
        </div>

        {/* ✅ ADDED: Supplier Dropdown */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Supplier</label>
          <select
            name="supplierId"
            value={formData.supplierId}
            onChange={handleChange}
            disabled={loadingSuppliers}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
          >
            <option value="">Select supplier (optional)</option>
            {suppliers.map((supplier) => (
              <option key={supplier.supplier_id} value={supplier.supplier_id}>
                {supplier.name} - {supplier.contact_person}
              </option>
            ))}
          </select>
          {loadingSuppliers && <p className="text-xs text-gray-500 mt-1">Loading suppliers...</p>}
        </div>

        {/* Reorder Point */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Reorder Point
          </label>
          <input
            type="number"
            name="reorderPoint"
            value={formData.reorderPoint}
            onChange={handleChange}
            min="0"
            step="1"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="10"
          />
          {errors.reorderPoint && <p className="text-red-600 text-sm mt-1">{errors.reorderPoint}</p>}
          <p className="text-xs text-gray-500 mt-1">Stock level to trigger reorder (default: 10)</p>
        </div>

        {/* Lead Time Days */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Lead Time (Days)
          </label>
          <input
            type="number"
            name="leadTimeDays"
            value={formData.leadTimeDays}
            onChange={handleChange}
            min="0"
            step="1"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="7"
          />
          {errors.leadTimeDays && <p className="text-red-600 text-sm mt-1">{errors.leadTimeDays}</p>}
          <p className="text-xs text-gray-500 mt-1">Days to receive stock after ordering (default: 7)</p>
        </div>
      </div>

      <div className="flex gap-4 justify-end pt-4 border-t border-gray-200">
        <Button 
          type="button" 
          onClick={handleCancel}
          disabled={submitting}
          className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
        >
          Cancel
        </Button>
        <Button 
          type="submit" 
          disabled={submitting}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {submitting ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
              Saving...
            </span>
          ) : (
            mode === 'create' ? 'Create Product' : 'Update Product'
          )}
        </Button>
      </div>
    </form>
  );
}