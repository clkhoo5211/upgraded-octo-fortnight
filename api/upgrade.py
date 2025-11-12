"""
用户计划升级API端点
用于付费用户升级计划并获取新的Token
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

# 计划配置
PLAN_RATE_LIMITS = {
    'free': 100,
    'basic': 1000,
    'premium': 10000
}

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_POST(self):
        """处理升级请求"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body) if body else {}
            else:
                data = {}
            
            # 需要认证
            auth_header = self.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                self._send_error(401, 'Authentication required')
                return
            
            access_token = auth_header[7:].strip()
            user_info = None
            
            # 验证Token
            if access_token.startswith('at_'):
                user_info = token_manager.verify_access_token(access_token)
            elif access_token.startswith('ak_'):
                user_info = token_manager.verify_api_key(access_token)
            
            if not user_info or user_info.get('expired'):
                self._send_error(401, 'Invalid or expired token')
                return
            
            user_id = user_info['user_id']
            current_plan = user_info.get('plan', 'free')
            
            # 获取新计划
            new_plan = data.get('plan', '').lower()
            if not new_plan or new_plan not in PLAN_RATE_LIMITS:
                self._send_error(400, f'Invalid plan. Available plans: {list(PLAN_RATE_LIMITS.keys())}')
                return
            
            if new_plan == current_plan:
                self._send_error(400, f'Already on {current_plan} plan')
                return
            
            # 在无状态系统中，用户计划信息在Token中
            # 只需要生成新的Token即可
            new_rate_limit = PLAN_RATE_LIMITS[new_plan]
            rate_limiter.set_rate_limit(user_id, new_rate_limit)
            
            # 生成新的付费Token
            is_paid = new_plan in ['basic', 'premium']
            new_tokens = token_manager.generate_access_token(
                user_id,
                plan=new_plan,
                is_paid=is_paid
            )
            
            self._send_json(200, {
                'success': True,
                'message': f'Plan upgraded from {current_plan} to {new_plan}',
                'old_plan': current_plan,
                'new_plan': new_plan,
                'rate_limit': PLAN_RATE_LIMITS[new_plan],
                'tokens': new_tokens,
                'instructions': {
                    'step1': 'Save the new access_token',
                    'step2': 'Update your API calls to use the new token',
                    'step3': 'Old token will expire but can still be used until expiry'
                }
            })
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"升级错误: {error_trace}")
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

