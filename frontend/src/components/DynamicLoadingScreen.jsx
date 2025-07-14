import React, { useState, useEffect, useRef } from 'react';
import { getRandomTrivia } from '../data/sqlTrivia';
import './DynamicLoadingScreen.css';

const DynamicLoadingScreen = ({ 
  message = "Loading...", 
  concept = null, 
  showTrivia = true,
  triviaType = 'mixed',
  minDisplayTime = 2000 // Minimum time to show the loading screen
}) => {
  const [currentTrivia, setCurrentTrivia] = useState(null);
  const [displayTime, setDisplayTime] = useState(0);
  const lastTriviaRef = useRef(null);

  useEffect(() => {
    // Get one trivia item for the entire loading session
    const singleTrivia = getRandomTrivia(concept, triviaType);
    setCurrentTrivia(singleTrivia);
    lastTriviaRef.current = singleTrivia;

    // Track display time
    const timeInterval = setInterval(() => {
      setDisplayTime(prev => prev + 100);
    }, 100);

    return () => {
      clearInterval(timeInterval);
    };
  }, [concept, triviaType]);

  const progressPercent = Math.min(100, (displayTime / minDisplayTime) * 100);

  return (
    <div className="dynamic-loading-screen">
      {/* Animated background with floating SQL symbols */}
      <div className="loading-background">
        <div className="floating-symbols">
          {['SELECT', 'FROM', 'WHERE', 'JOIN', '{', '}', '*', '='].map((symbol, index) => (
            <div 
              key={index} 
              className={`floating-symbol symbol-${index}`}
              style={{
                animationDelay: `${index * 0.5}s`,
                left: `${10 + (index * 12)}%`,
                fontSize: Math.random() > 0.5 ? '18px' : '14px',
                opacity: Math.random() * 0.3 + 0.1
              }}
            >
              {symbol}
            </div>
          ))}
        </div>
      </div>

      {/* Main loading content */}
      <div className="loading-content">
        {/* Main spinner and message */}
        <div className="loading-header">
          <div className="sql-spinner">
            <div className="spinner-ring"></div>
            <div className="spinner-ring"></div>
            <div className="spinner-ring"></div>
            <div className="sql-icon">⚡</div>
          </div>
          <h2 className="loading-message">{message}</h2>
          
          {/* Progress bar */}
          <div className="progress-container">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${progressPercent}%` }}
              ></div>
            </div>
            <div className="progress-text">
              {Math.round(progressPercent)}%
            </div>
          </div>
        </div>

        {/* Trivia section */}
        {showTrivia && currentTrivia && (
          <div className="trivia-section">
            <div className="trivia-header">
              <span className="trivia-icon">{currentTrivia.icon}</span>
              <span className="trivia-label">SQL趣事</span>
            </div>
            <div className="trivia-content">
              <p className="trivia-fact">{currentTrivia.fact}</p>
            </div>
          </div>
        )}

        {/* Loading dots animation */}
        <div className="loading-dots">
          <span className="dot"></span>
          <span className="dot"></span>
          <span className="dot"></span>
        </div>

        {/* Concept badge if provided */}
        {concept && (
          <div className="concept-badge">
            <span className="badge-label">当前学习</span>
            <span className="badge-concept">{concept}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default DynamicLoadingScreen; 