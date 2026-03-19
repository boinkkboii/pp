// src/pages/MetaAnalyticsPage.jsx
import { useState, useEffect } from 'react';
import '../App.css';
import { api } from '../services/api'; // <-- IMPORTING YOUR NEW API SERVICE

export default function MetaAnalyticsPage() {
  const [tournaments, setTournaments] = useState([]);
  const [selectedTournament, setSelectedTournament] = useState(null);
  const [metaStats, setMetaStats] = useState([]);
  const [loading, setLoading] = useState(true);

  // 1. Fetch all tournaments using the centralized API
  useEffect(() => {
    const fetchTournaments = async () => {
      try {
        const data = await api.getAllTournaments();
        setTournaments(data);
      } catch (error) {
        console.error("Failed to fetch tournaments:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchTournaments();
  }, []);

  // 2. Fetch specific meta stats using the centralized API
  const handleTournamentClick = async (tournament) => {
    setSelectedTournament(tournament);
    setMetaStats([]); 
    
    try {
      const data = await api.getTournamentMeta(tournament.limitless_id);
      setMetaStats(data);
    } catch (error) {
      console.error("Failed to fetch meta stats:", error);
    }
  };

  return (
    // Locked height to viewport to prevent Navbar shift
    <div className="analytics-container" style={{ display: 'flex', height: 'calc(100vh - 70px)', overflow: 'hidden', padding: '20px', gap: '20px', boxSizing: 'border-box' }}>
      
      {/* LEFT COLUMN: Tournament List */}
      <div className="tournament-list" style={{ width: '30%', backgroundColor: 'white', borderRadius: '8px', padding: '15px', overflowY: 'auto', height: '100%', boxShadow: '0 2px 4px rgba(0,0,0,0.05)', boxSizing: 'border-box' }}>
        <h2 style={{ borderBottom: '2px solid #1a237e', paddingBottom: '10px', marginBottom: '15px', color: '#1a237e' }}>
          Recent Events
        </h2>
        
        {loading ? <p>Loading database...</p> : (
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {tournaments.map((t) => (
              <li 
                key={t.id} 
                onClick={() => handleTournamentClick(t)}
                style={{ 
                  padding: '12px', 
                  marginBottom: '8px', 
                  backgroundColor: selectedTournament?.id === t.id ? '#e8eaf6' : '#f8f9fa',
                  borderLeft: selectedTournament?.id === t.id ? '4px solid #1a237e' : '4px solid transparent',
                  cursor: 'pointer',
                  borderRadius: '4px',
                  transition: 'background-color 0.2s'
                }}
              >
                <strong style={{ display: 'block', fontSize: '1rem', color: '#333' }}>{t.name}</strong>
                <span style={{ fontSize: '0.85rem', color: '#666' }}>
                  {new Date(t.date).toLocaleDateString()} • {t.format?.name || t.format}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* RIGHT COLUMN: The Meta Breakdown */}
      <div className="meta-details" style={{ width: '70%', backgroundColor: 'white', borderRadius: '8px', padding: '20px', overflowY: 'auto', height: '100%', boxShadow: '0 2px 4px rgba(0,0,0,0.05)', boxSizing: 'border-box' }}>
        {!selectedTournament ? (
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#999' }}>
            <h3>Select a tournament from the left to view its metagame data.</h3>
          </div>
        ) : (
          <>
            <h2 style={{ color: '#1a237e', marginBottom: '5px' }}>{selectedTournament.name}</h2>
            <p style={{ color: '#666', marginBottom: '20px' }}>Players: {selectedTournament.players} | Format: {selectedTournament.format?.name || selectedTournament.format}</p>
            
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ backgroundColor: '#f0f2f5', borderBottom: '2px solid #ccc' }}>
                  <th style={{ padding: '12px', width: '60px' }}>Rank</th>
                  <th style={{ padding: '12px' }}>Pokémon</th>
                  <th style={{ padding: '12px' }}>Usage %</th>
                </tr>
              </thead>
              <tbody>
                {metaStats.length === 0 ? (
                  <tr><td colSpan="3" style={{ padding: '20px', textAlign: 'center' }}>Loading stats...</td></tr>
                ) : (
                  metaStats.slice(0, 50).map((stat, index) => (
                    <tr key={stat.id} style={{ borderBottom: '1px solid #eee' }}>
                      <td style={{ padding: '12px', color: '#666', fontWeight: 'bold' }}>#{index + 1}</td>
                      
                      {/* Clean text-only rendering without sprites */}
                      <td style={{ padding: '12px', fontWeight: '500' }}>
                        {stat.species.name}
                      </td>

                      <td style={{ padding: '12px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                          <span style={{ width: '50px' }}>{stat.usage_share_pct.toFixed(2)}%</span>
                          <div style={{ flexGrow: 1, backgroundColor: '#e0e0e0', height: '8px', borderRadius: '4px' }}>
                            <div style={{ 
                              width: `${stat.usage_share_pct}%`, 
                              backgroundColor: '#ffb300', 
                              height: '100%', 
                              borderRadius: '4px' 
                            }}></div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </>
        )}
      </div>
    </div>
  );
}