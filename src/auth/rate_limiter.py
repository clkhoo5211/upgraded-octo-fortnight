"""
速率限制模块
防止API滥用和spam攻击
"""
import time
from collections import defaultdict
from typing import Dict, Optional
from datetime import datetime, timedelta

class RateLimiter:
    """速率限制器"""
    
    def __init__(self):
        """初始化速率限制器"""
        # 存储每个用户的请求记录: {user_id: [(timestamp, endpoint), ...]}
        self.request_history: Dict[str, list] = defaultdict(list)
        # 存储每个用户的速率限制配置: {user_id: requests_per_hour}
        self.rate_limits: Dict[str, int] = {}
        # 默认速率限制（每小时请求数）
        self.default_rate_limit = 1000
    
    def check_rate_limit(
        self,
        user_id: str,
        endpoint: str = "default",
        rate_limit: Optional[int] = None
    ) -> tuple[bool, Dict]:
        """
        检查速率限制
        
        Args:
            user_id: 用户ID
            endpoint: API端点
            rate_limit: 自定义速率限制（每小时请求数）
        
        Returns:
            (是否允许, 限制信息)
        """
        current_time = time.time()
        hour_ago = current_time - 3600  # 1小时前
        
        # 获取速率限制
        limit = rate_limit or self.rate_limits.get(user_id, self.default_rate_limit)
        
        # 清理1小时前的记录
        user_history = self.request_history[user_id]
        user_history[:] = [
            (ts, ep) for ts, ep in user_history
            if ts > hour_ago
        ]
        
        # 统计当前小时内的请求数
        recent_requests = [
            (ts, ep) for ts, ep in user_history
            if ts > hour_ago
        ]
        
        request_count = len(recent_requests)
        
        # 检查是否超过限制
        if request_count >= limit:
            return False, {
                'allowed': False,
                'limit': limit,
                'remaining': 0,
                'reset_at': hour_ago + 3600,
                'message': f'Rate limit exceeded. Limit: {limit} requests/hour'
            }
        
        # 记录本次请求
        user_history.append((current_time, endpoint))
        
        return True, {
            'allowed': True,
            'limit': limit,
            'remaining': limit - request_count - 1,
            'reset_at': hour_ago + 3600,
            'message': 'OK'
        }
    
    def set_rate_limit(self, user_id: str, rate_limit: int):
        """设置用户速率限制"""
        self.rate_limits[user_id] = rate_limit
    
    def get_rate_limit_info(self, user_id: str) -> Dict:
        """获取用户速率限制信息"""
        current_time = time.time()
        hour_ago = current_time - 3600
        
        user_history = self.request_history.get(user_id, [])
        recent_requests = [
            (ts, ep) for ts, ep in user_history
            if ts > hour_ago
        ]
        
        limit = self.rate_limits.get(user_id, self.default_rate_limit)
        
        return {
            'limit': limit,
            'used': len(recent_requests),
            'remaining': max(0, limit - len(recent_requests)),
            'reset_at': hour_ago + 3600
        }
    
    def reset_user_history(self, user_id: str):
        """重置用户请求历史"""
        if user_id in self.request_history:
            del self.request_history[user_id]

