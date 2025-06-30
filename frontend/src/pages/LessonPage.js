import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import ModernRoadMapProgressBar from "../components/ModernRoadMapProgressBar";
import lessonSteps from "../data/lessonSteps";
import { completeStepAndCheckMedals, getUserProgress, completeConcept } from "../utils/userProgress";
import AIChatScene from "../components/AIChatScene";
import MCQComponent from "../components/MCQComponent";
import TaskComponent from "../components/TaskComponent";
import ChallengeComponent from "../components/ChallengeComponent";
import robotIdle from "../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_idle.png";
import XPAnimation from "../components/XPAnimation";
import { auth } from "../firestoreSetUp/firebaseSetup";
import {
  fetchLessonStepContent,
  fetchMCQData,
  fetchStep3TaskData,
  submitStep3Solution,
  fetchStep4ChallengeData,
  fetchStep5Poem,
} from "../utils/lessonContent";

function LessonPage() {
  const user = auth.currentUser;
  const navigate = useNavigate();
  const location = useLocation();
  const conceptId = location.state?.conceptId;
  const concept = location.state?.concept || "INNER JOIN";

  // Data state
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dynamicContent, setDynamicContent] = useState({
    message: "",
    mcqData: null,
    taskData: null,
    challengeData: null,
    poem: null,
  });

  // UI/Interaction state
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [userQuery, setUserQuery] = useState("");
  const [userExplanation, setUserExplanation] = useState("");
  const [xpGain, setXpGain] = useState(0);
  const [showXpGain, setShowXpGain] = useState(false);
  const [showMedalPopup, setShowMedalPopup] = useState(false);
  const [earnedMedal, setEarnedMedal] = useState(null);

  // Derived from props/state
  const startFromIndex = location.state?.startFromIndex ?? 0;
  const [stepIndex, setStepIndex] = useState(Math.min(Math.max(startFromIndex, 0), lessonSteps.length - 1));
  const currentStep = lessonSteps[stepIndex];

  // Effect to fetch initial user progress
  useEffect(() => {
    if (user) {
      getUserProgress(user.uid)
        .then(userProgress => {
          setProgress(userProgress || { xp: 0, stepsCompleted: [], medals: [] });
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false); // No user, stop loading
    }
  }, [user]);

  // Effect to load content for the current step
  useEffect(() => {
    if (loading || !currentStep) return; // Don't fetch content until progress is loaded

    const loadContent = async () => {
      setIsProcessing(true);
      const newContent = { message: currentStep.description, mcqData: null, taskData: null, challengeData: null, poem: null };
      try {
        if (currentStep.id === "concept-intro") {
          newContent.message = await fetchLessonStepContent(concept, currentStep.id);
        } else if (currentStep.id === "mcq-predict") {
          const data = await fetchMCQData(concept);
          newContent.mcqData = data.question_data;
        } else if (currentStep.id === "user-query") {
          const data = await fetchStep3TaskData(concept);
          newContent.taskData = data.task_data;
        } else if (currentStep.id === "guided-practice") {
          const data = await fetchStep4ChallengeData(user.uid);
          newContent.challengeData = data.challenge_data;
          newContent.message = data.challenge_data.description;
        } else if (currentStep.id === "reflection-poem") {
          const data = await fetchStep5Poem(user.uid, concept);
          newContent.poem = data.poem;
        } else {
          newContent.message = `${currentStep.title}\n\n${currentStep.description}`;
        }
      } catch (error) {
        console.error(`Failed to load content for step ${currentStep.id}:`, error);
      } finally {
        setDynamicContent(newContent);
        setIsProcessing(false);
      }
    };
    loadContent();
  }, [stepIndex, currentStep, user, concept, loading]);
  
  // Effect to reset user input when step changes
  useEffect(() => {
    setSelectedAnswer(null);
    setUserQuery("");
    setUserExplanation("");
  }, [stepIndex]);


  const handleNext = async () => {
    if (isProcessing) return;

    let xpFromStep = currentStep.xp; // Default XP

    if (currentStep.id === "mcq-predict") {
      if (!selectedAnswer) return alert("Please select an answer!");
      const isCorrect = selectedAnswer === dynamicContent.mcqData.correct;
      alert(`You selected ${selectedAnswer}. That is ${isCorrect ? 'Correct!' : 'Incorrect.'}`);
      if (!isCorrect) return;
    }

    if (currentStep.id === "user-query") {
      if (!userQuery.trim() || !userExplanation.trim()) return alert("Please write a query and an explanation!");
      setIsProcessing(true);
      try {
        const result = await submitStep3Solution(user.uid, userQuery, userExplanation);
        alert(`Your submission received a score of ${result.score}.\nFeedback: ${result.feedback}`);
        xpFromStep = result.score; // Override XP with the score from backend
      } catch (error) {
        alert(`Error: ${error.message}`);
        setIsProcessing(false);
        return;
      }
    }

    setIsProcessing(true);
    try {
      const result = await completeStepAndCheckMedals(user.uid, currentStep.id, xpFromStep, lessonSteps, progress, conceptId);
      if (!result.isStepAlreadyCompleted) {
        setProgress(result.newProgress);
        setXpGain(xpFromStep); // Use the (potentially overridden) XP for animation
        setShowXpGain(true);
        setTimeout(() => setShowXpGain(false), 1500);
      }
      if (result.medalEarned) {
        setEarnedMedal(result.medalEarned);
        setShowMedalPopup(true);
      }
      if (stepIndex >= lessonSteps.length - 1) {
        await completeConcept(user.uid, conceptId);
        setTimeout(() => navigate("/"), result.medalEarned ? 3000 : 1000);
      } else {
        setStepIndex(s => s + 1);
      }
    } catch (error) {
      alert("There was an error saving your progress.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleBack = () => !isProcessing && stepIndex > 0 && setStepIndex(s => s - 1);
  const handleBackToOverview = () => navigate("/");
  const handleMedalPopupClose = () => setShowMedalPopup(false);

  if (loading) {
    return <div style={{height: "100vh", display: "flex", justifyContent: "center", alignItems: "center"}}>Loading Lesson...</div>;
  }
  
  const { stepsCompleted = [], xp = 0 } = progress;
  const completedLessons = Math.min(stepsCompleted.length, lessonSteps.length);

  return (
    <div style={{ padding: 32, position: "relative" }}>
      <h2>Lesson: {concept}</h2>
      <ModernRoadMapProgressBar
        totalSteps={lessonSteps.length}
        currentStep={completedLessons}
        completedSteps={stepsCompleted.map(id => lessonSteps.findIndex(step => step.id === id))}
        viewingStep={stepIndex}
        onLessonClick={(index) => setStepIndex(index)}
      />

      {/* Render Area */}
      {currentStep.id === 'mcq-predict' && dynamicContent.mcqData ? (
        <MCQComponent data={dynamicContent.mcqData} selectedAnswer={selectedAnswer} onSelectAnswer={setSelectedAnswer} />
      ) : currentStep.id === 'user-query' && dynamicContent.taskData ? (
        <TaskComponent data={dynamicContent.taskData} userQuery={userQuery} setUserQuery={setUserQuery} userExplanation={userExplanation} setUserExplanation={setUserExplanation} />
      ) : currentStep.id === 'guided-practice' && dynamicContent.challengeData ? (
        <ChallengeComponent data={dynamicContent.challengeData} />
      ) : currentStep.id === 'reflection-poem' && dynamicContent.poem ? (
        <div style={{ padding: '24px', textAlign: 'center', fontFamily: 'serif', fontSize: '1.2em', lineHeight: '1.6' }}>
          <p style={{ whiteSpace: 'pre-wrap' }}>{dynamicContent.poem}</p>
        </div>
      ) : (
        <AIChatScene pose={robotIdle} animation="bounce" user={user} initialMessage={dynamicContent.message} showInput={currentStep.id !== "concept-intro"} />
      )}

      <div style={{ marginTop: 20, display: "flex", gap: "10px" }}>
        <button onClick={handleNext} disabled={isProcessing}>
          {isProcessing ? "Processing..." : (stepIndex === lessonSteps.length - 1 ? "Complete Lesson" : "Next")}
        </button>

        {stepIndex > 0 && (
          <button onClick={handleBack} disabled={isProcessing}>
            Back
          </button>
        )}

        <button onClick={handleBackToOverview}>
          Back to Overview
        </button>
      </div>

      <div style={{ marginTop: 16, padding: 12, background: "#f0f8ff", borderRadius: 4, position: "relative" }}>
        <XPAnimation amount={xpGain} show={showXpGain} />
      </div>
    </div>
  );
}

export default LessonPage;