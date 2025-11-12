# Global News Aggregator API 使用指南

## 🌐 API 基础信息

**API地址**: `https://upgraded-octo-fortnight.vercel.app`

**版本**: 1.0.0

**状态**: 在线 ✅

**CORS**: 已启用，支持跨域请求

**格式**: JSON

---

## 📋 所有可用端点

### 基础端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | API首页，查看服务信息和端点列表 |
| `/api/health` | GET | 健康检查，查看配置状态和可用源 |
| `/api/test` | GET | 简单测试端点 |

### 核心功能端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/search` | GET/POST | 搜索全网新闻 |
| `/api/download` | GET/POST | 下载新闻完整内容（HTML、图片、视频） |
| `/api/archive` | POST | 完整归档API（搜索+下载+保存到GitHub） |
| `/api/auto_archive` | GET | 自动归档前一日新闻 |

### 管理端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/manage_categories` | GET | 查看所有分类 |
| `/api/manage_categories` | POST | 添加/更新分类 |
| `/api/manage_categories` | DELETE | 删除分类 |
| `/api/optimize_keywords` | GET | 查看关键词统计 |

---

## 🔍 端点详细说明

### 1. `/` - API首页

**方法**: GET

**URL**: `https://upgraded-octo-fortnight.vercel.app/`

**说明**: 返回API服务信息、可用端点和配置状态

**响应示例**:
```json
{
  "service": "Global News Aggregator API",
  "version": "1.0.0",
  "status": "online",
  "config": {
    "NEWSAPI_KEY": false,
    "BING_API_KEY": false,
    "NEWSDATA_KEY": false,
    "SERPAPI_KEY": false,
    "GOOGLE_SEARCH_API_KEY": false
  },
  "available_sources": [
    "Hacker News API",
    "Google News RSS",
    "Product Hunt GraphQL"
  ],
  "endpoints": {
    "/": "GET - API首页",
    "/api/search": "POST/GET - 搜索全网新闻",
    "/api/download": "POST/GET - 下载新闻完整内容",
    "/api/health": "GET - 健康检查"
  }
}
```

---

### 2. `/api/health` - 健康检查

**方法**: GET

**URL**: `https://upgraded-octo-fortnight.vercel.app/api/health`

**说明**: 检查API健康状态和配置

**响应示例**:
```json
{
  "status": "healthy",
  "config": {
    "NEWSAPI_KEY": false,
    "BING_API_KEY": false
  },
  "available_sources": [
    "Hacker News API",
    "Google News RSS"
  ]
}
```

---

### 3. `/api/search` - 搜索新闻

**方法**: GET 或 POST

**URL**: `https://upgraded-octo-fortnight.vercel.app/api/search`

#### GET 请求示例

```bash
curl "https://upgraded-octo-fortnight.vercel.app/api/search?keywords=AI&categories=tech&max_results=10&date_range=today_and_yesterday"
```

#### POST 请求示例

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "artificial intelligence",
    "categories": ["tech", "finance"],
    "languages": "en",
    "date_range": "today_and_yesterday",
    "max_results": 50
  }'
```

#### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `keywords` | string | 否 | null | 搜索关键词 |
| `categories` | array | 否 | 所有分类 | 分类列表：`["tech", "finance", "politics", "crypto", "blockchain", "fengshui", "social", "international"]` |
| `languages` | string | 否 | "all" | 语言：`"zh"`, `"en"`, `"all"` |
| `date_range` | string | 否 | "today_and_yesterday" | 日期范围：`"today_and_yesterday"`, `"today"`, `"yesterday"`, `"last_7_days"`, `"last_30_days"` |
| `max_results` | integer | 否 | 50 | 最大结果数 |

#### 响应示例

```json
{
  "success": true,
  "count": 10,
  "news": [
    {
      "title": "AI Breakthrough in Healthcare",
      "description": "Scientists develop new AI system...",
      "url": "https://example.com/news/ai-healthcare",
      "source": "Tech News",
      "published_at": "2025-11-12T10:00:00Z",
      "image_url": "https://example.com/image.jpg",
      "language": "en",
      "category": "tech"
    }
  ],
  "search_params": {
    "keywords": "artificial intelligence",
    "categories": ["tech", "finance"],
    "languages": "en",
    "date_range": "today_and_yesterday",
    "max_results": 50
  }
}
```

---

### 4. `/api/download` - 下载新闻内容

**方法**: GET 或 POST

**URL**: `https://upgraded-octo-fortnight.vercel.app/api/download`

