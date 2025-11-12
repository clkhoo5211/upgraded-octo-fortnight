"""
Token管理模块
支持API Key、Access Token和Refresh Token
"""
import os
import json
import secrets
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pathlib import Path

class TokenManager:
    """Token管理器"""
    
    def __init__(self, tokens_file: str = "tokens.json"):
        """
        初始化Token管理器
        
        Args:
            tokens_file: Token存储文件路径
        """
        self.tokens_file = tokens_file
        self.tokens_dir = Path(__file__).parent.parent.parent
        self.tokens_path = self.tokens_dir / tokens_file
        self._load_tokens()
    
    def _load_tokens(self):
        """加载Token数据"""
        if self.tokens_path.exists():
            try:
                with open(self.tokens_path, 'r', encoding='utf-8') as f:
                    self.tokens_data = json.load(f)
            except Exception as e:
                print(f"加载Token文件失败: {e}")
                self.tokens_data = {
                    'api_keys': {},
                    'access_tokens': {},
                    'refresh_tokens': {},
                    'users': {}
                }
        else:
            self.tokens_data = {
                'api_keys': {},
                'access_tokens': {},
                'refresh_tokens': {},
                'users': {}
            }
            self._save_tokens()
    
    def _save_tokens(self):
        """保存Token数据"""
        try:
            with open(self.tokens_path, 'w', encoding='utf-8') as f:
                json.dump(self.tokens_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存Token文件失败: {e}")
    
    def generate_api_key(self, user_id: str, name: str = "default") -> str:
        """
        生成API Key
        
        Args:
            user_id: 用户ID
            name: API Key名称
        
        Returns:
            API Key字符串
        """
        api_key = f"ak_{secrets.token_urlsafe(32)}"
        hashed_key = self._hash_token(api_key)
        
        if user_id not in self.tokens_data['users']:
            self.tokens_data['users'][user_id] = {
                'created_at': datetime.now().isoformat(),
                'api_keys': [],
                'rate_limit': 1000,  # 每小时请求数
                'enabled': True
            }
        
        key_data = {
            'name': name,
            'hashed_key': hashed_key,
            'created_at': datetime.now().isoformat(),
            'last_used': None,
            'enabled': True
        }
        
        self.tokens_data['api_keys'][hashed_key] = {
            'user_id': user_id,
            'name': name,
            'created_at': datetime.now().isoformat(),
            'last_used': None,
            'enabled': True
        }
        
        self.tokens_data['users'][user_id]['api_keys'].append(hashed_key)
        self._save_tokens()
        
        return api_key
    
    def generate_access_token(
        self,
        user_id: str,
        expires_in: int = 3600,
        plan: str = 'free',
        is_paid: bool = False
    ) -> Dict[str, str]:
        """
        生成Access Token和Refresh Token
        
        Args:
            user_id: 用户ID
            expires_in: Access Token过期时间（秒），默认1小时
            plan: 用户计划（free/basic/premium）
            is_paid: 是否为付费Token
        
        Returns:
            包含access_token和refresh_token的字典
        """
        access_token = f"at_{secrets.token_urlsafe(32)}"
        refresh_token = f"rt_{secrets.token_urlsafe(32)}"
        
        hashed_access = self._hash_token(access_token)
        hashed_refresh = self._hash_token(refresh_token)
        
        # 根据计划设置过期时间
        if is_paid:
            # 付费Token：30天
            expires_in = 30 * 24 * 3600
            refresh_expires_at = datetime.now() + timedelta(days=90)  # Refresh Token 90天
        else:
            # 免费Token：1小时
            expires_in = 3600
            refresh_expires_at = datetime.now() + timedelta(days=7)  # Refresh Token 7天
        
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        # 存储Access Token（包含计划信息）
        self.tokens_data['access_tokens'][hashed_access] = {
            'user_id': user_id,
            'expires_at': expires_at.isoformat(),
            'created_at': datetime.now().isoformat(),
            'plan': plan,
            'is_paid': is_paid,
            'expires_in': expires_in
        }
        
        # 存储Refresh Token
        self.tokens_data['refresh_tokens'][hashed_refresh] = {
            'user_id': user_id,
            'access_token_hash': hashed_access,
            'expires_at': refresh_expires_at.isoformat(),
            'created_at': datetime.now().isoformat(),
            'plan': plan,
            'is_paid': is_paid
        }
        
        self._save_tokens()
        
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
        验证API Key
        
        Args:
            api_key: API Key字符串
        
        Returns:
            如果有效返回用户信息，否则返回None
        """
        hashed_key = self._hash_token(api_key)
        
        if hashed_key in self.tokens_data['api_keys']:
            key_info = self.tokens_data['api_keys'][hashed_key]
            
            if not key_info.get('enabled', True):
                return None
            
            user_id = key_info['user_id']
            user_info = self.tokens_data['users'].get(user_id)
            
            if not user_info or not user_info.get('enabled', True):
                return None
            
            # 更新最后使用时间
            key_info['last_used'] = datetime.now().isoformat()
            self._save_tokens()
            
            return {
                'user_id': user_id,
                'rate_limit': user_info.get('rate_limit', 1000),
                'api_key_name': key_info.get('name', 'default')
            }
        
        return None
    
    def verify_access_token(self, access_token: str) -> Optional[Dict]:
        """
        验证Access Token
        
        Args:
            access_token: Access Token字符串
        
        Returns:
            如果有效返回用户信息，否则返回None
        """
        hashed_token = self._hash_token(access_token)
        
        if hashed_token in self.tokens_data['access_tokens']:
            token_info = self.tokens_data['access_tokens'][hashed_token]
            
            expires_at = datetime.fromisoformat(token_info['expires_at'])
            if datetime.now() > expires_at:
                # Token已过期，标记但保留（用于续期）
                token_info['expired'] = True
                self._save_tokens()
                return {
                    'expired': True,
                    'expires_at': expires_at.isoformat(),
                    'user_id': token_info.get('user_id'),
                    'plan': token_info.get('plan', 'free'),
                    'is_paid': token_info.get('is_paid', False)
                }
            
            user_id = token_info['user_id']
            user_info = self.tokens_data['users'].get(user_id)
            
            if not user_info or not user_info.get('enabled', True):
                return None
            
            return {
                'user_id': user_id,
                'rate_limit': user_info.get('rate_limit', 1000),
                'plan': token_info.get('plan', 'free'),
                'is_paid': token_info.get('is_paid', False),
                'expires_at': expires_at.isoformat(),
                'expired': False
            }
        
        return None
    
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
        hashed_token = self._hash_token(access_token)
        
        if hashed_token in self.tokens_data['access_tokens']:
            token_info = self.tokens_data['access_tokens'][hashed_token]
            user_id = token_info['user_id']
            plan = token_info.get('plan', 'free')
            is_paid = token_info.get('is_paid', False)
            
            # 检查用户是否仍然有效
            user_info = self.tokens_data['users'].get(user_id)
            if not user_info or not user_info.get('enabled', True):
                return None
            
            # 删除旧Token
            del self.tokens_data['access_tokens'][hashed_token]
            
            # 删除对应的Refresh Token
            for refresh_hash, refresh_info in list(self.tokens_data['refresh_tokens'].items()):
                if refresh_info.get('access_token_hash') == hashed_token:
                    del self.tokens_data['refresh_tokens'][refresh_hash]
                    break
            
            # 生成新Token
            if new_expires_in:
                expires_in = new_expires_in
            else:
                expires_in = None  # 使用默认值
            
            return self.generate_access_token(user_id, expires_in, plan, is_paid)
        
        return None
    
    def get_token_status(self, access_token: str) -> Dict:
        """
        获取Token状态（是否过期、剩余时间等）
        
        Args:
            access_token: Access Token字符串
        
        Returns:
            Token状态信息
        """
        hashed_token = self._hash_token(access_token)
        
        if hashed_token not in self.tokens_data['access_tokens']:
            return {
                'valid': False,
                'error': 'Token not found'
            }
        
        token_info = self.tokens_data['access_tokens'][hashed_token]
        expires_at = datetime.fromisoformat(token_info['expires_at'])
        now = datetime.now()
        
        if now > expires_at:
            return {
                'valid': False,
                'expired': True,
                'expires_at': expires_at.isoformat(),
                'expired_since': (now - expires_at).total_seconds(),
                'plan': token_info.get('plan', 'free'),
                'is_paid': token_info.get('is_paid', False),
                'can_renew': token_info.get('is_paid', False)  # 只有付费Token可以续期
            }
        else:
            remaining = (expires_at - now).total_seconds()
            return {
                'valid': True,
                'expired': False,
                'expires_at': expires_at.isoformat(),
                'remaining_seconds': remaining,
                'remaining_hours': remaining / 3600,
                'plan': token_info.get('plan', 'free'),
                'is_paid': token_info.get('is_paid', False)
            }
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict]:
        """
        使用Refresh Token刷新Access Token
        
        Args:
            refresh_token: Refresh Token字符串
        
        Returns:
            新的Access Token信息，如果无效返回None
        """
        hashed_refresh = self._hash_token(refresh_token)
        
        if hashed_refresh in self.tokens_data['refresh_tokens']:
            refresh_info = self.tokens_data['refresh_tokens'][hashed_refresh]
            
            expires_at = datetime.fromisoformat(refresh_info['expires_at'])
            if datetime.now() > expires_at:
                # Refresh Token已过期，删除
                del self.tokens_data['refresh_tokens'][hashed_refresh]
                if refresh_info['access_token_hash'] in self.tokens_data['access_tokens']:
                    del self.tokens_data['access_tokens'][refresh_info['access_token_hash']]
                self._save_tokens()
                return None
            
            user_id = refresh_info['user_id']
            
            # 删除旧的Access Token
            old_access_hash = refresh_info['access_token_hash']
            if old_access_hash in self.tokens_data['access_tokens']:
                del self.tokens_data['access_tokens'][old_access_hash]
            
            # 生成新的Access Token
            return self.generate_access_token(user_id)
        
        return None
    
    def revoke_api_key(self, api_key: str) -> bool:
        """撤销API Key"""
        hashed_key = self._hash_token(api_key)
        if hashed_key in self.tokens_data['api_keys']:
            self.tokens_data['api_keys'][hashed_key]['enabled'] = False
            self._save_tokens()
            return True
        return False
    
    def revoke_token(self, access_token: str) -> bool:
        """撤销Access Token和对应的Refresh Token"""
        hashed_token = self._hash_token(access_token)
        
        if hashed_token in self.tokens_data['access_tokens']:
            token_info = self.tokens_data['access_tokens'][hashed_token]
            
            # 删除Access Token
            del self.tokens_data['access_tokens'][hashed_token]
            
            # 删除对应的Refresh Token
            for refresh_hash, refresh_info in list(self.tokens_data['refresh_tokens'].items()):
                if refresh_info['access_token_hash'] == hashed_token:
                    del self.tokens_data['refresh_tokens'][refresh_hash]
                    break
            
            self._save_tokens()
            return True
        
        return False
    
    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """获取用户信息"""
        return self.tokens_data['users'].get(user_id)
    
    def update_user_rate_limit(self, user_id: str, rate_limit: int):
        """更新用户速率限制"""
        if user_id in self.tokens_data['users']:
            self.tokens_data['users'][user_id]['rate_limit'] = rate_limit
            self._save_tokens()
    
    def disable_user(self, user_id: str):
        """禁用用户"""
        if user_id in self.tokens_data['users']:
            self.tokens_data['users'][user_id]['enabled'] = False
            self._save_tokens()
    
    def enable_user(self, user_id: str):
        """启用用户"""
        if user_id in self.tokens_data['users']:
            self.tokens_data['users'][user_id]['enabled'] = True
            self._save_tokens()
    
    def _hash_token(self, token: str) -> str:
        """哈希Token（SHA-256）"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def list_api_keys(self, user_id: Optional[str] = None) -> List[Dict]:
        """列出API Keys"""
        keys = []
        for hashed_key, key_info in self.tokens_data['api_keys'].items():
            if user_id is None or key_info['user_id'] == user_id:
                keys.append({
                    'name': key_info.get('name', 'default'),
                    'created_at': key_info.get('created_at'),
                    'last_used': key_info.get('last_used'),
                    'enabled': key_info.get('enabled', True),
                    'user_id': key_info['user_id']
                })
        return keys

