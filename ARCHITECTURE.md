# ClawChat 架構文檔

## 系統概覽

```
┌─────────────────────────────────────────────────────────────────┐
│                        ClawChat                                  │
│                                                                 │
│  ┌─────────────────┐      ┌─────────────────┐                   │
│  │   Vue.js 前端   │      │  Python 後端    │                   │
│  │   (瀏覽器)      │ ←──→ │  (server.py)   │                   │
│  │   localhost:8093│      │  localhost:8093│                   │
│  └─────────────────┘      └────────┬────────┘                   │
│                                    │                             │
│                           Vite Proxy                           │
│                           (/api/*)                              │
│                                    │                             │
└────────────────────────────────────┼────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OpenClaw Gateway                             │
│                        localhost:18789                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Session 管理 │  │   Agent 調度  │  │  Tool 執行    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    外部渠道                                      │
│     Telegram | Discord | WhatsApp | Signal | ...              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 技術棧

| 層面 | 技術 | 說明 |
|-----|------|------|
| 前端 | Vue.js 3 + Pinia | 響應式 UI，狀態管理 |
| 構建工具 | Vite | 開發伺服器 + 代理 |
| 後端 | Python 3 + http.server | HTTP API 代理 |
| 協議 | SSE | 服務器推送流式響應 |
| 目標 | OpenClaw Gateway | AI Agent 運行時 |

---

## 目錄結構

```
ClawChat/
├── web/                      # 主項目 (Vue + Python)
│   ├── src/
│   │   ├── App.vue           # 根組件
│   │   ├── main.ts           # 入口
│   │   ├── stores/
│   │   │   └── chat.ts       # 狀態管理 (Pinia)
│   │   ├── components/       # UI 組件
│   │   ├── views/           # 頁面視圖
│   │   ├── types/           # TypeScript 類型
│   │   └── style.css        # 全局樣式
│   ├── public/              # 靜態資源
│   ├── dist/                # 構建產出
│   ├── server.py            # Python 後端
│   ├── vite.config.ts       # Vite 配置
│   └── package.json         # 依賴
│
├── web-old/                 # 舊版純前端 (CDN)
│   └── server.py            # 簡化版後端
│
├── assets/                  # 截圖等資源
├── README.md               # 項目說明
└── SESSION_IMPROVEMENT.md  # Session 改進方案
```

---

## 前端架構 (Vue.js)

### 核心狀態 (`stores/chat.ts`)

```typescript
// 主要狀態
selectedAgent     // 當前選擇的 Agent
selectedModel     // 當前選擇的模型
messages          // 當前對話訊息
sessions          // 對話列表
currentSession    // 當前會話 ID

