// src/components/Layout/NavBar.jsx
import { Link, useLocation } from 'react-router-dom';
import { useTheme } from '../../context/ThemeContext';

export default function Navbar() {
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="nav-left">
        <div className="nav-brand">
          <Link to="/">PRO GAME ANALYTICS</Link>
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
            Meta Analytics
          </Link>
          <Link 
            to="/team" 
            className={`nav-link ${isActive('/team') ? 'active' : ''}`}
          >
            Teambuilder
          </Link>
        </div>
      </div>

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
    </nav>
  );
}
