# 全网新闻聚合MCP服务

一个功能强大的MCP服务，用于全网搜索、聚合、分类和归档新闻内容。支持多种新闻源、智能过滤、自动分类，并可通过GitHub自动归档每日新闻。

## 🚀 核心特性

### 1. 全网多源搜索
- ✅ **NewsAPI.org** - 全球新闻API
- ✅ **Google News RSS** - 免费Google新闻搜索
- ✅ **Bing News Search** - 微软新闻搜索（需API密钥）
- ✅ **SerpAPI** - 多搜索引擎支持（Google/Bing/百度/Yahoo）**【新增】**
- ✅ **Google Custom Search** - Google官方搜索API **【新增】**
- ✅ **Hacker News** - 技术新闻热榜
- ✅ **Product Hunt** - 产品发布热榜
- ✅ **自定义RSS/JSON源** - 支持任意RSS或JSON格式新闻源
- ✅ **多语言支持** - 中文、英文及多语言混合搜索
- 💡 **无需API Key也可用** - 免费源（Hacker News + Google News RSS）即可工作

### 2. 智能过滤系统
- ✅ **关键词纳入/排除规则** - 灵活的内容过滤
- ✅ **域名白名单/黑名单** - 来源可信度控制
- ✅ **内容质量评分** - 自动评估新闻质量
- ✅ **垃圾内容识别** - 自动过滤广告和推广内容
- ✅ **长度限制** - 防止过长或过短的内容

### 3. 自动分类
支持多种新闻分类，基于关键词智能匹配：
- 政治 (politics)
- 财经 (finance)
- 加密货币 (crypto)
- 区块链 (blockchain)
- 风水 (fengshui)
- 科技 (tech)
- 社会 (social)
- 国际 (international)

### 4. 环境变量配置
- ✅ **自定义搜索关键词** - 通过环境变量扩展分类关键词
- ✅ **自定义新闻源链接** - 添加任意RSS/JSON数据源
- ✅ **灵活的过滤器配置** - 动态调整过滤规则

### 5. GitHub自动归档
- ✅ **按日期分类** - `/YYYY/MM/DD/` 目录结构
- ✅ **按类别归档** - 每个类别独立文件
- ✅ **多种格式** - 支持Markdown+HTML/XML代码块
- ✅ **自动提交** - 通过GitHub API自动推送
- ✅ **定时任务** - GitHub Actions每日凌晨1点执行

## 📦 项目结构

```
global-news-mcp/
├── server.py                    # MCP服务器主文件
├── api/                         # Vercel Serverless Functions
│   ├── index.py                # API首页
│   ├── search.py               # 搜索API端点
│   ├── download.py             # 下载API端点
│   └── health.py               # 健康检查端点
├── src/
│   └── news_tools/
│       ├── __init__.py
│       ├── news_searcher.py     # 新闻搜索和聚合
│       ├── news_filter.py       # 智能过滤系统
│       ├── content_downloader.py # 内容下载
│       ├── github_archiver.py   # GitHub归档
│       └── scheduler.py         # 定时任务配置
├── test_features.py             # 功能测试脚本
├── vercel.json                  # Vercel部署配置
├── vercel-deploy.sh             # Vercel部署脚本
├── DEPLOYMENT.md                # 部署指南
├── ENV_CONFIG.md                # 环境变量配置说明
├── README.md                    # 本文件
└── requirements.txt             # 依赖包
```

## 🛠️ 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件或在系统中设置以下环境变量：

```bash
# === 必需配置 ===
GITHUB_TOKEN=your_github_token_here          # GitHub个人访问令牌
NEWSAPI_KEY=your_newsapi_key_here            # NewsAPI密钥
GITHUB_REPO=username/repo-name               # GitHub仓库

# === 可选配置 ===
# 额外的搜索API
BING_API_KEY=your_bing_api_key               # Bing搜索API
NEWSDATA_KEY=your_newsdata_key               # NewsData.io API

# 自定义关键词（格式: 分类:关键词1,关键词2;分类2:关键词3）
CUSTOM_KEYWORDS=politics:美国大选,拜登;finance:A股,恒生指数;crypto:比特币ETF

# 自定义新闻源（逗号分隔的RSS/JSON链接）
CUSTOM_NEWS_LINKS=https://techcrunch.com/feed/,https://rsshub.app/weibo/search/hot

# 过滤器配置
ENABLE_NEWS_FILTER=true                      # 启用智能过滤
FILTER_INCLUDE_KEYWORDS=热点,重要,突发        # 包含关键词
FILTER_EXCLUDE_KEYWORDS=广告,推广,赞助        # 排除关键词
```

