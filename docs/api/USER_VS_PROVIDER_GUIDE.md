# 用户和API提供者功能指南

> 区分普通用户和API提供者的完整功能说明

## 👥 角色说明

- **普通用户**: 使用API的开发者/应用
- **API提供者**: 部署和管理API的服务提供者

---

## 👤 普通用户功能

### 1. 用户注册和Token获取

#### 注册账户

```bash
POST /api/register
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "plan": "free"
}
```

**功能**: 自助注册账户，自动获取Access Token和Refresh Token

#### 登录获取Token

```bash
POST /api/auth/login
Content-Type: application/json

{
  "user_id": "user@example.com"
}
```

**功能**: 使用已有账户登录，获取新的Token

#### 创建API Key

```bash
POST /api/auth/api-key
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "my-project-key"
}
```

**功能**: 创建长期有效的API Key（推荐用于生产环境）

### 2. Token管理

#### 检查Token状态

```bash
POST /api/auth/token-status
Content-Type: application/json

{
  "access_token": "at_xxx..."
}
```

**功能**: 检查Token是否过期、剩余时间、计划信息

#### 刷新Token

```bash
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "rt_xxx..."
}
```

**功能**: 使用Refresh Token刷新过期的Access Token（所有计划）

#### 续期Token（仅付费计划）

```bash
POST /api/auth/renew
Authorization: Bearer <expired_access_token>
Content-Type: application/json

{
  "access_token": "at_xxx..."
}
```

**功能**: 续期付费Token，延长有效期（仅Basic和Premium计划）

#### 升级计划

```bash
POST /api/upgrade
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "plan": "premium"
}
```

**功能**: 升级到付费计划，自动获得新的30天Token

### 3. 查看账户信息

#### 获取用户信息

```bash
GET /api/auth/me
Authorization: Bearer <token>
```

**功能**: 查看当前用户信息、计划、速率限制

#### 获取速率限制信息

```bash
GET /api/auth/rate-limit
Authorization: Bearer <token>
```

**功能**: 查看当前速率限制使用情况

### 4. 使用API

#### 搜索新闻

```bash
POST /api/search
Authorization: Bearer <api_key_or_token>
Content-Type: application/json

{
  "categories": ["tech"],
  "max_results": 10
}
```

**功能**: 搜索新闻（需要认证如果启用）

#### 下载内容

```bash
POST /api/download
Authorization: Bearer <api_key_or_token>
Content-Type: application/json

{
  "news_url": "https://example.com/article"
}
```

**功能**: 下载新闻完整内容

#### 完整归档

```bash
POST /api/archive
Authorization: Bearer <api_key_or_token>
Content-Type: application/json

{
  "categories": ["tech"],
  "save_to_github": false
}
```

**功能**: 搜索、下载并归档新闻

---

## 🏢 API提供者功能

### 1. 环境变量配置

在Vercel Dashboard设置：

```
ENABLE_API_AUTH=true
ADMIN_SECRET=your-secret-admin-key-here
REGISTRATION_SECRET=optional-registration-secret
```

**功能**: 
- `ENABLE_API_AUTH`: 启用/禁用API认证
- `ADMIN_SECRET`: 管理员密钥（用于管理操作）
- `REGISTRATION_SECRET`: 注册密钥（可选，用于限制注册）

### 2. 用户管理

#### 创建用户

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

**功能**: 手动创建用户，设置速率限制和计划

#### 列出所有用户

```bash
GET /api/auth/users
Authorization: Bearer <admin_secret>
```

**功能**: 查看所有注册用户、计划、使用情况

#### 列出所有API Keys

```bash
GET /api/auth/api-keys
Authorization: Bearer <admin_secret>
```

**功能**: 查看所有已创建的API Keys

### 3. 用户计划管理

#### 升级用户计划

```bash
POST /api/auth/user
Authorization: Bearer <admin_secret>
Content-Type: application/json

{
  "user_id": "user@example.com",
  "rate_limit": 10000,
  "plan": "premium"
}
```

**功能**: 升级用户计划，自动更新速率限制

#### 禁用用户

修改 `tokens.json` 文件或通过代码：

```python
token_manager.disable_user("user@example.com")
```

**功能**: 禁用用户，阻止其使用API

### 4. 监控和管理

#### 查看用户使用情况

