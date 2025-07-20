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
  }, [sessionId]);

  const loadChatHistory = async () => {
    try {
      const response = await axios.get(`${API}/history/${sessionId}`);
      setMessages(response.data.messages || []);
    } catch (error) {
      console.error('Error loading chat history:', error);
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

      const aiMessage = {
        id: response.data.id,
        message: inputMessage,
        response: response.data.response,
        intent_data: response.data.intent_data,
        needs_approval: response.data.needs_approval,
        isUser: false,
        timestamp: new Date(response.data.timestamp)
      };

      setMessages(prev => [...prev, aiMessage]);

      // Show approval modal if needed
      if (response.data.needs_approval) {
        setPendingApproval(aiMessage);
        setEditedData(response.data.intent_data);
        setShowApprovalModal(true);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now(),
        response: 'Sorry, I encountered an error. Please try again.',
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
      const response = await axios.post(`${API}/approve`, {
        session_id: sessionId,
        message_id: pendingApproval.id,
        approved: approved,
        edited_data: editMode ? editedData : null
      });

      const statusMessage = {
        id: Date.now(),
        response: approved ? 
          '✅ Action executed successfully!' : 
          '❌ Action cancelled',
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, statusMessage]);

    } catch (error) {
      console.error('Error handling approval:', error);
    } finally {
      setShowApprovalModal(false);
      setPendingApproval(null);
      setEditMode(false);
      setEditedData(null);
    }
  };

  const startNewChat = () => {
    setSessionId(generateSessionId());
    setMessages([]);
  };

  const renderIntentData = (intentData) => {
    if (!intentData || intentData.intent === 'general_chat') return null;

    return (
      <div className="mt-2 p-3 bg-purple-900/30 rounded-lg border border-purple-500/30">
        <div className="text-xs text-purple-300 mb-2">Detected Intent: {intentData.intent}</div>
        <pre className="text-xs text-gray-300 whitespace-pre-wrap">
          {JSON.stringify(intentData, null, 2)}
        </pre>
      </div>
    );
  };

  const renderEditForm = () => {
    if (!editedData || !editMode) return null;

    const handleFieldChange = (field, value) => {
      setEditedData(prev => ({
        ...prev,
        [field]: value
      }));
    };

    return (
      <div className="space-y-3">
        <h4 className="text-sm font-medium text-purple-300">Edit Details:</h4>
        {Object.entries(editedData).map(([key, value]) => {
          if (key === 'intent') return null;
          
          return (
            <div key={key}>
              <label className="block text-xs text-gray-300 mb-1 capitalize">
                {key.replace('_', ' ')}
              </label>
              {Array.isArray(value) ? (
                <input
                  type="text"
                  value={value.join(', ')}
                  onChange={(e) => handleFieldChange(key, e.target.value.split(', '))}
                  className="w-full px-3 py-2 bg-gray-800 border border-purple-500/30 rounded text-white text-sm"
                />
              ) : (
                <textarea
                  value={value || ''}
                  onChange={(e) => handleFieldChange(key, e.target.value)}
                  rows={key === 'body' || key === 'post_content' ? 3 : 1}
                  className="w-full px-3 py-2 bg-gray-800 border border-purple-500/30 rounded text-white text-sm resize-none"
                />
              )}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-pink-900 text-white">
      {/* Header */}
      <div className="bg-black/30 backdrop-blur-md border-b border-purple-500/30">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
              <span className="text-xl font-bold">E</span>
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                Elva AI
              </h1>
              <p className="text-xs text-gray-400">Smart Assistant</p>
            </div>
          </div>
          
          <button
            onClick={startNewChat}
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 px-4 py-2 rounded-full flex items-center space-x-2 transition-all duration-200"
          >
            <span className="text-lg">+</span>
            <span className="text-sm">New Chat</span>
          </button>
        </div>
      </div>

      {/* Chat Area */}
      <div className="max-w-4xl mx-auto px-4 py-6 flex flex-col h-screen">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-6">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🤖</span>
              </div>
              <h2 className="text-xl font-semibold mb-2">Welcome to Elva AI!</h2>
              <p className="text-gray-400">I can help you with emails, calendar events, reminders, todos, LinkedIn posts, and general conversation.</p>
            </div>
          )}

          {messages.map((msg, index) => (
            <div key={index} className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${
                msg.isUser 
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white' 
                  : 'bg-black/40 border border-purple-500/30 backdrop-blur-sm'
              }`}>
                <div className="text-sm">
                  {msg.isUser ? msg.message : msg.response}
                </div>
                {!msg.isUser && renderIntentData(msg.intent_data)}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-black/40 border border-purple-500/30 backdrop-blur-sm px-4 py-2 rounded-2xl">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-pink-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="bg-black/30 backdrop-blur-md rounded-2xl border border-purple-500/30 p-4">
          <div className="flex space-x-4">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask me anything..."
              className="flex-1 bg-transparent text-white placeholder-gray-400 focus:outline-none"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:from-gray-600 disabled:to-gray-600 px-6 py-2 rounded-full transition-all duration-200 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </div>
        </div>
      </div>

      {/* Approval Modal */}
      {showApprovalModal && pendingApproval && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 border border-purple-500/30 rounded-2xl p-6 max-w-md w-full max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4 text-purple-300">
              Review & Approve Action
            </h3>
            
            <div className="mb-4">
              <div className="text-sm text-gray-300 mb-2">AI Response:</div>
              <div className="bg-black/40 p-3 rounded-lg text-sm">
                {pendingApproval.response}
              </div>
            </div>

            <div className="mb-6">
              <div className="flex items-center justify-between mb-3">
                <div className="text-sm text-gray-300">Action Details:</div>
                <button
                  onClick={() => setEditMode(!editMode)}
                  className="text-xs text-purple-400 hover:text-purple-300"
                >
                  {editMode ? 'Cancel Edit' : 'Edit'}
                </button>
              </div>
              
              {editMode ? renderEditForm() : (
                <pre className="bg-black/40 p-3 rounded-lg text-xs text-gray-300 whitespace-pre-wrap overflow-x-auto">
                  {JSON.stringify(editedData, null, 2)}
                </pre>
              )}
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => handleApproval(false)}
                className="flex-1 bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => handleApproval(true)}
                className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 px-4 py-2 rounded-lg transition-all duration-200"
              >
                {editMode ? 'Approve with Changes' : 'Approve'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;