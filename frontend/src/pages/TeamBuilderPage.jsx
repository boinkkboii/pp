import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import '../App.css';

export const NATURES = {
  "Adamant": { plus: "atk", minus: "spa" },
  "Bashful": { plus: null, minus: null },
  "Bold": { plus: "def", minus: "atk" },
  "Brave": { plus: "atk", minus: "spe" },
  "Calm": { plus: "spd", minus: "atk" },
  "Careful": { plus: "spd", minus: "spa" },
  "Docile": { plus: null, minus: null },
  "Gentle": { plus: "spd", minus: "def" },
  "Hardy": { plus: null, minus: null },
  "Hasty": { plus: "spe", minus: "def" },
  "Impish": { plus: "def", minus: "spa" },
  "Jolly": { plus: "spe", minus: "spa" },
  "Lax": { plus: "def", minus: "spd" },
  "Lonely": { plus: "atk", minus: "def" },
  "Mild": { plus: "spa", minus: "def" },
  "Modest": { plus: "spa", minus: "atk" },
  "Naive": { plus: "spe", minus: "spd" },
  "Naughty": { plus: "atk", minus: "spd" },
  "Quiet": { plus: "spa", minus: "spe" },
  "Quirky": { plus: null, minus: null },
  "Rash": { plus: "spa", minus: "spd" },
  "Relaxed": { plus: "def", minus: "spe" },
  "Sassy": { plus: "spd", minus: "spe" },
  "Serious": { plus: null, minus: null },
  "Timid": { plus: "spe", minus: "atk" }
};

export const calculateStat = (statName, base, ev, iv = 31, level = 50, nature = "Serious") => {
  if (statName === 'hp') {
    if (base === 1) return 1; // Shedinja
    return Math.floor(((2 * base + iv + Math.floor(ev / 4)) * level) / 100) + level + 10;
  }
  
  let val = Math.floor(((2 * base + iv + Math.floor(ev / 4)) * level) / 100) + 5;
  
  const natureMod = NATURES[nature];
  if (natureMod.plus === statName) val = Math.floor(val * 1.1);
  if (natureMod.minus === statName) val = Math.floor(val * 0.9);
  
  return val;
};

// Initial template for an empty team (Anonymous use)
const createEmptyTeam = (name = "Untitled Team") => ({
  id: Math.random(), // Temporary local ID
  name: name,
  pokemons: Array.from({ length: 6 }, (_, i) => ({
    id: Math.random(),
    species_id: null,
    species: null,
    item_id: null,
    item: null,
    ability_id: null,
    ability: null,
    level: 50,
    nature: 'Serious',
    ev_hp: 0, ev_atk: 0, ev_def: 0, ev_spa: 0, ev_spd: 0, ev_spe: 0,
    iv_hp: 31, iv_atk: 31, iv_def: 31, iv_spa: 31, iv_spd: 31, iv_spe: 31,
    moves: Array.from({ length: 4 }, (_, j) => ({ slot: j + 1, move: null, move_id: null }))
  }))
});

