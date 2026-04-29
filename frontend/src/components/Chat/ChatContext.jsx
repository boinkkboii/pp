// src/context/ChatContext.jsx
import { createContext, useState, useContext } from 'react';

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const [messages, setMessages] = useState([
    { role: 'ai', content: "Hello! I am your VGC Coach. How can I help you today?" }
  ]);  
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeCommands, setActiveCommands] = useState([]);

  return (
    <ChatContext.Provider value={{ messages, setMessages, input, setInput, isLoading, setIsLoading, activeCommands, setActiveCommands }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => useContext(ChatContext);