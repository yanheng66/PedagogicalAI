/**
 * utils/lessonContent.js
 * 从后端请求指定课程步骤的动态文本内容。
 */

// FastAPI服务器地址
const FASTAPI_BASE_URL = 'http://localhost:8000';

export async function fetchLessonStepContent(concept, stepId) {
  const response = await fetch(`/api/lesson_content`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ concept, step_id: stepId }),
  });
  if (!response.ok) {
    throw new Error(`无法获取课程内容：${response.status}`);
  }
  const data = await response.json();
  return data.content;
}

export async function fetchMCQData(topic) {
  const response = await fetch(`${FASTAPI_BASE_URL}/api/step2`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, user_id: "guest" }), // user_id is a placeholder for now
  });
  if (!response.ok) {
    throw new Error(`无法获取 MCQ 数据：${response.status}`);
  }
  return await response.json();
}

export async function fetchStep3TaskData(topic) {
  const response = await fetch(`${FASTAPI_BASE_URL}/api/step3`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, user_id: "guest" }),
  });
  if (!response.ok) {
    throw new Error(`无法获取 Step 3 任务数据：${response.status}`);
  }
  return await response.json();
}

export async function submitStep3Solution(userId, query, explanation) {
  const response = await fetch(`${FASTAPI_BASE_URL}/api/step3/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, query, explanation }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred' }));
    throw new Error(`无法提交解答：${response.status} - ${errorData.detail}`);
  }
  return await response.json();
}

export async function fetchStep4ChallengeData(userId) {
  const response = await fetch(`${FASTAPI_BASE_URL}/api/step4`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId }),
  });
  if (!response.ok) {
    throw new Error(`无法获取 Step 4 挑战数据：${response.status}`);
  }
  return await response.json();
}

export async function fetchStep5Poem(userId, topic) {
  const response = await fetch(`${FASTAPI_BASE_URL}/api/step5`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, topic }),
  });
  if (!response.ok) {
    throw new Error(`无法获取 Step 5 诗歌：${response.status}`);
  }
  return await response.json();
} 