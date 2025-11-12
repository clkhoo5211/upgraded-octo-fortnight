"""
测试Token过期和刷新场景
"""
import requests
import json
import time
from datetime import datetime

API_BASE = "https://upgraded-octo-fortnight.vercel.app"
REGISTRATION_SECRET = "0x6c103441fed1fa4a908b76223de0e697097eed77"

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print('='*80)

def test_expired_access_token():
    """测试过期Access Token的行为"""
    print_section("测试1: 使用过期Access Token访问API")
    
    # 1. 注册用户
    email = f"expiry-test-{int(time.time())}@example.com"
    print(f"\n1. 注册用户: {email}")
    register_response = requests.post(
        f"{API_BASE}/api/register",
        json={'email': email, 'plan': 'free', 'registration_secret': REGISTRATION_SECRET}
    )
    
    if register_response.status_code != 201:
        print(f"❌ 注册失败: {register_response.status_code}")
        print(register_response.text)
        return
    
    register_data = register_response.json()
    access_token = register_data['tokens']['access_token']
    refresh_token = register_data['tokens']['refresh_token']
    
    print(f"✅ 注册成功")
    print(f"   Access Token: {access_token[:50]}...")
    print(f"   Refresh Token: {refresh_token[:50]}...")
    print(f"   过期时间: {register_data['tokens']['expires_at']}")
    
    # 2. 检查Token状态（应该有效）
    print(f"\n2. 检查Token状态（应该有效）")
    status_response = requests.post(
        f"{API_BASE}/api/auth/token-status",
        json={'access_token': access_token}
    )
    status_data = status_response.json()
    print(f"   状态码: {status_response.status_code}")
    print(f"   响应: {json.dumps(status_data, indent=2, ensure_ascii=False)}")
    
    if status_data.get('success') and status_data.get('status', {}).get('valid'):
        print("✅ Token当前有效")
    else:
        print("❌ Token状态异常")
    
    # 3. 使用Access Token访问API（应该成功）
    print(f"\n3. 使用Access Token访问API（应该成功）")
    search_response = requests.post(
        f"{API_BASE}/api/search",
        headers={'Authorization': f"Bearer {access_token}"},
        json={'categories': ['tech'], 'max_results': 1}
    )
    print(f"   状态码: {search_response.status_code}")
    if search_response.status_code == 200:
        print("✅ API访问成功")
    else:
        print(f"❌ API访问失败: {search_response.text[:200]}")
    
    # 4. 模拟Token过期（免费Token只有1小时，我们无法等待，但可以测试过期Token的验证）
    print(f"\n4. 测试Token过期验证逻辑")
    print("   注意: 免费Token有效期1小时，无法立即过期")
    print("   但我们可以测试token-status端点对过期Token的处理")
    
    # 5. 使用Refresh Token刷新（应该返回新的Access Token和Refresh Token）
    print(f"\n5. 使用Refresh Token刷新")
    refresh_response = requests.post(
        f"{API_BASE}/api/auth/refresh",
        json={'refresh_token': refresh_token}
    )
    print(f"   状态码: {refresh_response.status_code}")
    refresh_data = refresh_response.json()
    print(f"   响应: {json.dumps(refresh_data, indent=2, ensure_ascii=False)}")
    
    if refresh_response.status_code == 200 and refresh_data.get('success'):
        new_access_token = refresh_data['tokens']['access_token']
        new_refresh_token = refresh_data['tokens']['refresh_token']
        print(f"✅ Token刷新成功")
        print(f"   新Access Token: {new_access_token[:50]}...")
        print(f"   新Refresh Token: {new_refresh_token[:50]}...")
        print(f"   新过期时间: {refresh_data['tokens']['expires_at']}")
        
        # 验证新旧Token是否不同
        if new_access_token != access_token:
            print("✅ 返回了新的Access Token")
        else:
            print("⚠️  Access Token未变化")
        
        if new_refresh_token != refresh_token:
            print("✅ 返回了新的Refresh Token")
        else:
            print("⚠️  Refresh Token未变化")
        
        # 6. 使用新Token访问API
        print(f"\n6. 使用新Access Token访问API")
        new_search_response = requests.post(
            f"{API_BASE}/api/search",
            headers={'Authorization': f"Bearer {new_access_token}"},
            json={'categories': ['tech'], 'max_results': 1}
        )
        print(f"   状态码: {new_search_response.status_code}")
        if new_search_response.status_code == 200:
            print("✅ 新Token访问API成功")
        else:
            print(f"❌ 新Token访问失败: {new_search_response.text[:200]}")
    else:
        print(f"❌ Token刷新失败")

