# 搜索引擎新闻获取功能

## 概述

本文档说明如何让 MCP 服务在**没有 API Key** 的情况下，通过**搜索引擎**（Google、Bing、百度、Yahoo等）获取新闻。

## 功能优势

✅ **无需 API Key** - 不需要注册和配置 NewsAPI、Bing API 等服务  
✅ **全网覆盖** - 可以搜索任何公开的新闻网站  
✅ **实时内容** - 直接从网页提取最新内容  
✅ **灵活搜索** - 支持任意关键词搜索  

## 实现方案

### 方案 A: 通过 MiniMax Agent 辅助（推荐）

**适用场景**: 在 Claude Desktop 等 MCP 客户端中使用

当你在 MCP 客户端中使用时，可以请求 MiniMax Agent 帮助搜索：

```
请帮我搜索"人工智能"相关的最新新闻，并进行分类和过滤
```

MiniMax Agent 会：
1. 使用搜索引擎搜索关键词
2. 提取新闻内容
3. 调用你的 MCP 服务进行分类和过滤
4. 返回结构化结果

### 方案 B: 集成第三方搜索 API

**适用场景**: 独立部署的 MCP 服务

如果你需要完全自动化的搜索功能，可以集成以下服务：

#### 1. SerpAPI（推荐）
- 官网: https://serpapi.com/
- 免费额度: 100次/月
- 支持: Google、Bing、百度、Yahoo 等多个搜索引擎

```bash
# 安装
pip install google-search-results

# 配置环境变量
export SERPAPI_KEY="your_api_key"
```

#### 2. Google Custom Search API
- 官网: https://developers.google.com/custom-search
- 免费额度: 100次/天
- 仅支持 Google

```bash
# 配置环境变量
export GOOGLE_SEARCH_API_KEY="your_api_key"
export GOOGLE_SEARCH_ENGINE_ID="your_engine_id"
```

#### 3. Bing Web Search API
- 官网: https://www.microsoft.com/en-us/bing/apis/bing-web-search-api
- 免费试用: 1000次/月
- 微软官方

```bash
# 配置环境变量
export BING_SEARCH_API_KEY="your_api_key"
```

## 集成代码示例

### 使用 SerpAPI

在 `src/news_tools/news_searcher.py` 中添加：

```python
async def _search_with_serpapi(
    self,
    keywords: str,
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """使用 SerpAPI 搜索新闻"""
    try:
        from serpapi import GoogleSearch
        
        api_key = os.getenv('SERPAPI_KEY')
        if not api_key:
            return []
        
        params = {
            "q": keywords,
            "tbm": "nws",  # 新闻搜索
            "api_key": api_key,
            "num": max_results
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        news_list = []
        for item in results.get('news_results', []):
            news_list.append({
                'title': item.get('title', ''),
                'description': item.get('snippet', ''),
                'url': item.get('link', ''),
                'source': item.get('source', ''),
                'published_at': item.get('date', ''),
                'image_url': item.get('thumbnail', ''),
            })
        
        return news_list
    except Exception as e:
        print(f"SerpAPI搜索错误: {e}")
        return []
```

### 使用 Google Custom Search API

```python
async def _search_with_google_custom(
    self,
    keywords: str,
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """使用 Google Custom Search API 搜索新闻"""
    try:
        api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
        if not api_key or not engine_id:
            return []
        
        url = 'https://www.googleapis.com/customsearch/v1'
        params = {
            'key': api_key,
            'cx': engine_id,
            'q': keywords,
            'num': min(max_results, 10)  # 最多10条/次
        }
        
        response = await self.client.get(url, params=params)
        data = response.json()
        
        news_list = []
        for item in data.get('items', []):
            news_list.append({
                'title': item.get('title', ''),
                'description': item.get('snippet', ''),
                'url': item.get('link', ''),
                'source': item.get('displayLink', ''),
            })
        
        return news_list
    except Exception as e:
        print(f"Google搜索错误: {e}")
        return []
```

## 在 search_news 中集成

