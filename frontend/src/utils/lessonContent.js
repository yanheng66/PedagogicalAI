/**
 * utils/lessonContent.js
 * 从后端请求指定课程步骤的动态文本内容。
 */
export async function fetchLessonStepContent(concept, stepId) {
  const response = await fetch(`${process.env.REACT_APP_API_URL || "http://localhost:8000"}/api/lesson_content`, {
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