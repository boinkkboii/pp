// src/components/Layout/Navbar.jsx
import { Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <nav style={{
      display: 'flex',
      alignItems: 'center',
      padding: '0 20px',
      height: '60px',
      backgroundColor: '#12185b',
      color: 'white',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    }}>
      <h1 style={{ fontSize: '1.2rem', marginRight: '40px' }}>
        <Link to="/" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>VGC Limitless AI</Link>
      </h1>
      
      <div style={{ display: 'flex', gap: '20px' }}>
        <Link to="/coach" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>Coach</Link>
        <Link to="/meta" style={{ color: 'white', textDecoration: 'none', fontWeight: '500' }}>Meta Analytics</Link>
      </div>
    </nav>
  );
}