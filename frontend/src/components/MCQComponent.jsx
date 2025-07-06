import React, { useState } from 'react';
import robotIdle from '../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_idle.png';
import robotWave from '../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_cheer0.png';
import robotThinking from '../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_attack1.png';

const styles = {
  mainContainer: {
    display: 'grid',
    gridTemplateColumns: '200px 1fr',
    gap: '24px',
    marginTop: '20px',
    minHeight: '500px',
  },
  contentContainer: {
    padding: '24px',
    backgroundColor: '#f9f9f9',
    borderRadius: '8px',
    border: '1px solid #e0e0e0',
    fontFamily: 'sans-serif',
  },
  robotContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'flex-start',
    paddingTop: '20px',
  },
  robotImage: {
    width: '150px',
    height: '150px',
    objectFit: 'contain',
    marginBottom: '16px',
    transition: 'all 0.3s ease',
  },
  robotSpeech: {
    backgroundColor: '#ffffff',
    border: '2px solid #4a90e2',
    borderRadius: '12px',
    padding: '12px',
    fontSize: '14px',
    textAlign: 'center',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    position: 'relative',
    maxWidth: '180px',
    lineHeight: '1.4',
  },
  speechArrow: {
    content: '""',
    position: 'absolute',
    top: '-10px',
    left: '50%',
    transform: 'translateX(-50%)',
    width: '0',
    height: '0',
    borderLeft: '10px solid transparent',
    borderRight: '10px solid transparent',
    borderBottom: '10px solid #4a90e2',
  },
  scenario: {
    fontSize: '18px',
    fontWeight: 'bold',
    marginBottom: '16px',
    color: '#333',
  },
  tableContainer: {
    display: 'flex',
    gap: '24px',
    marginBottom: '16px',
    flexWrap: 'wrap',
  },
  table: {
    borderCollapse: 'collapse',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  tableTitle: {
    fontSize: '16px',
    fontWeight: 'bold',
    marginBottom: '8px',
  },
  th: {
    backgroundColor: '#4a90e2',
    color: 'white',
    padding: '8px 12px',
    border: '1px solid #ddd',
    textAlign: 'left',
  },
  td: {
    padding: '8px 12px',
    border: '1px solid #ddd',
    backgroundColor: 'white',
  },
  query: {
    backgroundColor: '#2d2d2d',
    color: '#f8f8f2',
    padding: '16px',
    borderRadius: '4px',
    marginBottom: '16px',
    fontFamily: 'monospace',
    whiteSpace: 'pre-wrap',
    fontSize: '14px',
  },
  optionsContainer: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '12px',
    marginBottom: '20px',
  },
  optionButton: {
    padding: '12px',
    fontSize: '16px',
    border: '2px solid #ddd',
    borderRadius: '4px',
    cursor: 'pointer',
    textAlign: 'left',
    backgroundColor: 'white',
    transition: 'all 0.2s ease',
    width: '100%',
    height: '100%',
  },
  selectedOption: {
    borderColor: '#4a90e2',
    backgroundColor: '#e9f2fc',
    boxShadow: '0 0 5px rgba(74, 144, 226, 0.5)',
  },
  disabledOption: {
    backgroundColor: '#f5f5f5',
    color: '#999',
    cursor: 'not-allowed',
  },
  submitButton: {
    backgroundColor: '#4a90e2',
    color: 'white',
    border: 'none',
    padding: '12px 24px',
    fontSize: '16px',
    borderRadius: '4px',
    cursor: 'pointer',
    marginRight: '12px',
    transition: 'background-color 0.2s ease',
  },
  submitButtonDisabled: {
    backgroundColor: '#ccc',
    cursor: 'not-allowed',
  },
  feedbackContainer: {
    marginTop: '20px',
    padding: '16px',
    borderRadius: '8px',
    border: '2px solid',
  },
  correctFeedback: {
    backgroundColor: '#d4edda',
    borderColor: '#28a745',
    color: '#155724',
  },
  incorrectFeedback: {
    backgroundColor: '#f8d7da',
    borderColor: '#dc3545',
    color: '#721c24',
  },
  hintFeedback: {
    backgroundColor: '#fff3cd',
    borderColor: '#ffc107',
    color: '#856404',
  },
  attemptInfo: {
    fontSize: '14px',
    color: '#666',
    marginBottom: '8px',
  },
  retryButton: {
    backgroundColor: '#28a745',
    color: 'white',
    border: 'none',
    padding: '8px 16px',
    fontSize: '14px',
    borderRadius: '4px',
    cursor: 'pointer',
    marginTop: '10px',
    marginRight: '10px',
  },
  newQuestionButton: {
    backgroundColor: '#17a2b8',
    color: 'white',
    border: 'none',
    padding: '8px 16px',
    fontSize: '14px',
    borderRadius: '4px',
    cursor: 'pointer',
    marginTop: '10px',
  },
  proceedButton: {
    backgroundColor: '#28a745',
    color: 'white',
    border: 'none',
    padding: '12px 24px',
    fontSize: '16px',
    borderRadius: '4px',
    cursor: 'pointer',
    marginTop: '15px',
    fontWeight: 'bold',
  }
};

