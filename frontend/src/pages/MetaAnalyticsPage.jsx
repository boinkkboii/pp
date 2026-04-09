// src/pages/MetaAnalyticsPage.jsx
import { useState, useEffect } from 'react';
import '../App.css';
import { api } from '../services/api'; 

export default function MetaAnalyticsPage() {
  const [tournaments, setTournaments] = useState([]);
  const [selectedTournament, setSelectedTournament] = useState(null);
  const [metaStats, setMetaStats] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const [activeFormat, setActiveFormat] = useState('');
  const [activeTime, setActiveTime] = useState('');
  const [availableFormats, setAvailableFormats] = useState([]);
  const [isFormatOpen, setIsFormatOpen] = useState(false);

  useEffect(() => {
    const fetchFormats = async () => {
      try {
        const data = await api.getAllFormats();
        setAvailableFormats(data);
      } catch (error) {
        console.error("Failed to fetch formats:", error);
      }
    };
    fetchFormats();
  }, []);

  useEffect(() => {
    const fetchTournaments = async () => {
      setLoading(true);
      try {
        const data = await api.getAllTournaments({ 
          format: activeFormat, 
          time: activeTime 
        });
        setTournaments(data);
      } catch (error) {
        console.error("Failed to fetch tournaments:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchTournaments();
  }, [activeFormat, activeTime]);

  useEffect(() => {
    if (selectedTournament && tournaments.length > 0 && !tournaments.find(t => t.id === selectedTournament.id)) {
      setSelectedTournament(null);
      setMetaStats([]);
    }
  }, [tournaments, selectedTournament]);

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
    <div className="analytics-container">
      
      {/* LEFT COLUMN: Tournament List */}
      <div className="tournament-sidebar">
        <h2 className="card-title">Recent Events</h2>
        
        <div className="filter-row">
          <div style={{ position: 'relative', flex: 1 }}>
            <div 
              className="custom-select"
              onClick={() => setIsFormatOpen(!isFormatOpen)}
              style={{ cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
            >
              <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {activeFormat || "All Formats"}
              </span>
              <span style={{ fontSize: '0.7rem', opacity: 0.6 }}>▼</span>
            </div>

            {isFormatOpen && (
              <ul className="card" style={{ 
                position: 'absolute', 
                top: '100%', 
                left: 0, 
                right: 0, 
                marginTop: '4px', 
                padding: 0, 
                zIndex: 10,
                maxHeight: '200px',
                overflowY: 'auto'
              }}>
                <li 
                  onClick={() => { setActiveFormat(''); setIsFormatOpen(false); }}
                  className="list-item"
                  style={{ 
                    padding: '8px 12px', 
                    cursor: 'pointer',
                    background: activeFormat === '' ? 'var(--bg-color)' : 'transparent'
                  }}
                >
                  All Formats
                </li>
                {availableFormats.map((f) => (
                  <li 
                    key={f.id} 
                    onClick={() => { setActiveFormat(f.name); setIsFormatOpen(false); }}
                    className="list-item"
                    style={{ 
                      padding: '8px 12px', 
                      cursor: 'pointer',
                      background: activeFormat === f.name ? 'var(--bg-color)' : 'transparent'
                    }}
                  >
                    {f.name}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <select 
            className="custom-select"
            value={activeTime} 
            onChange={(e) => setActiveTime(e.target.value)}
          >
            <option value="">All Time</option>
            <option value="last_week">Past Week</option>
            <option value="last_month">Past Month</option>
            <option value="last_3_months">Past 3 Months</option>
            <option value="last_year">Past Year</option>
          </select>
        </div>
        
        <div style={{ flexGrow: 1, overflowY: 'auto', paddingRight: '5px' }}>
          {loading ? (
            <p className="text-muted" style={{ textAlign: 'center', marginTop: '20px' }}>Loading database...</p>
          ) : tournaments.length === 0 ? (
            <div className="placeholder-card" style={{ padding: '20px' }}>
                <p>No results found.</p>
            </div>
          ) : (
            <ul className="list-unstyled">
              {tournaments.map((t) => (
                <li 
                  key={t.id} 
                  onClick={() => handleTournamentClick(t)}
                  className={`tournament-item ${selectedTournament?.id === t.id ? 'active' : ''}`}
                >
                  <strong style={{ display: 'block', fontSize: '0.95rem' }}>{t.name}</strong>
                  <span className="text-muted">
                    {new Date(t.date).toLocaleDateString()} • {typeof t.format === 'object' ? t.format?.name : t.format}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* RIGHT COLUMN: The Meta Breakdown */}
      <div className="tournament-content">
        {!selectedTournament ? (
          <div className="placeholder-card">
            <h3>Select a tournament to view metagame data.</h3>
          </div>
        ) : (
          <>
            <h2 className="card-title" style={{ border: 'none', marginBottom: '5px' }}>{selectedTournament.name}</h2>
            <p className="text-muted" style={{ marginBottom: '24px' }}>
              Players: {selectedTournament.players_count} | Format: {typeof selectedTournament.format === 'object' ? selectedTournament.format?.name : selectedTournament.format}
            </p>
            
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ width: '60px' }}>Rank</th>
                  <th>Pokémon</th>
                  <th style={{ width: '300px' }}>Usage %</th>
                </tr>
              </thead>
              <tbody>
                {metaStats.length === 0 ? (
                  <tr><td colSpan="3" style={{ padding: '40px', textAlign: 'center' }} className="text-muted">Loading stats...</td></tr>
                ) : (
                  metaStats.slice(0, 50).map((stat, index) => (
                    <tr key={stat.id}>
                      <td style={{ fontWeight: 'bold' }}>#{index + 1}</td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <img 
                            src={`https://r2.limitlesstcg.net/sprites/home-sv/${stat.species.limitless_id}.png`} 
                            alt={stat.species.name}
                            style={{ width: '40px', height: '40px', objectFit: 'contain' }}
                            onError={(e) => { e.target.src = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png'; }}
                          />
                          <span style={{ fontWeight: '600' }}>{stat.species.name}</span>
                        </div>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <span className="stat-value" style={{ width: '55px' }}>{stat.usage_share_pct.toFixed(1)}%</span>
                          <div className="progress-bar">
                            <div 
                              className="progress-fill"
                              style={{ width: `${stat.usage_share_pct}%` }}
                            ></div>
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
