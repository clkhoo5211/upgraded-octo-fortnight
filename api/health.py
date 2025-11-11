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
    # 检查环境变量配置
    config_status = {
        'NEWSAPI_KEY': bool(os.getenv('NEWSAPI_KEY')),
        'BING_API_KEY': bool(os.getenv('BING_API_KEY')),
        'SERPAPI_KEY': bool(os.getenv('SERPAPI_KEY')),
        'GOOGLE_SEARCH_API_KEY': bool(os.getenv('GOOGLE_SEARCH_API_KEY')),
        'GITHUB_TOKEN': bool(os.getenv('GITHUB_TOKEN')),
        'ENABLE_NEWS_FILTER': os.getenv('ENABLE_NEWS_FILTER', 'true')
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
        'endpoints': {
            '/api/search': 'POST/GET - 搜索全网新闻',
            '/api/download': 'POST/GET - 下载新闻完整内容',
            '/api/health': 'GET - 健康检查'
        },
        'available_sources': available_sources,
        'total_sources': len(available_sources),
        'config_status': config_status,
        'features': {
            'intelligent_filtering': config_status['ENABLE_NEWS_FILTER'] == 'true',
            'multi_language': True,
            'custom_keywords': True,
            'quality_scoring': True,
            'content_extraction': True
        }
    })

# Vercel入口
def handler(request):
    """Vercel Serverless Function入口"""
    with app.request_context(request.environ):
        return app.full_dispatch_request()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
