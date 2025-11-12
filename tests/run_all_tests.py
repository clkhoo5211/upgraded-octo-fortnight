#!/usr/bin/env python3
"""
运行所有测试 - 验证COMPLETE_INTEGRATION_GUIDE.md中的所有功能
"""
import os
import sys
import subprocess
from pathlib import Path

# 设置环境变量
os.environ['ADMIN_SECRET'] = '0x6c103441fed1fa4a908b76223de0e697097eed77'
os.environ['REGISTRATION_SECRET'] = '0x6c103441fed1fa4a908b76223de0e697097eed77'
os.environ['TEST_API_BASE'] = 'https://upgraded-octo-fortnight.vercel.app'

# 添加项目根目录到路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

def print_header(title):
    """打印测试标题"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def run_test(test_file, description):
    """运行单个测试文件"""
    print_header(f"测试: {description}")
    print(f"运行文件: {test_file}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            cwd=str(project_root),
            capture_output=False,
            text=True,
            timeout=300  # 5分钟超时
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"❌ 测试超时: {test_file}")
        return False
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        return False

def main():
    """主测试函数"""
    print_header("完整功能测试 - 验证COMPLETE_INTEGRATION_GUIDE.md中的所有功能")
    print(f"API地址: {os.environ['TEST_API_BASE']}")
    print(f"测试时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 测试文件列表
    tests = [
        {
            'file': project_root / 'tests' / 'integration' / 'test_all_plans.py',
            'description': '所有用户计划测试（Free/Basic/Premium）'
        },
        {
            'file': project_root / 'tests' / 'integration' / 'test_api_scenarios.py',
            'description': 'API场景测试（管理员、免费用户、付费用户）'
        },
        {
            'file': project_root / 'tests' / 'auth' / 'test_token_expiry.py',
            'description': 'Token过期和刷新测试'
        },
        {
            'file': project_root / 'tests' / 'api' / 'verify_archive.py',
            'description': '归档功能验证测试'
        },
    ]
    
    results = {}
    
    for test in tests:
        if test['file'].exists():
            success = run_test(test['file'], test['description'])
            results[test['description']] = success
        else:
            print(f"⚠️  测试文件不存在: {test['file']}")
            results[test['description']] = False
    
    # 总结
    print_header("测试总结")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    for desc, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status}: {desc}")
    
    print(f"\n总计: {total} 个测试")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")
    
    if failed == 0:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  有 {failed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())