#### POST 请求示例

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/download \
  -H "Content-Type: application/json" \
  -d '{
    "news_url": "https://example.com/article",
    "include_images": true,
    "include_banners": true
  }'
```

#### GET 请求示例

```bash
curl "https://upgraded-octo-fortnight.vercel.app/api/download?news_url=https://example.com/article&include_images=true"
```

#### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `news_url` | string | **是** | - | 新闻文章URL |
| `include_images` | boolean | 否 | true | 是否包含图片 |
| `include_banners` | boolean | 否 | true | 是否包含横幅图片 |

#### 响应示例

```json
{
  "success": true,
  "url": "https://example.com/article",
  "content": "文章正文内容...",
  "html_body": "<body>...</body>",
  "images": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ],
  "banners": [
    "https://example.com/banner.jpg"
  ],
  "videos": [
    {
      "url": "https://www.youtube.com/watch?v=xxx",
      "type": "youtube"
    }
  ]
}
```

---

### 5. `/api/archive` - 完整归档API（推荐）

**方法**: POST

**URL**: `https://upgraded-octo-fortnight.vercel.app/api/archive`

**说明**: 一键完成搜索、下载和保存到GitHub

#### 请求示例

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/archive \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "technology",
    "categories": ["tech", "finance"],
    "languages": "all",
    "date_range": "today_and_yesterday",
    "max_results": 50,
    "download_content": true,
    "save_to_github": true,
    "save_format": "md_with_html",
    "target_date": "2025-11-12"
  }'
```

#### 请求参数

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `keywords` | string | 否 | null | 搜索关键词 |
| `categories` | array | 否 | 所有分类 | 分类列表 |
| `languages` | string | 否 | "all" | 语言 |
| `date_range` | string | 否 | "last_7_days" | 日期范围 |
| `max_results` | integer | 否 | 50 | 最大结果数 |
| `download_content` | boolean | 否 | true | 是否下载完整内容 |
| `save_to_github` | boolean | 否 | false | 是否保存到GitHub（需要GITHUB_TOKEN） |
| `save_format` | string | 否 | "md_with_html" | 保存格式：`"md_with_html"` 或 `"md_with_xml"` |
| `target_date` | string | 否 | 今天 | 目标日期（YYYY-MM-DD） |

#### 响应示例

```json
{
  "success": true,
  "search_results": {
    "count": 50,
    "news": [...]
  },
  "download_enabled": true,
  "github_save_enabled": true,
  "saved_files": [
    "2025/11/12/tech.md",
    "2025/11/12/finance.md"
  ],
  "summary": {
    "total_news": 50,
    "with_content": 48,
    "with_html": 48,
    "with_images": 45,
    "with_videos": 12,
    "categories": {
      "tech": 30,
      "finance": 20
    }
  }
}
```

---

### 6. `/api/auto_archive` - 自动归档

**方法**: GET

**URL**: `https://upgraded-octo-fortnight.vercel.app/api/auto_archive`

**说明**: 自动归档前一日新闻（由Vercel Cron调用，也可手动触发）

#### 请求示例

```bash
curl "https://upgraded-octo-fortnight.vercel.app/api/auto_archive?categories=tech,finance&max_results=100&download_content=true"
```

#### 查询参数

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `categories` | string | 否 | 所有分类 | 分类（逗号分隔） |
| `languages` | string | 否 | "all" | 语言 |
| `max_results` | integer | 否 | 100 | 最大结果数 |
| `download_content` | boolean | 否 | true | 是否下载内容 |
| `save_format` | string | 否 | "md_with_html" | 保存格式 |

#### 响应示例

