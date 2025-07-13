import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import ModernRoadMapProgressBar from "../components/ModernRoadMapProgressBar";
import lessonSteps from "../data/lessonSteps";
import { completeStepAndCheckMedals, getUserProgress, completeConcept } from "../utils/userProgress";
import AIChatScene from "../components/AIChatScene";
import Step1Component from "../components/Step1Component";
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
  fetchStep3Hint,
  fetchStep3Retry,
  fetchStep4ChallengeData,
  fetchStep5Poem,
} from "../utils/lessonContent";

// FastAPI服务器地址
const FASTAPI_BASE_URL = 'http://localhost:8000';

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
    poem: null,
  });

  // Step 1 specific state
  const [step1State, setStep1State] = useState({
    analogy: "",
    regenerationCount: 0,
    isLoading: false,
    canProceed: false
  });

  // UI/Interaction state
  const [isProcessing, setIsProcessing] = useState(false);
  const [userQuery, setUserQuery] = useState("");
  const [userExplanation, setUserExplanation] = useState("");
  const [xpGain, setXpGain] = useState(0);
  const [showXpGain, setShowXpGain] = useState(false);
  const [showMedalPopup, setShowMedalPopup] = useState(false);
  const [earnedMedal, setEarnedMedal] = useState(null);

  // Step 3 specific state
  const [step3HintCount, setStep3HintCount] = useState(0);
  const [step3Hints, setStep3Hints] = useState([]);
  const [step3Elapsed, setStep3Elapsed] = useState(0);
  const [step3NeedsRetry, setStep3NeedsRetry] = useState(false);
  const [step3Score, setStep3Score] = useState(null);
  const [step3Feedback, setStep3Feedback] = useState("");
  const [step3Submitted, setStep3Submitted] = useState(false);
  const [step3UserId, setStep3UserId] = useState(user?.uid || "guest");

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
      const newContent = { message: currentStep.description, mcqData: null, taskData: null, poem: null };
      try {
        if (currentStep.id === "concept-intro") {
          // Load Step 1 analogy via new API
          const response = await fetch(`${FASTAPI_BASE_URL}/api/step1`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              user_id: user?.uid || 'guest',
              topic: concept
            })
          });
          const data = await response.json();
          setStep1State(prev => ({
            ...prev,
            analogy: data.analogy,
            regenerationCount: data.regeneration_count,
            canProceed: false
          }));
          newContent.message = data.analogy;
        } else if (currentStep.id === "mcq-predict") {
          const data = await fetchMCQData(concept);
          newContent.mcqData = data.question_data;
        } else if (currentStep.id === "user-query") {
          const uidForStep = user?.uid || "guest";
          setStep3UserId(uidForStep);
          const data = await fetchStep3TaskData(uidForStep, concept);
          newContent.taskData = data.task_data;
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
    setUserQuery("");
    setUserExplanation("");
  }, [stepIndex]);

  // Start a timer whenever we enter Step 3 (user-query)
  useEffect(() => {
    if (currentStep.id !== "user-query") return;

    setStep3Elapsed(0);
    const timer = setInterval(() => {
      setStep3Elapsed((t) => t + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [currentStep.id, dynamicContent.taskData]);

  // Step 1 specific handlers
  const handleStep1Understand = async () => {
    setStep1State(prev => ({ ...prev, isLoading: true }));
    
    try {
      const response = await fetch(`${FASTAPI_BASE_URL}/api/step1/confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user?.uid || 'guest',
          understood: true,
          topic: concept
        })
      });
      const data = await response.json();
      
      setStep1State(prev => ({
        ...prev,
        isLoading: false,
        canProceed: data.proceed_to_next
      }));
      
      // Automatically proceed to next step
      if (data.proceed_to_next) {
        setTimeout(() => setStepIndex(s => s + 1), 500);
      }
    } catch (error) {
      console.error('Error confirming understanding:', error);
      setStep1State(prev => ({ ...prev, isLoading: false }));
    }
  };

  const handleStep1Regenerate = async () => {
    setStep1State(prev => ({ ...prev, isLoading: true }));
    
    try {
      const response = await fetch(`${FASTAPI_BASE_URL}/api/step1/confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user?.uid || 'guest',
          understood: false,
          topic: concept
        })
      });
      const data = await response.json();
      
      setStep1State(prev => ({
        ...prev,
        analogy: data.analogy || prev.analogy,
        regenerationCount: data.regeneration_count,
        isLoading: false,
        canProceed: false
      }));
    } catch (error) {
      console.error('Error regenerating analogy:', error);
      setStep1State(prev => ({ ...prev, isLoading: false }));
    }
  };

  // Step 2 specific handler
  const handleStep2Complete = async (isCorrect) => {
    setIsProcessing(true);
    try {
      const xpFromStep = currentStep.xp; // Flat rate scoring
      const result = await completeStepAndCheckMedals(user.uid, currentStep.id, xpFromStep, lessonSteps, progress, conceptId);
      
      if (!result.isStepAlreadyCompleted) {
        setProgress(result.newProgress);
        setXpGain(xpFromStep);
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
      console.error("Error completing step 2:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  // Step 2 new question handler
  const handleStep2NewQuestion = async () => {
    try {
      const data = await fetchMCQData(concept);
      setDynamicContent(prevContent => ({
        ...prevContent,
        mcqData: data.question_data
      }));
    } catch (error) {
      console.error("Error generating new question:", error);
      throw error; // Re-throw to let the component handle the error
    }
  };

  // Step 3: Hint handler
  const handleStep3GetHint = async () => {
    if (isProcessing) return;
    try {
      const res = await fetchStep3Hint(step3UserId, step3HintCount);
      setStep3HintCount(res.hint_count);
      setStep3Hints((h) => [...h, res.hint]);
    } catch (err) {
      console.error("Error getting hint:", err);
    }
  };

  // Step 3: Retry handler
  const handleStep3Retry = async () => {
    if (isProcessing) return;
    setIsProcessing(true);
    try {
      const res = await fetchStep3Retry(step3UserId, concept);
      setDynamicContent((prev) => ({ ...prev, taskData: res.task_data }));

      // Reset all related states
      setUserQuery("");
      setUserExplanation("");
      setStep3HintCount(0);
      setStep3Hints([]);
      setStep3Elapsed(0);
      setStep3NeedsRetry(true);
      setStep3Submitted(false);
      setStep3Score(null);
      setStep3Feedback("");
    } catch (err) {
      console.error("Error retrying Step 3:", err);
    } finally {
      setIsProcessing(false);
    }
  };

  // Step 3: Submit handler
  const handleStep3Submit = async () => {
    if (isProcessing) return;

    if (!userQuery.trim() || !userExplanation.trim()) {
      alert("Please write a query and an explanation!");
      return;
    }

    setIsProcessing(true);
    try {
      const result = await submitStep3Solution(
        step3UserId,
        userQuery,
        userExplanation,
        step3Elapsed,
        step3HintCount
      );

      setStep3Feedback(result.feedback);
      setStep3Score(result.score);
      setStep3NeedsRetry(result.needs_retry);
      setStep3Submitted(true);

      // When needs_retry is false, enable Go to Step 4 button but DO NOT auto-advance.

    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Step 4 specific handler
  const handleStep4Complete = async (scoreFromChallenge = null) => {
    setIsProcessing(true);
    try {
      // Use score from Step 4 challenge if available, otherwise use default XP
      const xpFromStep = scoreFromChallenge !== null ? scoreFromChallenge : currentStep.xp;
      
      // Debug logging for XP integration
      console.log('[LessonPage] Step 4 complete:', {
        scoreFromChallenge,
        defaultXP: currentStep.xp,
        xpToAward: xpFromStep
      });
      const result = await completeStepAndCheckMedals(user.uid, currentStep.id, xpFromStep, lessonSteps, progress, conceptId);
      
      if (!result.isStepAlreadyCompleted) {
        setProgress(result.newProgress);
        setXpGain(xpFromStep);
        setShowXpGain(true);
        setTimeout(() => setShowXpGain(false), 1500);
        
        // Debug logging for Step 4 XP animation
        console.log('[LessonPage] Step 4 XP animation triggered:', {
          xpGain: xpFromStep,
          showXpGain: true
        });
      } else {
        console.log('[LessonPage] Step 4 already completed, skipping XP animation');
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
      console.error("Error completing step 4:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleNext = async () => {
    if (isProcessing) return;

    // Skip traditional next for Step 1, Step 2, and Step 4 - they handle their own progression
    if (currentStep.id === "concept-intro" || currentStep.id === "mcq-predict" || currentStep.id === "guided-practice") {
      return;
    }

    let xpFromStep = currentStep.xp; // Default XP

    if (currentStep.id === "user-query") {
      if (!userQuery.trim() || !userExplanation.trim()) return alert("Please write a query and an explanation!");
      setIsProcessing(true);
      try {
        const result = await submitStep3Solution(
          step3UserId,
          userQuery,
          userExplanation,
          step3Elapsed,
          step3HintCount
        );

        setStep3Feedback(result.feedback);
        setStep3Score(result.score);
        setStep3NeedsRetry(result.needs_retry);

        if (result.needs_retry) {
          // Do not proceed, allow retry
          setIsProcessing(false);
          return;
        }

        xpFromStep = result.score; // Override XP if no retry needed
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

  if (loading || (isProcessing && !dynamicContent.mcqData && !dynamicContent.taskData)) {
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
      {currentStep.id === 'concept-intro' ? (
        <Step1Component
          key={step1State.regenerationCount}
          initialMessage={step1State.analogy}
          onUnderstand={handleStep1Understand}
          onRegenerate={handleStep1Regenerate}
          isLoading={step1State.isLoading}
          regenerationCount={step1State.regenerationCount}
        />
      ) : currentStep.id === 'mcq-predict' ? (
        dynamicContent.mcqData ? (
          <MCQComponent 
            data={dynamicContent.mcqData} 
            user={user}
            onStepComplete={handleStep2Complete}
            onNewQuestion={handleStep2NewQuestion}
          />
        ) : (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <p>Loading MCQ challenge...</p>
          </div>
        )
      ) : currentStep.id === 'user-query' && dynamicContent.taskData ? (
        <TaskComponent
          data={dynamicContent.taskData}
          user={user}
          userQuery={userQuery}
          setUserQuery={setUserQuery}
          userExplanation={userExplanation}
          setUserExplanation={setUserExplanation}
          hintCount={step3HintCount}
          hints={step3Hints}
          onGetHint={handleStep3GetHint}
          onRetry={handleStep3Retry}
          onSubmit={handleStep3Submit}
          needsRetry={step3NeedsRetry}
          submitted={step3Submitted}
          score={step3Score}
          feedback={step3Feedback}
          isProcessing={isProcessing}
        />
      ) : currentStep.id === 'guided-practice' ? (
        <ChallengeComponent 
          userId={user?.uid || 'guest'} 
          onComplete={handleStep4Complete}
          concept={concept}
          conceptId={conceptId}
        />
      ) : currentStep.id === 'reflection-poem' && dynamicContent.poem ? (
        <div style={{ padding: '24px', textAlign: 'center', fontFamily: 'serif', fontSize: '1.2em', lineHeight: '1.6' }}>
          <p style={{ whiteSpace: 'pre-wrap' }}>{dynamicContent.poem}</p>
        </div>
      ) : (
        <AIChatScene pose={robotIdle} animation="bounce" user={user} initialMessage={dynamicContent.message} showInput={currentStep.id !== "concept-intro"} />
      )}

      <div style={{ marginTop: 20, display: "flex", gap: "10px" }}>
        {/* Only show Next button for steps that don't handle their own progression */}
        {currentStep.id !== "concept-intro" && currentStep.id !== "mcq-predict" && currentStep.id !== "guided-practice" && currentStep.id !== "user-query" && (
          <button onClick={handleNext} disabled={isProcessing}>
            {isProcessing ? "Processing..." : (stepIndex === lessonSteps.length - 1 ? "Complete Lesson" : "Next")}
          </button>
        )}

        {stepIndex > 0 && (
          <button onClick={handleBack} disabled={isProcessing}>
            Back
          </button>
        )}

        <button onClick={handleBackToOverview}>
          Back to Overview
        </button>
      </div>

      {/* Step 3 navigation */}
      {currentStep.id === "user-query" && step3Submitted && !step3NeedsRetry && (
        <button onClick={() => setStepIndex(s => s + 1)} disabled={isProcessing}>
          Go to Step 4
        </button>
      )}

      <div style={{ marginTop: 16, padding: 12, background: "#f0f8ff", borderRadius: 4, position: "relative" }}>
        <XPAnimation amount={xpGain} show={showXpGain} />
      </div>
    </div>
  );
}

export default LessonPage;