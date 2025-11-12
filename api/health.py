"""
健康检查和服务状态API端点
"""
import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    健康检查端点
    
    返回服务状态和配置信息
    """
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
    
    return jsonify({
        'status': 'healthy',
        'service': 'Global News Aggregator',
        'version': '1.0.0',
        'service_status': 'operational',  # 服务运行状态
        
        'endpoints': {
            '/api/search': 'POST/GET - 搜索全网新闻',
            '/api/download': 'POST/GET - 下载新闻完整内容',
            '/api/health': 'GET - 健康检查'
        },
        
        # 总是可用的免费功能
        'free_features': {
            'search': True,
            'content_extraction': True,
            'multi_language': True,
            'quality_scoring': True
        },
        
        # 可选的付费功能（需要API密钥）
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
                'NewsAPI.org' if config_status['NEWSAPI_KEY'] else None,
                'Bing News API' if config_status['BING_API_KEY'] else None,
                'SerpAPI' if config_status['SERPAPI_KEY'] else None,
                'Google Custom Search' if config_status['GOOGLE_SEARCH_API_KEY'] else None,
                'GitHub API' if config_status['GITHUB_TOKEN'] else None
            ]
        },
        
        'settings': {
            'intelligent_filtering': config_status['ENABLE_NEWS_FILTER'] == 'true',
            'production_mode': True
        },
        
        # 迁移说明
        'migration_note': '如果不使用付费API服务，此服务仅使用免费源也能正常工作'
    })

# Vercel入口
def handler(request):
    """Vercel Serverless Function入口"""
    with app.request_context(request.environ):
        return app.full_dispatch_request()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
