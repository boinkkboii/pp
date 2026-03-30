// src/components/Dashboard/SynergyChart.jsx
import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { api } from '../../services/api';
import { useTheme } from '../../context/ThemeContext';

export default function SynergyChart({ chartCommand }) {
  const [data, setData] = useState([]);
  const [title, setTitle] = useState("SYNCING...");
  const { theme } = useTheme();

  useEffect(() => {
    if (!chartCommand) return;

    const fetchData = async () => {
      const parts = chartCommand.split(':');
      const type = parts[0].trim();
      const value = parts.slice(1).join(':').trim();

      try {
        if (type === 'CHART_META') {
          setTitle(`FETCHING TOURNAMENT...`); 
          const infoData = await api.getTournamentInfo(value);
          const tournamentName = infoData.name || `EVENT ${value}`; 
          const rawData = await api.getTournamentMeta(value);
          
          setTitle(`${tournamentName.toUpperCase()}`);
          setData(rawData.slice(0, 10).map(item => ({
            name: item.species.name,
            value: item.usage_share_pct
          })));
        } 
        else if (type === 'CHART_SYNERGY') {
          setTitle(`${value.toUpperCase()} SYNERGY`);
          const rawData = await api.getBestTeammates(value);
          
          setData(rawData.slice(0, 10).map(item => ({ 
            name: item.teammate,
            value: item.pairings_count
          })));
        }
      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
        setTitle("DATA ERROR");
      }
    };

    fetchData();
  }, [chartCommand]);

  const barColor = theme === 'dark' ? '#3B82F6' : '#1E40AF';
  const textColor = theme === 'dark' ? '#94A3B8' : '#475569';
  const tooltipBg = theme === 'dark' ? '#1E293B' : '#FFFFFF';
  const tooltipText = theme === 'dark' ? '#F8FAFC' : '#1E3A8A';

  return (
    <div className="chart-container" style={{ height: '300px', width: '100%', display: 'flex', flexDirection: 'column' }}>
      <h3 style={{ 
        marginBottom: '20px', 
        color: 'var(--primary-color)', 
        fontSize: '0.9rem', 
        fontWeight: '800', 
        letterSpacing: '1px',
        borderLeft: '4px solid var(--primary-color)',
        paddingLeft: '12px',
        fontFamily: 'var(--font-heading)'
      }}>
        {title}
      </h3>
      
      <div style={{ flexGrow: 1, minHeight: 0 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
            <XAxis type="number" hide />
            <YAxis 
              dataKey="name" 
              type="category" 
              width={100} 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: textColor, fontSize: 11, fontWeight: 600, fontFamily: 'var(--font-body)' }}
            />
            <Tooltip 
              cursor={{fill: theme === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'}} 
              contentStyle={{ 
                borderRadius: '8px', 
                border: '1px solid var(--border-color)', 
                boxShadow: 'var(--shadow-md)',
                backgroundColor: tooltipBg,
                color: tooltipText,
                fontFamily: 'var(--font-body)'
              }}
              itemStyle={{ color: tooltipText }}
              formatter={(value) => [typeof value === 'number' && value < 100 ? `${value.toFixed(1)}%` : value, "VALUE"]}
            />
            <Bar dataKey="value" fill={barColor} radius={[0, 4, 4, 0]} barSize={18} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
