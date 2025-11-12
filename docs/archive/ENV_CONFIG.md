# 环境变量配置说明

本MCP服务支持通过环境变量进行灵活配置，您作为GitHub仓库的owner可以通过设置环境变量来自定义新闻搜索行为。

## 必需的环境变量

### 基础API密钥
```bash
# GitHub个人访问令牌（用于自动提交新闻到仓库）
GITHUB_TOKEN=your_github_token_here

# NewsAPI密钥（用于新闻API搜索）
NEWSAPI_KEY=your_newsapi_key_here

# GitHub仓库信息
GITHUB_REPO=clkhoo5211/upgraded-octo-fortnight
```

## 可选的环境变量

### 额外的搜索API密钥
```bash
# Bing News Search API密钥（可选，用于全网搜索）
BING_API_KEY=your_bing_api_key_here

# NewsData.io API密钥（可选，额外的新闻源）
NEWSDATA_KEY=your_newsdata_key_here
```

### 自定义搜索关键词
通过环境变量添加自定义搜索关键词，扩展默认分类的关键词列表。

**格式**: `CUSTOM_KEYWORDS=分类1:关键词1,关键词2;分类2:关键词3,关键词4`

**示例**:
```bash
# 为现有分类添加关键词
CUSTOM_KEYWORDS=politics:美国大选,总统选举;finance:A股,港股;crypto:狗狗币,柴犬币

# 创建新的自定义分类
CUSTOM_KEYWORDS=gaming:游戏,电竞,主机;education:在线教育,MOOC,课程
```

**支持的默认分类**:
- `politics` - 政治
- `finance` - 财经
- `crypto` - 加密货币
- `blockchain` - 区块链
- `fengshui` - 风水
- `tech` - 科技
- `social` - 社会
- `international` - 国际

### 自定义新闻源链接
通过环境变量添加自定义RSS或JSON新闻源链接。

**格式**: `CUSTOM_NEWS_LINKS=链接1,链接2,链接3`

**支持的链接类型**:
1. **RSS/Atom Feed**: 任何标准的RSS或Atom格式的新闻源
2. **JSON API**: 返回JSON格式新闻数据的API端点

**示例**:
```bash
# 添加自定义RSS源
CUSTOM_NEWS_LINKS=https://techcrunch.com/feed/,https://www.theverge.com/rss/index.xml

# 混合RSS和JSON源
CUSTOM_NEWS_LINKS=https://news.example.com/rss,https://api.example.com/news.json

# 添加多个源（逗号分隔）
CUSTOM_NEWS_LINKS=https://source1.com/feed,https://source2.com/api/news,https://source3.com/rss
```

**JSON格式要求**:
系统支持以下常见的JSON结构：
```json
{
  "items": [  // 或 "articles" 或 "data"
    {
      "title": "新闻标题",
      "description": "新闻描述",
      "content": "完整内容",
      "url": "新闻链接",
      "published_at": "发布时间",
      "image": "图片链接",
      "category": "分类"
    }
  ]
}
```

### 过滤器配置
```bash
# 启用/禁用智能过滤器（默认启用）
ENABLE_NEWS_FILTER=true

# 自定义包含关键词（用于NewsFilter）
FILTER_INCLUDE_KEYWORDS=热点,重要,紧急,突发

# 自定义排除关键词（用于NewsFilter）
FILTER_EXCLUDE_KEYWORDS=广告,推广,赞助,软文
```

## 完整配置示例

在GitHub Actions中设置环境变量：

