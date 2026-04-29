import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import '../App.css';

const ProfilePage = () => {
  const { user, logout } = useAuth();
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [showOld, setShowOld] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  if (!user) return <div className="container">Please log in to view your profile.</div>;

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (newPassword !== confirmPassword) {
      setError("New passwords don't match");
      return;
    }

    if (newPassword.length < 8) {
      setError("New password must be at least 8 characters long");
      return;
    }

    setLoading(true);
    try {
      await api.changePassword(oldPassword, newPassword);
      setSuccess('Password updated successfully');
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      setError(err.message || 'Failed to update password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container" style={{ maxWidth: '600px', marginTop: '40px' }}>
      <div className="card" style={{ padding: '32px' }}>
        <h1 className="card-title">User Profile</h1>
        
        <div style={{ marginBottom: '32px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span className="text-muted">Username</span>
            <span style={{ fontWeight: 'bold' }}>{user.username}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span className="text-muted">Member Since</span>
            <span>{new Date(user.created_at).toLocaleDateString()}</span>
          </div>
        </div>

        <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '32px' }}>
          <h2 style={{ fontSize: '1.2rem', marginBottom: '20px' }}>Security Settings</h2>
          
          <form onSubmit={handleChangePassword} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {error && (
              <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', padding: '12px', borderRadius: '8px', fontSize: '0.9rem' }}>
                {error}
              </div>
            )}
            {success && (
              <div style={{ background: 'rgba(16, 185, 129, 0.1)', color: '#10b981', padding: '12px', borderRadius: '8px', fontSize: '0.9rem' }}>
                {success}
              </div>
            )}

            <div style={{ position: 'relative' }}>
              <label className="text-muted" style={{ display: 'block', marginBottom: '8px' }}>Current Password</label>
              <input 
                type={showOld ? 'text' : 'password'} 
                className="chat-input" 
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
                required
                style={{ width: '100%', boxSizing: 'border-box', paddingRight: '60px' }}
                autoComplete="current-password"
              />
              <button
                type="button"
                onClick={() => setShowOld(!showOld)}
                style={{
                  position: 'absolute', right: '10px', bottom: '10px',
                  background: 'none', border: 'none', cursor: 'pointer', 
                  fontSize: '0.7rem', fontWeight: '700', color: 'var(--primary-color)',
                  opacity: 0.8, textTransform: 'uppercase'
                }}
              >
                {showOld ? 'HIDE' : 'SHOW'}
              </button>
            </div>

            <div style={{ position: 'relative' }}>
              <label className="text-muted" style={{ display: 'block', marginBottom: '8px' }}>New Password</label>
              <input 
                type={showNew ? 'text' : 'password'} 
                className="chat-input" 
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                style={{ width: '100%', boxSizing: 'border-box', paddingRight: '60px' }}
                autoComplete="new-password"
              />
              <button
                type="button"
                onClick={() => setShowNew(!showNew)}
                style={{
                  position: 'absolute', right: '10px', bottom: '10px',
                  background: 'none', border: 'none', cursor: 'pointer', 
                  fontSize: '0.7rem', fontWeight: '700', color: 'var(--primary-color)',
                  opacity: 0.8, textTransform: 'uppercase'
                }}
              >
                {showNew ? 'HIDE' : 'SHOW'}
              </button>
            </div>

            <div style={{ position: 'relative' }}>
              <label className="text-muted" style={{ display: 'block', marginBottom: '8px' }}>Confirm New Password</label>
              <input 
                type={showConfirm ? 'text' : 'password'} 
                className="chat-input" 
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                style={{ width: '100%', boxSizing: 'border-box', paddingRight: '60px' }}
                autoComplete="new-password"
              />
              <button
                type="button"
                onClick={() => setShowConfirm(!showConfirm)}
                style={{
                  position: 'absolute', right: '10px', bottom: '10px',
                  background: 'none', border: 'none', cursor: 'pointer', 
                  fontSize: '0.7rem', fontWeight: '700', color: 'var(--primary-color)',
                  opacity: 0.8, textTransform: 'uppercase'
                }}
              >
                {showConfirm ? 'HIDE' : 'SHOW'}
              </button>
            </div>
            
            <button className="btn-primary" type="submit" disabled={loading} style={{ marginTop: '8px' }}>
              {loading ? 'Updating...' : 'Update Password'}
            </button>
          </form>
        </div>

        <div style={{ marginTop: '40px', paddingTop: '24px', borderTop: '1px solid var(--border-color)', textAlign: 'center' }}>
          <button 
            onClick={logout}
            style={{ 
              background: 'none', border: '1px solid #ef4444', color: '#ef4444', 
              padding: '10px 24px', borderRadius: '8px', cursor: 'pointer',
              fontWeight: 'bold', width: '100%'
            }}
          >
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
