import React, { useState, useEffect } from "react";
import AICharacterScene from "./AICharacterScene";
import { getTutorReply } from "../utils/chat";

function AIChatScene({ pose, user, initialMessage, animation = "bounce", showInput = true }) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    { sender: "bot", text: initialMessage || "你好！有什么 SQL 问题想问我吗？" },
  ]);
  const [typingBotText, setTypingBotText] = useState("");
  const [isBotTyping, setIsBotTyping] = useState(false);

  const getInitialMessages = () => {
    if (messages && messages.length > 0) return messages;
    if (initialMessage) return [{ sender: "bot", text: initialMessage }];
    return [{ sender: "bot", text: "Loading..." }];
  };

  const [chatMessages, setChatMessages] = useState(getInitialMessages());

  // Handle prop changes
  useEffect(() => {
    const newMessages = getInitialMessages();
    setChatMessages(newMessages);
  }, [initialMessage, messages]);

  // 当父组件传入的 initialMessage 变化时，刷新首条机器人消息（仅在还未有真实对话时）
  useEffect(() => {
    setMessages((prev) => {
      // 若用户尚未发送消息，且首条为 bot，则替换内容
      if (prev.length === 1 && prev[0].sender === "bot") {
        return [{ sender: "bot", text: initialMessage || "你好！有什么 SQL 问题想问我吗？" }];
      }
      return prev;
    });
  }, [initialMessage]);

  // 逐字打字效果，用在 bot 正在输出时
  useEffect(() => {
    if (!isBotTyping) return;

    const full = typingBotText;
    let idx = 0;
    setMessages((prev) => {
      const copy = [...prev];
      copy[copy.length - 1] = { ...copy[copy.length - 1], text: "" };
      return copy;
    });

    const timer = setInterval(() => {
      idx += 1;
      setMessages((prev) => {
        const copy = [...prev];
        copy[copy.length - 1] = {
          ...copy[copy.length - 1],
          text: full.substring(0, idx),
        };
        return copy;
      });
      if (idx >= full.length) {
        clearInterval(timer);
        setIsBotTyping(false);
      }
    }, 30);

    return () => clearInterval(timer);
  }, [isBotTyping, typingBotText]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    // 显示用户消息
    setMessages((prev) => [...prev, { sender: "user", text: trimmed }]);
    setInput("");

    // 立即在 UI 中添加空占位 bot 消息，再填充
    setMessages((prev) => [...prev, { sender: "bot", text: "" }]);
    setIsBotTyping(true);

    try {
      const reply = await getTutorReply(user?.uid || "guest", trimmed);
      setTypingBotText(reply);
    } catch (err) {
      console.error(err);
      setTypingBotText("抱歉，服务器出错了，请稍后再试。");
    }
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
          height: 400,
          overflowY: "auto",
        }}
      >
        {messages.map((m, idx) => (
          <p
            key={idx}
            style={{
              whiteSpace: "pre-wrap",
              marginBottom: 12,
              textAlign: m.sender === "user" ? "right" : "left",
              color: m.sender === "user" ? "#1976d2" : "#000",
            }}
          >
            {m.text}
          </p>
        ))}
      </div>

      {showInput && (
        <div style={{ display: "flex", marginTop: 8, width: 500 }}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="输入你的问题..."
            style={{ flex: 1, padding: 8 }}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSend();
            }}
          />
          <button onClick={handleSend} style={{ marginLeft: 8 }}>
            发送
          </button>
        </div>
      )}
    </div>
  );
}

export default AIChatScene;