const FASTAPI_BASE_URL = 'http://localhost:5000';

function MCQComponent({ data, onStepComplete, user, onNewQuestion }) {
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [attemptNumber, setAttemptNumber] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [robotState, setRobotState] = useState('idle'); // 'idle', 'thinking', 'celebrating'

  if (!data) return null;

  const getRobotImage = () => {
    switch (robotState) {
      case 'thinking': return robotThinking;
      case 'celebrating': return robotWave;
      default: return robotIdle;
    }
  };

  const getRobotMessage = () => {
    if (feedback) {
      if (feedback.is_correct) {
        return "🎉 Excellent! You got it right! Take your time to review, then move on when ready.";
      } else if (attemptNumber === 1) {
        return "🤔 Not quite right. Try again!";
      } else if (attemptNumber === 2) {
        return "💡 Let me give you a hint...";
      } else {
        return "📚 Let me explain the correct answer. Try a new question to practice more!";
      }
    } else if (isSubmitting) {
      return "🧠 Let me check your answer...";
    } else if (robotState === 'thinking') {
      return "🔄 Generating a new question for you...";
    }
    return "🤖 Look at the tables and predict the output!";
  };

  const handleAnswerSelect = (answer) => {
    if (isComplete) return;
    setSelectedAnswer(answer);
  };

  const submitAnswer = async () => {
    if (!selectedAnswer || isSubmitting || isComplete) return;

    setIsSubmitting(true);
    setRobotState('thinking');

    try {
      const response = await fetch(`${FASTAPI_BASE_URL}/api/step2/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user?.uid || 'guest',
          user_answer: selectedAnswer,
          question_id: data.question_id
        })
      });

      const result = await response.json();
      setFeedback(result);
      setAttemptNumber(result.attempt_number);

      if (result.is_correct) {
        setRobotState('celebrating');
        setIsComplete(true);
        // Don't auto-complete - let user choose when to proceed
      } else {
        setRobotState('idle');
        if (!result.can_retry && !result.can_try_new_question) {
          setIsComplete(true);
          // Auto-complete step with flat rate scoring only for final wrong attempt
          setTimeout(() => {
            onStepComplete(true);
          }, 5000);
        }
      }
    } catch (error) {
      console.error('Error submitting answer:', error);
      setFeedback({
        is_correct: false,
        feedback: 'An error occurred. Please try again.',
        can_retry: true,
        can_try_new_question: false
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRetry = () => {
    setSelectedAnswer(null);
    setFeedback(null);
  };

  const handleNewQuestion = async () => {
    if (onNewQuestion) {
      setRobotState('thinking');
      setSelectedAnswer(null);
      setFeedback(null);
      setAttemptNumber(0);
      setIsComplete(false);
      
      try {
        await onNewQuestion(); // Call the parent's new question handler
      } catch (error) {
        console.error('Error generating new question:', error);
        setFeedback({
          is_correct: false,
          feedback: 'Error generating new question. Please try again.',
          can_retry: false,
          can_try_new_question: true
        });
      } finally {
        setRobotState('idle');
      }
    }
  };

  const handleProceedToNext = () => {
    onStepComplete(true);
  };

  const renderTable = (tableName, tableData) => {
    if (!tableData || tableData.length === 0) return null;
    const headers = Object.keys(tableData[0]);
    return (
      <div key={tableName}>
        <h4 style={styles.tableTitle}>{tableName}</h4>
        <table style={styles.table}>
          <thead>
            <tr>
              {headers.map(header => <th key={header} style={styles.th}>{header}</th>)}
            </tr>
          </thead>
          <tbody>
            {tableData.map((row, index) => (
              <tr key={index}>
                {headers.map(header => <td key={header} style={styles.td}>{String(row[header])}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const getFeedbackStyle = () => {
    if (!feedback) return {};
    if (feedback.is_correct) return styles.correctFeedback;
    if (attemptNumber === 2) return styles.hintFeedback;
    return styles.incorrectFeedback;
  };

  return (
    <div style={styles.mainContainer}>
      {/* Robot Section */}
      <div style={styles.robotContainer}>
        <img
          src={getRobotImage()}
          alt="SQL Tutor Robot"
          style={styles.robotImage}
        />
        <div style={styles.robotSpeech}>
          <div style={styles.speechArrow}></div>
          {getRobotMessage()}
        </div>
      </div>

      {/* Main Content */}
      <div style={styles.contentContainer}>
        <h3 style={styles.scenario}>{data.scenario}</h3>
        <div style={styles.tableContainer}>
          {Object.entries(data.tables).map(([tableName, tableData]) => (
            renderTable(tableName, tableData)
          ))}
        </div>
        <p>Given the tables above, what will this query return?</p>
        <pre style={styles.query}><code>{data.query}</code></pre>
        
        <div style={styles.optionsContainer}>
          {Object.entries(data.options).map(([key, value]) => (
            <button
              key={key}
              onClick={() => handleAnswerSelect(key)}
              disabled={isComplete}
              style={{
                ...styles.optionButton,
                ...(selectedAnswer === key ? styles.selectedOption : {}),
                ...(isComplete ? styles.disabledOption : {})
              }}
            >
              <strong>{key}:</strong> {value}
            </button>
          ))}
        </div>

        <button
          onClick={submitAnswer}
          disabled={!selectedAnswer || isSubmitting || isComplete}
          style={{
            ...styles.submitButton,
            ...(!selectedAnswer || isSubmitting || isComplete ? styles.submitButtonDisabled : {})
          }}
        >
          {isSubmitting ? 'Checking...' : 'Submit Answer'}
        </button>

        {/* Feedback Section */}
        {feedback && (
          <div style={{...styles.feedbackContainer, ...getFeedbackStyle()}}>
            <div style={styles.attemptInfo}>
              Attempt {attemptNumber} of 3
            </div>
            <div>{feedback.feedback}</div>
            {feedback.correct_answer && !feedback.is_correct && (
              <div style={{marginTop: '8px', fontWeight: 'bold'}}>
                Correct answer: {feedback.correct_answer}
              </div>
            )}
            {feedback.can_retry && (
              <button onClick={handleRetry} style={styles.retryButton}>
                Try Again
              </button>
            )}
            {feedback.can_try_new_question && (
              <button onClick={handleNewQuestion} style={styles.newQuestionButton}>
                🔄 Try New Question
              </button>
            )}
            {feedback.is_correct && (
              <button onClick={handleProceedToNext} style={styles.proceedButton}>
                Next, I'm ready to move on! 🚀
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default MCQComponent; 