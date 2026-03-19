// src/components/Dashboard/SynergyChart.jsx
import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { api } from '../../services/api';

export default function SynergyChart({ chartCommand }) {
  const [data, setData] = useState([]);
  const [title, setTitle] = useState("Loading Database...");

  useEffect(() => {
    if (!chartCommand) return;

    const fetchData = async () => {
      const [type, value] = chartCommand.split(':').map(str => str.trim());

      try {
        if (type === 'CHART_META') {
          setTitle(`Loading Tournament Data...`); 
          
          const infoData = await api.getTournamentInfo(value);
          const tournamentName = infoData.name || `Tournament ${value}`; 

          const rawData = await api.getTournamentMeta(value);
          
          setTitle(`${tournamentName} - Top Usage`);
          setData(rawData.slice(0, 10).map(item => ({
            name: item.species.name,
            value: item.usage_share_pct
          })));
        } 
        else if (type === 'CHART_SYNERGY') {
          setTitle(`${value}'s Best Teammates`);
          
          const rawData = await api.getBestTeammates(value);
          
          setData(rawData.slice(0, 10).map(item => ({ 
            name: item.teammate,
            value: item.pairings_count
          })));
        }
      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
        setTitle("Error loading data.");
      }
    };

    fetchData();
  }, [chartCommand]);

  return (
    <div style={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column' }}>
      <h3 style={{ marginBottom: '15px', color: '#1a237e', fontSize: '1.1rem' }}>{title}</h3>
      
      <div style={{ flexGrow: 1, minHeight: 0 }}>
        <ResponsiveContainer width="100%" height="100%">
          {/* Set left margin to 120 so long names like "Urshifu Rapid Strike" fit comfortably */}
          <BarChart data={data} layout="vertical" margin={{ top: 5, right: 20, left: 120, bottom: 5 }}>
            <XAxis type="number" hide />
            
            <YAxis 
              dataKey="name" 
              type="category" 
              width={120} 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: '#4a5568', fontSize: 13, fontWeight: 500 }}
            />
            
            <Tooltip 
              cursor={{fill: '#f0f2f5'}} 
              formatter={(value) => [typeof value === 'number' && value < 100 ? `${value.toFixed(1)}%` : value, "Usage/Pairings"]}
            />
            
            <Bar dataKey="value" fill="#1a237e" radius={[0, 4, 4, 0]} barSize={22} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}