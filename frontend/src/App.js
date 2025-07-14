import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { auth } from "./firestoreSetUp/firebaseSetup";
import { onAuthStateChanged } from "firebase/auth";
import HomePage from "./pages/HomePage";
import LessonPage from "./pages/LessonPage";
import AuthPage from "./pages/AuthPage";
import CurriculumPage from "./pages/CurriculumPage";
import DynamicLoadingScreen from "./components/DynamicLoadingScreen";

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  if (loading) {
    return (
      <DynamicLoadingScreen 
        message="Initializing application..."
        concept={null}
        showTrivia={true}
        triviaType="tips"
        minDisplayTime={1500}
      />
    );
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={user ? <HomePage /> : <Navigate to="/auth" />} />
        <Route path="/lesson" element={user ? <LessonPage /> : <Navigate to="/auth" />} />
        <Route path="/curriculum" element={user ? <CurriculumPage /> : <Navigate to="/auth" />} />
        <Route path="/auth" element={!user ? <AuthPage /> : <Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;
