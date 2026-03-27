# OpenClaw 配置文檔

## 文件位置

```
~/.openclaw/openclaw.json
```

---

## 配置區塊總覽

| 區塊 | 說明 |
|------|------|
| `meta` | 版本資訊 |
| `wizard` | 初始設定精靈 |
| `auth` | API 認證配置 |
| `models` | AI 模型配置 |
| `agents` | Agent 列表 |
| `tools` | 工具開關 |
| `bindings` | Agent-頻道綁定 |
| `messages` | 訊息配置 |
| `commands` | 命令配置 |
| `session` | 會話配置 |
| `hooks` | 內部鉤子 |
| `channels` | 通訊頻道 |
| `gateway` | Gateway 服務 |
| `plugins` | 插件配置 |

---

## 1. gateway - Gateway 服務配置

```json
{
  "gateway": {
    "port": 18789,
    "mode": "local",
    "bind": "loopback",
    "controlUi": {
      "allowedOrigins": ["*"]
    },
    "auth": {
      "mode": "token",
      "token": "your-token-here"
    },
    "tailscale": {
      "mode": "off",
      "resetOnExit": false
    },
    "http": {
      "endpoints": {
        "chatCompletions": {
          "enabled": true
        }
      }
    }
  }
}
```

| 欄位 | 類型 | 說明 |
|------|------|------|
| `port` | number | Gateway 服務端口，預設 18789 |
| `mode` | string | 運行模式 (local/remote) |
| `bind` | string | 綁定地址 (loopback/0.0.0.0) |
| `auth.mode` | string | 認證模式 (token) |
| `auth.token` | string | 訪問令牌 |
| `tailscale.mode` | string | Tailscale 模式 (off/on) |

---

## 2. channels - 通訊頻道配置

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "dmPolicy": "pairing",
      "groupPolicy": "allowlist",
      "streaming": "off",
      "accounts": {
        "main": {
          "enabled": true,
          "dmPolicy": "allowlist",
          "botToken": "YOUR_BOT_TOKEN",
          "allowFrom": ["USER_ID"],
          "groupPolicy": "allowlist",
          "streaming": "off"
        }
      }
    }
  }
}
```

### 政策選項

| 選項 | 說明 |
|------|------|
| `dmPolicy` | 私訊策略 (pairing/allowlist/block) |
| `groupPolicy` | 群組策略 (allowlist/block) |
| `streaming` | 串流模式 (off/on) |

---

## 3. agents - Agent 配置

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "minimax-portal/MiniMax-M2.1"
      },
      "models": {
        "minimax-portal/MiniMax-M2.5": {
          "alias": "minimax-m2.5"
        }
      },
      "workspace": "/path/to/workspace",
      "memorySearch": {
        "enabled": true,
        "sources": ["memory"]
      },
      "maxConcurrent": 4
    },
    "list": [
      {
        "id": "code",
        "name": "code",
        "workspace": "/path/to/workspace",
        "agentDir": "/path/to/agent/dir",
        "identity": {
          "name": "Code",
          "theme": "Technical, Precise, Efficient.",
          "emoji": "💻"
        },
        "model": {
          "primary": "minimax-portal/MiniMax-M2.1"
        }
      }
    ]
  }
}
```

### Agent 欄位說明

| 欄位 | 類型 | 說明 |
|------|------|------|
| `id` | string | Agent 唯一識別碼 |
| `name` | string | Agent 名稱 |
| `workspace` | string | 工作目錄路徑 |
| `agentDir` | string | Agent 程式碼目錄 |
| `identity.name` | string | 顯示名稱 |
| `identity.emoji` | string | 表情符號 |
| `identity.theme` | string | 描述主題 |
| `model.primary` | string | 預設模型 ID |

---

## 4. models - AI 模型供應商

