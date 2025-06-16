import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import StepProgressBar from "../components/StepProgressBar";
import { signOut } from "firebase/auth";
import { auth } from "../firestoreSetUp/firebaseSetup";
import lessonSteps from "../data/lessonSteps";
import ModernRoadMapProgressBar from "../components/ModernRoadMapProgressBar";
import robotIdle from "../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_idle.png";
import robotTalk from "../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_talk.png";
import { getCurrentUser } from "../utils/auth";
import { getUserProgress } from "../utils/userProgress";
import { addMedalToUser, getUserMedals } from "../firestoreSetUp/firestoreHelper";

function HomePage() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [progress, setProgress] = useState({ xp: 0, stepsCompleted: [] });
  const [pose, setPose] = useState(robotIdle);
  const [animation, setAnimation] = useState("bounce");
  const [showPopup, setShowPopup] = useState(false);
  const [medals, setMedals] = useState([]);
  const [showNewMedalPopup, setShowNewMedalPopup] = useState(false);
  const [newMedal, setNewMedal] = useState(null);

  useEffect(() => {
    const loadUserData = async () => {
      const currentUser = getCurrentUser();
      if (currentUser) {
        setUser(currentUser);
        const userProgress = await getUserProgress(currentUser.uid);
        setProgress(userProgress);
        
        // Load user medals first
        const userMedals = await getUserMedals(currentUser.uid);
        setMedals(userMedals);

        // Check if all lessons are completed and award medal if not already awarded
        console.log("Steps completed:", userProgress.stepsCompleted.length);
        console.log("Total lessons:", lessonSteps.length);
        
        if (userProgress.stepsCompleted.length >= lessonSteps.length) {
          const joinMasterMedal = {
            id: "join_master",
            name: "The JOIN Master",
            description: "Completed all INNER JOIN lessons",
            image: require("../assets/kenneymedals/PNG/1.png"),
            dateAwarded: new Date().toISOString()
          };
          
          // Check if user already has this medal
          const hasMedal = userMedals.some(medal => medal.id === "join_master");
          console.log("User has JOIN Master medal:", hasMedal);
          
          if (!hasMedal) {
            try {
              await addMedalToUser(currentUser.uid, joinMasterMedal);
              const updatedMedals = [...userMedals, joinMasterMedal];
              setMedals(updatedMedals);
              setNewMedal(joinMasterMedal);
              setShowNewMedalPopup(true);
              console.log("Medal awarded successfully!");
            } catch (error) {
              console.error("Error awarding medal:", error);
            }
          }
        }
      }
    };
    loadUserData();
  }, []);

  const handleLogout = async () => {
    await signOut(auth);
  };

  const handleStartLesson = () => {
    navigate("/lesson", { state: { startFromIndex: 0 } });
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

  const handleNewMedalClose = () => {
    setShowNewMedalPopup(false);
    setNewMedal(null);
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
                  {/* Sparkle effect for new medals */}
                  {medal.id === newMedal?.id && (
                    <div style={{
                      position: 'absolute',
                      top: '-5px',
                      right: '-5px',
                      width: '20px',
                      height: '20px',
                      background: '#FFD700',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '12px',
                      animation: 'sparkle 2s infinite'
                    }}>
                      ✨
                    </div>
                  )}
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

      {/* Completion popup */}
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

      {/* New Medal Celebration Popup */}
      {showNewMedalPopup && newMedal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1001
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '40px',
            borderRadius: '16px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
            maxWidth: '400px',
            width: '90%',
            textAlign: 'center',
            background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
            border: '3px solid #FFD700'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🎉</div>
            <h2 style={{ 
              marginTop: 0, 
              marginBottom: '16px',
              color: '#8B4513',
              textShadow: '1px 1px 2px rgba(255,255,255,0.8)'
            }}>
              Congratulations!
            </h2>
            <img 
              src={newMedal.image} 
              alt={newMedal.name}
              style={{
                width: '120px',
                height: '120px',
                objectFit: 'contain',
                marginBottom: '16px',
                filter: 'drop-shadow(0 4px 8px rgba(0,0,0,0.3))'
              }}
            />
            <h3 style={{ 
              color: '#8B4513',
              marginBottom: '8px',
              fontSize: '24px'
            }}>
              {newMedal.name}
            </h3>
            <p style={{ 
              color: '#8B4513',
              marginBottom: '24px',
              fontSize: '16px'
            }}>
              {newMedal.description}
            </p>
            <button 
              onClick={handleNewMedalClose}
              style={{
                backgroundColor: '#8B4513',
                color: 'white',
                border: 'none',
                padding: '12px 24px',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '16px',
                fontWeight: 'bold'
              }}
            >
              Awesome! 🏆
            </button>
          </div>
        </div>
      )}

      {/* CSS for animations */}
      <style jsx>{`
        @keyframes sparkle {
          0%, 100% { 
            transform: scale(1) rotate(0deg);
            opacity: 1;
          }
          50% { 
            transform: scale(1.2) rotate(180deg);
            opacity: 0.8;
          }
        }
      `}</style>
    </div>
  );
}

export default HomePage;