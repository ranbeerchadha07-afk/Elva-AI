import React from 'react';

const MessageInput = ({ 
  inputMessage, 
  setInputMessage, 
  sendMessage, 
  isLoading, 
  automationStatus 
}) => {
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="glassy-input-area rounded-xl p-4 mb-4 flex items-center space-x-3">
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
          onKeyPress={handleKeyPress}
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
  );
};

export default MessageInput;