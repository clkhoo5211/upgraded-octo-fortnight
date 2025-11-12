"""
健康检查和服务状态API端点
"""
import os
import json
import sys

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def handler(request):
    """
    健康检查端点
    
    返回服务状态和配置信息
    """
    try:
        # 检查环境变量配置（可选）
        newsapi_key = os.getenv('NEWSAPI_KEY')
        bing_api_key = os.getenv('BING_API_KEY')
        serpapi_key = os.getenv('SERPAPI_KEY')
        google_search_api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        github_token = os.getenv('GITHUB_TOKEN')
        enable_news_filter = os.getenv('ENABLE_NEWS_FILTER', 'true')
        
        config_status = {
            'NEWSAPI_KEY': bool(newsapi_key),
            'BING_API_KEY': bool(bing_api_key),
            'SERPAPI_KEY': bool(serpapi_key),
            'GOOGLE_SEARCH_API_KEY': bool(google_search_api_key),
            'GITHUB_TOKEN': bool(github_token),
            'ENABLE_NEWS_FILTER': enable_news_filter
        }
        
        # 统计可用的新闻源
        available_sources = []
        if config_status['NEWSAPI_KEY']:
            available_sources.append('NewsAPI.org')
        if config_status['BING_API_KEY']:
            available_sources.append('Bing News')
        if config_status['SERPAPI_KEY']:
            available_sources.append('SerpAPI (Google/Bing/百度/Yahoo)')
        if config_status['GOOGLE_SEARCH_API_KEY']:
            available_sources.append('Google Custom Search')
        
        # 总是可用的免费源
        available_sources.extend([
            'Hacker News API',
            'Google News RSS',
            'Product Hunt GraphQL'
        ])
        
        response_data = {
            'status': 'healthy',
            'service': 'Global News Aggregator',
            'version': '1.0.0',
            'service_status': 'operational',
            
            'endpoints': {
                '/api/search': 'POST/GET - 搜索全网新闻',
                '/api/download': 'POST/GET - 下载新闻完整内容',
                '/api/health': 'GET - 健康检查'
            },
            
            'free_features': {
                'search': True,
                'content_extraction': True,
                'multi_language': True,
                'quality_scoring': True
            },
            
            'premium_features': {
                'newsapi_source': bool(config_status['NEWSAPI_KEY']),
                'bing_news': bool(config_status['BING_API_KEY']),
                'serpapi_search': bool(config_status['SERPAPI_KEY']),
                'google_search': bool(config_status['GOOGLE_SEARCH_API_KEY']),
                'github_token': bool(config_status['GITHUB_TOKEN'])
            },
            
            'news_sources': {
                'free_sources': [
                    'Hacker News API',
                    'Google News RSS',
                    'Product Hunt GraphQL',
                    'Reddit JSON API'
                ],
                'premium_sources': [
                    src for src in [
                        'NewsAPI.org' if config_status['NEWSAPI_KEY'] else None,
                        'Bing News API' if config_status['BING_API_KEY'] else None,
                        'SerpAPI' if config_status['SERPAPI_KEY'] else None,
                        'Google Custom Search' if config_status['GOOGLE_SEARCH_API_KEY'] else None,
                        'GitHub API' if config_status['GITHUB_TOKEN'] else None
                    ] if src
                ]
            },
            
            'settings': {
                'intelligent_filtering': config_status['ENABLE_NEWS_FILTER'] == 'true',
                'production_mode': True
            },
            
            'migration_note': '如果不使用付费API服务，此服务仅使用免费源也能正常工作'
        }
        
        return json.dumps(response_data, ensure_ascii=False), {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"健康检查错误: {error_trace}")
        return json.dumps({
            'status': 'error',
            'service': 'global-news-mcp',
            'version': '1.0.0',
            'error': str(e),
            'available_sources': [
                'Hacker News API',
                'Google News RSS',
                'Product Hunt GraphQL'
            ]
        }, ensure_ascii=False), {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
