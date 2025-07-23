import React from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function TestGmailFlow({ sessionId, setMessages, setUserProfile }) {
  
  const simulateGmailSuccess = async () => {
    try {
      // Fetch user profile (mock data)
      const profileResponse = await axios.get(`${API}/gmail/profile?session_id=${sessionId}`);
      
      // Set user profile in app state
      if (profileResponse.data.success && setUserProfile) {
        setUserProfile(profileResponse.data.profile);
      }
      
      // Add success message to chat with profile data
      const successMessage = {
        id: 'gmail_auth_success_' + Date.now(),
        session_id: sessionId,
        user_id: 'system',
        message: 'Gmail connected successfully ✅',
        response: '', // Will be handled by special rendering
        timestamp: new Date().toISOString(),
        intent_data: null,
        needs_approval: false,
        isGmailSuccess: true, // Special flag for custom rendering
        userProfile: profileResponse.data.success ? profileResponse.data.profile : null
      };
      
      setMessages(prev => [...prev, successMessage]);
      
      console.log('Gmail authentication simulation successful!');
    } catch (error) {
      console.error('Error simulating Gmail auth success:', error);
    }
  };
  
  const addTestUserMessage = () => {
    const userMessage = {
      id: Date.now(),
      message: "Hello! This is a test message to show my avatar.",
      isUser: true,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
  };

  return (
    <div className="flex gap-2 p-2">
      <button
        onClick={simulateGmailSuccess}
        className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors"
      >
        🎭 Simulate Gmail Connection
      </button>
      <button
        onClick={addTestUserMessage}
        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
      >
        💬 Test User Message
      </button>
    </div>
  );
}

export default TestGmailFlow;