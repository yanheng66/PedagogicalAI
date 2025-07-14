import React, { useState, useEffect, useCallback } from 'react';
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
  const [error, setError] = useState(null); // Dedicated error state
  const [showHints, setShowHints] = useState(false);
  
  // Pass/Fail status tracking
  const [passStatus, setPassStatus] = useState(null); // "PASS", "RETRY_RECOMMENDED", "MUST_RETRY"
  const [canProceedToNext, setCanProceedToNext] = useState(false);
  const [thresholdMessage, setThresholdMessage] = useState('');
  
  // XP tracking
  const [totalScore, setTotalScore] = useState(0);
  
  // Quality-based grading (NEW)
  const [correctnessLevel, setCorrectnessLevel] = useState(null); // "EXCELLENT", "GOOD", "FAIR", "POOR"
  const [structureLevel, setStructureLevel] = useState(null);
  const [overallQuality, setOverallQuality] = useState(null);
  const [bonusScore, setBonusScore] = useState(0);

  const fetchStep4ChallengeData = useCallback(async (userId, topic, conceptId) => {
    try {
      const response = await fetch(`${FASTAPI_BASE_URL}/api/step4`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          topic: topic || "INNER JOIN",
          concept_id: conceptId || "inner-join"
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to load challenge');
      }

      return response.json();
    } catch (error) {
      console.error('Error fetching challenge data:', error);
      throw error;
    }
  }, []);

  const loadChallenge = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null); // Reset error state on load
      const data = await fetchStep4ChallengeData(userId, concept, conceptId);
      if (data && data.challenge_data) {
        setChallengeData(data.challenge_data);
      } else {
        throw new Error("No challenge data received from API.");
      }
    } catch (err) {
      console.error("Failed to load challenge:", err);
      setError(`Failed to load the challenge: ${err.message}. Please try again.`);
    } finally {
      setIsLoading(false);
    }
  }, [userId, concept, conceptId, fetchStep4ChallengeData]);

  // Load challenge data when component mounts
  useEffect(() => {
    loadChallenge();
  }, [loadChallenge]);

  const handleSubmit = async () => {
    if (!userSolution.trim()) {
      alert('Please enter a SQL solution before submitting.');
      return;
    }

    setIsSubmitting(true);
    setRobotState('thinking');
    setError(null); // Reset previous errors

    const payload = {
      user_id: userId,
      user_solution: userSolution,
      question_id: challengeData?.question_id,
    };

    console.log("Submitting to /api/step4/submit with payload:", JSON.stringify(payload, null, 2));

    try {
      const response = await fetch(`${FASTAPI_BASE_URL}/api/step4/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        let errorMsg = `API request failed with status ${response.status}.`;
        try {
          // Try to get more specific error from backend JSON response
          const errorData = await response.json();
          errorMsg = errorData.detail || errorMsg;
        } catch (e) {
          // Backend did not return JSON, use the raw text
          errorMsg = await response.text();
        }
        console.error("API Error Response:", errorMsg);
        throw new Error(errorMsg);
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
      
      // Store total score for XP system (internal use only)
      const scoreFromAPI = result.total_score || 0;
      setTotalScore(scoreFromAPI);
      
      // Handle quality-based grading (NEW: primary display to user)
      setCorrectnessLevel(result.correctness_level);
      setStructureLevel(result.structure_level);
      setOverallQuality(result.overall_quality);
      
      // Handle bonus score
      setBonusScore(result.bonus_score || 0);
      
      // Debug logging for XP and quality integration
      console.log('[Step4] Response received from API:', {
        total_score: result.total_score,
        pass_status: result.pass_status,
        overall_quality: result.overall_quality,
        correctness_level: result.correctness_level,
        structure_level: result.structure_level
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
      console.error('Error submitting solution:', error.message);
      // Display the specific error message from the backend if available
      setError(`An error occurred: ${error.message}. Please try again later.`);
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
    // Reset quality grades (NEW)
    setCorrectnessLevel(null);
    setStructureLevel(null);
    setOverallQuality(null);
    // Keep the user's solution for editing
  };

  const handleNextStep = () => {
    if (onComplete) {
      // Pass the pass status to the parent component (true if passed, false if not)
      const passed = passStatus === 'PASS' || passStatus === 'RETRY_RECOMMENDED';
      console.log('[Step4] Moving to next step with pass status:', passed);
      
      onComplete(passed);
    }
  };

  const handleShowHints = () => {
    setShowHints(true);
  };

  const getBonusTooltipContent = () => {
    const difficulty = challengeData?.difficulty?.toUpperCase() || 'MEDIUM';
    
    return (
      <div className="tooltip-content">
        <h4>Quality-Based Grading System</h4>
        <ul>
          <li><strong>EXCELLENT:</strong> Perfect solution - 100% correct with clear understanding</li>
          <li><strong>GOOD:</strong> Mostly correct (90-99%) - Minor issues but solid understanding</li>
          <li><strong>FAIR:</strong> Correct but has errors (70-89%) - Basic understanding shown</li>
          <li><strong>POOR:</strong> Major errors (&lt;70%) - Needs significant improvement</li>
        </ul>
        <p><small><strong>Passing threshold:</strong> GOOD quality or above</small></p>
        <p><small>Problem difficulty is determined by your Step 3 performance score.</small></p>
        
        <h4>Bonus Points</h4>
        <ul>
          <li><strong>EASY:</strong> +10 points for completing without hints</li>
          <li><strong>MEDIUM:</strong> +5 points for completing without hints</li>
          <li><strong>HARD:</strong> +15 points for EXCELLENT solutions with good structure</li>
        </ul>
        <p><small>Bonus points are awarded when you solve problems efficiently with minimal assistance.</small></p>
        
        {difficulty === 'EASY' && (
          <p><small><strong>Tip:</strong> Focus on getting the basics right to achieve GOOD quality!</small></p>
        )}
        {difficulty === 'MEDIUM' && (
          <p><small><strong>Tip:</strong> Pay attention to both correctness and code structure!</small></p>
        )}
        {difficulty === 'HARD' && (
          <p><small><strong>Tip:</strong> Strive for EXCELLENT quality with optimal solutions!</small></p>
        )}
      </div>
    );
  };

  const getQualityBadgeStyle = (quality) => {
    switch (quality) {
      case 'EXCELLENT':
        return { 
          backgroundColor: '#d4edda', 
          color: '#155724', 
          border: '2px solid #28a745',
          fontWeight: 'bold'
        };
      case 'GOOD':
        return { 
          backgroundColor: '#d1ecf1', 
          color: '#0c5460', 
          border: '2px solid #17a2b8',
          fontWeight: 'bold'
        };
      case 'FAIR':
        return { 
          backgroundColor: '#fff3cd', 
          color: '#856404', 
          border: '2px solid #ffc107',
          fontWeight: 'bold'
        };
      case 'POOR':
        return { 
          backgroundColor: '#f8d7da', 
          color: '#721c24', 
          border: '2px solid #dc3545',
          fontWeight: 'bold'
        };
      default:
        return { 
          backgroundColor: '#e9ecef', 
          color: '#495057', 
          border: '2px solid #ced4da'
        };
    }
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
          <button onClick={() => {
            setError(null);
            loadChallenge();
          }}>Try Again</button>
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
              
              {/* Show Retry button whenever there's feedback */}
              {feedback && (
                <button 
                  onClick={handleRetry}
                  className="retry-button"
                >
                  {passStatus === 'MUST_RETRY' 
                    ? 'Retry Challenge (Required)' 
                    : passStatus === 'PASS' 
                      ? 'Retry for Perfect Score' 
                      : 'Retry for Better Score'}
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
                <h3>Solution Evaluation</h3>
                <div className="info-icon-container">
                  <span className="info-icon">ℹ️</span>
                  <div className="tooltip">
                    {getBonusTooltipContent()}
                  </div>
                </div>
              </div>

              {/* Quality Grades Display (NEW) */}
              {overallQuality && (
                <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                  <h4 style={{ margin: '0 0 12px 0', color: '#333' }}>Solution Quality</h4>
                  <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', alignItems: 'center' }}>
                    <div>
                      <span style={{ fontSize: '14px', color: '#666', marginRight: '8px' }}>Overall:</span>
                      <span 
                        style={{
                          ...getQualityBadgeStyle(overallQuality),
                          padding: '6px 12px',
                          borderRadius: '6px',
                          fontSize: '14px'
                        }}
                      >
                        {overallQuality}
                      </span>
                    </div>
                    
                    {/* Bonus Score Display */}
                    {bonusScore > 0 && (
                      <div>
                        <span style={{ fontSize: '14px', color: '#666', marginRight: '8px' }}>Bonus:</span>
                        <span 
                          style={{
                            backgroundColor: '#fff3cd',
                            color: '#856404',
                            border: '2px solid #ffc107',
                            padding: '4px 8px',
                            borderRadius: '4px',
                            fontSize: '12px',
                            fontWeight: 'bold'
                          }}
                        >
                          +{bonusScore} pts
                        </span>
                        <span style={{ fontSize: '12px', color: '#666', marginLeft: '8px' }}>
                          (awarded when you use fewer hints)
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}
              
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
                <div className="pass-status-actions">
                  <button 
                    onClick={handleNextStep}
                    className="next-step-button success"
                  >
                    Excellent! Continue to Step 5 🚀
                  </button>
                  <p className="pass-text">
                    🎉 Great job! You've passed the challenge. You can proceed to the next step or retry to achieve a perfect score.
                  </p>
                </div>
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