"""
全网新闻聚合MCP服务器
提供新闻搜索、内容下载、分类归档和定时任务功能
"""
import os
import asyncio
from fastmcp import FastMCP
from typing import List, Optional
from src.news_tools import NewsSearcher, ContentDownloader, GitHubArchiver, NewsScheduler

# 创建MCP服务器实例
mcp = FastMCP("Global News Aggregator")

# 全局实例
news_searcher = None
content_downloader = None


def get_news_searcher() -> NewsSearcher:
    """获取新闻搜索器实例（支持环境变量配置）"""
    global news_searcher
    if news_searcher is None:
        # 创建搜索器实例
        news_searcher = NewsSearcher(
            newsapi_key=os.getenv('NEWSAPI_KEY'),
            newsdata_key=os.getenv('NEWSDATA_KEY'),
            bing_api_key=os.getenv('BING_API_KEY'),
            enable_filter=os.getenv('ENABLE_NEWS_FILTER', 'true').lower() == 'true'
        )
        # 加载自定义关键词配置
        custom_keywords = news_searcher.load_custom_keywords()
        if custom_keywords:
            print(f"✓ 已加载自定义关键词配置: {len(custom_keywords)} 个分类")
    return news_searcher


def get_content_downloader() -> ContentDownloader:
    """获取内容下载器实例"""
    global content_downloader
    if content_downloader is None:
        content_downloader = ContentDownloader()
    return content_downloader


@mcp.tool()
async def search_global_news(
    keywords: Optional[str] = None,
    categories: Optional[List[str]] = None,
    languages: str = 'all',
    date_range: str = 'last_7_days',
    sources: Optional[List[str]] = None,
    max_results: int = 50
) -> dict:
    """
    从多个新闻源搜索和聚合新闻内容
    
    Args:
        keywords: 搜索关键词（可选）
        categories: 新闻分类数组，可选值: politics, finance, crypto, blockchain, fengshui, tech, social, international
        languages: 语言过滤，可选值: zh (中文), en (英文), all (全部)
        date_range: 日期范围，可选值: yesterday, last_7_days, last_30_days
        sources: 指定新闻源列表（可选，目前未使用）
        max_results: 最大返回结果数，默认50
    
    Returns:
        包含新闻列表的字典，每条新闻包含：标题、摘要、链接、来源、发布时间、分类、语言等信息
    """
    try:
        searcher = get_news_searcher()
        
        # 搜索新闻
        news_list = await searcher.search_news(
            keywords=keywords,
            categories=categories,
            languages=languages,
            date_range=date_range,
            sources=sources,
            max_results=max_results
        )
        
        return {
            'success': True,
            'count': len(news_list),
            'news': news_list,
            'search_params': {
                'keywords': keywords,
                'categories': categories,
                'languages': languages,
                'date_range': date_range,
                'max_results': max_results
            }
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'count': 0,
            'news': []
        }


@mcp.tool()
async def download_news_content(
    news_url: str,
    include_images: bool = True,
    include_banners: bool = True
) -> dict:
    """
    下载完整新闻内容、图片和横幅
    
    Args:
        news_url: 新闻文章的URL链接
        include_images: 是否下载并提取图片URL，默认为True
        include_banners: 是否下载并提取横幅图片URL，默认为True
    
    Returns:
        包含完整新闻内容的字典，包括：标题、正文、图片URL数组、横幅URL数组等
    """
    try:
        downloader = get_content_downloader()
        
        # 下载内容
        result = await downloader.download_news_content(
            news_url=news_url,
            include_images=include_images,
            include_banners=include_banners
        )
        
        return result
    
    except Exception as e:
        return {
            'url': news_url,
            'title': '',
            'content': '',
            'images': [],
            'banners': [],
            'success': False,
            'error': str(e)
        }


@mcp.tool()
def classify_and_save_news(
    news_data: List[dict],
    save_format: str = 'md_with_html',
    target_date: Optional[str] = None
) -> dict:
    """
    智能分类新闻并保存到GitHub仓库
    
    Args:
        news_data: 新闻数据数组，每条新闻应包含title, description, content, url, source, published_at等字段
        save_format: 保存格式，可选值: md_with_html (Markdown+HTML), md_with_xml (Markdown+XML)
        target_date: 目标日期 (YYYY-MM-DD格式)，默认为当前日期
    
    Returns:
        保存结果，包含成功状态、已保存的文件路径列表、错误信息等
        
    注意:
        - 需要设置GITHUB_TOKEN环境变量
        - 文件将按日期和分类自动组织: /YYYY/MM/DD/category.md
        - 提交信息格式: "chore: archive news for YYYY-MM-DD"
    """
    try:
        # 获取GitHub Token
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            return {
                'success': False,
                'error': 'GITHUB_TOKEN环境变量未设置',
                'saved_files': [],
                'errors': []
            }
        
        # 创建归档器
        archiver = GitHubArchiver(github_token=github_token)
        
        # 分类并保存
        result = archiver.classify_and_save_news(
            news_data=news_data,
            save_format=save_format,
            target_date=target_date
        )
        
        return result
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'saved_files': [],
            'errors': [{'error': str(e)}]
        }


@mcp.tool()
def schedule_daily_news_archive(
    cron_expression: str = "0 1 * * *",
    categories: Optional[List[str]] = None,
    languages: str = "all"
) -> dict:
    """
    设置每日新闻自动归档任务配置
    
    Args:
        cron_expression: Cron表达式，默认"0 1 * * *"表示每日凌晨1点执行
        categories: 要归档的新闻分类列表，默认包含所有分类
        languages: 要归档的语言，可选值: zh, en, all
    
    Returns:
        调度任务配置信息，包括:
        - cron表达式和描述
        - 下次运行时间
        - GitHub Actions工作流配置
        - Vercel Cron配置
        - 手动执行脚本
        
    注意:
        此工具返回配置信息，实际的定时任务需要通过GitHub Actions或其他调度系统部署
    """
    try:
        scheduler = NewsScheduler()
        
        # 生成配置
        config = scheduler.schedule_daily_news_archive(
            cron_expression=cron_expression,
            categories=categories,
            languages=languages
        )
        
        return {
            'success': True,
            'config': config
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'config': None
        }


# 启动服务器
if __name__ == "__main__":
    mcp.run()
