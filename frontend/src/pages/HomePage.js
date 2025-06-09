import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import StepProgressBar from "../components/StepProgressBar";
import { signOut } from "firebase/auth";
import { auth } from "../firestoreSetUp/firebaseSetup";

function HomePage({ user, progress }) {
  const navigate = useNavigate();
  const [showDropdown, setShowDropdown] = useState(false);

  const handleLogout = async () => {
    await signOut(auth);
  };

  return (
    <div style={{ padding: 32 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>Welcome, {user.email} 👋</h1>
        <div style={{ position: "relative" }}>
          <button
            onClick={() => setShowDropdown(!showDropdown)}
            style={{
              background: "transparent",
              border: "none",
              fontSize: 24,
              cursor: "pointer",
            }}
          >
            👤
          </button>

          {showDropdown && (
            <div
              style={{
                position: "absolute",
                right: 0,
                background: "#fff",
                border: "1px solid #ccc",
                borderRadius: 4,
                padding: "8px 12px",
                boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
              }}
            >
              <div style={{ cursor: "pointer", marginBottom: 6 }} onClick={() => alert("Profile page coming soon!")}>
                Profile
              </div>
              <div style={{ cursor: "pointer", color: "red" }} onClick={handleLogout}>
                Log out
              </div>
            </div>
          )}
        </div>
      </div>

      <p>🏅 Badges: {progress.badges.join(", ") || "None yet"}</p>

      <button onClick={() => navigate("/lesson")}>Start Lesson</button>

      <StepProgressBar
        stepsCompleted={progress.stepsCompleted?.length || 0}
        totalSteps={5}
      />
    </div>
  );
}

export default HomePage;
