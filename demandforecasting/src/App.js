import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './Components/Navbar/Navbar';
import Dashboard from './pages/Dashboard/Dashboard';
import Upload from './pages/Upload/Upload';
import Forecasting from './pages/Forecasting/Forecasting';
import ModelComparison from './pages/ModelComparison/ModelComparison';
import Inventory from './pages/Inventory/Inventory';
import ForecastHistory from './pages/ForecastHistory/ForecastHistory';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/forecasting" element={<Forecasting />} />
            <Route path="/model-comparison" element={<ModelComparison />} />
            <Route path="/inventory" element={<Inventory />} />
            <Route path="/forecast-history" element={<ForecastHistory />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
