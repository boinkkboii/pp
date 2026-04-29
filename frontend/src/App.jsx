import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Layout/NavBar';
import HomePage from './pages/HomePage';
import CoachPage from './pages/CoachPage';
import MetaAnalyticsPage from './pages/MetaAnalyticsPage';
import TeamBuilderPage from './pages/TeamBuilderPage';
import ProfilePage from './pages/ProfilePage';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './context/AuthContext';
import { ChatProvider } from './components/Chat/ChatContext';
import './App.css';

function App() {
  return (
    <Router>
      <AuthProvider>
        <ThemeProvider>
          <ChatProvider>
            <div className="app-root">
              <Navbar />
              <main className="page-content">
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/coach" element={<CoachPage />} />
                  <Route path="/meta" element={<MetaAnalyticsPage />} />
                  <Route path="/team" element={<TeamBuilderPage />} />
                  <Route path="/profile" element={<ProfilePage />} />
                </Routes>
              </main>
            </div>
          </ChatProvider>
        </ThemeProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
