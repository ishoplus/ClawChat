#!/usr/bin/env python3
"""
ClawChat Server - HTTP + API proxy for OpenClaw Gateway
"""
import http.server
import socketserver
import json
import urllib.request
import urllib.error
import os
import time

PORT = int(os.environ.get('PORT', 8093))
GATEWAY_URL = os.environ.get('GATEWAY_URL', 'http://127.0.0.1:18789')
CONFIG_PATH = os.path.expanduser(os.environ.get('OPENCLAW_CONFIG_PATH', '~/.openclaw/openclaw.json'))

# 從配置檔讀取 token
def get_gateway_token():
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        return config.get('gateway', {}).get('auth', {}).get('token', '')
    except:
        return ''

GATEWAY_TOKEN = os.environ.get('GATEWAY_TOKEN', get_gateway_token())

# API Key for authentication (optional - set to protect API endpoints)
API_KEY = os.environ.get('API_KEY', '')
# CORS allowed origins (comma-separated, default: localhost only)
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'localhost,127.0.0.1').split(',')

def get_allowed_origin(origin=None):
    """取得允許的 CORS origin"""
    if not origin:
        return CORS_ORIGINS[0] if CORS_ORIGINS else '*'
    # 檢查 origin 是否在允許列表中
    for allowed in CORS_ORIGINS:
        if allowed.strip() in origin or allowed == '*':
            return origin
    return None

def check_api_key(headers):
    """檢查 API Key認證"""
    if not API_KEY:
        return True  # 未設置 API Key 時，跳過認證
    auth_header = headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
        if token == API_KEY:
            return True
    return False

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 快取配置
CACHE_TTL = 30  # 快取有效期（秒）
_cache = {}

def get_cached(key, fetch_func, ttl=CACHE_TTL):
    """簡單的記憶體快取"""
    now = time.time()
    if key in _cache:
        data, timestamp = _cache[key]
        if now - timestamp < ttl:
            return data
    # 重新取得
    data = fetch_func()
    _cache[key] = (data, now)
    return data

