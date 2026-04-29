// src/pages/CoachPage.jsx
import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import '../App.css'
import { useChat } from '../components/Chat/ChatContext';
import Dashboard from '../components/Dashboard/SynergyChart'
import { api } from '../services/api';

function CoachPage() {
  const { messages, setMessages, input, setInput, isLoading, setIsLoading, activeCommands, setActiveCommands } = useChat();

  useEffect(() => {
    document.body.classList.add('no-scroll');
    return () => {
      document.body.classList.remove('no-scroll');
    };
  }, []);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userText = input; 
    const newMessages = [...messages, { role: 'user', content: userText }];
    setMessages(newMessages);
    
    setInput('');
    setIsLoading(true);

    try {
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
      console.error(error);
      setMessages([...newMessages, { role: 'ai', content: "Error connecting to backend." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="vgc-container">
      {/* LEFT PANEL: The AI Coach Chat */}
      <div className="chat-panel">
        <div className="panel-header">
          <h2>AI COACH</h2>
        </div>
        
        <div className="chat-history">
          {messages.length === 0 && (
            <div className="placeholder-card" style={{ border: 'none', background: 'transparent' }}>
              <p>Welcome to Pro Game Analytics. I'm your AI Coach. Ask me anything about the current VGC meta or team building!</p>
            </div>
          )}
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
                Analyzing the data...
              </div>
            </div>
          )}
        </div>
        
        <div className="chat-input-area">
          <form className="chat-form" onSubmit={sendMessage}>
            <input 
              className="chat-input"
              type="text" 
              value={input} 
              onChange={(e) => setInput(e.target.value)} 
              placeholder="Ask me your questions here"
            />
            <button className="chat-send-btn" type="submit" disabled={isLoading}>
              {isLoading ? "..." : "SEND"}
            </button>
          </form>
        </div>
      </div>

      {/* RIGHT PANEL: The Data Dashboard */}
      <div className="data-panel">
        <div className="panel-header">
          <h2>VISUAL ANALYTICS</h2>
        </div>
        
        {activeCommands.length === 0 ? (
          <div className="placeholder-card">
            <div>
              <h3>No Active Visuals</h3>
              <p>Ask about specific synergies or meta trends to see charts here.</p>
            </div>
          </div>
        ) : (
          activeCommands.map((cmd, index) => (
            <div key={index} className="dashboard-card" style={{ height: 'auto', minHeight: '400px' }}>
              <Dashboard chartCommand={cmd} />
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default CoachPage
