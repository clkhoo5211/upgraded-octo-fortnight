"""
全网新闻聚合MCP服务 - 功能测试脚本
测试NewsFilter集成、全网搜索和环境变量配置功能
"""
import os
import sys
import asyncio
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.news_tools import NewsSearcher, NewsFilter


async def test_news_filter():
    """测试NewsFilter过滤功能"""
    print("\n" + "="*60)
    print("测试 1: NewsFilter 智能过滤功能")
    print("="*60)
    
    # 创建测试过滤器
    news_filter = NewsFilter.create_default_filter()
    
    # 添加自定义规则
    news_filter.add_include_keywords(['AI', '人工智能', '机器学习'])
    news_filter.add_exclude_keywords(['广告', '推广'])
    
    print(f"包含关键词: {news_filter.include_keywords}")
    print(f"排除关键词: {news_filter.exclude_keywords}")
    
    # 测试新闻样本
    test_news = [
        {
            'title': '突破性AI技术革新机器学习领域',
            'description': '研究人员开发了新的深度学习算法',
            'source': 'TechNews'
        },
        {
            'title': '推广：最新智能手机广告发布',
            'description': '这是一个商业推广内容',
            'source': 'AdNews'
        },
        {
            'title': '今日天气预报',
            'description': '明天将会有小雨',
            'source': 'WeatherNews'
        }
    ]
    
    for news in test_news:
        should_include = news_filter.should_include(news)
        status = "✓ 通过" if should_include else "✗ 过滤"
        print(f"\n{status}: {news['title']}")
        print(f"   来源: {news['source']}")


async def test_web_search():
    """测试全网搜索功能"""
    print("\n" + "="*60)
    print("测试 2: 全网搜索功能（多源并行）")
    print("="*60)
    
    # 创建搜索器
    searcher = NewsSearcher(
        newsapi_key=os.getenv('NEWSAPI_KEY'),
        bing_api_key=os.getenv('BING_API_KEY'),
        enable_filter=True
    )
    
    # 加载自定义关键词
    custom_keywords = searcher.load_custom_keywords()
    print(f"\n✓ 自定义关键词配置: {len(custom_keywords)} 个分类")
    
    # 测试搜索
    print("\n开始搜索关键词: 'AI技术'")
    print("搜索源: NewsAPI, Google News, Hacker News, Product Hunt...")
    
    try:
        results = await searcher.search_news(
            keywords='AI',
            categories=['tech'],
            languages='en',
            max_results=10
        )
        
        print(f"\n✓ 搜索成功! 找到 {len(results)} 条新闻")
        
        # 显示前3条结果
        for i, news in enumerate(results[:3], 1):
            print(f"\n{i}. {news['title']}")
            print(f"   来源: {news['source']}")
            print(f"   分类: {news['category']}")
            print(f"   语言: {news['language']}")
            print(f"   链接: {news['url'][:60]}...")
    
    except Exception as e:
        print(f"\n✗ 搜索失败: {e}")
    
    finally:
        await searcher.close()


async def test_custom_sources():
    """测试自定义新闻源"""
    print("\n" + "="*60)
    print("测试 3: 自定义新闻源（环境变量配置）")
    print("="*60)
    
    # 设置测试环境变量
    test_links = [
        'https://news.google.com/rss',
        'https://feeds.bbci.co.uk/news/rss.xml'
    ]
    
    print(f"\n自定义链接: {len(test_links)} 个")
    for link in test_links:
        print(f"  - {link}")
    
    # 临时设置环境变量
    original_links = os.getenv('CUSTOM_NEWS_LINKS', '')
    os.environ['CUSTOM_NEWS_LINKS'] = ','.join(test_links)
    
    try:
        searcher = NewsSearcher(enable_filter=False)
        
        print("\n开始从自定义源搜索新闻...")
        results = await searcher.search_news(
            languages='en',
            max_results=5
        )
        
        print(f"\n✓ 搜索成功! 找到 {len(results)} 条新闻")
        
        # 统计来源
        sources = {}
        for news in results:
            source = news['source']
            sources[source] = sources.get(source, 0) + 1
        
        print("\n新闻来源分布:")
        for source, count in sources.items():
            print(f"  - {source}: {count} 条")
    
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
    
    finally:
        # 恢复环境变量
        if original_links:
            os.environ['CUSTOM_NEWS_LINKS'] = original_links
        else:
            os.environ.pop('CUSTOM_NEWS_LINKS', None)
        
        await searcher.close()


async def test_hacker_news():
    """测试Hacker News API集成"""
    print("\n" + "="*60)
    print("测试 4: Hacker News API 集成")
    print("="*60)
    
    searcher = NewsSearcher(enable_filter=False)
    
    try:
        print("\n正在获取Hacker News热门故事...")
        results = await searcher._search_hackernews(max_results=5)
        
        print(f"\n✓ 成功获取 {len(results)} 条热门故事")
        
        for i, news in enumerate(results, 1):
            print(f"\n{i}. {news['title']}")
            print(f"   链接: {news['url'][:60]}...")
            print(f"   分类: {news['category']}")
    
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
    
    finally:
        await searcher.close()


async def test_classification():
    """测试新闻分类功能"""
    print("\n" + "="*60)
    print("测试 5: 新闻智能分类")
    print("="*60)
    
    searcher = NewsSearcher(enable_filter=False)
    
    test_samples = [
        {'title': 'Bitcoin价格突破新高', 'description': '加密货币市场迎来牛市'},
        {'title': '美国总统选举投票开始', 'description': '民主党和共和党展开激烈竞争'},
        {'title': '股市大涨创历史新高', 'description': '纳斯达克指数上涨3%'},
        {'title': '区块链技术在供应链中的应用', 'description': 'Web3和去中心化解决方案'},
    ]
    
    print("\n测试样本分类结果:")
    for sample in test_samples:
        category = searcher._classify_news(sample)
        print(f"\n标题: {sample['title']}")
        print(f"分类: {category}")
    
    await searcher.close()


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "█"*60)
    print("█  全网新闻聚合MCP服务 - 功能测试套件")
    print("█  测试时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("█"*60)
    
    # 检查环境变量
    print("\n环境变量检查:")
    print(f"  NEWSAPI_KEY: {'✓ 已设置' if os.getenv('NEWSAPI_KEY') else '✗ 未设置'}")
    print(f"  BING_API_KEY: {'✓ 已设置' if os.getenv('BING_API_KEY') else '✗ 未设置'}")
    print(f"  GITHUB_TOKEN: {'✓ 已设置' if os.getenv('GITHUB_TOKEN') else '✗ 未设置'}")
    print(f"  CUSTOM_KEYWORDS: {'✓ 已设置' if os.getenv('CUSTOM_KEYWORDS') else '✗ 未设置'}")
    print(f"  CUSTOM_NEWS_LINKS: {'✓ 已设置' if os.getenv('CUSTOM_NEWS_LINKS') else '✗ 未设置'}")
    
    # 运行测试
    tests = [
        test_news_filter,
        test_classification,
        test_hacker_news,
        test_custom_sources,
        test_web_search,
    ]
    
    for test_func in tests:
        try:
            await test_func()
        except Exception as e:
            print(f"\n✗ 测试异常: {test_func.__name__}")
            print(f"   错误: {e}")
        
        # 短暂延迟避免API限流
        await asyncio.sleep(2)
    
    print("\n" + "█"*60)
    print("█  测试完成!")
    print("█"*60 + "\n")


if __name__ == "__main__":
    # 运行异步测试
    asyncio.run(run_all_tests())
