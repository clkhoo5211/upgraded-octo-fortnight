# 文件组织说明

## 目录结构

### 核心功能文件（根目录）
- `api/` - Vercel Serverless Functions（API端点）
- `src/` - 源代码模块
- `vercel.json` - Vercel部署配置（当前使用）
- `requirements.txt` - Python依赖
- `server.py` - MCP服务器主文件
- `main.py` - 主入口文件
- `run.sh` - 启动脚本

### 测试文件
- `tests/` - 所有测试文件
  - `tests/auth/` - 认证测试
  - `tests/api/` - API端点测试
  - `tests/integration/` - 集成测试
  - `tests/unit/` - 单元测试
  - `tests/config/` - 测试配置

### 文档文件
- `docs/` - 所有文档
  - `docs/api/` - API文档
  - `docs/security/` - 安全文档
  - `docs/deployment/` - 部署文档
  - `docs/testing/` - 测试文档
  - `docs/troubleshooting/` - 故障排查文档
  - `docs/legacy/` - 历史配置文件

### 脚本文件
- `scripts/deployment/` - 部署脚本

### 示例文件
- `examples/` - 代码示例

### 归档文件
- `YYYY/MM/DD/` - 归档的新闻文件（按日期分类）

## 已移动的文件

以下文件已从根目录移动到相应目录：

### 测试文件
- `diagnose_vercel.py` → `tests/diagnose_vercel.py`
- `api/test.py` → `tests/integration/test.py`
- `api/simple_test.py` → `tests/integration/simple_test.py`
- `api/test_handler.py` → `tests/integration/test_handler.py`

### 文档文件
- `API_KEYS_REQUIRED.txt` → 内容已整合到 `docs/deployment/API_KEYS_SETUP.md`

### 脚本文件
- `vercel-deploy.sh` → `scripts/deployment/vercel-deploy.sh`

### 历史配置文件
- `vercel-backup-*.json` → `docs/legacy/`
- `vercel-fixed.json` → `docs/legacy/`
- `vercel-original.json` → `docs/legacy/`

## 保留在根目录的文件

以下文件保留在根目录，因为它们是项目运行所必需的：

- `vercel.json` - 当前Vercel配置
- `mcp-server.json` - MCP服务器配置
- `railway.json` - Railway部署配置（可选）
- `render.yaml` - Render部署配置（可选）
- `fly.toml` - Fly.io部署配置（可选）
- `requirements.txt` - Python依赖
- `requirements.min.txt` - 最小依赖
- `server.py` - MCP服务器
- `main.py` - 主入口
- `run.sh` - 启动脚本
- `README.md` - 项目说明