const TeamBuilderPage = () => {
  const { user } = useAuth();
  const [view, setView] = useState('list'); // 'list', 'editor'
  const [teams, setTeams] = useState([]);
  const [currentTeam, setCurrentTeam] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeSlot, setActiveSlot] = useState(0); 
  const [pickerMode, setPickerMode] = useState(null); 
  const [pickerTarget, setPickerTarget] = useState(null); 
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [pickerLoading, setPickerLoading] = useState(false);
  const [availableAbilities, setAvailableAbilities] = useState([]);
  const [teamToDelete, setTeamToDelete] = useState(null);

  const fetchTeams = useCallback(async () => {
    if (!user) {
      setTeams([]);
      return;
    }
    setLoading(true);
    try {
      const data = await api.getUserTeams();
      setTeams(data);
    } catch (error) {
      console.error("Failed to fetch teams:", error);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchTeams();
  }, [fetchTeams]);

  useEffect(() => {
    const fetchAbilities = async () => {
      if (view === 'editor' && currentTeam?.pokemons?.[activeSlot]) {
        const pokemon = currentTeam.pokemons[activeSlot];
        if (pokemon.species_id) {
          try {
            const data = await api.getSpeciesAbilities(pokemon.species_id);
            setAvailableAbilities(data);
          } catch (error) {
            console.error("Failed to fetch species abilities:", error);
            setAvailableAbilities([]);
          }
        } else {
          setAvailableAbilities([]);
        }
      }
    };
    fetchAbilities();
  }, [view, activeSlot, currentTeam]);

  const createTeam = async () => {
    if (!user) {
      const newTeam = createEmptyTeam("New Team");
      setTeams([newTeam, ...teams]);
      setCurrentTeam(newTeam);
      setView('editor');
      setActiveSlot(0);
      return;
    }

    try {
      const newTeam = await api.createUserTeam({ name: "New Team" });
      setTeams([newTeam, ...teams]);
      openEditor(newTeam);
    } catch (error) {
      console.error("Failed to create team:", error);
    }
  };

  const deleteTeam = async (id, e) => {
    e.stopPropagation();
    const team = teams.find(t => t.id === id);
    setTeamToDelete(team);
  };

  const confirmDelete = async () => {
    if (!teamToDelete) return;

    if (!user) {
      setTeams(teams.filter(t => t.id !== teamToDelete.id));
      setTeamToDelete(null);
      if (currentTeam?.id === teamToDelete.id) {
        setView('list');
        setCurrentTeam(null);
      }
      return;
    }

    try {
      await api.deleteUserTeam(teamToDelete.id);
      setTeams(teams.filter(t => t.id !== teamToDelete.id));
      setTeamToDelete(null);
      if (currentTeam?.id === teamToDelete.id) {
        setView('list');
        setCurrentTeam(null);
      }
    } catch (error) {
      console.error("Failed to delete team:", error);
    }
  };

  const openEditor = async (team) => {
    if (!user) {
      setCurrentTeam(team);
      setView('editor');
      setActiveSlot(0);
      return;
    }

    setLoading(true);
    try {
      const fullTeam = await api.getUserTeam(team.id);
      setCurrentTeam(fullTeam);
      setView('editor');
      setActiveSlot(0);
    } catch (error) {
      console.error("Failed to fetch team details:", error);
    } finally {
      setLoading(false);
    }
  };

  // Picker search
  useEffect(() => {
    if (!pickerMode || searchQuery.length < 2) {
      setSearchResults([]);
      return;
    }
    const delayDebounceFn = setTimeout(async () => {
      setPickerLoading(true);
      try {
        let results = [];
        if (pickerMode === 'pokemon') results = await api.searchPokemon(searchQuery);
        else if (pickerMode === 'item') results = await api.searchItems(searchQuery);
        else if (pickerMode === 'move') results = await api.searchMoves(searchQuery);
        setSearchResults(results);
      } catch (error) { console.error(error); } 
      finally { setPickerLoading(false); }
    }, 300);
    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery, pickerMode]);

  const handlePickerSelect = async (item) => {
    const slotIndex = typeof pickerTarget === 'number' ? pickerTarget : pickerTarget.slot;
    const pokemon = currentTeam.pokemons[slotIndex];

    if (!user) {
      // Local updates only
      const newPokes = [...currentTeam.pokemons];
      if (pickerMode === 'pokemon') {
        newPokes[slotIndex] = { ...newPokes[slotIndex], species_id: item.id, species: item };
      } else if (pickerMode === 'item') {
        newPokes[slotIndex] = { ...newPokes[slotIndex], item_id: item.id, item: item };
      } else if (pickerMode === 'move') {
        const moveSlot = pickerTarget.moveIndex + 1;
        const newMoves = [...newPokes[slotIndex].moves];
        const mIdx = newMoves.findIndex(m => m.slot === moveSlot);
        if (mIdx !== -1) newMoves[mIdx] = { ...newMoves[mIdx], move: item, move_id: item.id };
        else newMoves.push({ slot: moveSlot, move: item, move_id: item.id });
        newPokes[slotIndex] = { ...newPokes[slotIndex], moves: newMoves };
      }
      const updatedTeam = { ...currentTeam, pokemons: newPokes };
      setCurrentTeam(updatedTeam);
      setTeams(teams.map(t => t.id === currentTeam.id ? updatedTeam : t));
      closePicker();
      return;
    }

    try {
      if (pickerMode === 'pokemon') {
        const updated = await api.updateUserTeamPokemon(pokemon.id, { species_id: item.id });
        const newPokes = [...currentTeam.pokemons];
        newPokes[slotIndex] = { ...newPokes[slotIndex], ...updated, species: item };
        setCurrentTeam({ ...currentTeam, pokemons: newPokes });
      } 
      else if (pickerMode === 'item') {
        const updated = await api.updateUserTeamPokemon(pokemon.id, { item_id: item.id });
        const newPokes = [...currentTeam.pokemons];
        newPokes[slotIndex] = { ...newPokes[slotIndex], ...updated, item: item };
        setCurrentTeam({ ...currentTeam, pokemons: newPokes });
      }
      else if (pickerMode === 'move') {
        const moveSlot = pickerTarget.moveIndex + 1;
        await api.updateUserTeamPokemonMove(pokemon.id, moveSlot, item.id);
        const newPokes = [...currentTeam.pokemons];
        const newMoves = [...newPokes[slotIndex].moves];
        const mIdx = newMoves.findIndex(m => m.slot === moveSlot);
        if (mIdx !== -1) newMoves[mIdx] = { ...newMoves[mIdx], move: item, move_id: item.id };
        else newMoves.push({ slot: moveSlot, move: item, move_id: item.id });
        newPokes[slotIndex] = { ...newPokes[slotIndex], moves: newMoves };
        setCurrentTeam({ ...currentTeam, pokemons: newPokes });
      }
      closePicker();
    } catch (error) { console.error(error); }
  };

  const closePicker = () => {
    setPickerMode(null); setPickerTarget(null); setSearchQuery(''); setSearchResults([]);
  };

  const handleAbilityChange = async (e) => {
    const abilityId = parseInt(e.target.value) || null;
    const pokemon = currentTeam.pokemons[activeSlot];
    const ability = availableAbilities.find(a => a.id === abilityId);

    if (!user) {
      const newPokes = [...currentTeam.pokemons];
      newPokes[activeSlot] = { ...newPokes[activeSlot], ability_id: abilityId, ability };
      const updatedTeam = { ...currentTeam, pokemons: newPokes };
      setCurrentTeam(updatedTeam);
      setTeams(teams.map(t => t.id === currentTeam.id ? updatedTeam : t));
      return;
    }

    try {
      const updated = await api.updateUserTeamPokemon(pokemon.id, { ability_id: abilityId });
      const newPokes = [...currentTeam.pokemons];
      newPokes[activeSlot] = { ...newPokes[activeSlot], ...updated, ability };
      setCurrentTeam({ ...currentTeam, pokemons: newPokes });
    } catch (error) { console.error(error); }
  };

  const handleNatureChange = async (e) => {
    const nature = e.target.value;
    const pokemon = currentTeam.pokemons[activeSlot];

    if (!user) {
      const newPokes = [...currentTeam.pokemons];
      newPokes[activeSlot] = { ...newPokes[activeSlot], nature };
      const updatedTeam = { ...currentTeam, pokemons: newPokes };
      setCurrentTeam(updatedTeam);
      setTeams(teams.map(t => t.id === currentTeam.id ? updatedTeam : t));
      return;
    }

    try {
      await api.updateUserTeamPokemon(pokemon.id, { nature });
      const newPokes = [...currentTeam.pokemons];
      newPokes[activeSlot] = { ...newPokes[activeSlot], nature };
      setCurrentTeam({ ...currentTeam, pokemons: newPokes });
    } catch (error) { console.error(error); }
  };

  const handleLevelChange = async (e) => {
    let level = parseInt(e.target.value) || 1;
    if (level > 100) level = 100; if (level < 1) level = 1;
    const pokemon = currentTeam.pokemons[activeSlot];

    if (!user) {
      const newPokes = [...currentTeam.pokemons];
      newPokes[activeSlot] = { ...newPokes[activeSlot], level };
      const updatedTeam = { ...currentTeam, pokemons: newPokes };
      setCurrentTeam(updatedTeam);
      setTeams(teams.map(t => t.id === currentTeam.id ? updatedTeam : t));
      return;
    }

    try {
      await api.updateUserTeamPokemon(pokemon.id, { level });
      const newPokes = [...currentTeam.pokemons];
      newPokes[activeSlot] = { ...newPokes[activeSlot], level };
      setCurrentTeam({ ...currentTeam, pokemons: newPokes });
    } catch (error) { console.error(error); }
  };

  const updateStats = async (pokemonId, slotIndex, field, value) => {
    let val = parseInt(value) || 0;
    const pokemon = currentTeam.pokemons[slotIndex];

    if (field.startsWith('ev_')) {
      if (val > 252) val = 252; if (val < 0) val = 0;
      let otherTotal = 0;
      ['hp', 'atk', 'def', 'spa', 'spd', 'spe'].forEach(s => {
        if (`ev_${s}` !== field) otherTotal += pokemon[`ev_${s}`] || 0;
      });
      if (otherTotal + val > 510) val = 510 - otherTotal;
    } else if (field.startsWith('iv_')) {
      if (val > 31) val = 31; if (val < 0) val = 0;
    }

    if (!user) {
      const newPokes = [...currentTeam.pokemons];
      newPokes[slotIndex] = { ...newPokes[slotIndex], [field]: val };
      const updatedTeam = { ...currentTeam, pokemons: newPokes };
      setCurrentTeam(updatedTeam);
      setTeams(teams.map(t => t.id === currentTeam.id ? updatedTeam : t));
      return;
    }

    try {
      await api.updateUserTeamPokemon(pokemonId, { [field]: val });
      const newPokes = [...currentTeam.pokemons];
      newPokes[slotIndex] = { ...newPokes[slotIndex], [field]: val };
      setCurrentTeam({ ...currentTeam, pokemons: newPokes });
    } catch (error) { console.error(error); }
  };

  const currentTotalEVs = useMemo(() => {
    if (!currentTeam?.pokemons?.[activeSlot]) return 0;
    const p = currentTeam.pokemons[activeSlot];
    return ['hp', 'atk', 'def', 'spa', 'spd', 'spe'].reduce((sum, s) => sum + (p[`ev_${s}`] || 0), 0);
  }, [currentTeam, activeSlot]);

  const activePokemon = currentTeam?.pokemons?.[activeSlot];

  return (
    <div className="container" style={{ 
      minHeight: 'calc(100vh - var(--header-height) - 80px)', 
      display: 'flex', 
      flexDirection: 'column',
      paddingBottom: '40px'
    }}>
      
      {!user && (
        <div style={{ 
          background: 'var(--primary-color)', color: 'white', padding: '12px', 
          borderRadius: '8px', marginBottom: '20px', textAlign: 'center', fontWeight: 'bold'
        }}>
          💡 Anonymous Mode: Teams created will be deleted on refresh. Login to save your progress!
        </div>
      )}

      {/* 1. VIEW: LIST */}
      {view === 'list' && (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
            <h1 className="card-title" style={{ border: 'none', margin: 0 }}>My Teams</h1>
            <button className="btn-primary" onClick={createTeam}>➕ New Team</button>
          </div>
          {loading ? <p>Loading teams...</p> : teams.length === 0 ? (
            <div className="placeholder-card"><p>Start your first VGC masterpiece!</p></div>
          ) : (
            <div className="grid-cols">
              {teams.map(team => (
                <div key={team.id} className="card" onClick={() => openEditor(team)} style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: '180px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                    <h3 style={{ margin: 0, fontSize: '1.1rem', fontFamily: 'var(--font-heading)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '80%' }}>
                      {team.name}
                    </h3>
                    <button 
                      onClick={(e) => deleteTeam(team.id, e)} 
                      style={{ background: 'rgba(239, 68, 68, 0.1)', border: 'none', borderRadius: '6px', padding: '4px 8px', fontSize: '1rem', cursor: 'pointer', transition: 'background 0.2s' }}
                      onMouseEnter={(e) => e.target.style.background = 'rgba(239, 68, 68, 0.2)'}
                      onMouseLeave={(e) => e.target.style.background = 'rgba(239, 68, 68, 0.1)'}
                    >
                      🗑️
                    </button>
                  </div>
                  
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(3, 1fr)', 
                    gap: '10px', 
                    background: 'var(--bg-color)', 
                    padding: '12px', 
                    borderRadius: '8px' 
                  }}>
                    {[0, 1, 2, 3, 4, 5].map((i) => {
                      const p = team.pokemons?.[i];
                      return (
                        <div key={i} style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '40px' }}>
                          {p?.species ? (
                            <img 
                              src={`https://r2.limitlesstcg.net/sprites/home-sv/${p.species.limitless_id}.png`} 
                              style={{ width: '100%', height: '100%', objectFit: 'contain' }} 
                              alt=""
                              onError={(e) => { e.target.src = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png'; }}
                            />
                          ) : (
                            <div style={{ width: '24px', height: '24px', border: '1px dashed var(--border-color)', borderRadius: '50%', opacity: 0.3 }} />
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* 2. VIEW: EDITOR */}
      {view === 'editor' && currentTeam && (
        <>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '20px' }}>
            <button className="btn-primary" style={{ background: 'var(--bg-color)', color: 'var(--text-primary)' }} onClick={() => { if(user) fetchTeams(); setView('list'); }}>← Back</button>
            <input 
              className="chat-input" 
              value={currentTeam.name} 
              onChange={(e) => {
                const updated = { ...currentTeam, name: e.target.value };
                setCurrentTeam(updated);
                setTeams(teams.map(t => t.id === currentTeam.id ? updated : t));
              }} 
              onBlur={() => {
                if (user) api.updateUserTeam(currentTeam.id, { name: currentTeam.name });
              }} 
              style={{ fontSize: '1.2rem', fontWeight: 'bold', border: 'none', background: 'transparent' }} 
            />
          </div>
          <div style={{ display: 'flex', gap: '24px', flexGrow: 1, minHeight: 0 }}>
            <div style={{ width: '200px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {currentTeam.pokemons.map((p, i) => (
                <div key={i} className={`card ${activeSlot === i ? 'active' : ''}`} onClick={() => setActiveSlot(i)} style={{ padding: '10px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '12px', background: activeSlot === i ? 'var(--secondary-color)' : 'var(--card-bg)', color: activeSlot === i ? 'white' : 'inherit' }}>
                  <div style={{ width: '40px', height: '40px' }}>{p.species ? <img src={`https://r2.limitlesstcg.net/sprites/home-sv/${p.species.limitless_id}.png`} style={{ width: '100%' }} /> : <div style={{ width: '100%', height: '100%', border: '2px dashed var(--border-color)' }} />}</div>
                  <span style={{ fontSize: '0.9rem' }}>{p.species?.name || `Slot ${i + 1}`}</span>
                </div>
              ))}
            </div>
            <div className="card" style={{ flexGrow: 1, padding: '24px', overflowY: 'auto' }}>
              {activePokemon && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '15px', alignItems: 'end' }}>
                    <div onClick={() => { setPickerMode('pokemon'); setPickerTarget(activeSlot); }} style={{ cursor: 'pointer', flex: '2 1 200px' }}>
                      <label className="text-muted">Pokémon</label>
                      <div className="chat-input">{activePokemon.species?.name || "Select Pokémon"}</div>
                    </div>
                    <div style={{ minWidth: '80px' }}><label className="text-muted">Level</label><input type="number" className="chat-input" value={activePokemon.level} onChange={handleLevelChange} min="1" max="100" /></div>
                    <div onClick={() => { setPickerMode('item'); setPickerTarget(activeSlot); }} style={{ cursor: 'pointer' }}><label className="text-muted">Item</label><div className="chat-input">{activePokemon.item?.name || "No Item"}</div></div>
                    <div><label className="text-muted">Ability</label><select className="custom-select" style={{ width: '100%', height: '45px' }} value={activePokemon.ability_id || ""} onChange={handleAbilityChange} disabled={!activePokemon.species_id}><option value="" disabled>Select Ability</option>{availableAbilities.map(a => (<option key={a.id} value={a.id}>{a.name}</option>))}</select></div>
                    <div><label className="text-muted">Nature</label><select className="custom-select" style={{ width: '100%', height: '45px' }} value={activePokemon.nature} onChange={handleNatureChange}>{Object.keys(NATURES).map(n => (<option key={n} value={n}>{n}</option>))}</select></div>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '40px' }}>
                    <div><h4 className="card-title" style={{ fontSize: '0.9rem' }}>Moves</h4><div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>{[0, 1, 2, 3].map(moveIdx => { const move = activePokemon.moves.find(m => m.slot === moveIdx + 1)?.move; return (<div key={moveIdx} className="chat-input" onClick={() => { setPickerMode('move'); setPickerTarget({ slot: activeSlot, moveIndex: moveIdx }); }} style={{ cursor: 'pointer' }}>{move?.name || `Move ${moveIdx + 1}`}</div>); })}</div></div>
                    <div><div style={{ display: 'flex', justifyContent: 'space-between' }}><h4 className="card-title" style={{ fontSize: '0.9rem' }}>Stats & EVs</h4><span className={`stat-value ${currentTotalEVs > 510 ? 'text-red' : ''}`}>EV Total: {currentTotalEVs}/510</span></div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '40px 50px 50px 1fr 60px', gap: '12px', alignItems: 'center' }}><span className="text-muted" style={{ fontSize: '0.65rem' }}>STAT</span><span className="text-muted" style={{ fontSize: '0.65rem', textAlign: 'right' }}>TOTAL</span><span className="text-muted" style={{ fontSize: '0.65rem', textAlign: 'center' }}>IV</span><span className="text-muted" style={{ fontSize: '0.65rem' }}>EV SLIDER</span><span className="text-muted" style={{ fontSize: '0.65rem', textAlign: 'center' }}>EV</span></div>
                        {['hp', 'atk', 'def', 'spa', 'spd', 'spe'].map(stat => {
                          const base = activePokemon.species?.[`base_${stat}`] || 0;
                          const ev = activePokemon[`ev_${stat}`] || 0;
                          const iv = activePokemon[`iv_${stat}`] ?? 31;
                          const finalStat = activePokemon.species ? calculateStat(stat, base, ev, iv, activePokemon.level, activePokemon.nature) : '-';
                          const natureMod = NATURES[activePokemon.nature];
                          const isPlus = natureMod.plus === stat; const isMinus = natureMod.minus === stat;
                          return (
                            <div key={stat} style={{ display: 'grid', gridTemplateColumns: '40px 50px 50px 1fr 60px', gap: '12px', alignItems: 'center' }}>
                              <span style={{ textTransform: 'uppercase', fontSize: '0.75rem', fontWeight: 'bold', color: isPlus ? 'var(--accent-color)' : isMinus ? '#ef4444' : 'inherit' }}>{stat}{isPlus ? '+' : isMinus ? '-' : ''}</span>
                              <span style={{ fontSize: '0.9rem', fontWeight: 'bold', textAlign: 'right' }}>{finalStat}</span>
                              <input type="number" className="chat-input" style={{ width: '50px', padding: '4px', textAlign: 'center', fontSize: '0.8rem' }} value={iv} min="0" max="31" onChange={(e) => updateStats(activePokemon.id, activeSlot, `iv_${stat}`, e.target.value)} />
                              <input type="range" min="0" max="252" step="4" value={ev} onChange={(e) => updateStats(activePokemon.id, activeSlot, `ev_${stat}`, e.target.value)} style={{ width: '100%', accentColor: 'var(--accent-color)' }} />
                              <input type="number" className="chat-input" style={{ width: '60px', padding: '4px 8px', textAlign: 'center', fontSize: '0.8rem' }} value={ev} onChange={(e) => updateStats(activePokemon.id, activeSlot, `ev_${stat}`, e.target.value)} />
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {/* --- POPUPS (Global) --- */}

      {pickerMode && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div className="card" style={{ width: '500px', maxHeight: '80vh', display: 'flex', flexDirection: 'column', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ margin: 0 }}>Select {pickerMode}</h3>
              <button onClick={closePicker} style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer' }}>×</button>
            </div>
            <input autoFocus className="chat-input" placeholder={`Search ${pickerMode}...`} value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} style={{ marginBottom: '16px' }} />
            <div style={{ flexGrow: 1, overflowY: 'auto' }}>
              {pickerLoading ? <p>Searching...</p> : (
                <ul className="list-unstyled">
                  {searchResults.map(item => (
                    <li key={item.id} className="list-item" onClick={() => handlePickerSelect(item)} style={{ padding: '12px', cursor: 'pointer', borderRadius: '8px' }}>
                      <div style={{ fontWeight: 'bold' }}>{item.name}</div>
                      {item.type && <span className="text-muted" style={{ fontSize: '0.8rem' }}>{item.type} {item.category}</span>}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}

      {teamToDelete && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', zIndex: 2000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div className="card" style={{ width: '400px', padding: '32px', textAlign: 'center' }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>⚠️</div>
            <h3>Delete Team?</h3>
            <p className="text-muted">Are you sure you want to delete <strong>{teamToDelete.name}</strong>?</p>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginTop: '24px' }}>
              <button className="btn-primary" style={{ background: 'var(--bg-color)', color: 'var(--text-primary)' }} onClick={() => setTeamToDelete(null)}>Cancel</button>
              <button className="btn-primary" style={{ background: '#ef4444' }} onClick={confirmDelete}>Yes, Delete</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TeamBuilderPage;
