"""
健康检查和服务状态API端点
"""
import os
import json
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        try:
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
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            error_response = {
                'status': 'error',
                'service': 'global-news-mcp',
                'version': '1.0.0',
                'error': str(e),
                'traceback': error_trace
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
