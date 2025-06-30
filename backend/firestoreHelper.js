/**
 * backend/firestoreHelper.js
 * 统一封装 Firestore Admin SDK 读写函数，供本目录下其他脚本使用。
 */
const { initializeApp, cert } = require("firebase-admin/app");
const { getFirestore } = require("firebase-admin/firestore");
const fs = require("fs");
const path = require("path");
const dotenv = require("dotenv");

// 加载根目录的 .env 文件
dotenv.config({ path: path.join(__dirname, "..", ".env") });

// ---------------------------------------------------------------------------
// 初始化
// ---------------------------------------------------------------------------
if (!global._firebaseAppInstance) {
  // 1) 尝试读取环境变量 JSON
  let credentialsPath = process.env.FIREBASE_ADMIN_SA || process.env.GOOGLE_APPLICATION_CREDENTIALS;

  // 如果 credentialsPath 是一个相对路径 (例如 './firebase_service_account.json')，
  // 将它解析为相对于项目根目录的绝对路径
  if (credentialsPath && !path.isAbsolute(credentialsPath)) {
    credentialsPath = path.join(__dirname, "..", credentialsPath);
  }

  // 2) 若未设置环境变量，尝试默认的项目根目录路径
  if (!credentialsPath) {
    const candidate = path.join(__dirname, "..", "firebase_service_account.json");
    if (fs.existsSync(candidate)) {
      credentialsPath = candidate;
    }
  }

  if (!credentialsPath || !fs.existsSync(credentialsPath)) {
    throw new Error(
      `找不到 Firebase 服务账号 JSON，请检查 .env 文件和路径: ${credentialsPath}`
    );
  }

  // 初始化 Firebase Admin
  const serviceAccount = require(credentialsPath);

  global._firebaseAppInstance = initializeApp({
    credential: cert(serviceAccount),
  });
}

const db = getFirestore();

// ---------------------------------------------------------------------------
// 导出帮助函数
// ---------------------------------------------------------------------------
/**
 * 写入数据到指定集合，自动生成 docId。
 * @param {string} collectionName
 * @param {object} data
 * @returns {Promise<string>} 新文档 id
 */
async function writeToCollection(collectionName, data) {
  const ref = await db.collection(collectionName).add(data);
  return ref.id;
}

/**
 * 读取集合全部文档
 * @param {string} collectionName
 * @returns {Promise<Array<object>>}
 */
async function getAllDocs(collectionName) {
  const snapshot = await db.collection(collectionName).get();
  return snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
}

module.exports = {
  writeToCollection,
  getAllDocs,
  db,
}; 