```bash
GET /api/auth/users
Authorization: Bearer <admin_secret>
```

**响应示例**:
```json
{
  "success": true,
  "users": [
    {
      "user_id": "user@example.com",
      "created_at": "2025-11-12T10:00:00",
      "rate_limit": 1000,
      "enabled": true,
      "plan": "basic",
      "api_key_count": 2
    }
  ],
  "total": 1
}
```

#### 查看速率限制使用情况

通过用户信息端点查看每个用户的使用情况。

### 5. 商业模式管理

#### 计划配置

在代码中配置计划：

```python
PLAN_RATE_LIMITS = {
    'free': 100,      # 免费计划
    'basic': 1000,    # 基础计划 $9/月
    'premium': 10000  # 高级计划 $29/月
}
```

#### Token有效期配置

- **免费计划**: Access Token 1小时，Refresh Token 7天
- **付费计划**: Access Token 30天，Refresh Token 90天

#### 付费流程管理

1. **用户注册免费计划**
2. **用户升级到付费计划** (`POST /api/upgrade`)
3. **用户获得30天Token**
4. **Token过期前续期** (`POST /api/auth/renew`)

---

## 📊 功能对比表

### 普通用户可用功能

| 功能 | 端点 | 方法 | 说明 |
|------|------|------|------|
| 注册账户 | `/api/register` | POST | 自助注册 |
| 登录 | `/api/auth/login` | POST | 获取Token |
| 创建API Key | `/api/auth/api-key` | POST | 创建长期密钥 |
| 检查Token状态 | `/api/auth/token-status` | POST/GET | 查看是否过期 |
| 刷新Token | `/api/auth/refresh` | POST | 刷新过期Token |
| 续期Token | `/api/auth/renew` | POST | 续期付费Token |
| 升级计划 | `/api/upgrade` | POST | 升级到付费计划 |
| 查看用户信息 | `/api/auth/me` | GET | 查看账户信息 |
| 查看速率限制 | `/api/auth/rate-limit` | GET | 查看使用情况 |
| 搜索新闻 | `/api/search` | GET/POST | 搜索新闻 |
| 下载内容 | `/api/download` | GET/POST | 下载内容 |
| 归档新闻 | `/api/archive` | POST | 完整归档 |

### API提供者可用功能

| 功能 | 端点 | 方法 | 说明 |
|------|------|------|------|
| 创建用户 | `/api/auth/user` | POST | 手动创建用户 |
| 列出用户 | `/api/auth/users` | GET | 查看所有用户 |
| 列出API Keys | `/api/auth/api-keys` | GET | 查看所有密钥 |
| 升级用户计划 | `/api/auth/user` | POST | 升级用户计划 |
| 禁用用户 | 代码操作 | - | 禁用用户账户 |
| 配置环境变量 | Vercel Dashboard | - | 设置认证和密钥 |

---

## 🔄 Token过期处理流程

### 对于普通用户

#### 免费Token过期

1. **检测过期**: 调用API返回401错误
2. **检查状态**: `POST /api/auth/token-status`
3. **刷新Token**: `POST /api/auth/refresh`（使用Refresh Token）
4. **或重新登录**: `POST /api/auth/login`

#### 付费Token过期

1. **检测过期**: 调用API返回401错误
2. **检查状态**: `POST /api/auth/token-status`
3. **续期Token**: `POST /api/auth/renew`（推荐）
4. **或刷新Token**: `POST /api/auth/refresh`（使用Refresh Token）
5. **或重新登录**: `POST /api/auth/login`

### 对于API提供者

#### 监控Token过期

```python
# 检查所有用户的Token状态
for user_id, user_info in token_manager.tokens_data['users'].items():
    # 检查用户的Token
    for token_hash, token_info in token_manager.tokens_data['access_tokens'].items():
        if token_info['user_id'] == user_id:
            expires_at = datetime.fromisoformat(token_info['expires_at'])
            if datetime.now() > expires_at:
                print(f"User {user_id} token expired")
```

#### 自动续期（可选）

可以创建定时任务自动为付费用户续期Token。

---

## 💡 最佳实践

### 对于普通用户

1. **使用API Key**（推荐）
   - 长期有效，不需要管理Token过期
   - 适合生产环境

2. **如果使用Access Token**
   - 定期检查Token状态
   - Token过期前自动刷新或续期
   - 实现自动重试机制

