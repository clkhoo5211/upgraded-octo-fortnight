# API快速开始指南

## 🚀 5分钟快速开始

### 步骤1: 检查API状态

```bash
curl https://upgraded-octo-fortnight.vercel.app/api/health
```

### 步骤2: 获取API Key（如果启用认证）

#### 方式A: 使用已有用户ID

```bash
# 1. 登录获取Token
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "your-user-id"}'

# 2. 创建API Key
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/api-key \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-key"}'
```

#### 方式B: 联系管理员创建用户

联系API管理员创建用户并获取API Key。

### 步骤3: 保存API Key

**GitHub仓库**:
```
Settings → Secrets → Actions → New secret
名称: NEWS_API_KEY
值: ak_xxx...
```

**本地项目**:
创建`.env`文件:
```
NEWS_API_KEY=ak_xxx...
```

### 步骤4: 调用API

**Python**:
```python
import os
import requests

API_KEY = os.getenv('NEWS_API_KEY')
response = requests.post(
    "https://upgraded-octo-fortnight.vercel.app/api/search",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"categories": ["tech"], "max_results": 10}
)
print(response.json())
```

**JavaScript**:
```javascript
const API_KEY = process.env.NEWS_API_KEY;
const response = await fetch(
    'https://upgraded-octo-fortnight.vercel.app/api/search',
    {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${API_KEY}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            categories: ['tech'],
            max_results: 10
        })
    }
);
const data = await response.json();
console.log(data);
```

**curl**:
```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/search \
  -H "Authorization: Bearer $NEWS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"categories": ["tech"], "max_results": 10}'
```

## 📚 更多文档

- [完整API使用指南](./API_USAGE_GUIDE.md)
- [API安全指南](../security/API_SECURITY_GUIDE.md)
- [示例代码](../../examples/)

