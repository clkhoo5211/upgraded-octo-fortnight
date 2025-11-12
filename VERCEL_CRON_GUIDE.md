# Vercel Cron 设置和管理指南

## ✅ 当前状态

**Cron Job已正确设置并启用！**

- **状态**: Enabled（已启用）
- **路径**: `/api/auto_archive`
- **执行时间**: 每天凌晨1点（UTC时间）
- **Cron表达式**: `0 1 * * *`
- **时区**: UTC

## 🔧 Cron设置方式

### 自动设置（当前方式）

Vercel Cron通过 `vercel.json` 配置文件自动设置：

```json
{
  "crons": [
    {
      "path": "/api/auto_archive",
      "schedule": "0 1 * * *"
    }
  ]
}
```

当你部署到Vercel时，这个配置会自动创建Cron Job。

### 手动设置（如果需要）

1. 访问：Vercel Dashboard → 项目 → Settings → Cron Jobs
2. 点击 "Create Cron Job"
3. 填写：
   - **Path**: `/api/auto_archive`
   - **Schedule**: `0 1 * * *`
4. 保存

## ⏰ 执行时间说明

### 当前设置

- **Cron表达式**: `0 1 * * *`
- **含义**: 每天凌晨1点（UTC时间）
- **北京时间**: 凌晨1点UTC = 上午9点（UTC+8）
- **时区**: 所有Cron使用UTC时区

### Cron表达式格式

```
分钟 小时 日 月 星期
 0    1   *  *   *
```

- `0` - 分钟（0分）
- `1` - 小时（1点）
- `*` - 每天
- `*` - 每月
- `*` - 每星期

## 🎮 管理Cron Job

### 在Vercel Dashboard

1. **查看状态**
   - 访问：Settings → Cron Jobs
   - 查看Cron Job列表和状态

2. **手动触发**
   - 点击 "Run" 按钮
   - 立即执行一次归档任务
   - 可以查看执行结果

3. **查看日志**
   - 点击 "View Logs" 按钮
   - 查看历史执行记录
   - 查看错误信息（如果有）

4. **启用/禁用**
   - 顶部开关：启用/禁用所有Cron Jobs
   - 禁用后：Cron Job不会执行，但配置会保留

## 🧪 测试Cron Job

### 方式1: Vercel Dashboard

1. 访问：Settings → Cron Jobs
2. 找到 `/api/auto_archive`
3. 点击 **"Run"** 按钮
4. 查看执行结果

### 方式2: 手动访问API

```bash
curl "https://upgraded-octo-fortnight.vercel.app/api/auto_archive"
```

### 方式3: 查看日志

1. 点击 **"View Logs"** 按钮
2. 查看最近的执行记录
3. 检查是否有错误

## 📝 修改执行时间

### 方法1: 修改vercel.json（推荐）

编辑 `vercel.json`：

```json
{
  "crons": [
    {
      "path": "/api/auto_archive",
      "schedule": "0 9 * * *"  // 改为每天9点UTC（北京时间17点）
    }
  ]
}
```

然后重新部署：
```bash
git add vercel.json
git commit -m "Update cron schedule"
git push origin main
```

### 方法2: Vercel Dashboard

1. 访问：Settings → Cron Jobs
2. 编辑Cron Job
3. 修改Schedule
4. 保存

## 💡 常用Cron表达式

| Cron表达式 | 说明 | 北京时间（UTC+8） |
|-----------|------|------------------|
| `0 1 * * *` | 每天凌晨1点UTC | 上午9点 |
| `0 9 * * *` | 每天上午9点UTC | 下午5点 |
| `0 0 * * *` | 每天午夜UTC | 上午8点 |
| `0 */6 * * *` | 每6小时执行一次 | - |
| `0 1 * * 1` | 每周一凌晨1点UTC | 每周一上午9点 |
| `0 1 1 * *` | 每月1号凌晨1点UTC | 每月1号上午9点 |

## ⚠️ 注意事项

### 时区

- **所有Cron使用UTC时区**
- 北京时间 = UTC时间 + 8小时
- 例如：UTC 1:00 = 北京时间 9:00

### Hobby计划限制

- Cron Jobs在Hobby计划有**1小时的灵活时间窗口**
- 实际执行时间可能在设定时间的1小时内

### 执行时间

- Cron Job执行需要时间（通常几秒到几分钟）
- 可以在Logs中查看实际执行时间

## 🔍 验证Cron是否工作

### 检查1: Dashboard状态

- ✅ Cron Jobs页面显示 "Enabled"
- ✅ `/api/auto_archive` 显示在列表中
- ✅ Schedule显示正确的时间

### 检查2: 查看日志

1. 点击 "View Logs"
2. 查看最近的执行记录
3. 确认是否有成功执行

### 检查3: GitHub仓库

检查GitHub仓库是否有新的归档文件：
- https://github.com/clkhoo5211/upgraded-octo-fortnight/tree/main/2025

## 📊 当前配置总结

✅ **Cron Job已正确设置**
- 路径: `/api/auto_archive`
- 执行时间: 每天凌晨1点UTC（北京时间上午9点）
- 状态: Enabled（已启用）
- 配置文件: `vercel.json`

✅ **功能正常**
- 可以手动触发（点击Run）
- 可以查看日志（点击View Logs）
- 会自动执行（每天凌晨1点UTC）

## 🎯 总结

**你的Vercel Cron已经设置好了！**

- ✅ 配置正确
- ✅ 状态启用
- ✅ 可以正常使用

**下一步**：
- 等待自动执行（每天凌晨1点UTC）
- 或点击 "Run" 手动测试
- 查看 "View Logs" 确认执行情况

