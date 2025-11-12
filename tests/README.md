# 测试文件说明

## 📁 目录结构

```
tests/
├── config/              # 测试配置
│   ├── __init__.py     # 配置模块（从环境变量读取）
│   └── .env.test.example  # 环境变量示例文件
├── auth/                # 认证相关测试
│   └── test_token_expiry.py
├── api/                 # API端点测试
│   ├── test_news_search.py
│   └── test_manual_archive.py
├── integration/         # 集成测试
│   ├── test_all_plans.py
│   ├── test_api_scenarios.py
│   ├── test_api_complete.py
│   ├── test_vercel_api.py
│   └── test_with_mcp.py
├── unit/                # 单元测试
│   └── test_features.py
└── README.md           # 本文件
```

## 🔐 安全配置

### 重要：敏感信息保护

**所有敏感密钥（ADMIN_SECRET, REGISTRATION_SECRET）必须从环境变量读取，不能硬编码在代码中！**

### 设置测试环境变量

#### 方式1: 使用环境变量（推荐）

```bash
export ADMIN_SECRET='your-admin-secret'
export REGISTRATION_SECRET='your-registration-secret'
export TEST_API_BASE='https://upgraded-octo-fortnight.vercel.app'
```

#### 方式2: 使用 .env.test 文件

1. 复制示例文件：
```bash
cp tests/config/.env.test.example tests/config/.env.test
```

2. 编辑 `tests/config/.env.test` 填入实际值

3. 在测试脚本中加载（如果使用python-dotenv）：
```python
from dotenv import load_dotenv
load_dotenv('tests/config/.env.test')
```

### .gitignore 保护

以下文件已在 `.gitignore` 中，不会被提交到仓库：
- `tests/config/.env.test` - 实际环境变量文件
- `**/.env*` - 所有环境变量文件（除了 `.env.example`）

## 🧪 运行测试

### 运行所有测试

```bash
# 设置环境变量
export ADMIN_SECRET='your-secret'
export REGISTRATION_SECRET='your-secret'

# 运行测试
python3 tests/integration/test_all_plans.py
python3 tests/auth/test_token_expiry.py
```

### 运行特定测试

```bash
# 认证测试
python3 tests/auth/test_token_expiry.py

# API测试
python3 tests/api/test_news_search.py

# 集成测试
python3 tests/integration/test_all_plans.py
```

## 📝 测试文件说明

### 认证测试 (`tests/auth/`)
- `test_token_expiry.py` - 测试Token过期和刷新场景

### API测试 (`tests/api/`)
- `test_news_search.py` - 测试新闻搜索功能
- `test_manual_archive.py` - 测试手动归档功能

### 集成测试 (`tests/integration/`)
- `test_all_plans.py` - 测试所有用户计划（Free/Basic/Premium）
- `test_api_scenarios.py` - 测试各种API场景
- `test_api_complete.py` - 完整API测试
- `test_vercel_api.py` - Vercel部署测试
- `test_with_mcp.py` - MCP集成测试

### 单元测试 (`tests/unit/`)
- `test_features.py` - 功能单元测试

## ⚠️ 注意事项

1. **不要提交敏感信息**：确保 `.env.test` 文件不会被提交
2. **使用环境变量**：所有密钥必须从环境变量读取
3. **测试前验证配置**：测试脚本会自动验证必需的环境变量
4. **CI/CD配置**：在CI/CD中使用密钥管理服务（如GitHub Secrets）

## 🔄 迁移说明

如果你有旧的测试文件，请：

1. 更新导入路径：
```python
# 旧代码
API_BASE = "https://..."
ADMIN_SECRET = "hardcoded-secret"

# 新代码
from tests.config import API_BASE, ADMIN_SECRET, validate_test_config
validate_test_config()
```

2. 设置环境变量：
```bash
export ADMIN_SECRET='your-secret'
export REGISTRATION_SECRET='your-secret'
```

3. 运行测试验证

