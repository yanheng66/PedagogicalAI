import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AuthPage from "./pages/AuthPage";
import HomePage from "./pages/HomePage";
import LessonPage from "./pages/LessonPage";
import PracticePage from "./pages/PracticePage";
import { auth } from "./firestoreSetUp/firebaseSetup";
import { getOrCreateUserProgress } from "./utils/userProgress";

function App() {
  const [user, setUser] = useState(null);
  const [progress, setProgress] = useState(null);

  useEffect(() => {
    const unsub = auth.onAuthStateChanged(async (user) => {
      if (user) {
        setUser(user);
        const userProgress = await getOrCreateUserProgress(user.uid);
        setProgress(userProgress);
      } else {
        setUser(null);
        setProgress(null);
      }
    });
    return unsub;
  }, []);

  if (!user || !progress) {
    return <AuthPage onLogin={setUser} />;
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage user={user} progress={progress} />} />
        <Route path="/lesson" element={<LessonPage user={user} progress={progress} />} />
        <Route path="/practice" element={<PracticePage user={user} progress={progress} />} />
      </Routes>
    </Router>
  );
}

export default App;
