// src/pages/CoachPage.jsx
import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import '../App.css'
import Dashboard from '../components/Dashboard/SynergyChart'

function CoachPage() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    { role: 'ai', content: "Hello! I am your VGC Coach. What team are we building today?" }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeCommand, setActiveCommand] = useState(null); // <-- Added state for the chart

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const newMessages = [...messages, { role: 'user', content: input }];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });
      
      if (!res.ok) throw new Error("API Network Error");
      
      const data = await res.json();
      let aiText = data.response;

      // --- THE INTERCEPTOR ---
      // Catches hidden tags like [CHART_META: 7274]
      const commandRegex = /\[(CHART_(?:META|SYNERGY):\s*[^\]]+)\]/;
      const match = aiText.match(commandRegex);
      
      if (match) {
        setActiveCommand(match[1]); // Save the command for the Dashboard
        aiText = aiText.replace(commandRegex, '').trim(); // Remove the tag from the chat bubble
      }

      setMessages([...newMessages, { role: 'ai', content: aiText }]);
    } catch (error) {
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
        <div className="dashboard-content">
          {/* Render the Dashboard and pass the active command down */}
          <Dashboard chartCommand={activeCommand} />
        </div>
      </div>
    </div>
  )
}

export default CoachPage