```json
{
  "models": {
    "mode": "merge",
    "providers": {
      "ollama": {
        "baseUrl": "http://localhost:11434",
        "apiKey": "ollama",
        "models": [
          {
            "id": "llava:latest",
            "name": "LLaVA",
            "reasoning": false,
            "input": ["image", "text"],
            "cost": { "input": 0, "output": 0 },
            "contextWindow": 200000,
            "maxTokens": 8192
          }
        ]
      },
      "minimax-portal": {
        "baseUrl": "https://api.minimaxi.com/anthropic",
        "apiKey": "minimax-oauth",
        "api": "anthropic-messages",
        "models": [...]
      }
    }
  }
}
```

### 供應商類型

| 供應商 | 說明 |
|--------|------|
| `ollama` | 本地模型 |
| `minimax-portal` | MiniMax API |
| `google` | Google Gemini |
| `zai` | ZAI API |

### 模型欄位

| 欄位 | 說明 |
|------|------|
| `id` | 模型 ID |
| `name` | 顯示名稱 |
| `reasoning` | 是否支援推理 |
| `input` | 輸入類型 (text, image) |
| `contextWindow` | 上下文窗口大小 |
| `maxTokens` | 最大輸出 tokens |

---

## 5. plugins - 插件配置

```json
{
  "plugins": {
    "entries": {
      "telegram": {
        "enabled": true
      },
      "brave": {
        "enabled": true,
        "config": {
          "webSearch": {
            "apiKey": "YOUR_API_KEY"
          }
        }
      },
      "minimax": {
        "enabled": true
      }
    }
  }
}
```

### 內置插件

| 插件 | 說明 |
|------|------|
| `telegram` | Telegram 頻道支援 |
| `brave` | Brave 網路搜尋 |
| `minimax` | MiniMax API 支援 |
| `minimax-portal-auth` | MiniMax OAuth 認證 |

---

## 6. tools - 工具開關

```json
{
  "tools": {
    "web": {
      "search": { "enabled": true },
      "fetch": { "enabled": true }
    },
    "media": {
      "image": { "enabled": true }
    }
  }
}
```

---

## 7. bindings - Agent 頻道綁定

```json
{
  "bindings": [
    {
      "agentId": "code",
      "match": {
        "channel": "telegram",
        "accountId": "code"
      }
    }
  ]
}
```

---

## 8. auth - API 認證配置

```json
{
  "auth": {
    "profiles": {
      "zai:default": {
        "provider": "zai",
        "mode": "api_key"
      },
      "minimax-portal:default": {
        "provider": "minimax-portal",
        "mode": "oauth"
      }
    }
  }
}
```

---

## 9. 其他配置

### messages - 訊息配置
```json
{
  "messages": {
    "ackReactionScope": "group-mentions"
  }
}
```

### commands - 命令配置
```json
{
  "commands": {
    "native": "auto",
    "nativeSkills": "auto",
    "restart": true,
    "ownerDisplay": "raw"
  }
}
```

### session - 會話配置
```json
{
  "session": {
    "dmScope": "per-channel-peer"
  }
}
```

### hooks - 內部鉤子
```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "self-improvement": {
          "enabled": true
        }
      }
    }
  }
}
```

---

## 完整範例

```json
{
  "meta": {
    "lastTouchedVersion": "2026.3.23-2"
  },
  "gateway": {
    "port": 18789,
    "mode": "local",
    "bind": "loopback",
    "auth": {
      "mode": "token",
      "token": "your-token"
    }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "accounts": {
        "main": {
          "enabled": true,
          "botToken": "BOT_TOKEN",
          "allowFrom": ["USER_ID"]
        }
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "minimax-portal/MiniMax-M2.1"
      },
      "workspace": "/path/to/workspace"
    },
    "list": [
      {
        "id": "main",
        "name": "Main Agent",
        "workspace": "/path/to/workspace",
        "identity": {
          "name": "Main",
          "emoji": "⚡️"
        }
      }
    ]
  },
  "models": {
    "providers": {
      "minimax-portal": {
        "baseUrl": "https://api.minimaxi.com/anthropic",
        "models": [...]
      }
    }
  },
  "plugins": {
    "entries": {
      "brave": { "enabled": true }
    }
  }
}
```
