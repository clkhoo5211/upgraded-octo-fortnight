#!/usr/bin/env python3
"""
API测试脚本 - 测试三种场景
1. API提供者（管理员功能）
2. 普通用户免费配套
3. 其他各配套测试（Basic和Premium）
"""
import os
import sys
import requests
import json
import time
from datetime import datetime

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

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
    print(f"📌 {label}")
    print(f"   状态码: {response.status_code}")
    if show_body:
        try:
            data = response.json()
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
        "user_id": f"test-user-{int(time.time())}@example.com",
        "rate_limit": 1000,
        "plan": "basic"
    }
    response = requests.post(
        f"{API_BASE}/api/auth/user",
        headers=headers,
        json=user_data
    )
    print_result("创建用户", response)
    
    if response.status_code == 201:
        user_id = response.json().get('user_id')
        print(f"✅ 用户创建成功: {user_id}\n")
        return user_id
    else:
        print("❌ 用户创建失败\n")
        return None

def test_scenario_2_free_user():
    """场景2: 普通用户免费配套"""
    print_section("场景2: 普通用户免费配套")
    
    # 2.1 注册免费用户
    print("2.1 注册免费用户")
    register_data = {
        "email": f"free-user-{int(time.time())}@example.com",
        "name": "Free User",
        "plan": "free",
        "registration_secret": REGISTRATION_SECRET
    }
    response = requests.post(
        f"{API_BASE}/api/register",
        json=register_data
    )
    print_result("注册免费用户", response)
    
    if response.status_code not in [200, 201]:
        print("❌ 注册失败\n")
        return None
    
    data = response.json()
    if not data.get('success'):
        print("❌ 注册失败\n")
        return None
    
    access_token = data['tokens']['access_token']
    refresh_token = data['tokens']['refresh_token']
    user_id = data['user_id']
    plan = data['plan']
    
    print(f"✅ 注册成功!")
    print(f"   用户ID: {user_id}")
    print(f"   计划: {plan}")
    print(f"   Access Token: {access_token[:30]}...")
    print(f"   Token有效期: {data['tokens']['expires_in']}秒 ({data['tokens']['expires_in']/3600:.1f}小时)\n")
    
    # 2.2 创建API Key
    print("2.2 创建API Key")
    api_key_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    api_key_response = requests.post(
        f"{API_BASE}/api/auth/api-key",
        headers=api_key_headers,
        json={"name": "free-user-key"}
    )
    print_result("创建API Key", api_key_response)
    
    api_key = None
    if api_key_response.status_code == 201:
        api_key_data = api_key_response.json()
        api_key = api_key_data.get('api_key')
        print(f"✅ API Key创建成功: {api_key[:30]}...\n")
    
    # 2.3 检查Token状态
    print("2.3 检查Token状态")
    status_response = requests.post(
        f"{API_BASE}/api/auth/token-status",
        json={"access_token": access_token}
    )
    print_result("Token状态", status_response)
    
    # 2.4 使用API Key搜索新闻
    print("2.4 使用API Key搜索新闻")
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
            }
        )
        print_result("搜索新闻", search_response, show_body=False)
        if search_response.status_code == 200:
            search_data = search_response.json()
            print(f"✅ 搜索成功，找到 {search_data.get('count', 0)} 条新闻\n")
        else:
            print(f"❌ 搜索失败\n")
    
    # 2.5 查看用户信息
    print("2.5 查看用户信息")
    me_response = requests.get(
        f"{API_BASE}/api/auth/me",
        headers=api_key_headers if api_key else {"Authorization": f"Bearer {access_token}"}
    )
    print_result("用户信息", me_response)
    
    # 2.6 查看速率限制
    print("2.6 查看速率限制")
    rate_limit_response = requests.get(
        f"{API_BASE}/api/auth/rate-limit",
        headers=api_key_headers if api_key else {"Authorization": f"Bearer {access_token}"}
    )
    print_result("速率限制", rate_limit_response)
    
    return {
        "user_id": user_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "api_key": api_key,
        "plan": plan
    }

