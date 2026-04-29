// src/components/Layout/NavBar.jsx
import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useTheme } from '../../context/ThemeContext';
import { useAuth } from '../../context/AuthContext';
import AuthModal from '../Auth/AuthModal';

export default function Navbar() {
  const { theme, toggleTheme } = useTheme();
  const { user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  const isActive = (path) => location.pathname === path;

  const handleProfileClick = () => {
    if (user) {
      navigate('/profile');
    } else {
      setIsAuthModalOpen(true);
    }
  };

  return (
    <>
      <nav className="navbar">
        <div className="navbar-container">
          <div className="nav-left">
            <div className="nav-brand">
              <Link to="/">VGC ANALYTICS</Link>
            </div>
            
            <div className="nav-links">
              <Link 
                to="/coach" 
                className={`nav-link ${isActive('/coach') ? 'active' : ''}`}
              >
                Coach
              </Link>
              <Link 
                to="/meta" 
                className={`nav-link ${isActive('/meta') ? 'active' : ''}`}
              >
                Tournaments
              </Link>
              <Link 
                to="/team" 
                className={`nav-link ${isActive('/team') ? 'active' : ''}`}
              >
                Teambuilder
              </Link>
            </div>
          </div>

          <div className="nav-right" style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <div className="theme-toggle">
              <label className="switch">
                <input 
                  type="checkbox" 
                  checked={theme === 'dark'} 
                  onChange={toggleTheme} 
                />
                <span className="slider"></span>
              </label>
            </div>

            <button 
              onClick={handleProfileClick}
              style={{ 
                background: user ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.1)', 
                border: '1px solid rgba(255,255,255,0.3)',
                padding: '6px', cursor: 'pointer',
                color: 'white',
                display: 'flex', alignItems: 'center', transition: 'all 0.2s',
                borderRadius: '8px',
              }}
              title={user ? `Profile: ${user.username}` : 'Login / Register'}
            >
              <svg 
                width="20" 
                height="20" 
                viewBox="0 0 24 24" 
                fill={user ? "currentColor" : "none"} 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round"
              >
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
            </button>
          </div>
        </div>
      </nav>

      <AuthModal 
        isOpen={isAuthModalOpen} 
        onClose={() => setIsAuthModalOpen(false)} 
      />
    </>
  );
}
