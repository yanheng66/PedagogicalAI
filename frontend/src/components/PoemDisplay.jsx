import React, { useState, useEffect } from 'react';
import './PoemDisplay.css';

const PoemDisplay = ({ poem, concept, onComplete }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [poemLines, setPoemLines] = useState([]);
  const [visibleLines, setVisibleLines] = useState([]);
  const [showCompleteButton, setShowCompleteButton] = useState(false);

  useEffect(() => {
    if (poem) {
      // Start the entrance animation
      setIsVisible(true);
      
      // Debug: log the raw poem
      console.log('Raw poem received:', JSON.stringify(poem));
      console.log('Poem type:', typeof poem);
      
      // Split poem into lines and animate them one by one
      // Handle both literal "\n" and actual newlines, avoiding duplicates
      let processedPoem = poem;
      
      // If the poem contains literal \n, replace them with actual newlines
      if (processedPoem.includes('\\n')) {
        processedPoem = processedPoem.replace(/\\n/g, '\n');
        console.log('After replacing \\n:', JSON.stringify(processedPoem));
      }
      
      // Split by newlines and remove empty lines
      const lines = processedPoem
        .split('\n')
        .map(line => line.trim())
        .filter(line => line !== '');
      
      console.log('Final lines array:', lines);
      
      // Set all lines at once
      setPoemLines(lines);
      setVisibleLines([]);
      setShowCompleteButton(false);
      
      // Clear any existing timeouts
      const timeouts = [];
      
      // Show lines one by one
      lines.forEach((line, index) => {
        const timeout = setTimeout(() => {
          console.log(`Making line ${index} visible: "${line}"`);
          setVisibleLines(prev => {
            const newVisible = [...prev, index];
            console.log(`Visible line indices:`, newVisible);
            return newVisible;
          });
        }, index * 800); // 800ms delay between lines
        timeouts.push(timeout);
      });
      
      // Show complete button after all lines are animated
      const completeTimeout = setTimeout(() => {
        setShowCompleteButton(true);
      }, lines.length * 800 + 2000); // Extra 2 seconds after last line
      timeouts.push(completeTimeout);
      
      // Cleanup function to clear timeouts if component unmounts or poem changes
      return () => {
        timeouts.forEach(timeout => clearTimeout(timeout));
      };
    }
  }, [poem]);

  if (!poem) return null;

  return (
    <div className={`poem-container ${isVisible ? 'fade-in' : ''}`}>
      <div className="poem-background">
        <div className="floating-particles">
          {[...Array(20)].map((_, i) => (
            <div key={i} className={`particle particle-${i % 4}`}></div>
          ))}
        </div>
        
        <div className="poem-content">
          <div className="poem-header">
            <h2 className="poem-title">🎭 Learning Poem 🎭</h2>
            <div className="concept-badge">{concept}</div>
          </div>
          
          <div className="poem-text">
            {poemLines.map((line, index) => {
              const isVisible = visibleLines.includes(index);
              console.log(`Rendering line ${index}: "${line}" (visible: ${isVisible})`);
              return (
                <div 
                  key={`poem-line-${index}`}
                  className={`poem-line poem-line-${index} ${isVisible ? 'visible' : 'hidden'}`}
                  style={{ animationDelay: `${index * 0.8}s` }}
                >
                  {line}
                </div>
              );
            })}
          </div>
          
          <div className="poem-decoration">
            <div className="sparkle sparkle-1">✨</div>
            <div className="sparkle sparkle-2">🌟</div>
            <div className="sparkle sparkle-3">💫</div>
            <div className="sparkle sparkle-4">⭐</div>
          </div>
          
          {showCompleteButton && (
            <div className="poem-actions">
              <button 
                className="complete-button"
                onClick={onComplete}
              >
                🎉 Complete Lesson 🎉
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PoemDisplay; 