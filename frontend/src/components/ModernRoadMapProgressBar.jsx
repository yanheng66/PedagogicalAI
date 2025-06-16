import React from 'react';

function ModernRoadMapProgressBar({ totalSteps = 5, currentStep = 0, completedSteps = [], onLessonClick }) {
  const steps = Array.from({ length: totalSteps }, (_, i) => i);
  
  const getStepStatus = (stepIndex) => {
    if (stepIndex < currentStep) return 'completed';
    if (stepIndex === currentStep) return 'current';
    return 'upcoming';
  };

  const getStepIcon = (stepIndex, status) => {
    if (status === 'completed') return '✓';
    if (status === 'current') return '🎯';
    return stepIndex + 1;
  };

  const getBuildingEmoji = (stepIndex) => {
    const buildings = ['🏠', '🏪', '🏢', '🏛️', '🏰', '🕌', '🗼'];
    return buildings[stepIndex % buildings.length];
  };

  const handleStepClick = (stepIndex) => {
    // Only allow clicking if the step is completed
    if (completedSteps.includes(stepIndex) && onLessonClick) {
      onLessonClick(stepIndex);
    }
  };

  return (
    <div className="roadmap-container">
      <div className="roadmap-header">
        <h3>Learning Journey</h3>
        <p>Step {currentStep + 1} of {totalSteps}</p>
      </div>
      
      <div className="roadmap-track">
        {steps.map((stepIndex, index) => {
          const status = getStepStatus(stepIndex);
          const isLastStep = index === steps.length - 1;
          const isCompleted = completedSteps.includes(stepIndex);
          
          return (
            <div key={stepIndex} className="step-container">
              {/* Step Node */}
              <div className={`step-node ${status}`}>
                <div 
                  className={`step-building ${isCompleted ? 'clickable' : ''}`}
                  onClick={() => handleStepClick(stepIndex)}
                  style={{ cursor: isCompleted ? 'pointer' : 'default' }}
                >
                  {getBuildingEmoji(stepIndex)}
                </div>
                <div className="step-indicator">
                  {getStepIcon(stepIndex, status)}
                </div>
                <div className="step-label">
                  Lesson {stepIndex + 1}
                </div>
              </div>
              
              {/* Road Connection */}
              {!isLastStep && (
                <div className={`road-connection ${status === 'completed' ? 'completed' : 'incomplete'}`}>
                  <div className="road-line"></div>
                  <div className="road-dots">
                    <span>•</span>
                    <span>•</span>
                    <span>•</span>
                  </div>
                </div>
              )}
            </div>
          );
        })}
        
        {/* Goal Flag */}
        <div className="goal-container">
          <div className={`goal-flag ${currentStep >= totalSteps ? 'reached' : 'unreached'}`}>
            🏁
          </div>
          <div className="goal-label">
            {currentStep >= totalSteps ? 'Complete!' : 'Goal'}
          </div>
        </div>
      </div>

      <style jsx>{`
        .roadmap-container {
          padding: 24px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 16px;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
          margin: 20px 0;
          color: white;
        }

        .roadmap-header {
          text-align: center;
          margin-bottom: 24px;
        }

        .roadmap-header h3 {
          margin: 0 0 8px 0;
          font-size: 20px;
          font-weight: 600;
        }

        .roadmap-header p {
          margin: 0;
          opacity: 0.9;
          font-size: 14px;
        }

        .roadmap-track {
          display: flex;
          align-items: center;
          justify-content: center;
          overflow-x: auto;
          padding: 20px 0;
        }

        .step-container {
          display: flex;
          align-items: center;
          flex-shrink: 0;
        }

        .step-node {
          display: flex;
          flex-direction: column;
          align-items: center;
          position: relative;
          transition: all 0.3s ease;
        }

        .step-building {
          font-size: 32px;
          margin-bottom: 8px;
          transition: transform 0.3s ease;
        }

        .step-building.clickable:hover {
          transform: scale(1.3);
          filter: brightness(1.2);
          opacity: 1;
        }

        .step-node.current .step-building {
          transform: scale(1.2);
          animation: bounce 2s infinite;
        }

        .step-node.completed .step-building {
          transform: scale(1.1);
          opacity: 1;
          filter: none;
        }

        .step-node.upcoming .step-building {
          opacity: 0.3;
          filter: grayscale(100%);
        }

        .step-indicator {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          font-size: 14px;
          margin-bottom: 8px;
          transition: all 0.3s ease;
        }

        .step-node.completed .step-indicator {
          background: #4CAF50;
          color: white;
          box-shadow: 0 0 0 4px rgba(76, 175, 80, 0.2);
          opacity: 1;
        }

        .step-node.current .step-indicator {
          background: #FF9800;
          color: white;
          box-shadow: 0 0 0 4px rgba(255, 152, 0, 0.2);
          animation: pulse 2s infinite;
          opacity: 1;
        }

        .step-node.upcoming .step-indicator {
          background: rgba(255, 255, 255, 0.3);
          color: rgba(255, 255, 255, 0.7);
          border: 2px solid rgba(255, 255, 255, 0.5);
          opacity: 0.5;
        }

        .step-label {
          font-size: 12px;
          font-weight: 500;
          white-space: nowrap;
          opacity: 0.9;
        }

        .road-connection {
          display: flex;
          flex-direction: column;
          align-items: center;
          margin: 0 16px;
        }

        .road-line {
          width: 60px;
          height: 4px;
          border-radius: 2px;
          margin-bottom: 4px;
          transition: all 0.3s ease;
        }

        .road-connection.completed .road-line {
          background: #4CAF50;
          box-shadow: 0 0 8px rgba(76, 175, 80, 0.4);
        }

        .road-connection.incomplete .road-line {
          background: rgba(255, 255, 255, 0.3);
        }

        .road-dots {
          display: flex;
          gap: 8px;
          font-size: 12px;
          opacity: 0.6;
        }

        .goal-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          margin-left: 16px;
        }

        .goal-flag {
          font-size: 40px;
          margin-bottom: 8px;
          transition: all 0.3s ease;
        }

        .goal-flag.reached {
          transform: scale(1.2);
          animation: celebration 1s ease-in-out;
        }

        .goal-flag.unreached {
          opacity: 0.5;
          filter: grayscale(100%);
        }

        .goal-label {
          font-size: 12px;
          font-weight: 500;
          opacity: 0.9;
        }

        @keyframes bounce {
          0%, 20%, 50%, 80%, 100% {
            transform: scale(1.2) translateY(0);
          }
          40% {
            transform: scale(1.2) translateY(-8px);
          }
          60% {
            transform: scale(1.2) translateY(-4px);
          }
        }

        @keyframes pulse {
          0% {
            box-shadow: 0 0 0 4px rgba(255, 152, 0, 0.2);
          }
          50% {
            box-shadow: 0 0 0 8px rgba(255, 152, 0, 0.4);
          }
          100% {
            box-shadow: 0 0 0 4px rgba(255, 152, 0, 0.2);
          }
        }

        @keyframes celebration {
          0%, 100% { transform: scale(1.2) rotate(0deg); }
          25% { transform: scale(1.3) rotate(-5deg); }
          75% { transform: scale(1.3) rotate(5deg); }
        }

        /* Responsive */
        @media (max-width: 768px) {
          .roadmap-track {
            overflow-x: auto;
            justify-content: flex-start;
          }
          
          .step-building {
            font-size: 24px;
          }
          
          .road-connection {
            margin: 0 8px;
          }
          
          .road-line {
            width: 40px;
          }
        }
      `}</style>
    </div>
  );
}

export default ModernRoadMapProgressBar;