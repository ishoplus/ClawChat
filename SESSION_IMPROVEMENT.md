# ClawChat Session 管理改進方案

## 問題 (Problem)

### 現狀
1. **Session Key 格式不標準**
   - ClawChat 前端生成：`session_1709245600000`（時間戳格式）
   - OpenClaw 預期格式：`agent:code:main` 或 `agent:code:dm:<userId>`

2. **dmScope 配置失效**
   - 單人模式下 `dmScope: main` 應該將所有 DM 映射到 `agent:code:main`
   - 但 ClawChat 傳遞非標準格式，導致 Gateway 無法正確處理

3. **創建新對話的行為不符預期**
   - 用戶期望「創建新對話」= 全新上下文
   - 實際可能復用舊 context 或創建隨機 session

### 架構
```
ClawChat 前端 (Vue)
       ↓
Python 後端 (localhost:8093) ← server.py
       ↓
OpenClaw Gateway (localhost:18789)
```

---

## 目的 (Purpose)

1. **保留對話歷史，分開顯示** — 用戶選擇的功能
2. **符合 OpenClaw 規範** — 使用標準 session key 格式
3. **支持 dmScope 配置** — 讓隔離機制正確運作
4. **支持 `/new` 指令** — 讓新對話確實產生新 session

---

## 修改方案 (Solution)

### 方案：不改 Gateway，純前端 + 後端改動

#### 1. ClawChat 前端 (`stores/chat.ts`)

**創建新對話**
```typescript
// 改為發送 /new 指令觸發 Gateway 創建新 session
const createNewSession = async () => {
  // 發送 /new 指令
  await fetch('/api/chat', {
    method: 'POST',
    body: JSON.stringify({
      model: `openclaw:${selectedAgent.value.id}`,
      messages: [{ role: 'user', content: '/new' }],
      stream: false
    })
  })
  
  // 等待一下讓 Gateway 完成 session 創建
  await new Promise(r => setTimeout(r, 500))
  
  // 刷新 session 列表，獲取最新的 session
  await fetchSessions()
}
```

**發送訊息**
```typescript
// 使用正確的 user 參數
const currentSessionData = sessions.value.find(s => s.key === currentSession.value)

await fetch('/api/chat', {
  body: JSON.stringify({
    model: `openclaw:${selectedAgent.value.id}`,
    messages: [...],
    user: currentSessionData?.agentId || selectedAgent.value.id  // 👈 改為 agentId
  })
})
```

#### 2. Session 列表獲取

保持使用 `/api/sessions`，它已經返回正確的 Gateway session 數據：

```typescript
const fetchSessions = async () => {
  const res = await fetch('/api/sessions')
  const data = await res.json()
  
  sessions.value = data.sessions.map((s: any) => ({
    id: s.sessionId,
    key: s.key,
    name: s.name || s.label || '新對話',
    agentId: s.agentId
  }))
}
```

---

## 預期結果

| 功能 | 改進前 | 改進後 |
|-----|-------|-------|
| Session Key | `session_{timestamp}` | `agent:code:main` (從 Gateway 獲取) |
| 創建新對話 | 前端本地生成 | 觸發 `/new` 指令 |
| 對話歷史 | localStorage | Gateway 真實存儲 |
| dmScope | ❌ 無效 | ✅ 正確運作 |
| 多對話支援 | ❌ 不完整 | ✅ 完整支持 |

---

## 待確認事項

1. Gateway 的 `/api/chat` 對 `user` 參數的處理邏輯
2. `/new` 指令執行後 session 列表的更新時機
3. 是否需要後端 API 支援（如 `/api/sessions/new`）

---

## 相關檔案

- 前端：`/Users/showang/.openclaw/workspaces/code/ClawChat/web/src/stores/chat.ts`
- 後端：`/Users/showang/.openclaw/workspaces/code/ClawChat/web-old/server.py`
