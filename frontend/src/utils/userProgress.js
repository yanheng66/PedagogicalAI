import { doc, getDoc, setDoc, updateDoc, arrayUnion, arrayRemove } from "firebase/firestore";
import { database } from "../firestoreSetUp/firebaseSetup";
import { getMedalForConcept } from "../data/medals";

export async function getUserProgress(userId) {
  if (!userId) return null;
  const docRef = doc(database, "users", userId, "progress", "main");
  const docSnap = await getDoc(docRef);
  if (docSnap.exists()) {
    // Ensure `completedConcepts` exists
    const data = docSnap.data();
    return {
      ...data,
      completedConcepts: data.completedConcepts || [],
      medals: data.medals || [],
    };
  }
  return null;
}

export async function updateUserXP(uid, amount) {
  const ref = doc(database, "users", uid, "progress", "main");
  const snap = await getDoc(ref);
  const currentXP = snap.exists() ? snap.data().xp || 0 : 0;

  await setDoc(ref, {
    xp: currentXP + amount,
    lastUpdated: new Date().toISOString(),
  }, { merge: true });
}

export async function addBadge(uid, badgeName) {
  const ref = doc(database, "users", uid, "progress", "main");
  const snap = await getDoc(ref);
  const currentBadges = snap.exists() ? snap.data().badges || [] : [];

  if (!currentBadges.includes(badgeName)) {
    await updateDoc(ref, {
      badges: [...currentBadges, badgeName],
    });
  }
}

export async function getOrCreateUserProgress(uid) {
    const ref = doc(database, "users", uid, "progress", "main");
    const snap = await getDoc(ref);
  
    if (snap.exists()) {
      return snap.data();
    } else {
      const defaultProgress = {
        xp: 0,
        badges: [],
        stepsCompleted: [],
        medals: [], // Add medals array to user progress
        createdAt: new Date().toISOString(),
      };
      await setDoc(ref, defaultProgress);
      return defaultProgress;
    }
  }

export async function logStepCompleted(uid, stepKey) {
  const ref = doc(database, "users", uid, "progress", "main");
  const snap = await getDoc(ref);
  const steps = snap.exists() ? snap.data().stepsCompleted || [] : [];

  if (!steps.includes(stepKey)) {
    await updateDoc(ref, {
      stepsCompleted: [...steps, stepKey],
      lastUpdated: new Date().toISOString(),
    });
  }
}

/**
 * Complete a lesson step and check for unit completion medals
 * @param {string} userId - User ID
 * @param {string} stepId - Step identifier
 * @param {number} xpGained - XP to award
 * @param {Array} allSteps - All lesson steps to check completion
 * @param {Object} progress - Current user progress
 * @param {string} conceptId - The concept ID associated with the step
 * @returns {Promise<Object>} - Returns { isStepAlreadyCompleted: boolean, newProgress: updatedProgress, medalEarned: medal or null }
 */
export async function completeStepAndCheckMedals(userId, stepId, xpGained, allSteps, progress, conceptId) {
  if (!userId) return { isStepAlreadyCompleted: true, newProgress: progress, medalEarned: null };
  const progressRef = doc(database, "users", userId, "progress", "main");
  
  const currentProgress = progress || (await getUserProgress(userId)) || {
    xp: 0,
    stepsCompleted: [],
    medals: [],
    completedConcepts: [],
  };

  let isStepAlreadyCompleted = currentProgress.stepsCompleted.includes(stepId);
  let newProgress = { ...currentProgress };
  let medalEarned = null;

  if (!isStepAlreadyCompleted) {
    newProgress = {
      ...currentProgress,
      xp: (currentProgress.xp || 0) + xpGained,
      stepsCompleted: [...currentProgress.stepsCompleted, stepId],
    };
    
    // Check if this step completes a concept
    const completedStepsForConcept = allSteps.every(step => newProgress.stepsCompleted.includes(step.id));
    if (completedStepsForConcept) {
      const newMedal = getMedalForConcept(conceptId);
      if (newMedal && !newProgress.medals.some(m => m.id === newMedal.id)) {
        medalEarned = { ...newMedal, dateAwarded: new Date().toISOString() };
        newProgress.medals = [...newProgress.medals, medalEarned];
      }
    }

    await setDoc(progressRef, newProgress, { merge: true });
  }

  return {
    isStepAlreadyCompleted,
    newProgress,
    medalEarned
  };
}

/**
 * Get user medals from their progress document
 * @param {string} userId - User ID
 * @returns {Promise<Array>} Array of medal objects
 */
export async function getUserMedals(userId) {
  try {
    const ref = doc(database, "users", userId, "progress", "main");
    const snap = await getDoc(ref);
    
    if (snap.exists()) {
      return snap.data().medals || [];
    }
    return [];
  } catch (error) {
    console.error("Error getting user medals:", error);
    return [];
  }
}

/**
 * Check if user has completed a specific unit
 * @param {string} userId - User ID
 * @param {Array} requiredSteps - Array of step IDs required for completion
 * @returns {Promise<boolean>} True if unit is completed
 */
export async function isUnitCompleted(userId, requiredSteps) {
  const progress = await getUserProgress(userId);
  if (!progress) return false;
  
  const completedSteps = progress.stepsCompleted || [];
  return requiredSteps.every(stepId => completedSteps.includes(stepId));
}

export async function completeConcept(userId, conceptId) {
  if (!userId || !conceptId) return;
  const progressRef = doc(database, "users", userId, "progress", "main");
  await updateDoc(progressRef, {
    completedConcepts: arrayUnion(conceptId)
  });
}