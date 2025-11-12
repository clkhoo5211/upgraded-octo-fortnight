# 分类管理功能使用指南

## 🎯 功能说明

分类管理器支持动态添加、删除、更新分类和关键词，无需修改代码即可扩展新闻分类系统。

## ✨ 主要功能

1. ✅ **添加新分类** - 创建全新的分类和关键词
2. ✅ **更新分类** - 修改现有分类的关键词
3. ✅ **合并关键词** - 向现有分类添加关键词而不覆盖
4. ✅ **删除分类** - 删除自定义分类
5. ✅ **删除关键词** - 从分类中移除特定关键词
6. ✅ **查看分类** - 查看所有分类和关键词统计

## 🚀 API使用

### 1. 查看所有分类

```bash
GET /api/manage_categories
```

**响应示例:**
```json
{
  "total_categories": 10,
  "default_categories": 8,
  "custom_categories": 2,
  "categories": {
    "tech": {
      "keyword_count": 120,
      "is_custom": false,
      "is_default": true,
      "sample_keywords": ["科技", "技术", "AI", ...]
    },
    "gaming": {
      "keyword_count": 45,
      "is_custom": true,
      "is_default": false,
      "sample_keywords": ["游戏", "电竞", "主机", ...]
    }
  }
}
```

### 2. 查看特定分类信息

```bash
GET /api/manage_categories?category=gaming
```

**响应示例:**
```json
{
  "exists": true,
  "category": "gaming",
  "is_custom": true,
  "is_default": false,
  "keyword_count": 45,
  "keywords": ["游戏", "电竞", "主机", ...],
  "default_keywords": [],
  "custom_keywords": ["游戏", "电竞", "主机", ...]
}
```

### 3. 添加新分类

```bash
POST /api/manage_categories
Content-Type: application/json

{
  "action": "add_category",
  "category": "gaming",
  "keywords": ["游戏", "电竞", "主机", "PC游戏", "手游", "游戏机", "PlayStation", "Xbox", "Nintendo", "Steam"],
  "merge": false
}
```

**响应示例:**
```json
{
  "success": true,
  "action": "created",
  "category": "gaming",
  "keyword_count": 10,
  "keywords": ["游戏", "电竞", "主机", ...]
}
```

### 4. 向现有分类添加关键词

```bash
POST /api/manage_categories
Content-Type: application/json

{
  "action": "add_keywords",
  "category": "gaming",
  "keywords": ["VR游戏", "AR游戏", "云游戏", "独立游戏"]
}
```

**响应示例:**
```json
{
  "success": true,
  "action": "keywords_added",
  "category": "gaming",
  "added_count": 4,
  "total_keywords": 14,
  "keywords": ["游戏", "电竞", ..., "VR游戏", "AR游戏", ...]
}
```

### 5. 更新分类（替换关键词）

```bash
PUT /api/manage_categories
Content-Type: application/json

{
  "category": "gaming",
  "keywords": ["游戏", "电竞", "主机", "新关键词1", "新关键词2"]
}
```

**响应示例:**
```json
{
  "success": true,
  "action": "updated",
  "category": "gaming",
  "keyword_count": 5,
  "keywords": ["游戏", "电竞", "主机", "新关键词1", "新关键词2"]
}
```

### 6. 删除分类

```bash
DELETE /api/manage_categories
Content-Type: application/json

{
  "action": "remove_category",
  "category": "gaming"
}
```

**响应示例:**
```json
{
  "success": true,
  "action": "deleted",
  "category": "gaming"
}
```

### 7. 从分类中删除关键词

```bash
DELETE /api/manage_categories
Content-Type: application/json

{
  "action": "remove_keywords",
  "category": "gaming",
  "keywords": ["旧关键词1", "旧关键词2"]
}
```

**响应示例:**
```json
{
  "success": true,
  "action": "keywords_removed",
  "category": "gaming",
  "removed_count": 2,
  "remaining_keywords": 12,
  "removed_keywords": ["旧关键词1", "旧关键词2"]
}
```

## 💡 使用示例

### 示例1: 创建"教育"分类

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/manage_categories \
  -H "Content-Type: application/json" \
  -d '{
    "action": "add_category",
    "category": "education",
    "keywords": [
      "教育", "学校", "大学", "在线教育", "MOOC", "课程", "学习",
      "education", "school", "university", "online learning", "course"
    ]
  }'
```

### 示例2: 创建"健康"分类

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/manage_categories \
  -H "Content-Type: application/json" \
  -d '{
    "action": "add_category",
    "category": "health",
    "keywords": [
      "健康", "医疗", "医院", "医生", "疾病", "治疗", "药物", "疫苗",
      "health", "medical", "hospital", "doctor", "disease", "treatment"
    ]
  }'
```

### 示例3: 向科技分类添加新关键词

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/manage_categories \
  -H "Content-Type: application/json" \
  -d '{
    "action": "add_keywords",
    "category": "tech",
    "keywords": ["ChatGPT", "GPT-4", "LLM", "大语言模型"]
  }'
```

### 示例4: 查看所有分类

```bash
curl https://upgraded-octo-fortnight.vercel.app/api/manage_categories
```

## 📝 分类命名建议

### 推荐命名规则
- 使用小写字母
- 多个单词用下划线连接：`health_care`, `artificial_intelligence`
- 简短且描述性强：`gaming` 而不是 `video_games_and_entertainment`

### 示例分类
- `gaming` - 游戏
- `education` - 教育
- `health` - 健康
- `sports` - 体育
- `entertainment` - 娱乐
- `food` - 美食
- `travel` - 旅游
- `fashion` - 时尚
- `art` - 艺术
- `music` - 音乐

## 🔄 与关键词优化工具结合使用

1. **创建新分类** → 使用 `/api/manage_categories`
2. **添加基础关键词** → 使用 `/api/manage_categories` (add_keywords)
3. **自动扩展关键词** → 使用 `/api/optimize_keywords`
4. **查看优化结果** → 使用 `/api/manage_categories` (GET)

## 📊 数据存储

- **默认分类**: 存储在代码中 (`news_searcher.py`)
- **自定义分类**: 存储在 `custom_categories.json` 文件中
- **自动合并**: 系统自动合并默认和自定义分类

## ⚠️ 注意事项

1. **默认分类**: 不能删除默认分类，但可以添加关键词
2. **分类名称**: 建议使用英文，避免特殊字符
3. **关键词格式**: 支持中英文混合，自动去重和清理
4. **持久化**: 自定义分类保存在文件中，重启后仍然有效

## 🎉 总结

分类管理器让你可以：
1. ✅ 动态创建新分类
2. ✅ 灵活管理关键词
3. ✅ 无需修改代码即可扩展分类系统
4. ✅ 与关键词优化工具无缝集成

通过分类管理器，你可以根据实际需求定制新闻分类系统！

