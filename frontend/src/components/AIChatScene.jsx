import React, { useState, useEffect } from "react";
import AICharacterScene from "./AICharacterScene";

function AIChatScene({ pose, message, onUserInput, animation = "bounce" }) {
  const [input, setInput] = useState("");
  const [typedMessage, setTypedMessage] = useState("");

  // Typing effect when message changes
  useEffect(() => {
    let i = 0;
    setTypedMessage(""); // clear previous

    const interval = setInterval(() => {
      setTypedMessage((prev) => prev + message.charAt(i));
      i++;
      if (i >= message.length) clearInterval(interval);
    }, 25); // Speed: 25ms per character

    return () => clearInterval(interval);
  }, [message]);

  const handleSend = () => {
    if (!input.trim()) return;
    onUserInput(input);
    setInput("");
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: 16 }}>
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
          <strong>Robot:</strong> {typedMessage}
        </p>
        <div style={{ display: "flex" }}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your response..."
            style={{ flex: 1, padding: 8 }}
          />
          <button onClick={handleSend} style={{ marginLeft: 8 }}>Send</button>
        </div>
      </div>
    </div>
  );
}

export default AIChatScene;
