import asyncio
import os
from src.news_tools import NewsSearcher

async def test_search():
    """测试新闻搜索功能"""
    print("=" * 60)
    print("测试1: 搜索最新科技新闻（英文）")
    print("=" * 60)
    
    # 检查API密钥
    newsapi_key = os.getenv('NEWSAPI_KEY')
    if newsapi_key:
        print(f"✓ NewsAPI密钥已配置: {newsapi_key[:10]}...")
    else:
        print("⚠ NewsAPI密钥未配置，将仅使用RSS源")
    
    searcher = NewsSearcher()
    
    # 搜索科技新闻
    news = await searcher.search_news(
        keywords="artificial intelligence",
        categories=["tech"],
        languages="en",
        date_range="last_7_days",
        max_results=5
    )
    
    print(f"\n✓ 找到 {len(news)} 条新闻\n")
    
    for i, item in enumerate(news[:3], 1):
        print(f"{i}. {item['title']}")
        print(f"   来源: {item['source']}")
        print(f"   时间: {item['published_at']}")
        print(f"   链接: {item['url'][:80]}...")
        print()
    
    await searcher.close()
    return news

if __name__ == "__main__":
    asyncio.run(test_search())
