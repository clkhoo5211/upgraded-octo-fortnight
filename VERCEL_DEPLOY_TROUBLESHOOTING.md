# 🚨 Vercel自动部署问题排查指南

## 📋 常见问题与解决方案

### 问题1: 导入仓库后没有自动部署

**原因分析：**
- 首次导入可能需要手动触发一次部署
- 项目设置可能有问题
- 环境变量缺失

**解决方案：**

1. **手动触发首次部署**
   - 进入Vercel项目Dashboard
   - 点击 "Deployments" 标签
   - 点击 "Create Deployment" 或 "Redeploy"
   
2. **检查项目设置**
   - Settings → General → Framework Preset
   - 确保设置为 `Other`
   - Build Command: 留空
   - Output Directory: 留空

3. **添加环境变量**
   - Settings → Environment Variables
   - 添加：`NEWSAPI_KEY` = 你的API密钥

### 问题2: 部署失败/构建错误

**检查步骤：**

1. **查看部署日志**
   - Vercel Dashboard → Deployments → 点击失败的部署
   - 查看详细的错误日志

2. **常见错误及修复**

   **错误：Python版本问题**
   ```
   Python version 3.11 not supported
   ```
   **解决：** 在 `vercel.json` 中指定版本
   ```json
   {
     "builds": [{"src": "api/index.py", "use": "@vercel/python"}],
     "pythonVersion": "3.11"
   }
   ```

   **错误：模块导入失败**
   ```
   ModuleNotFoundError: No module named 'xxx'
   ```
   **解决：** 检查 `requirements.txt` 是否包含所有依赖

   **错误：超时**
   ```
   Function timeout exceeded
   ```
   **解决：** 在 `vercel.json` 中增加超时时间
   ```json
   {
     "functions": {
       "api/index.py": {
         "maxDuration": 60
       }
     }
   }
   ```

### 问题3: API访问失败

**检查项目：**

1. **验证部署状态**
   - Deployments标签 → 最新部署应该是 "Ready"
   - 绿色状态表示成功

2. **检查域名**
   - Settings → Domains
   - 确保域名配置正确
   - 默认：your-project.vercel.app

3. **测试API端点**
   - 访问：`https://your-project.vercel.app/api/health`
   - 应该返回JSON响应

### 问题4: 环境变量不生效

**解决方法：**

1. **在Vercel中添加**
   - Settings → Environment Variables
   - 变量名：`NEWSAPI_KEY`
   - 变量值：你的API密钥
   - 环境：Production, Preview, Development (都选)

2. **确保环境变量名称正确**
   - 区分大小写
   - 不要有多余的空格

3. **重新部署**
   - 修改环境变量后需要重新部署
   - 手动触发或修改代码触发

## 🔧 快速诊断命令

在本地测试你的API：

```bash
# 测试Flask应用
cd api
python index.py

# 访问 http://localhost:5000/api/health
```

## 📞 需要帮助？

**如果问题仍未解决，请提供以下信息：**

1. Vercel项目Dashboard截图（Deployments标签）
2. 失败的部署日志
3. Vercel项目设置截图
4. 环境变量配置截图

我会根据具体错误信息给出针对性的解决方案。

## ✅ 推荐流程

1. **初次部署** → 手动触发
2. **配置环境变量** → NEWSAPI_KEY
3. **测试API** → 访问health端点
4. **验证自动部署** → 推送代码测试