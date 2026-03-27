# ClawChat 啟動說明

## 組件

| 組件 | 目錄 | Port | 命令 |
|------|------|------|------|
| 前端 (Vite) | `ClawChat/web` | 5173 | `npm run dev` |
| 後端 (Python) | `ClawChat/server` | 8093 | `python3 server.py` |

## 啟動步驟

### 1. 啟動後端

```bash
cd /Users/showang/.openclaw/workspaces/code/ClawChat/server
python3 server.py
```

### 2. 啟動前端

```bash
cd /Users/showang/.openclaw/workspaces/code/ClawChat/web
npm run dev
```

### 3. 訪問

- **網址:** http://localhost:5173
- **API 代理:** Vite 自動將 `/api` 請求轉發到後端 (localhost:8093)

## 停止服務

- 前端: `Ctrl+C` 或關閉 terminal
- 後端: `Ctrl+C` 或 `kill <PID>`

## 狀態檢查

```bash
# 後端
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8093
# 預期輸出: 200

# 前端
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5173
# 預期輸出: 200
```

## 架構說明

```
用戶瀏覽器
    │
    ▼
http://localhost:5173 (Vite 前端)
    │
    │ /api 代理
    ▼
http://localhost:8093 (Python 後端)
    │
    │ WebSocket + HTTP
    ▼
OpenClaw Gateway (127.0.0.1:18789)
```