修改 `src/news_tools/news_searcher.py` 的 `search_news` 方法：

```python
async def search_news(
    self,
    keywords: Optional[str] = None,
    categories: Optional[List[str]] = None,
    languages: str = 'all',
    date_range: str = 'last_7_days',
    sources: Optional[List[str]] = None,
    max_results: int = 50
) -> List[Dict[str, Any]]:
    """搜索和聚合新闻"""
    all_news = []
    tasks = []
    
    # 现有的搜索源...
    
    # 新增：搜索引擎搜索
    if keywords and os.getenv('SERPAPI_KEY'):
        tasks.append(self._search_with_serpapi(keywords, max_results))
    elif keywords and os.getenv('GOOGLE_SEARCH_API_KEY'):
        tasks.append(self._search_with_google_custom(keywords, max_results))
    
    # 并发执行所有搜索
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, list):
                all_news.extend(result)
    
    # 过滤、分类、评分...
    return self._filter_and_classify(all_news, categories, languages, max_results)
```

## 工作流程图

```
用户输入关键词
    ↓
并行搜索多个源
    ├─ Hacker News API (免费)
    ├─ Google News RSS (免费)
    ├─ NewsAPI.org (需要key)
    ├─ Bing News API (需要key)
    └─ 搜索引擎 (SerpAPI/Google Custom Search)  ← 新增
    ↓
内容提取与解析
    ↓
智能分类
    ├─ tech
    ├─ crypto
    ├─ blockchain
    └─ ...
    ↓
质量过滤与评分
    ├─ 关键词过滤
    ├─ 来源可信度
    └─ 内容完整性
    ↓
返回结构化结果
```

## 成本对比

| 方案 | 免费额度 | 成本 | 优势 | 劣势 |
|------|----------|------|------|------|
| **MiniMax Agent 辅助** | 无限制* | 按 MiniMax 计费 | 最简单，无需配置 | 需要在 MCP 客户端中使用 |
| **SerpAPI** | 100次/月 | $50/月（5000次） | 多引擎支持 | 有配额限制 |
| **Google Custom Search** | 100次/天 | $5/千次 | Google 官方 | 配额较少 |
| **Bing Search API** | 1000次/月 | 按量计费 | 微软官方 | 需要 Azure 账号 |

*注：MiniMax Agent 使用按 MiniMax 平台计费规则计费

## 推荐配置

### 个人使用
```bash
# 使用免费源 + MiniMax Agent 辅助
# 无需额外配置
```

### 小型项目
```bash
# 配置 SerpAPI（免费额度通常够用）
export SERPAPI_KEY="your_key"
```

### 企业部署
```bash
# 多引擎配置，提高可用性
export NEWSAPI_KEY="your_newsapi_key"
export SERPAPI_KEY="your_serpapi_key"
export BING_API_KEY="your_bing_key"
```

## 环境变量配置

在 `.env` 文件中添加：

```bash
# 搜索引擎 API（选择一个）
SERPAPI_KEY=your_serpapi_key
# 或
GOOGLE_SEARCH_API_KEY=your_google_key
GOOGLE_SEARCH_ENGINE_ID=your_engine_id
# 或
BING_SEARCH_API_KEY=your_bing_key
```

## 测试

```bash
# 测试 SerpAPI 集成
python -c "
import os
os.environ['SERPAPI_KEY'] = 'your_key'

from src.news_tools import NewsSearcher
import asyncio

async def test():
    searcher = NewsSearcher()
    results = await searcher.search_news(keywords='人工智能', max_results=10)
    print(f'找到 {len(results)} 条新闻')
    for news in results[:3]:
        print(f'- {news[\"title\"]}')

asyncio.run(test())
"
```

## 总结

通过以上方案，你的 MCP 服务可以在**没有专门新闻 API key** 的情况下，通过搜索引擎获取全网新闻，实现：

✅ 关键词搜索  
✅ 内容提取  
✅ 智能分类  
✅ 质量过滤  
✅ 结构化输出  

选择最适合你需求的方案即可！
