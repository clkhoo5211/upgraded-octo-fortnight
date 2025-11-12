# ✅ 完整功能说明

## 🎯 你现在可以做什么？

### ✅ 1. 拉取和爬虫全网所有类型的最新热门新闻

**支持的新闻源：**
- ✅ NewsAPI.org（全球新闻）
- ✅ Google News RSS（免费）
- ✅ Bing News Search
- ✅ SerpAPI（Google/Bing/百度/Yahoo）
- ✅ Hacker News（技术新闻）
- ✅ Product Hunt（产品发布）
- ✅ 自定义RSS/JSON源

**支持的分类：**
- 政治 (politics)
- 财经 (finance)
- 加密货币 (crypto)
- 区块链 (blockchain)
- 风水 (fengshui)
- 科技 (tech)
- 社会 (social)
- 国际 (international)

**API端点：**
```bash
# 搜索新闻
POST /api/search
{
  "keywords": "AI",
  "categories": ["tech", "finance"],
  "languages": "all",
  "date_range": "last_7_days",
  "max_results": 50
}
```

### ✅ 2. 进行归类、分类、筛选

**智能过滤功能：**
- ✅ 关键词纳入/排除规则
- ✅ 域名白名单/黑名单
- ✅ 内容质量评分
- ✅ 垃圾内容识别
- ✅ 长度限制

**自动分类：**
- ✅ 基于关键词智能匹配分类
- ✅ 支持自定义分类关键词
- ✅ 多语言分类支持

### ✅ 3. 规则性创建MD文档保存

**保存格式：**
- ✅ Markdown格式（`.md`）
- ✅ 包含HTML代码块（`md_with_html`）
- ✅ 包含XML代码块（`md_with_xml`）

**文件结构：**
```
YYYY/MM/DD/
  ├── politics.md      # 政治新闻
  ├── finance.md       # 财经新闻
  ├── tech.md          # 科技新闻
  └── ...
```

**保存内容包含：**
- ✅ 标题、来源、时间
- ✅ 摘要和正文
- ✅ 图片链接
- ✅ 视频链接
- ✅ HTML原始内容
- ✅ 原文链接

### ✅ 4. 保存HTML Body、图片、动态图、视频链接

**下载的内容：**
- ✅ **HTML Body**：完整的HTML原始内容
- ✅ **图片**：所有图片的URL链接
- ✅ **横幅**：主要横幅图片
- ✅ **视频**：YouTube、Vimeo、MP4等视频链接

**支持的视频源：**
- ✅ YouTube（iframe）
- ✅ Vimeo（iframe）
- ✅ MP4直接链接
- ✅ 视频标签（video tag）
- ✅ 数据属性（data-video-url）

**API端点：**
```bash
# 下载完整内容
POST /api/download
{
  "news_url": "https://example.com/article",
  "include_images": true,
  "include_banners": true
}
```

## 🚀 完整归档API（推荐使用）

**一键完成所有操作：搜索 → 下载 → 分类 → 保存**

```bash
POST /api/archive
{
  "keywords": "AI technology",
  "categories": ["tech", "finance"],
  "languages": "all",
  "date_range": "last_7_days",
  "max_results": 50,
  "download_content": true,      # 下载完整内容（HTML、图片、视频）
  "save_to_github": true,        # 保存到GitHub
  "save_format": "md_with_html", # 保存格式
  "target_date": "2025-11-12"    # 目标日期（可选）
}
```

**返回结果：**
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

## 📝 使用示例

### 示例1: 搜索并下载科技新闻

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/archive \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "artificial intelligence",
    "categories": ["tech"],
    "languages": "en",
    "max_results": 20,
    "download_content": true,
    "save_to_github": false
  }'
```

### 示例2: 完整归档到GitHub

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/archive \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": "区块链",
    "categories": ["blockchain", "crypto"],
    "languages": "zh",
    "max_results": 50,
    "download_content": true,
    "save_to_github": true,
    "save_format": "md_with_html"
  }'
```

## 🔧 环境变量配置

**必需：**
- `GITHUB_TOKEN` - GitHub Personal Access Token（用于保存到GitHub）

**可选（增强功能）：**
- `NEWSAPI_KEY` - NewsAPI.org密钥
- `BING_API_KEY` - Bing Search API密钥
- `SERPAPI_KEY` - SerpAPI密钥
- `ENABLE_NEWS_FILTER=true` - 启用智能过滤

## 📊 功能对比

| 功能 | 搜索API | 下载API | 归档API |
|------|---------|---------|---------|
| 搜索新闻 | ✅ | ❌ | ✅ |
| 下载内容 | ❌ | ✅ | ✅ |
| 提取HTML | ❌ | ✅ | ✅ |
| 提取图片 | ❌ | ✅ | ✅ |
| 提取视频 | ❌ | ✅ | ✅ |
| 自动分类 | ✅ | ❌ | ✅ |
| 保存到GitHub | ❌ | ❌ | ✅ |

## 🎉 总结

**你现在可以：**
1. ✅ 拉取全网最新热门新闻
2. ✅ 自动分类和筛选
3. ✅ 下载完整内容（HTML、图片、视频）
4. ✅ 自动保存为MD文档到GitHub
5. ✅ 按日期和分类组织文件结构

**所有功能都已集成在 `/api/archive` 端点中！**

