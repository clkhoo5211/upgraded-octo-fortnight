"""
完整的API接口和功能测试脚本
"""
import requests
import json
import sys
from datetime import datetime

# API基础URL
BASE_URL = "https://upgraded-octo-fortnight.vercel.app"

# 测试结果
test_results = []

def print_section(title):
    """打印测试章节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_endpoint(name, method, url, data=None, headers=None, expected_status=200):
    """测试API端点"""
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=30)
        else:
            return False, f"不支持的HTTP方法: {method}"
        
        status_ok = response.status_code == expected_status
        try:
            json_data = response.json()
            json_ok = True
        except:
            json_data = response.text
            json_ok = False
        
        result = {
            'name': name,
            'method': method,
            'url': url,
            'status_code': response.status_code,
            'expected_status': expected_status,
            'status_ok': status_ok,
            'is_json': json_ok,
            'response': json_data if json_ok else json_data[:200],
            'success': status_ok and json_ok
        }
        
        return True, result
    except requests.exceptions.RequestException as e:
        return False, {'error': str(e), 'name': name, 'url': url}

def run_tests():
    """运行所有测试"""
    print_section("🚀 开始API接口和功能测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API基础URL: {BASE_URL}")
    
    # 测试1: 健康检查端点
    print_section("测试1: 健康检查端点 (/api/health)")
    success, result = test_endpoint(
        "健康检查",
        "GET",
        f"{BASE_URL}/api/health"
    )
    test_results.append(result)
    if success:
        print(f"✅ 状态码: {result['status_code']}")
        if result['is_json']:
            print(f"✅ 返回JSON格式")
            if isinstance(result['response'], dict):
                print(f"   服务状态: {result['response'].get('status', 'N/A')}")
                print(f"   服务名称: {result['response'].get('service', 'N/A')}")
        else:
            print(f"⚠️ 返回非JSON格式: {result['response'][:100]}")
    else:
        print(f"❌ 测试失败: {result}")
    
    # 测试2: API首页
    print_section("测试2: API首页 (/)")
    success, result = test_endpoint(
        "API首页",
        "GET",
        f"{BASE_URL}/"
    )
    test_results.append(result)
    if success:
        print(f"✅ 状态码: {result['status_code']}")
        if result['is_json']:
            print(f"✅ 返回JSON格式")
            if isinstance(result['response'], dict):
                print(f"   服务名称: {result['response'].get('service', 'N/A')}")
                print(f"   版本: {result['response'].get('version', 'N/A')}")
                print(f"   状态: {result['response'].get('status', 'N/A')}")
        else:
            print(f"⚠️ 返回非JSON格式: {result['response'][:100]}")
    else:
        print(f"❌ 测试失败: {result}")
    
    # 测试3: 测试端点
    print_section("测试3: 测试端点 (/api/test)")
    success, result = test_endpoint(
        "测试端点",
        "GET",
        f"{BASE_URL}/api/test"
    )
    test_results.append(result)
    if success:
        print(f"✅ 状态码: {result['status_code']}")
        if result['is_json']:
            print(f"✅ 返回JSON格式")
            print(f"   响应: {json.dumps(result['response'], ensure_ascii=False, indent=2)[:200]}")
        else:
            print(f"⚠️ 返回非JSON格式: {result['response'][:100]}")
    else:
        print(f"❌ 测试失败: {result}")
    
    # 测试4: 搜索API - GET方式
    print_section("测试4: 搜索API - GET方式 (/api/search)")
    success, result = test_endpoint(
        "搜索API (GET)",
        "GET",
        f"{BASE_URL}/api/search",
        data={"keywords": "technology", "max_results": 3}
    )
    test_results.append(result)
    if success:
        print(f"✅ 状态码: {result['status_code']}")
        if result['is_json']:
            print(f"✅ 返回JSON格式")
            if isinstance(result['response'], dict):
                print(f"   成功: {result['response'].get('success', 'N/A')}")
                print(f"   新闻数量: {result['response'].get('count', 0)}")
                if result['response'].get('news'):
                    print(f"   第一条新闻标题: {result['response']['news'][0].get('title', 'N/A')[:50]}")
        else:
            print(f"⚠️ 返回非JSON格式: {result['response'][:100]}")
    else:
        print(f"❌ 测试失败: {result}")
    
    # 测试5: 搜索API - POST方式
    print_section("测试5: 搜索API - POST方式 (/api/search)")
    success, result = test_endpoint(
        "搜索API (POST)",
        "POST",
        f"{BASE_URL}/api/search",
        data={"keywords": "AI", "max_results": 2, "languages": "en"}
    )
    test_results.append(result)
    if success:
        print(f"✅ 状态码: {result['status_code']}")
        if result['is_json']:
            print(f"✅ 返回JSON格式")
            if isinstance(result['response'], dict):
                print(f"   成功: {result['response'].get('success', 'N/A')}")
                print(f"   新闻数量: {result['response'].get('count', 0)}")
        else:
            print(f"⚠️ 返回非JSON格式: {result['response'][:100]}")
    else:
        print(f"❌ 测试失败: {result}")
    
    # 测试6: 下载API - 缺少参数
    print_section("测试6: 下载API - 错误处理 (缺少news_url)")
    success, result = test_endpoint(
        "下载API (缺少参数)",
        "POST",
        f"{BASE_URL}/api/download",
        data={},
        expected_status=400
    )
    test_results.append(result)
    if success:
        print(f"✅ 状态码: {result['status_code']} (预期400)")
        if result['is_json']:
            print(f"✅ 返回JSON格式")
            if isinstance(result['response'], dict):
                print(f"   错误信息: {result['response'].get('error', 'N/A')}")
        else:
            print(f"⚠️ 返回非JSON格式: {result['response'][:100]}")
    else:
        print(f"❌ 测试失败: {result}")
    
    # 测试7: 下载API - 有效请求
    print_section("测试7: 下载API - 有效请求")
    success, result = test_endpoint(
        "下载API (有效请求)",
        "POST",
        f"{BASE_URL}/api/download",
        data={"news_url": "https://news.ycombinator.com/item?id=1"}
    )
    test_results.append(result)
    if success:
        print(f"✅ 状态码: {result['status_code']}")
        if result['is_json']:
            print(f"✅ 返回JSON格式")
            if isinstance(result['response'], dict):
                print(f"   成功: {result['response'].get('success', 'N/A')}")
                print(f"   URL: {result['response'].get('url', 'N/A')}")
        else:
            print(f"⚠️ 返回非JSON格式: {result['response'][:100]}")
    else:
        print(f"❌ 测试失败: {result}")
    
    # 测试8: CORS支持
    print_section("测试8: CORS支持检查")
    try:
        response = requests.options(
            f"{BASE_URL}/api/health",
            headers={"Origin": "https://example.com"},
            timeout=10
        )
        cors_header = response.headers.get('Access-Control-Allow-Origin', '')
        if cors_header:
            print(f"✅ CORS头存在: {cors_header}")
            test_results.append({'name': 'CORS支持', 'success': True})
        else:
            print(f"⚠️ CORS头不存在")
            test_results.append({'name': 'CORS支持', 'success': False})
    except Exception as e:
        print(f"❌ CORS测试失败: {e}")
        test_results.append({'name': 'CORS支持', 'success': False, 'error': str(e)})
    
    # 生成测试报告
    print_section("📊 测试报告总结")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r.get('success', False))
    failed_tests = total_tests - passed_tests
    
    print(f"总测试数: {total_tests}")
    print(f"✅ 通过: {passed_tests}")
    print(f"❌ 失败: {failed_tests}")
    print(f"成功率: {passed_tests/total_tests*100:.1f}%")
    
    print("\n详细结果:")
    for i, result in enumerate(test_results, 1):
        status = "✅" if result.get('success', False) else "❌"
        name = result.get('name', f'测试{i}')
        if 'status_code' in result:
            print(f"  {status} {name}: HTTP {result['status_code']}")
        else:
            print(f"  {status} {name}: {result.get('error', '未知错误')}")
    
    return passed_tests == total_tests

if __name__ == '__main__':
    try:
        success = run_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

