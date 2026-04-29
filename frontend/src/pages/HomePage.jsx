// src/pages/HomePage.jsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import homePageVideo from '../assets/homepage_video.gif';

export default function HomePage() {
  const navigate = useNavigate();
  const [recentTournaments, setRecentTournaments] = useState([]);
  const [topPokemon, setTopPokemon] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHomeData = async () => {
      setLoading(true);
      try {
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
    <div className="container">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingTop: '20px', paddingBottom: '20px' }}>
        
        <div className="hero-section">
          <img 
            src={homePageVideo} 
            alt="Hero Background"
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              objectFit: 'contain',
              zIndex: 0
            }}
          />

          <div className="hero-pattern" style={{ zIndex: 1 }}></div>
          
          {/* Dark Overlay for legibility */}
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            background: 'linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.6))',
            zIndex: 1
          }}></div>

          <h1 style={{ 
            margin: 0, 
            fontSize: '2.5rem', 
            zIndex: 2,
            textShadow: '0 2px 10px rgba(0,0,0,0.5)' 
          }}>
            VGC ANALYTICS
          </h1>
          <p style={{ 
            opacity: 0.9, 
            marginTop: '10px', 
            fontSize: '1.2rem', 
            zIndex: 2,
            textShadow: '0 1px 5px rgba(0,0,0,0.5)'
          }}>
            Master the Meta with AI-Powered Insights
          </p>
          <div style={{ marginTop: '20px', display: 'flex', gap: '12px', zIndex: 2 }}>
            <button className="btn-primary" onClick={() => navigate('/coach')}>Start Coaching</button>
            <button className="btn-primary" style={{ backgroundColor: 'rgba(255,255,255,0.2)', backdropFilter: 'blur(4px)' }} onClick={() => navigate('/team')}>Build a Team</button>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
          
          <div className="card" style={{ flex: '2 1 400px' }}>
            <h2 className="card-title">Top Pokémon (Current Meta)</h2>
            
            <div className="grid-cols" style={{ marginTop: '20px' }}>
              {loading ? (
                <p>Loading Pokémon data...</p>
              ) : topPokemon.length === 0 ? (
                <p>No meta data available.</p>
              ) : (
                topPokemon.map((pkmn, index) => (
                  <div key={pkmn.id} className="card" style={{ display: 'flex', alignItems: 'center', padding: '12px', background: 'var(--bg-color)', border: 'none' }}>
                    <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: 'var(--primary-color)', width: '25px' }}>
                      {index + 1}
                    </div>
                    
                    <div style={{ width: '50px', height: '50px', marginRight: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <img 
                        src={`https://r2.limitlesstcg.net/sprites/home-sv/${pkmn.species.limitless_id}.png`} 
                        alt={pkmn.species.name}
                        style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }}
                        onError={(e) => { e.target.src = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png'; }}
                      />
                    </div>
                    
                    <div>
                      <div style={{ fontWeight: 'bold', fontSize: '1rem' }}>{pkmn.species.name}</div>
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                        <span className="stat-value">{pkmn.usage_share_pct.toFixed(1)}%</span> Usage
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="card" style={{ flex: '1 1 300px', display: 'flex', flexDirection: 'column' }}>
            <h2 className="card-title">Recent Tournaments</h2>
            
            <div style={{ flexGrow: 1, marginTop: '10px' }}>
              {loading ? (
                <p style={{ textAlign: 'center' }}>Loading events...</p>
              ) : recentTournaments.length === 0 ? (
                <p style={{ textAlign: 'center' }}>No recent tournaments found.</p>
              ) : (
                <ul className="list-unstyled">
                  {recentTournaments.map((t) => (
                    <li key={t.id} className="list-item">
                      <div style={{ fontWeight: 'bold', fontSize: '1rem', marginBottom: '4px' }}>
                        {t.name}
                      </div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', justifyContent: 'space-between' }}>
                        <span>{new Date(t.date).toLocaleDateString()}</span>
                        <span>{t.players_count} Players</span>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            
            <button className="btn-primary" onClick={() => navigate('/meta')} style={{ marginTop: '20px', width: '100%' }}>
                Browse All Tournaments
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}
