// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ChatProvider } from './components/Chat/ChatContext';
import { ThemeProvider } from './context/ThemeContext';
import Navbar from './components/Layout/NavBar';
import CoachPage from './pages/CoachPage';
import MetaAnalyticsPage from './pages/MetaAnalyticsPage';
import HomePage from './pages/HomePage';
import './App.css';
import TeambuilderLayout from './pages/TeamBuilderPage';

function App() {
  return (
    <ThemeProvider>
      <ChatProvider>
        <Router>
          <div className="app-root">
            <Navbar />
            
            <div className="page-content">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/coach" element={<CoachPage />} />
                <Route path="/meta" element={<MetaAnalyticsPage />} />
                <Route path="/team" element={<TeambuilderLayout />} />
              </Routes>
            </div>
          </div>
        </Router>
      </ChatProvider>
    </ThemeProvider>
  );
}

export default App;