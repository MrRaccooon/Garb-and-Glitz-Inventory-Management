import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Login from './pages/Auth/Login';
import ProtectedRoute from './components/auth/ProtectedRoute';

// Real component imports
import ProductList from './pages/Products/ProductList';
import SalesHistory from './pages/Sales/SalesHistory';
import NewSale from './pages/Sales/NewSale';
import StockView from './pages/Inventory/StockView';
import AnalyticsDashboard from './pages/Analytics/AnalyticsDashboard';
import ForecastDashboard from './pages/Forecasting/ForecastDashboard';

// Placeholder imports
import {
  ProductForm,
  ProductDetail,
} from './pages/PlaceholderPages';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index element={<Dashboard />} />
          <Route path="products" element={<ProductList />} />
          <Route path="products/new" element={<ProductForm />} />
          <Route path="products/:sku" element={<ProductDetail />} />
          <Route path="sales" element={<SalesHistory />} />
          <Route path="sales/new" element={<NewSale />} />
          <Route path="inventory" element={<StockView />} />
          <Route path="forecast" element={<ForecastDashboard />} />
          <Route path="analytics" element={<AnalyticsDashboard />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;