import React, { useState, useEffect } from 'react';
import './ChallengeComponent.css';
import robotIdle from '../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_idle.png';
import robotWave from '../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_cheer0.png';
import robotThinking from '../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_attack1.png';

const FASTAPI_BASE_URL = 'http://localhost:8000';

const ChallengeComponent = ({ userId, onComplete, concept, conceptId }) => {
  const [challengeData, setChallengeData] = useState(null);
  const [userSolution, setUserSolution] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [isCorrect, setIsCorrect] = useState(false);
  const [attemptNumber, setAttemptNumber] = useState(0);
  const [canRetry, setCanRetry] = useState(true);
  const [robotState, setRobotState] = useState('idle'); // idle, thinking, celebrating, encouraging
  const [showNextButton, setShowNextButton] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showHints, setShowHints] = useState(false);
  
  // Pass/Fail status tracking
  const [passStatus, setPassStatus] = useState(null); // "PASS", "RETRY_RECOMMENDED", "MUST_RETRY"
  const [canProceedToNext, setCanProceedToNext] = useState(false);
  const [thresholdMessage, setThresholdMessage] = useState('');
  
  // XP tracking
  const [totalScore, setTotalScore] = useState(0);

  // Load challenge data when component mounts
  useEffect(() => {
    const loadChallenge = async () => {
      try {
        setIsLoading(true);
        const response = await fetch(`${FASTAPI_BASE_URL}/api/step4`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: userId,
            topic: concept || "INNER JOIN",
            concept_id: conceptId || "inner-join"
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to load challenge');
        }

        const data = await response.json();
        setChallengeData(data.challenge_data);
        setRobotState('idle');
        setError(null);
      } catch (error) {
        console.error('Error loading challenge:', error);
        setError('Failed to load challenge. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    loadChallenge();
  }, [userId]);

  const handleSubmit = async () => {
    if (!userSolution.trim()) {
      alert('Please enter a SQL solution before submitting.');
      return;
    }

    setIsSubmitting(true);
    setRobotState('thinking');

    try {
      const response = await fetch(`${FASTAPI_BASE_URL}/api/step4/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          user_solution: userSolution,
          question_id: challengeData?.question_id,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit solution');
      }

      const result = await response.json();
      
      setFeedback(result.feedback);
      setIsCorrect(result.is_correct);
      setAttemptNumber(result.attempt_number);
      setCanRetry(result.can_retry);
      
      // Handle pass/fail status
      setPassStatus(result.pass_status);
      setCanProceedToNext(result.can_proceed_to_next);
      setThresholdMessage(result.threshold_message);
      
      // Store total score for XP system
      const scoreFromAPI = result.total_score || 0;
      setTotalScore(scoreFromAPI);
      
      // Debug logging for XP integration
      console.log('[Step4] Score received from API:', {
        total_score: result.total_score,
        pass_status: result.pass_status,
        scoreToUse: scoreFromAPI
      });

      // Update robot state and show next button based on pass status
      if (result.pass_status === 'PASS') {
        setRobotState('celebrating');
        setShowNextButton(true);
      } else if (result.pass_status === 'RETRY_RECOMMENDED') {
        setRobotState('encouraging');
        setShowNextButton(true); // Can proceed but with warning
      } else { // MUST_RETRY
        setRobotState('encouraging');
        setShowNextButton(false); // Cannot proceed
      }

    } catch (error) {
      console.error('Error submitting solution:', error);
      setFeedback('Error submitting solution. Please try again.');
      setRobotState('idle');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRetry = () => {
    setFeedback('');
    setRobotState('idle');
    setIsCorrect(false);
    setShowNextButton(false);
    // Reset pass/fail status
    setPassStatus(null);
    setCanProceedToNext(false);
    setThresholdMessage('');
    // Reset score
    setTotalScore(0);
    // Keep the user's solution for editing
  };

  const handleNextStep = () => {
    if (onComplete) {
      // Pass the total score as XP to the parent component
      console.log('[Step4] Moving to next step with score:', totalScore);
      
      // Only pass score if it's greater than 0, otherwise let parent use default XP
      const xpToAward = totalScore > 0 ? totalScore : null;
      onComplete(xpToAward);
    }
  };

  const handleShowHints = () => {
    setShowHints(true);
  };

  const getBonusTooltipContent = () => {
    const difficulty = challengeData?.difficulty?.toUpperCase() || 'MEDIUM';
    
    return (
      <div className="tooltip-content">
        <h4>Bonus Scoring System</h4>
        <ul>
          <li>
            <strong>Easy Problems:</strong> +10 bonus points if completed without using hints
            {difficulty === 'EASY' && <span> ⭐ (Current Level)</span>}
          </li>
          <li>
            <strong>Medium Problems:</strong> +5 bonus points if completed without using hints
            {difficulty === 'MEDIUM' && <span> ⭐ (Current Level)</span>}
          </li>
          <li>
            <strong>Hard Problems:</strong> +15 bonus points for optimal solutions with excellent code structure
            {difficulty === 'HARD' && <span> ⭐ (Current Level)</span>}
          </li>
        </ul>
        <p><small>Problem difficulty is determined by your Step 3 performance score.</small></p>
        {difficulty === 'EASY' && (
          <p><small><strong>Tip:</strong> Complete this problem without hints to earn bonus points!</small></p>
        )}
        {difficulty === 'MEDIUM' && (
          <p><small><strong>Tip:</strong> Complete this problem without hints to earn +5 bonus points!</small></p>
        )}
        {difficulty === 'HARD' && (
          <p><small><strong>Tip:</strong> Focus on both correctness and clean code structure for maximum points!</small></p>
        )}
      </div>
    );
  };

  const getRobotImage = () => {
    switch (robotState) {
      case 'thinking':
        return robotThinking;
      case 'celebrating':
      case 'encouraging':
        return robotWave;
      default:
        return robotIdle;
    }
  };

  const getRobotMessage = () => {
    switch (robotState) {
      case 'thinking':
        return "Let me analyze your SQL solution... 🤔";
      case 'celebrating':
        if (passStatus === 'PASS') {
          return "Outstanding! You passed with flying colors! 🎉";
        }
        return "Excellent work! Your solution is correct! 🎉";
      case 'encouraging':
        if (passStatus === 'RETRY_RECOMMENDED') {
          return "Good effort! You can proceed, but I recommend practicing more. 💪";
        } else if (passStatus === 'MUST_RETRY') {
          return "Keep practicing! You need a bit more work before proceeding. 📚";
        }
        return "Good effort! Let's work on improving your solution. 💪";
      default:
        return "I'm here to help you with this SQL challenge! Write your solution and I'll provide feedback. 🤖";
    }
  };

  if (isLoading) {
    return (
      <div className="challenge-container">
        <div className="loading-message">
          <div className="spinner"></div>
          <p>Loading your SQL challenge...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="challenge-container">
        <div className="error-message">
          <p>❌ {error}</p>
          <button onClick={() => window.location.reload()}>Try Again</button>
        </div>
      </div>
    );
  }

  return (
    <div className="challenge-container">
      <div className="challenge-layout">
        {/* Robot Section */}
        <div className="robot-section">
          <div className="robot-character">
            <img 
              src={getRobotImage()} 
              alt="Robot Helper" 
              className="robot-image"
            />
          </div>
          <div className="robot-speech-bubble">
            <div className="speech-arrow"></div>
            <p>{getRobotMessage()}</p>
          </div>
        </div>

        {/* Challenge Content */}
        <div className="challenge-content">
          <div className="challenge-header">
            <h2>{challengeData?.title}</h2>
            <div className="difficulty-badge">
              <span className={`badge ${challengeData?.difficulty?.toLowerCase()}`}>
                {challengeData?.difficulty}
              </span>
            </div>
          </div>

          <div className="challenge-description">
            <h3>Scenario</h3>
            <p>{challengeData?.scenario}</p>
            
            <h3>Challenge</h3>
            <p>{challengeData?.task}</p>
          </div>

          {/* Database Schema */}
          <div className="schema-section">
            <h3>Database Schema</h3>
            <div className="schema-tables">
              {challengeData?.schema && Object.entries(challengeData.schema).map(([tableName, columns]) => (
                <div key={tableName} className="table-schema">
                  <h4>{tableName}</h4>
                  <div className="table-columns">
                    {columns.map((column, index) => (
                      <div key={index} className="column-info">
                        <span className="column-name">{column.column}</span>
                        <span className="column-type">{column.type}</span>
                        <span className="column-desc">{column.description}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Sample Data */}
          {challengeData?.sample_data && (
            <div className="sample-data-section">
              <h3>Sample Data</h3>
              {Object.entries(challengeData.sample_data).map(([tableName, rows]) => (
                <div key={tableName} className="sample-table">
                  <h4>{tableName}</h4>
                  <div className="table-preview">
                    {rows.slice(0, 3).map((row, index) => (
                      <div key={index} className="sample-row">
                        {Object.entries(row).map(([key, value]) => (
                          <span key={key} className="sample-cell">
                            <strong>{key}:</strong> {value}
                          </span>
                        ))}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* SQL Solution Input */}
          <div className="solution-section">
            <h3>Your SQL Solution</h3>
            <textarea
              value={userSolution}
              onChange={(e) => setUserSolution(e.target.value)}
              placeholder="Write your SQL query here..."
              className="sql-input"
              rows="8"
              disabled={isSubmitting}
            />
            
            <div className="solution-actions">
              {/* Show Submit button only when no feedback is present */}
              {!feedback && (
                <button 
                  onClick={handleSubmit} 
                  disabled={isSubmitting || !userSolution.trim()}
                  className="submit-button"
                >
                  {isSubmitting ? 'Analyzing...' : 'Submit Solution'}
                </button>
              )}
              
              {/* Show Retry button based on pass status */}
              {feedback && (passStatus === 'RETRY_RECOMMENDED' || passStatus === 'MUST_RETRY') && (
                <button 
                  onClick={handleRetry}
                  className="retry-button"
                >
                  {passStatus === 'MUST_RETRY' ? 'Retry Challenge' : 'Retry for Better Score'}
                </button>
              )}

              {/* Show Hint Button when hints are available and not already shown */}
              {challengeData?.hints && challengeData.hints.length > 0 && !showHints && (
                <button 
                  onClick={handleShowHints}
                  className="hint-button"
                >
                  💡 Show Hints
                </button>
              )}
            </div>
          </div>

          {/* Feedback Section */}
          {feedback && (
            <div className={`feedback-section ${isCorrect ? 'correct' : 'incorrect'}`}>
              <div className="feedback-header">
                <h3>Feedback</h3>
                <div className="info-icon-container">
                  <span className="info-icon">ℹ️</span>
                  <div className="tooltip">
                    {getBonusTooltipContent()}
                  </div>
                </div>
              </div>
              <div className="feedback-content">
                <pre className="feedback-text">{feedback}</pre>
              </div>
              
              {attemptNumber > 0 && (
                <div className="attempt-info">
                  <span>Attempt {attemptNumber}</span>
                </div>
              )}
            </div>
          )}

          {/* Hints Section - Only show when requested */}
          {showHints && challengeData?.hints && challengeData.hints.length > 0 && (
            <div className="hints-section">
              <h3>💡 Hints</h3>
              <ul>
                {challengeData.hints.map((hint, index) => (
                  <li key={index}>{hint}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Next Step Buttons based on pass status */}
          {showNextButton && (
            <div className="next-step-section">
              {passStatus === 'PASS' && (
                <button 
                  onClick={handleNextStep}
                  className="next-step-button success"
                >
                  Excellent! Continue to Step 5 🚀
                </button>
              )}
              
              {passStatus === 'RETRY_RECOMMENDED' && (
                <div className="recommended-retry-actions">
                  <button 
                    onClick={handleNextStep}
                    className="next-step-button warning"
                  >
                    Continue to Step 5 (Not Recommended) ⚠️
                  </button>
                  <p className="recommendation-text">
                    💡 While you can proceed, we recommend retrying for better understanding!
                  </p>
                </div>
              )}
              
              {/* MUST_RETRY status doesn't show next button at all - handled by showNextButton state */}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChallengeComponent; 