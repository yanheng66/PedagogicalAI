import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { signOut } from "firebase/auth";
import { auth } from "../firestoreSetUp/firebaseSetup";
import lessonSteps from "../data/lessonSteps";
import { getUserProgress } from "../utils/userProgress";
import curriculumData from "../data/curriculumData";
import { calculateLevelInfo, getLevelTitle } from "../utils/levelSystem";

// Using require.context to dynamically import all medal images
const medalImages = require.context('../assets/kenneymedals/PNG', false, /\.png$/);

// A map to get medal details by ID
const medalDetails = {
  'select-from': { name: 'Data Novice', description: 'Mastered SELECT.', image: medalImages('./1.png') },
  'where': { name: 'Filter Fanatic', description: 'Learned WHERE.', image: medalImages('./2.png') },
  // ... add all other medals here
};

const styles = {
  container: {
    padding: '40px',
    fontFamily: "'Segoe UI', sans-serif",
    backgroundColor: '#f4f7f6',
    minHeight: '100vh',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '40px',
  },
  title: {
    fontSize: '36px',
    fontWeight: '700',
    color: '#2c3e50',
  },
  logoutButton: {
    padding: '10px 20px',
    border: 'none',
    backgroundColor: '#e74c3c',
    color: 'white',
    borderRadius: '5px',
    cursor: 'pointer',
    fontWeight: 'bold',
    transition: 'background-color 0.2s',
  },
  dashboardGrid: {
    display: 'grid',
    gridTemplateColumns: '2fr 1fr',
    gap: '40px',
    alignItems: 'flex-start',
  },
  leftColumn: {
    display: 'flex',
    flexDirection: 'column',
    gap: '40px',
  },
  rightColumn: {
    display: 'flex',
    flexDirection: 'column',
    gap: '40px',
  },
  sectionContainer: {
    backgroundColor: 'white',
    padding: '30px',
    borderRadius: '8px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.05)',
  },
  sectionTitle: {
    fontSize: '24px',
    fontWeight: '600',
    color: '#34495e',
    marginBottom: '20px',
    borderBottom: '2px solid #ecf0f1',
    paddingBottom: '10px',
  },
  progressPreviewContainer: {
    /* Styles for the progress preview container */
  },
  seeAllButton: {
    /* Styles for the 'See All' button */
  },
  xpContainer: {
    /* Styles for the XP container */
  },
  medalsContainer: {
    /* Styles for the medals container */
  },
};

