# API商业模式和用户管理指南

## 💰 商业模式概述

本文档说明如何将API转换为可盈利的服务，包括用户注册、计划管理和计费系统。

---

## 🎯 快速确认：环境变量设置

### 在Vercel Dashboard设置

**必需的环境变量**:

```
ENABLE_API_AUTH=true
ADMIN_SECRET=your-secret-admin-key-here
```

**可选的环境变量**（用于注册保护）:

```
REGISTRATION_SECRET=optional-secret-to-protect-registration
```

---

## 👥 用户接入流程

### 方式1: 用户自助注册（推荐）

#### 步骤1: 用户注册

用户通过注册端点自助注册：

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "plan": "free"
  }'
```

**响应**:
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
    "expires_in": 3600
  },
  "next_step": "create_api_key"
}
```

#### 步骤2: 用户创建API Key

使用返回的Access Token创建API Key：

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/api-key \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-project-key"}'
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

#### 步骤3: 用户使用API Key

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/search \
  -H "Authorization: Bearer <api_key>" \
  -H "Content-Type: application/json" \
  -d '{"categories": ["tech"], "max_results": 10}'
```

### 方式2: 管理员手动创建（当前方式）

如果不想开放公开注册，管理员可以手动创建用户：

```bash
# 管理员创建用户
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/user \
  -H "Authorization: Bearer <admin_secret>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user@example.com",
    "rate_limit": 1000
  }'
```

然后用户使用分配的user_id登录获取Token。

---

## 💼 商业模式实现

### 方案1: 免费+付费计划（推荐）

#### 计划配置

| 计划 | 速率限制 | 价格 | 适用场景 |
|------|----------|------|----------|
| **Free** | 100 请求/小时 | 免费 | 个人项目、测试 |
| **Basic** | 1,000 请求/小时 | $9/月 | 小型应用 |
| **Premium** | 10,000 请求/小时 | $29/月 | 企业应用 |

#### 实现步骤

**1. 用户注册时选择计划**

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "plan": "basic"
  }'
```

**2. 升级计划（管理员操作）**

```bash
# 管理员升级用户计划
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/user \
  -H "Authorization: Bearer <admin_secret>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user@example.com",
    "rate_limit": 10000,
    "plan": "premium"
  }'
```

### 方案2: 使用量计费

#### 实现使用量追踪

修改 `api/search.py` 添加使用量追踪：

```python
from src.auth.usage_tracker import UsageTracker

usage_tracker = UsageTracker()

# 在请求处理中添加
if authenticated:
    user_id = user_info['user_id']
    usage_tracker.track_request(user_id, "search")
```

#### 计费端点

创建 `api/billing.py`:

```python
def get_billing_info(user_id):
    """获取账单信息"""
    usage = usage_tracker.get_usage(user_id)
    user_info = token_manager.get_user_info(user_id)
    plan = user_info.get('plan', 'free')
    
    # 计算费用
    pricing = {
        'free': 0,
        'basic': 0.001,    # $0.001 per request
        'premium': 0.0005  # $0.0005 per request
    }
    
    cost = usage['requests'] * pricing.get(plan, 0)
    
    return {
        'user_id': user_id,
        'plan': plan,
        'usage': usage,
        'cost': cost,
        'billing_period': 'current_month'
    }
```

### 方案3: 订阅制 + API Key购买

#### 集成支付系统（Stripe示例）

**1. 设置Stripe环境变量**

```
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
```

**2. 创建购买端点**

```python
# api/purchase.py
import stripe

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def purchase_api_key(email, plan, payment_token):
    """处理API Key购买"""
    plan_prices = {
        'basic': 900,    # $9.00
        'premium': 2900 # $29.00
    }
    
    # 验证支付
    try:
        charge = stripe.Charge.create(
            amount=plan_prices[plan],
            currency='usd',
            source=payment_token,
            description=f'API Key - {plan} plan'
        )
    except stripe.error.StripeError as e:
        return {'success': False, 'error': str(e)}
    
    # 创建或升级用户
    user_id = email.lower()
    if user_id not in token_manager.tokens_data['users']:
        register_user(user_id, plan)
    else:
        upgrade_user(user_id, plan)
    
    # 生成API Key
    tokens = token_manager.generate_access_token(user_id)
    api_key_result = create_api_key_with_token(tokens['access_token'])
    
    return {
        'success': True,
        'api_key': api_key_result['api_key'],
        'plan': plan,
        'charge_id': charge.id
    }
```

---

## 🌐 用户申请页面

### 简单HTML注册页面

