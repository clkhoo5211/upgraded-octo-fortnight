# API密钥配置指南

> 此文档已从根目录移动到 `docs/deployment/API_KEYS_SETUP.md`

## MCP新闻聚合服务 - API密钥配置指南

为了完成测试和使用，需要以下API密钥：

### 1. GitHub Personal Access Token (必需) ⭐

- **用途**: 自动提交新闻归档到GitHub仓库
- **获取方式**: https://github.com/settings/tokens
- **权限要求**: repo (完整仓库访问权限)
- **目标仓库**: clkhoo5211/upgraded-octo-fortnight

### 2. NewsAPI.org API Key (推荐)

- **用途**: 搜索全球新闻源（150,000+新闻源）
- **获取方式**: https://newsapi.org/register
- **免费套餐**: 100次/天
- **注册仅需邮箱，即时获取密钥**

### 3. NewsData.io API Key (可选)

- **用途**: 额外的新闻源支持
- **获取方式**: https://newsdata.io/register
- **免费套餐**: 200次/天

### 4. Bing API Key (可选)

- **用途**: Bing新闻搜索
- **获取方式**: https://www.microsoft.com/en-us/bing/apis/bing-news-search-api

### 5. SerpAPI Key (可选)

- **用途**: 多搜索引擎支持（Google/Bing/百度/Yahoo）
- **获取方式**: https://serpapi.com/

## 注意事项

- GitHub Token是必需的（用于归档功能）
- 至少需要一个新闻API密钥（NewsAPI或NewsData）以获得最佳体验
- 如果不提供新闻API密钥，系统将仅使用RSS源（功能有限）

## 配置方式

### 方式1: 环境变量

```bash
export GITHUB_TOKEN="your_github_token"
export NEWSAPI_KEY="your_newsapi_key"
export NEWSDATA_KEY="your_newsdata_key"
export BING_API_KEY="your_bing_api_key"
export SERPAPI_KEY="your_serpapi_key"
```

### 方式2: Vercel环境变量

在Vercel Dashboard的Environment Variables中配置：
- `GITHUB_TOKEN`
- `NEWSAPI_KEY`
- `NEWSDATA_KEY`
- `BING_API_KEY`
- `SERPAPI_KEY`

### 方式3: .env文件（本地开发）

创建 `.env` 文件（已在.gitignore中，不会被提交）：

```bash
GITHUB_TOKEN=your_github_token
NEWSAPI_KEY=your_newsapi_key
NEWSDATA_KEY=your_newsdata_key
BING_API_KEY=your_bing_api_key
SERPAPI_KEY=your_serpapi_key
```

## 相关文档

- [环境变量配置指南](./ENV_SETUP.md)
- [Vercel部署指南](./VERCEL_DEPLOY_GUIDE.md)
- [GitHub Token设置](../security/GITHUB_TOKEN_SETUP.md)
