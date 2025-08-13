import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { auth } from "../firestoreSetUp/firebaseSetup";
import { getUserProgress } from "../utils/userProgress";
import curriculumData from "../data/curriculumData";
import DynamicLoadingScreen from "../components/DynamicLoadingScreen";

const styles = {
  container: {
    padding: '40px',
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    maxWidth: '900px',
    margin: '0 auto',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '40px',
  },
  title: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#1e3a8a',
  },
  backLink: {
    padding: '8px 16px',
    border: 'none',
    backgroundColor: '#3b82f6',
    color: 'white',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 'bold',
    textDecoration: 'none',
  },
  unitContainer: {
    marginBottom: '32px',
  },
  unitTitle: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#3b82f6',
    borderBottom: '2px solid #dbeafe',
    paddingBottom: '8px',
    marginBottom: '16px',
  },
  conceptGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
    gap: '16px',
  },
  conceptCard: {
    backgroundColor: '#ffffff',
    padding: '20px',
    borderRadius: '8px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    cursor: 'pointer',
    transition: 'transform 0.2s, box-shadow 0.2s',
    position: 'relative',
  },
  conceptCardLocked: {
    backgroundColor: '#f1f5f9',
    cursor: 'not-allowed',
    color: '#94a3b8',
  },
  conceptCardCompleted: {
    backgroundColor: '#dcfce7',
    border: '2px solid #22c55e',
  },
  conceptTitle: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#1e3a8a',
    marginBottom: '8px',
  },
  conceptDescription: {
    fontSize: '14px',
    color: '#64748b',
  },
  statusIndicator: {
    position: 'absolute',
    top: '12px',
    right: '12px',
    fontSize: '24px',
  }
};

function CurriculumPage() {
  const navigate = useNavigate();
  const user = auth.currentUser;
  const [progress, setProgress] = useState({ xp: 0, stepsCompleted: [], medals: [], completedConcepts: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      getUserProgress(user.uid)
        .then(userProgress => {
          if (userProgress) {
            setProgress(userProgress);
          }
        })
        .finally(() => setLoading(false));
    } else {
      navigate("/auth");
    }
  }, [user, navigate]);

  const handleConceptClick = (concept, isLocked) => {
    if (isLocked) {
      alert("You must complete the previous concepts first!");
      return;
    }
    navigate("/lesson", { state: { concept: concept.title, conceptId: concept.id } });
  };

  if (loading) {
    return (
      <DynamicLoadingScreen 
        message="Loading curriculum..."
        concept={null}
        showTrivia={true}
        triviaType="general"
        minDisplayTime={1000}
      />
    );
  }
  
  const completedConcepts = new Set(progress.completedConcepts || []);
  let firstUnlockedConceptId = null;
  for (const unit of curriculumData) {
    for (const concept of unit.concepts) {
      if (!completedConcepts.has(concept.id)) {
        firstUnlockedConceptId = concept.id;
        break;
      }
    }
    if (firstUnlockedConceptId) break;
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Full Curriculum</h1>
        <Link to="/" style={styles.backLink}>Back to Dashboard</Link>
      </div>
      
      {curriculumData.map((unit) => (
        <div key={unit.id} style={styles.unitContainer}>
          <h2 style={styles.unitTitle}>{unit.title}</h2>
          <div style={styles.conceptGrid}>
            {unit.concepts.map((concept) => {
              const isCompleted = completedConcepts.has(concept.id);
              const isLocked = firstUnlockedConceptId ? concept.id !== firstUnlockedConceptId && !isCompleted : false;
              let cardStyle = { ...styles.conceptCard };
              if (isLocked) cardStyle = { ...cardStyle, ...styles.conceptCardLocked };
              if (isCompleted) cardStyle = { ...cardStyle, ...styles.conceptCardCompleted };

              return (
                <div 
                  key={concept.id} 
                  style={cardStyle} 
                  onClick={() => handleConceptClick(concept, isLocked)}
                  onMouseEnter={e => { if (!isLocked) e.currentTarget.style.transform = 'translateY(-5px)'; }}
                  onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0px)'}
                >
                  {isCompleted && <span style={styles.statusIndicator}>✅</span>}
                  {isLocked && <span style={styles.statusIndicator}>🔒</span>}
                  <h3 style={styles.conceptTitle}>{concept.title}</h3>
                  <p style={styles.conceptDescription}>{concept.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

export default CurriculumPage; 