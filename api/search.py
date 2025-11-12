"""
全网新闻搜索API端点
"""
import os
import json
import sys
import asyncio
from http.server import BaseHTTPRequestHandler

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
        try:
            custom_keywords = news_searcher.load_custom_keywords()
            if custom_keywords:
                print(f"✓ 已加载自定义关键词配置: {len(custom_keywords)} 个分类")
        except Exception as e:
            print(f"警告: 加载自定义关键词失败: {e}")
    return news_searcher

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle_request()
    
    def do_POST(self):
        self._handle_request()
    
    def _handle_request(self):
        """处理搜索请求"""
        try:
            # 获取请求参数
            if self.command == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    body = self.rfile.read(content_length).decode('utf-8')
                    data = json.loads(body) if body else {}
                else:
                    data = {}
            else:
                # GET请求从查询字符串获取
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(self.path)
                query_params = parse_qs(parsed.query)
                data = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
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
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"搜索错误: {error_trace}")
            
            error_response = {
                'success': False,
                'error': str(e),
                'traceback': error_trace,
                'count': 0,
                'news': []
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