```yaml
name: Daily News Archive
on:
  schedule:
    - cron: '0 1 * * *'  # 每天凌晨1点运行
  workflow_dispatch:

jobs:
  archive:
    runs-on: ubuntu-latest
    env:
      # 基础配置
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      NEWSAPI_KEY: ${{ secrets.NEWSAPI_KEY }}
      GITHUB_REPO: clkhoo5211/upgraded-octo-fortnight
      
      # 可选API密钥
      BING_API_KEY: ${{ secrets.BING_API_KEY }}
      
      # 自定义关键词
      CUSTOM_KEYWORDS: |
        politics:美国大选,拜登,特朗普;
        finance:A股,恒生指数,美联储;
        crypto:比特币ETF,去中心化交易所;
        gaming:Switch 2,PS5 Pro,Xbox
      
      # 自定义新闻源
      CUSTOM_NEWS_LINKS: |
        https://www.zhihu.com/rss,
        https://rsshub.app/weibo/search/hot,
        https://techcrunch.com/feed/
      
      # 过滤器配置
      ENABLE_NEWS_FILTER: true
      FILTER_INCLUDE_KEYWORDS: 热点,重要,突发
      FILTER_EXCLUDE_KEYWORDS: 广告,推广,软文
    
    steps:
      - name: Run MCP News Archiver
        run: |
          # 运行MCP服务或调用API
```

## 本地开发配置

创建 `.env` 文件：

```bash
# .env
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
NEWSAPI_KEY=abc123xxxxxxxxxxxx
BING_API_KEY=def456xxxxxxxxxxxx
GITHUB_REPO=clkhoo5211/upgraded-octo-fortnight

# 自定义配置
CUSTOM_KEYWORDS=politics:川普,拜登;finance:纳斯达克,道琼斯
CUSTOM_NEWS_LINKS=https://feeds.bbci.co.uk/news/rss.xml,https://rss.cnn.com/rss/edition.rss
ENABLE_NEWS_FILTER=true
```

然后使用 `python-dotenv` 加载：

```python
from dotenv import load_dotenv
load_dotenv()
```

## 配置更新流程

1. **修改环境变量**: 在GitHub仓库的Settings > Secrets and variables > Actions中更新
2. **无需重启**: 环境变量在每次执行时动态加载
3. **立即生效**: 下次定时任务或手动触发时使用新配置

## 注意事项

1. **安全性**: 所有API密钥和敏感信息应存储在GitHub Secrets中，不要直接写在代码或配置文件中
2. **格式要求**: 多个值使用逗号分隔，分类使用冒号分隔，不同分类使用分号分隔
3. **链接有效性**: 自定义链接必须是可访问的公开RSS或JSON端点
4. **关键词语言**: 支持中英文关键词混合，系统会自动检测和匹配
5. **配额限制**: 注意各个API的调用配额限制，建议合理设置搜索频率

## 故障排查

如果自定义配置不生效，请检查：

1. **环境变量格式**: 确保符合上述格式要求
2. **链接可访问性**: 使用curl测试自定义链接是否可访问
3. **日志输出**: 查看MCP服务日志中的错误信息
4. **API密钥有效性**: 验证所有API密钥是否有效且未过期


---

## 搜索引擎 API 配置（新增功能）

### 🔍 概述

搜索引擎 API 让你的 MCP 服务在**没有专门新闻 API Key** 的情况下，也能通过 Google、Bing、百度、Yahoo 等主流搜索引擎获取全网新闻。

### SerpAPI（推荐）

**说明**: 支持多个搜索引擎（Google、Bing、百度、Yahoo等）

```bash
SERPAPI_KEY=your_serpapi_key_here
```

- **获取方式**: https://serpapi.com/
- **免费额度**: 100次/月
- **付费价格**: $50/月（5000次）
- **优势**: 多引擎支持，结果稳定，返回结构化数据

### Google Custom Search API

**说明**: Google 官方搜索 API

```bash
GOOGLE_SEARCH_API_KEY=your_google_search_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
```

- **获取方式**: https://developers.google.com/custom-search
- **免费额度**: 100次/天
- **付费价格**: $5/1000次
- **优势**: Google 官方，结果质量高

### 使用场景

搜索引擎 API 特别适用于：

