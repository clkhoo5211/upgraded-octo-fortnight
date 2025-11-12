#!/usr/bin/env python3
"""
API认证快速设置脚本
用于快速创建用户和API Key
"""
import requests
import json
import sys
import os

API_BASE = os.getenv('API_BASE', 'https://upgraded-octo-fortnight.vercel.app')
ADMIN_SECRET = os.getenv('ADMIN_SECRET', '')

def create_user(user_id: str, rate_limit: int = 1000):
    """创建用户"""
    if not ADMIN_SECRET:
        print("❌ 错误: 请设置 ADMIN_SECRET 环境变量")
        return None
    
    url = f"{API_BASE}/api/auth/user"
    headers = {
        "Authorization": f"Bearer {ADMIN_SECRET}",
        "Content-Type": "application/json"
    }
    payload = {
        "user_id": user_id,
        "rate_limit": rate_limit
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            print(f"✅ 用户 '{user_id}' 创建成功")
            return response.json()
        else:
            print(f"❌ 创建用户失败: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def login(user_id: str):
    """登录获取Token"""
    url = f"{API_BASE}/api/auth/login"
    headers = {"Content-Type": "application/json"}
    payload = {"user_id": user_id}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 登录成功")
            print(f"   Access Token: {data['tokens']['access_token'][:20]}...")
            print(f"   Refresh Token: {data['tokens']['refresh_token'][:20]}...")
            print(f"   过期时间: {data['tokens']['expires_at']}")
            return data['tokens']
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def create_api_key(access_token: str, name: str = "default"):
    """创建API Key"""
    url = f"{API_BASE}/api/auth/api-key"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {"name": name}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            data = response.json()
            print(f"✅ API Key创建成功")
            print(f"   API Key: {data['api_key']}")
            print(f"   ⚠️  请妥善保存，此密钥不会再次显示！")
            return data['api_key']
        else:
            print(f"❌ 创建API Key失败: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def test_api_key(api_key: str):
    """测试API Key"""
    url = f"{API_BASE}/api/search"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "categories": ["tech"],
        "max_results": 1
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"✅ API Key测试成功")
            data = response.json()
            print(f"   找到 {data['count']} 条新闻")
            return True
        else:
            print(f"❌ API Key测试失败: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 70)
    print("🔐 API认证快速设置")
    print("=" * 70)
    print()
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python setup_auth.py <user_id> [rate_limit]")
        print()
        print("示例:")
        print("  python setup_auth.py myuser 1000")
        print()
        print("环境变量:")
        print("  ADMIN_SECRET - 管理员密钥（必需）")
        print("  API_BASE - API地址（可选，默认: https://upgraded-octo-fortnight.vercel.app）")
        sys.exit(1)
    
    user_id = sys.argv[1]
    rate_limit = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    
    print(f"📋 设置信息:")
    print(f"   用户ID: {user_id}")
    print(f"   速率限制: {rate_limit} 请求/小时")
    print()
    
    # 步骤1: 创建用户
    print("步骤1: 创建用户...")
    user_result = create_user(user_id, rate_limit)
    if not user_result:
        print("⚠️  用户可能已存在，继续...")
    print()
    
    # 步骤2: 登录
    print("步骤2: 登录获取Token...")
    tokens = login(user_id)
    if not tokens:
        print("❌ 登录失败，退出")
        sys.exit(1)
    print()
    
    # 步骤3: 创建API Key
    print("步骤3: 创建API Key...")
    api_key = create_api_key(tokens['access_token'], f"{user_id}-key")
    if not api_key:
        print("❌ 创建API Key失败，退出")
        sys.exit(1)
    print()
    
    # 步骤4: 测试API Key
    print("步骤4: 测试API Key...")
    test_api_key(api_key)
    print()
    
    print("=" * 70)
    print("✅ 设置完成！")
    print("=" * 70)
    print()
    print("📝 保存以下信息:")
    print(f"   用户ID: {user_id}")
    print(f"   API Key: {api_key}")
    print(f"   Access Token: {tokens['access_token']}")
    print(f"   Refresh Token: {tokens['refresh_token']}")
    print()
    print("💡 使用示例:")
    print(f"   curl -X POST {API_BASE}/api/search \\")
    print(f"     -H 'Authorization: Bearer {api_key}' \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"categories\": [\"tech\"], \"max_results\": 10}}'")

if __name__ == "__main__":
    main()

