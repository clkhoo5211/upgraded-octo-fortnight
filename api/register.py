"""
用户注册API端点
允许用户自助注册并获取API Key
"""
import os
import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.auth.token_manager import TokenManager
from src.auth.rate_limiter import RateLimiter

# 全局实例
token_manager = TokenManager()
rate_limiter = RateLimiter()

# 注册验证密钥（用于防止滥用，可选）
REGISTRATION_SECRET = os.getenv('REGISTRATION_SECRET', '')

# 计划配置
PLAN_RATE_LIMITS = {
    'free': 100,      # 免费计划：100请求/小时
    'basic': 1000,    # 基础计划：1000请求/小时
    'premium': 10000  # 高级计划：10000请求/小时
}

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """处理用户注册请求"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body) if body else {}
            else:
                data = {}
            
            # 验证注册密钥（如果设置了）
            if REGISTRATION_SECRET:
                provided_secret = data.get('registration_secret')
                if provided_secret != REGISTRATION_SECRET:
                    self._send_error(403, 'Invalid registration secret')
                    return
            
            # 获取用户信息
            email = data.get('email', '').strip().lower()
            name = data.get('name', '').strip()
            plan = data.get('plan', 'free').lower()
            
            if not email:
                self._send_error(400, 'Email is required')
                return
            
            # 验证邮箱格式（简单验证）
            if '@' not in email or '.' not in email.split('@')[1]:
                self._send_error(400, 'Invalid email format')
                return
            
            # 验证计划
            if plan not in PLAN_RATE_LIMITS:
                self._send_error(400, f'Invalid plan. Available plans: {list(PLAN_RATE_LIMITS.keys())}')
                return
            
            # 检查用户是否已存在
            user_id = email
            existing_user = token_manager.get_user_info(user_id)
            
            if existing_user:
                # 用户已存在，返回现有用户信息和登录Token
                tokens = token_manager.generate_access_token(user_id)
                self._send_json(200, {
                    'success': True,
                    'message': 'User already exists. Please login.',
                    'user_id': user_id,
                    'plan': existing_user.get('plan', 'free'),
                    'rate_limit': existing_user.get('rate_limit', 100),
                    'tokens': tokens,
                    'next_step': 'create_api_key'
                })
                return
            
            # 获取速率限制
            rate_limit = PLAN_RATE_LIMITS.get(plan, 100)
            
            # 创建用户
            token_manager.tokens_data['users'][user_id] = {
                'created_at': datetime.now().isoformat(),
                'api_keys': [],
                'rate_limit': rate_limit,
                'enabled': True,
                'plan': plan,
                'name': name,
                'email': email
            }
            token_manager._save_tokens()
            
            # 设置速率限制
            rate_limiter.set_rate_limit(user_id, rate_limit)
            
            # 自动登录并返回Token（根据计划设置）
            is_paid = plan in ['basic', 'premium']
            tokens = token_manager.generate_access_token(user_id, plan=plan, is_paid=is_paid)
            
            self._send_json(201, {
                'success': True,
                'message': 'User registered successfully',
                'user_id': user_id,
                'plan': plan,
                'rate_limit': rate_limit,
                'tokens': tokens,
                'next_step': 'create_api_key',
                'instructions': {
                    'step1': 'Use the access_token to create an API key',
                    'step2': 'POST /api/auth/api-key with Authorization: Bearer <access_token>',
                    'step3': 'Save the API key securely - it will not be shown again'
                }
            })
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"注册错误: {error_trace}")
            self._send_error(500, str(e))
    
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

