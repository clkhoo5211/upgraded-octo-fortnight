# Vercel 快速部署指南

本项目已配置好 GitHub Actions 自动部署工作流，可以实现代码推送后自动部署到 Vercel。

## 方式一：通过 Vercel Dashboard 导入（推荐，最简单）

### 1. 导入 GitHub 仓库
1. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
2. 点击 "Add New..." → "Project"
3. 选择 "Import Git Repository"
4. 找到 `upgraded-octo-fortnight` 仓库并点击 "Import"

### 2. 配置项目（关键步骤）

#### 基本设置
- **Framework Preset**: 选择 `Other`
- **Root Directory**: 保持默认 `./`
- **Build Command**: 留空（或填写 `echo "Using API directory"`）
- **Output Directory**: 留空
- **Install Command**: `pip install -r requirements.txt`

#### 环境变量配置
在 "Environment Variables" 部分添加：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `NEWSAPI_KEY` | 你的 NewsAPI 密钥 | 从 https://newsapi.org 获取 |

### 3. 部署
- 点击 "Deploy" 按钮
- 等待部署完成（约 1-2 分钟）
- 获得部署 URL（如：`https://your-project.vercel.app`）

### 4. 测试 API 端点
部署成功后，访问以下端点测试：
- 健康检查：`https://your-project.vercel.app/api/health`
- 获取新闻：`https://your-project.vercel.app/api/news?query=AI&language=zh`

---

## 方式二：使用 GitHub Actions 自动部署（高级）

如果想要每次推送代码自动部署，按以下步骤配置：

### 1. 在 Vercel 获取部署令牌
1. 访问 [Vercel Account Settings](https://vercel.com/account/tokens)
2. 创建一个新的 Token
3. 复制保存（只显示一次）

### 2. 在 Vercel 获取项目 ID
1. 进入你的 Vercel 项目
2. 点击 "Settings" → "General"
3. 找到并复制：
   - `Project ID`
   - `Organization ID`（在项目列表页面的团队/个人账号设置中）

### 3. 在 GitHub 仓库配置 Secrets
1. 打开 GitHub 仓库：https://github.com/clkhoo5211/upgraded-octo-fortnight
2. 进入 "Settings" → "Secrets and variables" → "Actions"
3. 点击 "New repository secret" 添加以下三个密钥：

| Secret 名称 | 值 |
|------------|-----|
| `VERCEL_TOKEN` | 步骤1中获取的 Vercel Token |
| `VERCEL_ORG_ID` | 你的 Organization ID |
| `VERCEL_PROJECT_ID` | 你的 Project ID |

### 4. 触发自动部署
配置完成后，每次推送代码到 `main` 分支，GitHub Actions 会自动：
1. 检出代码
2. 安装依赖
3. 构建项目
4. 部署到 Vercel

可以在仓库的 "Actions" 标签页查看部署状态。

---

## 方式三：使用 Vercel CLI 手动部署

### 1. 安装 Vercel CLI
```bash
npm install -g vercel
```

### 2. 登录
```bash
vercel login
```

### 3. 部署
```bash
cd /path/to/global-news-mcp
vercel --prod
```

---

## 重要提示

### 环境变量配置
部署后，**必须**在 Vercel Dashboard 中配置环境变量：
1. 进入项目 "Settings" → "Environment Variables"
2. 添加 `NEWSAPI_KEY`
3. 点击 "Save"
4. 重新部署项目（如果需要）

### API 端点说明
- `/api/health` - 健康检查
- `/api/news` - 获取新闻（支持参数：query, language, pageSize, page）
- `/api/trending` - 获取热门新闻
- `/api/sources` - 获取新闻源列表

### 故障排查
如果部署失败：
1. 检查 `requirements.txt` 中的依赖版本
2. 确认 `vercel.json` 配置正确
3. 查看 Vercel 部署日志
4. 确认环境变量已正确设置

---

## 推荐配置总结

**最简单方式**：
1. Vercel Dashboard 导入仓库
2. 选择 Framework: `Other`
3. 添加环境变量 `NEWSAPI_KEY`
4. 点击 Deploy

整个过程不超过 3 分钟！
