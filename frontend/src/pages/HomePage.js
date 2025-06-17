import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { signOut } from "firebase/auth";
import { auth } from "../firestoreSetUp/firebaseSetup";
import lessonSteps from "../data/lessonSteps";
import ModernRoadMapProgressBar from "../components/ModernRoadMapProgressBar";
import { getCurrentUser } from "../utils/auth";
import { getUserProgress, getUserMedals } from "../utils/userProgress";

function HomePage() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [progress, setProgress] = useState({ xp: 0, stepsCompleted: [], medals: [] });
  const [showPopup, setShowPopup] = useState(false);
  const [medals, setMedals] = useState([]);

  useEffect(() => {
    const loadUserData = async () => {
      const currentUser = getCurrentUser();
      if (currentUser) {
        setUser(currentUser);
        const userProgress = await getUserProgress(currentUser.uid);
        
        if (userProgress) {
          setProgress(userProgress);
          // Get medals from the progress document
          const userMedals = userProgress.medals || [];
          setMedals(userMedals);
          console.log("User medals loaded:", userMedals);
        } else {
          // No progress yet, initialize empty state
          setProgress({ xp: 0, stepsCompleted: [], medals: [] });
          setMedals([]);
        }
      }
    };
    loadUserData();
  }, []);

  const handleLogout = async () => {
    await signOut(auth);
  };

  const handleRevisitLessons = () => {
    if (progress.stepsCompleted.length === 0) {
      setShowPopup(true);
      return;
    }
    navigate("/lesson", { state: { startFromIndex: 0 } });
  };

  const handlePopupClose = () => {
    setShowPopup(false);
  };

  const totalLessons = lessonSteps.length;
  const completedLessons = Math.min(progress.stepsCompleted.length, totalLessons);
  const progressPercentage = (completedLessons / totalLessons) * 100;

  // Find the next lesson to continue from
  const completedSteps = progress.stepsCompleted || [];
  const completedSet = new Set(completedSteps);
  
  // Find the first incomplete step
  const firstIncompleteIndex = lessonSteps.findIndex(step => !completedSet.has(step.id));
  
  // If all steps are completed, start from the last step
  const continueFromIndex = firstIncompleteIndex === -1 ? totalLessons - 1 : firstIncompleteIndex;

  return (
    <div style={{ padding: 32, maxWidth: 800, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <h1>Welcome, {user?.email} 👋</h1>
        <div style={{ position: "relative" }}>
          <button
            onClick={() => alert("Profile page coming soon!")}
            style={{
              background: "transparent",
              border: "none",
              fontSize: 24,
              cursor: "pointer",
            }}
          >
            👤
          </button>

          <div style={{ cursor: "pointer", color: "red" }} onClick={handleLogout}>
            Log out
          </div>
        </div>
      </div>

      {/* Display Medals */}
      {medals.length > 0 && (
        <div style={{ 
          marginBottom: 32,
          background: "linear-gradient(135deg, #FFD700 0%, #FFA500 100%)",
          padding: 24,
          borderRadius: 12,
          boxShadow: "0 8px 32px rgba(255, 215, 0, 0.3)",
          border: "2px solid #FFD700"
        }}>
          <div style={{ display: "flex", alignItems: "center", marginBottom: 16 }}>
            <h3 style={{ 
              margin: 0, 
              color: "#8B4513",
              fontSize: "24px",
              fontWeight: "bold",
              textShadow: "1px 1px 2px rgba(255,255,255,0.8)"
            }}>
              🏆 Your Achievements
            </h3>
            <div style={{
              marginLeft: "auto",
              background: "rgba(139, 69, 19, 0.1)",
              padding: "4px 12px",
              borderRadius: "20px",
              color: "#8B4513",
              fontWeight: "bold",
              fontSize: "14px"
            }}>
              {medals.length} Medal{medals.length !== 1 ? 's' : ''} Earned
            </div>
          </div>
          
          <div style={{ 
            display: 'flex', 
            gap: '20px', 
            flexWrap: 'wrap',
            justifyContent: 'flex-start'
          }}>
            {medals.map((medal) => (
              <div key={medal.id} style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                background: 'rgba(255, 255, 255, 0.9)',
                padding: '20px',
                borderRadius: '12px',
                boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)',
                border: '2px solid rgba(255, 215, 0, 0.5)',
                minWidth: '140px',
                transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.boxShadow = '0 8px 24px rgba(0, 0, 0, 0.15)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.1)';
              }}
              >
                <div style={{
                  position: 'relative',
                  marginBottom: '12px'
                }}>
                  <img 
                    src={medal.image} 
                    alt={medal.name}
                    style={{
                      width: '80px',
                      height: '80px',
                      objectFit: 'contain',
                      filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))'
                    }}
                  />
                </div>
                
                <div style={{ textAlign: 'center' }}>
                  <div style={{ 
                    fontWeight: 'bold', 
                    fontSize: '16px',
                    color: '#8B4513',
                    marginBottom: '4px'
                  }}>
                    {medal.name}
                  </div>
                  {medal.description && (
                    <div style={{ 
                      fontSize: '12px', 
                      color: '#666',
                      marginBottom: '8px',
                      fontStyle: 'italic'
                    }}>
                      {medal.description}
                    </div>
                  )}
                  <div style={{ 
                    fontSize: '11px', 
                    opacity: 0.7,
                    color: '#8B4513'
                  }}>
                    Earned: {new Date(medal.dateAwarded).toLocaleDateString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ 
        background: "#f5f5f5", 
        padding: 24, 
        borderRadius: 8, 
        marginBottom: 32,
        boxShadow: "0 2px 4px rgba(0,0,0,0.05)"
      }}>
        <h2 style={{ marginTop: 0 }}>Your Progress</h2>
        <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 16 }}>
          <div style={{ 
            background: "#4CAF50", 
            color: "white", 
            padding: "8px 16px", 
            borderRadius: 20,
            fontSize: 18,
            fontWeight: "bold"
          }}>
            {completedLessons}/{totalLessons} Lessons Completed
          </div>
          {completedLessons === totalLessons && (
            <span style={{ color: "#4CAF50", fontWeight: "bold" }}>🎉 All lessons completed!</span>
          )}
        </div>
        <div
          style={{
            width: "100%",
            height: 20,
            backgroundColor: "#e0e0e0",
            borderRadius: 10,
            overflow: "hidden",
          }}
        >
          <div
            style={{
              width: `${progressPercentage}%`,
              height: "100%",
              backgroundColor: "#4CAF50",
              transition: "width 0.3s ease-in-out",
            }}
          />
        </div>
      </div>

      <ModernRoadMapProgressBar
        totalSteps={totalLessons}
        currentStep={completedLessons}
        completedSteps={progress.stepsCompleted.map(id => lessonSteps.findIndex(step => step.id === id))}
      />

      <div style={{ display: "flex", gap: 16 }}>
        <button 
          onClick={() => navigate("/lesson", { state: { startFromIndex: continueFromIndex } })}
          style={{
            padding: "12px 24px",
            fontSize: 16,
            background: "#2196F3",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: "pointer",
            flex: 1
          }}
        >
          {completedLessons === 0 ? "Start Lesson" : "Continue Learning"}
        </button>
        <button 
          onClick={handleRevisitLessons}
          style={{
            padding: "12px 24px",
            fontSize: 16,
            background: "#fff",
            color: "#2196F3",
            border: "1px solid #2196F3",
            borderRadius: 4,
            cursor: "pointer",
            flex: 1
          }}
        >
          Revisit Lessons
        </button>
      </div>

      {showPopup && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '20px',
            borderRadius: '8px',
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
            maxWidth: '400px',
            width: '90%'
          }}>
            <h3 style={{ marginTop: 0 }}>Complete a Lesson First</h3>
            <p>You need to complete at least one lesson before you can revisit lessons.</p>
            <button 
              onClick={handlePopupClose}
              style={{
                backgroundColor: '#4CAF50',
                color: 'white',
                border: 'none',
                padding: '8px 16px',
                borderRadius: '4px',
                cursor: 'pointer',
                marginTop: '16px'
              }}
            >
              OK
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default HomePage;