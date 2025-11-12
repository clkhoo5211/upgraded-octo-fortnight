"""
完整的功能测试脚本
"""
import sys
import os

def test_imports():
    """测试所有模块导入"""
    print("=" * 60)
    print("测试1: 模块导入")
    print("=" * 60)
    
    try:
        from src.news_tools.news_searcher import NewsSearcher
        print("✅ NewsSearcher 导入成功")
    except Exception as e:
        print(f"❌ NewsSearcher 导入失败: {e}")
        return False
    
    try:
        from src.news_tools.content_downloader import ContentDownloader
        print("✅ ContentDownloader 导入成功")
    except Exception as e:
        print(f"❌ ContentDownloader 导入失败: {e}")
        return False
    
    try:
        from src.news_tools.news_filter import NewsFilter
        print("✅ NewsFilter 导入成功")
    except Exception as e:
        print(f"❌ NewsFilter 导入失败: {e}")
        return False
    
    try:
        from src.news_tools.github_archiver import GitHubArchiver
        print("✅ GitHubArchiver 导入成功")
    except Exception as e:
        print(f"❌ GitHubArchiver 导入失败: {e}")
        return False
    
    return True

def test_api_syntax():
    """测试API端点语法"""
    print("\n" + "=" * 60)
    print("测试2: API端点语法检查")
    print("=" * 60)
    
    import py_compile
    
    api_files = [
        'api/index.py',
        'api/health.py',
        'api/search.py',
        'api/download.py',
        'api/test.py'
    ]
    
    all_ok = True
    for file in api_files:
        try:
            py_compile.compile(file, doraise=True)
            print(f"✅ {file} 语法正确")
        except py_compile.PyCompileError as e:
            print(f"❌ {file} 语法错误: {e}")
            all_ok = False
    
    return all_ok

def test_initialization():
    """测试类初始化"""
    print("\n" + "=" * 60)
    print("测试3: 类初始化")
    print("=" * 60)
    
    try:
        from src.news_tools.news_searcher import NewsSearcher
        searcher = NewsSearcher()
        print("✅ NewsSearcher 初始化成功")
    except Exception as e:
        print(f"❌ NewsSearcher 初始化失败: {e}")
        return False
    
    try:
        from src.news_tools.content_downloader import ContentDownloader
        downloader = ContentDownloader()
        print("✅ ContentDownloader 初始化成功")
    except Exception as e:
        print(f"❌ ContentDownloader 初始化失败: {e}")
        return False
    
    try:
        from src.news_tools.news_filter import NewsFilter
        filter = NewsFilter.create_default_filter()
        print("✅ NewsFilter 初始化成功")
    except Exception as e:
        print(f"❌ NewsFilter 初始化失败: {e}")
        return False
    
    return True

def main():
    """运行所有测试"""
    print("\n🚀 开始完整功能测试\n")
    
    results = []
    
    # 测试1: 模块导入
    results.append(("模块导入", test_imports()))
    
    # 测试2: API语法
    results.append(("API语法", test_api_syntax()))
    
    # 测试3: 类初始化
    results.append(("类初始化", test_initialization()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 所有测试通过！")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查错误信息")
        return 1

if __name__ == '__main__':
    sys.exit(main())

