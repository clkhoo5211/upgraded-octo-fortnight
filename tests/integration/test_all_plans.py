#!/usr/bin/env python3
"""
完整API测试脚本 - 测试所有配套
1. API提供者（管理员功能）
2. 普通用户免费配套 (Free)
3. 基础配套 (Basic)
4. 高级配套 (Premium)
"""
import os
import sys
import requests
import json
import time
from datetime import datetime

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

# 设置环境变量（如果未设置）
if 'ADMIN_SECRET' not in os.environ:
    os.environ['ADMIN_SECRET'] = '0x6c103441fed1fa4a908b76223de0e697097eed77'
if 'REGISTRATION_SECRET' not in os.environ:
    os.environ['REGISTRATION_SECRET'] = '0x6c103441fed1fa4a908b76223de0e697097eed77'
if 'TEST_API_BASE' not in os.environ:
    os.environ['TEST_API_BASE'] = 'https://upgraded-octo-fortnight.vercel.app'

from tests.config import API_BASE, ADMIN_SECRET, REGISTRATION_SECRET, validate_test_config

# 验证配置
try:
    validate_test_config()
except ValueError as e:
    print(f"❌ 配置错误: {e}")
    sys.exit(1)

def print_section(title):
    """打印章节标题"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def print_result(label, response, show_body=True):
    """打印请求结果"""
    status_icon = "✅" if response.status_code in [200, 201] else "❌"
    print(f"{status_icon} {label}")
    print(f"   状态码: {response.status_code}")
    if show_body:
        try:
            data = response.json()
            # 隐藏敏感信息
            if 'api_key' in data:
                data['api_key'] = data['api_key'][:30] + "..."
            if 'access_token' in data.get('tokens', {}):
                data['tokens']['access_token'] = data['tokens']['access_token'][:30] + "..."
            print(f"   响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        except:
            print(f"   响应: {response.text[:200]}")
    print()

def test_scenario_1_provider():
    """场景1: API提供者（管理员功能）"""
    print_section("场景1: API提供者（管理员功能）")
    
    headers = {
        "Authorization": f"Bearer {ADMIN_SECRET}",
        "Content-Type": "application/json"
    }
    
    # 1.1 创建用户
    print("1.1 创建用户（管理员操作）")
    user_data = {
        "user_id": f"admin-test-{int(time.time())}@example.com",
        "rate_limit": 1000,
        "plan": "basic"
    }
    response = requests.post(
        f"{API_BASE}/api/auth/user",
        headers=headers,
        json=user_data,
        timeout=30
    )
    print_result("创建用户", response)
    
    user_id = None
    if response.status_code == 201:
        user_id = response.json().get('user_id')
        print(f"✅ 用户创建成功: {user_id}\n")
    else:
        print(f"❌ 用户创建失败: {response.text[:200]}\n")
    
    # 1.2 查看所有用户
    print("1.2 查看所有用户")
    response = requests.get(
        f"{API_BASE}/api/auth/users",
        headers=headers,
        timeout=30
    )
    print_result("所有用户列表", response, show_body=False)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 找到 {data.get('total', 0)} 个用户\n")
    
    # 1.3 查看所有API Keys
    print("1.3 查看所有API Keys")
    response = requests.get(
        f"{API_BASE}/api/auth/api-keys",
        headers=headers,
        timeout=30
    )
    print_result("所有API Keys", response, show_body=False)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 找到 {data.get('total', 0)} 个API Keys\n")
    
    return user_id

def test_scenario_plan(plan_name):
    """测试单个计划"""
    print_section(f"测试 {plan_name.upper()} 计划")
    
    results = {}
    
    # 1. 注册用户
    print(f"1. 注册 {plan_name} 用户")
    register_data = {
        "email": f"{plan_name}-test-{int(time.time())}@example.com",
        "name": f"{plan_name.title()} Test User",
        "plan": plan_name,
        "registration_secret": REGISTRATION_SECRET
    }
    response = requests.post(
        f"{API_BASE}/api/register",
        json=register_data,
        timeout=30
    )
    print_result(f"注册 {plan_name} 用户", response)
    
    if response.status_code not in [200, 201]:
        print(f"❌ {plan_name} 用户注册失败\n")
        return None
    
    data = response.json()
    if not data.get('success'):
        print(f"❌ {plan_name} 用户注册失败\n")
        return None
    
    access_token = data['tokens']['access_token']
    refresh_token = data['tokens']['refresh_token']
    user_id = data['user_id']
    plan = data['plan']
    is_paid = data['tokens'].get('is_paid', False)
    expires_in = data['tokens']['expires_in']
    rate_limit = data.get('rate_limit', 100)
    
    print(f"✅ {plan_name} 用户注册成功!")
    print(f"   用户ID: {user_id}")
    print(f"   计划: {plan}")
    print(f"   是否付费: {is_paid}")
    print(f"   速率限制: {rate_limit} 请求/小时")
    print(f"   Token有效期: {expires_in}秒 ({expires_in/86400:.1f}天)\n")
    
    # 2. 创建API Key
    print(f"2. 创建 {plan_name} API Key")
    api_key_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    api_key_response = requests.post(
        f"{API_BASE}/api/auth/api-key",
        headers=api_key_headers,
        json={"name": f"{plan_name}-key"},
        timeout=30
    )
    print_result(f"创建 {plan_name} API Key", api_key_response)
    
    api_key = None
    if api_key_response.status_code == 201:
        api_key_data = api_key_response.json()
        api_key = api_key_data.get('api_key')
        print(f"✅ {plan_name} API Key创建成功: {api_key[:30]}...\n")
    
    # 3. 检查Token状态
    print(f"3. 检查 {plan_name} Token状态")
    status_response = requests.post(
        f"{API_BASE}/api/auth/token-status",
        json={"access_token": access_token},
        timeout=30
    )
    print_result(f"{plan_name} Token状态", status_response)
    
    # 4. 查看用户信息
    print(f"4. 查看 {plan_name} 用户信息")
    token_to_use = api_key if api_key else access_token
    me_response = requests.get(
        f"{API_BASE}/api/auth/me",
        headers={"Authorization": f"Bearer {token_to_use}"},
        timeout=30
    )
    print_result(f"{plan_name} 用户信息", me_response)
    
    # 5. 查看速率限制
    print(f"5. 查看 {plan_name} 速率限制")
    rate_limit_response = requests.get(
        f"{API_BASE}/api/auth/rate-limit",
        headers={"Authorization": f"Bearer {token_to_use}"},
        timeout=30
    )
    print_result(f"{plan_name} 速率限制", rate_limit_response)
    
    # 6. 测试Token续期（仅付费计划）
    if is_paid:
        print(f"6. 测试 {plan_name} Token续期")
        renew_response = requests.post(
            f"{API_BASE}/api/auth/renew",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"access_token": access_token},
            timeout=30
        )
        print_result(f"{plan_name} Token续期", renew_response)
        
        if renew_response.status_code == 200:
            renew_data = renew_response.json()
            new_token = renew_data['tokens']['access_token']
            print(f"✅ {plan_name} Token续期成功!")
            print(f"   新Token: {new_token[:30]}...")
            print(f"   新有效期: {renew_data['tokens']['expires_in']}秒 ({renew_data['tokens']['expires_in']/86400:.1f}天)\n")
            access_token = new_token  # 使用新Token
        else:
            print(f"❌ {plan_name} Token续期失败\n")
    else:
        print(f"6. {plan_name} 计划不支持Token续期（跳过）\n")
    
    # 7. 测试升级计划（如果当前是basic，升级到premium）
    if plan_name == "basic":
        print(f"7. 测试从 {plan_name} 升级到 premium")
        upgrade_response = requests.post(
            f"{API_BASE}/api/upgrade",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"plan": "premium"},
            timeout=30
        )
        print_result(f"升级计划", upgrade_response)
        
        if upgrade_response.status_code == 200:
            upgrade_data = upgrade_response.json()
            print(f"✅ 计划升级成功!")
            print(f"   从 {upgrade_data['old_plan']} 升级到 {upgrade_data['new_plan']}")
            print(f"   新速率限制: {upgrade_data['rate_limit']}/小时\n")
            access_token = upgrade_data['tokens']['access_token']
            plan = "premium"
    
    # 8. 使用API Key搜索新闻
    print(f"8. 使用 {plan_name} API Key搜索新闻")
    if api_key:
        search_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        search_response = requests.post(
            f"{API_BASE}/api/search",
            headers=search_headers,
            json={
                "categories": ["tech"],
                "max_results": 5,
                "date_range": "today_and_yesterday"
            },
            timeout=30
        )
        print_result(f"{plan_name} 搜索新闻", search_response, show_body=False)
        if search_response.status_code == 200:
            search_data = search_response.json()
            print(f"✅ {plan_name} 搜索成功，找到 {search_data.get('count', 0)} 条新闻\n")
        else:
            print(f"❌ {plan_name} 搜索失败: {search_response.text[:200]}\n")
    
    results = {
        "user_id": user_id,
        "access_token": access_token,
        "api_key": api_key,
        "plan": plan,
        "is_paid": is_paid,
        "rate_limit": rate_limit
    }
    
    return results

def test_root_endpoint():
    """测试根路径是否需要认证"""
    print_section("测试根路径认证")
    
    # 1. 无Token访问
    print("1. 无Token访问根路径")
    response = requests.get(f"{API_BASE}/", timeout=30)
    print_result("无Token访问", response)
    
    if response.status_code == 401:
        print("✅ 正确：未授权访问被拒绝\n")
    else:
        print("❌ 错误：应该返回401未授权\n")
    
    # 2. 使用Token访问
    print("2. 使用Token访问根路径")
    # 先注册一个免费用户获取Token
    register_data = {
        "email": f"test-root-{int(time.time())}@example.com",
        "plan": "free",
        "registration_secret": REGISTRATION_SECRET
    }
    register_response = requests.post(
        f"{API_BASE}/api/register",
        json=register_data,
        timeout=30
    )
    
    if register_response.status_code in [200, 201]:
        token = register_response.json()['tokens']['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/", headers=headers, timeout=30)
        print_result("使用Token访问", response)
        
        if response.status_code == 200:
            print("✅ 正确：已授权用户可以访问\n")
        else:
            print(f"❌ 错误：应该返回200成功\n")

def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("  完整API功能测试 - 所有配套")
    print("="*80)
    print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API地址: {API_BASE}\n")
    
    all_results = {}
    
    try:
        # 测试根路径认证
        test_root_endpoint()
        
        # 场景1: API提供者
        admin_user = test_scenario_1_provider()
        all_results['admin'] = admin_user
        
        # 场景2-4: 测试所有配套
        plans = ["free", "basic", "premium"]
        for plan in plans:
            result = test_scenario_plan(plan)
            all_results[plan] = result
        
        # 总结
        print_section("测试总结")
        print("✅ 场景1: API提供者（管理员功能）")
        if all_results.get('admin'):
            print(f"   创建用户: {all_results['admin']}")
        
        for plan in plans:
            result = all_results.get(plan)
            if result:
                print(f"✅ {plan.upper()}计划:")
                print(f"   用户ID: {result['user_id']}")
                print(f"   计划: {result['plan']}")
                print(f"   是否付费: {result['is_paid']}")
                print(f"   速率限制: {result['rate_limit']}/小时")
                print(f"   API Key: {'已创建' if result['api_key'] else '未创建'}")
            else:
                print(f"❌ {plan.upper()}计划: 测试失败")
        
        print("\n" + "="*80)
        print("  所有测试完成！")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

