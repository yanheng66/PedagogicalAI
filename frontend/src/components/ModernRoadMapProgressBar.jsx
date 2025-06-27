import React from 'react';

function ModernRoadMapProgressBar({ totalSteps = 5, currentStep = 0, onLessonClick, completedSteps = [], viewingStep }) {
  const steps = Array.from({ length: totalSteps }, (_, i) => i);
  
  const getStepStatus = (stepIndex) => {
    // Check if this specific step is completed based on completedSteps array
    const isCompleted = completedSteps.includes(stepIndex);
    
    if (isCompleted) return 'completed';
    if (stepIndex === viewingStep) return 'viewing'; // Currently viewing this step
    if (stepIndex <= currentStep) return 'current'; // Available to access
    return 'upcoming';
  };

  const handleStepClick = (stepIndex) => {
    const status = getStepStatus(stepIndex);
    // Allow clicking on completed lessons and available lessons
    if (status === 'completed' || status === 'current' || status === 'viewing') {
      onLessonClick?.(stepIndex);
    }
  };

  const getStepIcon = (stepIndex, status) => {
    if (status === 'completed') return '✓';
    if (status === 'viewing') return '👁️'; // Eye icon for currently viewing
    if (status === 'current') return '🎯';
    return stepIndex + 1;
  };

  const getBuildingEmoji = (stepIndex) => {
    const buildings = ['🏠', '🏪', '🏢', '🏛️', '🏰', '🕌', '🗼'];
    return buildings[stepIndex % buildings.length];
  };

  return (
    <div className="roadmap-container">
      <div className="roadmap-header">
        <h3>Learning Journey</h3>
        <p>
          {viewingStep !== undefined 
            ? `Viewing Lesson ${viewingStep + 1} of ${totalSteps}` 
            : `Progress: ${Math.min(currentStep, totalSteps)} of ${totalSteps} completed`
          }
        </p>
      </div>
      
      <div className="roadmap-track">
        {steps.map((stepIndex, index) => {
          const status = getStepStatus(stepIndex);
          const isLastStep = index === steps.length - 1;
          
          return (
            <div key={stepIndex} className="step-container">
              {/* Step Node */}
              <div 
                className={`step-node ${status}`}
                onClick={() => handleStepClick(stepIndex)}
                style={{ 
                  cursor: (status === 'completed' || status === 'current' || status === 'viewing') ? 'pointer' : 'not-allowed' 
                }}
              >
                <div className="step-building">
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

        .step-node.current .step-building {
          transform: scale(1.2);
          animation: bounce 2s infinite;
        }

        .step-node.viewing .step-building {
          transform: scale(1.15);
          filter: brightness(1.2);
          animation: viewingPulse 3s infinite;
        }

        .step-node.completed .step-building {
          transform: scale(1.1);
        }

        .step-node.upcoming .step-building {
          opacity: 0.5;
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
        }

        .step-node.current .step-indicator {
          background: #FF9800;
          color: white;
          box-shadow: 0 0 0 4px rgba(255, 152, 0, 0.2);
          animation: pulse 2s infinite;
        }

        .step-node.viewing .step-indicator {
          background: #2196F3;
          color: white;
          box-shadow: 0 0 0 4px rgba(33, 150, 243, 0.2);
          animation: viewingIndicator 2s infinite;
        }

        .step-node.upcoming .step-indicator {
          background: rgba(255, 255, 255, 0.3);
          color: rgba(255, 255, 255, 0.7);
          border: 2px solid rgba(255, 255, 255, 0.5);
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

        @keyframes viewingPulse {
          0%, 100% { 
            transform: scale(1.15);
            filter: brightness(1.2);
          }
          50% { 
            transform: scale(1.25);
            filter: brightness(1.4);
          }
        }

        @keyframes viewingIndicator {
          0% {
            box-shadow: 0 0 0 4px rgba(33, 150, 243, 0.2);
          }
          50% {
            box-shadow: 0 0 0 8px rgba(33, 150, 243, 0.4);
          }
          100% {
            box-shadow: 0 0 0 4px rgba(33, 150, 243, 0.2);
          }
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