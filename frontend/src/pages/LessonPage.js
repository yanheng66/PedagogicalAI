import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import StepProgressBar from "../components/StepProgressBar";
import lessonSteps from "../data/lessonSteps";
import { updateUserXP, logStepCompleted } from "../utils/userProgress";
import AIChatScene from "../components/AIChatScene";
import robotIdle from "../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_idle.png";
import robotTalk from "../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_talk.png";

function LessonPage({ user, progress }) {
  const navigate = useNavigate();
  const [pose, setPose] = useState(robotIdle);
  const [animation, setAnimation] = useState("bounce");

  const [stepsCompleted, setStepsCompleted] = useState(
    progress.stepsCompleted || []
  );
  const completedSteps = progress.stepsCompleted || [];
  const completedSet = new Set(completedSteps);

  // Find first step that is NOT completed
  const firstIncompleteIndex = lessonSteps.findIndex(
    (step) => !completedSet.has(step.id)
  );

  // If all steps are done, default to step 0 (or show summary later)
  const startingIndex = firstIncompleteIndex === -1 ? 0 : firstIncompleteIndex;

  const [stepIndex, setStepIndex] = useState(startingIndex);

  const [xp, setXp] = useState(progress.xp);

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

  return (
    <div style={{ padding: 32 }}>
      <h2>Lesson: INNER JOIN</h2>

      <StepProgressBar
        stepsCompleted={stepsCompleted.length}
        totalSteps={lessonSteps.length}
      />
      <AIChatScene
        pose={pose}
        animation={animation}
        message={`Step ${stepIndex + 1}: ${currentStep.title}\n\n${
          currentStep.description
        }`}
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
