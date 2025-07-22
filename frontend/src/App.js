import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import axios from 'axios';
import TypewriterTagline from './TypewriterTagline';

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
  const [automationStatus, setAutomationStatus] = useState(null); // Track automation status
  const [isDirectAutomation, setIsDirectAutomation] = useState(false); // Track if current request is direct automation
  const [gmailAuthStatus, setGmailAuthStatus] = useState({ 
    authenticated: false, 
    loading: true, 
    credentialsConfigured: false,
    error: null,
    debugInfo: null 
  }); // Gmail authentication status
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
    // Check Gmail authentication status
    checkGmailAuthStatus();
  }, [sessionId]);

  // Handle Gmail OAuth redirect response
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const auth = urlParams.get('auth');
    const service = urlParams.get('service');
    const message = urlParams.get('message');
    
    if (auth === 'success' && service === 'gmail') {
      // Gmail authentication successful
      handleGmailAuthSuccess();
      // Clear URL parameters
      window.history.replaceState({}, document.title, '/');
    } else if (auth === 'error') {
      // Gmail authentication failed
      handleGmailAuthError(message);
      // Clear URL parameters
      window.history.replaceState({}, document.title, '/');
    }
  }, []);

  const checkGmailAuthStatus = async () => {
    try {
      const response = await axios.get(`${API}/gmail/status?session_id=${sessionId}`);
      const data = response.data;
      
      setGmailAuthStatus({ 
        authenticated: data.authenticated || false,
        loading: false,
        credentialsConfigured: data.credentials_configured || false,
        error: data.error || null,
        debugInfo: {
          success: data.success,
          requires_auth: data.requires_auth,
          scopes: data.scopes,
          service: data.service,
          session_id: data.session_id
        }
      });
      
      // Add debug information to chat if there are issues
      if (!data.success || !data.credentials_configured) {
        console.log('Gmail Auth Debug Info:', data);
        
        // Add helpful debug message to chat
        const debugMessage = {
          id: 'gmail_debug_' + Date.now(),
          response: `🔧 **Gmail Connection Debug**\n\n` +
            `📋 **Status**: ${data.success ? 'Service Running' : 'Service Error'}\n` +
            `🔑 **Credentials**: ${data.credentials_configured ? 'Configured ✅' : 'Missing ❌'}\n` +
            `🔐 **Authentication**: ${data.authenticated ? 'Connected ✅' : 'Not Connected ❌'}\n` +
            `🆔 **Session ID**: ${sessionId}\n\n` +
            (!data.credentials_configured ? 
              '⚠️ **Issue**: Gmail credentials.json file is missing from backend. This is required for OAuth2 authentication to work properly.' : 
              !data.authenticated ? 
                '💡 Click "Connect Gmail" above to authenticate with your Google account.' : 
                '✅ Everything looks good!'),
          isUser: false,
          isSystem: true,
          timestamp: new Date()
        };
        
        // Only add debug message if we don't have one already
        setTimeout(() => {
          setMessages(prev => {
            const hasDebugMessage = prev.some(msg => msg.id && msg.id.startsWith('gmail_debug_'));
            if (!hasDebugMessage) {
              return [...prev, debugMessage];
            }
            return prev;
          });
        }, 1000);
      }
      
    } catch (error) {
      console.error('Gmail auth status check failed:', error);
      setGmailAuthStatus({ 
        authenticated: false, 
        loading: false,
        credentialsConfigured: false,
        error: error.message,
        debugInfo: { error: error.response?.data || error.message }
      });
    }
  };

  const initiateGmailAuth = async () => {
    try {
      const response = await axios.get(`${API}/gmail/auth?session_id=${sessionId}`);
      if (response.data.success && response.data.auth_url) {
        // Add session ID to the auth URL state parameter
        const authUrl = new URL(response.data.auth_url);
        const currentState = authUrl.searchParams.get('state') || '';
        authUrl.searchParams.set('state', `${sessionId}_${currentState}`);
        
        // Redirect to Google OAuth2 with session-aware state
        window.location.href = authUrl.toString();
      } else {
        console.error('Failed to get Gmail auth URL:', response.data.message);
      }
    } catch (error) {
      console.error('Gmail auth initiation failed:', error);
    }
  };

  const handleGmailAuthSuccess = async () => {
    try {
      // Update auth status
      await checkGmailAuthStatus(); // Re-check the actual status
      
      // Add success message to chat
      const successMessage = {
        id: 'gmail_auth_success_' + Date.now(),
        session_id: sessionId,
        user_id: 'system',
        message: '✅ Gmail OAuth2 Flow Completed!',
        response: '🎉 **Gmail Authentication Successful!** \n\n' +
                 'Your Gmail account has been securely connected using OAuth2. I can now help you with:\n\n' +
                 '• 📧 Check your Gmail inbox\n' +
                 '• ✉️ Send emails\n' +
                 '• 📨 Read specific emails\n' +
                 '• 🔍 Search your messages\n\n' +
                 'Try saying: "*Check my Gmail inbox*" or "*Send an email to [someone]*"',
        timestamp: new Date().toISOString(),
        intent_data: null,
        needs_approval: false
      };
      
      setMessages(prev => [...prev, successMessage]);
      
      console.log('Gmail authentication successful - status updated!');
    } catch (error) {
      console.error('Error handling Gmail auth success:', error);
    }
  };

  const handleGmailAuthError = (errorMessage) => {
    try {
      // Update auth status and re-check
      checkGmailAuthStatus();
      
      // Map error codes to user-friendly messages
      let userMessage = 'Gmail authentication failed. Please try again.';
      let debugInfo = '';
      
      switch(errorMessage) {
        case 'access_denied':
          userMessage = 'Gmail authentication was cancelled. You can try connecting again anytime.';
          debugInfo = 'User denied access during OAuth2 flow.';
          break;
        case 'no_code':
          userMessage = 'Gmail authentication failed - no authorization received.';
          debugInfo = 'OAuth2 callback did not receive authorization code.';
          break;
        case 'auth_failed':
          userMessage = 'Gmail authentication failed during token exchange.';
          debugInfo = 'Token exchange with Google failed.';
          break;
        case 'server_error':
          userMessage = 'Gmail authentication failed due to a server error.';
          debugInfo = 'Backend server error during OAuth2 processing.';
          break;
        default:
          debugInfo = `Unknown error: ${errorMessage}`;
      }
      
      // Add error message to chat with debug info
      const errorMsg = {
        id: 'gmail_auth_error_' + Date.now(),
        session_id: sessionId,
        user_id: 'system', 
        message: '❌ Gmail Authentication Failed',
        response: `❌ **Gmail Authentication Error**\n\n${userMessage}\n\n` +
                 `🔧 **Debug Info**: ${debugInfo}\n` +
                 `🆔 **Session**: ${sessionId}\n\n` +
                 `💡 **Next Steps**: Check the "Connect Gmail" button above shows the correct status, or try the authentication flow again.`,
        timestamp: new Date().toISOString(),
        intent_data: null,
        needs_approval: false
      };
      
      setMessages(prev => [...prev, errorMsg]);
      
      console.error('Gmail authentication error:', errorMessage, debugInfo);
    } catch (error) {
      console.error('Error handling Gmail auth error:', error);
    }
  };

  const handleGmailCallback = async (authorizationCode) => {
    try {
      const response = await axios.post(`${API}/gmail/callback`, {
        code: authorizationCode
      });
      
      if (response.data.success) {
        // Clear URL parameters
        window.history.replaceState({}, document.title, '/');
        
        // Update auth status
        setGmailAuthStatus({ authenticated: true, loading: false });
        
        // Add success message to chat
        const successMessage = {
          id: 'gmail_auth_success_' + Date.now(),
          response: "✅ **Gmail Integration Successful!** 🎉\n\nI can now help you with:\n• 📧 Check your Gmail inbox\n• ✉️ Send emails\n• 📨 Read specific emails\n• 🔍 Search your messages\n\nTry saying: '*Check my Gmail inbox*' or '*Send an email to [someone]*'",
          isUser: false,
          isSystem: true,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, successMessage]);
      } else {
        console.error('Gmail OAuth callback failed:', response.data.message);
      }
    } catch (error) {
      console.error('Gmail callback handling failed:', error);
    }
  };

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

  const getAutomationStatusMessage = (message) => {
    const directAutomationPatterns = {
      'check.*linkedin.*notification': '🔔 Checking LinkedIn notifications...',
      'scrape.*product|product.*listing|find.*product': '🛒 Scraping product listings...',
      'job.*alert|linkedin.*job|check.*job': '💼 Checking LinkedIn job alerts...',
      'website.*update|check.*website': '🔍 Monitoring website updates...',
      'competitor.*monitor|monitor.*competitor': '📊 Analyzing competitor data...',
      'news.*article|scrape.*news|latest.*news': '📰 Gathering latest news...'
    };

    const lowerMessage = message.toLowerCase();
    for (const [pattern, status] of Object.entries(directAutomationPatterns)) {
      if (new RegExp(pattern).test(lowerMessage)) {
        return status;
      }
    }
    return null;
  };

  const isDirectAutomationMessage = (message) => {
    return getAutomationStatusMessage(message) !== null;
  };

  // Function to render beautiful email cards
  const renderEmailDisplay = (response) => {
    // Handle authentication prompts
    if (response.includes('🔐 Please connect your Gmail account')) {
      return (
        <div className="email-display-card">
          <div className="email-header">
            🔐 Gmail Connection Required
          </div>
          <div className="email-item">
            <div className="email-field">
              <span className="email-field-icon">📧</span>
              <span className="email-field-content">
                Please connect your Gmail account to let Elva AI access your inbox.
              </span>
            </div>
            <div className="email-field">
              <span className="email-field-icon">👆</span>
              <span className="email-field-content">
                Click the <strong>"Connect Gmail"</strong> button above to continue.
              </span>
            </div>
          </div>
        </div>
      );
    }

    // Check if this is an email display response
    if (!response.includes('📥') && !response.includes('have') && !response.includes('emails') && !response.includes('unread')) {
      return response;
    }

    // Handle "no unread emails" message
    if (response.includes('No unread emails') || response.includes('all caught up')) {
      return (
        <div className="email-display-card">
          <div className="email-header">
            ✅ No unread emails! Your inbox is all caught up.
          </div>
        </div>
      );
    }

    // If the response contains the special email format, parse and render it
    if (response.includes('**From:**') && response.includes('**Subject:**')) {
      const lines = response.split('\n');
      const headerLine = lines[0];
      
      // Extract count from header
      const countMatch = headerLine.match(/(\d+)\s+(?:unread\s+)?emails?/i);
      const count = countMatch ? parseInt(countMatch[1]) : 0;
      
      if (count === 0) {
        return (
          <div className="email-display-card">
            <div className="email-header">
              ✅ No unread emails! Your inbox is all caught up.
            </div>
          </div>
        );
      }

      // Parse individual email blocks
      const emailBlocks = [];
      let currentBlock = null;
      
      for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        
        if (line.match(/^\*\*\d+\.\*\*/)) {
          // Start of new email block
          if (currentBlock) {
            emailBlocks.push(currentBlock);
          }
          currentBlock = { lines: [line] };
        } else if (currentBlock && line) {
          currentBlock.lines.push(line);
        }
      }
      
      if (currentBlock) {
        emailBlocks.push(currentBlock);
      }

      return (
        <div className="email-display-card">
          <div className="email-header">
            📥 You have <span className="email-count-badge">{count}</span> unread email{count !== 1 ? 's' : ''}:
          </div>
          
          {emailBlocks.map((block, index) => {
            const lines = block.lines;
            let sender = '', subject = '', date = '', snippet = '';
            
            lines.forEach(line => {
              if (line.includes('**From:**')) {
                sender = line.replace(/.*\*\*From:\*\*\s*/, '').trim();
              } else if (line.includes('**Subject:**')) {
                subject = line.replace(/.*\*\*Subject:\*\*\s*/, '').trim();
              } else if (line.includes('**Received:**')) {
                date = line.replace(/.*\*\*Received:\*\*\s*/, '').trim();
              } else if (line.includes('**Snippet:**')) {
                snippet = line.replace(/.*\*\*Snippet:\*\*\s*"?/, '').replace(/"$/, '').trim();
              }
            });
            
            return (
              <div key={index} className="email-item">
                <div className="email-field">
                  <span className="email-field-icon">🧑</span>
                  <span className="email-field-label">From:</span>
                  <span className="email-field-content">{sender}</span>
                </div>
                
                <div className="email-field">
                  <span className="email-field-icon">📨</span>
                  <span className="email-field-label">Subject:</span>
                  <span className="email-field-content">{subject}</span>
                </div>
                
                <div className="email-field">
                  <span className="email-field-icon">🕒</span>
                  <span className="email-field-label">Received:</span>
                  <span className="email-field-content">{date}</span>
                </div>
                
                {snippet && (
                  <div className="email-field">
                    <span className="email-field-icon">✏️</span>
                    <span className="email-field-label">Snippet:</span>
                    <div className="email-field-content">
                      <div className="email-snippet">"{snippet}"</div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      );
    }

    return response;
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    // Check if user is trying to approve/reject a pending action
    const approvalKeywords = ['send it', 'approve', 'yes', 'confirm', 'execute', 'do it', 'go ahead'];
    const rejectionKeywords = ['cancel', 'no', 'reject', 'don\'t send', 'abort', 'stop'];
    const message = inputMessage.toLowerCase().trim();
    
    // If there's a pending approval and user uses approval/rejection keywords
    if (pendingApproval && (approvalKeywords.some(keyword => message.includes(keyword)) || 
                           rejectionKeywords.some(keyword => message.includes(keyword)))) {
      
      const isApproval = approvalKeywords.some(keyword => message.includes(keyword));
      
      const userMessage = {
        id: Date.now(),
        message: inputMessage,
        isUser: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, userMessage]);
      setInputMessage('');
      
      // Handle the approval/rejection directly
      await handleApproval(isApproval);
      return;
    }

    // If user says approval keywords but there's no pending approval, provide helpful message
    if (!pendingApproval && approvalKeywords.some(keyword => message.includes(keyword))) {
      const userMessage = {
        id: Date.now(),
        message: inputMessage,
        isUser: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, userMessage]);
      setInputMessage('');
      
      const helpMessage = {
        id: Date.now() + 1,
        response: "🤔 I don't see any pending actions to approve. Try asking me to do something first, like 'Send an email to John about the meeting' or 'Create a reminder for tomorrow'!",
        isUser: false,
        isSystem: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, helpMessage]);
      return;
    }

    // Check if this is a direct automation request
    const statusMessage = getAutomationStatusMessage(inputMessage);
    const isDirect = isDirectAutomationMessage(inputMessage);
    
    if (isDirect) {
      setIsDirectAutomation(true);
      setAutomationStatus(statusMessage);
    } else {
      setIsDirectAutomation(false);
      setAutomationStatus(null);
    }

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
        timestamp: new Date(data.timestamp),
        isDirectAutomation: isDirect
      };

      setMessages(prev => [...prev, aiMessage]);

      // Show approval modal immediately if needed with pre-filled data (but not for direct automation)
      if (data.needs_approval && data.intent_data && !isDirect) {
        setPendingApproval(aiMessage);
        setEditedData(data.intent_data); // Pre-fill with AI-generated data
        setEditMode(true); // Start in edit mode so user can see and modify fields
        setShowApprovalModal(true);
        
        // Add a helpful message about the modal
        const modalHelpMessage = {
          id: Date.now() + 1,
          response: "📋 I've opened the approval modal with pre-filled details. You can review and edit the information above, then click 'Approve' or just type 'Send it' to execute! Type 'Cancel' to abort.",
          isUser: false,
          isSystem: true,
          timestamp: new Date()
        };
        setTimeout(() => {
          setMessages(prev => [...prev, modalHelpMessage]);
        }, 500);
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
      setAutomationStatus(null);
      setIsDirectAutomation(false);
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
    <div className="min-h-screen chat-background text-white">
      {/* Premium Glassy Header */}
      <div className="glassy-header shadow-lg">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
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
                className="w-12 h-12 bg-gradient-to-br from-blue-500 via-purple-500 to-indigo-600 rounded-full flex items-center justify-center shadow-xl border-2 border-blue-400/20"
                style={{ display: 'none' }}
              >
                <span className="text-2xl font-bold">E</span>
              </div>
            </div>
            <div>
              <h1 className="text-2xl smooth-glow-title">
                Elva AI
              </h1>
              <TypewriterTagline 
                text="Your personal smart assistant" 
                className="text-xs font-medium"
                speed={120}
                pauseDuration={3000}
                eraseSpeed={80}
              />
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            {/* Gmail Authentication Button */}
            {!gmailAuthStatus.loading && (
              <div className="flex items-center space-x-2">
                <button
                  onClick={gmailAuthStatus.authenticated ? null : initiateGmailAuth}
                  className={`px-6 py-3 rounded-full flex items-center space-x-2 text-xs font-medium transition-all duration-300 ${
                    gmailAuthStatus.authenticated 
                      ? 'premium-gmail-connected cursor-default' 
                      : gmailAuthStatus.credentialsConfigured 
                        ? 'premium-gmail-btn hover:scale-105'
                        : 'premium-gmail-error cursor-not-allowed opacity-75'
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
                  <span className="text-sm">
                    {gmailAuthStatus.authenticated 
                      ? '✅' 
                      : gmailAuthStatus.credentialsConfigured 
                        ? '📧' 
                        : '⚠️'}
                  </span>
                  <span className="font-semibold">
                    {gmailAuthStatus.authenticated 
                      ? 'Gmail Connected' 
                      : gmailAuthStatus.credentialsConfigured 
                        ? 'Connect Gmail' 
                        : 'Gmail Setup Required'}
                  </span>
                </button>
                
                {/* Debug Status Indicator */}
                {gmailAuthStatus.debugInfo && (
                  <div className="text-xs text-gray-400 flex items-center space-x-1">
                    <span>🔧</span>
                    <span title={JSON.stringify(gmailAuthStatus.debugInfo, null, 2)}>
                      Debug
                    </span>
                  </div>
                )}
              </div>
            )}
            
            <button
              onClick={startNewChat}
              className="premium-new-chat-btn px-6 py-2.5 rounded-full flex items-center space-x-2 shadow-lg"
              title="Start New Chat"
            >
              <span className="text-xl premium-plus-icon">+</span>
              <span className="text-sm font-medium">New Chat</span>
            </button>
          </div>
        </div>
      </div>

      {/* Chat Area with Premium Container */}
      <div className="max-w-4xl mx-auto px-4 py-6 flex flex-col h-screen premium-chat-container">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-6 scrollbar-thin scrollbar-thumb-blue-500/50 scrollbar-track-transparent">
          {messages.length === 0 && (
            <div className="text-center py-16">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 via-purple-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-2xl">
                <span className="text-3xl">🤖</span>
              </div>
              <h2 className="text-2xl font-bold mb-3 smooth-glow-title">
                Welcome to Elva AI!
              </h2>
              <TypewriterTagline 
                text="Your personal smart assistant" 
                className="text-lg mb-2"
                speed={100}
                pauseDuration={2500}
                eraseSpeed={70}
              />
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
                        : msg.isDirectAutomation
                          ? 'bg-gradient-to-r from-orange-900/40 to-red-900/40 border-2 border-orange-400/40 backdrop-blur-sm shadow-lg'
                          : 'bg-black/30 border border-blue-500/20 backdrop-blur-sm shadow-lg'
                } ${msg.isWelcome ? 'border-2 border-blue-400/40 bg-gradient-to-r from-blue-900/40 to-purple-900/40' : ''}`}>
                  <div className="text-sm leading-relaxed">
                    {msg.isUser ? msg.message : renderEmailDisplay(msg.response)}
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
                    {msg.isDirectAutomation && (
                      <div className="mt-2 text-xs text-orange-300 flex items-center">
                        <span>⚡</span>
                        <span className="ml-1">Direct automation result</span>
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
              <div className="flex flex-col">
                {/* Show automation status if this is direct automation */}
                {automationStatus && isDirectAutomation && (
                  <div className="automation-status mb-3 ml-11">
                    <div className="shimmer-text">
                      {automationStatus}
                    </div>
                  </div>
                )}
                
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
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Glassy Input Area */}
        <div className="glassy-input-area rounded-2xl p-4 shadow-xl">
          <div className="flex space-x-4">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask me anything... ✨"
              className="flex-1 clean-input"
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
              Review AI-Generated Action
            </h3>
            
            <div className="mb-4 p-3 bg-green-900/20 border border-green-500/30 rounded-lg">
              <div className="text-xs text-green-300 flex items-center mb-1">
                <span className="mr-2">✨</span>
                <span>AI has pre-filled all the details below based on your request</span>
              </div>
              <div className="text-xs text-gray-400">
                Review the information, make any changes needed, then approve to execute!
              </div>
            </div>
            
            <div className="mb-6">
              <div className="text-sm text-gray-300 mb-3 font-medium">🤖 AI Summary:</div>
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