# 如何查看运行时日志

## 📍 根据你的构建日志

构建已经成功，但运行时失败（FUNCTION_INVOCATION_FAILED）。

## 🔍 查看运行时日志的步骤

### 方法1: 通过部署详情查看运行时日志

1. **在Deployments页面**
2. **点击最新的部署**（如 `FAbDtCy7D`）
3. **在部署详情页面**：
   - 找到 **"Function Logs"** 或 **"Runtime Logs"** 标签
   - 查看函数执行时的错误

### 方法2: 通过Logs标签查看实时日志

1. **点击顶部导航栏的 "Logs" 标签**
2. **访问API端点触发函数执行**
3. **查看实时日志中的错误**

### 方法3: 测试API并查看日志

1. **访问**: `https://upgraded-octo-fortnight.vercel.app/api/health`
2. **立即切换到Vercel Dashboard的Logs标签**
3. **查看实时出现的错误日志**

## 📝 需要查找的信息

在运行时日志中查找：

```
Traceback (most recent call last):
  File "/var/task/api/health.py", line X, in handler
    ...
Error: ...
```

或者：

```
ModuleNotFoundError: No module named 'xxx'
ImportError: ...
AttributeError: ...
```

## 🛠️ 已修复的问题

1. ✅ **更新了vercel.json**
   - 移除了过时的`builds`配置
   - 改用新的`functions`配置
   - 指定Python 3.12运行时

2. ✅ **构建已成功**
   - 所有函数都构建成功
   - 大小约13MB（包含依赖）

## ⚠️ 注意事项

函数大小13MB较大，可能导致：
- 冷启动慢
- 内存使用高
- 但这不是主要问题，主要问题是运行时错误

## 🎯 下一步

1. **等待新的部署完成**（已推送修复）
2. **测试API端点**
3. **查看运行时日志**获取具体错误
4. **根据错误信息进行修复**

