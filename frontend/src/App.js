import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { auth } from "./firestoreSetUp/firebaseSetup";
import { onAuthStateChanged } from "firebase/auth";
import HomePage from "./pages/HomePage";
import LessonPage from "./pages/LessonPage";
import AuthPage from "./pages/AuthPage";
import { getCurrentUser } from "./utils/auth";
import { getUserProgress } from "./utils/userProgress";

function App() {
  const [user, setUser] = useState(null);
  const [progress, setProgress] = useState({ xp: 0, stepsCompleted: [], medals: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (user) {
        setUser(user);
        const userProgress = await getUserProgress(user.uid);
        setProgress(userProgress || { xp: 0, stepsCompleted: [], medals: [] });
      } else {
        setUser(null);
        setProgress({ xp: 0, stepsCompleted: [], medals: [] });
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  if (loading) {
    return (
      <div style={{
        height: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        color: "white",
        fontSize: "24px"
      }}>
        Loading...
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        <Route 
          path="/" 
          element={user ? <HomePage /> : <Navigate to="/auth" />} 
        />
        <Route 
          path="/lesson" 
          element={user ? <LessonPage user={user} progress={progress} /> : <Navigate to="/auth" />} 
        />
        <Route 
          path="/auth" 
          element={!user ? <AuthPage /> : <Navigate to="/" />} 
        />
      </Routes>
    </Router>
  );
}

export default App;
