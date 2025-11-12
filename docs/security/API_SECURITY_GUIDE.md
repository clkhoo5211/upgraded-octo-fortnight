# API 安全认证和授权指南

## 🔐 概述

本API现在支持完整的认证和授权系统，包括：

- ✅ **API Key认证** - 长期有效的API密钥
- ✅ **Access Token + Refresh Token** - 短期访问令牌和刷新令牌
- ✅ **速率限制** - 防止API滥用和spam攻击
- ✅ **用户管理** - 指定授权用户才能使用
- ✅ **HTTPS加密** - Vercel自动提供HTTPS加密

---

## 🚀 快速开始

### 场景1: API管理员设置认证系统

#### 步骤1: 启用认证

在Vercel Dashboard设置环境变量：

```
ENABLE_API_AUTH=true
ADMIN_SECRET=your-secret-admin-key-here
```

#### 步骤2: 创建用户

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/user \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-admin-secret" \
  -d '{
    "user_id": "user123",
    "rate_limit": 1000
  }'
```

#### 步骤3: 为用户生成API Key

```bash
# 首先用户登录获取Access Token
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'

# 使用Access Token创建API Key
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/api-key \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"name": "production-key"}'
```

### 场景2: 在其他仓库/项目中使用API

#### 步骤1: 获取API Key

联系API管理员获取API Key，或使用已有的用户ID登录：

```bash
# 登录获取Token
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "your-user-id"}'

# 创建API Key（推荐用于生产环境）
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/api-key \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-project-key"}'
```

#### 步骤2: 保存API Key到安全位置

**GitHub仓库**:
1. 进入仓库 Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. 名称: `NEWS_API_KEY`
4. 值: 你的API Key（`ak_xxx...`）

**本地项目**:
创建`.env`文件（不要提交到Git）:
```
NEWS_API_KEY=ak_xxx...
```

#### 步骤3: 在代码中使用API Key

**Python示例**:
```python
import os
import requests

API_KEY = os.getenv('NEWS_API_KEY')
API_BASE = "https://upgraded-octo-fortnight.vercel.app"

response = requests.post(
    f"{API_BASE}/api/search",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"categories": ["tech"], "max_results": 10}
)
```

**JavaScript示例**:
```javascript
const API_KEY = process.env.NEWS_API_KEY;
const API_BASE = 'https://upgraded-octo-fortnight.vercel.app';

const response = await fetch(`${API_BASE}/api/search`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    categories: ['tech'],
    max_results: 10
  })
});
```

**GitHub Actions示例**:
```yaml
- name: Fetch news
  env:
    API_KEY: ${{ secrets.NEWS_API_KEY }}
  run: |
    curl -X POST https://upgraded-octo-fortnight.vercel.app/api/search \
      -H "Authorization: Bearer $API_KEY" \
      -H "Content-Type: application/json" \
      -d '{"categories": ["tech"], "max_results": 10}'
```

#### 步骤4: Token刷新（如果使用Access Token）

如果使用Access Token而不是API Key，需要定期刷新：

```python
import requests
import os
from datetime import datetime, timedelta

class NewsAPIClient:
    def __init__(self, user_id, refresh_token=None):
        self.user_id = user_id
        self.refresh_token = refresh_token
        self.access_token = None
        self.token_expires_at = None
        self.api_base = "https://upgraded-octo-fortnight.vercel.app"
    
    def _ensure_valid_token(self):
        """确保Token有效，如果过期则刷新"""
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return  # Token仍然有效
        
        # Token过期或不存在，刷新
        if self.refresh_token:
            self._refresh_token()
        else:
            self._login()
    
    def _login(self):
        """登录获取Token"""
        response = requests.post(
            f"{self.api_base}/api/auth/login",
            json={"user_id": self.user_id}
        )
        data = response.json()
        self.access_token = data['tokens']['access_token']
        self.refresh_token = data['tokens']['refresh_token']
        expires_at = datetime.fromisoformat(data['tokens']['expires_at'])
        self.token_expires_at = expires_at
    
    def _refresh_token(self):
        """刷新Token"""
        response = requests.post(
            f"{self.api_base}/api/auth/refresh",
            json={"refresh_token": self.refresh_token}
        )
        data = response.json()
        self.access_token = data['tokens']['access_token']
        self.refresh_token = data['tokens']['refresh_token']
        expires_at = datetime.fromisoformat(data['tokens']['expires_at'])
        self.token_expires_at = expires_at
    
    def search_news(self, **kwargs):
        """搜索新闻"""
        self._ensure_valid_token()
        
        response = requests.post(
            f"{self.api_base}/api/search",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json=kwargs
        )
        return response.json()

