/**
 * utils/chat.js
 * 与后端 FastAPI `/api/chat` 进行交互，获取机器人回复。
 */
export async function getTutorReply(userId, message) {
  const response = await fetch(`${process.env.REACT_APP_API_URL || "http://localhost:8000"}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ user_id: userId, message }),
  });

  if (!response.ok) {
    throw new Error(`Server error: ${response.status}`);
  }

  const data = await response.json();
  return data.reply;
} 