import React from 'react';
import './TaskComponent.css';
import robotIdle from '../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_idle.png';
import robotThinking from '../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_attack1.png';
import robotWave from '../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_cheer0.png';

function TaskComponent({
  data,
  user,
  userQuery,
  setUserQuery,
  userExplanation,
  setUserExplanation,
  hintCount,
  hints = [],
  hintLoading = false,
  maxHints = 3,
  onGetHint,
  onRetry,
  onSubmit,
  submitted,
  needsRetry,
  score,
  feedback,
  isProcessing,
  onNextStep,
}) {
  if (!data) return null;

  const getRobotImage = () => {
    if (submitted && !needsRetry) {
      return robotWave;
    } else if (isProcessing) {
      return robotThinking;
    } else {
      return robotIdle;
    }
  };

  const getRobotMessage = () => {
    if (submitted && !needsRetry) {
          return "Great! Your answer has been submitted.";
  } else if (isProcessing) {
    return "Thinking...";
  } else if (needsRetry) {
    return "Try again, you can do it!";
  } else {
    return "Let's solve this SQL task together!";
  }
  };

  const renderSchemaTable = (tableName, columns) => {
    if (!columns || columns.length === 0) return null;
    return (
      <div className="table-schema" key={tableName}>
        <h5>{tableName}</h5>
        <table className="schema-table">
          <thead>
            <tr>
              <th>Column</th>
              <th>Type</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {columns.map((col, index) => (
              <tr key={index}>
                <td>{col.column}</td>
                <td>{col.type}</td>
                <td>{col.desc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const getFeedbackClass = () => {
    if (score === null) return '';
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  return (
    <div className="task-container">
      <div className="task-layout">
        {/* Robot Section */}
        <div className="robot-section">
          <div className="robot-character">
            <img 
              src={getRobotImage()} 
              alt="Robot Character" 
              className="robot-image"
            />
          </div>
          <div className="robot-speech-bubble">
            <div className="speech-arrow"></div>
            {getRobotMessage()}
          </div>
        </div>

        {/* Task Content */}
        <div className="task-content">
          <div className="task-header">
            <h3>SQL Query Task</h3>
          </div>
          
          <div className="task-description">
            <p>{data.task}</p>
          </div>

          {/* Schema Section */}
          <div className="schema-section">
            <h4>Database Schema Reference</h4>
            <div className="schema-tables">
              {Object.entries(data.schema).map(([tableName, columns]) => (
                renderSchemaTable(tableName, columns)
              ))}
            </div>
          </div>

          {/* Input Section */}
          <div className="input-section">
            <h4>Your Answer</h4>
            <div className="input-container">
              <div className="input-field">
                <label htmlFor="sql-query">Your SQL Query:</label>
                <textarea
                  id="sql-query"
                  className="sql-textarea"
                  value={userQuery}
                  onChange={(e) => setUserQuery(e.target.value)}
                />
              </div>
              <div className="input-field">
                <label htmlFor="explanation">Explain the query in your own words:</label>
                <textarea
                  id="explanation"
                  className="explanation-textarea"
                  value={userExplanation}
                  onChange={(e) => setUserExplanation(e.target.value)}
                />
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="action-buttons">
            <button 
              className="action-button hint-button" 
              onClick={onGetHint} 
              disabled={isProcessing || hintLoading || hintCount >= maxHints}
            >
                              {hintLoading ? "💡 Loading..." :
                hintCount >= maxHints ? `💡 Maximum hints reached (${hintCount}/${maxHints})` :
                `💡 Get Hint (${hintCount}/${maxHints})`}
            </button>
            {needsRetry && (
              <button 
                className="action-button retry-button" 
                onClick={onRetry} 
                disabled={isProcessing}
              >
                                  🔄 Retry
              </button>
            )}
            {!submitted && (
              <button 
                className="action-button submit-button" 
                onClick={onSubmit} 
                disabled={isProcessing}
              >
                🚀 Submit Answer
              </button>
            )}
          </div>

          {/* Hints Section */}
          {hints.length > 0 && (
            <div className="hints-section">
              <h4>Received Hints:</h4>
              <ul className="hints-list">
                {hints.map((hint, idx) => (
                  <li key={idx} className={hint === "Loading..." ? "loading" : ""}>
                    {hint}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Feedback Section */}
          {(feedback || score !== null) && (
            <div className={`feedback-section ${getFeedbackClass()}`}>
              {score !== null && (
                <div className="score-display">Score: {score}/100</div>
              )}
              {feedback && (
                <div className="feedback-text">{feedback}</div>
              )}
            </div>
          )}

          {/* Next Step Section */}
          {submitted && !needsRetry && (
            <div className="next-step-section">
              <button
                className="next-step-button success"
                onClick={onNextStep}
                disabled={isProcessing}
              >
                                  👍 Passed! Continue to next step 🚀
              </button>
              <p className="next-step-text">
                🎉 Congratulations! You have completed this task. You can proceed to Step 4 or click retry to get a higher score.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default TaskComponent; 