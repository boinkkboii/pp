// src/services/api.js

const BASE_URL = 'http://localhost:8000/api';

async function fetchWithConfig(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json',
    'X-API-KEY': import.meta.env.VITE_VGC_API_KEY,
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API Request Failed: ${response.statusText}`);
  }
  
  return response.json();
}

export const api = {
  // --- Auth ---
  register: (username, password) => 
    fetchWithConfig('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    }),
  login: (username, password) => 
    fetchWithConfig('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    }),
  getProfile: () => fetchWithConfig('/auth/profile'),
  changePassword: (oldPassword, newPassword) => 
    fetchWithConfig('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword })
    }),

  // --- Chat ---
  sendChatMessage: (message) => 
    fetchWithConfig('/chat', {
      method: 'POST',
      body: JSON.stringify({ message })
    }),

  // --- Tournaments ---
  getAllTournaments: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.format) params.append('format', filters.format);
    if (filters.time) params.append('time_frame', filters.time); 
    const queryString = params.toString();
    const endpoint = queryString ? `/tournaments/?${queryString}` : '/tournaments/';
    return fetchWithConfig(endpoint);
  },
  getTournamentInfo: (id) => fetchWithConfig(`/tournaments/${id}`),
  getTournamentMeta: (id) => fetchWithConfig(`/tournaments/${id}/meta`),
  getAllFormats: () => fetchWithConfig('/formats/'),
  getLatestMeta: () => fetchWithConfig('/meta/latest'),

  // --- Teambuilder ---
  searchPokemon: (q) => fetchWithConfig(`/teambuilder/search/pokemon?q=${q}`),
  searchMoves: (q) => fetchWithConfig(`/teambuilder/search/moves?q=${q}`),
  searchItems: (q) => fetchWithConfig(`/teambuilder/search/items?q=${q}`),
  searchAbilities: (q) => fetchWithConfig(`/teambuilder/search/abilities?q=${q}`),
  getSpeciesAbilities: (speciesId) => fetchWithConfig(`/teambuilder/species/${speciesId}/abilities`),
  
  getUserTeams: () => fetchWithConfig('/teambuilder/teams'),
  getUserTeam: (id) => fetchWithConfig(`/teambuilder/teams/${id}`),
  createUserTeam: (data) => fetchWithConfig('/teambuilder/teams', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  updateUserTeam: (id, data) => fetchWithConfig(`/teambuilder/teams/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data)
  }),
  deleteUserTeam: (id) => fetchWithConfig(`/teambuilder/teams/${id}`, {
    method: 'DELETE'
  }),
  
  updateUserTeamPokemon: (pokemonId, updates) => fetchWithConfig(`/teambuilder/pokemon/${pokemonId}`, {
    method: 'PUT',
    body: JSON.stringify(updates)
  }),
  updateUserTeamPokemonMove: (pokemonId, slot, moveId) => fetchWithConfig(`/teambuilder/pokemon/${pokemonId}/moves/${slot}`, {
    method: 'PUT',
    body: JSON.stringify({ move_id: moveId })
  }),
};
