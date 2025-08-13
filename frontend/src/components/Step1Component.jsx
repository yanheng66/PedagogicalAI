import React, { useState } from "react";
import AICharacterScene from "./AICharacterScene";
import robotIdle from "../assets/kenney_toon-characters-1/Robot/PNG/Poses/character_robot_idle.png";

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    padding: 16,
  },
  messageContainer: {
    marginTop: 8,
    background: "#f5f5f5",
    padding: 20,
    borderRadius: 12,
    maxWidth: 600,
    width: "100%",
    minHeight: 200,
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
  },
  messageText: {
    fontSize: "16px",
    lineHeight: "1.6",
    color: "#333",
    marginBottom: 20,
    whiteSpace: "pre-wrap",
  },
  buttonContainer: {
    display: "flex",
    gap: "16px",
    justifyContent: "center",
    marginTop: 20,
  },
  understandButton: {
    backgroundColor: "#4CAF50",
    color: "white",
    border: "none",
    padding: "12px 24px",
    borderRadius: "8px",
    fontSize: "16px",
    fontWeight: "bold",
    cursor: "pointer",
    transition: "all 0.3s ease",
    minWidth: "180px",
  },
  regenerateButton: {
    backgroundColor: "#FF6B35",
    color: "white",
    border: "none",
    padding: "12px 24px",
    borderRadius: "8px",
    fontSize: "16px",
    fontWeight: "bold",
    cursor: "pointer",
    transition: "all 0.3s ease",
    minWidth: "180px",
  },
  loadingText: {
    textAlign: "center",
    color: "#666",
    fontStyle: "italic",
    margin: "20px 0",
  },
  regenerationCount: {
    textAlign: "center",
    color: "#888",
    fontSize: "14px",
    marginBottom: "10px",
  }
};

function Step1Component({ 
  initialMessage, 
  onUnderstand, 
  onRegenerate, 
  isLoading = false,
  regenerationCount = 0 
}) {
  const [currentMessage, setCurrentMessage] = useState(initialMessage);

  const handleUnderstand = () => {
    if (onUnderstand) {
      onUnderstand();
    }
  };

  const handleRegenerate = () => {
    if (onRegenerate) {
      onRegenerate();
    }
  };

  return (
    <div style={styles.container}>
      <AICharacterScene pose={robotIdle} animation="bounce" />

      <div style={styles.messageContainer}>
        {regenerationCount > 0 && (
          <div style={styles.regenerationCount}>
            Attempt {regenerationCount + 1} - Let me explain it differently
          </div>
        )}

        <div style={styles.messageText}>
          {isLoading ? "🤔 AI is thinking of a new way to explain..." : (currentMessage || initialMessage)}
        </div>

        {isLoading && (
          <div style={styles.loadingText}>
            Please wait, generating personalized analogy...
          </div>
        )}

        {!isLoading && (
          <div style={styles.buttonContainer}>
            <button
              style={styles.understandButton}
              onClick={handleUnderstand}
              onMouseOver={(e) => {
                e.target.style.backgroundColor = "#45a049";
                e.target.style.transform = "translateY(-2px)";
              }}
              onMouseOut={(e) => {
                e.target.style.backgroundColor = "#4CAF50";
                e.target.style.transform = "translateY(0)";
              }}
            >
              ✅ I understand, continue to next step
            </button>

            <button
              style={styles.regenerateButton}
              onClick={handleRegenerate}
              disabled={regenerationCount >= 2} // 限制最多重新生成3次
              onMouseOver={(e) => {
                if (regenerationCount < 2) {
                  e.target.style.backgroundColor = "#e55a2b";
                  e.target.style.transform = "translateY(-2px)";
                }
              }}
              onMouseOut={(e) => {
                if (regenerationCount < 2) {
                  e.target.style.backgroundColor = "#FF6B35";
                  e.target.style.transform = "translateY(0)";
                }
              }}
            >
              {regenerationCount >= 2 
                ? "🔒 Maximum regeneration limit reached" 
                : "🔄 Please explain differently"
              }
            </button>
          </div>
        )}

        {regenerationCount >= 2 && !isLoading && (
          <div style={{ textAlign: 'center', marginTop: '16px', fontSize: '14px', color: '#666' }}>
            💡 Tip: If you still have questions, you can continue learning in the next steps
          </div>
        )}
      </div>
    </div>
  );
}

export default Step1Component; 