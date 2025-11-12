# GitHub Token 设置说明

## 🤔 需要设置 Personal Access Token 吗？

### 简短回答

**是的，需要设置 Personal Access Token**，但原因不是Vercel部署，而是**自动归档功能需要写入GitHub仓库**。

## 📋 详细说明

### Vercel导入 vs GitHub API写入

1. **Vercel导入GitHub仓库**：
   - ✅ Vercel可以读取仓库代码
   - ✅ Vercel可以自动部署
   - ❌ **但不能写入文件到仓库**

2. **自动归档功能**：
   - 需要**创建和更新文件**到GitHub仓库
   - 需要**提交代码**到仓库
   - 这需要**GitHub API写入权限**
   - 所以需要**Personal Access Token**

### 两种使用场景

#### 场景1: 只需要API功能（不需要自动归档）

**不需要设置 GITHUB_TOKEN**

- ✅ 搜索新闻：`/api/search`
- ✅ 下载内容：`/api/download`
- ✅ 手动归档：`/api/archive`（如果不需要保存到GitHub）

**设置位置**: 无需设置

#### 场景2: 需要自动归档到GitHub（推荐）

**需要设置 GITHUB_TOKEN**

- ✅ 自动归档：`/api/auto_archive`（Vercel Cron）
- ✅ 完整归档：`/api/archive`（保存到GitHub）
- ✅ GitHub Actions自动归档

**设置位置**: Vercel Dashboard → Settings → Environment Variables

## 🔑 如何创建 Personal Access Token

### 步骤1: 创建Token

1. 访问：https://github.com/settings/tokens
2. 点击 **"Generate new token"** → **"Generate new token (classic)"**
3. 填写信息：
   - **Note**: `Vercel News Archiver`
   - **Expiration**: 选择过期时间（建议90天或No expiration）
   - **Scopes**: 勾选以下权限：
     - ✅ `repo` - 完整仓库访问权限（包括写入）

4. 点击 **"Generate token"**
5. **复制token**（只显示一次！）

### 步骤2: 在Vercel中设置

1. 访问：https://vercel.com/dashboard
2. 进入项目：`upgraded-octo-fortnight`
3. 点击 **Settings** → **Environment Variables**
4. 添加：
   - **Name**: `GITHUB_TOKEN`
   - **Value**: 粘贴刚才复制的token
   - **Environment**: 选择所有环境（Production, Preview, Development）

5. 点击 **Save**

## ⚠️ 重要提示

### Token权限要求

- ✅ **必须勾选 `repo` 权限**
- ✅ 这样才能写入文件到仓库

### 安全建议

1. **不要分享token**：token就像密码，不要公开
2. **定期更新**：建议每90天更新一次
3. **限制权限**：只给必要的权限（`repo`）
4. **使用环境变量**：不要写在代码中

## 🎯 如果不想设置Token

如果你**不需要自动归档到GitHub**，可以：

1. **只使用搜索和下载功能**
   - `/api/search` - 搜索新闻
   - `/api/download` - 下载内容
   - 不需要设置 `GITHUB_TOKEN`

2. **使用其他存储方式**
   - 保存到本地文件
   - 保存到其他云存储（S3、Dropbox等）
   - 需要修改代码实现

3. **禁用自动归档**
   - 在 `vercel.json` 中删除 `crons` 配置
   - 或设置 `GITHUB_TOKEN` 为空，归档功能会跳过

## 📝 总结

| 功能 | 需要Token? | 原因 |
|------|-----------|------|
| Vercel部署 | ❌ 不需要 | Vercel自动处理 |
| 搜索新闻 | ❌ 不需要 | 只读取外部API |
| 下载内容 | ❌ 不需要 | 只读取外部网站 |
| **自动归档到GitHub** | ✅ **需要** | **需要写入GitHub仓库** |

**结论**: 如果使用自动归档功能，**必须设置 Personal Access Token**。

