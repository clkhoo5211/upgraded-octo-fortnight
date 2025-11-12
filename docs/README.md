# 📚 文档目录

欢迎使用 Global News Aggregator API 文档！

## 🚀 快速开始

- **[快速开始指南](api/QUICK_START.md)** - 5分钟快速上手
- **[API使用指南](api/API_USAGE_GUIDE.md)** - 完整的API使用说明
- **[API安全指南](security/API_SECURITY_GUIDE.md)** - 认证、授权和安全配置

---

## 📖 文档分类

### 🔌 API文档 (`api/`)

| 文档 | 说明 |
|------|------|
| [API使用指南](api/API_USAGE_GUIDE.md) | 完整的API端点说明、请求/响应示例、代码示例 |
| [快速开始](api/QUICK_START.md) | 5分钟快速上手指南 |
| [分类管理指南](api/CATEGORY_MANAGER_GUIDE.md) | 如何管理新闻分类和关键词 |
| [关键词优化指南](api/KEYWORD_OPTIMIZER_GUIDE.md) | 关键词优化功能说明 |

### 🔐 安全文档 (`security/`)

| 文档 | 说明 |
|------|------|
| [API安全指南](security/API_SECURITY_GUIDE.md) | 认证、授权、Token管理、速率限制 |
| [GitHub Token设置](security/GITHUB_TOKEN_SETUP.md) | GitHub Token配置指南 |
| [Fine-grained Token指南](security/FINE_GRAINED_TOKEN_GUIDE.md) | GitHub Fine-grained Personal Access Token设置 |

### 🚀 部署文档 (`deployment/`)

| 文档 | 说明 |
|------|------|
| [Vercel Cron设置](deployment/VERCEL_CRON_GUIDE.md) | Vercel Cron任务配置 |
| [自动归档设置](deployment/AUTO_ARCHIVE_SETUP.md) | 自动归档功能配置 |
| [环境变量设置](deployment/ENV_SETUP.md) | 环境变量配置指南 |
| [Vercel部署指南](deployment/VERCEL_DEPLOY_GUIDE.md) | Vercel部署说明 |
| [Vercel快速开始](deployment/VERCEL_QUICK_START.md) | Vercel快速部署 |
| [GitHub Actions部署](deployment/GITHUB_ACTIONS_DEPLOYMENT.md) | GitHub Actions部署说明 |
| [部署总览](deployment/DEPLOYMENT.md) | 部署相关文档汇总 |

### 🧪 测试文档 (`testing/`)

| 文档 | 说明 |
|------|------|
| [测试结果](testing/TEST_RESULTS.md) | API测试结果报告 |
| [测试报告](testing/TEST_REPORT.md) | 详细测试报告 |
| [测试状态](testing/TESTING_STATUS.md) | 当前测试状态 |
| [完整测试总结](testing/COMPLETE_TEST_SUMMARY.md) | 完整测试总结 |
| [最终测试总结](testing/FINAL_TEST_SUMMARY.md) | 最终测试总结 |
| [手动归档测试](testing/MANUAL_ARCHIVE_TEST.md) | 手动归档功能测试 |
| [归档文件位置](testing/ARCHIVE_FILE_LOCATION.md) | 归档文件位置说明 |

### 🔧 故障排除 (`troubleshooting/`)

| 文档 | 说明 |
|------|------|
| [Vercel配置修复](troubleshooting/VERCEL_CONFIG_FIX.md) | Vercel配置问题修复 |
| [Vercel部署故障排除](troubleshooting/VERCEL_DEPLOY_TROUBLESHOOTING.md) | Vercel部署问题排查 |
| [Vercel部署Hook修复](troubleshooting/VERCEL_DEPLOY_HOOK_FIX.md) | Vercel部署Hook问题修复 |
| [诊断总结](troubleshooting/DIAGNOSIS_SUMMARY.md) | 问题诊断总结 |
| [修复总结](troubleshooting/FIXES_SUMMARY.md) | 问题修复总结 |
| [查看运行时日志](troubleshooting/VIEW_RUNTIME_LOGS_GUIDE.md) | 如何查看Vercel运行时日志 |

### 📦 归档文档 (`archive/`)

历史文档和已完成的特性说明：

