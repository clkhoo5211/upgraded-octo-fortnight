"""
测试配置文件
从环境变量读取敏感信息，避免硬编码
"""
import os

# API配置
API_BASE = os.getenv('TEST_API_BASE', 'https://upgraded-octo-fortnight.vercel.app')

# 敏感密钥 - 必须从环境变量读取
ADMIN_SECRET = os.getenv('ADMIN_SECRET', '')
REGISTRATION_SECRET = os.getenv('REGISTRATION_SECRET', '')

def validate_test_config():
    """验证测试配置是否完整"""
    missing = []
    if not ADMIN_SECRET:
        missing.append('ADMIN_SECRET')
    if not REGISTRATION_SECRET:
        missing.append('REGISTRATION_SECRET')
    
    if missing:
        raise ValueError(
            f"缺少必需的环境变量: {', '.join(missing)}\n"
            f"请设置环境变量或创建 .env.test 文件\n"
            f"示例:\n"
            f"  export ADMIN_SECRET='your-admin-secret'\n"
            f"  export REGISTRATION_SECRET='your-registration-secret'"
        )
    
    return True