1. ✅ **没有专门新闻 API Key** - 可以通过搜索引擎获取全网新闻
2. ✅ **需要更广泛的新闻来源** - 不限于特定新闻网站
3. ✅ **搜索特定关键词** - 精确搜索感兴趣的主题
4. ✅ **多语言支持** - 支持中文、英文等多种语言搜索
5. ✅ **实时内容** - 直接从网页提取最新内容

### 配置示例

```bash
# 方案1: 使用 SerpAPI（推荐）
SERPAPI_KEY=abc123def456

# 方案2: 使用 Google Custom Search
GOOGLE_SEARCH_API_KEY=AIzaSyD1234567890
GOOGLE_SEARCH_ENGINE_ID=0123456789abc:xyz

# 方案3: 同时配置多个（系统会并行搜索，提高结果数量）
SERPAPI_KEY=abc123def456
GOOGLE_SEARCH_API_KEY=AIzaSyD1234567890
GOOGLE_SEARCH_ENGINE_ID=0123456789abc:xyz
```

### 工作流程

```
用户输入关键词 "人工智能"
    ↓
系统并行搜索多个源
    ├─ Hacker News API (技术新闻)
    ├─ Google News RSS (综合新闻)
    ├─ NewsAPI.org (如果配置了key)
    ├─ SerpAPI (全网搜索) ← 新增
    └─ Google Custom Search (全网搜索) ← 新增
    ↓
提取新闻内容
    ↓
智能分类（tech/crypto/blockchain等）
    ↓
质量过滤（关键词、评分等）
    ↓
返回高质量新闻结果
```

### 成本对比

| 方案 | 免费额度 | 付费成本 | 优势 | 劣势 |
|------|----------|----------|------|------|
| **无配置** | 无限 | 免费 | 零成本 | 仅限 Hacker News + Google News RSS |
| **SerpAPI** | 100次/月 | $50/月 | 多引擎，结果丰富 | 有成本 |
| **Google Custom Search** | 100次/天 | $5/1000次 | Google官方，质量高 | 仅 Google |
| **NewsAPI** | 100次/天 | $449/月 | 专业新闻API | 成本较高 |

### 推荐配置策略

#### 个人使用/测试
```bash
# 使用免费源，无需配置
# 已包含: Hacker News + Google News RSS
```

#### 小型项目
```bash
# 配置 SerpAPI 免费额度
SERPAPI_KEY=your_key
# 免费100次/月，通常够用
```

#### 中型项目
```bash
# SerpAPI + Google Custom Search
SERPAPI_KEY=your_serpapi_key
GOOGLE_SEARCH_API_KEY=your_google_key
GOOGLE_SEARCH_ENGINE_ID=your_engine_id
# 合计: 100次/月 + 100次/天
```

#### 企业部署
```bash
# 全量配置，最大覆盖
NEWSAPI_KEY=your_newsapi_key
SERPAPI_KEY=your_serpapi_key
GOOGLE_SEARCH_API_KEY=your_google_key
GOOGLE_SEARCH_ENGINE_ID=your_engine_id
BING_API_KEY=your_bing_key
# 多源并行，高可用性
```

### 测试搜索引擎集成

```bash
# 测试 SerpAPI
export SERPAPI_KEY="your_key"
cd /workspace/global-news-mcp
python -c "
from src.news_tools import NewsSearcher
import asyncio

async def test():
    searcher = NewsSearcher()
    results = await searcher.search_news(keywords='人工智能', max_results=10)
    print(f'✓ 找到 {len(results)} 条新闻')
    for news in results[:3]:
        print(f'  - {news[\"title\"]}')
    await searcher.close()

asyncio.run(test())
"
```

### 详细文档

更多关于搜索引擎集成的详细信息，请参阅：
- <filepath>docs/SEARCH_ENGINE_INTEGRATION.md</filepath> - 完整实现指南
- <filepath>README.md</filepath> - 项目总览和快速开始

