import { doc, getDoc, setDoc, updateDoc, arrayUnion } from "firebase/firestore";
import { database } from "../firestoreSetUp/firebaseSetup";

export async function getUserProgress(uid) {
  const ref = doc(database, "users", uid, "progress", "main");
  const snap = await getDoc(ref);
  return snap.exists() ? snap.data() : null;
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
 * @param {string} uid - User ID
 * @param {string} stepKey - Step identifier
 * @param {number} xpAmount - XP to award
 * @param {Array} allLessonSteps - All lesson steps to check completion
 * @returns {Promise<Object>} - Returns { medalEarned: medal or null, newProgress: updatedProgress }
 */
export async function completeStepAndCheckMedals(uid, stepKey, xpAmount, allLessonSteps) {
  const ref = doc(database, "users", uid, "progress", "main");
  const snap = await getDoc(ref);
  
  // Get current progress or create default
  const currentProgress = snap.exists() ? snap.data() : {
    xp: 0,
    badges: [],
    stepsCompleted: [],
    medals: [],
    createdAt: new Date().toISOString(),
  };

  // Check if step is already completed
  const isStepAlreadyCompleted = currentProgress.stepsCompleted?.includes(stepKey);
  
  let newProgress = { ...currentProgress };
  let medalEarned = null;

  // Only process if step is not already completed
  if (!isStepAlreadyCompleted) {
    // Add XP and mark step as completed
    newProgress.xp = (currentProgress.xp || 0) + xpAmount;
    newProgress.stepsCompleted = [...(currentProgress.stepsCompleted || []), stepKey];
    newProgress.lastUpdated = new Date().toISOString();

    // Check if all lessons are now completed
    const allStepsCompleted = allLessonSteps.every(step => 
      newProgress.stepsCompleted.includes(step.id)
    );

    // Award medal if all lessons completed and user doesn't already have it
    if (allStepsCompleted) {
      const joinMasterMedal = {
        id: "join_master",
        name: "The JOIN Master",
        description: "Completed all INNER JOIN lessons",
        image: require("../assets/kenneymedals/PNG/1.png"),
        dateAwarded: new Date().toISOString(),
        unitCompleted: "INNER_JOIN"
      };

      // Check if user already has this medal
      const currentMedals = currentProgress.medals || [];
      const hasMedal = currentMedals.some(medal => medal.id === "join_master");

      if (!hasMedal) {
        newProgress.medals = [...currentMedals, joinMasterMedal];
        medalEarned = joinMasterMedal;
        console.log("🏆 Medal earned:", joinMasterMedal.name);
      }
    }

    // Save updated progress to database
    await setDoc(ref, newProgress, { merge: true });
  }

  return {
    medalEarned,
    newProgress,
    isStepAlreadyCompleted
  };
}

/**
 * Get user medals from their progress document
 * @param {string} uid - User ID
 * @returns {Promise<Array>} Array of medal objects
 */
export async function getUserMedals(uid) {
  try {
    const ref = doc(database, "users", uid, "progress", "main");
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
 * @param {string} uid - User ID
 * @param {Array} requiredSteps - Array of step IDs required for completion
 * @returns {Promise<boolean>} True if unit is completed
 */
export async function isUnitCompleted(uid, requiredSteps) {
  const progress = await getUserProgress(uid);
  if (!progress) return false;
  
  const completedSteps = progress.stepsCompleted || [];
  return requiredSteps.every(stepId => completedSteps.includes(stepId));
}