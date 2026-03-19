// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Layout/NavBar';
import CoachPage from './pages/CoachPage';
import MetaAnalyticsPage from './pages/MetaAnalyticsPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app-root" style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
        <Navbar />
        
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