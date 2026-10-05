import { BrowserRouter, Routes, Route } from 'react-router-dom';
import DashboardLayout from './Components/Dashboard/DashboardLayout';
import Dashboard from './pages/Dashboard/Dashboard';
import Upload from './pages/Upload/Upload';
import Forecasting from './pages/Forecasting/Forecasting';
import ModelComparison from './pages/ModelComparison/ModelComparison';
import Inventory from './pages/Inventory/Inventory';
import ForecastHistory from './pages/ForecastHistory/ForecastHistory';
import Products from './pages/Products/Products';

export default function App() {
  return (
    <BrowserRouter>
      <DashboardLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/products" element={<Products />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/forecasting" element={<Forecasting />} />
          <Route path="/model-comparison" element={<ModelComparison />} />
          <Route path="/inventory" element={<Inventory />} />
          <Route path="/forecast-history" element={<ForecastHistory />} />
        </Routes>
      </DashboardLayout>
    </BrowserRouter>
  );
}
