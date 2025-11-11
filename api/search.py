"""
全网新闻搜索API端点
"""
import os
import sys
import asyncio
from flask import Flask, jsonify, request

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.news_tools import NewsSearcher

app = Flask(__name__)

# 全局搜索器实例
news_searcher = None

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
        # 加载自定义关键词
        custom_keywords = news_searcher.load_custom_keywords()
        if custom_keywords:
            print(f"✓ 已加载自定义关键词配置: {len(custom_keywords)} 个分类")
    return news_searcher

@app.route('/api/search', methods=['POST', 'GET'])
def search_news():
    """
    搜索全网新闻
    
    请求参数:
        keywords: 搜索关键词（可选）
        categories: 新闻分类数组（可选）
        languages: 语言过滤 (zh/en/all)，默认all
        date_range: 日期范围 (yesterday/last_7_days/last_30_days)，默认last_7_days
        max_results: 最大结果数，默认50
    
    返回:
        {
            "success": true,
            "count": 10,
            "news": [...],
            "search_params": {...}
        }
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

# Vercel入口
def handler(request):
    """Vercel Serverless Function入口"""
    with app.request_context(request.environ):
        return app.full_dispatch_request()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