创建 `public/register.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>申请API Key - Global News Aggregator API</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; }
        form { display: flex; flex-direction: column; gap: 15px; }
        input, select { padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        button { padding: 12px; background: #0070f3; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0051cc; }
        .result { margin-top: 20px; padding: 15px; border-radius: 4px; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; border: 1px solid #f5c6cb; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>🔑 申请API Key</h1>
    <p>注册账户并获取API Key以使用Global News Aggregator API</p>
    
    <form id="registerForm">
        <label>邮箱地址 *</label>
        <input type="email" id="email" required placeholder="your@email.com">
        
        <label>姓名</label>
        <input type="text" id="name" placeholder="Your Name">
        
        <label>选择计划</label>
        <select id="plan">
            <option value="free">免费计划 - 100请求/小时</option>
            <option value="basic">基础计划 - 1,000请求/小时 ($9/月)</option>
            <option value="premium">高级计划 - 10,000请求/小时 ($29/月)</option>
        </select>
        
        <button type="submit">申请API Key</button>
    </form>
    
    <div id="result"></div>
    
    <script>
        const API_BASE = 'https://upgraded-octo-fortnight.vercel.app';
        
        document.getElementById('registerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const name = document.getElementById('name').value;
            const plan = document.getElementById('plan').value;
            const resultDiv = document.getElementById('result');
            
            resultDiv.innerHTML = '<p>正在处理...</p>';
            
            try {
                // 步骤1: 注册用户
                const registerResponse = await fetch(`${API_BASE}/api/register`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email, name, plan})
                });
                
                const registerData = await registerResponse.json();
                
                if (!registerData.success) {
                    throw new Error(registerData.error || '注册失败');
                }
                
                // 步骤2: 创建API Key
                const keyResponse = await fetch(`${API_BASE}/api/auth/api-key`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${registerData.tokens.access_token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({name: 'default'})
                });
                
                const keyData = await keyResponse.json();
                
                if (keyData.success) {
                    resultDiv.className = 'result success';
                    resultDiv.innerHTML = `
                        <h2>✅ 注册成功！</h2>
                        <p><strong>您的API Key:</strong></p>
                        <p><code style="font-size: 14px; word-break: break-all;">${keyData.api_key}</code></p>
                        <p><strong>⚠️ 请妥善保存此密钥，它不会再次显示！</strong></p>
                        <hr>
                        <p><strong>使用示例:</strong></p>
                        <pre style="background: #f4f4f4; padding: 10px; border-radius: 4px; overflow-x: auto;">
curl -X POST ${API_BASE}/api/search \\
  -H "Authorization: Bearer ${keyData.api_key}" \\
  -H "Content-Type: application/json" \\
  -d '{"categories": ["tech"], "max_results": 10}'
                        </pre>
                    `;
                } else {
                    throw new Error(keyData.error || '创建API Key失败');
                }
            } catch (error) {
                resultDiv.className = 'result error';
                resultDiv.innerHTML = `<p><strong>错误:</strong> ${error.message}</p>`;
            }
        });
    </script>
</body>
</html>
```

---

## 📊 用户管理

### 查看所有用户

```bash
curl -H "Authorization: Bearer <admin_secret>" \
  https://upgraded-octo-fortnight.vercel.app/api/auth/users
```

### 升级用户计划

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/auth/user \
  -H "Authorization: Bearer <admin_secret>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user@example.com",
    "rate_limit": 10000,
    "plan": "premium"
  }'
```

### 禁用用户

修改 `api/auth.py` 添加禁用端点，或直接修改tokens.json文件。

---

## 💡 变现建议

### 1. 免费计划吸引用户
- ✅ 100请求/小时足够测试
- ✅ 展示完整功能
- ✅ 收集用户邮箱用于营销

### 2. 分层定价策略
- ✅ Basic: $9/月 - 个人开发者
- ✅ Premium: $29/月 - 企业用户
- ✅ 年付折扣（如年付打8折）

### 3. 使用量监控
- ✅ 显示使用统计
- ✅ 超出限制时提示升级
- ✅ 发送使用报告邮件

### 4. 客户支持
- ✅ 免费计划: 社区支持（GitHub Issues）
- ✅ 付费计划: 优先邮件支持
- ✅ Premium: 专属支持渠道

### 5. 营销策略
- ✅ 免费计划用户升级优惠
- ✅ 推荐奖励（推荐新用户获得奖励）
- ✅ 企业定制方案

---

## 🔒 安全建议

1. **邮箱验证**: 发送验证邮件确认邮箱所有权
2. **防止滥用**: 
   - 使用 `REGISTRATION_SECRET` 限制注册
   - 添加CAPTCHA验证
   - IP限制
3. **监控使用**: 追踪异常使用模式
4. **定期审计**: 检查用户使用情况

---

## 📝 完整工作流程总结

### 对于API提供者

1. ✅ **设置环境变量**（Vercel Dashboard）
   ```
   ENABLE_API_AUTH=true
   ADMIN_SECRET=your-secret-admin-key-here
   ```

2. ✅ **部署注册端点**（已创建 `api/register.py`）

3. ✅ **管理用户**
   - 查看用户: `GET /api/auth/users`
   - 升级计划: 修改用户rate_limit
   - 监控使用: 查看速率限制信息

### 对于普通用户

1. ✅ **注册账户**
   ```bash
   curl -X POST https://upgraded-octo-fortnight.vercel.app/api/register \
     -d '{"email": "user@example.com", "plan": "free"}'
   ```

2. ✅ **获取API Key**
   - 使用返回的Access Token创建API Key
   - 或访问注册页面自动完成

3. ✅ **使用API Key**
   ```bash
   curl -X POST https://upgraded-octo-fortnight.vercel.app/api/search \
     -H "Authorization: Bearer <api_key>" \
     -d '{"categories": ["tech"]}'
   ```

---

## 🎯 下一步行动

1. ✅ **已实现**: 用户注册端点 (`/api/register`)
2. ⏳ **可选**: 集成支付系统（Stripe/PayPal）
3. ⏳ **可选**: 创建用户仪表板
4. ⏳ **可选**: 实现使用量追踪和计费
5. ⏳ **可选**: 设置客户支持系统

---

## 📞 支持

- 查看 [API安全指南](./API_SECURITY_GUIDE.md)
- 查看 [用户注册指南](./USER_REGISTRATION_GUIDE.md)
- 访问 [GitHub仓库](https://github.com/clkhoo5211/upgraded-octo-fortnight)

