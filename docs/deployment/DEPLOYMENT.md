# Vercel部署指南

## 概述

本指南说明如何将全网新闻聚合MCP服务部署到Vercel平台，使其作为HTTP API服务运行。

## 架构说明

部署后的服务架构：
- **前端**: Vercel托管的API端点
- **后端**: Python Serverless Functions
- **数据源**: 多个新闻API和RSS源
- **存储**: GitHub仓库（用于归档）

## 前置要求

### 1. Vercel账号
- 访问 https://vercel.com 注册账号
- 安装Vercel CLI: `npm install -g vercel`

### 2. GitHub仓库
- 确保代码已推送到GitHub仓库
- 仓库地址: https://github.com/clkhoo5211/upgraded-octo-fortnight

### 3. API密钥（可选，建议配置）
- **NewsAPI**: https://newsapi.org/register（免费100次/天）
- **Bing News**: https://azure.microsoft.com/services/cognitive-services/bing-news-search-api/
- **SerpAPI**: https://serpapi.com/users/sign_up（免费100次/月）
- **Google Custom Search**: https://developers.google.com/custom-search/v1/overview

## 部署步骤

### 方式一：通过Vercel Dashboard部署（推荐）

#### 1. 导入项目
1. 登录Vercel Dashboard: https://vercel.com/dashboard
2. 点击 **"Add New..."** → **"Project"**
3. 选择 **"Import Git Repository"**
4. 选择你的GitHub仓库: `clkhoo5211/upgraded-octo-fortnight`

#### 2. 配置项目
- **Framework Preset**: Other
- **Root Directory**: `global-news-mcp`
- **Build Command**: 留空（无需构建）
- **Output Directory**: 留空

#### 3. 配置环境变量
在 **Environment Variables** 部分添加以下变量：

**必需配置**:
```bash
ENABLE_NEWS_FILTER=true
```

**可选配置（推荐）**:
```bash
# NewsAPI.org密钥（免费100次/天）
NEWSAPI_KEY=your_newsapi_key

# Bing News API密钥
BING_API_KEY=your_bing_api_key

# SerpAPI密钥（支持Google/Bing/百度/Yahoo）
SERPAPI_KEY=your_serpapi_key

# Google Custom Search API
GOOGLE_SEARCH_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id

# GitHub Token（用于归档功能）
GITHUB_TOKEN=your_github_token
```

**自定义配置（可选）**:
```bash
# 自定义分类关键词（JSON格式）
CUSTOM_KEYWORDS={"tech":["AI","blockchain"],"finance":["stock","crypto"]}

# 自定义新闻源（JSON格式）
CUSTOM_NEWS_LINKS=[{"name":"BBC","url":"https://feeds.bbci.co.uk/news/rss.xml","type":"rss"}]
```

#### 4. 部署
点击 **"Deploy"** 按钮开始部署。

部署完成后，你将获得一个Vercel域名，例如：
```
https://global-news-mcp.vercel.app
```

### 方式二：通过Vercel CLI部署

#### 1. 登录Vercel
```bash
vercel login
```

#### 2. 进入项目目录
```bash
cd /path/to/global-news-mcp
```

#### 3. 部署
```bash
# 首次部署
vercel

# 生产环境部署
vercel --prod
```

#### 4. 设置环境变量
```bash
# 设置环境变量
vercel env add NEWSAPI_KEY
vercel env add BING_API_KEY
vercel env add SERPAPI_KEY
vercel env add GOOGLE_SEARCH_API_KEY
vercel env add GOOGLE_SEARCH_ENGINE_ID
vercel env add GITHUB_TOKEN
vercel env add ENABLE_NEWS_FILTER

# 重新部署以应用环境变量
vercel --prod
```

## API端点说明

部署成功后，可访问以下API端点：

### 1. 服务状态
```bash
GET https://your-domain.vercel.app/
GET https://your-domain.vercel.app/api/health
```

**响应示例**:
```json
{
  "status": "healthy",
  "service": "Global News Aggregator",
  "version": "1.0.0",
  "available_sources": [
    "NewsAPI.org",
    "Bing News",
    "SerpAPI (Google/Bing/百度/Yahoo)",
    "Google Custom Search",
    "Hacker News API",
    "Google News RSS",
    "Product Hunt GraphQL"
  ],
  "total_sources": 7
}
```

### 2. 搜索新闻
```bash
POST https://your-domain.vercel.app/api/search
Content-Type: application/json

{
  "keywords": "人工智能",
  "categories": ["tech", "finance"],
  "languages": "zh",
  "date_range": "last_7_days",
  "max_results": 50
}
```

**GET方式**:
```bash
GET https://your-domain.vercel.app/api/search?keywords=AI&languages=en&max_results=20
```

**响应示例**:
```json
{
  "success": true,
  "count": 45,
  "news": [
    {
      "title": "OpenAI发布GPT-5",
      "description": "...",
      "url": "https://...",
      "source": "TechCrunch",
      "published_at": "2025-11-11T10:00:00Z",
      "category": "TECH",
      "language": "en",
      "quality_score": 85
    }
  ],
  "search_params": {
    "keywords": "人工智能",
    "categories": ["tech", "finance"],
    "languages": "zh",
    "date_range": "last_7_days",
    "max_results": 50
  }
}
```

