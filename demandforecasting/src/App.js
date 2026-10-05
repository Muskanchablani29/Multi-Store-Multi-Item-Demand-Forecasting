import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from './Components/Dashboard/DashboardLayout';
import Home from './Components/Home/Home';
import Dashboard from './pages/Dashboard/Dashboard';
import Upload from './pages/Upload/Upload';
import Forecasting from './pages/Forecasting/Forecasting';
import ModelComparison from './pages/ModelComparison/ModelComparison';
import Inventory from './pages/Inventory/Inventory';
import ForecastHistory from './pages/ForecastHistory/ForecastHistory';
import Products from './pages/Products/Products';

function PrivateRoute({ children }) {
  return localStorage.getItem('token') ? (
    <DashboardLayout>{children}</DashboardLayout>
  ) : (
    <Navigate to="/login" replace />
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Home />} />
        <Route path="/" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/products" element={<PrivateRoute><Products /></PrivateRoute>} />
        <Route path="/upload" element={<PrivateRoute><Upload /></PrivateRoute>} />
        <Route path="/forecasting" element={<PrivateRoute><Forecasting /></PrivateRoute>} />
        <Route path="/model-comparison" element={<PrivateRoute><ModelComparison /></PrivateRoute>} />
        <Route path="/inventory" element={<PrivateRoute><Inventory /></PrivateRoute>} />
        <Route path="/forecast-history" element={<PrivateRoute><ForecastHistory /></PrivateRoute>} />
      </Routes>
    </BrowserRouter>
  );
}
