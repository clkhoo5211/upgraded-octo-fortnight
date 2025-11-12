"""
认证和授权管理API端点
用于管理API Keys、Tokens和用户
"""
import os
import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.auth.token_manager import TokenManager
from src.auth.rate_limiter import RateLimiter

# 全局实例
token_manager = TokenManager()
rate_limiter = RateLimiter()

# 管理员密钥（从环境变量获取）
ADMIN_SECRET = os.getenv('ADMIN_SECRET', 'change-me-in-production')

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def _check_admin(self) -> bool:
        """检查管理员权限"""
        auth_header = self.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:].strip()
            return token == ADMIN_SECRET
        return False
    
    def do_GET(self):
        """处理GET请求"""
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        path = parsed.path
        
        try:
            # /api/auth/me - 获取当前用户信息
            if path == '/api/auth/me' or path.endswith('/me'):
                self._handle_get_me()
            
            # /api/auth/rate-limit - 获取速率限制信息
            elif path == '/api/auth/rate-limit' or path.endswith('/rate-limit'):
                self._handle_get_rate_limit()
            
            # /api/auth/users - 列出所有用户（需要管理员）
            elif path == '/api/auth/users' or path.endswith('/users'):
                if not self._check_admin():
                    self._send_error(403, 'Admin access required')
                    return
                self._handle_list_users()
            
            # /api/auth/api-keys - 列出API Keys（需要管理员）
            elif path == '/api/auth/api-keys' or path.endswith('/api-keys'):
                if not self._check_admin():
                    self._send_error(403, 'Admin access required')
                    return
                self._handle_list_api_keys()
            
            else:
                self._send_error(404, 'Endpoint not found')
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"认证API错误: {error_trace}")
            self._send_error(500, str(e))
    
    def do_POST(self):
        """处理POST请求"""
        from urllib.parse import urlparse
        parsed = urlparse(self.path)
        path = parsed.path
        
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body) if body else {}
            else:
                data = {}
            
            # /api/auth/login - 登录获取Token
            if path == '/api/auth/login' or path.endswith('/login'):
                self._handle_login(data)
            
            # /api/auth/refresh - 刷新Access Token
            elif path == '/api/auth/refresh' or path.endswith('/refresh'):
                self._handle_refresh(data)
            
            # /api/auth/api-key - 生成API Key
            elif path == '/api/auth/api-key' or path.endswith('/api-key'):
                self._handle_create_api_key(data)
            
            # /api/auth/user - 创建用户（需要管理员）
            elif path == '/api/auth/user' or path.endswith('/user'):
                if not self._check_admin():
                    self._send_error(403, 'Admin access required')
                    return
                self._handle_create_user(data)
            
            else:
                self._send_error(404, 'Endpoint not found')
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"认证API错误: {error_trace}")
            self._send_error(500, str(e))
    
    def do_DELETE(self):
        """处理DELETE请求"""
        from urllib.parse import urlparse
        parsed = urlparse(self.path)
        path = parsed.path
        
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body) if body else {}
            else:
                data = {}
            
            # /api/auth/api-key - 撤销API Key
            if path == '/api/auth/api-key' or path.endswith('/api-key'):
                self._handle_revoke_api_key(data)
            
            # /api/auth/token - 撤销Token
            elif path == '/api/auth/token' or path.endswith('/token'):
                self._handle_revoke_token(data)
            
            else:
                self._send_error(404, 'Endpoint not found')
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"认证API错误: {error_trace}")
            self._send_error(500, str(e))
    
    def _handle_login(self, data: dict):
        """处理登录请求"""
        user_id = data.get('user_id')
        if not user_id:
            self._send_error(400, 'user_id is required')
            return
        
        # 检查用户是否存在
        user_info = token_manager.get_user_info(user_id)
        if not user_info:
            self._send_error(404, 'User not found')
            return
        
        if not user_info.get('enabled', True):
            self._send_error(403, 'User is disabled')
            return
        
        # 生成Token
        tokens = token_manager.generate_access_token(user_id)
        
        self._send_json(200, {
            'success': True,
            'tokens': tokens,
            'user_id': user_id
        })
    
    def _handle_refresh(self, data: dict):
        """处理刷新Token请求"""
        refresh_token = data.get('refresh_token')
        if not refresh_token:
            self._send_error(400, 'refresh_token is required')
            return
        
        new_tokens = token_manager.refresh_access_token(refresh_token)
        if not new_tokens:
            self._send_error(401, 'Invalid or expired refresh token')
            return
        
        self._send_json(200, {
            'success': True,
            'tokens': new_tokens
        })
    
    def _handle_create_api_key(self, data: dict):
        """处理创建API Key请求"""
        # 需要认证
        auth_header = self.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            self._send_error(401, 'Authentication required')
            return
        
        token = auth_header[7:].strip()
        user_info = None
        
        # 验证Token
        if token.startswith('at_'):
            user_info = token_manager.verify_access_token(token)
        elif token.startswith('ak_'):
            user_info = token_manager.verify_api_key(token)
        
        if not user_info:
            self._send_error(401, 'Invalid token')
            return
        
        user_id = user_info['user_id']
        name = data.get('name', 'default')
        
        api_key = token_manager.generate_api_key(user_id, name)
        
        self._send_json(201, {
            'success': True,
            'api_key': api_key,
            'name': name,
            'user_id': user_id,
            'warning': 'Save this API key securely. It will not be shown again.'
        })
    
    def _handle_create_user(self, data: dict):
        """处理创建用户请求（管理员）"""
        user_id = data.get('user_id')
        rate_limit = data.get('rate_limit', 1000)
        
        if not user_id:
            self._send_error(400, 'user_id is required')
            return
        
        # 创建用户（如果不存在）
        if user_id not in token_manager.tokens_data['users']:
            token_manager.tokens_data['users'][user_id] = {
                'created_at': token_manager.tokens_data.get('users', {}).get(user_id, {}).get('created_at') or __import__('datetime').datetime.now().isoformat(),
                'api_keys': [],
                'rate_limit': rate_limit,
                'enabled': True
            }
            token_manager._save_tokens()
        
        rate_limiter.set_rate_limit(user_id, rate_limit)
        
        self._send_json(201, {
            'success': True,
            'user_id': user_id,
            'rate_limit': rate_limit,
            'message': 'User created successfully'
        })
    
    def _handle_get_me(self):
        """获取当前用户信息"""
        auth_header = self.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            self._send_error(401, 'Authentication required')
            return
        
        token = auth_header[7:].strip()
        user_info = None
        
        if token.startswith('at_'):
            user_info = token_manager.verify_access_token(token)
        elif token.startswith('ak_'):
            user_info = token_manager.verify_api_key(token)
        
        if not user_info:
            self._send_error(401, 'Invalid token')
            return
        
        rate_limit_info = rate_limiter.get_rate_limit_info(user_info['user_id'])
        
        self._send_json(200, {
            'success': True,
            'user_id': user_info['user_id'],
            'rate_limit': user_info.get('rate_limit', 1000),
            'rate_limit_info': rate_limit_info
        })
    
    def _handle_get_rate_limit(self):
        """获取速率限制信息"""
        auth_header = self.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            self._send_error(401, 'Authentication required')
            return
        
        token = auth_header[7:].strip()
        user_info = None
        
        if token.startswith('at_'):
            user_info = token_manager.verify_access_token(token)
        elif token.startswith('ak_'):
            user_info = token_manager.verify_api_key(token)
        
        if not user_info:
            self._send_error(401, 'Invalid token')
            return
        
        rate_limit_info = rate_limiter.get_rate_limit_info(user_info['user_id'])
        
        self._send_json(200, {
            'success': True,
            'rate_limit_info': rate_limit_info
        })
    
    def _handle_list_users(self):
        """列出所有用户"""
        users = []
        for user_id, user_info in token_manager.tokens_data['users'].items():
            users.append({
                'user_id': user_id,
                'created_at': user_info.get('created_at'),
                'rate_limit': user_info.get('rate_limit', 1000),
                'enabled': user_info.get('enabled', True),
                'api_key_count': len(user_info.get('api_keys', []))
            })
        
        self._send_json(200, {
            'success': True,
            'users': users,
            'total': len(users)
        })
    
    def _handle_list_api_keys(self):
        """列出所有API Keys"""
        api_keys = token_manager.list_api_keys()
        
        self._send_json(200, {
            'success': True,
            'api_keys': api_keys,
            'total': len(api_keys)
        })
    
    def _handle_revoke_api_key(self, data: dict):
        """撤销API Key"""
        api_key = data.get('api_key')
        if not api_key:
            self._send_error(400, 'api_key is required')
            return
        
        success = token_manager.revoke_api_key(api_key)
        if success:
            self._send_json(200, {
                'success': True,
                'message': 'API key revoked successfully'
            })
        else:
            self._send_error(404, 'API key not found')
    
    def _handle_revoke_token(self, data: dict):
        """撤销Token"""
        access_token = data.get('access_token')
        if not access_token:
            self._send_error(400, 'access_token is required')
            return
        
        success = token_manager.revoke_token(access_token)
        if success:
            self._send_json(200, {
                'success': True,
                'message': 'Token revoked successfully'
            })
        else:
            self._send_error(404, 'Token not found')
    
    def _send_json(self, status_code: int, data: dict):
        """发送JSON响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def _send_error(self, status_code: int, message: str):
        """发送错误响应"""
        self._send_json(status_code, {
            'success': False,
            'error': message
        })