详细配置说明请参考 [ENV_CONFIG.md](ENV_CONFIG.md)

### 3. 启动MCP服务器

```bash
python server.py
```

## 🧪 功能测试

运行测试脚本验证所有功能：

```bash
python test_features.py
```

测试覆盖：
- ✅ NewsFilter智能过滤
- ✅ 新闻自动分类
- ✅ Hacker News集成
- ✅ 自定义新闻源
- ✅ 多源并行搜索

## 📖 MCP工具使用

### 1. search_global_news
搜索和聚合全网新闻

```python
{
  "keywords": "AI技术",
  "categories": ["tech", "crypto"],
  "languages": "all",  # zh/en/all
  "date_range": "last_7_days",  # yesterday/last_7_days/last_30_days
  "max_results": 50
}
```

### 2. download_news_content
下载完整新闻内容、图片和横幅

```python
{
  "news_url": "https://example.com/article",
  "include_images": true,
  "include_banners": true
}
```

### 3. classify_and_save_news
智能分类并保存到GitHub

```python
{
  "news_data": [...],  # 新闻数据数组
  "save_format": "md_with_html",  # md_with_html/md_with_xml
  "target_date": "2025-11-12"  # 可选，默认今天
}
```

### 4. schedule_daily_news_archive
生成定时任务配置

```python
{
  "cron_expression": "0 1 * * *",  # 每日凌晨1点
  "categories": ["politics", "finance", "tech"],
  "languages": "all"
}
```

## 🔄 GitHub Actions自动化

在GitHub仓库中创建 `.github/workflows/daily-news.yml`：

```yaml
name: Daily News Archive
on:
  schedule:
    - cron: '0 1 * * *'  # 每天凌晨1点
  workflow_dispatch:  # 允许手动触发

jobs:
  archive:
    runs-on: ubuntu-latest
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      NEWSAPI_KEY: ${{ secrets.NEWSAPI_KEY }}
      BING_API_KEY: ${{ secrets.BING_API_KEY }}
      GITHUB_REPO: ${{ github.repository }}
      CUSTOM_KEYWORDS: politics:美国大选;finance:A股,港股
      CUSTOM_NEWS_LINKS: https://techcrunch.com/feed/
      ENABLE_NEWS_FILTER: true
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run MCP News Archiver
        run: |
          python -c "
          import asyncio
          from server import search_global_news, classify_and_save_news
          
          async def main():
              # 搜索昨日新闻
              result = await search_global_news(
                  date_range='yesterday',
                  languages='all',
                  max_results=100
              )
              
              # 分类并保存
              if result['success']:
                  classify_and_save_news(
                      news_data=result['news'],
                      save_format='md_with_html'
                  )
          
          asyncio.run(main())
          "
```

## 📚 API集成文档

**想要在其他项目中使用此API？**

👉 **[完整集成指南](./docs/api/COMPLETE_INTEGRATION_GUIDE.md)** - ⭐ **推荐：其他项目集成此API的完整指南**

包含：
- ✅ 5分钟快速开始
- ✅ 用户注册和Token获取
- ✅ Python和JavaScript完整客户端代码（可直接复制使用）
- ✅ Token管理和续期
- ✅ 错误处理
- ✅ 所有API端点说明

---

## 🚀 Vercel部署（HTTP API模式）

除了作为MCP服务运行，本项目还支持部署到Vercel作为HTTP API服务。

### 快速部署

**方式一：通过Vercel Dashboard（推荐）**

1. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
2. 点击 **"Add New..."** → **"Project"**
3. 导入GitHub仓库: `clkhoo5211/upgraded-octo-fortnight`
4. 设置Root Directory为 `global-news-mcp`
5. 配置环境变量（见下方）
6. 点击 **"Deploy"**

**方式二：通过CLI部署**

```bash
# 安装Vercel CLI
npm install -g vercel

# 进入项目目录
cd global-news-mcp

# 登录并部署
vercel login
vercel --prod
```

