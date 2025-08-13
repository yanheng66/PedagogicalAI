# Firebase 本地配置指南

## 1. 后端 Firebase Service Account 配置

### 方法一：下载新的Service Account文件（推荐）

1. 访问 [Firebase Console](https://console.firebase.google.com/)
2. 选择项目：`pedai-8a999`
3. 点击设置齿轮 ⚙️ > 项目设置
4. 切换到"服务账号"标签页
5. 点击"生成新的私钥"
6. 下载JSON文件并重命名为 `firebase_service_account.json`
7. 将文件放在项目根目录（与README.md同级）

### 方法二：使用环境变量

创建 `.env` 文件在项目根目录：

```bash
# Backend Firebase Service Account
FIREBASE_ADMIN_SA=./firebase_service_account.json
# 或者使用Google Cloud标准环境变量
GOOGLE_APPLICATION_CREDENTIALS=./firebase_service_account.json
```

## 2. 前端 Firebase Web配置

在 `frontend/` 目录创建 `.env` 文件：

```bash
# 从Firebase控制台 > 项目设置 > 一般 > 您的应用 > Firebase SDK snippet > 配置
REACT_APP_FIREBASE_API_KEY=your_api_key_here
REACT_APP_FIREBASE_AUTH_DOMAIN=pedai-8a999.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=pedai-8a999
REACT_APP_FIREBASE_STORAGE_BUCKET=pedai-8a999.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your_sender_id_here
REACT_APP_FIREBASE_APP_ID=your_app_id_here
```

## 3. 获取前端配置信息

1. 在Firebase Console中，点击项目设置
2. 滚动到"您的应用"部分
3. 如果还没有Web应用，点击"添加应用" > Web
4. 复制配置对象中的值到前端.env文件

## 4. 验证配置

运行以下命令检查配置是否正确：

### 后端测试：
```bash
cd backend
node -e "const { writeToCollection } = require('./firestoreHelper'); console.log('Firebase backend configured successfully!');"
```

### 前端测试：
```bash
cd frontend
npm start
# 检查浏览器控制台是否有Firebase配置日志
```

## 5. 安全注意事项

- ✅ `firebase_service_account.json` 已添加到 `.gitignore`
- ✅ 永远不要提交服务账号密钥到GitHub
- ✅ 前端的API Key是公开的，这是正常的
- ✅ 使用Firebase Security Rules保护数据

## 故障排除

如果遇到权限错误：
1. 确保Service Account有Firestore权限
2. 检查Firebase项目是否启用了Firestore
3. 验证文件路径是否正确 