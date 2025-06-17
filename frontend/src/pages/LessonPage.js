import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import ModernRoadMapProgressBar from "../components/ModernRoadMapProgressBar";
import lessonSteps from "../data/lessonSteps";
import { completeStepAndCheckMedals } from "../utils/userProgress";
import AIChatScene from "../components/AIChatScene";
import robotIdle from "../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_idle.png";
import robotTalk from "../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_talk.png";

function LessonPage({ user, progress }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [pose, setPose] = useState(robotIdle);
  const [animation, setAnimation] = useState("bounce");
  const [isProcessing, setIsProcessing] = useState(false);
  const [showMedalPopup, setShowMedalPopup] = useState(false);
  const [earnedMedal, setEarnedMedal] = useState(null);

  const [stepsCompleted, setStepsCompleted] = useState(
    progress.stepsCompleted || []
  );
  const completedSteps = progress.stepsCompleted || [];
  const completedSet = new Set(completedSteps);

  // Get the starting index from navigation state, or find first incomplete step
  const startFromIndex = location.state?.startFromIndex ?? 0;
  
  // Ensure the index is within bounds and valid
  const validIndex = Math.min(Math.max(startFromIndex, 0), lessonSteps.length - 1);
  const [stepIndex, setStepIndex] = useState(validIndex);

  const [xp, setXp] = useState(progress.xp);

  // Ensure currentStep is always defined
  const currentStep = lessonSteps[stepIndex];

  const isFirstStep = stepIndex === 0;
  const isLastStep = stepIndex === lessonSteps.length - 1;

  // Calculate completed lessons for roadmap display
  const completedLessons = Math.min(stepsCompleted.length, lessonSteps.length);

  const handleNext = async () => {
    if (isProcessing) return; // Prevent double-clicks
    
    setIsProcessing(true);

    try {
      // Complete the step and check for medals
      const result = await completeStepAndCheckMedals(
        user.uid, 
        currentStep.id, 
        currentStep.xp, 
        lessonSteps
      );

      // Update local state with new progress
      if (!result.isStepAlreadyCompleted) {
        setStepsCompleted(result.newProgress.stepsCompleted);
        setXp(result.newProgress.xp);
      }

      // Show medal popup if earned
      if (result.medalEarned) {
        setEarnedMedal(result.medalEarned);
        setShowMedalPopup(true);
      }

      // Move to next step if not the last step
      if (!isLastStep) {
        setStepIndex(stepIndex + 1);
      } else {
        // Last step completed - could navigate to summary or home
        console.log("All lessons completed!");
        // Optionally navigate back to home after a delay
        setTimeout(() => {
          navigate("/");
        }, result.medalEarned ? 3000 : 1000); // Wait longer if medal was earned
      }

    } catch (error) {
      console.error("Error completing step:", error);
      alert("There was an error saving your progress. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleBack = () => {
    if (!isFirstStep) {
      setStepIndex(stepIndex - 1);
    }
  };

  const handleBackToOverview = () => {
    navigate("/");
  };

  const handleMedalPopupClose = () => {
    setShowMedalPopup(false);
    setEarnedMedal(null);
  };

  // If we somehow have an invalid step, redirect to home
  useEffect(() => {
    if (!currentStep) {
      navigate("/");
    }
  }, [currentStep, navigate]);

  // Don't render anything if we don't have a valid step
  if (!currentStep) {
    return null;
  }

  return (
    <div style={{ padding: 32 }}>
      <h2>Lesson: INNER JOIN</h2>

      <ModernRoadMapProgressBar
        totalSteps={lessonSteps.length}
        currentStep={completedLessons}
        completedSteps={stepsCompleted.map(id => lessonSteps.findIndex(step => step.id === id))}
        viewingStep={stepIndex}
        onLessonClick={(index) => {
          setStepIndex(index);
        }}
      />

      <AIChatScene
        pose={pose}
        animation={animation}
        message={`${currentStep.title}\n\n${currentStep.description}`}
        onUserInput={(text) => {
          console.log("User input:", text);

          // Animate robot and switch pose briefly
          setPose(robotTalk);
          setAnimation("pulse");

          // Reset to idle after 1.5s
          setTimeout(() => {
            setPose(robotIdle);
            setAnimation("bounce");
          }, 1500);
        }}
      />

      <div style={{ marginTop: 20, display: "flex", gap: "10px" }}>
        <button 
          onClick={handleNext}
          disabled={isProcessing}
          style={{
            padding: "12px 24px",
            fontSize: 16,
            background: isProcessing ? "#ccc" : "#4CAF50",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: isProcessing ? "not-allowed" : "pointer",
          }}
        >
          {isProcessing ? "Processing..." : (isLastStep ? "Complete Lesson" : "Next")}
        </button>

        {!isFirstStep && (
          <button 
            onClick={handleBack}
            disabled={isProcessing}
            style={{
              padding: "12px 24px",
              fontSize: 16,
              background: "#2196F3",
              color: "white",
              border: "none",
              borderRadius: 4,
              cursor: isProcessing ? "not-allowed" : "pointer",
            }}
          >
            Back
          </button>
        )}

        <button 
          onClick={handleBackToOverview}
          style={{
            padding: "12px 24px",
            fontSize: 16,
            background: "#fff",
            color: "#666",
            border: "1px solid #ddd",
            borderRadius: 4,
            cursor: "pointer",
          }}
        >
          Back to Lesson Overview
        </button>
      </div>

      <div style={{ marginTop: 16, padding: 12, background: "#f0f8ff", borderRadius: 4 }}>
        <small>
          Progress: {stepsCompleted.length}/{lessonSteps.length} lessons completed | XP: {xp}
        </small>
      </div>

      {/* Medal Earned Popup */}
      {showMedalPopup && earnedMedal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '40px',
            borderRadius: '16px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
            maxWidth: '400px',
            width: '90%',
            textAlign: 'center',
            background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
            border: '3px solid #FFD700'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🎉</div>
            <h2 style={{ 
              marginTop: 0, 
              marginBottom: '16px',
              color: '#8B4513',
              textShadow: '1px 1px 2px rgba(255,255,255,0.8)'
            }}>
              Congratulations!
            </h2>
            <img 
              src={earnedMedal.image} 
              alt={earnedMedal.name}
              style={{
                width: '120px',
                height: '120px',
                objectFit: 'contain',
                marginBottom: '16px',
                filter: 'drop-shadow(0 4px 8px rgba(0,0,0,0.3))'
              }}
            />
            <h3 style={{ 
              color: '#8B4513',
              marginBottom: '8px',
              fontSize: '24px'
            }}>
              {earnedMedal.name}
            </h3>
            <p style={{ 
              color: '#8B4513',
              marginBottom: '24px',
              fontSize: '16px'
            }}>
              {earnedMedal.description}
            </p>
            <button 
              onClick={handleMedalPopupClose}
              style={{
                backgroundColor: '#8B4513',
                color: 'white',
                border: 'none',
                padding: '12px 24px',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: 'bold'
              }}
            >
              Awesome! 🏆
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default LessonPage;