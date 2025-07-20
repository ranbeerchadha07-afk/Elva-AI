import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sessionId, setSessionId] = useState(generateSessionId());
  const [isLoading, setIsLoading] = useState(false);
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [pendingApproval, setPendingApproval] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [editedData, setEditedData] = useState(null);
  const [lastIntentData, setLastIntentData] = useState(null); // Store parsed intent data
  const [currentMessageId, setCurrentMessageId] = useState(null); // Track current message for approval
  const messagesEndRef = useRef(null);

  function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadChatHistory();
    // Add welcome message when starting a new chat
    if (messages.length === 0) {
      addWelcomeMessage();
    }
  }, [sessionId]);

  const addWelcomeMessage = () => {
    const welcomeMessage = {
      id: 'welcome_' + Date.now(),
      response: "Hi Buddy 👋 Good to see you! Elva AI at your service. Ask me anything or tell me what to do!",
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

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      message: inputMessage,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setInputMessage('');

    try {
      const response = await axios.post(`${API}/chat`, {
        message: inputMessage,
        session_id: sessionId,
        user_id: 'default_user'
      });

      const data = response.data;

      // Store parsed intent data for modal use
      if (data.intent_data) {
        setLastIntentData(data.intent_data);
        setCurrentMessageId(data.id);
      }

      const aiMessage = {
        id: data.id,
        message: inputMessage,
        response: data.response,
        intent_data: data.intent_data,
        needs_approval: data.needs_approval,
        isUser: false,
        timestamp: new Date(data.timestamp)
      };

      setMessages(prev => [...prev, aiMessage]);

      // Show approval modal immediately if needed with pre-filled data
      if (data.needs_approval && data.intent_data) {
        setPendingApproval(aiMessage);
        setEditedData(data.intent_data); // Pre-fill with AI-generated data
        setEditMode(true); // Start in edit mode so user can see and modify fields
        setShowApprovalModal(true);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now(),
        response: 'Sorry, I encountered an error. Please try again! 🤖',
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApproval = async (approved) => {
    if (!pendingApproval) return;

    try {
      let finalData = editedData;
      
      // If user made edits, show the edited data in chat
      if (editMode && editedData) {
        const editSummary = {
          id: Date.now(),
          response: `📝 Updated details:\n${JSON.stringify(editedData, null, 2)}`,
          isUser: false,
          isEdit: true,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, editSummary]);
      }

      const response = await axios.post(`${API}/approve`, {
        session_id: sessionId,
        message_id: currentMessageId || pendingApproval.id,
        approved: approved,
        edited_data: editMode ? finalData : null
      });

      const statusMessage = {
        id: Date.now(),
        response: approved ? 
          '✅ Perfect! Action executed successfully! Your request has been sent to the automation system.' : 
          '❌ No worries! Action cancelled as requested.',
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, statusMessage]);

      // If successful and approved, show n8n response details
      if (approved && response.data.n8n_response) {
        const n8nMessage = {
          id: Date.now() + 1,
          response: `🔗 Automation Response: ${JSON.stringify(response.data.n8n_response, null, 2)}`,
          isUser: false,
          isSystem: true,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, n8nMessage]);
      }

    } catch (error) {
      console.error('Error handling approval:', error);
      const errorMessage = {
        id: Date.now(),
        response: '⚠️ Something went wrong with the approval. Please try again!',
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setShowApprovalModal(false);
      setPendingApproval(null);
      setEditMode(false);
      setEditedData(null);
      setLastIntentData(null);
      setCurrentMessageId(null);
    }
  };

  const startNewChat = () => {
    setSessionId(generateSessionId());
    setMessages([]);
  };

  const renderIntentData = (intentData) => {
    if (!intentData || intentData.intent === 'general_chat') return null;

    return (
      <div className="mt-3 p-3 bg-blue-900/20 rounded-lg border border-blue-500/30">
        <div className="text-xs text-blue-300 mb-2 font-medium">
          🎯 Detected Intent: {intentData.intent.replace('_', ' ').toUpperCase()}
        </div>
        <pre className="text-xs text-gray-300 whitespace-pre-wrap font-mono">
          {JSON.stringify(intentData, null, 2)}
        </pre>
      </div>
    );
  };

  const renderEditForm = () => {
    if (!editedData) return null;

    const handleFieldChange = (field, value) => {
      setEditedData(prev => ({
        ...prev,
        [field]: value
      }));
    };

    return (
      <div className="space-y-4">
        <h4 className="text-sm font-medium text-blue-300 flex items-center">
          <span className="mr-2">✏️</span>
          Edit Action Details:
        </h4>
        <div className="bg-blue-900/20 p-4 rounded-lg border border-blue-500/30">
          {Object.entries(editedData).map(([key, value]) => {
            if (key === 'intent') return null;
            
            return (
              <div key={key} className="mb-3 last:mb-0">
                <label className="block text-sm text-blue-200 mb-2 capitalize font-medium">
                  {key.replace(/_/g, ' ')}:
                </label>
                {Array.isArray(value) ? (
                  <input
                    type="text"
                    value={value.join(', ')}
                    onChange={(e) => handleFieldChange(key, e.target.value.split(', ').filter(v => v.trim()))}
                    className="w-full px-4 py-3 bg-gray-800 border border-blue-500/30 rounded-lg text-white text-sm focus:border-blue-400/60 focus:ring-2 focus:ring-blue-400/20 transition-all duration-200 placeholder-gray-500"
                    placeholder={`Enter ${key.replace(/_/g, ' ')}...`}
                  />
                ) : (
                  <textarea
                    value={value || ''}
                    onChange={(e) => handleFieldChange(key, e.target.value)}
                    rows={key === 'body' || key === 'post_content' ? 4 : 2}
                    className="w-full px-4 py-3 bg-gray-800 border border-blue-500/30 rounded-lg text-white text-sm resize-none focus:border-blue-400/60 focus:ring-2 focus:ring-blue-400/20 transition-all duration-200 placeholder-gray-500"
                    placeholder={`Enter ${key.replace(/_/g, ' ')}...`}
                  />
                )}
              </div>
            );
          })}
        </div>
        
        <div className="mt-4 p-3 bg-green-900/20 border border-green-500/30 rounded-lg">
          <div className="text-xs text-green-300 mb-2">✅ Current Values Preview:</div>
          <pre className="text-xs text-green-200 whitespace-pre-wrap font-mono">
            {JSON.stringify(editedData, null, 2)}
          </pre>
        </div>
      </div>
    );
  };

  const renderAIAvatar = () => {
    return (
      <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-blue-500 via-purple-500 to-indigo-600 rounded-full flex items-center justify-center mr-3 shadow-lg">
        <span className="text-white text-sm font-bold">🤖</span>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900/30 to-purple-900/40 text-white">
      {/* Header */}
      <div className="bg-black/40 backdrop-blur-xl border-b border-blue-500/20 shadow-lg">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 via-purple-500 to-indigo-600 rounded-full flex items-center justify-center shadow-xl border-2 border-blue-400/20">
              <span className="text-2xl font-bold">E</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">
                Elva AI
              </h1>
              <p className="text-xs text-gray-400 font-medium">Your personal smart assistant</p>
            </div>
          </div>
          
          <button
            onClick={startNewChat}
            className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 hover:from-blue-500 hover:via-purple-500 hover:to-indigo-500 px-6 py-2.5 rounded-full flex items-center space-x-2 transition-all duration-300 shadow-lg hover:shadow-xl border border-blue-500/20 hover:border-blue-400/40"
            title="Start New Chat"
          >
            <span className="text-xl">+</span>
            <span className="text-sm font-medium">New Chat</span>
          </button>
        </div>
      </div>

      {/* Chat Area */}
      <div className="max-w-4xl mx-auto px-4 py-6 flex flex-col h-screen">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-6 scrollbar-thin scrollbar-thumb-blue-500/50 scrollbar-track-transparent">
          {messages.length === 0 && (
            <div className="text-center py-16">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 via-purple-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-2xl">
                <span className="text-3xl">🤖</span>
              </div>
              <h2 className="text-2xl font-bold mb-3 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Welcome to Elva AI!
              </h2>
              <p className="text-gray-400 text-lg">Your personal smart assistant</p>
              <p className="text-gray-500 text-sm mt-2">I can help you with emails, calendar events, reminders, todos, LinkedIn posts, and general conversation.</p>
            </div>
          )}

          {messages.map((msg, index) => (
            <div key={index} className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'} animate-slide-in`}>
              <div className={`flex max-w-xs lg:max-w-md ${msg.isUser ? 'flex-row-reverse' : 'flex-row'}`}>
                {!msg.isUser && renderAIAvatar()}
                <div className={`px-4 py-3 rounded-2xl ${
                  msg.isUser 
                    ? 'bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 text-white shadow-lg ml-3' 
                    : msg.isEdit
                      ? 'bg-gradient-to-r from-green-900/40 to-emerald-900/40 border-2 border-green-400/40 backdrop-blur-sm shadow-lg'
                      : msg.isSystem
                        ? 'bg-gradient-to-r from-cyan-900/40 to-blue-900/40 border-2 border-cyan-400/40 backdrop-blur-sm shadow-lg'
                        : 'bg-black/30 border border-blue-500/20 backdrop-blur-sm shadow-lg'
                } ${msg.isWelcome ? 'border-2 border-blue-400/40 bg-gradient-to-r from-blue-900/40 to-purple-900/40' : ''}`}>
                  <div className="text-sm leading-relaxed">
                    {msg.isUser ? msg.message : msg.response}
                    {msg.isWelcome && (
                      <div className="mt-2 text-xs text-blue-300 flex items-center">
                        <span className="animate-pulse">✨</span>
                        <span className="ml-1">Ready to help you!</span>
                      </div>
                    )}
                    {msg.isEdit && (
                      <div className="mt-2 text-xs text-green-300 flex items-center">
                        <span>📝</span>
                        <span className="ml-1">Your customizations</span>
                      </div>
                    )}
                    {msg.isSystem && (
                      <div className="mt-2 text-xs text-cyan-300 flex items-center">
                        <span>🔗</span>
                        <span className="ml-1">System Response</span>
                      </div>
                    )}
                  </div>
                  {!msg.isUser && !msg.isEdit && !msg.isSystem && renderIntentData(msg.intent_data)}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start animate-slide-in">
              <div className="flex">
                {renderAIAvatar()}
                <div className="bg-black/30 border border-blue-500/20 backdrop-blur-sm px-4 py-3 rounded-2xl shadow-lg">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="bg-black/30 backdrop-blur-xl rounded-2xl border border-blue-500/20 p-4 shadow-xl">
          <div className="flex space-x-4">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask me anything... ✨"
              className="flex-1 bg-transparent text-white placeholder-gray-400 focus:outline-none text-lg"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 hover:from-blue-500 hover:via-purple-500 hover:to-indigo-500 disabled:from-gray-600 disabled:to-gray-700 px-8 py-3 rounded-full transition-all duration-300 disabled:cursor-not-allowed shadow-lg hover:shadow-xl border border-blue-500/20"
            >
              <span className="font-medium">Send</span>
            </button>
          </div>
        </div>
      </div>

      {/* Approval Modal */}
      {showApprovalModal && pendingApproval && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900/95 border border-blue-500/30 rounded-2xl p-6 max-w-lg w-full max-h-[85vh] overflow-y-auto shadow-2xl backdrop-blur-xl">
            <h3 className="text-xl font-bold mb-4 text-blue-300 flex items-center">
              <span className="mr-2">🔍</span>
              Review & Approve Action
            </h3>
            
            <div className="mb-6">
              <div className="text-sm text-gray-300 mb-3 font-medium">🤖 AI Response:</div>
              <div className="bg-black/40 p-4 rounded-lg text-sm border border-blue-500/20">
                {pendingApproval.response}
              </div>
            </div>

            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <div className="text-sm text-gray-300 font-medium">⚙️ Action Configuration:</div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setEditMode(!editMode)}
                    className={`text-xs px-3 py-1.5 border rounded-full transition-all duration-200 ${
                      editMode 
                        ? 'text-red-400 border-red-500/30 hover:border-red-400/50 bg-red-900/20' 
                        : 'text-blue-400 border-blue-500/30 hover:border-blue-400/50 bg-blue-900/20'
                    }`}
                  >
                    {editMode ? '👀 View Only' : '✏️ Edit Fields'}
                  </button>
                </div>
              </div>
              
              {editMode ? renderEditForm() : (
                <div className="bg-black/40 p-4 rounded-lg border border-blue-500/20">
                  <div className="text-xs text-blue-300 mb-2">📋 Detected Intent Data:</div>
                  <pre className="text-xs text-gray-300 whitespace-pre-wrap overflow-x-auto font-mono">
                    {JSON.stringify(editedData, null, 2)}
                  </pre>
                </div>
              )}
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => handleApproval(false)}
                className="flex-1 bg-gray-700 hover:bg-gray-600 px-4 py-3 rounded-lg transition-colors border border-gray-600/50 font-medium flex items-center justify-center"
              >
                <span className="mr-2">❌</span>
                Cancel
              </button>
              <button
                onClick={() => handleApproval(true)}
                className="flex-1 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 hover:from-blue-500 hover:via-purple-500 hover:to-indigo-500 px-4 py-3 rounded-lg transition-all duration-300 shadow-lg font-medium flex items-center justify-center"
              >
                <span className="mr-2">✅</span>
                {editMode ? 'Approve Changes' : 'Approve Action'}
              </button>
            </div>

            {editMode && (
              <div className="mt-4 p-3 bg-blue-900/20 border border-blue-500/30 rounded-lg">
                <div className="text-xs text-blue-300 flex items-center">
                  <span className="mr-2">💡</span>
                  Tip: Make your changes above, then click "Approve Changes" to execute with your modifications!
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;