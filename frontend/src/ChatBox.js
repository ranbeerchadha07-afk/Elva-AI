import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function ChatBox({ sessionId, gmailAuthStatus, setGmailAuthStatus, messages, setMessages, userProfile, setUserProfile }) {
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [pendingApproval, setPendingApproval] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [editedData, setEditedData] = useState(null);
  const [lastIntentData, setLastIntentData] = useState(null);
  const [currentMessageId, setCurrentMessageId] = useState(null);
  const [automationStatus, setAutomationStatus] = useState(null);
  const [isDirectAutomation, setIsDirectAutomation] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check Gmail authentication status
  useEffect(() => {
    checkGmailAuthStatus();
  }, [sessionId]);

  // Handle Gmail OAuth redirect response
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const auth = urlParams.get('auth');
    const service = urlParams.get('service');
    const message = urlParams.get('message');
    const details = urlParams.get('details');
    const returnedSessionId = urlParams.get('session_id');
    
    console.log('🔍 OAuth Redirect Params:', { auth, service, message, details, returnedSessionId, currentSessionId: sessionId });
    
    if (auth === 'success' && service === 'gmail') {
      console.log('✅ Processing Gmail auth success');
      handleGmailAuthSuccess();
      window.history.replaceState({}, document.title, '/');
    } else if (auth === 'error') {
      console.error('❌ Processing Gmail auth error:', message, details);
      handleGmailAuthError(message, details);
      window.history.replaceState({}, document.title, '/');
    }
  }, []);

  const checkGmailAuthStatus = async () => {
    try {
      console.log('🔍 Checking Gmail auth status for session:', sessionId);
      const response = await axios.get(`${API}/gmail/status?session_id=${sessionId}`);
      const data = response.data;
      
      console.log('📊 Gmail Auth Status Response:', data);
      
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
      if (!data.success || !data.credentials_configured || data.error) {
        console.log('🔧 Gmail Auth Issues Detected:', data);
        
        const debugMessage = {
          id: 'gmail_debug_' + Date.now(),
          response: `🔧 **Gmail Connection Debug**\n\n` +
            `📋 **Status**: ${data.success ? 'Service Running' : 'Service Error'}\n` +
            `🔑 **Credentials**: ${data.credentials_configured ? 'Configured ✅' : 'Missing ❌'}\n` +
            `🔐 **Authentication**: ${data.authenticated ? 'Connected ✅' : 'Not Connected ❌'}\n` +
            `🆔 **Session ID**: ${sessionId}\n` +
            (data.error ? `❌ **Error**: ${data.error}\n` : '') +
            `\n` +
            (!data.credentials_configured ? 
              '⚠️ **Issue**: Gmail credentials.json file is missing from backend. This is required for OAuth2 authentication to work properly.' : 
              !data.authenticated ? 
                '💡 Click "Connect Gmail" above to authenticate with your Google account.' : 
                '✅ Everything looks good!'),
          isUser: false,
          isSystem: true,
          timestamp: new Date()
        };
        
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
      console.error('❌ Gmail auth status check failed:', error);
      setGmailAuthStatus({ 
        authenticated: false, 
        loading: false,
        credentialsConfigured: false,
        error: error.message,
        debugInfo: { error: error.response?.data || error.message }
      });
    }
  };

  const handleGmailAuthSuccess = async () => {
    try {
      await checkGmailAuthStatus();
      
      // Fetch user profile after successful authentication
      const profileResponse = await axios.get(`${API}/gmail/profile?session_id=${sessionId}`);
      
      // Set user profile in app state
      if (profileResponse.data.success && setUserProfile) {
        setUserProfile(profileResponse.data.profile);
      }
      
      // Add styled success message with proper chat bubble formatting
      const successMessage = {
        id: 'gmail_auth_success_' + Date.now(),
        session_id: sessionId,
        user_id: 'system',
        message: 'Gmail connected successfully ✅',
        response: 'Gmail connected successfully ✅',
        timestamp: new Date().toISOString(),
        intent_data: null,
        needs_approval: false,
        isGmailSuccess: true, // Special flag for styling
        userProfile: profileResponse.data.success ? profileResponse.data.profile : null
      };
      
      setMessages(prev => [...prev, successMessage]);
      console.log('Gmail authentication successful - status updated!');
    } catch (error) {
      console.error('Error handling Gmail auth success:', error);
      
      // Still show success message even if profile fetch fails
      const successMessage = {
        id: 'gmail_auth_success_' + Date.now(),
        session_id: sessionId,
        user_id: 'system',
        message: 'Gmail connected successfully ✅',
        response: 'Gmail connected successfully ✅',
        timestamp: new Date().toISOString(),
        intent_data: null,
        needs_approval: false,
        isGmailSuccess: true // Special flag for styling
      };
      
      setMessages(prev => [...prev, successMessage]);
    }
  };

  const handleGmailAuthError = (errorMessage, details) => {
    try {
      checkGmailAuthStatus();
      
      let userMessage = 'Gmail authentication failed. Please try again.';
      let debugInfo = details || '';
      
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
          debugInfo = details || 'Token exchange with Google failed.';
          break;
        case 'server_error':
          userMessage = 'Gmail authentication failed due to a server error.';
          debugInfo = details || 'Backend server error during OAuth2 processing.';
          break;
        default:
          debugInfo = details || `Unknown error: ${errorMessage}`;
      }
      
      console.error('🚨 Gmail Auth Error Details:', { errorMessage, details, debugInfo });
      
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
      console.error('Gmail authentication error processed');
    } catch (error) {
      console.error('Error handling Gmail auth error:', error);
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

  const renderGmailSuccessMessage = (message) => {
    const profile = message?.userProfile || userProfile;
    
    return (
      <div className="premium-gmail-success-card bg-gradient-to-r from-green-900/30 to-emerald-900/30 border border-green-500/40 rounded-xl p-6 backdrop-blur-sm shadow-xl">
        <div className="flex items-center space-x-4">
          {/* Success Icon */}
          <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center shadow-lg">
            <span className="text-white text-2xl">✅</span>
          </div>
          
          {/* Success Content */}
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-green-100 mb-2">
              Gmail Connected Successfully!
            </h3>
            
            {profile && (
              <div className="flex items-center space-x-3 mb-3">
                {profile.picture && (
                  <img 
                    src={profile.picture} 
                    alt={profile.name || 'User'} 
                    className="w-10 h-10 rounded-full border-2 border-green-400/30 shadow-md"
                  />
                )}
                <div>
                  <p className="text-green-200 font-medium">
                    {profile.name || 'Unknown User'}
                  </p>
                  <p className="text-green-300 text-sm">
                    {profile.email || profile.gmail_address}
                  </p>
                </div>
              </div>
            )}
            
            <div className="text-green-300 text-sm space-y-1">
              <p>🎉 Your Gmail account is now connected to Elva AI!</p>
              <p>📧 I can now help you with email management, reading, and sending.</p>
              {profile && profile.messages_total && (
                <p>📊 Found {profile.messages_total.toLocaleString()} messages in your account.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderEmailDisplay = (response) => {
    // Handle authentication prompts
    if (response.includes('🔐 Please connect your Gmail account')) {
      return (
        <div className="email-display-card premium-gmail-card">
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
        <div className="email-display-card premium-gmail-card">
          <div className="email-header no-emails-header">
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
        <div className="email-display-card premium-gmail-card">
          <div className="email-header">
            📥 You have <span className="email-count-badge-enhanced">{count}</span> unread email{count !== 1 ? 's' : ''}
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
        setEditedData(data.intent_data);
        setEditMode(true);
        setShowApprovalModal(true);
        
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

      // Add special handling for Gmail debug commands
      if (inputMessage.toLowerCase().includes('gmail debug') || inputMessage.toLowerCase().includes('test gmail')) {
        const debugTestMessage = {
          id: Date.now() + 1,
          response: `🔧 **Gmail Integration Test**\n\n` +
                   `🔗 **Current Status**: ${gmailAuthStatus.authenticated ? 'Connected ✅' : 'Not Connected ❌'}\n` +
                   `🔑 **Credentials**: ${gmailAuthStatus.credentialsConfigured ? 'Configured ✅' : 'Missing ❌'}\n` +
                   `🆔 **Session ID**: ${sessionId}\n\n` +
                   `**🧪 Test Steps:**\n` +
                   `1. Click the "Connect Gmail" button above\n` +
                   `2. You'll be redirected to Google's OAuth page\n` +
                   `3. Grant permissions to your Google account\n` +
                   `4. You'll be redirected back here\n` +
                   `5. You should see a success message in this chat\n` +
                   `6. The button should change to "Gmail Connected ✅"\n\n` +
                   `**💡 Debug Info**: Click the "Debug Info" button next to the Gmail button for technical details.`,
          isUser: false,
          isSystem: true,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, debugTestMessage]);
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

  const renderIntentData = (intentData) => {
    if (!intentData || intentData.intent === 'general_chat') return null;
    
    const gmailReadOnlyIntents = ['check_gmail_inbox', 'check_gmail_unread', 'gmail_inbox_check'];
    if (gmailReadOnlyIntents.includes(intentData.intent)) {
      return null;
    }

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

  const renderUserAvatar = () => {
    if (userProfile && userProfile.picture) {
      return (
        <div className="flex-shrink-0 w-8 h-8 rounded-full overflow-hidden ml-3 shadow-lg border-2 border-blue-400/30 user-avatar">
          <img 
            src={userProfile.picture} 
            alt={userProfile.name || 'User'} 
            className="w-full h-full object-cover"
            onError={(e) => {
              // Fallback to initials if image fails to load
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
          <div 
            className="w-full h-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold"
            style={{ display: 'none' }}
          >
            {userProfile.name ? userProfile.name.charAt(0).toUpperCase() : 'U'}
          </div>
        </div>
      );
    } else {
      return (
        <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center ml-3 shadow-lg user-avatar">
          <span className="text-white text-sm font-bold">👤</span>
        </div>
      );
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Chat Messages - Scrollable Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-blue-500/50 scrollbar-track-transparent">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} mb-4`}>
            <div className={`max-w-3xl ${message.isUser ? 'order-2' : 'order-1'}`}>
              <div className={`message-bubble p-4 rounded-xl shadow-lg ${
                message.isUser 
                  ? 'bg-gradient-to-br from-blue-600 to-purple-600 text-white ml-auto' 
                  : message.isSystem 
                    ? 'bg-cyan-900/30 border border-cyan-500/30 text-cyan-100'
                    : message.isEdit
                      ? 'bg-green-900/30 border border-green-500/30 text-green-100'
                      : message.isWelcome
                        ? 'bg-gradient-to-br from-purple-900/40 to-blue-900/40 border border-purple-500/30 text-purple-100'
                        : message.isGmailSuccess
                          ? 'bg-transparent border-0 p-0' // Special styling for Gmail success
                          : 'bg-gray-800/40 backdrop-blur-sm border border-gray-600/30 text-white'
              }`}>
                {!message.isUser && (
                  <div className="flex items-start space-x-3">
                    {!message.isGmailSuccess && renderAIAvatar()}
                    <div className="flex-1">
                      {message.isGmailSuccess ? (
                        renderGmailSuccessMessage(message)
                      ) : (
                        <div className="whitespace-pre-wrap">
                          {message.response ? renderEmailDisplay(message.response) : message.message}
                        </div>
                      )}
                      {renderIntentData(message.intent_data)}
                      <div className="text-xs opacity-70 mt-2">
                        {message.timestamp && new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>
                  </div>
                )}

                {message.isUser && (
                  <div className="flex items-start space-x-3">
                    <div className="flex-1">
                      <div className="whitespace-pre-wrap">
                        {message.message}
                      </div>
                      <div className="text-xs opacity-70 mt-2">
                        {message.timestamp && new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>
                    {renderUserAvatar()}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {/* Loading indicator */}
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="max-w-3xl">
              <div className="message-bubble p-4 rounded-xl bg-gray-800/40 backdrop-blur-sm border border-gray-600/30">
                <div className="flex items-start space-x-3">
                  {renderAIAvatar()}
                  <div className="flex-1">
                    <div className="loading-dots">
                      <div className="loading-dot bg-blue-400"></div>
                      <div className="loading-dot bg-blue-500"></div>
                      <div className="loading-dot bg-blue-600"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input - Fixed at Bottom */}
      <div className="chat-input-container p-4">
        <div className="max-w-4xl mx-auto">
          <div className="glassy-input-area rounded-xl p-4 flex items-center space-x-3">
            {/* Show automation status if available */}
            {automationStatus && (
              <div className="automation-status">
                <span className="shimmer-text">{automationStatus}</span>
              </div>
            )}
            
            <div className="flex-1 flex items-center space-x-3">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder="Ask me anything... ✨"
                className="flex-1 clean-input"
                disabled={isLoading}
              />
              
              <button
                onClick={sendMessage}
                disabled={isLoading || !inputMessage.trim()}
                className="premium-new-chat-btn px-6 py-3 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
              >
                {isLoading ? (
                  <div className="loading-dots">
                    <div className="loading-dot bg-blue-400"></div>
                    <div className="loading-dot bg-blue-500"></div>
                    <div className="loading-dot bg-blue-600"></div>
                  </div>
                ) : (
                  'Send'
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Approval Modal */}
      {showApprovalModal && pendingApproval && (
        <AnimatePresence>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-gray-800 rounded-xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto border border-gray-600"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white flex items-center">
                  <span className="mr-2">🤖</span>
                  Action Approval Required
                </h3>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setEditMode(!editMode)}
                    className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors"
                  >
                    {editMode ? 'View' : 'Edit'}
                  </button>
                </div>
              </div>

              <div className="mb-4 p-3 bg-blue-900/20 rounded-lg border border-blue-500/30">
                <p className="text-sm text-blue-300 mb-2">
                  ⚠️ This action was generated by AI. Please review the details before approving.
                </p>
                <div className="text-sm text-gray-300">
                  <strong>Detected Intent:</strong> {pendingApproval.intent_data?.intent?.replace('_', ' ').toUpperCase()}
                </div>
              </div>

              {editMode ? (
                renderEditForm()
              ) : (
                <div className="space-y-4">
                  <h4 className="text-sm font-medium text-blue-300 flex items-center">
                    <span className="mr-2">📋</span>
                    Action Details:
                  </h4>
                  <div className="bg-gray-900/40 p-4 rounded-lg border border-gray-600/30">
                    <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono">
                      {JSON.stringify(editedData || pendingApproval.intent_data, null, 2)}
                    </pre>
                  </div>
                </div>
              )}

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => handleApproval(false)}
                  className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleApproval(true)}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  Approve
                </button>
              </div>
            </motion.div>
          </motion.div>
        </AnimatePresence>
      )}
    </div>
  );
}

export default ChatBox;