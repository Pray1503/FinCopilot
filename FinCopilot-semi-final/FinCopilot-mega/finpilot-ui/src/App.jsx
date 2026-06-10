import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { ProfileProvider, useProfile } from './context/ProfileContext';
import ProfileModal from './components/ProfileModal';
import Sidebar from './components/Sidebar';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import CopilotChat from './pages/CopilotChat';
import Boardroom from './pages/Boardroom';
import CashFlow from './pages/CashFlow';
import DecisionSim from './pages/DecisionSim';
import SpendingInsights from './pages/SpendingInsights';
import BillScanner from './pages/BillScanner';

function AppLayout() {
  const location = useLocation();
  const { hasProfile, setProfile } = useProfile();
  const isLanding = location.pathname === '/';

  if (isLanding) {
    return <Landing />;
  }

  return (
    <>
      {!hasProfile && <ProfileModal onSave={setProfile} />}
      <div className="layout-app">
        <Sidebar />
        <main className="layout-main">
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/chat" element={<CopilotChat />} />
            <Route path="/boardroom" element={<Boardroom />} />
            <Route path="/cashflow" element={<CashFlow />} />
            <Route path="/simulator" element={<DecisionSim />} />
            <Route path="/spending" element={<SpendingInsights />} />
            <Route path="/bills" element={<BillScanner />} />
          </Routes>
        </main>
      </div>
    </>
  );
}

export default function App() {
  return (
    <ProfileProvider>
      <Router>
        <Routes>
          <Route path="/*" element={<AppLayout />} />
        </Routes>
      </Router>
    </ProfileProvider>
  );
}
