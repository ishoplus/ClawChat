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

PORT = int(os.environ.get('PORT', 8093))
GATEWAY_URL = os.environ.get('GATEWAY_URL', 'http://127.0.0.1:18789')
GATEWAY_TOKEN = os.environ.get('GATEWAY_TOKEN', '')
CONFIG_PATH = os.path.expanduser(os.environ.get('OPENCLAW_CONFIG_PATH', '~/.openclaw/openclaw.json'))

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SCRIPT_DIR, **kwargs)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/api/status':
            self.send_json_response(self.get_status())
        elif self.path == '/api/agents':
            self.send_json_response(self.get_agents())
        elif self.path == '/api/channels':
            self.send_json_response(self.get_channels())
        elif self.path == '/api/config':
            self.send_json_response(self.get_config())
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
        else:
            super().do_GET()
    
    def send_json_response(self, data):
        result = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
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
                    import json
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
                import json
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
    
    def get_agents(self):
        """取得 Agents 列表"""
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
    
    def get_channels(self):
        """取得 Channels 狀態"""
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
                            "botToken": "***" + acc_conf.get('botToken', '')[-10:] if acc_conf.get('botToken') else None,
                        })
                    result[ch] = {
                        "enabled": conf.get('enabled', True),
                        "accounts": account_list,
                    }
            return {"channels": result}
        except Exception as e:
            return {"channels": {}, "error": str(e)}
    
    def get_config(self):
        """取得完整配置"""
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
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                    self.end_headers()
                    
                    # 使用較小的 chunk size 以獲得更快的響應
                    gateway_resp = urllib.request.urlopen(req, timeout=120)
                    while True:
                        chunk = gateway_resp.read(8192)
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
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(result)
            except urllib.error.HTTPError as e:
                error_body = e.read()
                self.send_response(e.code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(error_body)
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_error(404)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

print(f"🚀 ClawChat Server: http://localhost:{PORT}")
print(f"📡 API: /api/status, /api/agents, /api/channels, /api/config")

with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
    httpd.serve_forever()
