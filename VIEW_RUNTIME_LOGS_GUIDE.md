# 如何查看Vercel运行时日志 - 详细指南

## 🎯 目标
获取Python错误堆栈，这是修复FUNCTION_INVOCATION_FAILED的关键！

## 📍 方法1: 通过Logs标签查看（推荐）

### 步骤：

1. **访问Vercel Dashboard**
   - https://vercel.com/dashboard
   - 进入项目 `upgraded-octo-fortnight`

2. **点击顶部导航栏的 "Logs" 标签**
   - 在 Overview, Deployments, Analytics 等标签旁边

3. **触发函数执行**
   - 在另一个标签页访问：`https://upgraded-octo-fortnight.vercel.app/api/health`
   - 或者使用curl：`curl https://upgraded-octo-fortnight.vercel.app/api/health`

4. **立即回到Logs标签**
   - 你应该能看到实时的日志输出
   - 查找Python错误堆栈

5. **复制完整的错误信息**
   - 包括完整的Traceback
   - 包括错误类型和消息

## 📍 方法2: 通过部署详情查看

### 步骤：

1. **在Deployments页面**
2. **点击最新的部署**（如 `FAbDtCy7D`）
3. **在部署详情页面查找**：
   - **"Function Logs"** 标签
   - **"Runtime Logs"** 标签
   - **"Logs"** 标签
4. **查看函数执行日志**

## 🔍 需要查找的信息

### Python错误堆栈示例：

```
Traceback (most recent call last):
  File "/var/task/api/health.py", line 11, in handler
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
  File "/var/task/api/health.py", line X, in <module>
    ...
ModuleNotFoundError: No module named 'xxx'
```

或者：

```
AttributeError: 'dict' object has no attribute 'get'
TypeError: ...
ImportError: ...
```

## 📝 如果找不到Logs标签

如果导航栏中没有"Logs"标签，尝试：

1. **点击部署详情**
2. **查找"View Function Logs"或类似按钮**
3. **或者点击函数名称查看详情**

## 💡 提示

- **实时日志**：访问API端点后立即查看Logs，日志会实时出现
- **完整错误**：复制完整的错误堆栈，不只是最后一行
- **多个错误**：可能有多个错误，都记录下来

## 🎯 找到错误后

请把完整的错误信息告诉我，包括：
1. 完整的Traceback
2. 错误类型（如ModuleNotFoundError）
3. 错误消息
4. 出错的文件和行号

有了这些信息，我可以立即修复问题！

