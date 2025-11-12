"""
认证中间件
用于API端点的认证和授权检查
"""
import os
import json
from typing import Optional, Dict, Callable
from http.server import BaseHTTPRequestHandler

# 导入认证模块
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.auth.token_manager import TokenManager
from src.auth.rate_limiter import RateLimiter

class AuthMiddleware:
    """认证中间件"""
    
    def __init__(self):
        """初始化认证中间件"""
        self.token_manager = TokenManager()
        self.rate_limiter = RateLimiter()
        # 是否启用认证（可通过环境变量控制）
        self.auth_enabled = os.getenv('ENABLE_API_AUTH', 'false').lower() == 'true'
    
    def extract_token(self, handler: BaseHTTPRequestHandler) -> Optional[str]:
        """
        从请求中提取Token
        
        支持方式：
        1. Authorization Header: Bearer <token>
        2. Authorization Header: Bearer <api_key>
        3. Query参数: ?api_key=<key>
        4. Header: X-API-Key: <key>
        """
        # 方式1: Authorization Header
        auth_header = handler.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:].strip()
        
        # 方式2: X-API-Key Header
        api_key_header = handler.headers.get('X-API-Key', '')
        if api_key_header:
            return api_key_header.strip()
        
        # 方式3: Query参数
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(handler.path)
        query_params = parse_qs(parsed.query)
        if 'api_key' in query_params:
            return query_params['api_key'][0]
        
        return None
    
    def authenticate_request(
        self,
        handler: BaseHTTPRequestHandler,
        endpoint: str = "default"
    ) -> tuple[bool, Optional[Dict], Optional[Dict]]:
        """
        认证请求
        
        Returns:
            (是否认证成功, 用户信息, 错误信息)
        """
        # 如果未启用认证，直接允许
        if not self.auth_enabled:
            return True, {'user_id': 'anonymous', 'rate_limit': 10000}, None
        
        # 提取Token
        token = self.extract_token(handler)
        
        if not token:
            return False, None, {
                'error': 'Authentication required',
                'message': 'Please provide API key or access token',
                'auth_methods': [
                    'Authorization: Bearer <token>',
                    'X-API-Key: <api_key>',
                    '?api_key=<api_key>'
                ]
            }
        
        # 验证Token
        user_info = None
        
        # 尝试作为API Key验证
        if token.startswith('ak_'):
            user_info = self.token_manager.verify_api_key(token)
        
        # 尝试作为Access Token验证
        if not user_info and token.startswith('at_'):
            user_info = self.token_manager.verify_access_token(token)
        
        # 如果都不匹配，尝试作为普通API Key验证（向后兼容）
        if not user_info:
            user_info = self.token_manager.verify_api_key(token)
        
        if not user_info:
            return False, None, {
                'error': 'Invalid token',
                'message': 'The provided token is invalid or expired'
            }
        
        # 检查速率限制
        user_id = user_info['user_id']
        rate_limit = user_info.get('rate_limit', 1000)
        
        allowed, rate_info = self.rate_limiter.check_rate_limit(
            user_id,
            endpoint,
            rate_limit
        )
        
        if not allowed:
            return False, None, {
                'error': 'Rate limit exceeded',
                'message': rate_info['message'],
                'limit': rate_info['limit'],
                'remaining': rate_info['remaining'],
                'reset_at': rate_info['reset_at']
            }
        
        # 添加速率限制信息到用户信息
        user_info['rate_limit_info'] = rate_info
        
        return True, user_info, None
    
    def require_auth(self, endpoint: str = "default"):
        """
        装饰器：要求认证
        
        Usage:
            @auth_middleware.require_auth("search")
            def handle_request(handler):
                ...
        """
        def decorator(func: Callable):
            def wrapper(handler: BaseHTTPRequestHandler, *args, **kwargs):
                # 执行认证检查
                authenticated, user_info, error = self.authenticate_request(
                    handler,
                    endpoint
                )
                
                if not authenticated:
                    # 返回401错误
                    handler.send_response(401)
                    handler.send_header('Content-Type', 'application/json')
                    handler.send_header('Access-Control-Allow-Origin', '*')
                    
                    # 如果是速率限制错误，返回429
                    if error and error.get('error') == 'Rate limit exceeded':
                        handler.send_response(429)
                        handler.send_header('Retry-After', '3600')
                    
                    handler.end_headers()
                    handler.wfile.write(
                        json.dumps(error, ensure_ascii=False).encode('utf-8')
                    )
                    return
                
                # 将用户信息添加到handler
                handler.user_info = user_info
                
                # 调用原始函数
                return func(handler, *args, **kwargs)
            
            return wrapper
        return decorator

# 全局实例
auth_middleware = AuthMiddleware()

