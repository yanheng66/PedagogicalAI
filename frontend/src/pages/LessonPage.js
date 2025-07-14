import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import ModernRoadMapProgressBar from "../components/ModernRoadMapProgressBar";
import lessonSteps from "../data/lessonSteps";
import { completeStepAndCheckMedals, getUserProgress, completeConcept, recordStepProgress, getConceptStepProgress } from "../utils/userProgress";
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

  // Debug state for progress system
  const [debugMode] = useState(process.env.NODE_ENV === 'development');

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

  // Progress warning state
  const [hasUnsavedProgress, setHasUnsavedProgress] = useState(false);
  const [showExitConfirm, setShowExitConfirm] = useState(false);

  // Derived from props/state - Always start from step 0 unless unit is completed
  const [stepIndex, setStepIndex] = useState(0);
  const [completedStepsInConcept, setCompletedStepsInConcept] = useState([]); // 存储当前概念中已完成的步骤
  const currentStep = lessonSteps[stepIndex];

  // Effect to fetch initial user progress
  useEffect(() => {
    if (user) {
      Promise.all([
        getUserProgress(user.uid),
        getConceptStepProgress(user.uid, conceptId)
      ])
        .then(([userProgress, conceptSteps]) => {
          const progress = userProgress || { xp: 0, stepsCompleted: [], medals: [], completedConcepts: [] };
          
          // 设置已完成的步骤
          setCompletedStepsInConcept(conceptSteps);
          
          // Check if this concept/unit is already completed
          const isUnitCompleted = progress.completedConcepts?.includes(conceptId);
          
          if (isUnitCompleted) {
            // If unit is completed, user can view but with no new progress tracking
            setProgress({ xp: 0, stepsCompleted: [], medals: progress.medals, completedConcepts: progress.completedConcepts });
            setHasUnsavedProgress(false);
          } else {
            // Fresh start for this unit
            setProgress({ xp: 0, stepsCompleted: [], medals: progress.medals, completedConcepts: progress.completedConcepts });
            setHasUnsavedProgress(false);
          }
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false); // No user, stop loading
    }
  }, [user, conceptId]);

  // Effect to handle page leave warning
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (hasUnsavedProgress) {
        e.preventDefault();
        e.returnValue = ''; // Modern browsers ignore custom messages
        return '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [hasUnsavedProgress]);

  // Effect to track unsaved progress
  useEffect(() => {
    // Set unsaved progress when user starts working on any step
    if (stepIndex > 0 || userQuery.trim() || userExplanation.trim()) {
      setHasUnsavedProgress(true);
    }
  }, [stepIndex, userQuery, userExplanation]);

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

  // Helper function to record step completion
  const recordStepCompletion = async (stepIdx) => {
    if (user?.uid && conceptId) {
      try {
        await recordStepProgress(user.uid, conceptId, stepIdx);
        // 更新本地状态
        setCompletedStepsInConcept(prev => {
          if (!prev.includes(stepIdx)) {
            return [...prev, stepIdx].sort((a, b) => a - b);
          }
          return prev;
        });
      } catch (error) {
        console.error('Error recording step progress:', error);
      }
    }
  };

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
        // Award XP for completing Step 1 (temporary, not saved to profile)
        const xpFromStep = currentStep.xp;
        setProgress(prev => ({
          ...prev,
          xp: (prev?.xp || 0) + xpFromStep
        }));
        setXpGain(xpFromStep);
        setShowXpGain(true);
        setTimeout(() => setShowXpGain(false), 1500);
        
        // 记录步骤完成
        await recordStepCompletion(stepIndex);
        
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
      // Award fixed XP only if answer is correct (temporary, not saved to profile)
      const xpFromStep = isCorrect ? currentStep.xp : 0;
      setProgress(prev => ({
        ...prev,
        xp: (prev?.xp || 0) + xpFromStep
      }));
      
      if (xpFromStep > 0) {
        setXpGain(xpFromStep);
        setShowXpGain(true);
        setTimeout(() => setShowXpGain(false), 1500);
      }
      
      if (stepIndex >= lessonSteps.length - 1) {
        // This shouldn't happen as Step 2 is not the last step
        setTimeout(() => navigate("/"), 1000);
      } else {
        // 记录步骤完成
        await recordStepCompletion(stepIndex);
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
  const handleStep4Complete = async (passedChallenge = null) => {
    setIsProcessing(true);
    try {
      // Award fixed XP only if challenge was passed (temporary, not saved to profile)
      const xpFromStep = passedChallenge ? currentStep.xp : 0;
      
      // Debug logging for XP integration
      console.log('[LessonPage] Step 4 complete:', {
        passedChallenge,
        fixedXP: currentStep.xp,
        xpToAward: xpFromStep
      });
      
      setProgress(prev => ({
        ...prev,
        xp: (prev?.xp || 0) + xpFromStep
      }));
      
      if (xpFromStep > 0) {
        setXpGain(xpFromStep);
        setShowXpGain(true);
        setTimeout(() => setShowXpGain(false), 1500);
        
        // Debug logging for Step 4 XP animation
        console.log('[LessonPage] Step 4 XP animation triggered:', {
          xpGain: xpFromStep,
          showXpGain: true
        });
      }
      
      if (stepIndex >= lessonSteps.length - 1) {
        // This shouldn't happen as Step 4 is not the last step
        setTimeout(() => navigate("/"), 1000);
      } else {
        // 记录步骤完成
        await recordStepCompletion(stepIndex);
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

        // If passed (no retry needed), award fixed XP
        xpFromStep = currentStep.xp;
      } catch (error) {
        alert(`Error: ${error.message}`);
        setIsProcessing(false);
        return;
      }
    }

    setIsProcessing(true);
    try {
      // For Step 5 (reflection-poem), save the complete unit progress
      if (stepIndex >= lessonSteps.length - 1) {
        // This is the final step - save actual progress to profile
        const totalUnitXP = progress.xp; // All accumulated XP from this unit
        const result = await completeStepAndCheckMedals(user.uid, `unit-${conceptId}`, totalUnitXP, lessonSteps, progress, conceptId);
        
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
        
        await completeConcept(user.uid, conceptId);
        setHasUnsavedProgress(false); // Clear unsaved progress flag
        setTimeout(() => navigate("/"), result.medalEarned ? 3000 : 1000);
      } else {
        // For other steps (Step 5), just award temporary XP and continue
        setProgress(prev => ({
          ...prev,
          xp: (prev?.xp || 0) + xpFromStep
        }));
        
        if (xpFromStep > 0) {
          setXpGain(xpFromStep);
          setShowXpGain(true);
          setTimeout(() => setShowXpGain(false), 1500);
        }
        
        // 记录步骤完成
        await recordStepCompletion(stepIndex);
        setStepIndex(s => s + 1);
      }
    } catch (error) {
      alert("There was an error saving your progress.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleBack = () => !isProcessing && stepIndex > 0 && setStepIndex(s => s - 1);
  
  const handleBackToOverview = () => {
    if (hasUnsavedProgress) {
      setShowExitConfirm(true);
    } else {
      navigate("/");
    }
  };

  const handleConfirmExit = () => {
    setHasUnsavedProgress(false);
    setShowExitConfirm(false);
    navigate("/");
  };

  const handleCancelExit = () => {
    setShowExitConfirm(false);
  };

  const handleMedalPopupClose = () => setShowMedalPopup(false);

  if (loading || (isProcessing && !dynamicContent.mcqData && !dynamicContent.taskData)) {
    return <div style={{height: "100vh", display: "flex", justifyContent: "center", alignItems: "center"}}>Loading Lesson...</div>;
  }
  
  // progress.xp 若需展示可直接引用，此处不再解构。

  return (
    <div style={{ padding: 32, position: "relative" }}>
      <h2>Lesson: {concept}</h2>
      
      {/* Debug information for development */}
      {debugMode && (
        <div style={{
          backgroundColor: '#f0f0f0',
          padding: '10px',
          marginBottom: '20px',
          borderRadius: '5px',
          fontSize: '12px',
          fontFamily: 'monospace'
        }}>
          <strong>Debug Info:</strong><br/>
          Step: {stepIndex + 1}/{lessonSteps.length} ({currentStep?.id})<br/>
          Unsaved Progress: {hasUnsavedProgress ? 'Yes' : 'No'}<br/>
          Current XP (temp): {progress?.xp || 0}<br/>
          Completed Concepts: {progress?.completedConcepts?.join(', ') || 'None'}<br/>
          Unit Completed: {progress?.completedConcepts?.includes(conceptId) ? 'Yes' : 'No'}
        </div>
      )}
      {/*
        进度条应允许用户在当前会话中回到已浏览过的任何步骤。但数据库中只记录单元级进度，
        因此这里直接根据 stepIndex 推断「已完成」的步骤，而不依赖 progress.stepsCompleted。
        这样可以保证：
        1. 当前步骤之前的所有步骤都被视为 completed ⇒ 图标变绿、可点击。
        2. 当前步骤本身标记为 viewing。
        3. 下一步（current）以及其后的步骤保持锁定状态，与原有逻辑一致。
      */}
      <ModernRoadMapProgressBar
        totalSteps={lessonSteps.length}
        completedSteps={completedStepsInConcept}
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
            key={dynamicContent.mcqData?.question_id || Date.now()}
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
          onNextStep={() => setStepIndex(s => s + 1)}
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

      <div style={{ marginTop: 16, padding: 12, background: "#f0f8ff", borderRadius: 4, position: "relative" }}>
        <XPAnimation amount={xpGain} show={showXpGain} />
      </div>

      {/* Exit confirmation modal */}
      {showExitConfirm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '30px',
            borderRadius: '12px',
            maxWidth: '400px',
            textAlign: 'center',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
          }}>
            <h3 style={{ margin: '0 0 15px 0', color: '#d32f2f' }}>⚠️ Unsaved Progress</h3>
            <p style={{ margin: '0 0 25px 0', lineHeight: '1.5' }}>
              Your progress in this lesson will not be saved if you leave now. 
              You'll need to start from the beginning when you return to this unit.
            </p>
            <p style={{ margin: '0 0 25px 0', fontWeight: 'bold', color: '#d32f2f' }}>
              Do you wish to continue?
            </p>
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
              <button 
                onClick={handleConfirmExit}
                style={{
                  backgroundColor: '#d32f2f',
                  color: 'white',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                Yes, I'm leaving
              </button>
              <button 
                onClick={handleCancelExit}
                style={{
                  backgroundColor: '#4caf50',
                  color: 'white',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                No, I'll stay
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default LessonPage;