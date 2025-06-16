import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import ModernRoadMapProgressBar from "../components/ModernRoadMapProgressBar";
import lessonSteps from "../data/lessonSteps";
import { updateUserXP, logStepCompleted } from "../utils/userProgress";
import AIChatScene from "../components/AIChatScene";
import robotIdle from "../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_idle.png";
import robotTalk from "../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_talk.png";

function LessonPage({ user, progress }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [pose, setPose] = useState(robotIdle);
  const [animation, setAnimation] = useState("bounce");

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

  const handleNext = async () => {
    if (!stepsCompleted.includes(currentStep.id)) {
      await updateUserXP(user.uid, currentStep.xp);
      await logStepCompleted(user.uid, currentStep.id);
      setStepsCompleted([...stepsCompleted, currentStep.id]); //update local
      setXp((prev) => prev + currentStep.xp);
    }

    if (!isLastStep) {
      setStepIndex(stepIndex + 1);
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
        currentStep={stepIndex}
        completedSteps={stepsCompleted.map(id => lessonSteps.findIndex(step => step.id === id))}
        onLessonClick={(index) => {
          setStepIndex(index);
        }}
      />

      <AIChatScene
        pose={pose}
        animation={animation}
        message={`Robot: ${currentStep.title}\n\n${currentStep.description}`}
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
        <button onClick={handleNext}>Next</button>

        {!isFirstStep && <button onClick={handleBack}>Back</button>}

        <button onClick={handleBackToOverview}>Back to Lesson Overview</button>
      </div>
    </div>
  );
}

export default LessonPage;