```json
{
  "success": true,
  "message": "前一日(2025-11-11)新闻归档完成",
  "date": "2025-11-11",
  "news_count": 45,
  "saved_files": [
    "2025/11/11/tech.md",
    "2025/11/11/finance.md"
  ],
  "summary": {
    "total_news": 45,
    "with_content": 42,
    "with_html": 42,
    "with_images": 38,
    "with_videos": 5,
    "categories": {
      "tech": 25,
      "finance": 20
    }
  }
}
```

---

### 7. `/api/manage_categories` - 分类管理

#### GET - 查看所有分类

```bash
curl "https://upgraded-octo-fortnight.vercel.app/api/manage_categories"
```

#### POST - 添加/更新分类

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/manage_categories \
  -H "Content-Type: application/json" \
  -d '{
    "category": "gaming",
    "keywords": ["game", "gaming", "video game", "esports"]
  }'
```

#### DELETE - 删除分类

```bash
curl -X DELETE https://upgraded-octo-fortnight.vercel.app/api/manage_categories \
  -H "Content-Type: application/json" \
  -d '{
    "category": "gaming"
  }'
```

---

### 8. `/api/optimize_keywords` - 关键词优化

**方法**: GET

**URL**: `https://upgraded-octo-fortnight.vercel.app/api/optimize_keywords`

**说明**: 查看关键词统计信息

---

## 💻 代码示例

### Python 示例

```python
import requests
import json

API_BASE = "https://upgraded-octo-fortnight.vercel.app"

# 1. 搜索新闻
def search_news(keywords=None, categories=None, max_results=50):
    url = f"{API_BASE}/api/search"
    payload = {
        "keywords": keywords,
        "categories": categories,
        "date_range": "today_and_yesterday",
        "max_results": max_results
    }
    response = requests.post(url, json=payload)
    return response.json()

# 2. 下载新闻内容
def download_news(news_url):
    url = f"{API_BASE}/api/download"
    payload = {
        "news_url": news_url,
        "include_images": True,
        "include_banners": True
    }
    response = requests.post(url, json=payload)
    return response.json()

# 3. 完整归档
def archive_news(keywords=None, categories=None, save_to_github=False):
    url = f"{API_BASE}/api/archive"
    payload = {
        "keywords": keywords,
        "categories": categories,
        "max_results": 50,
        "download_content": True,
        "save_to_github": save_to_github,
        "save_format": "md_with_html"
    }
    response = requests.post(url, json=payload)
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 搜索科技新闻
    results = search_news(keywords="AI", categories=["tech"], max_results=10)
    print(f"找到 {results['count']} 条新闻")
    
    # 下载第一条新闻的完整内容
    if results['news']:
        first_news = results['news'][0]
        content = download_news(first_news['url'])
        print(f"标题: {first_news['title']}")
        print(f"内容长度: {len(content.get('content', ''))}")
        print(f"图片数: {len(content.get('images', []))}")
    
    # 归档到GitHub（需要GITHUB_TOKEN）
    # archive_result = archive_news(categories=["tech"], save_to_github=True)
    # print(f"保存文件: {archive_result.get('saved_files', [])}")
```

### JavaScript/Node.js 示例

```javascript
const API_BASE = 'https://upgraded-octo-fortnight.vercel.app';

// 1. 搜索新闻
async function searchNews(keywords, categories, maxResults = 50) {
  const response = await fetch(`${API_BASE}/api/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      keywords: keywords,
      categories: categories,
      date_range: 'today_and_yesterday',
      max_results: maxResults
    })
  });
  return await response.json();
}

// 2. 下载新闻内容
async function downloadNews(newsUrl) {
  const response = await fetch(`${API_BASE}/api/download`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      news_url: newsUrl,
      include_images: true,
      include_banners: true
    })
  });
  return await response.json();
}

// 3. 完整归档
async function archiveNews(keywords, categories, saveToGitHub = false) {
  const response = await fetch(`${API_BASE}/api/archive`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      keywords: keywords,
      categories: categories,
      max_results: 50,
      download_content: true,
      save_to_github: saveToGitHub,
      save_format: 'md_with_html'
    })
  });
  return await response.json();
}

