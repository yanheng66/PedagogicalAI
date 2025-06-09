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
    orderBy
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
  