// 功能
fetchSessions()   // 獲取 session 列表
sendMessage()     // 發送訊息
createNewSession() // 創建新對話
switchSession()   // 切換會話
```

### 頁面結構

```
App.vue
├── Sidebar.vue              # 左側邊欄 (會話列表)
├── ChatView.vue             # 對話主區域
│   ├── MessageList.vue      # 訊息列表
│   ├── MessageInput.vue     # 輸入框
│   └── ChatHeader.vue       # 頂部標題
├── BoardView.vue            # 留言板
├── ScheduleView.vue         # 排程管理
└── ManageView.vue           # 系統管理
```

---

## 後端架構 (Python server.py)

### 核心功能

```
server.py
├── GET  /api/*              # 查詢端點
├── POST /api/chat           # 聊天入口 (轉發 Gateway)
├── POST /v1/responses      # OpenClaw Web UI 兼容
└── 靜態文件服務             # Vue 構建產出
```

### API 端點詳解

| 端點 | 說明 | 數據來源 |
|------|------|---------|
| `GET /api/status` | Gateway 狀態 | 配置文件 + subprocess |
| `GET /api/agents` | Agent 列表 | 配置文件 |
| `GET /api/sessions` | 會話列表 | `openclaw sessions --json` |
| `GET /api/channels` | 頻道狀態 | 配置文件 |
| `GET /api/config` | 完整配置 | 配置文件 |
| `GET /api/session/{id}/messages` | 訊息歷史 | 本地 JSONL 文件 |
| `GET /api/cron` | Cron Jobs | `~/.openclaw/cron/jobs.json` |
| `GET /api/board` | 留言板 | `~/.openclaw/workspaces/shared/BOARD.md` |
| `POST /api/chat` | 聊天 | 轉發到 Gateway |

### 訊息流轉

```python
# 1. 接收前端請求
POST /api/chat
  → body: { model, messages, stream, user }

# 2. 轉發到 Gateway
urllib.request.Request(
    f"{GATEWAY_URL}/v1/chat/completions",
    data=body,
    headers={ 'Authorization': f'Bearer {GATEWAY_TOKEN}' }
)

# 3. 流式返回 (SSE)
if stream:
    while chunk := gateway_resp.read(16384):
        self.wfile.write(chunk)  # 直接轉發
```

---

## Session 管理機制

### 當前實現

```
ClawChat 前端                    Python 後端                   Gateway
     │                              │                            │
     │ GET /api/sessions           │                            │
     ├─────────────────────────────→│                            │
     │                             │ openclaw sessions --json   │
     │                             ├───────────────────────────→│
     │                             │←───────────────────────────┤
     │←────────────────────────────┤                            │
     │ sessions: [                  │                            │
     │   { key, sessionId, ... }   │                            │
     │ ]                           │                            │
     │                              │                            │
     │ POST /api/chat              │                            │
     │   user: "session_xxx"      │                            │
     ├─────────────────────────────→│                            │
     │                             │ /v1/chat/completions       │
     │                             ├───────────────────────────→│
     │←────────────────────────────┤                            │
```

### Session Key 格式問題

| 來源 | Key 格式 | 說明 |
|-----|---------|------|
| Gateway 預期 | `agent:code:main` | 標準格式 |
| Gateway 預期 | `agent:code:dm:userId` | DM 隔離格式 |
| ClawChat 產生 | `session_{timestamp}` | 非標準 |

---

## 配置管理

### 環境變數

```bash
PORT=8093                      # 服務端口
GATEWAY_URL=http://127.0.0.1:18789  # Gateway 地址
GATEWAY_TOKEN=xxx              # 認證令牌
OPENCLAW_CONFIG_PATH=~/.openclaw/openclaw.json  # 配置路徑
API_KEY=                       # API 認證 (可選)
CORS_ORIGINS=localhost,127.0.0.1  # CORS 允許
```

### 配置文件讀取

```python
# 從 ~/.openclaw/openclaw.json 讀取
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

# 使用
gateway.auth.token           # Gateway 認證
agents.list                  # Agent 列表
channels                    # 頻道配置
```

---

## 部署模式

### 開發模式

```bash
cd ClawChat/web
npm install
npm run dev   # Vite 開發伺服器 (port 5173)
              # 代理 /api/* 到 localhost:8093

# 另起終端
python server.py  # Python 後端 (port 8093)
```

### 生產模式

```bash
# 1. 構建 Vue
npm run build

# 2. 啟動後端 (服務靜態文件 + API)
python server.py  # static files from ./dist
```

### 公開訪問

```bash
# ngrok 穿透
ngrok http 8093
```

---

## 安全考量

| 項目 | 當前狀態 | 建議 |
|-----|---------|------|
| CORS | 僅 localhost | 生產環境限制來源 |
| API Key | 可選 | 敏感端點建議開啟 |
| Gateway Token | 配置文件讀取 | 妥善保管 |
| 靜態文件 | 無認證 | 可考慮添加 |

---

## 相關檔案路徑

- 前端：`/Users/showang/.openclaw/workspaces/code/ClawChat/web/src/`
- 後端：`/Users/showang/.openclaw/workspaces/code/ClawChat/web-old/server.py`
- 配置：`~/.openclaw/openclaw.json`
- Sessions：`~/.openclaw/agents/<agentId>/sessions/`
- 工作區：`~/.openclaw/workspaces/code/`
