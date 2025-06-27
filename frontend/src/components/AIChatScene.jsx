import React, { useState, useEffect } from "react";
import AICharacterScene from "./AICharacterScene";

function AIChatScene({ pose, message, onUserInput, animation = "bounce" }) {
  const [input, setInput] = useState("");
  const [typedMessage, setTypedMessage] = useState("");

  // Typing effect when message changes
  useEffect(() => {
    const fullMessage = message ?? ""; // fallback to empty string
    
    // Clear the typed message immediately
    setTypedMessage("");
    
    if (fullMessage.length === 0) {
      return;
    }

    let index = 0;
    
    const interval = setInterval(() => {
      if (index >= fullMessage.length) {
        clearInterval(interval);
        return;
      }
      
      // Use the index directly instead of relying on previous state
      setTypedMessage(fullMessage.substring(0, index + 1));
      index++;
    }, 25); // Speed of typing

    return () => clearInterval(interval);
  }, [message]);

  const handleSend = () => {
    if (!input.trim()) return;
    onUserInput(input);
    setInput("");
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: 16,
      }}
    >
      <AICharacterScene pose={pose} animation={animation} />

      <div
        style={{
          marginTop: 8,
          background: "#f5f5f5",
          padding: 16,
          borderRadius: 8,
          maxWidth: 500,
          width: "100%",
        }}
      >
        <p style={{ whiteSpace: "pre-wrap", marginBottom: 16 }}>
          {typedMessage}
        </p>

        <div style={{ display: "flex" }}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your response..."
            style={{ flex: 1, padding: 8 }}
          />
          <button onClick={handleSend} style={{ marginLeft: 8 }}>
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default AIChatScene;