def test_scenario_3_paid_plans():
    """场景3: 其他各配套测试（Basic和Premium）"""
    print_section("场景3: 其他各配套测试（Basic和Premium）")
    
    plans = ["basic", "premium"]
    results = {}
    
    for plan in plans:
        print(f"\n{'='*80}")
        print(f"  测试 {plan.upper()} 计划")
        print(f"{'='*80}\n")
        
        # 3.1 注册付费用户
        print(f"3.1 注册 {plan} 用户")
        register_data = {
            "email": f"{plan}-user-{int(time.time())}@example.com",
            "name": f"{plan.title()} User",
            "plan": plan,
            "registration_secret": REGISTRATION_SECRET
        }
        response = requests.post(
            f"{API_BASE}/api/register",
            json=register_data
        )
        print_result(f"注册 {plan} 用户", response)
        
        if response.status_code not in [200, 201]:
            print(f"❌ {plan} 用户注册失败\n")
            continue
        
        data = response.json()
        if not data.get('success'):
            print(f"❌ {plan} 用户注册失败\n")
            continue
        
        access_token = data['tokens']['access_token']
        refresh_token = data['tokens']['refresh_token']
        user_id = data['user_id']
        is_paid = data['tokens'].get('is_paid', False)
        expires_in = data['tokens']['expires_in']
        
        print(f"✅ {plan} 用户注册成功!")
        print(f"   用户ID: {user_id}")
        print(f"   计划: {plan}")
        print(f"   是否付费: {is_paid}")
        print(f"   Token有效期: {expires_in}秒 ({expires_in/86400:.1f}天)\n")
        
        # 3.2 检查Token状态
        print(f"3.2 检查 {plan} Token状态")
        status_response = requests.post(
            f"{API_BASE}/api/auth/token-status",
            json={"access_token": access_token}
        )
        print_result(f"{plan} Token状态", status_response)
        
        # 3.3 创建API Key
        print(f"3.3 创建 {plan} API Key")
        api_key_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        api_key_response = requests.post(
            f"{API_BASE}/api/auth/api-key",
            headers=api_key_headers,
            json={"name": f"{plan}-user-key"}
        )
        print_result(f"创建 {plan} API Key", api_key_response)
        
        api_key = None
        if api_key_response.status_code == 201:
            api_key_data = api_key_response.json()
            api_key = api_key_data.get('api_key')
            print(f"✅ {plan} API Key创建成功: {api_key[:30]}...\n")
        
        # 3.4 测试Token续期（仅付费计划）
        if is_paid:
            print(f"3.4 测试 {plan} Token续期")
            renew_response = requests.post(
                f"{API_BASE}/api/auth/renew",
                headers={"Authorization": f"Bearer {access_token}"},
                json={"access_token": access_token}
            )
            print_result(f"{plan} Token续期", renew_response)
            
            if renew_response.status_code == 200:
                renew_data = renew_response.json()
                new_token = renew_data['tokens']['access_token']
                print(f"✅ {plan} Token续期成功!")
                print(f"   新Token: {new_token[:30]}...")
                print(f"   新有效期: {renew_data['tokens']['expires_in']}秒 ({renew_data['tokens']['expires_in']/86400:.1f}天)\n")
                access_token = new_token  # 使用新Token
            else:
                print(f"❌ {plan} Token续期失败\n")
        else:
            print(f"3.4 {plan} 计划不支持Token续期（跳过）\n")
        
        # 3.5 测试升级计划（如果当前是basic，升级到premium）
        if plan == "basic":
            print(f"3.5 测试从 {plan} 升级到 premium")
            upgrade_response = requests.post(
                f"{API_BASE}/api/upgrade",
                headers={"Authorization": f"Bearer {access_token}"},
                json={"plan": "premium"}
            )
            print_result(f"升级计划", upgrade_response)
            
            if upgrade_response.status_code == 200:
                upgrade_data = upgrade_response.json()
                print(f"✅ 计划升级成功!")
                print(f"   从 {upgrade_data['old_plan']} 升级到 {upgrade_data['new_plan']}")
                print(f"   新速率限制: {upgrade_data['rate_limit']}/小时")
                print(f"   新Token: {upgrade_data['tokens']['access_token'][:30]}...\n")
        
        # 3.6 使用API Key搜索新闻
        print(f"3.6 使用 {plan} API Key搜索新闻")
        if api_key:
            search_headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            search_response = requests.post(
                f"{API_BASE}/api/search",
                headers=search_headers,
                json={
                    "categories": ["tech", "finance"],
                    "max_results": 10,
                    "date_range": "today_and_yesterday"
                }
            )
            print_result(f"{plan} 搜索新闻", search_response, show_body=False)
            if search_response.status_code == 200:
                search_data = search_response.json()
                print(f"✅ {plan} 搜索成功，找到 {search_data.get('count', 0)} 条新闻\n")
            else:
                print(f"❌ {plan} 搜索失败\n")
        
        results[plan] = {
            "user_id": user_id,
            "access_token": access_token,
            "api_key": api_key,
            "plan": plan,
            "is_paid": is_paid
        }
    
    return results

def test_admin_functions():
    """测试管理员功能"""
    print_section("管理员功能测试")
    
    headers = {
        "Authorization": f"Bearer {ADMIN_SECRET}",
        "Content-Type": "application/json"
    }
    
    # 查看所有用户
    print("查看所有用户")
    users_response = requests.get(
        f"{API_BASE}/api/auth/users",
        headers=headers
    )
    print_result("所有用户列表", users_response)
    
    # 查看所有API Keys
    print("查看所有API Keys")
    api_keys_response = requests.get(
        f"{API_BASE}/api/auth/api-keys",
        headers=headers
    )
    print_result("所有API Keys", api_keys_response)

def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("  API功能测试 - 三种场景")
    print("="*80)
    print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API地址: {API_BASE}\n")
    
    try:
        # 场景1: API提供者
        test_scenario_1_provider()
        
        # 场景2: 普通用户免费配套
        free_user_result = test_scenario_2_free_user()
        
        # 场景3: 其他各配套测试
        paid_plans_results = test_scenario_3_paid_plans()
        
        # 管理员功能测试
        test_admin_functions()
        
        # 总结
        print_section("测试总结")
        print("✅ 场景1: API提供者（管理员功能） - 完成")
        if free_user_result:
            print(f"✅ 场景2: 普通用户免费配套 - 完成")
            print(f"   用户ID: {free_user_result['user_id']}")
            print(f"   计划: {free_user_result['plan']}")
        else:
            print("❌ 场景2: 普通用户免费配套 - 失败")
        
        print(f"✅ 场景3: 其他各配套测试 - 完成")
        for plan, result in paid_plans_results.items():
            if result:
                print(f"   {plan.upper()}计划: ✅")
                print(f"      用户ID: {result['user_id']}")
                print(f"      是否付费: {result['is_paid']}")
        
        print("\n" + "="*80)
        print("  所有测试完成！")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

