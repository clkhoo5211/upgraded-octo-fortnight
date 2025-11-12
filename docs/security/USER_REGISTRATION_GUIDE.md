# 用户注册和API Key申请指南

## 📋 概述

本文档说明普通用户如何申请API Key，以及API提供者如何管理用户和实现商业模式。

---

## 🔐 Vercel环境变量设置（API提供者）

### 必需的环境变量

在Vercel Dashboard设置以下环境变量：

```
ENABLE_API_AUTH=true
ADMIN_SECRET=your-secret-admin-key-here
```

**重要提示**:
- `ADMIN_SECRET` 应该是强密码（至少32个字符）
- 不要将 `ADMIN_SECRET` 提交到代码仓库
- 定期轮换 `ADMIN_SECRET`

---

## 👤 用户申请API Key流程

### 方式1: 用户直接联系管理员（当前方式）

**步骤1: 用户联系API提供者**

用户通过以下方式联系：
- GitHub Issues
- 电子邮件
- 其他联系方式

**步骤2: 管理员创建用户**

管理员使用Admin Secret创建用户：

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/user \
  -H "Authorization: Bearer <admin_secret>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-email-or-username",
    "rate_limit": 1000
  }'
```

**步骤3: 用户登录获取Token**

用户使用分配的user_id登录：

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-email-or-username"}'
```

**步骤4: 用户创建API Key**

使用返回的Access Token创建API Key：

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/api-key \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-project-key"}'
```

### 方式2: 自动化用户注册系统（推荐用于商业模式）

#### 实现用户注册端点

创建一个公开的注册端点，允许用户自助注册：

```python
# api/register.py
"""
用户注册API端点
"""
import os
import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.auth.token_manager import TokenManager
from src.auth.rate_limiter import RateLimiter

token_manager = TokenManager()
rate_limiter = RateLimiter()

