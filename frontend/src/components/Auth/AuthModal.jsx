import React, { useState } from 'react';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

const AuthModal = ({ isOpen, onClose }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { login } = useAuth();

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!isLogin && password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (!isLogin && password.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }

    setLoading(true);

    try {
      if (isLogin) {
        const data = await api.login(username, password);
        login(data.access_token);
        onClose();
      } else {
        await api.register(username, password);
        const data = await api.login(username, password);
        login(data.access_token);
        onClose();
      }
    } catch (err) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleMode = (mode) => {
    setIsLogin(mode);
    setError('');
    setPassword('');
    setConfirmPassword('');
  };

  return (
    <div className="modal-overlay" onClick={onClose} style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(15, 23, 42, 0.85)', 
      backdropFilter: 'blur(4px)',
      zIndex: 3000,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: '20px'
    }}>
      <div className="card" onClick={(e) => e.stopPropagation()} style={{
        width: '100%',
        maxWidth: '400px',
        padding: '40px',
        position: 'relative',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.2)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px'
      }}>
        <button onClick={onClose} style={{
          position: 'absolute', top: '20px', right: '20px',
          background: 'none', border: 'none', 
          fontSize: '1.5rem', cursor: 'pointer',
          color: 'var(--text-secondary)',
          zIndex: 10,
          opacity: 0.5
        }}>&times;</button>

        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h2 style={{ margin: 0, fontSize: '1.5rem', color: 'var(--primary-color)', textTransform: 'uppercase', letterSpacing: '1px' }}>
            {isLogin ? 'Login' : 'Register'}
          </h2>
          <p className="text-muted" style={{ marginTop: '8px', fontSize: '0.9rem' }}>
            {isLogin ? 'Enter your credentials to continue' : 'Create an account to save your teams'}
          </p>
        </div>

        {/* Segmented Control */}
        <div style={{
          display: 'flex',
          background: 'var(--bg-color)',
          padding: '4px',
          borderRadius: '10px',
          marginBottom: '28px',
          border: '1px solid var(--border-color)'
        }}>
          <button 
            onClick={() => handleToggleMode(true)}
            style={{
              flex: 1, padding: '8px', border: 'none', borderRadius: '6px',
              background: isLogin ? 'var(--card-bg)' : 'transparent',
              color: isLogin ? 'var(--primary-color)' : 'var(--text-secondary)',
              fontWeight: '600', cursor: 'pointer', fontSize: '0.85rem',
              transition: 'all 0.2s'
            }}
          >
            LOGIN
          </button>
          <button 
            onClick={() => handleToggleMode(false)}
            style={{
              flex: 1, padding: '8px', border: 'none', borderRadius: '6px',
              background: !isLogin ? 'var(--card-bg)' : 'transparent',
              color: !isLogin ? 'var(--primary-color)' : 'var(--text-secondary)',
              fontWeight: '600', cursor: 'pointer', fontSize: '0.85rem',
              transition: 'all 0.2s'
            }}
          >
            REGISTER
          </button>
        </div>

        {error && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.05)', color: '#ef4444',
            padding: '12px', borderRadius: '8px', marginBottom: '20px',
            fontSize: '0.8rem', textAlign: 'center', border: '1px solid rgba(239, 68, 68, 0.2)'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
              Username
            </label>
            <input
              type="text"
              className="chat-input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoFocus
              placeholder="Username"
              style={{ width: '100%', boxSizing: 'border-box' }}
              autoComplete="username"
            />
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <label style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
              Password
            </label>
            <div style={{ position: 'relative', width: '100%' }}>
              <input
                type={showPassword ? 'text' : 'password'}
                className="chat-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Password"
                style={{ width: '100%', boxSizing: 'border-box', paddingRight: '60px' }}
                autoComplete={isLogin ? "current-password" : "new-password"}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute', 
                  right: '10px', 
                  top: '50%', 
                  transform: 'translateY(-50%)',
                  background: 'none', 
                  border: 'none', 
                  cursor: 'pointer', 
                  fontSize: '0.7rem',
                  fontWeight: '700',
                  color: 'var(--primary-color)',
                  opacity: 0.8,
                  textTransform: 'uppercase'
                }}
              >
                {showPassword ? 'HIDE' : 'SHOW'}
              </button>
            </div>
          </div>

          {!isLogin && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <label style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                Confirm Password
              </label>
              <input
                type={showPassword ? 'text' : 'password'}
                className="chat-input"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                placeholder="Confirm Password"
                style={{ width: '100%', boxSizing: 'border-box' }}
                autoComplete="new-password"
              />
            </div>
          )}
          
          <button 
            className="btn-primary" 
            type="submit" 
            disabled={loading} 
            style={{ 
              height: '44px', marginTop: '10px', fontSize: '0.9rem'
            }}
          >
            {loading ? 'PROCESSING...' : isLogin ? 'LOGIN' : 'REGISTER'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AuthModal;
