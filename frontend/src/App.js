import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { auth } from "./firestoreSetUp/firebaseSetup";
import { onAuthStateChanged } from "firebase/auth";
import HomePage from "./pages/HomePage";
import LessonPage from "./pages/LessonPage";
import AuthPage from "./pages/AuthPage";
import CurriculumPage from "./pages/CurriculumPage";
import DynamicLoadingScreen from "./components/DynamicLoadingScreen";
import PerformanceDashboard from "./components/PerformanceDashboard";
import performanceMonitor from "./utils/performanceMonitor";

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isSigningUp, setIsSigningUp] = useState(false);
  
  // Performance dashboard visibility (enable with ?perf=true in URL or in development)
  const [showPerformanceDashboard] = useState(() => {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('perf') === 'true' || process.env.NODE_ENV === 'development';
  });

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
    <>
      <Router>
        <Routes>
          <Route path="/" element={user ? <HomePage /> : <Navigate to="/auth" />} />
          <Route path="/lesson" element={user ? <LessonPage /> : <Navigate to="/auth" />} />
          <Route path="/curriculum" element={user ? <CurriculumPage /> : <Navigate to="/auth" />} />
          <Route path="/auth" element={!user || isSigningUp ? <AuthPage setIsSigningUp={setIsSigningUp} /> : <Navigate to="/" />} />
        </Routes>
      </Router>
      
      {/* Performance Dashboard - only visible in development or with ?perf=true */}
      <PerformanceDashboard isVisible={showPerformanceDashboard} position="bottom-right" />
    </>
  );
}

export default App;
