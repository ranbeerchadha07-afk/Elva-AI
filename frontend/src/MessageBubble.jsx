import React from 'react';

const MessageBubble = ({ message, renderEmailDisplay, renderIntentData, renderAIAvatar, renderGmailSuccessMessage }) => {
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} mb-4`}>
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
                  : 'bg-gray-800/40 backdrop-blur-sm border border-gray-600/30 text-white'
        }`}>
          {/* AI Avatar for non-user messages */}
          {!message.isUser && (
            <div className="flex items-start space-x-3">
              {renderAIAvatar()}
              <div className="flex-1">
                {/* Special rendering for Gmail success message */}
                {message.isGmailSuccess ? (
                  renderGmailSuccessMessage()
                ) : (
                  <div className="whitespace-pre-wrap">
                    {message.response ? renderEmailDisplay(message.response) : message.message}
                  </div>
                )}
                
                {/* Intent Data Display */}
                {renderIntentData(message.intent_data)}
                
                {/* Timestamp */}
                <div className="text-xs opacity-70 mt-2">
                  {formatTimestamp(message.timestamp)}
                </div>
              </div>
            </div>
          )}

          {/* User message content */}
          {message.isUser && (
            <div>
              <div className="whitespace-pre-wrap">
                {message.message}
              </div>
              <div className="text-xs opacity-70 mt-2">
                {formatTimestamp(message.timestamp)}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;