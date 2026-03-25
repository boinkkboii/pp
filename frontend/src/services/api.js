// src/services/api.js

// 1. Define the base URL once. 
// When you deploy to production later, you only have to change this one line!
const BASE_URL = 'http://localhost:8000/api';

// 2. A centralized fetcher that handles JSON parsing and error throwing automatically
async function fetchWithConfig(endpoint, options = {}) {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    // If the backend throws a 404, 422, or 500, this catches it globally
    throw new Error(`API Request Failed: ${response.statusText}`);
  }
  
  return response.json();
}

// 3. Export all your specific backend routes as clean, simple functions
export const api = {
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
    
    // Check for our new time filter
    if (filters.time) params.append('time_frame', filters.time); 
    
    const queryString = params.toString();
    const endpoint = queryString ? `/tournaments/?${queryString}` : '/tournaments/';
    
    return fetchWithConfig(endpoint);
  },
  
  getTournamentInfo: (id) => 
    fetchWithConfig(`/tournaments/${id}`),
    
  getTournamentMeta: (id) => 
    fetchWithConfig(`/tournaments/${id}/meta`),

  // --- Synergy ---
  getBestTeammates: (pokemonName) => 
    fetchWithConfig(`/synergy/${pokemonName}/teammates`),
  
  // --- Formats ---
  getAllFormats: () =>
    fetchWithConfig('/formats/'),

  // --- Meta & Synergy ---
  getLatestMeta: () => {
    return fetchWithConfig('/meta/latest');
  },
};