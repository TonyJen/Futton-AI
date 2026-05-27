import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';

// Pages
import Dashboard from './pages/Dashboard';
import Items from './pages/Items';
import Inventory from './pages/Inventory';
import Production from './pages/Production';
import Agents from './pages/Agents';
import Sales from './pages/Sales';
import Quotes from './pages/Quotes';
import Returns from './pages/Returns';
import Purchasing from './pages/Purchasing';
import Reports from './pages/Reports';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/items" element={<Items />} />
        <Route path="/inventory" element={<Inventory />} />
        <Route path="/production" element={<Production />} />
        <Route path="/sales" element={<Sales />} />
        <Route path="/quotes" element={<Quotes />} />
        <Route path="/returns" element={<Returns />} />
        <Route path="/purchasing" element={<Purchasing />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/agents" element={<Agents />} />
        {/* Fallback */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Layout>
  );
}

export default App;
