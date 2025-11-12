"""
全网新闻搜索API端点
"""
import os
import json
import sys
import asyncio

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.news_tools import NewsSearcher

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
        try:
            custom_keywords = news_searcher.load_custom_keywords()
            if custom_keywords:
                print(f"✓ 已加载自定义关键词配置: {len(custom_keywords)} 个分类")
        except Exception as e:
            print(f"警告: 加载自定义关键词失败: {e}")
    return news_searcher

def handler(request):
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
        # 解析请求
        method = request.get('httpMethod', 'GET') if isinstance(request, dict) else 'GET'
        
        # 获取请求参数
        if method == 'POST':
            body = request.get('body', '{}') if isinstance(request, dict) else '{}'
            if isinstance(body, str):
                data = json.loads(body)
            else:
                data = body
        else:
            # GET请求从queryStringParameters获取
            query_params = request.get('queryStringParameters') if isinstance(request, dict) else {}
            data = (query_params or {}).copy()
            # 处理数组参数
            if 'categories' in data and isinstance(data['categories'], str):
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
        try:
            news_list = loop.run_until_complete(
                searcher.search_news(
                    keywords=keywords,
                    categories=categories,
                    languages=languages,
                    date_range=date_range,
                    max_results=max_results
                )
            )
        finally:
            loop.close()
        
        response_data = {
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
        
        return json.dumps(response_data, ensure_ascii=False), {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"搜索错误: {error_trace}")
        
        return json.dumps({
            'success': False,
            'error': str(e),
            'count': 0,
            'news': []
        }, ensure_ascii=False), {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'status': 500
        }