3. **保存Token安全**
   - 使用环境变量存储
   - 不要提交到代码仓库
   - 定期轮换API Key

### 对于API提供者

1. **环境变量安全**
   - `ADMIN_SECRET` 使用强密码
   - 定期轮换密钥
   - 不要提交到代码仓库

2. **用户管理**
   - 定期审查用户使用情况
   - 监控异常使用模式
   - 及时处理滥用行为

3. **计划管理**
   - 清晰定义计划层级
   - 合理设置速率限制
   - 提供升级路径

---

## 📝 完整工作流程示例

### 普通用户完整流程

```python
# 1. 注册账户
response = requests.post(
    'https://upgraded-octo-fortnight.vercel.app/api/register',
    json={'email': 'user@example.com', 'plan': 'free'}
)
tokens = response.json()['tokens']

# 2. 创建API Key
api_key_response = requests.post(
    'https://upgraded-octo-fortnight.vercel.app/api/auth/api-key',
    headers={'Authorization': f"Bearer {tokens['access_token']}"},
    json={'name': 'production'}
)
api_key = api_key_response.json()['api_key']

# 3. 使用API Key（长期使用）
news = requests.post(
    'https://upgraded-octo-fortnight.vercel.app/api/search',
    headers={'Authorization': f"Bearer {api_key}"},
    json={'categories': ['tech']}
)

# 4. 升级计划（可选）
upgrade_response = requests.post(
    'https://upgraded-octo-fortnight.vercel.app/api/upgrade',
    headers={'Authorization': f"Bearer {tokens['access_token']}"},
    json={'plan': 'premium'}
)
new_tokens = upgrade_response.json()['tokens']

# 5. Token过期处理（如果使用Access Token）
status = requests.post(
    'https://upgraded-octo-fortnight.vercel.app/api/auth/token-status',
    json={'access_token': new_tokens['access_token']}
).json()

if status['status']['expired']:
    if status['status']['can_renew']:
        # 续期
        renew_response = requests.post(
            'https://upgraded-octo-fortnight.vercel.app/api/auth/renew',
            headers={'Authorization': f"Bearer {new_tokens['access_token']}"},
            json={'access_token': new_tokens['access_token']}
        )
    else:
        # 刷新
        refresh_response = requests.post(
            'https://upgraded-octo-fortnight.vercel.app/api/auth/refresh',
            json={'refresh_token': new_tokens['refresh_token']}
        )
```

### API提供者完整流程

```python
# 1. 设置环境变量（Vercel Dashboard）
# ENABLE_API_AUTH=true
# ADMIN_SECRET=your-secret-key

# 2. 创建用户
response = requests.post(
    'https://upgraded-octo-fortnight.vercel.app/api/auth/user',
    headers={'Authorization': f"Bearer {ADMIN_SECRET}"},
    json={'user_id': 'user@example.com', 'rate_limit': 1000, 'plan': 'basic'}
)

# 3. 查看所有用户
users = requests.get(
    'https://upgraded-octo-fortnight.vercel.app/api/auth/users',
    headers={'Authorization': f"Bearer {ADMIN_SECRET}"}
).json()

# 4. 升级用户计划
upgrade = requests.post(
    'https://upgraded-octo-fortnight.vercel.app/api/auth/user',
    headers={'Authorization': f"Bearer {ADMIN_SECRET}"},
    json={'user_id': 'user@example.com', 'rate_limit': 10000, 'plan': 'premium'}
)

# 5. 监控使用情况
for user in users['users']:
    print(f"User: {user['user_id']}, Plan: {user['plan']}, Rate Limit: {user['rate_limit']}")
```

---

## ✅ 总结

### 普通用户

- ✅ 可以自助注册
- ✅ 可以创建API Key
- ✅ 可以升级计划
- ✅ 可以管理Token（刷新、续期）
- ✅ 可以查看使用情况

### API提供者

- ✅ 可以管理用户
- ✅ 可以设置计划
- ✅ 可以监控使用
- ✅ 可以实现商业模式
- ✅ 可以控制访问权限

---

**相关文档**:
- [完整对接指南](./COMPLETE_INTEGRATION_GUIDE.md)
- [API使用指南](./API_USAGE_GUIDE.md)
- [API安全指南](../security/API_SECURITY_GUIDE.md)

