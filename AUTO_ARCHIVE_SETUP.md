# 自动归档设置指南

## 🎯 功能说明

系统现在默认只搜索**当日和前一日的新闻**，并支持自动将**前一日的内容转换为MD文档并保存**。

## ✅ 已实现的改进

### 1. 默认日期范围改为当日和前一日

- **之前**: 默认搜索最近7天的新闻
- **现在**: 默认搜索当日和前一日的新闻 (`today_and_yesterday`)
- **效果**: 只获取最新、最相关的新闻，不包含历史热门热搜

### 2. 移除历史热门热搜

- Hacker News等源现在只在搜索当日和前一日新闻时启用
- 不再返回历史热门内容

### 3. 自动归档功能

系统提供两种方式自动归档前一日新闻：

## 🚀 方式1: Vercel Cron（推荐）

### 设置步骤

1. **已自动配置**: `vercel.json` 中已添加Cron配置
   ```json
   "crons": [
     {
       "path": "/api/auto_archive",
       "schedule": "0 1 * * *"  // 每天凌晨1点（UTC时间）
     }
   ]
   ```

2. **设置环境变量**（在Vercel Dashboard）:
   - `GITHUB_TOKEN` - GitHub Personal Access Token（必需）
   - `NEWSAPI_KEY` - 可选
   - `BING_API_KEY` - 可选
   - `ENABLE_NEWS_FILTER=true` - 推荐

3. **自动执行**: Vercel会在每天凌晨1点（UTC时间）自动调用 `/api/auto_archive`

### 自定义执行时间

修改 `vercel.json` 中的 `schedule`:
- `"0 1 * * *"` - 每天凌晨1点（UTC）
- `"0 9 * * *"` - 每天上午9点（UTC，对应北京时间17点）
- `"0 0 * * *"` - 每天午夜（UTC）

### 手动触发

访问: `https://upgraded-octo-fortnight.vercel.app/api/auto_archive`

## 🚀 方式2: GitHub Actions

### 设置步骤

1. **工作流已创建**: `.github/workflows/daily-archive.yml`

2. **设置Secrets**（在GitHub仓库Settings > Secrets）:
   - `GITHUB_TOKEN` - 使用默认的 `${{ secrets.GITHUB_TOKEN }}` 即可
   - `NEWSAPI_KEY` - 可选
   - `BING_API_KEY` - 可选
   - `ENABLE_NEWS_FILTER` - 可选，默认true

3. **自动执行**: GitHub Actions会在每天凌晨1点（UTC时间）自动执行

### 手动触发

在GitHub仓库的Actions标签页，找到 "Daily News Archive" 工作流，点击 "Run workflow"

## 📊 API端点说明

### `/api/auto_archive`

**功能**: 自动归档前一日新闻到GitHub

**请求方式**: GET（由Cron调用）

**查询参数**:
- `categories` - 要归档的分类（逗号分隔），默认所有分类
- `languages` - 语言（zh/en/all），默认all
- `max_results` - 最大新闻数，默认100
- `download_content` - 是否下载完整内容（true/false），默认true
- `save_format` - 保存格式（md_with_html/md_with_xml），默认md_with_html

**示例**:
```
GET /api/auto_archive?categories=tech,finance&max_results=50
```

**响应示例**:
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

## 📝 保存的文件结构

归档的文件会保存在GitHub仓库中：

```
YYYY/MM/DD/
  ├── politics.md      # 政治新闻
  ├── finance.md       # 财经新闻
  ├── tech.md          # 科技新闻
  ├── crypto.md        # 加密货币新闻
  └── ...
```

每个MD文件包含：
- ✅ 标题、来源、时间
- ✅ 摘要和正文
- ✅ 图片链接
- ✅ 视频链接
- ✅ HTML原始内容
- ✅ 原文链接

## ⚙️ 配置选项

### 修改执行时间

**Vercel Cron**: 修改 `vercel.json` 中的 `schedule`
**GitHub Actions**: 修改 `.github/workflows/daily-archive.yml` 中的 `cron`

### 修改归档分类

**方式1**: 修改API调用参数
```
GET /api/auto_archive?categories=tech,finance,gaming
```

**方式2**: 修改GitHub Actions工作流中的 `categories=None` 为具体分类列表

### 修改归档语言

```
GET /api/auto_archive?languages=zh
```

## 🔍 验证归档

### 检查GitHub仓库

1. 访问你的GitHub仓库
2. 查看是否有新的日期目录（如 `2025/11/11/`）
3. 检查MD文件是否已创建

### 查看日志

**Vercel**:
1. 访问 Vercel Dashboard
2. 进入项目 → Functions → 查看 `auto_archive` 函数的日志

**GitHub Actions**:
1. 访问 GitHub仓库 → Actions标签
2. 查看 "Daily News Archive" 工作流的运行日志

## ⚠️ 注意事项

1. **时区**: Cron使用UTC时间，注意时区转换
2. **API限制**: 注意各API的调用频率限制
3. **GitHub Token**: 确保有写入仓库的权限
4. **存储空间**: 长期归档会占用GitHub仓库空间

## 🎉 总结

现在系统会：
1. ✅ 默认只搜索当日和前一日的新闻
2. ✅ 自动在每天凌晨归档前一日新闻
3. ✅ 将新闻转换为MD文档保存到GitHub
4. ✅ 包含完整内容（HTML、图片、视频链接）

设置完成后，系统会自动每天归档前一日新闻，无需手动操作！

