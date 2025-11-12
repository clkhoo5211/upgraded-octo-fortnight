# 关键词优化工具使用指南

## 🎯 功能说明

关键词优化工具可以从多个搜索引擎和社交平台自动抓取关键词，扩展和优化现有的关键词列表，提高新闻分类的准确性。

## 🔍 支持的搜索源

### 搜索引擎
- ✅ **Google News** - 通过SerpAPI或Google Custom Search API
- ✅ **Bing News** - 通过Bing Search API

### 社交平台
- ✅ **Reddit** - 从多个subreddit搜索
- ✅ **Hacker News** - 技术社区搜索
- ✅ **Twitter** - 通过Twitter API v2（需要Bearer Token）

## 📊 工作原理

1. **基础关键词搜索**: 对每个分类的基础关键词进行搜索
2. **多源抓取**: 从Google News、Bing News、Reddit、Hacker News等源抓取相关内容
3. **关键词提取**: 从标题、描述、正文中提取高频关键词
4. **频率统计**: 统计关键词出现频率
5. **智能筛选**: 排除停用词，选择高频、相关的新关键词
6. **自动扩展**: 将新关键词添加到对应分类

## 🚀 API使用

### 1. 获取当前关键词统计

```bash
GET /api/optimize_keywords
```

**响应示例:**
```json
{
  "total_categories": 8,
  "categories": {
    "tech": {
      "keyword_count": 120,
      "sample_keywords": ["科技", "技术", "AI", "人工智能", ...]
    },
    ...
  }
}
```

### 2. 优化关键词

```bash
POST /api/optimize_keywords
Content-Type: application/json

{
  "categories": ["tech", "finance"],  // 可选：指定要优化的分类，不指定则优化全部
  "max_new_per_category": 50,         // 每个分类最大新关键词数量
  "search_sources": ["google", "bing", "reddit", "hackernews"]  // 搜索源
}
```

**响应示例:**
```json
{
  "success": true,
  "optimized_categories": 2,
  "results": {
    "tech": {
      "category": "tech",
      "original_count": 120,
      "new_keywords": ["GPT-4", "ChatGPT", "LLM", "transformer", ...],
      "total_count": 170,
      "optimized_keywords": [...]
    },
    "finance": {
      "category": "finance",
      "original_count": 80,
      "new_keywords": ["Fed", "interest rate", "inflation", ...],
      "total_count": 130,
      "optimized_keywords": [...]
    }
  },
  "summary": {
    "total_original_keywords": 200,
    "total_new_keywords": 100,
    "total_final_keywords": 300,
    "improvement_rate": "50.0%"
  }
}
```

## 💡 使用示例

### 示例1: 优化所有分类

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/optimize_keywords \
  -H "Content-Type: application/json" \
  -d '{
    "max_new_per_category": 30
  }'
```

### 示例2: 只优化科技和财经分类

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/optimize_keywords \
  -H "Content-Type: application/json" \
  -d '{
    "categories": ["tech", "finance"],
    "max_new_per_category": 50
  }'
```

### 示例3: 查看当前关键词统计

```bash
curl https://upgraded-octo-fortnight.vercel.app/api/optimize_keywords
```

## 🔧 环境变量配置

**必需（用于搜索）:**
- `SERPAPI_KEY` - SerpAPI密钥（推荐，支持多个搜索引擎）
- 或 `BING_API_KEY` - Bing Search API密钥
- 或 `GOOGLE_SEARCH_API_KEY` + `GOOGLE_SEARCH_ENGINE_ID` - Google Custom Search

**可选:**
- `TWITTER_BEARER_TOKEN` - Twitter API Bearer Token（用于Twitter搜索）

## 📝 关键词提取规则

### 英文关键词
- 长度: 2-30个字符
- 排除: 常见停用词（the, a, an, is, are等）
- 提取: 标题、描述、正文中的高频词

### 中文关键词
- 长度: 2-10个字符
- 提取: 标题、描述、正文中的中文词组

### 特殊格式
- 数字+字母组合: 5G, AI, Web3等
- 缩写: NFT, DeFi, API等

## 🎯 优化策略

1. **频率优先**: 优先选择出现频率高的关键词
2. **相关性**: 基于基础关键词搜索，确保新关键词相关
3. **去重**: 自动排除已有关键词
4. **质量过滤**: 排除停用词和无关词汇

## ⚠️ 注意事项

1. **API限制**: 注意各API的调用频率限制
2. **成本**: SerpAPI等付费API会产生费用
3. **时间**: 优化过程可能需要几分钟
4. **结果验证**: 建议手动检查新关键词的质量

## 🔄 自动优化流程

可以设置定时任务自动优化关键词：

1. 每周运行一次关键词优化
2. 将优化结果保存到文件
3. 手动审核后更新到代码库

## 📊 优化效果

优化后可以：
- ✅ 提高新闻分类准确性
- ✅ 覆盖更多相关话题
- ✅ 跟上最新趋势和术语
- ✅ 支持多语言关键词扩展

## 🎉 总结

关键词优化工具可以：
1. 自动从多个源抓取关键词
2. 智能筛选和扩展关键词列表
3. 提高新闻分类的准确性和覆盖率
4. 跟上最新趋势和术语

通过定期运行优化工具，可以保持关键词列表的时效性和准确性！

