"""
Vercel部署问题诊断脚本
检查可能的问题并提供修复建议
"""
import os
import sys

def check_file_structure():
    """检查文件结构"""
    print("=" * 70)
    print("1. 检查文件结构")
    print("=" * 70)
    
    required_files = [
        'api/index.py',
        'api/health.py',
        'api/search.py',
        'api/download.py',
        'api/test.py',
        'vercel.json',
        'requirements.txt'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - 缺失")
    
    print()

def check_handler_format():
    """检查handler函数格式"""
    print("=" * 70)
    print("2. 检查handler函数格式")
    print("=" * 70)
    
    api_files = ['api/index.py', 'api/health.py', 'api/search.py', 'api/download.py', 'api/test.py']
    
    for file in api_files:
        if not os.path.exists(file):
            continue
        
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        has_handler = 'def handler(' in content
        has_return_dict = "'statusCode'" in content or '"statusCode"' in content
        
        status = "✅" if (has_handler and has_return_dict) else "⚠️"
        print(f"{status} {file}:")
        print(f"   - handler函数: {'✅' if has_handler else '❌'}")
        print(f"   - 返回字典格式: {'✅' if has_return_dict else '❌'}")
    
    print()

def check_imports():
    """检查导入语句"""
    print("=" * 70)
    print("3. 检查导入语句")
    print("=" * 70)
    
    api_files = ['api/search.py', 'api/download.py']
    
    for file in api_files:
        if not os.path.exists(file):
            continue
        
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        has_sys_path = 'sys.path.insert' in content
        has_import = 'from src.news_tools' in content
        
        print(f"{file}:")
        print(f"   - sys.path设置: {'✅' if has_sys_path else '❌'}")
        print(f"   - 导入src模块: {'✅' if has_import else '❌'}")
    
    print()

def check_requirements():
    """检查requirements.txt"""
    print("=" * 70)
    print("4. 检查requirements.txt")
    print("=" * 70)
    
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt 不存在")
        return
    
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    required_packages = [
        'httpx',
        'feedparser',
        'beautifulsoup4',
        'python-dateutil',
        'lxml',
        'PyGithub'
    ]
    
    for package in required_packages:
        if package.lower() in content.lower():
            print(f"✅ {package}")
        else:
            print(f"❌ {package} - 缺失")
    
    print()

def check_vercel_config():
    """检查vercel.json配置"""
    print("=" * 70)
    print("5. 检查vercel.json配置")
    print("=" * 70)
    
    if not os.path.exists('vercel.json'):
        print("❌ vercel.json 不存在")
        return
    
    import json
    try:
        with open('vercel.json', 'r') as f:
            config = json.load(f)
        
        print("✅ vercel.json 格式正确")
        print(f"   版本: {config.get('version', 'N/A')}")
        
        builds = config.get('builds', [])
        print(f"   构建配置: {len(builds)} 个")
        for build in builds:
            print(f"     - {build.get('src', 'N/A')} -> {build.get('use', 'N/A')}")
        
        routes = config.get('routes', [])
        print(f"   路由配置: {len(routes)} 个")
        for route in routes:
            print(f"     - {route.get('src', 'N/A')} -> {route.get('dest', 'N/A')}")
        
    except json.JSONDecodeError as e:
        print(f"❌ vercel.json JSON格式错误: {e}")
    except Exception as e:
        print(f"❌ 读取vercel.json失败: {e}")
    
    print()

def suggest_fixes():
    """提供修复建议"""
    print("=" * 70)
    print("6. 修复建议")
    print("=" * 70)
    
    print("""
根据测试结果，所有API端点都返回 FUNCTION_INVOCATION_FAILED。

可能的原因和解决方案：

1. **Vercel Python运行时格式问题**
   - 当前使用字典返回格式可能不正确
   - 建议：查看Vercel Functions日志获取详细错误
   - 可能需要使用不同的返回格式

2. **导入路径问题**
   - sys.path.insert可能不正确
   - 建议：检查Vercel环境中的路径设置

3. **依赖安装问题**
   - 某些依赖可能在Vercel环境中安装失败
   - 建议：查看Vercel构建日志

4. **环境变量问题**
   - 虽然设置了ENABLE_NEWS_FILTER，但可能还有其他问题
   - 建议：检查Vercel Dashboard中的环境变量

**立即行动：**
1. 访问 Vercel Dashboard → Functions → 查看日志
2. 复制完整的错误堆栈
3. 根据错误信息进行针对性修复
""")

def main():
    """运行所有检查"""
    print("\n" + "=" * 70)
    print("  Vercel部署问题诊断")
    print("=" * 70 + "\n")
    
    check_file_structure()
    check_handler_format()
    check_imports()
    check_requirements()
    check_vercel_config()
    suggest_fixes()
    
    print("=" * 70)
    print("诊断完成")
    print("=" * 70)

if __name__ == '__main__':
    main()

