// src/pages/MetaAnalyticsPage.jsx
import { useState, useEffect } from 'react';
import '../App.css';
import { api } from '../services/api'; 

export default function MetaAnalyticsPage() {
  const [tournaments, setTournaments] = useState([]);
  const [selectedTournament, setSelectedTournament] = useState(null);
  const [metaStats, setMetaStats] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // State to hold the active filters
  const [activeFormat, setActiveFormat] = useState('');
  const [activeTime, setActiveTime] = useState('');

  // State to hold the dynamic formats from the database
  const [availableFormats, setAvailableFormats] = useState([]);
  
  // NEW: State to control the custom format dropdown
  const [isFormatOpen, setIsFormatOpen] = useState(false);

  // Fetch available formats once on mount
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

// 1. Fetch tournaments ONLY when the page loads OR a filter changes!
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
  }, [activeFormat, activeTime]); // <-- selectedTournament REMOVED from here!

  // 1.5 Clear the right-side dashboard ONLY if the current list changes and hides your selection
  useEffect(() => {
    if (selectedTournament && tournaments.length > 0 && !tournaments.find(t => t.id === selectedTournament.id)) {
      setSelectedTournament(null);
      setMetaStats([]);
    }
  }, [tournaments, selectedTournament]);

  // Fetch specific meta stats using the centralized API
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
    <div className="analytics-container" style={{ display: 'flex', height: 'calc(100vh - 70px)', overflow: 'hidden', padding: '20px', gap: '20px', boxSizing: 'border-box' }}>
      
      {/* LEFT COLUMN: Tournament List */}
      <div className="tournament-list" style={{ width: '30%', backgroundColor: 'white', borderRadius: '8px', padding: '15px', overflowY: 'auto', height: '100%', boxShadow: '0 2px 4px rgba(0,0,0,0.05)', boxSizing: 'border-box', display: 'flex', flexDirection: 'column' }}>
        <h2 style={{ borderBottom: '2px solid #1a237e', paddingBottom: '10px', marginBottom: '15px', color: '#1a237e' }}>
          Recent Events
        </h2>
        
        {/* THE FILTER CONTROLS */}
        <div style={{ display: 'flex', gap: '10px', marginBottom: '15px', paddingBottom: '15px', borderBottom: '2px solid #f0f2f5', height: '50px' }}>
          
          {/* CUSTOM FORMAT DROPDOWN */}
          <div style={{ position: 'relative', flex: 1 }}>
            
            {/* The clickable box */}
            <div 
              onClick={() => setIsFormatOpen(!isFormatOpen)}
              style={{ 
                padding: '0 12px', 
                borderRadius: '4px', 
                border: '1px solid #ccc', 
                fontSize: '0.9rem', 
                backgroundColor: 'white', 
                cursor: 'pointer', 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                height: '100%',
                boxSizing: 'border-box'
              }}
            >
              <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {activeFormat || "All Formats"}
              </span>
              <span style={{ fontSize: '0.7rem', color: '#666', marginLeft: '5px' }}>▼</span>
            </div>

            {/* The floating menu list */}
            {isFormatOpen && (
              <ul style={{ 
                position: 'absolute', 
                top: '100%', 
                left: 0, 
                right: 0, 
                backgroundColor: 'white', 
                border: '1px solid #ccc', 
                borderRadius: '4px', 
                marginTop: '4px', 
                padding: 0, 
                margin: 0,
                listStyle: 'none', 
                zIndex: 10,
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                maxHeight: '175px', // Approx 5 items height
                overflowY: 'auto' 
              }}>
                <li 
                  onClick={() => { setActiveFormat(''); setIsFormatOpen(false); }}
                  style={{ 
                    padding: '8px 12px', 
                    cursor: 'pointer', 
                    borderBottom: '1px solid #eee', 
                    fontSize: '0.9rem',
                    backgroundColor: activeFormat === '' ? '#e8eaf6' : 'white',
                    fontWeight: activeFormat === '' ? 'bold' : 'normal'
                  }}
                  onMouseEnter={(e) => { if(activeFormat !== '') e.target.style.backgroundColor = '#f0f2f5'; }}
                  onMouseLeave={(e) => { if(activeFormat !== '') e.target.style.backgroundColor = 'white'; }}
                >
                  All Formats
                </li>
                
                {availableFormats.map((f) => (
                  <li 
                    key={f.id} 
                    onClick={() => { setActiveFormat(f.name); setIsFormatOpen(false); }}
                    style={{ 
                      padding: '8px 12px', 
                      cursor: 'pointer', 
                      borderBottom: '1px solid #eee', 
                      fontSize: '0.9rem',
                      backgroundColor: activeFormat === f.name ? '#e8eaf6' : 'white',
                      fontWeight: activeFormat === f.name ? 'bold' : 'normal'
                    }}
                    onMouseEnter={(e) => { if(activeFormat !== f.name) e.target.style.backgroundColor = '#f0f2f5'; }}
                    onMouseLeave={(e) => { if(activeFormat !== f.name) e.target.style.backgroundColor = 'white'; }}
                  >
                    {f.name}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <select 
            value={activeTime} 
            onChange={(e) => setActiveTime(e.target.value)}
            style={{ flex: 1, padding: '0 12px', borderRadius: '4px', border: '1px solid #ccc', fontSize: '0.9rem', height: '100%', boxSizing: 'border-box' }}
          >
            <option value="">All Time</option>
            <option value="last_week">Past Week</option>
            <option value="last_month">Past Month</option>
            <option value="last_3_months">Past 3 Months</option>
            <option value="last_year">Past Year</option>
          </select>
        </div>
        
        {/* THE TOURNAMENT LIST OR EMPTY STATE */}
        <div style={{ flexGrow: 1, overflowY: 'auto' }}>
          {loading ? (
            <p style={{ color: '#666', textAlign: 'center', marginTop: '20px' }}>Loading database...</p>
          ) : tournaments.length === 0 ? (
            <div style={{ padding: '30px 10px', textAlign: 'center', color: '#666', backgroundColor: '#f8f9fa', borderRadius: '8px', border: '1px dashed #ccc' }}>
                <p style={{ margin: 0, fontWeight: '500' }}>No results found.</p>
                <p style={{ margin: '5px 0 0 0', fontSize: '0.85rem' }}>Try broadening your filters.</p>
            </div>
          ) : (
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
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
            <p style={{ color: '#666', marginBottom: '20px' }}>Players: {selectedTournament.players_count} | Format: {selectedTournament.format?.name || selectedTournament.format}</p>
            
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