def clear_cache():
    """清除快取"""
    global _cache
    _cache = {}

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SCRIPT_DIR, **kwargs)
        # 取得請求的 Origin
        self._request_origin = ''
    
    def end_headers(self):
        # 動態設定 CORS Origin
        if not self._request_origin:
            self._request_origin = self.headers.get('Origin', '')
        allowed_origin = get_allowed_origin(self._request_origin)
        if allowed_origin:
            self.send_header('Access-Control-Allow-Origin', allowed_origin)
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_GET(self):
        # 每次請求更新 Origin
        self._request_origin = self.headers.get('Origin', '')
        
        # 敏感端點需要 API Key 認證
        sensitive_paths = ['/api/channels', '/api/config', '/api/board', '/api/cron', '/api/backlog']
        needs_auth = any(self.path.startswith(p) for p in sensitive_paths)
        
        if needs_auth and not check_api_key(self.headers):
            self.send_error(401, 'Unauthorized')
            return
        
        if self.path == '/api/status':
            self.send_json_response(self.get_status())
        elif self.path == '/api/agents':
            self.send_json_response(self.get_agents())
        elif self.path == '/api/channels':
            self.send_json_response(self.get_channels())
        elif self.path == '/api/config':
            self.send_json_response(self.get_config())
        elif self.path == '/api/sessions':
            self.send_json_response(self.get_sessions())
        elif self.path.startswith('/api/agent/'):
            parts = self.path.split('/')
            # parts: ['', 'api', 'agent', '<agent_id>', 'files', ...]
            agent_id = parts[3] if len(parts) > 3 else None
            if not agent_id:
                self.send_json_response({"error": "Missing agent ID"})
                return
            
            if len(parts) > 4 and parts[4].startswith('files'):
                # 取得 query string 中的 path 參數
                file_path = ''
                if '?' in self.path:
                    from urllib.parse import parse_qs, urlparse
                    parsed = urlparse(self.path)
                    file_path = parse_qs(parsed.query).get('path', [''])[0]
                
                if file_path:
                    # 檢查是檔案還是目錄
                    import os
                    workspace = None
                    with open(CONFIG_PATH, 'r') as f:
                        config = json.load(f)
                    agents_list = config.get('agents', {}).get('list', [])
                    for a in agents_list:
                        if a.get('id') == agent_id:
                            workspace = a.get('workspace', '')
                            break
                    
                    if workspace:
                        full_path = os.path.join(workspace, file_path)
                        if os.path.isdir(full_path):
                            # 是目錄，列出內容
                            self.send_json_response(self.list_agent_files(agent_id, file_path))
                        elif os.path.isfile(full_path):
                            # 是檔案，讀取內容
                            self.send_json_response(self.read_agent_file(agent_id, file_path))
                        else:
                            self.send_json_response({"error": "Path not found"})
                    else:
                        self.send_json_response({"error": "Workspace not found"})
                else:
                    # 列出所有檔案
                    self.send_json_response(self.list_agent_files(agent_id))
            else:
                self.send_json_response(self.get_agent_detail(agent_id))
        elif self.path == '/api/ngrok/start':
            self.send_json_response(self.start_ngrok())
        elif self.path == '/api/board':
            self.send_json_response(self.get_board())
        elif self.path == '/api/backlog':
            self.send_json_response(self.get_backlog())
        elif self.path.startswith('/api/board/'):
            # 讀取留言板相關檔案
            filename = self.path.replace('/api/board/', '')
            self.send_board_file(filename)
        elif self.path == '/api/schedules':
            self.send_json_response(self.get_schedules())
        elif self.path == '/api/cron':
            self.send_json_response(self.get_crons())
        else:
            super().do_GET()
    
    def send_json_response(self, data):
        result = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(result))
        self.end_headers()
        self.wfile.write(result)
    
    def get_status(self):
        """取得 Gateway 狀態"""
        import subprocess
        try:
            # 檢查 ngrok 狀態
            ngrok_url = None
            try:
                result = subprocess.run(['curl', '-s', 'localhost:4040/api/tunnels'], 
                                      capture_output=True, timeout=2)
                if result.returncode == 0:

                    tunnels = json.loads(result.stdout)
                    for tunnel in tunnels.get('tunnels', []):
                        if tunnel.get('proto') == 'https':
                            ngrok_url = tunnel.get('public_url')
                            break
            except:
                pass
            
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
            
            gateway = config.get('gateway', {})
            return {
                "status": "online",
                "gateway": {
                    "port": gateway.get('port', 18789),
                    "httpPort": gateway.get('http', {}).get('port', 18789),
                },
                "ngrokUrl": ngrok_url,
                "uptime": "N/A",
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def start_ngrok(self):
        """啟動 ngrok"""
        import subprocess
        import os
        try:
            # 檢查是否已運行
            result = subprocess.run(['curl', '-s', 'localhost:4040/api/tunnels'], 
                                  capture_output=True, timeout=2)
            if result.returncode == 0:

                tunnels = json.loads(result.stdout)
                for tunnel in tunnels.get('tunnels', []):
                    if tunnel.get('proto') == 'https':
                        return {"ngrokUrl": tunnel.get('public_url'), "status": "already running"}
            
            # 啟動 ngrok
            subprocess.Popen(['ngrok', 'http', '8095'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            return {"status": "starting", "message": "正在啟動 ngrok..."}
        except Exception as e:
            return {"error": str(e)}
    
    def get_board(self):
        """取得留言板內容"""
        import os
        try:
            board_path = os.path.expanduser('~/.openclaw/workspaces/shared/BOARD.md')
            if os.path.isfile(board_path):
                with open(board_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"content": content}
            else:
                return {"content": "", "error": "Board file not found"}
        except Exception as e:
            return {"content": "", "error": str(e)}
    
    def get_backlog(self):
        """取得 Backlog 看板內容"""
        import os
        try:
            backlog_path = os.path.expanduser('~/.openclaw/workspaces/shared/BACKLOG.md')
            if os.path.isfile(backlog_path):
                with open(backlog_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"content": content}
            else:
                return {"content": "", "error": "Backlog file not found"}
        except Exception as e:
            return {"content": "", "error": str(e)}
    
    def send_board_file(self, filename):
        """取得留言板相關檔案"""
        import os
        try:
            # 防止目錄遍歷攻擊
            filename = os.path.basename(filename)
            file_path = os.path.expanduser(f'~/.openclaw/workspaces/shared/{filename}')
            
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.send_json_response({"content": content})
            else:
                self.send_json_response({"error": "File not found"})
        except Exception as e:
            self.send_json_response({"error": str(e)})
    
    def get_schedules(self):
        """取得所有 Agent 的排程資訊"""
        import os
        import glob
        try:
            schedules = []
            workspaces_path = os.path.expanduser('~/.openclaw/workspaces')
            
            # 讀取每個 workspace 的 HEARTBEAT.md
            for workspace_dir in os.listdir(workspaces_path):
                workspace_full = os.path.join(workspaces_path, workspace_dir)
                if not os.path.isdir(workspace_full):
                    continue
                
                heartbeat_path = os.path.join(workspace_full, 'HEARTBEAT.md')
                identity_path = os.path.join(workspace_full, 'IDENTITY.md')
                
                agent_name = workspace_dir
                agent_emoji = '🤖'
                
                # 嘗試讀取 IDENTITY.md 獲取名稱
                if os.path.isfile(identity_path):
                    try:
                        with open(identity_path, 'r') as f:
                            content = f.read()
                            # 解析 IDENTITY.md 格式: - **Name:** Coder
                            for line in content.split('\n'):
                                line = line.strip()
                                # 移除 leading - 或 * 
                                if line.startswith('- ') or line.startswith('* '):
                                    line = line[2:].strip()
                                if line.startswith('**Name:**'):
                                    agent_name = line.split('**Name:**')[1].strip()
                                elif line.startswith('**Emoji:**'):
                                    agent_emoji = line.split('**Emoji:**')[1].strip()
                    except:
                        pass
                
                # 讀取 HEARTBEAT.md
                has_schedule = False
                tasks = []
                if os.path.isfile(heartbeat_path):
                    with open(heartbeat_path, 'r') as f:
                        content = f.read()
                        # 檢查是否有實際內容（非僅註釋）
                        lines = [l.strip() for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]
                        if lines:
                            has_schedule = True
                            tasks = lines
                
                schedules.append({
                    "workspace": workspace_dir,
                    "name": agent_name,
                    "emoji": agent_emoji,
                    "hasSchedule": has_schedule,
                    "tasks": tasks
                })
            
            return {"schedules": schedules}
        except Exception as e:
            return {"schedules": [], "error": str(e)}
    
    def get_crons(self):
        """取得 Cron Jobs"""
        import os

        try:
            cron_path = os.path.expanduser('~/.openclaw/cron/jobs.json')
            if os.path.isfile(cron_path):
                with open(cron_path, 'r') as f:
                    data = json.load(f)
                
                jobs = []
                for job in data.get('jobs', []):
                    schedule = job.get('schedule', {})
                    state = job.get('state', {})
                    payload = job.get('payload', {})
                    delivery = job.get('delivery', {})
                    
                    # 格式化時間
                    from datetime import datetime
                    next_run = None
                    last_run = None
                    if state.get('nextRunAtMs'):
                        next_run = datetime.fromtimestamp(state['nextRunAtMs'] / 1000).strftime('%Y-%m-%d %H:%M')
                    if state.get('lastRunAtMs'):
                        last_run = datetime.fromtimestamp(state['lastRunAtMs'] / 1000).strftime('%Y-%m-%d %H:%M')
                    
                    # 格式化執行時長
                    last_duration_ms = state.get('lastDurationMs')
                    last_duration = None
                    if last_duration_ms:
                        if last_duration_ms < 1000:
                            last_duration = f"{last_duration_ms}ms"
                        elif last_duration_ms < 60000:
                            last_duration = f"{last_duration_ms/1000:.1f}秒"
                        else:
                            last_duration = f"{last_duration_ms/60000:.1f}分"
                    
                    # 取得提示詞 (可選截斷長內容)
                    message = payload.get('message', '')
                    message_preview = message[:200] + '...' if len(message) > 200 else message
                    
                    jobs.append({
                        "id": job.get('id'),
                        "name": job.get('name'),
                        "description": job.get('description', ''),
                        "enabled": job.get('enabled', True),
                        "schedule": schedule.get('expr', ''),
                        "scheduleKind": schedule.get('kind', 'cron'),
                        "tz": schedule.get('tz', 'UTC'),
                        "nextRun": next_run,
                        "lastRun": last_run,
                        "lastStatus": state.get('lastStatus', 'unknown'),
                        "lastDuration": last_duration,
                        "lastDurationMs": last_duration_ms,
                        # 新增欄位
                        "agentId": job.get('agentId', ''),
                        "sessionTarget": job.get('sessionTarget', 'isolated'),
                        "wakeMode": job.get('wakeMode', 'now'),
                        "payloadKind": payload.get('kind', ''),
                        "message": message,
                        "messagePreview": message_preview,
                        "model": payload.get('model', ''),
                        "deliveryMode": delivery.get('mode', ''),
                        "deliveryChannel": delivery.get('channel', ''),
                        "deliveryTo": delivery.get('to', ''),
                        "lastError": state.get('lastError'),
                        "lastDelivered": state.get('lastDelivered'),
                        "consecutiveErrors": state.get('consecutiveErrors', 0),
                    })
                
                return {"jobs": jobs, "count": len(jobs)}
            else:
                return {"jobs": [], "error": "Cron config not found"}
        except Exception as e:
            return {"jobs": [], "error": str(e)}
    
    def get_agents(self):
        """取得 Agents 列表"""
        def fetch():
            try:
                with open(CONFIG_PATH, 'r') as f:
                    config = json.load(f)
                
                agents_list = config.get('agents', {}).get('list', [])
                agents = []
                for a in agents_list:
                    identity = a.get('identity', {})
                    agents.append({
                        "id": a.get('id'),
                        "name": identity.get('name', a.get('id')),
                        "emoji": identity.get('emoji', '🤖'),
                        "description": identity.get('description', ''),
                    })
                return {"agents": agents}
            except Exception as e:
                return {"agents": [], "error": str(e)}
        return get_cached('agents', fetch, ttl=60)
    
    def get_sessions(self):
        """取得 OpenClaw Sessions"""
        def fetch():
            try:
                import subprocess
                result = subprocess.run(
                    ['openclaw', 'sessions', '--json'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    # 簡化 sessions 數據
                    sessions = []
                    for s in data.get('sessions', []):
                        # 解析 key 取得來源
                        key = s.get('key', '')
                        source = 'unknown'
                        if 'telegram' in key:
                            source = 'telegram'
                        elif 'discord' in key:
                            source = 'discord'
                        elif 'webchat' in key:
                            source = 'webchat'
                        elif 'cron' in key:
                            source = 'cron'
                        elif 'main_session' in key:
                            source = 'main'
                        
                        # 格式化時間
                        age_ms = s.get('ageMs', 0)
                        if age_ms < 60000:
                            age = f"{age_ms//1000}秒前"
                        elif age_ms < 3600000:
                            age = f"{age_ms//60000}分前"
                        elif age_ms < 86400000:
                            age = f"{age_ms//3600000}小時前"
                        else:
                            age = f"{age_ms//86400000}天前"
                        
                        sessions.append({
                            "id": s.get('sessionId', ''),
                            "key": key,
                            "agentId": s.get('agentId', ''),
                            "source": source,
                            "age": age,
                            "ageMs": age_ms,
                            "model": s.get('model', ''),
                            "tokens": s.get('totalTokens', 0),
                            "contextPercent": round(((s.get('totalTokens') or 0) / (s.get('contextTokens') or 200000)) * 100, 1),
                            "updatedAt": s.get('updatedAt', 0),
                        })
                    return {"sessions": sessions, "count": len(sessions)}
                else:
                    return {"sessions": [], "error": result.stderr}
            except Exception as e:
                return {"sessions": [], "error": str(e)}
        return get_cached('sessions', fetch, ttl=30)
    
    def get_channels(self):
        """取得 Channels 狀態"""
        def fetch():
            try:
                with open(CONFIG_PATH, 'r') as f:
                    config = json.load(f)
                
                channels = config.get('channels', {})
                result = {}
                for ch, conf in channels.items():
                    if isinstance(conf, dict):
                        accounts = conf.get('accounts', {})
                        account_list = []
                        for acc_id, acc_conf in accounts.items():
                            account_list.append({
                                "id": acc_id,
                                "enabled": acc_conf.get('enabled', True),
                                "botToken": "***" if acc_conf.get('botToken') else None,
                            })
                        result[ch] = {
                            "enabled": conf.get('enabled', True),
                            "accounts": account_list,
                        }
                return {"channels": result}
            except Exception as e:
                return {"channels": {}, "error": str(e)}
        return get_cached('channels', fetch, ttl=60)
    
    def get_config(self):
        """取得完整配置"""
        def fetch():
            try:
                with open(CONFIG_PATH, 'r') as f:
                    config = json.load(f)
                # 隱藏敏感資訊
                if 'channels' in config:
                    for ch, conf in config['channels'].items():
                        if isinstance(conf, dict) and 'accounts' in conf:
                            for acc_id, acc_conf in conf.get('accounts', {}).items():
                                if 'botToken' in acc_conf:
                                    acc_conf['botToken'] = '***'
                                if 'apiKey' in acc_conf:
                                    acc_conf['apiKey'] = '***'
                return {"config": config}
            except Exception as e:
                return {"error": str(e)}
        return get_cached('config', fetch, ttl=60)
    
    def get_agent_detail(self, agent_id):
        """取得單一 Agent 詳情"""
        import os
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
            
            agents_list = config.get('agents', {}).get('list', [])
            agent = None
            for a in agents_list:
                if a.get('id') == agent_id:
                    agent = a
                    break
            
            if not agent:
                return {"error": "Agent not found"}
            
            # 讀取 workspace 中的 md 文件
            workspace = agent.get('workspace', '')
            docs = {}
            if workspace and os.path.isdir(workspace):
                md_files = ['SOUL.md', 'AGENTS.md', 'USER.md', 'IDENTITY.md', 'TOOLS.md', 'MEMORY.md', 'HEARTBEAT.md']
                for md in md_files:
                    md_path = os.path.join(workspace, md)
                    if os.path.isfile(md_path):
                        try:
                            with open(md_path, 'r') as f:
                                docs[md] = f.read()[:2000]  # 限制長度
                        except:
                            pass
            
            return {
                "id": agent.get('id'),
                "name": agent.get('name'),
                "workspace": workspace,
                "agentDir": agent.get('agentDir'),
                "identity": agent.get('identity', {}),
                "model": agent.get('model', {}),
                "docs": docs
            }
        except Exception as e:
            return {"error": str(e)}
    
    def list_agent_files(self, agent_id, subdir=''):
        """列出 Agent workspace 中的檔案"""
        import os
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
            
            agents_list = config.get('agents', {}).get('list', [])
            agent = None
            for a in agents_list:
                if a.get('id') == agent_id:
                    agent = a
                    break
            
            if not agent:
                return {"error": "Agent not found"}
            
            workspace = agent.get('workspace', '')
            # 如果有 subdir，則列出子目錄
            if subdir:
                workspace = os.path.join(workspace, subdir)
            
            if not workspace or not os.path.isdir(workspace):
                return {"files": [], "workspace": workspace}
            
            # 遞迴列出所有檔案
            def list_dir(path, base=""):
                items = []
                try:
                    for item in os.listdir(path):
                        item_path = os.path.join(path, item)
                        rel_path = os.path.join(base, item) if base else item
                        if os.path.isdir(item_path):
                            items.append({
                                "name": item,
                                "path": rel_path,
                                "type": "directory",
                            })
                        else:
                            size = os.path.getsize(item_path)
                            items.append({
                                "name": item,
                                "path": rel_path,
                                "type": "file",
                                "size": size,
                            })
                except PermissionError:
                    pass
                return sorted(items, key=lambda x: (x["type"] != "file", x["name"]))
            
            files = list_dir(workspace)
            return {
                "workspace": agent.get('workspace', ''),
                "path": subdir,
                "files": files
            }
        except Exception as e:
            return {"error": str(e)}
    
    def read_agent_file(self, agent_id, file_path):
        """讀取 Agent workspace 中的檔案內容"""
        import os
        import urllib.parse
        import base64
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
            
            agents_list = config.get('agents', {}).get('list', [])
            agent = None
            for a in agents_list:
                if a.get('id') == agent_id:
                    agent = a
                    break
            
            if not agent:
                return {"error": "Agent not found"}
            
            workspace = agent.get('workspace', '')
            if not workspace:
                return {"error": "No workspace"}
            
            # 解碼路徑
            file_path = urllib.parse.unquote(file_path)
            full_path = os.path.join(workspace, file_path)
            
            # 安全檢查：確保路徑在 workspace 內
            if not os.path.abspath(full_path).startswith(os.path.abspath(workspace)):
                return {"error": "Invalid path"}
            
            if not os.path.isfile(full_path):
                return {"error": "File not found"}
            
            # 讀取檔案（限制大小）
            size = os.path.getsize(full_path)
            max_size = 5 * 1024 * 1024  # 5MB for images
            
            if size > max_size:
                return {"error": f"File too large ({size} bytes)", "size": size}
            
            # 檢查是否為圖片
            image_exts = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp']
            ext = file_path.lower().split('.')[-1] if '.' in file_path else ''
            
            if ext in image_exts:
                # 圖片：返回 base64 編碼
                with open(full_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')
                
                # 根據擴展名確定 MIME 類型
                mime_types = {
                    'png': 'image/png',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'gif': 'image/gif',
                    'webp': 'image/webp',
                    'svg': 'image/svg+xml',
                    'bmp': 'image/bmp'
                }
                mime_type = mime_types.get(ext, 'image/png')
                
                return {
                    "path": file_path,
                    "content": f"data:{mime_type};base64,{img_data}",
                    "size": size,
                    "isImage": True
                }
            
            # 一般文字檔案
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return {
                "path": file_path,
                "content": content,
                "size": size
            }
        except Exception as e:
            return {"error": str(e)}
    
    def do_POST(self):
        # 每次請求更新 Origin
        self._request_origin = self.headers.get('Origin', '')
        
        if self.path == '/api/chat':
            # Proxy to Gateway with SSE support
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # 檢查是否需要流式輸出
            try:
                body_json = json.loads(body)
                stream = body_json.get('stream', False)
            except:
                stream = False
            
            req = urllib.request.Request(
                f"{GATEWAY_URL}/v1/chat/completions",
                data=body,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {GATEWAY_TOKEN}',
                    'Origin': '*'
                },
                method='POST'
            )
            
            try:
                if stream:
                    # SSE 流式轉發
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/event-stream')
                    self.send_header('Cache-Control', 'no-cache')
                    self.send_header('Connection', 'close')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                    self.end_headers()
                    
                    # 優化 chunk size 提升流式響應速度
                    gateway_resp = urllib.request.urlopen(req, timeout=120)
                    while True:
                        chunk = gateway_resp.read(16384)  # 16KB chunks for faster streaming
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        self.wfile.flush()
                    gateway_resp.close()
                else:
                    # 普通模式（完整響應）
                    with urllib.request.urlopen(req, timeout=120) as response:
                        result = response.read()
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(result)
            except urllib.error.HTTPError as e:
                error_body = e.read()
                self.send_response(e.code)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(error_body)
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_error(404)

print(f"🚀 ClawChat Server: http://localhost:{PORT}")
print(f"📡 API: /api/status, /api/agents, /api/channels, /api/config")

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
    httpd.serve_forever()
