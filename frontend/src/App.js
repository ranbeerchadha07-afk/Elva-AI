import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import TypewriterTagline from './TypewriterTagline';
import ChatBox from './ChatBox';
import DropdownMenu from './DropdownMenu';
import GmailAuthHandler from './GmailAuthHandler';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(generateSessionId());
  const [isDarkTheme, setIsDarkTheme] = useState(() => {
    // Initialize theme from localStorage or default to dark
    const savedTheme = localStorage.getItem('elva-theme');
    return savedTheme ? savedTheme === 'dark' : true;
  }); // Theme toggle state with localStorage persistence
  const [gmailAuthStatus, setGmailAuthStatus] = useState({ 
    authenticated: false, 
    loading: true, 
    credentialsConfigured: false,
    error: null,
    debugInfo: null 
  }); // Gmail authentication status
  const [showDropPanel, setShowDropPanel] = useState(false); // Drop-left panel state

  function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  // Initialize theme on app load
  useEffect(() => {
    const savedTheme = localStorage.getItem('elva-theme');
    const isInitiallyDark = savedTheme ? savedTheme === 'dark' : true;
    
    if (isInitiallyDark) {
      document.documentElement.classList.add('dark-theme');
      document.documentElement.classList.remove('light-theme');
    } else {
      document.documentElement.classList.add('light-theme');
      document.documentElement.classList.remove('dark-theme');
    }
  }, []);

  useEffect(() => {
    loadChatHistory();
    // Add welcome message when starting a new chat
    if (messages.length === 0) {
      addWelcomeMessage();
    }
  }, [sessionId]);

  const addWelcomeMessage = () => {
    const baseMessage = "Hi Buddy 👋 Good to see you! Elva AI at your service. Ask me anything or tell me what to do!";
    const gmailMessage = gmailAuthStatus.authenticated 
      ? "\n\n🎉 **Gmail is connected!** I can now help you with:\n• 📧 Check your Gmail inbox\n• ✉️ Send emails\n• 📨 Read specific emails\n• 🔍 Search your messages"
      : "\n\n💡 **Tip:** Connect Gmail above for email assistance!";
    
    const welcomeMessage = {
      id: 'welcome_' + Date.now(),
      response: baseMessage + gmailMessage,
      isUser: false,
      isWelcome: true,
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
  };

  const loadChatHistory = async () => {
    try {
      const response = await axios.get(`${API}/history/${sessionId}`);
      const historyMessages = response.data.messages || [];
      if (historyMessages.length === 0) {
        addWelcomeMessage();
      } else {
        setMessages(historyMessages.map(msg => ({
          ...msg,
          isUser: false, // History messages are from AI
          timestamp: new Date(msg.timestamp)
        })));
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
      addWelcomeMessage();
    }
  };

  const startNewChat = () => {
    setSessionId(generateSessionId());
    setMessages([]);
    setShowDropPanel(false); // Close panel when starting new chat
  };

  // Theme toggle function with localStorage persistence
  const toggleTheme = () => {
    const newTheme = !isDarkTheme;
    setIsDarkTheme(newTheme);
    
    // Save theme preference to localStorage
    localStorage.setItem('elva-theme', newTheme ? 'dark' : 'light');
    
    // Apply theme changes to document
    if (newTheme) {
      // Dark theme
      document.documentElement.classList.remove('light-theme');
      document.documentElement.classList.add('dark-theme');
    } else {
      // Light theme
      document.documentElement.classList.remove('dark-theme');
      document.documentElement.classList.add('light-theme');
    }
  };

  // Export chat function
  const exportChat = () => {
    const chatData = messages.map(msg => `${msg.isUser ? 'User' : 'AI'}: ${msg.message || msg.response}`).join('\n\n');
    const blob = new Blob([chatData], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `elva-chat-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setShowDropPanel(false); // Close panel after export
  };

  // Initialize Gmail auth handler
  const gmailAuthHandler = GmailAuthHandler({ 
    gmailAuthStatus, 
    setGmailAuthStatus, 
    sessionId, 
    setMessages 
  });

  return (
    <div className="chat-background min-h-screen text-white flex flex-col">
      {/* Premium Glassy Header */}
      <header className="glassy-header shadow-lg flex-shrink-0">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between relative z-10">
          <div className="flex items-center space-x-4">
            <div className="logo-container">
              <img 
                src="/logo.svg" 
                alt="Elva AI Logo" 
                className="elva-logo"
                onError={(e) => {
                  // Fallback to gradient logo if image fails to load
                  e.target.style.display = 'none';
                  e.target.nextElementSibling.style.display = 'flex';
                }}
              />
              {/* Fallback gradient logo */}
              <div 
                className="w-12 h-12 bg-gradient-to-br from-blue-500 via-purple-500 to-indigo-600
                         rounded-full flex items-center justify-center text-white font-bold text-xl shadow-lg"
                style={{ display: 'none' }}
              >
                E
              </div>
            </div>
            <div>
              <h1 className="text-3xl font-bold smooth-glow-title">Elva AI</h1>
              <TypewriterTagline />
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Drop-Left Panel with 3D Buttons */}
            <DropdownMenu
              showDropPanel={showDropPanel}
              setShowDropPanel={setShowDropPanel}
              toggleTheme={toggleTheme}
              isDarkTheme={isDarkTheme}
              exportChat={exportChat}
              startNewChat={startNewChat}
            />

            {/* Gmail Button in Header */}
            <button
              onClick={gmailAuthStatus.authenticated ? null : gmailAuthHandler.initiateGmailAuth}
              className={`circular-icon-btn ${
                gmailAuthStatus.authenticated 
                  ? 'gmail-connected' 
                  : gmailAuthStatus.credentialsConfigured 
                    ? 'gmail-ready' 
                    : 'gmail-error'
              }`}
              title={
                gmailAuthStatus.authenticated 
                  ? "Gmail Connected ✅" 
                  : gmailAuthStatus.credentialsConfigured 
                    ? "Connect Gmail" 
                    : "Gmail credentials missing ❌"
              }
              disabled={gmailAuthStatus.authenticated || !gmailAuthStatus.credentialsConfigured}
            >
              <div className="connected-indicator">
                <img 
                  src="https://images.unsplash.com/photo-1706879349268-8cb3a9ae739a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzd8MHwxfHNlYXJjaHwxfHxnbWFpbCUyMGxvZ298ZW58MHx8fHwxNzUzMjQ4NTQ1fDA&ixlib=rb-4.1.0&q=85"
                  alt="Gmail"
                  className="gmail-icon"
                />
                {gmailAuthStatus.authenticated && (
                  <div className="connected-check">✓</div>
                )}
              </div>
            </button>
          </div>
        </div>
      </header>

      {/* Chat Container - Proper Flex Layout */}
      <main className="premium-chat-container">
        <ChatBox
          sessionId={sessionId}
          gmailAuthStatus={gmailAuthStatus}
          setGmailAuthStatus={setGmailAuthStatus}
          messages={messages}
          setMessages={setMessages}
        />
      </main>
    </div>
  );
}

export default App;