# 使用示例
client = NewsAPIClient("user123")
results = client.search_news(categories=["tech"], max_results=10)
```

### 完整工作流程示例

#### 在GitHub Actions中使用

```yaml
name: Daily News Fetch

on:
  schedule:
    - cron: '0 9 * * *'  # 每天UTC 9点
  workflow_dispatch:

jobs:
  fetch:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Fetch news
        env:
          API_KEY: ${{ secrets.NEWS_API_KEY }}
        run: |
          curl -X POST https://upgraded-octo-fortnight.vercel.app/api/search \
            -H "Authorization: Bearer $API_KEY" \
            -H "Content-Type: application/json" \
            -d '{
              "categories": ["tech", "finance"],
              "date_range": "today_and_yesterday",
              "max_results": 50
            }' > news.json
      
      - name: Commit results
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add news.json
          git commit -m "Update news" || exit 0
          git push
```

#### 在Python项目中使用

```python
# requirements.txt
requests>=2.31.0

# main.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()  # 加载.env文件

API_KEY = os.getenv('NEWS_API_KEY')
API_BASE = "https://upgraded-octo-fortnight.vercel.app"

def fetch_news(categories=None, max_results=50):
    """获取新闻"""
    response = requests.post(
        f"{API_BASE}/api/search",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "categories": categories,
            "date_range": "today_and_yesterday",
            "max_results": max_results
        },
        timeout=30
    )
    
    if response.status_code == 401:
        raise Exception("无效的API Key，请检查环境变量")
    elif response.status_code == 429:
        retry_after = response.headers.get('Retry-After', '3600')
        raise Exception(f"速率限制，请在 {retry_after} 秒后重试")
    
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    results = fetch_news(categories=["tech"], max_results=10)
    print(f"找到 {results['count']} 条新闻")
    for news in results['news']:
        print(f"- {news['title']}")
```

#### 在Node.js项目中使用

```javascript
// package.json
{
  "dependencies": {
    "dotenv": "^16.0.0",
    "node-fetch": "^3.0.0"
  }
}

// index.js
require('dotenv').config();
const fetch = require('node-fetch');

const API_KEY = process.env.NEWS_API_KEY;
const API_BASE = 'https://upgraded-octo-fortnight.vercel.app';

async function fetchNews(categories, maxResults = 50) {
  const response = await fetch(`${API_BASE}/api/search`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      categories,
      date_range: 'today_and_yesterday',
      max_results: maxResults
    })
  });
  
  if (response.status === 401) {
    throw new Error('无效的API Key，请检查环境变量');
  }
  
  if (response.status === 429) {
    const retryAfter = response.headers.get('Retry-After');
    throw new Error(`速率限制，请在 ${retryAfter} 秒后重试`);
  }
  
  return await response.json();
}

// 使用
fetchNews(['tech'], 10)
  .then(results => {
    console.log(`找到 ${results.count} 条新闻`);
    results.news.forEach(news => {
      console.log(`- ${news.title}`);
    });
  })
  .catch(error => console.error(error));
```

---

## 📋 认证方式

### 方式1: Authorization Header（推荐）

```bash
Authorization: Bearer <api_key_or_token>
```

### 方式2: X-API-Key Header

```bash
X-API-Key: <api_key>
```

### 方式3: Query参数

```bash
?api_key=<api_key>
```

---

## 🔑 API端点

### 认证管理端点

#### 1. 登录获取Token

```bash
POST /api/auth/login
Content-Type: application/json

