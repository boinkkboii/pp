// src/pages/MetaAnalyticsPage.jsx
import { useState, useEffect } from 'react';
import '../App.css';

export default function MetaAnalyticsPage() {
  const [tournaments, setTournaments] = useState([]);
  const [selectedTournament, setSelectedTournament] = useState(null);
  const [metaStats, setMetaStats] = useState([]);
  const [loading, setLoading] = useState(true);

  // 1. Fetch all tournaments as soon as the page loads
  useEffect(() => {
    const fetchTournaments = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/tournaments/');
        const data = await res.json();
        setTournaments(data);
      } catch (error) {
        console.error("Failed to fetch tournaments:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchTournaments();
  }, []);

  // 2. Fetch specific meta stats when a tournament is clicked
  const handleTournamentClick = async (tournament) => {
    setSelectedTournament(tournament);
    setMetaStats([]); // Clear old stats while loading
    
    try {
      const res = await fetch(`http://localhost:8000/api/tournaments/${tournament.limitless_id}/meta`);
      const data = await res.json();
      setMetaStats(data);
    } catch (error) {
      console.error("Failed to fetch meta stats:", error);
    }
  };

  return (
    <div className="analytics-container" style={{ display: 'flex', height: '100%', padding: '20px', gap: '20px' }}>
      
      {/* LEFT COLUMN: Tournament List */}
      <div className="tournament-list" style={{ width: '30%', backgroundColor: 'white', borderRadius: '8px', padding: '15px', overflowY: 'auto', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
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
      <div className="meta-details" style={{ width: '70%', backgroundColor: 'white', borderRadius: '8px', padding: '20px', overflowY: 'auto', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
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
                  <th style={{ padding: '12px' }}>Rank</th>
                  <th style={{ padding: '12px' }}>Pokémon</th>
                  <th style={{ padding: '12px' }}>Usage %</th>
                </tr>
              </thead>
              <tbody>
                {metaStats.length === 0 ? (
                  <tr><td colSpan="3" style={{ padding: '20px', textAlign: 'center' }}>Loading stats...</td></tr>
                ) : (
                  metaStats.slice(0, 20).map((stat, index) => (
                    <tr key={stat.id} style={{ borderBottom: '1px solid #eee' }}>
                      <td style={{ padding: '12px', color: '#666', fontWeight: 'bold' }}>#{index + 1}</td>
                      <td style={{ padding: '12px', fontWeight: '500' }}>{stat.species.name}</td>
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