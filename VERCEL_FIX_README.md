# Vercel部署修复说明

## 🔧 修复内容

### 1. 更新了 `vercel.json` 配置
- 移除了Flask相关的配置
- 正确配置了API路由，每个端点指向对应的Python文件
- 使用Vercel Python运行时的标准格式

### 2. 重写了所有API端点
所有API端点 (`api/index.py`, `api/health.py`, `api/search.py`, `api/download.py`) 都已重写为Vercel Python运行时的标准格式：
- 使用 `handler(request)` 函数作为入口点
- 接收 `request` 字典对象
- 返回包含 `statusCode`, `headers`, `body` 的字典

### 3. 更新了 `requirements.txt`
- 移除了Flask依赖（Vercel Python运行时不需要）
- 添加了 `lxml` 用于BeautifulSoup解析

## 🚀 部署步骤

### 方法1: 通过Vercel Dashboard部署

1. **推送代码到GitHub**
   ```bash
   cd upgraded-octo-fortnight
   git add .
   git commit -m "Fix Vercel deployment configuration"
   git push origin main
   ```

2. **在Vercel Dashboard中重新部署**
   - 访问 https://vercel.com/dashboard
   - 找到你的项目 `upgraded-octo-fortnight`
   - 点击 "Redeploy" 或等待自动重新部署

3. **配置环境变量（可选）**
   在Vercel Dashboard的Settings > Environment Variables中添加：
   - `ENABLE_NEWS_FILTER=true` (推荐)
   - `NEWSAPI_KEY` (可选)
   - `BING_API_KEY` (可选)
   - `SERPAPI_KEY` (可选)
   - `GOOGLE_SEARCH_API_KEY` (可选)
   - `GOOGLE_SEARCH_ENGINE_ID` (可选)

### 方法2: 通过Vercel CLI部署

```bash
cd upgraded-octo-fortnight
npm install -g vercel
vercel --prod
```

## 🧪 测试API端点

部署成功后，访问以下端点进行测试：

### 1. API首页
```bash
curl https://upgraded-octo-fortnight.vercel.app/
```

### 2. 健康检查
```bash
curl https://upgraded-octo-fortnight.vercel.app/api/health
```

### 3. 搜索新闻（GET方式）
```bash
curl "https://upgraded-octo-fortnight.vercel.app/api/search?keywords=AI&max_results=5"
```

### 4. 搜索新闻（POST方式）
```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/search \
  -H "Content-Type: application/json" \
  -d '{"keywords": "AI", "max_results": 5}'
```

### 5. 下载新闻内容
```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/download \
  -H "Content-Type: application/json" \
  -d '{"news_url": "https://example.com/article"}'
```

## 📝 主要变更

### API端点格式变更

**之前（Flask格式）：**
```python
@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy'})
```

**现在（Vercel格式）：**
```python
def handler(request):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'status': 'healthy'})
    }
```

### 请求处理变更

**之前：**
```python
data = request.get_json()
```

**现在：**
```python
body = request.get('body', '{}')
if isinstance(body, str):
    data = json.loads(body)
else:
    data = body
```

## ⚠️ 注意事项

1. **无需API密钥也能运行**：即使不配置任何API密钥，服务也能使用免费源（Hacker News、Google News RSS等）正常运行

2. **环境变量**：至少设置 `ENABLE_NEWS_FILTER=true` 以获得最佳体验

3. **CORS支持**：所有API端点都已添加CORS头，支持跨域请求

4. **错误处理**：所有端点都包含完整的错误处理，即使出错也会返回友好的错误信息

## 🔍 故障排查

如果部署后仍然无法使用：

1. **检查Vercel部署日志**
   - 在Vercel Dashboard中查看部署日志
   - 检查是否有Python依赖安装错误

2. **验证API端点**
   - 访问 `/api/health` 端点，应该返回健康状态
   - 如果返回404，检查 `vercel.json` 路由配置

3. **检查Python版本**
   - Vercel默认使用Python 3.9
   - 如果需要特定版本，创建 `runtime.txt` 文件

4. **查看函数日志**
   - 在Vercel Dashboard的Functions标签页查看实时日志
   - 检查是否有运行时错误

## ✅ 验证清单

- [x] `vercel.json` 配置正确
- [x] 所有API端点使用Vercel格式
- [x] `requirements.txt` 已更新（移除Flask）
- [x] 错误处理完善
- [x] CORS头已添加
- [x] 支持GET和POST请求
- [x] 环境变量处理正确

## 📞 需要帮助？

如果遇到问题，请检查：
1. Vercel部署日志
2. 函数执行日志
3. GitHub Actions（如果有）
4. 环境变量配置

