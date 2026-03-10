// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Layout/Navbar';
import CoachPage from './pages/CoachPage';
import MetaAnalyticsPage from './pages/MetaAnalyticsPage'; // We will build this later
import './App.css';

function App() {
  return (
    <Router>
      <div className="app-root" style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
        {/* The Navbar stays at the top of every page */}
        <Navbar />
        
        {/* The Routes determine what renders below the Navbar */}
        <div className="page-content" style={{ flexGrow: 1, overflow: 'hidden' }}>
          <Routes>
            <Route path="/" element={<CoachPage />} />
            <Route path="/meta" element={<MetaAnalyticsPage />} />
            {/* Add more routes here as your app grows! */}
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;