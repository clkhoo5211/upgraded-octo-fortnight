# 完整API对接指南

> 适用于其他项目对接Global News Aggregator API的完整文档

## 📋 目录

1. [快速开始](#快速开始)
2. [用户注册和Token获取](#用户注册和token获取)
3. [Token管理和续期](#token管理和续期)
4. [API使用示例](#api使用示例)
5. [错误处理](#错误处理)
6. [商业模式](#商业模式)
7. [完整工作流程](#完整工作流程)

---

## 🚀 快速开始

### API基础信息

- **API地址**: `https://upgraded-octo-fortnight.vercel.app`
- **版本**: 1.0.0
- **认证方式**: Bearer Token (API Key或Access Token)
- **格式**: JSON

### 5分钟快速对接

```python
import requests

# 1. 注册用户（免费计划）
response = requests.post(
    'https://upgraded-octo-fortnight.vercel.app/api/register',
    json={'email': 'user@example.com', 'plan': 'free'}
)
data = response.json()

# 2. 创建API Key
api_key_response = requests.post(
    'https://upgraded-octo-fortnight.vercel.app/api/auth/api-key',
    headers={'Authorization': f"Bearer {data['tokens']['access_token']}"},
    json={'name': 'my-key'}
)
api_key = api_key_response.json()['api_key']

# 3. 使用API Key
news_response = requests.post(
    'https://upgraded-octo-fortnight.vercel.app/api/search',
    headers={'Authorization': f"Bearer {api_key}"},
    json={'categories': ['tech'], 'max_results': 10}
)
print(news_response.json())
```

---

## 👤 用户注册和Token获取

### 方式1: 用户自助注册（推荐）

#### 注册端点

```bash
POST /api/register
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "plan": "free"
}
```

#### 可用计划

| 计划 | 速率限制 | Token有效期 | 价格 |
|------|----------|-------------|------|
| `free` | 100 请求/小时 | 1小时 | 免费 |
| `basic` | 1,000 请求/小时 | 30天 | $9/月 |
| `premium` | 10,000 请求/小时 | 30天 | $29/月 |

#### 注册响应

```json
{
  "success": true,
  "message": "User registered successfully",
  "user_id": "user@example.com",
  "plan": "free",
  "rate_limit": 100,
  "tokens": {
    "access_token": "at_xxx...",
    "refresh_token": "rt_xxx...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "expires_at": "2025-11-12T15:00:00",
    "plan": "free",
    "is_paid": false
  },
  "next_step": "create_api_key"
}
```

#### 创建API Key

```bash
POST /api/auth/api-key
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "my-project-key"
}
```

**响应**:
```json
{
  "success": true,
  "api_key": "ak_xxx...",
  "name": "my-project-key",
  "user_id": "user@example.com",
  "warning": "Save this API key securely. It will not be shown again."
}
```

### 方式2: 管理员创建用户

如果API提供者不想开放公开注册，可以手动创建用户：

```bash
POST /api/auth/user
Authorization: Bearer <admin_secret>
Content-Type: application/json

{
  "user_id": "user@example.com",
  "rate_limit": 1000,
  "plan": "basic"
}
```

**响应**:
```json
{
  "success": true,
  "user_id": "user@example.com",
  "rate_limit": 1000,
  "plan": "basic",
  "tokens": {
    "access_token": "at_xxx...",
    "refresh_token": "rt_xxx...",
    "token_type": "Bearer",
    "expires_in": 2592000,
    "expires_at": "2025-12-12T15:00:00",
    "plan": "basic",
    "is_paid": true
  },
  "message": "User created successfully. Tokens generated."
}
```

### 方式3: 登录获取Token

如果已有账户，可以直接登录获取Token：

```bash
POST /api/auth/login
Content-Type: application/json

{
  "user_id": "user@example.com",
  "plan": "free"
}
```

**响应**:
```json
{
  "success": true,
  "tokens": {
    "access_token": "at_xxx...",
    "refresh_token": "rt_xxx...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "expires_at": "2025-11-12T15:00:00",
    "plan": "free",
    "is_paid": false
  },
  "user_id": "user@example.com",
  "plan": "free"
}
```

---

## 🔄 Token管理和续期

### Token类型和有效期

#### 免费Token (Free Plan)
- **Access Token**: 1小时有效期
- **Refresh Token**: 7天有效期
- **特点**: 过期后需要重新登录或使用Refresh Token刷新

#### 付费Token (Basic/Premium Plan)
- **Access Token**: 30天有效期
- **Refresh Token**: 90天有效期
- **特点**: 可以续期，支持到期验证

### 检查Token状态

```bash
POST /api/auth/token-status
Content-Type: application/json

{
  "access_token": "at_xxx..."
}
```

或使用Header:

```bash
GET /api/auth/token-status
Authorization: Bearer <access_token>
```

**响应示例（有效Token）**:
```json
{
  "success": true,
  "status": {
    "valid": true,
    "expired": false,
    "expires_at": "2025-11-13T15:00:00",
    "remaining_seconds": 86400,
    "remaining_hours": 24,
    "plan": "basic",
    "is_paid": true
  }
}
```

**响应示例（过期Token）**:
```json
{
  "success": false,
  "status": {
    "valid": false,
    "expired": true,
    "expires_at": "2025-11-12T14:00:00",
    "expired_since": 3600,
    "plan": "basic",
    "is_paid": true,
    "can_renew": true
  }
}
```

### Token刷新（所有计划）

使用Refresh Token刷新Access Token：

```bash
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "rt_xxx..."
}
```

**响应**:
```json
{
  "success": true,
  "tokens": {
    "access_token": "at_new_xxx...",
    "refresh_token": "rt_new_xxx...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "expires_at": "2025-11-12T16:00:00",
    "plan": "free",
    "is_paid": false
  }
}
```

**重要说明**:
- ✅ **刷新时会返回新的Access Token和新的Refresh Token**
- ✅ **旧的Refresh Token使用后即失效，必须保存新的Refresh Token**
- ✅ **如果Refresh Token过期，需要重新注册或登录**
- ⚠️ **Refresh Token过期后无法刷新，必须重新获取**

**错误响应（Refresh Token过期）**:
```json
{
  "success": false,
  "error": "Invalid or expired refresh token"
}
```

### Token续期（仅付费计划）

付费Token可以续期，延长有效期：

```bash
POST /api/auth/renew
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "access_token": "at_xxx...",
  "expires_in": 2592000
}
```

**响应**:
```json
{
  "success": true,
  "message": "Token renewed successfully",
  "tokens": {
    "access_token": "at_new_xxx...",
    "refresh_token": "rt_new_xxx...",
    "token_type": "Bearer",
    "expires_in": 2592000,
    "expires_at": "2025-12-12T15:00:00",
    "plan": "premium",
    "is_paid": true
  }
}
```

**重要说明**:
- ✅ **续期时会返回新的Access Token和新的Refresh Token**
- ✅ **旧的Token使用后仍可使用直到过期，但建议立即使用新Token**
- ✅ **只有付费Token（`is_paid: true`）可以续期**
- ✅ **Token可以未过期时续期，也可以过期后续期（如果仍在Refresh Token有效期内）**
- ❌ **免费Token过期后只能使用Refresh Token刷新或重新登录**

**错误响应（免费Token尝试续期）**:
```json
{
  "success": false,
  "error": "Only paid tokens can be renewed. Please upgrade your plan."
}
```

**错误响应（Token无效）**:
```json
{
  "success": false,
  "error": "Invalid token"
}
```

### 升级计划并获取新Token

```bash
POST /api/upgrade
Authorization: Bearer <current_access_token>
Content-Type: application/json

{
  "plan": "premium"
}
```

**响应**:
```json
{
  "success": true,
  "message": "Plan upgraded from basic to premium",
  "old_plan": "basic",
  "new_plan": "premium",
  "rate_limit": 10000,
  "tokens": {
    "access_token": "at_new_xxx...",
    "refresh_token": "rt_new_xxx...",
    "expires_in": 2592000,
    "expires_at": "2025-12-12T15:00:00",
    "plan": "premium",
    "is_paid": true
  }
}
```

---

## 📡 核心API端点响应格式

### `/api/search` - 搜索新闻

**请求示例**:
```bash
POST /api/search
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "categories": ["tech"],
  "max_results": 10,
  "date_range": "today_and_yesterday"
}
```

**成功响应**:
```json
{
  "success": true,
  "count": 10,
  "news": [
    {
      "title": "新闻标题",
      "url": "https://example.com/news",
      "source": "来源名称",
      "published_at": "2025-11-12T10:00:00",
      "category": "tech",
      "language": "zh",
      "description": "新闻摘要",
      "image": "https://example.com/image.jpg"
    }
  ],
  "search_params": {
    "keywords": null,
    "categories": ["tech"],
    "languages": "all",
    "date_range": "today_and_yesterday",
    "max_results": 10
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "错误信息",
  "count": 0,
  "news": []
}
```

### `/api/download` - 下载新闻内容

**请求示例**:
```bash
POST /api/download
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "news_url": "https://example.com/news",
  "include_images": true,
  "include_banners": true
}
```

**成功响应**:
```json
{
  "url": "https://example.com/news",
  "title": "新闻标题",
  "content": "完整的新闻文本内容",
  "html_body": "<div>完整的HTML内容</div>",
  "images": [
    {
      "url": "https://example.com/image1.jpg",
      "alt": "图片描述"
    }
  ],
  "banners": [
    {
      "url": "https://example.com/banner.jpg",
      "alt": "横幅描述"
    }
  ],
  "videos": [
    {
      "url": "https://example.com/video.mp4",
      "type": "video/mp4"
    }
  ],
  "success": true
}
```

**错误响应**:
```json
{
  "url": "https://example.com/news",
  "title": "",
  "content": "",
  "images": [],
  "banners": [],
  "success": false,
  "error": "错误信息"
}
```

### `/api/archive` - 完整归档

**请求示例**:
```bash
POST /api/archive
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "categories": ["tech"],
  "max_results": 50,
  "download_content": true,
  "save_to_github": true,
  "save_format": "md_with_html"
}
```

**成功响应**:
```json
{
  "success": true,
  "search_results": {
    "count": 50,
    "news": [
      {
        "title": "新闻标题",
        "url": "https://example.com/news",
        "content": "完整内容",
        "html_body": "<div>HTML内容</div>",
        "images": [],
        "banners": [],
        "videos": [],
        "category": "tech"
      }
    ]
  },
  "download_enabled": true,
  "github_save_enabled": true,
  "saved_files": [
    "2025/11/12/tech.md",
    "2025/11/12/finance.md"
  ],
  "summary": {
    "total_news": 50,
    "with_content": 45,
    "with_html": 45,
    "with_images": 30,
    "with_videos": 5,
    "categories": {
      "tech": 30,
      "finance": 20
    }
  }
}
```

### `/api/auth/me` - 获取用户信息

**请求示例**:
```bash
GET /api/auth/me
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "success": true,
  "user_id": "user@example.com",
  "rate_limit": 100,
  "plan": "free",
  "is_paid": false,
  "rate_limit_info": {
    "limit": 100,
    "used": 5,
    "remaining": 95,
    "reset_at": 1762928400.0
  }
}
```

### `/api/auth/rate-limit` - 获取速率限制信息

**请求示例**:
```bash
GET /api/auth/rate-limit
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "success": true,
  "rate_limit_info": {
    "limit": 100,
    "used": 5,
    "remaining": 95,
    "reset_at": 1762928400.0
  },
  "plan": "free",
  "is_paid": false
}
```

### `/api/auth/users` - 列出所有用户（管理员）

**请求示例**:
```bash
GET /api/auth/users
Authorization: Bearer <admin_secret>
```

**响应**:
```json
{
  "success": true,
  "users": [],
  "total": 0,
  "message": "Stateless system: User information is not stored. Users are identified by their tokens."
}
```

### `/api/auth/api-keys` - 列出所有API Keys（管理员）

**请求示例**:
```bash
GET /api/auth/api-keys
Authorization: Bearer <admin_secret>
```

**响应**:
```json
{
  "success": true,
  "api_keys": [],
  "total": 0,
  "message": "Stateless system: API keys are not stored. Keys are self-contained tokens."
}
```

### `/` - API首页

**请求示例**:
```bash
GET /
Authorization: Bearer <api_key>  # 如果启用认证
```

**响应（已认证）**:
```json
{
  "service": "Global News Aggregator API",
  "version": "1.0.0",
  "status": "online",
  "config": {
    "NEWSAPI_KEY": false,
    "BING_API_KEY": false,
    "NEWSDATA_KEY": false,
    "SERPAPI_KEY": false,
    "GOOGLE_SEARCH_API_KEY": false
  },
  "available_sources": [
    "Hacker News API",
    "Google News RSS",
    "Product Hunt GraphQL"
  ],
  "endpoints": {
    "/": "GET - API首页",
    "/api/search": "POST/GET - 搜索全网新闻",
    "/api/download": "POST/GET - 下载新闻完整内容",
    "/api/health": "GET - 健康检查"
  },
  "usage": {
    "search": {
      "method": "POST/GET",
      "url": "/api/search",
      "body": {
        "keywords": "搜索关键词（可选）",
        "categories": ["科技", "商业", "体育"],
        "languages": "zh/en/all（默认all）",
        "date_range": "yesterday/last_7_days/last_30_days（默认last_7_days）",
        "max_results": "50"
      }
    },
    "download": {
      "method": "POST/GET",
      "url": "/api/download",
      "body": {
        "news_url": "新闻URL（必需）",
        "include_images": "true/false（默认true）",
        "include_banners": "true/false（默认true）"
      }
    }
  },
  "documentation": "https://github.com/clkhoo5211/upgraded-octo-fortnight"
}
```

**响应（未认证，如果启用认证）**:
```json
{
  "error": "Unauthorized",
  "message": "Authentication required. Please provide a valid API Key or Access Token.",
  "status_code": 401,
  "service": "Global News Aggregator API",
  "authentication": {
    "required": true,
    "methods": [
      "Authorization: Bearer <api_key>",
      "Authorization: Bearer <access_token>"
    ],
    "register_url": "/api/register",
    "login_url": "/api/auth/login"
  }
}
```

### `/api/health` - 健康检查

**请求示例**:
```bash
GET /api/health
```

**响应**:
```json
{
  "status": "healthy",
  "service": "Global News Aggregator",
  "version": "1.0.0",
  "service_status": "operational",
  "endpoints": {
    "/api/search": "POST/GET - 搜索全网新闻",
    "/api/download": "POST/GET - 下载新闻完整内容",
    "/api/health": "GET - 健康检查"
  },
  "free_features": {
    "search": true,
    "content_extraction": true,
    "multi_language": true,
    "quality_scoring": true
  },
  "premium_features": {
    "newsapi_source": false,
    "bing_news": false,
    "serpapi_search": false,
    "google_search": false,
    "github_token": false
  },
  "news_sources": {
    "free_sources": [
      "Hacker News API",
      "Google News RSS",
      "Product Hunt GraphQL",
      "Reddit JSON API"
    ],
    "premium_sources": []
  },
  "settings": {
    "intelligent_filtering": true,
    "production_mode": true
  }
}
```

---

## 💻 API使用示例

### Python完整示例（带Token管理）

```python
import requests
import os
from datetime import datetime
from typing import Optional, Dict

class NewsAPIClient:
    """News API客户端，自动处理Token过期和续期"""
    
    def __init__(self, api_key: Optional[str] = None, email: Optional[str] = None):
        """
        初始化客户端
        
        Args:
            api_key: API Key（如果已有）
            email: 用户邮箱（如果需要自动注册）
        """
        self.api_base = "https://upgraded-octo-fortnight.vercel.app"
        self.api_key = api_key or os.getenv('NEWS_API_KEY')
        self.email = email
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.plan = 'free'
        self.is_paid = False
        
        if not self.api_key and self.email:
            # 自动注册
            self._register()
    
    def _register(self):
        """注册用户并获取Token"""
        response = requests.post(
            f"{self.api_base}/api/register",
            json={'email': self.email, 'plan': 'free'}
        )
        data = response.json()
        
        if data.get('success'):
            self.access_token = data['tokens']['access_token']
            self.refresh_token = data['tokens']['refresh_token']
            self.token_expires_at = datetime.fromisoformat(data['tokens']['expires_at'])
            self.plan = data.get('plan', 'free')
            self.is_paid = data['tokens'].get('is_paid', False)
            
            # 创建API Key
            self._create_api_key()
    
    def _create_api_key(self):
        """创建API Key"""
        response = requests.post(
            f"{self.api_base}/api/auth/api-key",
            headers={'Authorization': f"Bearer {self.access_token}"},
            json={'name': 'default'}
        )
        data = response.json()
        if data.get('success'):
            self.api_key = data['api_key']
            print(f"✅ API Key已创建: {self.api_key[:20]}...")
    
    def _check_token_status(self) -> Dict:
        """检查Token状态"""
        if not self.access_token:
            return {'valid': False}
        
        response = requests.post(
            f"{self.api_base}/api/auth/token-status",
            json={'access_token': self.access_token}
        )
        return response.json().get('status', {})
    
    def _ensure_valid_token(self):
        """确保Token有效，如果过期则刷新或续期"""
        if not self.access_token:
            return
        
        status = self._check_token_status()
        
        if not status.get('valid'):
            if status.get('expired'):
                if self.is_paid and status.get('can_renew'):
                    # 付费Token可以续期
                    self._renew_token()
                elif self.refresh_token:
                    # 使用Refresh Token刷新
                    self._refresh_token()
                else:
                    # 重新登录
                    self._login()
            else:
                # Token无效，重新登录
                self._login()
    
    def _refresh_token(self):
        """刷新Token"""
        response = requests.post(
            f"{self.api_base}/api/auth/refresh",
            json={'refresh_token': self.refresh_token}
        )
        data = response.json()
        if data.get('success'):
            tokens = data['tokens']
            # 重要：保存新的Access Token和Refresh Token
            self.access_token = tokens['access_token']
            self.refresh_token = tokens['refresh_token']  # 新的Refresh Token
            self.token_expires_at = datetime.fromisoformat(tokens['expires_at'])
            print("✅ Token已刷新，已保存新的Refresh Token")
    
    def _renew_token(self):
        """续期Token（仅付费计划）"""
        response = requests.post(
            f"{self.api_base}/api/auth/renew",
            headers={'Authorization': f"Bearer {self.access_token}"},
            json={'access_token': self.access_token}
        )
        data = response.json()
        if data.get('success'):
            tokens = data['tokens']
            # 重要：保存新的Access Token和Refresh Token
            self.access_token = tokens['access_token']
            self.refresh_token = tokens['refresh_token']  # 新的Refresh Token
            self.token_expires_at = datetime.fromisoformat(tokens['expires_at'])
            print("✅ Token已续期，已保存新的Refresh Token")
    
    def _login(self):
        """登录获取Token"""
        if not self.email:
            raise Exception("Email required for login")
        
        response = requests.post(
            f"{self.api_base}/api/auth/login",
            json={'user_id': self.email}
        )
        data = response.json()
        if data.get('success'):
            tokens = data['tokens']
            self.access_token = tokens['access_token']
            self.refresh_token = tokens['refresh_token']
            self.token_expires_at = datetime.fromisoformat(tokens['expires_at'])
            self.plan = data.get('plan', 'free')
            self.is_paid = tokens.get('is_paid', False)
    
    def search_news(self, **kwargs):
        """搜索新闻"""
        # 如果使用Access Token，先检查有效性
        if self.access_token and not self.api_key:
            self._ensure_valid_token()
            token = self.access_token
        else:
            token = self.api_key
        
        if not token:
            raise Exception("No API key or access token available")
        
        response = requests.post(
            f"{self.api_base}/api/search",
            headers={'Authorization': f"Bearer {token}"},
            json=kwargs,
            timeout=30
        )
        
        if response.status_code == 401:
            # Token可能过期，尝试刷新
            if self.access_token:
                self._ensure_valid_token()
                token = self.access_token
                response = requests.post(
                    f"{self.api_base}/api/search",
                    headers={'Authorization': f"Bearer {token}"},
                    json=kwargs
                )
        
        if response.status_code == 429:
            retry_after = response.headers.get('Retry-After', '3600')
            raise Exception(f"Rate limit exceeded. Retry after {retry_after} seconds")
        
        response.raise_for_status()
        return response.json()
    
    def upgrade_plan(self, new_plan: str):
        """升级计划"""
        if not self.access_token:
            raise Exception("Access token required for upgrade")
        
        self._ensure_valid_token()
        
        response = requests.post(
            f"{self.api_base}/api/upgrade",
            headers={'Authorization': f"Bearer {self.access_token}"},
            json={'plan': new_plan}
        )
        
        data = response.json()
        if data.get('success'):
            tokens = data['tokens']
            self.access_token = tokens['access_token']
            self.refresh_token = tokens['refresh_token']
            self.token_expires_at = datetime.fromisoformat(tokens['expires_at'])
            self.plan = new_plan
            self.is_paid = tokens.get('is_paid', False)
            print(f"✅ 计划已升级到 {new_plan}")
        
        return data

# 使用示例
if __name__ == "__main__":
    # 方式1: 使用API Key
    client = NewsAPIClient(api_key="ak_xxx...")
    results = client.search_news(categories=["tech"], max_results=10)
    print(f"找到 {results['count']} 条新闻")
    
    # 方式2: 自动注册
    client = NewsAPIClient(email="user@example.com")
    results = client.search_news(categories=["tech"], max_results=10)
    
    # 方式3: 升级计划
    client.upgrade_plan("premium")
```

### JavaScript完整示例

```javascript
class NewsAPIClient {
    constructor(apiKey, email) {
        this.apiBase = 'https://upgraded-octo-fortnight.vercel.app';
        this.apiKey = apiKey || process.env.NEWS_API_KEY;
        this.email = email;
        this.accessToken = null;
        this.refreshToken = null;
        this.tokenExpiresAt = null;
        this.plan = 'free';
        this.isPaid = false;
        
        if (!this.apiKey && this.email) {
            this.register();
        }
    }
    
    async register() {
        const response = await fetch(`${this.apiBase}/api/register`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email: this.email, plan: 'free'})
        });
        
        const data = await response.json();
        if (data.success) {
            this.accessToken = data.tokens.access_token;
            this.refreshToken = data.tokens.refresh_token;
            this.tokenExpiresAt = new Date(data.tokens.expires_at);
            this.plan = data.plan;
            this.isPaid = data.tokens.is_paid;
            
            // 创建API Key
            await this.createApiKey();
        }
    }
    
    async createApiKey() {
        const response = await fetch(`${this.apiBase}/api/auth/api-key`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.accessToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({name: 'default'})
        });
        
        const data = await response.json();
        if (data.success) {
            this.apiKey = data.api_key;
            console.log(`✅ API Key已创建: ${this.apiKey.substring(0, 20)}...`);
        }
    }
    
    async checkTokenStatus() {
        if (!this.accessToken) return {valid: false};
        
        const response = await fetch(`${this.apiBase}/api/auth/token-status`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({access_token: this.accessToken})
        });
        
        const data = await response.json();
        return data.status || {};
    }
    
    async ensureValidToken() {
        if (!this.accessToken) return;
        
        const status = await this.checkTokenStatus();
        
        if (!status.valid) {
            if (status.expired) {
                if (this.isPaid && status.can_renew) {
                    await this.renewToken();
                } else if (this.refreshToken) {
                    await this.refreshToken();
                } else {
                    await this.login();
                }
            } else {
                await this.login();
            }
        }
    }
    
    async refreshToken() {
        const response = await fetch(`${this.apiBase}/api/auth/refresh`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({refresh_token: this.refreshToken})
        });
        
        const data = await response.json();
        if (data.success) {
            // 重要：保存新的Access Token和Refresh Token
            this.accessToken = data.tokens.access_token;
            this.refreshToken = data.tokens.refresh_token;  // 新的Refresh Token
            this.tokenExpiresAt = new Date(data.tokens.expires_at);
            console.log('✅ Token已刷新，已保存新的Refresh Token');
        }
    }
    
    async renewToken() {
        const response = await fetch(`${this.apiBase}/api/auth/renew`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.accessToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({access_token: this.accessToken})
        });
        
        const data = await response.json();
        if (data.success) {
            // 重要：保存新的Access Token和Refresh Token
            this.accessToken = data.tokens.access_token;
            this.refreshToken = data.tokens.refresh_token;  // 新的Refresh Token
            this.tokenExpiresAt = new Date(data.tokens.expires_at);
            console.log('✅ Token已续期，已保存新的Refresh Token');
        }
    }
    
    async searchNews(options = {}) {
        // 如果使用Access Token，先检查有效性
        if (this.accessToken && !this.apiKey) {
            await this.ensureValidToken();
        }
        
        const token = this.apiKey || this.accessToken;
        if (!token) {
            throw new Error('No API key or access token available');
        }
        
        const response = await fetch(`${this.apiBase}/api/search`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(options)
        });
        
        if (response.status === 401 && this.accessToken) {
            await this.ensureValidToken();
            const retryResponse = await fetch(`${this.apiBase}/api/search`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.accessToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(options)
            });
            return await retryResponse.json();
        }
        
        if (response.status === 429) {
            const retryAfter = response.headers.get('Retry-After');
            throw new Error(`Rate limit exceeded. Retry after ${retryAfter} seconds`);
        }
        
        return await response.json();
    }
    
    async upgradePlan(newPlan) {
        if (!this.accessToken) {
            throw new Error('Access token required for upgrade');
        }
        
        await this.ensureValidToken();
        
        const response = await fetch(`${this.apiBase}/api/upgrade`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.accessToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({plan: newPlan})
        });
        
        const data = await response.json();
        if (data.success) {
            this.accessToken = data.tokens.access_token;
            this.refreshToken = data.tokens.refresh_token;
            this.tokenExpiresAt = new Date(data.tokens.expires_at);
            this.plan = newPlan;
            this.isPaid = data.tokens.is_paid;
            console.log(`✅ 计划已升级到 ${newPlan}`);
        }
        
        return data;
    }
}

// 使用示例
(async () => {
    // 方式1: 使用API Key
    const client1 = new NewsAPIClient('ak_xxx...');
    const results1 = await client1.searchNews({categories: ['tech'], max_results: 10});
    console.log(`找到 ${results1.count} 条新闻`);
    
    // 方式2: 自动注册
    const client2 = new NewsAPIClient(null, 'user@example.com');
    await new Promise(resolve => setTimeout(resolve, 2000)); // 等待注册完成
    const results2 = await client2.searchNews({categories: ['tech'], max_results: 10});
    
    // 方式3: 升级计划
    await client2.upgradePlan('premium');
})();
```

---

## ⚠️ 错误处理

### 常见错误码

| 状态码 | 说明 | 解决方案 |
|--------|------|----------|
| `200` | 成功 | - |
| `400` | 请求参数错误 | 检查请求参数 |
| `401` | 未认证或Token无效/过期 | 刷新Token或重新登录 |
| `403` | 权限不足 | 检查用户是否被禁用或计划限制 |
| `429` | 速率限制 | 等待后重试或升级计划 |
| `500` | 服务器错误 | 稍后重试或联系支持 |

### Token过期处理流程

#### 使用过期Token访问API的返回信息

当使用过期或无效的Token访问API时，会返回以下错误：

**HTTP状态码**: `401 Unauthorized`

**响应体**:
```json
{
  "error": "Invalid token",
  "message": "The provided token is invalid or expired"
}
```

#### Token过期处理流程

```python
def handle_token_expiry(client, func, *args, **kwargs):
    """处理Token过期的通用函数"""
    try:
        return func(*args, **kwargs)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            error_data = e.response.json()
            if 'expired' in error_data.get('message', '').lower() or 'invalid' in error_data.get('message', '').lower():
                # Token过期或无效，尝试刷新
                if client.refresh_token:
                    # 使用Refresh Token刷新（会返回新的Access Token和Refresh Token）
                    client._refresh_token()
                    # 重要：保存新的Refresh Token
                    return func(*args, **kwargs)
                elif client.is_paid:
                    # 付费Token可以续期（会返回新的Access Token和Refresh Token）
                    client._renew_token()
                    # 重要：保存新的Refresh Token
                    return func(*args, **kwargs)
                else:
                    # 免费Token需要重新登录
                    client._login()
                    return func(*args, **kwargs)
        raise
```

#### 刷新Token后的处理

**重要**: 刷新或续期Token后，**必须保存新的Refresh Token**，因为旧的Refresh Token会失效。

```python
def _refresh_token(self):
    """刷新Token"""
    response = requests.post(
        f"{self.api_base}/api/auth/refresh",
        json={'refresh_token': self.refresh_token}
    )
    data = response.json()
    if data.get('success'):
        tokens = data['tokens']
        # 保存新的Access Token和Refresh Token
        self.access_token = tokens['access_token']
        self.refresh_token = tokens['refresh_token']  # 重要：保存新的Refresh Token
        self.token_expires_at = datetime.fromisoformat(tokens['expires_at'])
        print("✅ Token已刷新，已保存新的Refresh Token")
```

#### 续期Token后的处理

```python
def _renew_token(self):
    """续期Token（仅付费计划）"""
    response = requests.post(
        f"{self.api_base}/api/auth/renew",
        headers={'Authorization': f"Bearer {self.access_token}"},
        json={'access_token': self.access_token}
    )
    data = response.json()
    if data.get('success'):
        tokens = data['tokens']
        # 保存新的Access Token和Refresh Token
        self.access_token = tokens['access_token']
        self.refresh_token = tokens['refresh_token']  # 重要：保存新的Refresh Token
        self.token_expires_at = datetime.fromisoformat(tokens['expires_at'])
        print("✅ Token已续期，已保存新的Refresh Token")
```

---

## 💰 商业模式

### 计划对比

| 特性 | Free | Basic | Premium |
|------|------|-------|---------|
| 速率限制 | 100/小时 | 1,000/小时 | 10,000/小时 |
| Token有效期 | 1小时 | 30天 | 30天 |
| Refresh Token | 7天 | 90天 | 90天 |
| Token续期 | ❌ | ✅ | ✅ |
| 价格 | 免费 | $9/月 | $29/月 |

### 付费流程

1. **用户注册免费计划**
2. **测试API功能**
3. **升级到付费计划** (`POST /api/upgrade`)
4. **自动获得新的30天Token**
5. **Token过期前续期** (`POST /api/auth/renew`)

---

## 📝 完整工作流程

### 对于普通用户

#### 场景1: 首次使用（免费计划）

```python
# 1. 注册
client = NewsAPIClient(email="user@example.com")

# 2. 使用API（自动使用API Key）
results = client.search_news(categories=["tech"])

# 3. Token过期时自动刷新
# 客户端会自动处理Token刷新
```

#### 场景2: 升级到付费计划

```python
# 1. 升级计划
client.upgrade_plan("premium")

# 2. 获得新的30天Token
# 3. Token过期前续期
status = client.checkTokenStatus()
if status.get('remaining_hours', 0) < 24:  # 剩余不足24小时
    client.renewToken()
```

#### 场景3: 使用API Key（推荐）

```python
# 1. 注册并获取API Key
client = NewsAPIClient(email="user@example.com")
# API Key已自动创建

# 2. 保存API Key到环境变量
# export NEWS_API_KEY=ak_xxx...

# 3. 在其他项目中使用
client = NewsAPIClient(api_key=os.getenv('NEWS_API_KEY'))
```

### 对于API提供者

#### 环境变量设置

在Vercel Dashboard设置：

```
ENABLE_API_AUTH=true
ADMIN_SECRET=your-secret-admin-key-here
```

#### 用户管理

```bash
# 查看所有用户
curl -H "Authorization: Bearer <admin_secret>" \
  https://upgraded-octo-fortnight.vercel.app/api/auth/users

# 手动创建用户
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/user \
  -H "Authorization: Bearer <admin_secret>" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user@example.com", "rate_limit": 1000, "plan": "basic"}'

# 升级用户计划
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/user \
  -H "Authorization: Bearer <admin_secret>" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user@example.com", "rate_limit": 10000, "plan": "premium"}'
```

---

## 🔍 Token到期验证逻辑

### 免费Token

- **过期时间**: 1小时
- **过期后**: 
  - ✅ 可以使用Refresh Token刷新（7天内）
  - ✅ 可以重新登录获取新Token
  - ❌ 不能续期

### 付费Token

- **过期时间**: 30天
- **过期后**:
  - ✅ 可以使用Refresh Token刷新（90天内）
  - ✅ 可以续期（`POST /api/auth/renew`）
  - ✅ 可以重新登录获取新Token

### 验证Token是否过期

```python
def is_token_expired(access_token):
    """检查Token是否过期"""
    response = requests.post(
        'https://upgraded-octo-fortnight.vercel.app/api/auth/token-status',
        json={'access_token': access_token}
    )
    status = response.json().get('status', {})
    return status.get('expired', False)

def check_and_refresh_token(client):
    """检查Token状态并在需要时刷新"""
    status = client._check_token_status()
    
    if not status.get('valid'):
        if status.get('expired'):
            if client.is_paid and status.get('can_renew'):
                # 付费Token可以续期
                client._renew_token()
                print("✅ Token已续期")
            elif client.refresh_token:
                # 使用Refresh Token刷新
                client._refresh_token()
                print("✅ Token已刷新")
            else:
                # 需要重新登录
                client._login()
                print("✅ 已重新登录")
        else:
            # Token无效
            print("❌ Token无效，需要重新登录")
            client._login()
```

### Token刷新和续期的关键点

1. **刷新Token时**:
   - ✅ 返回**新的Access Token**和**新的Refresh Token**
   - ✅ 旧的Refresh Token使用后即失效
   - ⚠️ **必须保存新的Refresh Token**，否则下次无法刷新

2. **续期Token时**:
   - ✅ 返回**新的Access Token**和**新的Refresh Token**
   - ✅ 旧的Token仍可使用直到过期
   - ⚠️ **建议立即使用新Token**，并保存新的Refresh Token

3. **Token过期时**:
   - ❌ 使用过期Token访问API返回 `401 Unauthorized`
   - ✅ 可以使用Refresh Token刷新（如果未过期）
   - ✅ 付费Token可以续期（如果Refresh Token未过期）
   - ❌ 如果Refresh Token也过期，必须重新注册或登录

---

## 📊 所有可用端点总结

### 认证和注册

| 端点 | 方法 | 说明 | 需要认证 |
|------|------|------|----------|
| `/api/register` | POST | 用户注册 | ❌ |
| `/api/auth/login` | POST | 登录获取Token | ❌ |
| `/api/auth/refresh` | POST | 刷新Token | ❌ |
| `/api/auth/renew` | POST | 续期Token（付费） | ✅ |
| `/api/auth/api-key` | POST | 创建API Key | ✅ |
| `/api/auth/me` | GET | 获取用户信息 | ✅ |
| `/api/auth/rate-limit` | GET | 获取速率限制 | ✅ |
| `/api/auth/token-status` | POST/GET | 获取Token状态 | ✅ |
| `/api/upgrade` | POST | 升级计划 | ✅ |

### API功能

| 端点 | 方法 | 说明 | 需要认证 |
|------|------|------|----------|
| `/api/search` | GET/POST | 搜索新闻 | ✅（如果启用） |
| `/api/download` | GET/POST | 下载内容 | ✅（如果启用） |
| `/api/archive` | POST | 完整归档 | ✅（如果启用） |
| `/api/auto_archive` | GET | 自动归档 | ❌ |

### 管理端点（管理员）

| 端点 | 方法 | 说明 | 需要认证 |
|------|------|------|----------|
| `/api/auth/user` | POST | 创建用户 | ✅ Admin |
| `/api/auth/users` | GET | 列出用户 | ✅ Admin |
| `/api/auth/api-keys` | GET | 列出API Keys | ✅ Admin |

---

## ✅ 总结

### Token管理最佳实践

1. **使用API Key**（推荐）
   - 长期有效，不需要刷新
   - 适合生产环境
   - 无需处理Token过期问题

2. **使用Access Token**
   - 免费计划：1小时，需要定期刷新
   - 付费计划：30天，可以续期
   - ⚠️ **必须保存Refresh Token**，用于刷新Access Token

3. **Token过期处理**
   - **免费Token过期**：
     - ✅ 使用Refresh Token刷新（返回新的Access Token和Refresh Token）
     - ✅ 如果Refresh Token也过期，需要重新注册或登录
   - **付费Token过期**：
     - ✅ 使用Refresh Token刷新（返回新的Access Token和Refresh Token）
     - ✅ 可以续期（返回新的Access Token和Refresh Token）
     - ✅ 如果Refresh Token也过期，需要重新注册或登录

4. **重要提醒**
   - ⚠️ **刷新或续期Token后，必须保存新的Refresh Token**
   - ⚠️ **旧的Refresh Token使用后即失效**
   - ⚠️ **如果丢失新的Refresh Token，下次Token过期时无法刷新**
   - ✅ **建议将Refresh Token存储在安全的地方（环境变量、密钥管理服务等）**

### 对接步骤

1. ✅ 用户注册 (`POST /api/register`)
2. ✅ 创建API Key (`POST /api/auth/api-key`)
3. ✅ 使用API Key调用API
4. ✅ 监控Token状态（如果使用Access Token）
5. ✅ 处理Token过期（自动刷新或续期）

---

## 📚 相关文档

- [API使用指南](./API_USAGE_GUIDE.md) - 完整的API端点说明
- [API安全指南](../security/API_SECURITY_GUIDE.md) - 认证和安全配置
- [用户注册指南](../security/USER_REGISTRATION_GUIDE.md) - 用户注册流程
- [商业模式指南](../security/BUSINESS_MODEL_GUIDE.md) - 商业模式实现
- [快速开始指南](./QUICK_START.md) - 5分钟快速上手

## 🎯 使用此文档

**是的，这个文档就是您在其他项目中集成此API的完整指南！**

### 文档包含的内容：

✅ **快速开始** - 5分钟快速对接示例  
✅ **用户注册和Token获取** - 完整的注册流程  
✅ **Token管理和续期** - Token生命周期管理  
✅ **API使用示例** - Python和JavaScript完整示例代码  
✅ **错误处理** - 常见错误和解决方案  
✅ **商业模式** - 计划对比和付费流程  
✅ **完整工作流程** - 不同场景的使用示例  
✅ **Token到期验证** - 过期处理逻辑  
✅ **所有端点总结** - 完整的API端点列表  

### 快速开始步骤：

1. **阅读"快速开始"章节** - 了解基本用法
2. **复制示例代码** - Python或JavaScript客户端代码
3. **注册用户** - 获取Access Token和API Key
4. **开始使用** - 调用API端点

### 示例代码位置：

文档中包含了完整的、可直接使用的客户端代码：
- **Python示例** (第340-526行) - `NewsAPIClient`类
- **JavaScript示例** (第528-738行) - `NewsAPIClient`类

这些代码可以直接复制到您的项目中使用！

---

**最后更新**: 2025-11-12