| 文档 | 说明 |
|------|------|
| [完整功能列表](archive/COMPLETE_FEATURES.md) | 所有已实现功能 |
| [成功报告](archive/SUCCESS_REPORT.md) | 项目成功报告 |
| [环境配置](archive/ENV_CONFIG.md) | 环境配置说明（历史） |
| [环境设置指南](archive/ENV_SETUP_GUIDE.md) | 环境设置指南（历史） |

---

## 🎯 常用文档链接

### 新手入门
1. [快速开始](api/QUICK_START.md) - 5分钟快速上手
2. [API使用指南](api/API_USAGE_GUIDE.md) - 了解如何使用API
3. [API安全指南](security/API_SECURITY_GUIDE.md) - 设置认证和授权

### 部署相关
1. [Vercel快速开始](deployment/VERCEL_QUICK_START.md) - 快速部署到Vercel
2. [环境变量设置](deployment/ENV_SETUP.md) - 配置环境变量
3. [Vercel Cron设置](deployment/VERCEL_CRON_GUIDE.md) - 设置定时任务

### 在其他仓库使用
1. [API安全指南 - 场景2](security/API_SECURITY_GUIDE.md#场景2-在其他仓库项目中使用api) - 在其他仓库使用API
2. [API使用指南 - 在其他仓库中使用](api/API_USAGE_GUIDE.md#在其他仓库中使用) - 使用示例

### 故障排除
1. [Vercel部署故障排除](troubleshooting/VERCEL_DEPLOY_TROUBLESHOOTING.md) - 常见问题解决
2. [查看运行时日志](troubleshooting/VIEW_RUNTIME_LOGS_GUIDE.md) - 如何查看日志

---

## 📁 文档结构

```
docs/
├── README.md                    # 本文档（文档索引）
├── api/                        # API相关文档
│   ├── API_USAGE_GUIDE.md
│   ├── QUICK_START.md
│   ├── CATEGORY_MANAGER_GUIDE.md
│   └── KEYWORD_OPTIMIZER_GUIDE.md
├── security/                   # 安全相关文档
│   ├── API_SECURITY_GUIDE.md
│   ├── GITHUB_TOKEN_SETUP.md
│   └── FINE_GRAINED_TOKEN_GUIDE.md
├── deployment/                 # 部署相关文档
│   ├── VERCEL_CRON_GUIDE.md
│   ├── AUTO_ARCHIVE_SETUP.md
│   ├── ENV_SETUP.md
│   ├── VERCEL_DEPLOY_GUIDE.md
│   └── ...
├── testing/                    # 测试相关文档
│   ├── TEST_RESULTS.md
│   ├── TEST_REPORT.md
│   └── ...
├── troubleshooting/            # 故障排除文档
│   ├── VERCEL_CONFIG_FIX.md
│   ├── VERCEL_DEPLOY_TROUBLESHOOTING.md
│   └── ...
└── archive/                    # 归档/历史文档
    ├── COMPLETE_FEATURES.md
    └── ...
```

---

## 🔍 搜索文档

### 按主题搜索

- **认证和授权**: [API安全指南](security/API_SECURITY_GUIDE.md)
- **API使用**: [API使用指南](api/API_USAGE_GUIDE.md)
- **部署问题**: [故障排除文档](troubleshooting/)
- **测试相关**: [测试文档](testing/)

### 按场景搜索

- **第一次使用**: [快速开始](api/QUICK_START.md)
- **在其他项目中使用**: [API安全指南 - 场景2](security/API_SECURITY_GUIDE.md#场景2-在其他仓库项目中使用api)
- **部署到Vercel**: [Vercel快速开始](deployment/VERCEL_QUICK_START.md)
- **设置定时任务**: [Vercel Cron设置](deployment/VERCEL_CRON_GUIDE.md)
- **遇到问题**: [故障排除文档](troubleshooting/)

---

## 📞 需要帮助？

- 查看 [快速开始指南](api/QUICK_START.md)
- 阅读 [API使用指南](api/API_USAGE_GUIDE.md)
- 参考 [故障排除文档](troubleshooting/)
- 访问 [GitHub仓库](https://github.com/clkhoo5211/upgraded-octo-fortnight) 提交Issue

---

**最后更新**: 2025-11-12
