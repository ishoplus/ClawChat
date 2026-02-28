# ClawChat

一個輕量的 OpenClaw WebChat 客戶端，使用 Python 後端 + Vue.js 前端。

## 功能

- 🤖 多 Agent 切換
- 💬 會話管理 (Session 持久化)
- 🖼️ 圖片上傳支援
- 📡 SSE 流式輸出
- 🎨 現代化 UI (深色/淺色主題)
- 📊 系統管理面板
- ⏰ 排程管理
- 📝 留言板 / Backlog 看板
- 🔧 檔案瀏覽器

## 截圖

![ClawChat UI](assets/screenshot.png)

## 環境需求

- Python 3.8+
- OpenClaw Gateway 運行中 (Port 18789)

## 快速開始

```bash
# 克隆專案
git clone https://github.com/ishoplus/ClawChat.git
cd ClawChat/web

# 複製環境配置
cp .env.example .env

# 編輯 .env 填入你的 Gateway Token
# GATEWAY_TOKEN=your_token_here

# 啟動服務
python server.py

# 打開瀏覽器訪問
# http://localhost:8093
```

## 配置

### 環境變數

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `PORT` | 8093 | 服務端口 |
| `GATEWAY_URL` | http://127.0.0.1:18789 | OpenClaw Gateway URL |
| `GATEWAY_TOKEN` | (從配置檔讀取) | Gateway 訪問令牌 |
| `OPENCLAW_CONFIG_PATH` | ~/.openclaw/openclaw.json | OpenClaw 配置路徑 |
| `API_KEY` | - | API 認證 Key (可選) |
| `CORS_ORIGINS` | localhost,127.0.0.1 | CORS 允許來源 |

### 啟動方式

```bash
# 方式 1: 使用 .env 文件
python server.py

# 方式 2: 使用環境變數
GATEWAY_TOKEN=your_token python server.py

# 方式 3: 自定義端口
PORT=8094 python server.py
```

## 頁面功能

### 對話頁面
- 選擇不同 Agent 進行對話
- 切換會話 (Session)
- 選擇模型 (MiniMax, GLM, Gemini 等)
- 圖片上傳
- 檔案瀏覽器

### 管理頁面
- Gateway 狀態監控
- Agent 列表
- 活躍 Sessions 列表
- Channels 狀態

### 其他頁面
- 留言板
- 排程管理
- Backlog 看板

## API

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/api/status` | Gateway 狀態 |
| GET | `/api/agents` | Agent 列表 |
| GET | `/api/sessions` | Sessions 列表 |
| GET | `/api/channels` | 頻道狀態 |
| GET | `/api/config` | 配置資訊 |
| GET | `/api/cron` | Cron Jobs |
| GET | `/api/board` | 留言板內容 |
| GET | `/api/backlog` | Backlog 內容 |
| POST | `/api/chat` | 聊天 (支援 SSE 流式) |

## 部署

### 本地訪問

```bash
python server.py
# 訪問 http://localhost:8093
```

### 公開訪問 (ngrok)

```bash
# 啟動 ngrok
ngrok http 8093

# 獲得 public URL
```

## 安全說明

- 敏感 API 端點 (`/api/channels`, `/api/config` 等) 可透過 `API_KEY` 環境變數保護
- CORS 預設僅允許 localhost
- 生產環境建議設置 `API_KEY` 和 `CORS_ORIGINS`

## 技術棧

- **前端**: Vue.js 3 (CDN)
- **後端**: Python 3 + http.server
- **協議**: SSE (Server-Sed Events)

## License

MIT