或使用提供的部署脚本：

```bash
chmod +x vercel-deploy.sh
./vercel-deploy.sh
```

### 环境变量配置

在Vercel Dashboard的Environment Variables中配置：

**必需**:
- `ENABLE_NEWS_FILTER=true`

**可选（推荐）**:
- `NEWSAPI_KEY` - NewsAPI密钥
- `BING_API_KEY` - Bing搜索API密钥
- `SERPAPI_KEY` - SerpAPI密钥（支持Google/Bing/百度/Yahoo）
- `GOOGLE_SEARCH_API_KEY` - Google Custom Search API密钥
- `GOOGLE_SEARCH_ENGINE_ID` - Google搜索引擎ID
- `GITHUB_TOKEN` - GitHub访问令牌

### API端点

部署成功后可访问以下端点：

**1. 健康检查**
```bash
GET https://your-domain.vercel.app/api/health
```

**2. 搜索新闻**
```bash
POST https://your-domain.vercel.app/api/search
Content-Type: application/json

{
  "keywords": "人工智能",
  "languages": "zh",
  "max_results": 20
}
```

或使用GET方式：
```bash
GET https://your-domain.vercel.app/api/search?keywords=AI&max_results=10
```

**3. 下载完整内容**
```bash
POST https://your-domain.vercel.app/api/download
Content-Type: application/json

{
  "news_url": "https://example.com/article"
}
```

### 零配置运行

即使不配置任何API密钥，服务也能使用免费源正常运行：
- ✅ Hacker News API
- ✅ Google News RSS
- ✅ Product Hunt GraphQL

详细部署说明请参考 [DEPLOYMENT.md](DEPLOYMENT.md)

## 🎯 使用场景

### 1. 个人新闻聚合
每日自动收集感兴趣的新闻，按分类归档到GitHub私人仓库

### 2. 行业动态监控
持续跟踪特定行业（如加密货币、AI技术）的最新动态

### 3. 研究资料收集
为学术研究或市场分析收集和整理新闻资料

### 4. 内容创作素材
为自媒体、博客提供持续的新闻素材来源

### 5. HTTP API服务
部署到Vercel后可作为新闻API服务，供其他应用调用

## 🧩 技术栈

- **FastMCP** - MCP服务器框架
- **httpx** - 异步HTTP客户端
- **feedparser** - RSS/Atom解析
- **PyGithub** - GitHub API集成
- **asyncio** - 异步并发处理

## 📊 测试结果

最新测试（2025-11-12）：

```
✅ NewsFilter智能过滤功能 - 正常
✅ 新闻智能分类 - 正常（4/4分类准确）
✅ Hacker News API - 正常（5条热门故事）
✅ 自定义新闻源 - 正常（5条新闻）
✅ 全网搜索 - 正常（10条新闻，多源聚合）
```

## 🔧 故障排查

### 问题：API调用失败
- 检查API密钥是否正确设置
- 确认API配额未超限
- 验证网络连接

### 问题：GitHub提交失败
- 确认GITHUB_TOKEN权限包含repo写权限
- 检查仓库名称格式（username/repo）
- 验证GitHub API连接

### 问题：过滤器不生效
- 检查环境变量格式是否正确
- 确认ENABLE_NEWS_FILTER=true
- 查看日志输出中的过滤信息

## 📝 更新日志

### v1.1.0 (2025-11-12)
- ✨ 新增智能过滤系统（NewsFilter）
- ✨ 集成Bing News Search API
- ✨ 集成Google News RSS
- ✨ 集成Hacker News API
- ✨ 支持自定义RSS/JSON新闻源
- ✨ 支持环境变量配置自定义关键词
- ✨ 完整的测试套件
- 📝 完善的文档和配置说明

### v1.0.0 (2025-11-11)
- 🎉 初始版本发布
- ✅ 基础新闻搜索和聚合
- ✅ GitHub自动归档
- ✅ 定时任务配置

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📧 联系方式

项目维护者: MiniMax Agent
GitHub仓库: https://github.com/clkhoo5211/upgraded-octo-fortnight

---

**提示**: 使用前请先阅读 [ENV_CONFIG.md](ENV_CONFIG.md) 了解详细的环境变量配置方法。
