# 如何查看Vercel日志和错误信息

## 📍 查看日志的正确方法

### 方法1: 通过Deployments查看（推荐）

1. **访问Vercel Dashboard**
   - https://vercel.com/dashboard
   - 进入项目 `upgraded-octo-fortnight`

2. **点击Deployments标签**（你已经在这里了）

3. **点击最新的部署**（当前是Building状态的 `FAbDtCy7D`）

4. **在部署详情页面中**：
   - 查看 **Build Logs**（构建日志）
   - 查看 **Function Logs**（函数日志）
   - 查看 **Runtime Logs**（运行时日志）

### 方法2: 通过Logs标签查看

1. **点击顶部导航栏的 "Logs" 标签**

2. **查看实时日志**
   - 这里会显示所有函数的实时日志
   - 可以筛选特定的函数

### 方法3: 点击具体部署查看详情

1. **在Deployments列表中**
2. **点击任意一个部署**（如 `EgQwPvNgo` 或 `EuzFgAMbe`）
3. **在部署详情页面**：
   - 查看构建日志
   - 查看函数执行日志
   - 查看错误信息

## 🔍 需要查找的信息

### 构建日志中查找：
- Python依赖安装错误
- 构建失败信息
- 任何警告

### 函数日志中查找：
- Python错误堆栈（Traceback）
- 导入错误（ModuleNotFoundError）
- 运行时错误
- FUNCTION_INVOCATION_FAILED的详细原因

## 📝 具体步骤

1. **点击当前Building的部署** `FAbDtCy7D`
2. **等待构建完成**（如果还在Building）
3. **查看构建日志**，查找：
   ```
   Installing dependencies...
   ERROR: ...
   ```
4. **查看函数日志**，查找：
   ```
   Traceback (most recent call last):
     File "...", line X, in handler
   Error: ...
   ```

## 💡 提示

- 如果部署还在Building，等待它完成
- 如果部署是Ready状态，点击它查看历史日志
- 日志会显示具体的错误信息，这是修复问题的关键

