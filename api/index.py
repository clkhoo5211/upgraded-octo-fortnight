"""
Vercel Serverless Functions入口
提供HTTP API访问全网新闻服务
"""
import os
import sys
import asyncio
from flask import Flask, jsonify, request

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.news_tools import NewsSearcher, ContentDownloader

app = Flask(__name__)

# 全局实例
news_searcher = None
content_downloader = None

def get_news_searcher():
    """获取新闻搜索器实例"""
    global news_searcher
    if news_searcher is None:
        news_searcher = NewsSearcher(
            newsapi_key=os.getenv('NEWSAPI_KEY'),
            newsdata_key=os.getenv('NEWSDATA_KEY'),
            bing_api_key=os.getenv('BING_API_KEY'),
            serpapi_key=os.getenv('SERPAPI_KEY'),
            enable_filter=os.getenv('ENABLE_NEWS_FILTER', 'true').lower() == 'true'
        )
    return news_searcher

def get_content_downloader():
    """获取内容下载器实例"""
    global content_downloader
    if content_downloader is None:
        content_downloader = ContentDownloader()
    return content_downloader

@app.route('/')
def index():
    """API首页"""
    # 检查配置状态
    config_status = {
        'NEWSAPI_KEY': bool(os.getenv('NEWSAPI_KEY')),
        'BING_API_KEY': bool(os.getenv('BING_API_KEY')),
        'NEWSDATA_KEY': bool(os.getenv('NEWSDATA_KEY')),
        'SERPAPI_KEY': bool(os.getenv('SERPAPI_KEY'))
    }
    
    available_sources = []
    if config_status['NEWSAPI_KEY']:
        available_sources.append('NewsAPI.org')
    if config_status['BING_API_KEY']:
        available_sources.append('Bing News API')
    if config_status['NEWSDATA_KEY']:
        available_sources.append('NewsData.io')
    
    # 总是可用的免费源
    available_sources.extend([
        'Hacker News API',
        'Google News RSS',
        'Product Hunt GraphQL'
    ])
    
    return jsonify({
        'service': 'Global News Aggregator API',
        'version': '1.0.0',
        'status': 'online',
        'config': config_status,
        'available_sources': available_sources,
        'endpoints': {
            '/': 'GET - API首页',
            '/api/search': 'POST - 搜索全网新闻',
            '/api/download': 'POST - 下载新闻完整内容',
            '/api/health': 'GET - 健康检查'
        },
        'usage': {
            'search': {
                'method': 'POST',
                'url': '/api/search',
                'body': {
                    'keywords': '搜索关键词（可选）',
                    'categories': ['科技', '商业', '体育'], 
                    'languages': 'zh/en/all（默认all）',
                    'date_range': 'yesterday/last_7_days/last_30_days（默认last_7_days）',
                    'max_results': '50'
                }
            },
            'download': {
                'method': 'POST', 
                'url': '/api/download',
                'body': {
                    'news_url': '新闻URL（必需）',
                    'include_images': 'true/false（默认true）',
                    'include_banners': 'true/false（默认true）'
                }
            }
        },
        'documentation': 'https://github.com/clkhoo5211/upgraded-octo-fortnight'
    })

@app.route('/api/health')
def health():
    """健康检查端点"""
    try:
        # 检查配置状态
        config_status = {
            'NEWSAPI_KEY': bool(os.getenv('NEWSAPI_KEY')),
            'BING_API_KEY': bool(os.getenv('BING_API_KEY')),
            'NEWSDATA_KEY': bool(os.getenv('NEWSDATA_KEY')),
            'SERPAPI_KEY': bool(os.getenv('SERPAPI_KEY'))
        }
        
        available_sources = []
        if config_status['NEWSAPI_KEY']:
            available_sources.append('NewsAPI.org')
        if config_status['BING_API_KEY']:
            available_sources.append('Bing News API')
        if config_status['NEWSDATA_KEY']:
            available_sources.append('NewsData.io')
        
        # 总是可用的免费源
        available_sources.extend([
            'Hacker News API',
            'Google News RSS',
            'Product Hunt GraphQL'
        ])
        
        return jsonify({
            'status': 'healthy',
            'service': 'global-news-mcp',
            'version': '1.0.0',
            'config_status': config_status,
            'available_sources': available_sources,
            'free_sources': [
                'Hacker News API',
                'Google News RSS', 
                'Product Hunt GraphQL'
            ],
            'enhanced_sources': [src for src in available_sources if src not in [
                'Hacker News API', 'Google News RSS', 'Product Hunt GraphQL'
            ]]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'service': 'global-news-mcp',
            'version': '1.0.0',
            'error': str(e),
            'available_sources': [
                'Hacker News API',
                'Google News RSS',
                'Product Hunt GraphQL'
            ]
        }), 200  # 200 status even on error to show service is running

@app.route('/api/search', methods=['POST', 'GET'])
def search_news():
    """
    搜索全网新闻
    """
    try:
        # 获取请求参数
        if request.method == 'POST':
            data = request.get_json() or {}
        else:
            data = request.args.to_dict()
            # 处理数组参数
            if 'categories' in data:
                data['categories'] = data['categories'].split(',')
        
        keywords = data.get('keywords')
        categories = data.get('categories')
        languages = data.get('languages', 'all')
        date_range = data.get('date_range', 'last_7_days')
        max_results = int(data.get('max_results', 50))
        
        # 获取搜索器
        searcher = get_news_searcher()
        
        # 异步搜索新闻
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        news_list = loop.run_until_complete(
            searcher.search_news(
                keywords=keywords,
                categories=categories,
                languages=languages,
                date_range=date_range,
                max_results=max_results
            )
        )
        loop.close()
        
        return jsonify({
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
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'count': 0,
            'news': []
        }), 500

@app.route('/api/download', methods=['POST', 'GET'])
def download_content():
    """
    下载完整新闻内容
    """
    try:
        # 获取请求参数
        if request.method == 'POST':
            data = request.get_json() or {}
        else:
            data = request.args.to_dict()
        
        news_url = data.get('news_url')
        if not news_url:
            return jsonify({
                'success': False,
                'error': 'news_url参数是必需的'
            }), 400
        
        include_images = data.get('include_images', 'true').lower() == 'true'
        include_banners = data.get('include_banners', 'true').lower() == 'true'
        
        # 获取下载器
        downloader = get_content_downloader()
        
        # 异步下载内容
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            downloader.download_news_content(
                news_url=news_url,
                include_images=include_images,
                include_banners=include_banners
            )
        )
        loop.close()
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'url': data.get('news_url', ''),
            'title': '',
            'content': '',
            'images': [],
            'banners': [],
            'success': False,
            'error': str(e)
        }), 500

# Vercel入口
def handler(request):
    """Vercel Serverless Function入口"""
    with app.request_context(request.environ):
        return app.full_dispatch_request()

if __name__ == '__main__':
    app.run(debug=True)
