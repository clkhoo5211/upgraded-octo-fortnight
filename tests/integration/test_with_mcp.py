"""
使用MCP工具测试完整流程
"""
import asyncio
import os
import sys

# 添加项目路径
sys.path.insert(0, '/workspace/global-news-mcp')

from src.news_tools import NewsSearcher, ContentDownloader, GitHubArchiver
from datetime import datetime, timedelta

async def test_full_workflow():
    """测试完整工作流"""
    
    print("\n" + "=" * 70)
    print("MCP新闻聚合服务 - 完整功能测试")
    print("=" * 70)
    
    # 步骤1: 搜索新闻
    print("\n步骤1: 搜索最新科技新闻...")
    print("-" * 70)
    
    searcher = NewsSearcher(
        newsapi_key=os.getenv('NEWSAPI_KEY'),
        newsdata_key=os.getenv('NEWSDATA_KEY')
    )
    
    news_list = await searcher.search_news(
        keywords="technology",
        categories=["tech"],
        languages="en",
        date_range="last_7_days",
        max_results=10
    )
    
    print(f"✓ 找到 {len(news_list)} 条新闻")
    
    if news_list:
        print(f"\n示例新闻:")
        for i, news in enumerate(news_list[:3], 1):
            print(f"  {i}. {news['title'][:80]}...")
            print(f"     来源: {news['source']}, 时间: {news['published_at']}")
    
    await searcher.close()
    
    # 步骤2: 下载内容（仅下载第一条）
    if news_list:
        print(f"\n步骤2: 下载完整新闻内容...")
        print("-" * 70)
        
        downloader = ContentDownloader()
        first_news = news_list[0]
        
        content = await downloader.download_news_content(
            news_url=first_news['url'],
            include_images=True,
            include_banners=True
        )
        
        if content['success']:
            print(f"✓ 成功下载内容")
            print(f"  标题: {content['title'][:60]}...")
            print(f"  内容长度: {len(content['content'])} 字符")
            print(f"  图片数量: {len(content['images'])}")
            
            # 更新新闻内容
            first_news['content'] = content['content']
            first_news['images'] = content['images']
        else:
            print(f"✗ 下载失败: {content['error']}")
        
        await downloader.close()
    
    # 步骤3: 创建测试数据（模拟归档）
    print(f"\n步骤3: 准备归档数据...")
    print("-" * 70)
    
    # 创建少量测试数据
    test_news = news_list[:3] if len(news_list) >= 3 else news_list
    
    # 确保每条新闻都有必要的字段
    for news in test_news:
        if not news.get('content'):
            news['content'] = news.get('description', '内容暂无')
        if not news.get('images'):
            news['images'] = []
    
    print(f"✓ 准备归档 {len(test_news)} 条新闻")
    
    # 步骤4: 归档到GitHub
    github_token = os.getenv('GITHUB_TOKEN')
    
    if github_token:
        print(f"\n步骤4: 归档到GitHub...")
        print("-" * 70)
        print(f"  目标仓库: clkhoo5211/upgraded-octo-fortnight")
        print(f"  归档日期: {datetime.now().strftime('%Y-%m-%d')}")
        
        try:
            archiver = GitHubArchiver(
                github_token=github_token,
                repo_name="clkhoo5211/upgraded-octo-fortnight"
            )
            
            result = archiver.classify_and_save_news(
                news_data=test_news,
                save_format='md_with_html',
                target_date=datetime.now().strftime('%Y-%m-%d')
            )
            
            if result['success']:
                print(f"✓ 归档成功!")
                print(f"  保存文件数: {len(result['saved_files'])}")
                for file_path in result['saved_files']:
                    print(f"    - {file_path}")
                print(f"  总新闻数: {result['total_news']}")
            else:
                print(f"✗ 归档失败!")
                for error in result['errors']:
                    print(f"  错误: {error}")
        
        except Exception as e:
            print(f"✗ GitHub归档错误: {str(e)}")
    else:
        print(f"\n步骤4: 跳过GitHub归档（未配置GITHUB_TOKEN）")
    
    print("\n" + "=" * 70)
    print("测试完成!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    asyncio.run(test_full_workflow())
