import React, { useState, useEffect } from 'react';

const TypewriterTagline = ({ 
  text = "Your personal smart assistant", 
  className = "",
  speed = 150,
  pauseDuration = 2000,
  eraseSpeed = 100 
}) => {
  const [displayText, setDisplayText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isErasing, setIsErasing] = useState(false);
  const [showCursor, setShowCursor] = useState(true);

  useEffect(() => {
    // Cursor blinking effect
    const cursorInterval = setInterval(() => {
      setShowCursor(prev => !prev);
    }, 530);

    return () => clearInterval(cursorInterval);
  }, []);

  useEffect(() => {
    const timeout = setTimeout(() => {
      if (!isErasing) {
        // Typing phase
        if (currentIndex < text.length) {
          setDisplayText(text.slice(0, currentIndex + 1));
          setCurrentIndex(currentIndex + 1);
        } else {
          // Finished typing, wait then start erasing
          setTimeout(() => setIsErasing(true), pauseDuration);
        }
      } else {
        // Erasing phase
        if (currentIndex > 0) {
          setDisplayText(text.slice(0, currentIndex - 1));
          setCurrentIndex(currentIndex - 1);
        } else {
          // Finished erasing, start typing again
          setIsErasing(false);
          setTimeout(() => setCurrentIndex(0), 500);
        }
      }
    }, isErasing ? eraseSpeed : speed);

    return () => clearTimeout(timeout);
  }, [currentIndex, isErasing, text, speed, eraseSpeed, pauseDuration]);

  return (
    <div className={`typewriter-container ${className}`}>
      <span className="shimmer-gradient-text">
        {displayText}
        <span 
          className={`typewriter-cursor ${showCursor ? 'visible' : 'invisible'}`}
        >
          |
        </span>
      </span>
    </div>
  );
};

export default TypewriterTagline;