def test_paid_token_renewal():
    """测试付费Token续期"""
    print_section("测试2: 付费Token续期")
    
    # 1. 注册premium用户
    email = f"renew-test-{int(time.time())}@example.com"
    print(f"\n1. 注册premium用户: {email}")
    register_response = requests.post(
        f"{API_BASE}/api/register",
        json={'email': email, 'plan': 'premium', 'registration_secret': REGISTRATION_SECRET}
    )
    
    if register_response.status_code != 201:
        print(f"❌ 注册失败: {register_response.status_code}")
        print(register_response.text)
        return
    
    register_data = register_response.json()
    access_token = register_data['tokens']['access_token']
    refresh_token = register_data['tokens']['refresh_token']
    
    print(f"✅ 注册成功")
    print(f"   计划: {register_data['plan']}")
    print(f"   是否付费: {register_data['tokens']['is_paid']}")
    print(f"   Access Token: {access_token[:50]}...")
    print(f"   过期时间: {register_data['tokens']['expires_at']}")
    
    # 2. 检查Token状态
    print(f"\n2. 检查Token状态")
    status_response = requests.post(
        f"{API_BASE}/api/auth/token-status",
        json={'access_token': access_token}
    )
    status_data = status_response.json()
    print(f"   状态码: {status_response.status_code}")
    print(f"   响应: {json.dumps(status_data, indent=2, ensure_ascii=False)}")
    
    # 3. 续期Token（付费Token可以续期）
    print(f"\n3. 续期Token（付费Token）")
    renew_response = requests.post(
        f"{API_BASE}/api/auth/renew",
        headers={'Authorization': f"Bearer {access_token}"},
        json={'access_token': access_token}
    )
    print(f"   状态码: {renew_response.status_code}")
    renew_data = renew_response.json()
    print(f"   响应: {json.dumps(renew_data, indent=2, ensure_ascii=False)}")
    
    if renew_response.status_code == 200 and renew_data.get('success'):
        new_access_token = renew_data['tokens']['access_token']
        new_refresh_token = renew_data['tokens']['refresh_token']
        print(f"✅ Token续期成功")
        print(f"   新Access Token: {new_access_token[:50]}...")
        print(f"   新Refresh Token: {new_refresh_token[:50]}...")
        print(f"   新过期时间: {renew_data['tokens']['expires_at']}")
        
        # 验证新旧Token是否不同
        if new_access_token != access_token:
            print("✅ 返回了新的Access Token")
        else:
            print("⚠️  Access Token未变化")
        
        if new_refresh_token != refresh_token:
            print("✅ 返回了新的Refresh Token")
        else:
            print("⚠️  Refresh Token未变化")
    else:
        print(f"❌ Token续期失败")

def test_expired_token_api_access():
    """测试使用过期Token访问API的返回信息"""
    print_section("测试3: 使用过期Token访问API")
    
    # 创建一个Token，然后模拟过期（实际上无法立即过期，但可以测试验证逻辑）
    email = f"expired-api-test-{int(time.time())}@example.com"
    print(f"\n1. 注册用户: {email}")
    register_response = requests.post(
        f"{API_BASE}/api/register",
        json={'email': email, 'plan': 'free', 'registration_secret': REGISTRATION_SECRET}
    )
    
    if register_response.status_code != 201:
        print(f"❌ 注册失败")
        return
    
    register_data = register_response.json()
    access_token = register_data['tokens']['access_token']
    
    # 使用无效Token访问API（模拟过期）
    print(f"\n2. 使用无效Token访问API（模拟过期Token）")
    invalid_token = "at_invalid_token_12345"
    invalid_response = requests.post(
        f"{API_BASE}/api/search",
        headers={'Authorization': f"Bearer {invalid_token}"},
        json={'categories': ['tech'], 'max_results': 1}
    )
    print(f"   状态码: {invalid_response.status_code}")
    print(f"   响应: {json.dumps(invalid_response.json(), indent=2, ensure_ascii=False)}")
    
    if invalid_response.status_code == 401:
        print("✅ 正确返回401未授权")
    else:
        print("⚠️  未返回预期的401状态码")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  Token过期和刷新测试")
    print("="*80)
    
    try:
        test_expired_access_token()
        test_paid_token_renewal()
        test_expired_token_api_access()
        
        print("\n" + "="*80)
        print("  测试完成！")
        print("="*80)
    except Exception as e:
        import traceback
        print(f"\n❌ 测试出错: {e}")
        traceback.print_exc()