# 注册验证密钥（用于防止滥用）
REGISTRATION_SECRET = os.getenv('REGISTRATION_SECRET', '')

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
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
            
            # 验证注册密钥（可选，用于防止滥用）
            if REGISTRATION_SECRET:
                provided_secret = data.get('registration_secret')
                if provided_secret != REGISTRATION_SECRET:
                    self._send_error(403, 'Invalid registration secret')
                    return
            
            # 获取用户信息
            email = data.get('email')
            name = data.get('name', '')
            plan = data.get('plan', 'free')  # free, basic, premium
            
            if not email:
                self._send_error(400, 'Email is required')
                return
            
            # 检查用户是否已存在
            user_id = email.lower().strip()
            existing_user = token_manager.get_user_info(user_id)
            
            if existing_user:
                # 用户已存在，返回现有用户信息
                self._send_json(200, {
                    'success': True,
                    'message': 'User already exists',
                    'user_id': user_id,
                    'next_step': 'login'
                })
                return
            
            # 根据计划设置速率限制
            rate_limits = {
                'free': 100,      # 免费计划：100请求/小时
                'basic': 1000,    # 基础计划：1000请求/小时
                'premium': 10000  # 高级计划：10000请求/小时
            }
            rate_limit = rate_limits.get(plan, 100)
            
            # 创建用户
            if user_id not in token_manager.tokens_data['users']:
                token_manager.tokens_data['users'][user_id] = {
                    'created_at': __import__('datetime').datetime.now().isoformat(),
                    'api_keys': [],
                    'rate_limit': rate_limit,
                    'enabled': True,
                    'plan': plan,
                    'name': name,
                    'email': email
                }
                token_manager._save_tokens()
            
            rate_limiter.set_rate_limit(user_id, rate_limit)
            
            # 自动登录并返回Token
            tokens = token_manager.generate_access_token(user_id)
            
            self._send_json(201, {
                'success': True,
                'message': 'User registered successfully',
                'user_id': user_id,
                'plan': plan,
                'rate_limit': rate_limit,
                'tokens': tokens,
                'next_step': 'create_api_key'
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
```

#### 添加注册路由

在 `vercel.json` 中添加：

```json
{
  "routes": [
    {
      "src": "/api/register",
      "dest": "/api/register.py"
    }
  ]
}
```

---

## 💰 商业模式实现

### 方案1: 免费+付费计划

#### 计划层级

| 计划 | 速率限制 | 价格 | 特性 |
|------|----------|------|------|
| **Free** | 100 请求/小时 | 免费 | 基础功能 |
| **Basic** | 1,000 请求/小时 | $9/月 | 所有功能 |
| **Premium** | 10,000 请求/小时 | $29/月 | 所有功能 + 优先支持 |

#### 实现步骤

**1. 创建注册端点**（见上方代码）

**2. 用户注册流程**

```bash
# 用户注册
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "plan": "free"
  }'
```

**3. 升级计划**

创建升级端点：

```python
# api/upgrade.py
def upgrade_user(user_id, new_plan):
    """升级用户计划"""
    rate_limits = {
        'free': 100,
        'basic': 1000,
        'premium': 10000
    }
    
    if user_id in token_manager.tokens_data['users']:
        token_manager.tokens_data['users'][user_id]['plan'] = new_plan
        token_manager.tokens_data['users'][user_id]['rate_limit'] = rate_limits[new_plan]
        token_manager._save_tokens()
        rate_limiter.set_rate_limit(user_id, rate_limits[new_plan])
        return True
    return False
```

### 方案2: API Key购买系统

#### 实现购买流程

**1. 创建购买端点**

```python
# api/purchase.py
"""
API Key购买端点
集成支付系统（如Stripe、PayPal）
"""
def purchase_api_key(email, plan, payment_token):
    """处理API Key购买"""
    # 1. 验证支付
    payment_result = verify_payment(payment_token, plan)
    
    if not payment_result['success']:
        return {'success': False, 'error': 'Payment failed'}
    
    # 2. 创建或升级用户
    user_id = email.lower()
    if user_id not in token_manager.tokens_data['users']:
        # 注册新用户
        register_user(user_id, plan)
    else:
        # 升级现有用户
        upgrade_user(user_id, plan)
    
    # 3. 生成API Key
    tokens = token_manager.generate_access_token(user_id)
    api_key_result = create_api_key_with_token(tokens['access_token'])
    
    return {
        'success': True,
        'api_key': api_key_result['api_key'],
        'plan': plan,
        'expires_at': calculate_expiry(plan)
    }
```

**2. 集成支付系统**

使用Stripe示例：

```python
import stripe

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def verify_payment(payment_token, plan):
    """验证Stripe支付"""
    try:
        charge = stripe.Charge.create(
            amount=plan_prices[plan] * 100,  # 转换为分
            currency='usd',
            source=payment_token,
            description=f'API Key - {plan} plan'
        )
        return {'success': True, 'charge_id': charge.id}
    except stripe.error.StripeError as e:
        return {'success': False, 'error': str(e)}
```

### 方案3: 使用量计费

#### 实现使用量追踪

```python
# src/auth/usage_tracker.py
"""
使用量追踪模块
"""
class UsageTracker:
    def __init__(self):
        self.usage_data = {}
    
    def track_request(self, user_id, endpoint):
        """追踪API请求"""
        today = datetime.now().strftime('%Y-%m-%d')
        key = f"{user_id}:{today}"
        
        if key not in self.usage_data:
            self.usage_data[key] = {
                'requests': 0,
                'endpoints': {}
            }
        
        self.usage_data[key]['requests'] += 1
        self.usage_data[key]['endpoints'][endpoint] = \
            self.usage_data[key]['endpoints'].get(endpoint, 0) + 1
    
    def get_usage(self, user_id, date=None):
        """获取使用量"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        key = f"{user_id}:{date}"
        return self.usage_data.get(key, {'requests': 0, 'endpoints': {}})
```

#### 计费端点

```python
# api/billing.py
def get_billing_info(user_id):
    """获取账单信息"""
    usage = usage_tracker.get_usage(user_id)
    user_info = token_manager.get_user_info(user_id)
    plan = user_info.get('plan', 'free')
    
    # 计算费用
    if plan == 'free':
        cost = 0
    elif plan == 'basic':
        cost = usage['requests'] * 0.001  # $0.001 per request
    else:
        cost = usage['requests'] * 0.0005  # $0.0005 per request
    
    return {
        'user_id': user_id,
        'plan': plan,
        'usage': usage,
        'cost': cost,
        'billing_period': 'current_month'
    }
```

---

## 🌐 用户申请页面示例

### HTML注册表单

```html
<!DOCTYPE html>
<html>
<head>
    <title>申请API Key</title>
</head>
<body>
    <h1>申请API Key</h1>
    <form id="registerForm">
        <label>邮箱:</label>
        <input type="email" id="email" required>
        
        <label>姓名:</label>
        <input type="text" id="name">
        
        <label>计划:</label>
        <select id="plan">
            <option value="free">免费计划 (100请求/小时)</option>
            <option value="basic">基础计划 (1,000请求/小时) - $9/月</option>
            <option value="premium">高级计划 (10,000请求/小时) - $29/月</option>
        </select>
        
        <button type="submit">申请API Key</button>
    </form>
    
    <div id="result"></div>
    
    <script>
        document.getElementById('registerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const name = document.getElementById('name').value;
            const plan = document.getElementById('plan').value;
            
            try {
                const response = await fetch('https://upgraded-octo-fortnight.vercel.app/api/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email, name, plan})
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // 创建API Key
                    const keyResponse = await fetch('https://upgraded-octo-fortnight.vercel.app/api/auth/api-key', {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${data.tokens.access_token}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({name: 'default'})
                    });
                    
                    const keyData = await keyResponse.json();
                    
                    document.getElementById('result').innerHTML = `
                        <h2>注册成功！</h2>
                        <p>您的API Key:</p>
                        <code>${keyData.api_key}</code>
                        <p><strong>请妥善保存，此密钥不会再次显示！</strong></p>
                    `;
                } else {
                    document.getElementById('result').innerHTML = `<p>错误: ${data.error}</p>`;
                }
            } catch (error) {
                document.getElementById('result').innerHTML = `<p>错误: ${error.message}</p>`;
            }
        });
    </script>
</body>
</html>
```

---

## 📝 完整工作流程

### 对于API提供者

1. **设置环境变量**
   ```
   ENABLE_API_AUTH=true
   ADMIN_SECRET=your-secret-admin-key-here
   REGISTRATION_SECRET=optional-registration-secret
   ```

2. **部署注册端点**（如果使用自动化注册）

3. **管理用户**
   - 查看所有用户: `GET /api/auth/users`
   - 升级用户计划: 使用升级端点
   - 禁用用户: 使用管理员端点

### 对于普通用户

1. **注册账户**
   ```bash
   curl -X POST https://upgraded-octo-fortnight.vercel.app/api/register \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "plan": "free"}'
   ```

2. **获取API Key**
   - 使用返回的Access Token创建API Key
   - 或登录后创建

3. **使用API Key**
   ```bash
   curl -X POST https://upgraded-octo-fortnight.vercel.app/api/search \
     -H "Authorization: Bearer <api_key>" \
     -H "Content-Type: application/json" \
     -d '{"categories": ["tech"], "max_results": 10}'
   ```

---

## 💡 商业模式建议

### 1. 免费计划吸引用户
- 100请求/小时足够测试和开发
- 展示完整功能，吸引升级

### 2. 分层定价
- Basic: $9/月 - 适合个人开发者
- Premium: $29/月 - 适合企业用户

### 3. 使用量追踪
- 显示使用统计
- 超出限制时提示升级

### 4. 客户支持
- 免费计划: 社区支持
- 付费计划: 优先邮件支持

---

## 🔒 安全建议

1. **验证邮箱**: 发送验证邮件确认邮箱所有权
2. **防止滥用**: 使用CAPTCHA或注册密钥
3. **监控使用**: 追踪异常使用模式
4. **定期审计**: 检查用户使用情况

---

## 📞 下一步

1. 实现注册端点（如果需要自动化）
2. 集成支付系统（如果需要付费）
3. 创建用户仪表板（查看使用量、账单）
4. 设置客户支持系统

