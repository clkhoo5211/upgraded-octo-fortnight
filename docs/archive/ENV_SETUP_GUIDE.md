# 环境变量配置指南

## 📍 配置位置：Vercel Dashboard

所有运行时环境变量都应该在 **Vercel Dashboard** 中配置，而不是 GitHub。

## 🔧 配置步骤

### 1. 访问 Vercel Dashboard
- 打开：https://vercel.com/dashboard
- 登录你的账户

### 2. 选择项目
- 找到并点击项目：`upgraded-octo-fortnight`

### 3. 进入环境变量设置
- 点击顶部菜单的 **Settings**
- 在左侧菜单选择 **Environment Variables**

### 4. 添加环境变量

#### 必需的环境变量（推荐）

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `ENABLE_NEWS_FILTER` | `true` | 启用智能新闻过滤功能 |

#### 可选的环境变量（增强功能）

| 变量名 | 值 | 说明 | 获取方式 |
|--------|-----|------|----------|
| `NEWSAPI_KEY` | `your_key` | NewsAPI.org API密钥 | https://newsapi.org/register |
| `BING_API_KEY` | `your_key` | Bing Search API密钥 | Azure Portal |
| `SERPAPI_KEY` | `your_key` | SerpAPI密钥 | https://serpapi.com/ |
| `GOOGLE_SEARCH_API_KEY` | `your_key` | Google Custom Search API密钥 | Google Cloud Console |
| `GOOGLE_SEARCH_ENGINE_ID` | `your_id` | Google搜索引擎ID | Google Custom Search |
| `GITHUB_TOKEN` | `your_token` | GitHub访问令牌（用于归档） | GitHub Settings > Developer settings |

### 5. 设置环境范围
对于每个环境变量，选择应用范围：
- ✅ **Production** - 生产环境
- ✅ **Preview** - 预览环境（PR部署）
- ✅ **Development** - 开发环境

**建议**：至少勾选 Production 和 Preview

### 6. 保存并重新部署
- 点击 **Save**
- Vercel 会自动重新部署，或手动点击 **Redeploy**

## ⚠️ 重要提示

### ✅ 应该在 Vercel 配置的变量
- `ENABLE_NEWS_FILTER` ✅
- `NEWSAPI_KEY` ✅
- `BING_API_KEY` ✅
- `SERPAPI_KEY` ✅
- `GOOGLE_SEARCH_API_KEY` ✅
- `GOOGLE_SEARCH_ENGINE_ID` ✅
- `GITHUB_TOKEN` ✅
- `CUSTOM_KEYWORDS` ✅（如果使用）
- `CUSTOM_NEWS_LINKS` ✅（如果使用）

### ❌ 不应该在 GitHub 配置的变量
- 所有运行时环境变量都不应该在 GitHub Secrets 中配置
- GitHub Secrets 只用于 CI/CD 流程（如 VERCEL_TOKEN）

## 🎯 最小配置

即使不配置任何 API 密钥，服务也能正常工作（使用免费源）：

**最小配置：**
```
ENABLE_NEWS_FILTER=true
```

**免费源包括：**
- ✅ Hacker News API
- ✅ Google News RSS
- ✅ Product Hunt GraphQL

## 🔍 验证配置

部署后，访问健康检查端点验证配置：

```bash
curl https://upgraded-octo-fortnight.vercel.app/api/health
```

响应中会显示：
- `config_status` - 显示哪些API密钥已配置
- `available_sources` - 显示可用的新闻源
- `free_features` - 显示免费功能状态

## 📝 GitHub Actions 说明

项目中的 GitHub Actions workflows（`.github/workflows/`）用于：
- 自动触发 Vercel 部署
- 运行测试
- 部署到其他平台（如 Render, Railway）

这些 workflows **不需要** `ENABLE_NEWS_FILTER` 等应用环境变量，因为它们不直接运行应用。

## 🚀 快速开始

1. **最小配置**（推荐先测试）：
   ```
   ENABLE_NEWS_FILTER=true
   ```

2. **完整配置**（需要API密钥）：
   ```
   ENABLE_NEWS_FILTER=true
   NEWSAPI_KEY=your_newsapi_key
   BING_API_KEY=your_bing_key
   ```

3. **部署后测试**：
   ```bash
   # 健康检查
   curl https://upgraded-octo-fortnight.vercel.app/api/health
   
   # 搜索测试（使用免费源）
   curl "https://upgraded-octo-fortnight.vercel.app/api/search?keywords=AI&max_results=5"
   ```

## ❓ 常见问题

**Q: 为什么不在 GitHub Secrets 中配置？**
A: GitHub Secrets 用于 CI/CD 流程，而应用运行时环境变量应该在部署平台（Vercel）配置。

**Q: 不配置 API 密钥能工作吗？**
A: 可以！服务会使用免费源（Hacker News, Google News RSS等）正常工作。

**Q: 配置后需要重新部署吗？**
A: Vercel 会自动重新部署，或手动点击 Redeploy。

**Q: 如何知道配置是否生效？**
A: 访问 `/api/health` 端点，查看 `config_status` 和 `available_sources`。