// 使用示例
(async () => {
  // 搜索科技新闻
  const results = await searchNews('AI', ['tech'], 10);
  console.log(`找到 ${results.count} 条新闻`);
  
  // 下载第一条新闻
  if (results.news && results.news.length > 0) {
    const firstNews = results.news[0];
    const content = await downloadNews(firstNews.url);
    console.log(`标题: ${firstNews.title}`);
    console.log(`内容长度: ${content.content?.length || 0}`);
    console.log(`图片数: ${content.images?.length || 0}`);
  }
})();
```

### curl 示例

```bash
#!/bin/bash

API_BASE="https://upgraded-octo-fortnight.vercel.app"

# 1. 搜索新闻
search_news() {
  curl -X POST "${API_BASE}/api/search" \
    -H "Content-Type: application/json" \
    -d '{
      "keywords": "AI",
      "categories": ["tech"],
      "date_range": "today_and_yesterday",
      "max_results": 10
    }'
}

# 2. 下载新闻内容
download_news() {
  local url="$1"
  curl -X POST "${API_BASE}/api/download" \
    -H "Content-Type: application/json" \
    -d "{
      \"news_url\": \"${url}\",
      \"include_images\": true,
      \"include_banners\": true
    }"
}

# 3. 完整归档
archive_news() {
  curl -X POST "${API_BASE}/api/archive" \
    -H "Content-Type: application/json" \
    -d '{
      "keywords": "technology",
      "categories": ["tech"],
      "max_results": 50,
      "download_content": true,
      "save_to_github": false,
      "save_format": "md_with_html"
    }'
}

# 使用示例
echo "搜索新闻..."
search_news | jq '.count'

echo "归档新闻..."
archive_news | jq '.saved_files'
```

---

## 🔧 GitHub Actions 使用示例

### 示例1: 每天自动归档新闻

```yaml
name: Daily News Archive

on:
  schedule:
    # 每天UTC时间1点执行（北京时间9点）
    - cron: '0 1 * * *'
  workflow_dispatch: # 允许手动触发

jobs:
  archive:
    runs-on: ubuntu-latest
    steps:
      - name: Archive yesterday's news
        run: |
          curl -X GET "https://upgraded-octo-fortnight.vercel.app/api/auto_archive?max_results=100&download_content=true" \
            -H "Accept: application/json" \
            | jq '.'
```

### 示例2: 搜索并保存特定分类新闻

```yaml
name: Archive Tech News

on:
  workflow_dispatch:
    inputs:
      categories:
        description: 'Categories (comma-separated)'
        required: true
        default: 'tech,finance'

jobs:
  archive:
    runs-on: ubuntu-latest
    steps:
      - name: Archive news
        run: |
          curl -X POST "https://upgraded-octo-fortnight.vercel.app/api/archive" \
            -H "Content-Type: application/json" \
            -d "{
              \"categories\": [\"${{ github.event.inputs.categories }}\"],
              \"max_results\": 50,
              \"download_content\": true,
              \"save_to_github\": false,
              \"save_format\": \"md_with_html\"
            }" | jq '.summary'
```

### 示例3: Python脚本调用API

```yaml
name: News Aggregator

on:
  schedule:
    - cron: '0 */6 * * *'  # 每6小时执行一次
  workflow_dispatch:

jobs:
  aggregate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install requests
      
      - name: Fetch and process news
        run: |
          python << 'EOF'
          import requests
          import json
          
          API_BASE = "https://upgraded-octo-fortnight.vercel.app"
          
          # 搜索新闻
          response = requests.post(
              f"{API_BASE}/api/search",
              json={
                  "categories": ["tech", "finance"],
                  "date_range": "today_and_yesterday",
                  "max_results": 20
              }
          )
          
          data = response.json()
          print(f"找到 {data['count']} 条新闻")
          
          # 保存结果
          with open('news_results.json', 'w', encoding='utf-8') as f:
              json.dump(data, f, ensure_ascii=False, indent=2)
          EOF
      
      - name: Commit results
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add news_results.json
          git commit -m "Update news results" || exit 0
          git push
```

---

## 📊 分类列表

### 默认分类

- `tech` - 科技
- `finance` - 财经
- `politics` - 政治
- `crypto` - 加密货币
- `blockchain` - 区块链
- `fengshui` - 风水
- `social` - 社会
- `international` - 国际

### 添加自定义分类

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/manage_categories \
  -H "Content-Type: application/json" \
  -d '{
    "category": "gaming",
    "keywords": ["game", "gaming", "video game", "esports"]
  }'
```

