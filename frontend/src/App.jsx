import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import {
  ProductList,
  ProductForm,
  ProductDetail,
  SalesHistory,
  NewSale,
  StockView,
  ForecastDashboard,
  Reports,
} from './pages/PlaceholderPages';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="products" element={<ProductList />} />
          <Route path="products/new" element={<ProductForm />} />
          <Route path="products/:sku" element={<ProductDetail />} />
          <Route path="sales" element={<SalesHistory />} />
          <Route path="sales/new" element={<NewSale />} />
          <Route path="inventory" element={<StockView />} />
          <Route path="forecast" element={<ForecastDashboard />} />
          <Route path="analytics" element={<Reports />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;