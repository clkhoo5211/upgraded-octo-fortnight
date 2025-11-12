# GitHub Actions Workflows 说明

## 📋 可用的Workflows

### 1. test.yml - 测试和验证（推荐）
**触发条件：** 每次push和PR
**功能：** 
- 测试Python模块导入
- 验证API端点语法
- 不依赖外部服务

**状态：** ✅ 无需配置即可运行

### 2. vercel-deploy.yml - Vercel部署
**触发条件：** push到main分支
**功能：** 自动部署到Vercel

**需要配置：**
- `VERCEL_TOKEN` - Vercel访问令牌
- `VERCEL_ORG_ID` - Vercel组织ID（可选）
- `VERCEL_PROJECT_ID` - Vercel项目ID（可选）

**如何获取Vercel Token：**
1. 访问：https://vercel.com/account/tokens
2. 创建新的Token
3. 复制Token值
4. 在GitHub仓库中添加Secret：
   - Settings → Secrets and variables → Actions
   - New repository secret
   - Name: `VERCEL_TOKEN`
   - Value: 你的Token

**注意：** 如果没有配置Token，workflow会跳过部署步骤，不会失败

### 3. deploy-python-app.yml - 多平台部署
**触发条件：** 手动触发或特定commit消息
**功能：** 支持部署到多个平台（Render, Railway, Fly.io等）

## 🔧 配置说明

### 必需配置（用于Vercel自动部署）

在GitHub仓库的Settings → Secrets and variables → Actions中添加：

1. **VERCEL_TOKEN**
   - 获取方式：https://vercel.com/account/tokens
   - 用途：Vercel CLI认证

2. **VERCEL_ORG_ID**（可选）
   - 获取方式：Vercel Dashboard → Settings → General
   - 用途：指定组织

3. **VERCEL_PROJECT_ID**（可选）
   - 获取方式：Vercel Dashboard → Project Settings → General
   - 用途：指定项目

### 可选配置（用于其他平台）

- `RENDER_DEPLOY_HOOK_URL` - Render部署钩子
- `RAILWAY_TOKEN` - Railway访问令牌
- `FLY_API_TOKEN` - Fly.io访问令牌
- `DOCKER_USERNAME` / `DOCKER_PASSWORD` - Docker Hub凭证

## ✅ 推荐设置

**最小配置（只运行测试）：**
- 无需任何配置
- test.yml会自动运行

**完整配置（自动部署到Vercel）：**
- 添加 `VERCEL_TOKEN` Secret
- vercel-deploy.yml会自动运行

## 🚀 使用建议

1. **首次使用：** 先运行test.yml确保代码正常
2. **配置Vercel：** 添加VERCEL_TOKEN后启用自动部署
3. **监控部署：** 在GitHub Actions页面查看运行状态

## 📝 注意事项

- Vercel部署workflow在没有Token时会跳过，不会失败
- 测试workflow不依赖外部服务，总是可以运行
- 所有workflow都支持手动触发（workflow_dispatch）

