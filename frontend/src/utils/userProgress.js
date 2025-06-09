import { doc, getDoc, setDoc, updateDoc } from "firebase/firestore";
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
  