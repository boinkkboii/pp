// src/pages/HomePage.jsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';

export default function HomePage() {
  const navigate = useNavigate();
  const [recentTournaments, setRecentTournaments] = useState([]);
  const [topPokemon, setTopPokemon] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHomeData = async () => {
      setLoading(true);
      try {
        // Fetch tournaments AND homepage meta concurrently
        const [tournamentsData, metaData] = await Promise.all([
          api.getAllTournaments({ limit: 5 }),
          api.getLatestMeta()
        ]);
        
        setRecentTournaments(tournamentsData.slice(0, 5));
        setTopPokemon(metaData);
      } catch (error) {
        console.error("Failed to fetch homepage data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchHomeData();
  }, []);

  return (
    <div style={{ padding: '20px', overflowY: 'auto', height: 'calc(100vh - 70px)', boxSizing: 'border-box', backgroundColor: '#f0f2f5' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        
        {/* =========================================
            HERO SECTION: Video/Animation Placeholder 
            ========================================= */}
        <div style={{ 
          width: '100%', 
          aspectRatio: '16/9', 
          maxHeight: '400px', 
          backgroundColor: '#1a237e', 
          borderRadius: '12px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
          position: 'relative',
          overflow: 'hidden'
        }}>
          <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, opacity: 0.1, backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)', backgroundSize: '24px 24px' }}></div>
          <div style={{ fontSize: '3rem', marginBottom: '10px' }}>▶️</div>
          <h1 style={{ margin: 0, fontSize: '2rem', fontWeight: 'bold' }}>Animation / Video Placeholder</h1>
          <p style={{ opacity: 0.8, marginTop: '10px' }}>Your interactive visualizer or welcome video goes here.</p>
        </div>

        {/* =========================================
            TWO COLUMN DATA LAYOUT
            ========================================= */}
        <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
          
          {/* LEFT COLUMN: Top Pokemon */}
          <div style={{ flex: '2 1 400px', backgroundColor: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
            <h2 style={{ borderBottom: '2px solid #1a237e', paddingBottom: '10px', marginTop: 0, color: '#1a237e' }}>
              Top Pokémon (Current Meta)
            </h2>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '15px', marginTop: '15px' }}>
              {loading ? (
                <p style={{ color: '#666' }}>Loading Pokémon data...</p>
              ) : topPokemon.length === 0 ? (
                <p style={{ color: '#666' }}>No meta data available.</p>
              ) : (
                topPokemon.map((pkmn, index) => (
                  <div key={pkmn.id} style={{ display: 'flex', alignItems: 'center', padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '8px', border: '1px solid #eee', transition: 'transform 0.2s', cursor: 'pointer' }} onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'} onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}>
                    
                    {/* Rank Number */}
                    <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#1a237e', width: '30px' }}>
                      {index + 1}.
                    </div>
                    
                    {/* Official Limitless Sprite! */}
                    <div style={{ width: '60px', height: '60px', marginRight: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <img 
                        src={`https://r2.limitlesstcg.net/sprites/home-sv/${pkmn.species.limitless_id}.png`} 
                        alt={pkmn.species.name}
                        style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }}
                        onError={(e) => { e.target.src = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png'; }} // Fallback if image fails
                      />
                    </div>
                    
                    {/* Name and Usage */}
                    <div style={{ flexGrow: 1 }}>
                      <div style={{ fontWeight: 'bold', color: '#333', fontSize: '1.05rem' }}>{pkmn.species.name}</div>
                      <div style={{ fontSize: '0.9rem', color: '#666', marginTop: '2px' }}>
                        <span style={{ fontWeight: 'bold', color: '#1a237e' }}>{pkmn.usage_share_pct.toFixed(2)}%</span> Usage
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* RIGHT COLUMN: Recent Tournaments */}
          <div style={{ flex: '1 1 300px', backgroundColor: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)', display: 'flex', flexDirection: 'column' }}>
            <h2 style={{ borderBottom: '2px solid #1a237e', paddingBottom: '10px', marginTop: 0, color: '#1a237e' }}>
              Recent Tournaments
            </h2>
            
            <div style={{ flexGrow: 1, marginTop: '10px' }}>
              {loading ? (
                <p style={{ textAlign: 'center', color: '#666' }}>Loading events...</p>
              ) : recentTournaments.length === 0 ? (
                <p style={{ textAlign: 'center', color: '#666' }}>No recent tournaments found.</p>
              ) : (
                <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                  {recentTournaments.map((t) => (
                    <li key={t.id} style={{ padding: '15px 0', borderBottom: '1px solid #eee' }}>
                      <div style={{ fontWeight: 'bold', fontSize: '1.05rem', color: '#333', marginBottom: '4px' }}>
                        {t.name}
                      </div>
                      <div style={{ fontSize: '0.85rem', color: '#666', display: 'flex', justifyContent: 'space-between' }}>
                        <span>{new Date(t.date).toLocaleDateString()}</span>
                        <span>{t.players_count} Players</span>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            
            <button
                onClick={() => navigate('/meta')}
                style={{ padding: '10px 20px', backgroundColor: '#1a237e', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', marginTop: '15px' }}>
                Browse All Tournaments
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}