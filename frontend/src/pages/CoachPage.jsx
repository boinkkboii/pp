// src/pages/CoachPage.jsx
import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import '../App.css'
import Dashboard from '../components/Dashboard/SynergyChart'
import { api } from '../services/api'; // <-- IMPORTING THE API SERVICE

function CoachPage() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    { role: 'ai', content: "Hello! I am your VGC Coach. What team are we building today?" }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeCommands, setActiveCommands] = useState([]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const newMessages = [...messages, { role: 'user', content: input }];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);

    try {
      // THE REFACTOR: One clean line replaces the entire fetch block!
      const data = await api.sendChatMessage(input);
      let aiText = data.response;

      const commandRegex = /\[(CHART_(?:META|SYNERGY):\s*[^\]]+)\]/g;
      const matches = [...aiText.matchAll(commandRegex)];
      
      if (matches.length > 0) {
        const commands = matches.map(match => match[1]);
        setActiveCommands(commands);
        aiText = aiText.replace(commandRegex, '').trim(); 
      }

      setMessages([...newMessages, { role: 'ai', content: aiText }]);
    } catch (error) {
      console.error(error); // Always good to log the actual error to the console!
      setMessages([...newMessages, { role: 'ai', content: "Error connecting to backend." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* LEFT PANEL: The AI Coach Chat */}
      <div className="chat-panel">
        <div className="chat-header">
          <h2>VGC AI Coach</h2>
        </div>
        
        <div className="chat-history">
          {messages.map((msg, index) => (
            <div key={index} className={`message-row ${msg.role}`}>
              <div className="message-bubble">
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message-row ai">
              <div className="message-bubble typing-indicator">
                Coach is analyzing the meta...
              </div>
            </div>
          )}
        </div>
        
        <form className="chat-input-form" onSubmit={sendMessage}>
          <input 
            type="text" 
            value={input} 
            onChange={(e) => setInput(e.target.value)} 
            placeholder="Ask about the meta, team building, or mechanics..."
          />
          <button type="submit" disabled={isLoading}>Send</button>
        </form>
      </div>

      {/* RIGHT PANEL: The Data Dashboard */}
      <div className="data-panel">
        <div className="dashboard-header">
          <h2>Data Dashboard</h2>
        </div>
        <div className="dashboard-content" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {activeCommands.length === 0 ? (
            <div className="placeholder-card">
              <p>Ask the AI about a tournament meta or a Pokémon's synergy to populate the dashboard!</p>
            </div>
          ) : (
            // Render a separate chart for every command the AI generated!
            activeCommands.map((cmd, index) => (
              <div key={index} style={{ height: '400px', backgroundColor: 'white', padding: '15px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                <Dashboard chartCommand={cmd} />
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default CoachPage