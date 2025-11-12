# Fine-grained Personal Access Token 使用指南

## ✅ 可以使用 Fine-grained Token

**是的，Fine-grained Personal Access Token 可以使用！**

PyGithub库完全支持Fine-grained tokens，使用方式与Classic tokens相同。

## 🔑 两种Token类型对比

### Classic Personal Access Token（传统）
- ✅ 完全支持
- ✅ 使用简单
- ✅ 权限范围广（repo权限包含所有仓库）

### Fine-grained Personal Access Token（细粒度）
- ✅ **完全支持**
- ✅ 更安全的权限控制
- ✅ 可以限制到特定仓库
- ✅ 可以设置过期时间
- ✅ 推荐使用（更安全）

## 📋 如何创建 Fine-grained Token

### 步骤1: 创建Token

1. 访问：https://github.com/settings/tokens?type=beta
2. 点击 **"Generate new token"** → **"Generate new token (fine-grained)"**
3. 填写信息：
   - **Token name**: `Vercel News Archiver`
   - **Expiration**: 选择过期时间（建议90天或自定义）
   - **Repository access**: 
     - 选择 **"Only select repositories"**
     - 选择仓库：`clkhoo5211/upgraded-octo-fortnight`
   - **Repository permissions**:
     - ✅ **Contents**: Read and write（必需，用于创建/更新文件）
     - ✅ **Metadata**: Read-only（自动包含）
4. 点击 **"Generate token"**
5. **复制token**（只显示一次！）

### 步骤2: 在Vercel中设置

1. 访问：https://vercel.com/dashboard
2. 进入项目：`upgraded-octo-fortnight`
3. 点击 **Settings** → **Environment Variables**
4. 添加：
   - **Name**: `GITHUB_TOKEN`
   - **Value**: 粘贴刚才复制的Fine-grained token
   - **Environment**: 选择所有环境（Production, Preview, Development）
5. 点击 **Save**

## 🔒 权限要求

### Fine-grained Token 必需权限

- ✅ **Contents**: Read and write
  - 用于：创建、更新、删除文件
  - 必需：是

- ✅ **Metadata**: Read-only
  - 用于：读取仓库信息
  - 必需：自动包含，无需单独设置

### 不需要的权限

- ❌ **Actions**: 不需要
- ❌ **Administration**: 不需要
- ❌ **Checks**: 不需要
- ❌ **Codespaces**: 不需要
- ❌ **Deployments**: 不需要
- ❌ **Environments**: 不需要
- ❌ **Issues**: 不需要
- ❌ **Packages**: 不需要
- ❌ **Pull requests**: 不需要
- ❌ **Repository secrets**: 不需要
- ❌ **Secret scanning alerts**: 不需要
- ❌ **Security events**: 不需要
- ❌ **Variables**: 不需要

## ✅ 优势

### Fine-grained Token 的优势

1. **更安全**
   - 只能访问指定的仓库
   - 权限最小化原则
   - 如果token泄露，影响范围有限

2. **更灵活**
   - 可以为不同仓库设置不同权限
   - 可以设置精确的过期时间

3. **更易管理**
   - 可以查看token的使用情况
   - 可以随时撤销token

## 🔍 验证Token是否工作

### 测试命令

```bash
curl -X POST https://upgraded-octo-fortnight.vercel.app/api/archive \
  -H "Content-Type: application/json" \
  -d '{
    "max_results": 2,
    "download_content": true,
    "save_to_github": true
  }'
```

### 检查返回结果

**成功情况**:
```json
{
  "success": true,
  "saved_files": [
    "2025/11/12/tech.md",
    "2025/11/12/finance.md"
  ]
}
```

**失败情况**:
```json
{
  "success": false,
  "errors": [
    {
      "error": "保存到GitHub失败: ..."
    }
  ]
}
```

## ⚠️ 常见问题

### Q1: Fine-grained token 和 Classic token 有什么区别？

**A**: Fine-grained token 提供更细粒度的权限控制，可以限制到特定仓库，更安全。

### Q2: 代码需要修改吗？

**A**: 不需要！PyGithub库完全支持Fine-grained tokens，使用方式完全相同。

### Q3: 如果token权限不足会怎样？

**A**: GitHub API会返回403错误，归档功能会失败，错误信息会显示在API响应的`errors`字段中。

### Q4: 如何知道token是否有足够权限？

**A**: 执行归档测试，如果`saved_files`不为空，说明权限足够。

## 📝 总结

✅ **Fine-grained Personal Access Token 完全可以使用**

**推荐设置**:
- Token类型: Fine-grained
- Repository: `clkhoo5211/upgraded-octo-fortnight`
- 权限: Contents (Read and write)
- 环境变量: `GITHUB_TOKEN`

**使用方式**: 与Classic token完全相同，无需修改代码！

