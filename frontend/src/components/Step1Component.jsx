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
            尝试 {regenerationCount + 1} - 让我用不同的方式来解释
          </div>
        )}

        <div style={styles.messageText}>
          {isLoading ? "🤔 AI 正在思考一个新的解释方式..." : (currentMessage || initialMessage)}
        </div>

        {isLoading && (
          <div style={styles.loadingText}>
            请稍等，正在生成个性化的类比...
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
              ✅ 我理解了，继续下一步
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
                ? "🔒 已达到重新生成上限" 
                : "🔄 请用不同方式解释"
              }
            </button>
          </div>
        )}

        {regenerationCount >= 2 && !isLoading && (
          <div style={{ textAlign: 'center', marginTop: '16px', fontSize: '14px', color: '#666' }}>
            💡 提示：如果仍有疑问，可以在后续步骤中继续学习
          </div>
        )}
      </div>
    </div>
  );
}

export default Step1Component; 