function HomePage() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [progress, setProgress] = useState({ xp: 0, stepsCompleted: [], medals: [], completedConcepts: [] });
  const [showPopup, setShowPopup] = useState(false);

  // NOTE: This combines the user and progress loading from both versions
  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged(async (currentUser) => {
      if (currentUser) {
        setUser(currentUser);
        const userProgress = await getUserProgress(currentUser.uid);
        if (userProgress) {
          setProgress(userProgress);
        }
      }
    });
    return () => unsubscribe();
  }, []);

  const handleLogout = async () => {
    await signOut(auth);
    navigate("/auth");
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

  // --- Advanced Level System Calculations ---
  const xp = progress.xp || 0;
  const levelInfo = calculateLevelInfo(xp);
  const {
    currentLevel: level,
    xpIntoCurrentLevel: xpIntoLevel,
    xpToNextLevel,
    progressPercent: xpProgressPercent,
    xpRequiredForCurrentLevel,
    isMaxLevel
  } = levelInfo;
  const levelTitle = getLevelTitle(level);

  // --- Logic for the new Progress Preview ---
  const completedConcepts = new Set(progress.completedConcepts || []);
  const allConcepts = curriculumData.flatMap(unit => unit.concepts);
  const firstUnlockedIndex = allConcepts.findIndex(c => !completedConcepts.has(c.id));
  const previewIndex = firstUnlockedIndex === -1 ? allConcepts.length - 1 : firstUnlockedIndex;
  const previewConcepts = allConcepts.slice(
    Math.max(0, previewIndex - 1),
    previewIndex + 2
  );
  
  const handleConceptClick = (concept, isLocked) => {
    if (isLocked) {
        alert("You must complete the previous concepts first!");
        return;
    }
    navigate("/lesson", { state: { concept: concept.title, conceptId: concept.id } });
  };

  return (
    <>
      <style>
        {`
          @keyframes shimmer {
            0% { background-position: -200px 0; }
            100% { background-position: 200px 0; }
          }
        `}
      </style>
      <div style={{ padding: 32, maxWidth: 800, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 32 }}>
        <h1>Welcome, {user?.email} 👋</h1>
        <div style={{ position: "relative" }}>
          <button onClick={() => alert("Profile page coming soon!")} style={{ background: "transparent", border: "none", fontSize: 24, cursor: "pointer" }}>
            👤
          </button>
          <div style={{ cursor: "pointer", color: "red" }} onClick={handleLogout}>
            Log out
          </div>
        </div>
      </div>

      {progress.medals && progress.medals.length > 0 && (
        <div style={{ marginBottom: 32, background: "linear-gradient(135deg, #FFD700 0%, #FFA500 100%)", padding: 24, borderRadius: 12, boxShadow: "0 8px 32px rgba(255, 215, 0, 0.3)", border: "2px solid #FFD700" }}>
          <div style={{ display: "flex", alignItems: "center", marginBottom: 16 }}>
            <h3 style={{ margin: 0, color: "#8B4513", fontSize: "24px", fontWeight: "bold", textShadow: "1px 1px 2px rgba(255,255,255,0.8)" }}>
              🏆 Your Achievements
            </h3>
          </div>
          <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', justifyContent: 'flex-start' }}>
            {progress.medals.map((medal) => (
              <div key={medal.id} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', background: 'rgba(255, 255, 255, 0.9)', padding: '20px', borderRadius: '12px', boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)', border: '2px solid rgba(255, 215, 0, 0.5)', minWidth: '140px' }}>
                <img src={medal.image} alt={medal.name} style={{ width: '80px', height: '80px', objectFit: 'contain', filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))', marginBottom: '12px' }} />
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontWeight: 'bold', fontSize: '16px', color: '#8B4513', marginBottom: '4px' }}>{medal.name}</div>
                  <div style={{ fontSize: '11px', opacity: 0.7, color: '#8B4513' }}>Earned: {new Date(medal.dateAwarded).toLocaleDateString()}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ background: "linear-gradient(90deg, #2196F3 0%, #21CBF3 100%)", color: "white", padding: "20px", borderRadius: "12px", marginBottom: "24px", boxShadow: "0 4px 16px rgba(33, 203, 243, 0.15)", display: "flex", alignItems: "center", gap: "24px" }}>
        <div style={{ fontSize: "32px", fontWeight: "bold" }}>
          🧑‍🎓 Level {level}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: "16px", fontWeight: "600", marginBottom: "4px", opacity: 0.9 }}>
            {levelTitle}
          </div>
          <div style={{ fontSize: "18px", fontWeight: "bold" }}>
            XP: {xp} 
            {!isMaxLevel && (
              <span style={{ fontSize: "14px", opacity: 0.8 }}>
                ({xpIntoLevel}/{xpRequiredForCurrentLevel} • +{xpToNextLevel} to next level)
              </span>
            )}
            {isMaxLevel && (
              <span style={{ fontSize: "14px", opacity: 0.8 }}>
                (Maximum Level Achieved! 🎉)
              </span>
            )}
          </div>
          {!isMaxLevel && (
            <div style={{ width: "100%", height: "14px", background: "#e0e0e0", borderRadius: "7px", marginTop: "8px", overflow: "hidden" }}>
              <div style={{ width: `${xpProgressPercent}%`, height: "100%", background: "#4CAF50", transition: "width 0.3s" }} />
            </div>
          )}
          {isMaxLevel && (
            <div style={{ width: "100%", height: "14px", background: "#FFD700", borderRadius: "7px", marginTop: "8px", overflow: "hidden" }}>
              <div style={{ width: "100%", height: "100%", background: "linear-gradient(45deg, #FFD700, #FFA500)", animation: "shimmer 2s infinite" }} />
            </div>
          )}
        </div>
      </div>
      
      {/* --- REPLACEMENT SECTION --- */}
      <div style={{ 
        background: "linear-gradient(90deg, #d4e4ff 0%, #dbeafe 100%)",
        padding: 24, 
        borderRadius: 8, 
        marginBottom: 32,
        boxShadow: "0 2px 4px rgba(0,0,0,0.05)"
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ marginTop: 0, color: "#1e3a8a" }}>Your Next Steps</h2>
          <Link to="/curriculum" style={{fontWeight: 'bold', textDecoration: 'none', color: '#1e3a8a'}}>See All Units →</Link>
        </div>
        <div style={{display: 'flex', flexDirection: 'row', gap: '15px', flexWrap: 'wrap'}}> 
          {previewConcepts.map((concept) => {
            const isCompleted = completedConcepts.has(concept.id);
            const isUnlocked = concept.id === allConcepts[previewIndex]?.id;
            const isLocked = !isCompleted && !isUnlocked;
            
            let cardStyle = { padding: '15px', borderRadius: '8px', border: '1px solid #ddd', display: 'flex', alignItems: 'center', gap: '15px', transition: 'all 0.2s ease', flex: 1, minWidth: '200px' };
            if(isCompleted) cardStyle = {...cardStyle, backgroundColor: '#e8f8f5', borderColor: '#d1f0e1'};
            if(isUnlocked) cardStyle = {...cardStyle, backgroundColor: '#e9f2fc', cursor: 'pointer', borderColor: '#c3dafa'};
            if(isLocked) cardStyle = {...cardStyle, backgroundColor: '#f1f1f1', opacity: 0.7, cursor: 'not-allowed'};

            return (
              <div key={concept.id} style={cardStyle} onClick={() => handleConceptClick(concept, isLocked)}>
                <span style={{fontSize: '24px'}}>{isCompleted ? '✅' : isUnlocked ? '🎯' : '🔒'}</span>
                <div>
                  <h3 style={{margin: 0, fontSize: '16px'}}>{concept.title}</h3>
                  <p style={{margin: '4px 0 0 0', fontSize: '14px', color: '#666'}}>{concept.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
      {/* --- END REPLACEMENT SECTION --- */}

      {showPopup && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0, 0, 0, 0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
          <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)', maxWidth: '400px', width: '90%' }}>
            <h3 style={{ marginTop: 0 }}>Complete a Lesson First</h3>
            <p>You need to complete at least one lesson before you can revisit lessons.</p>
            <button onClick={handlePopupClose} style={{ backgroundColor: '#4CAF50', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '4px', cursor: 'pointer', marginTop: '16px' }}>
              OK
            </button>
          </div>
        </div>
      )}
    </div>
    </>
  );
}

export default HomePage;