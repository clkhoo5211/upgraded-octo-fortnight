"""
测试Vercel API端点
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_health_api():
    """测试健康检查API"""
    print("=" * 60)
    print("测试健康检查API")
    print("=" * 60)
    
    from api.health import app
    
    with app.test_client() as client:
        response = client.get('/api/health')
        data = response.get_json()
        
        print(f"✓ 状态码: {response.status_code}")
        print(f"✓ 服务名称: {data.get('service')}")
        print(f"✓ 服务状态: {data.get('status')}")
        print(f"✓ 可用源数量: {data.get('total_sources')}")
        print(f"✓ 可用源: {', '.join(data.get('available_sources', [])[:5])}")
        print()
        
        assert response.status_code == 200
        assert data['status'] == 'healthy'
        print("✅ 健康检查API测试通过\n")

def test_search_api():
    """测试搜索API基础功能"""
    print("=" * 60)
    print("测试搜索API（无实际API调用）")
    print("=" * 60)
    
    from api.search import app
    
    with app.test_client() as client:
        # 测试GET请求
        response = client.get('/api/search?max_results=5')
        data = response.get_json()
        
        print(f"✓ 状态码: {response.status_code}")
        print(f"✓ 成功状态: {data.get('success')}")
        print(f"✓ 新闻数量: {data.get('count', 0)}")
        print()
        
        print("✅ 搜索API基础测试通过\n")

def test_download_api():
    """测试下载API基础功能"""
    print("=" * 60)
    print("测试下载API（参数验证）")
    print("=" * 60)
    
    from api.download import app
    
    with app.test_client() as client:
        # 测试缺少必需参数
        response = client.get('/api/download')
        data = response.get_json()
        
        print(f"✓ 状态码: {response.status_code}")
        print(f"✓ 错误信息: {data.get('error')}")
        
        assert response.status_code == 400
        assert 'news_url' in data.get('error', '')
        print()
        
        print("✅ 下载API参数验证测试通过\n")

def main():
    """运行所有测试"""
    print("\n🚀 开始测试Vercel API端点\n")
    
    try:
        test_health_api()
        test_search_api()
        test_download_api()
        
        print("=" * 60)
        print("✅ 所有API端点测试通过！")
        print("=" * 60)
        print("\n下一步：")
        print("1. 提交代码到GitHub")
        print("2. 运行 ./vercel-deploy.sh 部署到Vercel")
        print("3. 访问Vercel提供的URL测试API")
        print()
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
