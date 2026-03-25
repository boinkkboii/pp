// src/context/ChatContext.jsx
import { createContext, useState, useContext } from 'react';

// Create the memory bank
const ChatContext = createContext();

// Create the provider that wraps around your app
export const ChatProvider = ({ children }) => {
  // Move your Coach states here!
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

// Create a custom hook to easily grab this memory
export const useChat = () => useContext(ChatContext);