{
  "user_id": "user123"
}
```

**响应**:
```json
{
  "success": true,
  "tokens": {
    "access_token": "at_xxx",
    "refresh_token": "rt_xxx",
    "token_type": "Bearer",
    "expires_in": 3600,
    "expires_at": "2025-11-12T14:00:00"
  },
  "user_id": "user123"
}
```

#### 2. 刷新Access Token

```bash
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "rt_xxx"
}
```

**响应**:
```json
{
  "success": true,
  "tokens": {
    "access_token": "at_new_xxx",
    "refresh_token": "rt_new_xxx",
    "token_type": "Bearer",
    "expires_in": 3600,
    "expires_at": "2025-11-12T15:00:00"
  }
}
```

#### 3. 创建API Key

```bash
POST /api/auth/api-key
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "my-api-key"
}
```

**响应**:
```json
{
  "success": true,
  "api_key": "ak_xxx",
  "name": "my-api-key",
  "user_id": "user123",
  "warning": "Save this API key securely. It will not be shown again."
}
```

#### 4. 获取当前用户信息

```bash
GET /api/auth/me
Authorization: Bearer <token>
```

**响应**:
```json
{
  "success": true,
  "user_id": "user123",
  "rate_limit": 1000,
  "rate_limit_info": {
    "limit": 1000,
    "used": 45,
    "remaining": 955,
    "reset_at": 1734000000
  }
}
```

#### 5. 获取速率限制信息

```bash
GET /api/auth/rate-limit
Authorization: Bearer <token>
```

#### 6. 撤销API Key

```bash
DELETE /api/auth/api-key
Content-Type: application/json

{
  "api_key": "ak_xxx"
}
```

#### 7. 撤销Token

```bash
DELETE /api/auth/token
Content-Type: application/json

{
  "access_token": "at_xxx"
}
```

### 管理员端点

#### 创建用户

```bash
POST /api/auth/user
Authorization: Bearer <admin_secret>
Content-Type: application/json

{
  "user_id": "user123",
  "rate_limit": 1000
}
```

#### 列出所有用户

```bash
GET /api/auth/users
Authorization: Bearer <admin_secret>
```

#### 列出所有API Keys

```bash
GET /api/auth/api-keys
Authorization: Bearer <admin_secret>
```

---

## ⚡ 速率限制

### 默认限制

- **默认用户**: 1000 请求/小时
- **可自定义**: 每个用户可以设置不同的速率限制

### 速率限制响应

当超过速率限制时，API返回：

```json
{
  "error": "Rate limit exceeded",
  "message": "Rate limit exceeded. Limit: 1000 requests/hour",
  "limit": 1000,
  "remaining": 0,
  "reset_at": 1734000000
}
```

**HTTP状态码**: `429 Too Many Requests`

**响应头**:
```
Retry-After: 3600
```

### 检查速率限制

```bash
GET /api/auth/rate-limit
Authorization: Bearer <token>
```

---

## 🔒 安全最佳实践

### 1. 保护API Key

- ✅ **永远不要**在客户端代码中硬编码API Key
- ✅ **使用环境变量**存储API Key
- ✅ **定期轮换**API Key
- ✅ **使用HTTPS**传输（Vercel自动提供）

### 2. Token管理

- ✅ Access Token有效期：1小时
- ✅ Refresh Token有效期：30天
- ✅ 及时撤销不再使用的Token
- ✅ 使用Refresh Token刷新Access Token

### 3. 速率限制

- ✅ 根据实际需求设置合理的速率限制
- ✅ 监控API使用情况
- ✅ 实现客户端重试逻辑（指数退避）

---

## 💻 代码示例

### Python示例

```python
import requests

API_BASE = "https://upgraded-octo-fortnight.vercel.app"
API_KEY = "ak_your-api-key-here"  # 从环境变量获取

