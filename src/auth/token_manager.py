"""
Token管理模块 - 完全无状态Token系统
使用HMAC签名，Token包含所有信息，无需任何存储
"""
import os
import json
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, List

def _get_secret_key() -> str:
    """获取签名密钥（使用ADMIN_SECRET）"""
    return os.getenv('ADMIN_SECRET', 'change-me-in-production')

class TokenManager:
    """Token管理器 - 完全无状态实现，无需存储"""
    
    def __init__(self):
        """初始化Token管理器"""
        self.secret_key = _get_secret_key()
    
    def _sign(self, data: str) -> str:
        """生成HMAC-SHA256签名"""
        return hmac.new(
            self.secret_key.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _verify_signature(self, data: str, signature: str) -> bool:
        """验证签名"""
        expected_signature = self._sign(data)
        return hmac.compare_digest(expected_signature, signature)
    
    def _encode_token(self, payload: Dict) -> str:
        """编码Token（Base64 + 签名）"""
        # 创建数据字符串
        data_str = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        # 生成签名
        signature = self._sign(data_str)
        # 组合数据
        token_data = f"{data_str}|{signature}"
        # Base64编码
        return base64.urlsafe_b64encode(token_data.encode('utf-8')).decode('utf-8').rstrip('=')
    
    def _decode_token(self, token: str) -> Optional[Dict]:
        """解码并验证Token"""
        try:
            # Base64解码
            token_data = base64.urlsafe_b64decode(token + '==').decode('utf-8')
            # 分离数据和签名
            if '|' not in token_data:
                return None
            data_str, signature = token_data.rsplit('|', 1)
            # 验证签名
            if not self._verify_signature(data_str, signature):
                return None
            # 解析JSON
            return json.loads(data_str)
        except Exception as e:
            print(f"Token解码错误: {e}")
            return None
    
    def generate_api_key(self, user_id: str, name: str = "default", plan: str = "free", rate_limit: int = 100) -> str:
        """
        生成API Key（签名Token，包含所有信息）
        
        Args:
            user_id: 用户ID
            name: API Key名称
            plan: 用户计划
            rate_limit: 速率限制
        
        Returns:
            API Key字符串
        """
        payload = {
            'type': 'api_key',
            'user_id': user_id,
            'name': name,
            'plan': plan,
            'rate_limit': rate_limit,
            'is_paid': plan in ['basic', 'premium'],
            'created_at': datetime.now().isoformat()
        }
        
        token = self._encode_token(payload)
        return f"ak_{token}"
    
    def generate_access_token(
        self,
        user_id: str,
        expires_in: int = 3600,
        plan: str = 'free',
        is_paid: bool = False
    ) -> Dict[str, str]:
        """
        生成Access Token和Refresh Token（签名Token，包含所有信息）
        
        Args:
            user_id: 用户ID
            expires_in: Access Token过期时间（秒）
            plan: 用户计划
            is_paid: 是否为付费Token
        
        Returns:
            包含access_token和refresh_token的字典
        """
        # 根据计划设置过期时间
        if is_paid:
            expires_in = 30 * 24 * 3600  # 30天
            refresh_expires_in = 90 * 24 * 3600  # 90天
        else:
            expires_in = 3600  # 1小时
            refresh_expires_in = 7 * 24 * 3600  # 7天
        
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        refresh_expires_at = datetime.now() + timedelta(seconds=refresh_expires_in)
        
        # 计算速率限制
        rate_limits = {'free': 100, 'basic': 1000, 'premium': 10000}
        rate_limit = rate_limits.get(plan, 100)
        
        # Access Token payload
        access_payload = {
            'type': 'access_token',
            'user_id': user_id,
            'plan': plan,
            'is_paid': is_paid,
            'rate_limit': rate_limit,
            'expires_at': expires_at.isoformat(),
            'created_at': datetime.now().isoformat()
        }
        
        # Refresh Token payload
        refresh_payload = {
            'type': 'refresh_token',
            'user_id': user_id,
            'plan': plan,
            'is_paid': is_paid,
            'expires_at': refresh_expires_at.isoformat(),
            'created_at': datetime.now().isoformat()
        }
        
        # 编码Tokens
        access_token = f"at_{self._encode_token(access_payload)}"
        refresh_token = f"rt_{self._encode_token(refresh_payload)}"
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': expires_in,
            'expires_at': expires_at.isoformat(),
            'plan': plan,
            'is_paid': is_paid
        }
    
    def verify_api_key(self, api_key: str) -> Optional[Dict]:
        """
        验证API Key（无需查找数据库，直接验证签名）
        
        Args:
            api_key: API Key字符串
        
        Returns:
            如果有效返回用户信息，否则返回None
        """
        if not api_key.startswith('ak_'):
            return None
        
        token = api_key[3:]  # 移除 'ak_' 前缀
        payload = self._decode_token(token)
        
        if not payload or payload.get('type') != 'api_key':
            return None
        
        return {
            'user_id': payload['user_id'],
            'rate_limit': payload.get('rate_limit', 1000),
            'plan': payload.get('plan', 'free'),
            'is_paid': payload.get('is_paid', False),
            'api_key_name': payload.get('name', 'default')
        }
    
    def verify_access_token(self, access_token: str) -> Optional[Dict]:
        """
        验证Access Token（无需查找数据库，直接验证签名和过期时间）
        
        Args:
            access_token: Access Token字符串
        
        Returns:
            如果有效返回用户信息，否则返回None
        """
        if not access_token.startswith('at_'):
            return None
        
        token = access_token[3:]  # 移除 'at_' 前缀
        payload = self._decode_token(token)
        
        if not payload or payload.get('type') != 'access_token':
            return None
        
        # 检查过期时间
        expires_at_str = payload.get('expires_at')
        if expires_at_str:
            expires_at = datetime.fromisoformat(expires_at_str)
            if datetime.now() > expires_at:
                return {
                    'expired': True,
                    'expires_at': expires_at_str,
                    'user_id': payload.get('user_id'),
                    'plan': payload.get('plan', 'free'),
                    'is_paid': payload.get('is_paid', False)
                }
        
        return {
            'user_id': payload['user_id'],
            'rate_limit': payload.get('rate_limit', 1000),
            'plan': payload.get('plan', 'free'),
            'is_paid': payload.get('is_paid', False),
            'expires_at': expires_at_str,
            'expired': False
        }
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict]:
        """
        使用Refresh Token刷新Access Token
        
        Args:
            refresh_token: Refresh Token字符串
        
        Returns:
            新的Access Token信息，如果无效返回None
        """
        if not refresh_token.startswith('rt_'):
            return None
        
        token = refresh_token[3:]  # 移除 'rt_' 前缀
        payload = self._decode_token(token)
        
        if not payload or payload.get('type') != 'refresh_token':
            return None
        
        # 检查过期时间
        expires_at_str = payload.get('expires_at')
        if expires_at_str:
            expires_at = datetime.fromisoformat(expires_at_str)
            if datetime.now() > expires_at:
                return None
        
        # 生成新的Access Token
        user_id = payload['user_id']
        plan = payload.get('plan', 'free')
        is_paid = payload.get('is_paid', False)
        return self.generate_access_token(user_id, plan=plan, is_paid=is_paid)
    
    def renew_access_token(
        self,
        access_token: str,
        new_expires_in: Optional[int] = None
    ) -> Optional[Dict[str, str]]:
        """
        续期Access Token（付费用户）
        
        Args:
            access_token: 旧的Access Token
            new_expires_in: 新的过期时间（秒），如果为None则根据计划自动设置
        
        Returns:
            新的Token信息，如果无法续期返回None
        """
        payload = None
        if access_token.startswith('at_'):
            token = access_token[3:]
            payload = self._decode_token(token)
        
        if not payload or payload.get('type') != 'access_token':
            return None
        
        # 只有付费Token可以续期
        if not payload.get('is_paid', False):
            return None
        
        user_id = payload['user_id']
        plan = payload.get('plan', 'free')
        is_paid = payload.get('is_paid', False)
        
        # 生成新Token
        return self.generate_access_token(user_id, new_expires_in or None, plan, is_paid)
    
    def get_token_status(self, access_token: str) -> Dict:
        """
        获取Token状态（是否过期、剩余时间等）
        
        Args:
            access_token: Access Token字符串
        
        Returns:
            Token状态信息
        """
        if not access_token.startswith('at_'):
            return {
                'valid': False,
                'error': 'Invalid token format'
            }
        
        token = access_token[3:]
        payload = self._decode_token(token)
        
        if not payload or payload.get('type') != 'access_token':
            return {
                'valid': False,
                'error': 'Token not found or invalid'
            }
        
        expires_at_str = payload.get('expires_at')
        if not expires_at_str:
            return {
                'valid': False,
                'error': 'Token missing expiration'
            }
        
        expires_at = datetime.fromisoformat(expires_at_str)
        now = datetime.now()
        
        if now > expires_at:
            return {
                'valid': False,
                'expired': True,
                'expires_at': expires_at_str,
                'expired_since': (now - expires_at).total_seconds(),
                'plan': payload.get('plan', 'free'),
                'is_paid': payload.get('is_paid', False),
                'can_renew': payload.get('is_paid', False)
            }
        else:
            remaining = (expires_at - now).total_seconds()
            return {
                'valid': True,
                'expired': False,
                'expires_at': expires_at_str,
                'remaining_seconds': remaining,
                'remaining_hours': remaining / 3600,
                'plan': payload.get('plan', 'free'),
                'is_paid': payload.get('is_paid', False)
            }
    
    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """获取用户信息（无状态系统，无法获取，返回None）"""
        # 在无状态系统中，无法通过user_id获取信息
        # 用户信息都在Token中
        return None
    
    def update_user_rate_limit(self, user_id: str, rate_limit: int):
        """更新用户速率限制（无状态系统，无法更新）"""
        # 速率限制信息在Token中，需要重新生成Token
        pass
    
    def disable_user(self, user_id: str):
        """禁用用户（无状态系统，无法禁用）"""
        # 在无状态系统中，无法禁用用户
        # 如果需要禁用功能，需要维护一个黑名单（但用户不想存储）
        pass
    
    def enable_user(self, user_id: str):
        """启用用户（无状态系统，无法启用）"""
        pass
    
    def list_api_keys(self, user_id: Optional[str] = None) -> List[Dict]:
        """列出API Keys（无状态系统，无法列出）"""
        return []
    
    def revoke_api_key(self, api_key: str) -> bool:
        """撤销API Key（无状态系统，无法撤销）"""
        # 在无状态系统中，无法撤销Token
        # Token一旦签发就有效，直到过期
        return False
    
    def revoke_token(self, access_token: str) -> bool:
        """撤销Token（无状态系统，无法撤销）"""
        return False
