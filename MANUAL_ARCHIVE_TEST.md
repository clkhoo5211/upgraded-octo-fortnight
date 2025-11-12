# 手动归档测试指南

## 🎯 通过Vercel链接测试归档功能

是的，可以通过 https://upgraded-octo-fortnight.vercel.app/ 链接进行API手动归档测试！

## 📋 可用的归档API端点

### 1. `/api/archive` - 完整归档API（推荐）

**功能**: 搜索 → 下载 → 分类 → 保存到GitHub（一键完成）

**请求方式**: POST

**URL**: `https://upgraded-octo-fortnight.vercel.app/api/archive`

**请求体示例**:
```json
{
  "keywords": "technology",
  "categories": ["tech", "finance"],
  "max_results": 10,
  "download_content": true,
  "save_to_github": true,
  "save_format": "md_with_html"
}
```

**参数说明**:
- `keywords` - 搜索关键词（可选）
- `categories` - 分类列表（可选，默认所有分类）
- `max_results` - 最大新闻数（默认50）
- `download_content` - 是否下载完整内容（默认true）
- `save_to_github` - 是否保存到GitHub（默认false）
- `save_format` - 保存格式：`md_with_html` 或 `md_with_xml`（默认md_with_html）

**响应示例**:
```json
{
  "success": true,
  "search_results": {
    "count": 10,
    "news": [...]
  },
  "download_enabled": true,
  "github_save_enabled": true,
  "saved_files": [
    "2025/11/12/tech.md",
    "2025/11/12/finance.md"
  ],
  "summary": {
    "total_news": 10,
    "with_content": 8,
    "with_html": 8,
    "with_images": 5,
    "with_videos": 2,
    "categories": {
      "tech": 6,
      "finance": 4
    }
  }
}
```

### 2. `/api/auto_archive` - 自动归档API（手动触发）

**功能**: 自动归档前一日新闻（由Vercel Cron调用，也可手动触发）

**请求方式**: GET

**URL**: `https://upgraded-octo-fortnight.vercel.app/api/auto_archive`

**查询参数**:
- `categories` - 分类（逗号分隔，可选）
- `languages` - 语言（zh/en/all，默认all）
- `max_results` - 最大新闻数（默认100）
- `download_content` - 是否下载内容（true/false，默认true）
- `save_format` - 保存格式（默认md_with_html）

**示例**:
```
https://upgraded-octo-fortnight.vercel.app/api/auto_archive?max_results=10
```

## 🧪 测试命令

### 测试1: 完整归档（保存到GitHub）

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/archive \
  -H "Content-Type: application/json" \
  -d '{
    "max_results": 5,
    "download_content": true,
    "save_to_github": true
  }'
```

### 测试2: 完整归档（不保存到GitHub，只测试功能）

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/archive \
  -H "Content-Type: application/json" \
  -d '{
    "max_results": 5,
    "download_content": true,
    "save_to_github": false
  }'
```

### 测试3: 搜索特定分类并归档

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/archive \
  -H "Content-Type: application/json" \
  -d '{
    "categories": ["tech", "finance"],
    "max_results": 10,
    "download_content": true,
    "save_to_github": true
  }'
```

### 测试4: 手动触发自动归档

```bash
curl "https://upgraded-octo-fortnight.vercel.app/api/auto_archive?max_results=5"
```

## 🔍 验证文件是否创建

### 方法1: 检查API返回

查看响应中的 `saved_files` 字段：

```json
{
  "saved_files": [
    "2025/11/12/tech.md",
    "2025/11/12/finance.md"
  ]
}
```

如果 `saved_files` 为空，检查 `errors` 字段。

### 方法2: 在GitHub仓库查看

1. 访问：https://github.com/clkhoo5211/upgraded-octo-fortnight
2. 浏览到对应的日期目录：`2025/11/12/`
3. 查看是否有对应的MD文件

### 方法3: 使用GitHub API查看

```bash
# 查看2025年目录
curl https://api.github.com/repos/clkhoo5211/upgraded-octo-fortnight/contents/2025

# 查看具体文件
curl https://api.github.com/repos/clkhoo5211/upgraded-octo-fortnight/contents/2025/11/12/tech.md
```

## ⚠️ 注意事项

### 如果没有设置GITHUB_TOKEN

- `save_to_github: true` 会失败
- API会返回错误信息
- 文件不会创建

**解决方案**: 在Vercel Dashboard设置 `GITHUB_TOKEN` 环境变量

### 如果设置了GITHUB_TOKEN

- 文件会保存到GitHub仓库
- 路径格式：`YYYY/MM/DD/分类.md`
- 可以在GitHub仓库中查看

## 📊 测试结果示例

### 成功情况

```json
{
  "success": true,
  "saved_files": [
    "2025/11/12/tech.md",
    "2025/11/12/finance.md"
  ],
  "summary": {
    "total_news": 10,
    "with_content": 8,
    "with_html": 8,
    "with_images": 5
  }
}
```

### 失败情况（没有GITHUB_TOKEN）

```json
{
  "success": false,
  "saved_files": [],
  "errors": [
    {
      "error": "GITHUB_TOKEN未设置，跳过GitHub归档"
    }
  ]
}
```

## 🎯 快速测试

最简单的测试命令：

```bash
# 测试归档功能（不保存到GitHub）
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/archive \
  -H "Content-Type: application/json" \
  -d '{"max_results":3,"download_content":true,"save_to_github":false}'
```

## 📝 总结

✅ **可以通过** https://upgraded-octo-fortnight.vercel.app/ 链接进行API手动归档测试

**推荐使用**:
- `/api/archive` - 完整归档功能（POST方式）
- `/api/auto_archive` - 自动归档（GET方式，手动触发）

**文件位置**: GitHub仓库的 `YYYY/MM/DD/分类.md` 路径

**前提条件**: 需要设置 `GITHUB_TOKEN` 环境变量才能保存文件到GitHub