### 3. 下载完整新闻内容
```bash
POST https://your-domain.vercel.app/api/download
Content-Type: application/json

{
  "news_url": "https://techcrunch.com/article/...",
  "include_images": true,
  "include_banners": true
}
```

**GET方式**:
```bash
GET https://your-domain.vercel.app/api/download?news_url=https://...
```

**响应示例**:
```json
{
  "url": "https://techcrunch.com/article/...",
  "title": "OpenAI发布GPT-5",
  "content": "完整新闻正文...",
  "images": [
    "https://techcrunch.com/images/1.jpg",
    "https://techcrunch.com/images/2.jpg"
  ],
  "banners": [
    "https://techcrunch.com/banners/main.jpg"
  ],
  "success": true
}
```

## 测试部署

### 1. 健康检查
```bash
curl https://your-domain.vercel.app/api/health
```

### 2. 搜索测试（使用免费源）
```bash
curl -X POST https://your-domain.vercel.app/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "blockchain",
    "languages": "en",
    "max_results": 10
  }'
```

### 3. 下载测试
```bash
curl -X POST https://your-domain.vercel.app/api/download \
  -H "Content-Type: application/json" \
  -d '{
    "news_url": "https://news.ycombinator.com/item?id=12345678"
  }'
```

## 零配置运行

即使不配置任何API密钥，服务也能正常运行，使用免费的新闻源：
- ✅ Hacker News API（完全免费）
- ✅ Google News RSS（完全免费）
- ✅ Product Hunt GraphQL（免费，有限制）

**零配置测试**:
```bash
# 搜索Hacker News热门新闻
curl "https://your-domain.vercel.app/api/search?max_results=10"
```

## 性能优化

### 1. 函数配置
在 `vercel.json` 中已配置：
- **Memory**: 1024 MB
- **Max Duration**: 60秒
- **Regions**: 香港(hkg1)、新加坡(sin1) - 针对亚洲用户优化

### 2. 冷启动优化
- Vercel会缓存函数实例
- 首次请求可能需要3-5秒
- 后续请求通常在1秒内响应

### 3. 并发限制
- 免费计划: 10个并发请求
- Pro计划: 100个并发请求
- Enterprise: 无限制

## 监控和日志

### 1. Vercel Dashboard
访问 https://vercel.com/dashboard 查看：
- 实时日志
- 性能指标
- 错误追踪
- 请求统计

### 2. 日志查看
```bash
# CLI查看实时日志
vercel logs your-domain.vercel.app
```

## 故障排除

### 问题1: 部署失败
**症状**: 部署过程中报错

**解决方案**:
1. 检查 `requirements.txt` 是否正确
2. 确保Python版本>=3.11
3. 查看部署日志了解具体错误

### 问题2: API返回500错误
**症状**: API请求返回内部服务器错误

**解决方案**:
1. 检查环境变量是否正确配置
2. 查看Vercel日志了解错误详情
3. 确认请求参数格式正确

### 问题3: 搜索结果为空
**症状**: 搜索API返回0条结果

**解决方案**:
1. 检查关键词是否正确
2. 尝试扩大日期范围
3. 检查API密钥是否有效
4. 使用零配置模式测试（不传关键词）

### 问题4: 函数超时
**症状**: 请求超过60秒未响应

**解决方案**:
1. 减少 `max_results` 参数值
2. 限制搜索的新闻源数量
3. 考虑升级到Pro计划（300秒超时）

## 成本估算

### Vercel免费计划限制
- ✅ 100 GB带宽/月
- ✅ 100小时函数执行时间/月
- ✅ 10个并发请求
- ✅ 60秒函数最大执行时间

**预估使用量**（每次搜索请求）:
- 函数执行时间: 2-5秒
- 数据传输: 约50KB

**免费额度可支持**:
- 约 72,000 次搜索请求/月
- 适合个人和小型项目

### API密钥成本
- **NewsAPI.org**: 免费100次/天，$449/月无限制
- **Bing News**: 免费1,000次/月，$4/1,000次
- **SerpAPI**: 免费100次/月，$50/月5,000次
- **Google Custom Search**: 免费100次/天，$5/1,000次

## 自定义域名

### 1. 添加域名
1. 在Vercel Dashboard中选择项目
2. 进入 **Settings** → **Domains**
3. 添加你的域名（例如: api.yourdomain.com）

### 2. 配置DNS
根据Vercel提供的说明，在你的DNS提供商处添加：
- A记录或CNAME记录指向Vercel

### 3. HTTPS证书
Vercel自动提供免费的Let's Encrypt SSL证书。

## 安全建议

### 1. API密钥保护
- ✅ 使用Vercel环境变量存储
- ✅ 不要在代码中硬编码
- ✅ 不要提交到Git仓库

### 2. 请求限制
建议实现请求限制：
- 使用Vercel Edge Config
- 添加请求频率限制
- 考虑添加API密钥认证

### 3. CORS配置
如需从浏览器直接调用API，在API代码中添加CORS头：
```python
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://yourdomain.com"}})
```

## 下一步

- 📊 配置监控和告警
- 🔒 添加API认证
- 🚀 优化性能和缓存
- 📱 创建前端界面
- 🤖 设置定时任务（GitHub Actions）

## 支持

- 📖 文档: [README.md](README.md)
- 🐛 问题反馈: https://github.com/clkhoo5211/upgraded-octo-fortnight/issues
- 💬 讨论: GitHub Discussions

---

**部署愉快！** 🎉
