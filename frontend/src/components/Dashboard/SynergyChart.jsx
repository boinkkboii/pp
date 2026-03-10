// src/components/Dashboard/SynergyChart.jsx
import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function SynergyChart({ chartCommand }) {
  const [data, setData] = useState([]);
  const [title, setTitle] = useState("Awaiting Coach's Analysis...");

  useEffect(() => {
    if (!chartCommand) return;

    const fetchData = async () => {
      const [type, value] = chartCommand.split(':').map(str => str.trim());

      try {
        if (type === 'CHART_META') {
          // Set a temporary loading title
          setTitle(`Loading Tournament Data...`); 
          
          // 1. Fetch the Tournament Details to get the official name!
          const infoRes = await fetch(`http://localhost:8000/api/tournaments/${value}`);
          const infoData = await infoRes.json();
          // Fallback to the ID just in case the name is missing
          const tournamentName = infoData.name || `Tournament ${value}`; 

          // 2. Fetch the Meta Usage Data for the chart
          const res = await fetch(`http://localhost:8000/api/tournaments/${value}/meta`);
          const rawData = await res.json();
          
          // 3. Set the beautiful title!
          setTitle(`${tournamentName} - Top Usage`);
          
          setData(rawData.slice(0, 10).map(item => ({
            name: item.species.name,
            value: item.usage_share_pct
          })));
        }
        else if (type === 'CHART_SYNERGY') {
          setTitle(`${value}'s Best Teammates`);
          const res = await fetch(`http://localhost:8000/api/synergy/${value}/teammates`);
          const rawData = await res.json();
          setData(rawData.map(item => ({
            name: item.teammate,
            value: item.pairings_count
          })));
        }
      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
      }
    };

    fetchData();
  }, [chartCommand]);

  if (!data.length) {
    return (
      <div className="placeholder-card">
        <p>Ask the AI about a tournament meta or a Pokémon's synergy to populate the dashboard!</p>
      </div>
    );
  }

  return (
    <div style={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column' }}>
      <h3 style={{ marginBottom: '20px', color: '#1a237e' }}>{title}</h3>
      <div style={{ flexGrow: 1, minHeight: 0 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
            <XAxis type="number" hide />
            <YAxis dataKey="name" type="category" width={100} axisLine={false} tickLine={false} />
            <Tooltip cursor={{fill: '#f0f2f5'}} />
            <Bar dataKey="value" fill="#1a237e" radius={[0, 4, 4, 0]} barSize={30} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}