def search_news(keywords=None, categories=None):
    """搜索新闻（带认证）"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "keywords": keywords,
        "categories": categories,
        "max_results": 10
    }
    
    response = requests.post(
        f"{API_BASE}/api/search",
        json=payload,
        headers=headers
    )
    
    if response.status_code == 401:
        print("认证失败：无效的API Key")
        return None
    elif response.status_code == 429:
        print("速率限制：请求过于频繁")
        return None
    
    response.raise_for_status()
    return response.json()

# 使用示例
results = search_news(keywords="AI", categories=["tech"])
if results:
    print(f"找到 {results['count']} 条新闻")
```

### JavaScript示例

```javascript
const API_BASE = 'https://upgraded-octo-fortnight.vercel.app';
const API_KEY = process.env.API_KEY; // 从环境变量获取

async function searchNews(keywords, categories) {
  const response = await fetch(`${API_BASE}/api/search`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      keywords,
      categories,
      max_results: 10
    })
  });
  
  if (response.status === 401) {
    throw new Error('认证失败：无效的API Key');
  }
  
  if (response.status === 429) {
    const retryAfter = response.headers.get('Retry-After');
    throw new Error(`速率限制：请在 ${retryAfter} 秒后重试`);
  }
  
  return await response.json();
}

// 使用示例
searchNews('AI', ['tech'])
  .then(results => console.log(`找到 ${results.count} 条新闻`))
  .catch(error => console.error(error));
```

### 带重试的Python示例

```python
import requests
import time
from typing import Optional

def search_with_retry(
    keywords: Optional[str] = None,
    categories: Optional[list] = None,
    max_retries: int = 3
):
    """带重试和速率限制处理的搜索"""
    API_BASE = "https://upgraded-octo-fortnight.vercel.app"
    API_KEY = os.getenv("API_KEY")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "keywords": keywords,
        "categories": categories,
        "max_results": 10
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{API_BASE}/api/search",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 429:
                # 速率限制，等待后重试
                retry_after = int(response.headers.get('Retry-After', 3600))
                if attempt < max_retries - 1:
                    print(f"速率限制，等待 {retry_after} 秒后重试...")
                    time.sleep(retry_after)
                    continue
                else:
                    raise Exception("速率限制：已达到最大重试次数")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避
                print(f"请求失败，{wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                raise
    
    return None
```

---

## 🔧 配置说明

### 环境变量

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `ENABLE_API_AUTH` | 否 | `false` | 是否启用API认证 |
| `ADMIN_SECRET` | 是（启用认证时） | - | 管理员密钥 |

### Token配置

- **Access Token有效期**: 1小时（3600秒）
- **Refresh Token有效期**: 30天
- **默认速率限制**: 1000 请求/小时

---

## 📊 监控和管理

### 查看用户使用情况

```bash
# 获取当前用户信息
curl -H "Authorization: Bearer <token>" \
  https://upgraded-octo-fortnight.vercel.app/api/auth/me

# 获取速率限制信息
curl -H "Authorization: Bearer <token>" \
  https://upgraded-octo-fortnight.vercel.app/api/auth/rate-limit
```

### 管理员查看所有用户

```bash
curl -H "Authorization: Bearer <admin_secret>" \
  https://upgraded-octo-fortnight.vercel.app/api/auth/users
```

---

## 🚨 错误处理

### 常见错误码

| 状态码 | 说明 | 解决方案 |
|--------|------|----------|
| `401` | 未认证或Token无效 | 检查API Key是否正确 |
| `403` | 权限不足 | 检查用户是否被禁用 |
| `429` | 速率限制 | 等待后重试或联系管理员提高限制 |
| `500` | 服务器错误 | 稍后重试或联系支持 |

### 错误响应格式

```json
{
  "success": false,
  "error": "错误描述",
  "message": "详细错误信息"
}
```

---

## 🔄 迁移指南

### 从无认证迁移到有认证

1. **启用认证**:
   ```
   ENABLE_API_AUTH=true
   ADMIN_SECRET=your-secret-key
   ```

2. **创建用户**:
   ```bash
   curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/user \
     -H "Authorization: Bearer your-admin-secret" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "user1", "rate_limit": 1000}'
   ```

3. **获取API Key**:
   ```bash
   # 登录
   curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"user_id": "user1"}'
   
   # 创建API Key
   curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/api-key \
     -H "Authorization: Bearer <access_token>" \
     -H "Content-Type: application/json" \
     -d '{"name": "production"}'
   ```

4. **更新客户端代码**:
   - 添加Authorization Header
   - 实现错误处理（401, 429）
   - 添加重试逻辑

---

## 📝 完整工作流程

### 1. 管理员创建用户

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/user \
  -H "Authorization: Bearer <admin_secret>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "client-app",
    "rate_limit": 2000
  }'
```

### 2. 用户登录获取Token

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "client-app"}'
```

### 3. 创建API Key（可选，推荐）

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/api-key \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "production-key"}'
```

### 4. 使用API Key调用API

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/search \
  -H "Authorization: Bearer <api_key>" \
  -H "Content-Type: application/json" \
  -d '{"categories": ["tech"], "max_results": 10}'
```

### 5. Token过期时刷新

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

---

## ✅ 总结

- ✅ **HTTPS加密**: Vercel自动提供
- ✅ **API Key认证**: 长期有效的密钥
- ✅ **Token认证**: 短期访问令牌
- ✅ **速率限制**: 防止滥用
- ✅ **用户管理**: 指定授权用户
- ✅ **Token刷新**: 自动续期机制

现在你的API已经具备完整的安全保护！

