# 🚀 Vercel部署方案 (无需GitHub Secrets)

## 📋 现状说明

你遇到了Vercel CLI认证错误，提示需要运行`vercel login`。这是因为工作流需要GitHub Secrets配置，但你想避免设置这些敏感信息。

## ✅ 解决方案 (3种方法)

### 方法一：Vercel Dashboard导入 (推荐 ⭐)

**最简单，3分钟完成，无需GitHub配置**

1. **访问Vercel Dashboard**
   - 打开 https://vercel.com/dashboard
   - 使用你的账号登录

2. **导入GitHub仓库**
   - 点击 "Add New..." → "Project"
   - 选择 "Import Git Repository"
   - 找到你的仓库：`upgraded-octo-fortnight`
   - 点击 "Import"

3. **配置项目** (关键步骤)
   | 设置项 | 配置值 |
   |--------|--------|
   | Framework Preset | `Other` |
   | Root Directory | `./` (默认) |
   | Build Command | 留空 |
   | Output Directory | 留空 |
   | Install Command | `pip install -r requirements.txt` |

4. **添加环境变量**
   - 在 "Environment Variables" 部分
   - **Name**: `NEWSAPI_KEY`
   - **Value**: 你的NewsAPI密钥 (从 https://newsapi.org 获取)

5. **部署**
   - 点击 "Deploy" 按钮
   - 等待1-2分钟完成部署
   - 获得访问URL

### 方法二：GitHub Actions手动触发 (无Secrets)

我为你创建了新的工作流文件：
- ✅ `.github/workflows/vercel-simple-deploy.yml` - 简化版，手动触发
- ✅ `.github/workflows/vercel-deploy-no-secrets.yml` - 使用Deploy Hook

**手动触发方式：**
1. 访问你的GitHub仓库
2. 进入 "Actions" 标签
3. 选择 "Vercel 部署 (简化版)"
4. 点击 "Run workflow"
5. 输入部署信息并运行

### 方法三：本地命令行部署

如果你更喜欢本地操作：

```bash
# 1. 安装Vercel CLI
npm install -g vercel

# 2. 登录Vercel
vercel login

# 3. 进入项目目录并部署
cd /path/to/global-news-mcp
vercel --prod
```

## 🔄 自动化部署选项

如果想要推送代码自动部署，需要在GitHub仓库设置中添加3个Secrets：

| Secret名称 | 获取方式 |
|------------|----------|
| `VERCEL_TOKEN` | Vercel Account Settings → Tokens |
| `VERCEL_ORG_ID` | Vercel项目Settings → General |
| `VERCEL_PROJECT_ID` | Vercel项目Settings → General |

**设置步骤：**
1. GitHub仓库 → Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. 添加上述3个Secrets

## 📱 部署后测试

任何方式部署成功后，测试这些API端点：

- 🏥 **健康检查**：`https://your-project.vercel.app/api/health`
- 📰 **获取新闻**：`https://your-project.vercel.app/api/news?query=AI&language=zh`
- 🔥 **热门新闻**：`https://your-project.vercel.app/api/trending`
- 📋 **新闻源**：`https://your-project.vercel.app/api/sources`

## 💡 推荐流程

1. **首次部署**：使用方法一 (Dashboard导入)
2. **日常开发**：推送代码自动部署 (需要配置Secrets)
3. **紧急部署**：使用方法二 (手动触发)

## ⚠️ 注意事项

- 方法一最稳定，适合初次部署
- 配置环境变量 `NEWSAPI_KEY` 是必需的
- 如果遇到权限问题，确保Vercel账户有GitHub访问权限

**推荐从方法一开始！**