---

## ⚠️ 错误处理

### 错误响应格式

```json
{
  "success": false,
  "error": "错误描述",
  "traceback": "详细错误堆栈（开发环境）"
}
```

### 常见错误码

- `200` - 成功
- `400` - 请求参数错误
- `500` - 服务器内部错误

### 错误处理示例

```python
import requests

def safe_api_call(url, payload):
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None
    except ValueError as e:
        print(f"JSON解析错误: {e}")
        return None

# 使用
result = safe_api_call(
    "https://upgraded-octo-fortnight.vercel.app/api/search",
    {"max_results": 10}
)

if result and result.get('success'):
    print(f"成功: {result['count']} 条新闻")
else:
    print(f"失败: {result.get('error', '未知错误')}")
```

---

## 🔐 认证说明

### 公开API

大部分端点**不需要认证**，可以直接使用：

- `/api/search`
- `/api/download`
- `/api/health`
- `/api/manage_categories` (GET)

### 需要GitHub Token的端点

以下端点需要API服务端配置`GITHUB_TOKEN`（由API提供者配置，使用者无需提供）：

- `/api/archive` (当`save_to_github=true`时)
- `/api/auto_archive` (自动归档到GitHub)

**注意**: 这些端点的GitHub Token是在Vercel环境变量中配置的，API调用者不需要提供认证信息。

---

## 📝 最佳实践

### 1. 使用适当的日期范围

```python
# 推荐：只获取当日和前一日的新闻
date_range = "today_and_yesterday"

# 避免：获取过多历史数据
date_range = "last_30_days"  # 仅在需要时使用
```

### 2. 限制结果数量

```python
# 推荐：根据需求设置合理的数量
max_results = 50  # 或更少

# 避免：请求过多结果
max_results = 1000  # 可能导致超时
```

### 3. 错误处理和重试

```python
import time
import requests

def api_call_with_retry(url, payload, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避
                print(f"重试 {attempt + 1}/{max_retries}，等待 {wait_time} 秒...")
                time.sleep(wait_time)
            else:
                raise
```

### 4. 批量处理

```python
# 推荐：批量下载内容
urls = [news['url'] for news in news_list]
# 使用 /api/archive 端点，它会自动批量下载

# 避免：逐个调用 /api/download
for news in news_list:
    download_news(news['url'])  # 效率低
```

---

## 🚀 快速开始

### 最简单的使用示例

```python
import requests

# 搜索10条科技新闻
response = requests.post(
    "https://upgraded-octo-fortnight.vercel.app/api/search",
    json={
        "categories": ["tech"],
        "max_results": 10,
        "date_range": "today_and_yesterday"
    }
)

data = response.json()
print(f"找到 {data['count']} 条新闻")

for news in data['news']:
    print(f"- {news['title']}")
```

---

## 📚 更多资源

- **GitHub仓库**: https://github.com/clkhoo5211/upgraded-octo-fortnight
- **API地址**: https://upgraded-octo-fortnight.vercel.app
- **健康检查**: https://upgraded-octo-fortnight.vercel.app/api/health

---

## ❓ 常见问题

### Q: API有速率限制吗？

A: 目前没有严格的速率限制，但建议合理使用，避免过于频繁的请求。

### Q: 支持哪些语言？

A: 支持中文（zh）和英文（en），也可以设置为"all"获取所有语言。

### Q: 如何获取历史新闻？

A: 使用`date_range`参数，可选值：`"last_7_days"`, `"last_30_days"`等。

### Q: 可以保存到自己的GitHub仓库吗？

A: 目前保存功能使用API服务端配置的GitHub Token。如需保存到自己的仓库，可以：
1. 使用API获取数据
2. 在自己的代码中实现GitHub保存逻辑

### Q: 图片和视频是直接链接还是下载的？

A: API返回的是图片和视频的URL链接，不直接下载文件内容。

---

## 📞 支持

如有问题或建议，请访问GitHub仓库提交Issue。

