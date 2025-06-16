import {
    collection,
    doc,
    addDoc,
    deleteDoc,
    updateDoc,
    setDoc,
    query,
    where,
    getDoc,
    getDocs, 
    orderBy,
    arrayUnion
  } from "firebase/firestore";
  import { database } from "./firebaseSetup";
  
  export async function writeToDB(collectionName, data) {
    //addDoc()
    try {
      await addDoc(collection(database, collectionName), data);
    } catch (e) {
      console.log("Error adding document: ", e);
    }
  }
  
  export async function deleteFromDB(collectionName, deletedID) {
    //deleteDoc()
    try {
      await deleteDoc(doc(database, collectionName, deletedID));
    } catch (e) {
      console.log("Error deleting document: ", e);
    }
  }
  
  export async function deleteAllFromDB(collectionName) {
    try {
      const querySnapshot = await getDocs(collection(database, collectionName));
      querySnapshot.forEach((doc) => {
        deleteFromDB(collectionName, doc.id);
      });
    } catch (e) {
      console.log("Error deleting all documents: ", e);
    }
  }
  
  export async function updateDB(collectionName, id, data) {
    //updateDoc()
    try {
      const docRef = doc(database, collectionName, id);
      await updateDoc(docRef, data);
    } catch (e) {
      console.log("Error updating document: ", e);
    }
  }
  
  export async function overrideDataInDB(collectionName, id, data) {
    try {
      await setDoc(doc(database, collectionName, id), data);
    } catch (err) {
      console.log("Error overriding data in DB ", err);
    }
  }
  
  export async function readSingleDocFromDB(collectionName, id) {
    try {
      const docRef = doc(database, collectionName, id);
      const docSnap = await getDoc(docRef);
      let data = {};
      if (docSnap.exists()) {
        data = docSnap.data();
      }
      return data;
    } catch (e) {
      console.log("Error getting single document from DB ", e);
    }
  }
  
  export async function readAllFromDB(collectionName) {
    try {
      const querySnapshot = await getDocs(collection(database, collectionName));
      const data = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      return data;
    } catch (e) {
      console.log("Error fetching documents: ", e);
      return [];
    }
  }
  
  export async function readOneDoc(id, collectionName) {
    try {
      const docSnapshot = await getDoc(doc(database, collectionName, id));
      if (docSnapshot.exists()) {
        return docSnapshot.data();
      }
      return null;
    } catch (err) {
      console.log("read one doc ", err);
    }
  }
  
  export async function readAllFromDBWithOrder(
    collectionName,
    orderByField,
    ascending = true,
    filterField = null,
    filterValue = null
  ) {
    try {
      const collectionRef = collection(database, collectionName);
  
      let q;
      if (filterField && filterValue !== null) {
        q = query(
          collectionRef,
          where(filterField, "==", filterValue),
          orderBy(orderByField, ascending ? "asc" : "desc")
        );
      } else {
        q = query(
          collectionRef,
          orderBy(orderByField, ascending ? "asc" : "desc")
        );
      }
  
      const querySnapshot = await getDocs(q);
      const results = querySnapshot.docs.map((doc) => ({
        id: doc.id,
        ...doc.data(),
      }));
  
      return results;
    } catch (e) {
      console.log("Error fetching ordered documents:", e);
      return [];
    }
  }
  
 /**
 * Add a medal to a user's profile
 * @param {string} userId - The user's ID
 * @param {Object} medal - The medal object to add
 * @returns {Promise<void>}
 */
export const addMedalToUser = async (userId, medal) => {
  try {
    const userRef = doc(database, "users", userId);
    
    // First, check if the user document exists
    const userDoc = await getDoc(userRef);
    
    if (userDoc.exists()) {
      // User document exists, add medal to existing medals array
      await updateDoc(userRef, {
        medals: arrayUnion(medal)
      });
    } else {
      // User document doesn't exist, create it with the medal
      await setDoc(userRef, {
        medals: [medal],
        createdAt: new Date().toISOString()
      });
    }
    
    console.log("Medal added successfully:", medal.name);
  } catch (error) {
    console.error("Error adding medal:", error);
    throw error;
  }
};

/**
 * Get all medals for a user
 * @param {string} userId - The user's ID
 * @returns {Promise<Array>} Array of medal objects
 */
export const getUserMedals = async (userId) => {
  try {
    const userRef = doc(database, "users", userId);
    const userDoc = await getDoc(userRef);
    
    if (userDoc.exists()) {
      const userData = userDoc.data();
      return userData.medals || [];
    } else {
      // User document doesn't exist yet, return empty array
      console.log("User document doesn't exist yet, returning empty medals array");
      return [];
    }
  } catch (error) {
    console.error("Error getting user medals:", error);
    return [];
  }
};

/**
 * Check if user has a specific medal
 * @param {string} userId - The user's ID
 * @param {string} medalId - The medal ID to check for
 * @returns {Promise<boolean>} True if user has the medal
 */
export const userHasMedal = async (userId, medalId) => {
  try {
    const medals = await getUserMedals(userId);
    return medals.some(medal => medal.id === medalId);
  } catch (error) {
    console.error("Error checking if user has medal:", error);
    return false;
  }
};

/**
 * Initialize user document with basic structure
 * @param {string} userId - The user's ID
 * @param {Object} userData - Initial user data
 * @returns {Promise<void>}
 */
export const initializeUser = async (userId, userData = {}) => {
  try {
    const userRef = doc(database, "users", userId);
    const userDoc = await getDoc(userRef);
    
    if (!userDoc.exists()) {
      await setDoc(userRef, {
        medals: [],
        createdAt: new Date().toISOString(),
        ...userData
      });
      console.log("User document initialized");
    }
  } catch (error) {
    console.error("Error initializing user:", error);
    throw error;
  }
};