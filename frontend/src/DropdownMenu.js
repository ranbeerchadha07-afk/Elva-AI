import React, { useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

function DropdownMenu({ 
  showDropPanel, 
  setShowDropPanel, 
  toggleTheme, 
  isDarkTheme, 
  exportChat, 
  startNewChat
}) {
  const dropPanelRef = useRef(null);

  // Toggle drop-left panel
  const toggleDropPanel = () => {
    setShowDropPanel(!showDropPanel);
  };

  // Click outside to close panel
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropPanelRef.current && !dropPanelRef.current.contains(event.target)) {
        setShowDropPanel(false);
      }
    };

    if (showDropPanel) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showDropPanel, setShowDropPanel]);

  return (
    <div className="relative" ref={dropPanelRef}>
      {/* Plus Button Trigger */}
      <button
        onClick={toggleDropPanel}
        className="circular-icon-btn new-chat-btn"
        title="Open Menu"
      >
        <motion.div 
          className="plus-icon"
          animate={{ rotate: showDropPanel ? 45 : 0 }}
          transition={{ 
            duration: 0.3,
            ease: "easeInOut"
          }}
        >
          +
        </motion.div>
      </button>

      {/* Drop-Down Panel */}
      <AnimatePresence>
        {showDropPanel && (
          <motion.div
            initial={{ opacity: 0, y: -20, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.8 }}
            transition={{ 
              type: "spring", 
              stiffness: 300, 
              damping: 25,
              duration: 0.4
            }}
            className="drop-down-panel"
            style={{
              willChange: 'transform, opacity',
              backfaceVisibility: 'hidden'
            }}
          >
            <div className="drop-panel-content">
              {/* Theme Toggle Button */}
              <motion.button
                onClick={toggleTheme}
                className="panel-btn theme-panel-btn"
                title="Toggle Theme"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                whileHover={{ scale: 1.1, y: -2 }}
                whileTap={{ scale: 0.95 }}
              >
                <motion.div
                  className="btn-icon-text"
                  animate={{ rotate: isDarkTheme ? 0 : 180 }}
                  transition={{ duration: 0.5 }}
                >
                  {isDarkTheme ? '🌙' : '☀️'}
                </motion.div>
              </motion.button>

              {/* Export Chat Button */}
              <motion.button
                onClick={exportChat}
                className="panel-btn export-panel-btn"
                title="Export Chat"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                whileHover={{ scale: 1.1, y: -2 }}
                whileTap={{ scale: 0.95 }}
              >
                <div className="btn-icon-text">📤</div>
              </motion.button>

              {/* New Chat Button */}
              <motion.button
                onClick={startNewChat}
                className="panel-btn new-chat-panel-btn"
                title="Start New Chat"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                whileHover={{ scale: 1.1, y: -2 }}
                whileTap={{ scale: 0.95 }}
              >
                <div className="btn-icon-text">➕</div>
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default DropdownMenu;