"""
Vercel Serverless Functions入口 - API首页
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
            # 检查配置状态
            config_status = {
                'NEWSAPI_KEY': bool(os.getenv('NEWSAPI_KEY')),
                'BING_API_KEY': bool(os.getenv('BING_API_KEY')),
                'NEWSDATA_KEY': bool(os.getenv('NEWSDATA_KEY')),
                'SERPAPI_KEY': bool(os.getenv('SERPAPI_KEY')),
                'GOOGLE_SEARCH_API_KEY': bool(os.getenv('GOOGLE_SEARCH_API_KEY'))
            }
            
            available_sources = []
            if config_status['NEWSAPI_KEY']:
                available_sources.append('NewsAPI.org')
            if config_status['BING_API_KEY']:
                available_sources.append('Bing News API')
            if config_status['NEWSDATA_KEY']:
                available_sources.append('NewsData.io')
            if config_status['SERPAPI_KEY']:
                available_sources.append('SerpAPI')
            if config_status['GOOGLE_SEARCH_API_KEY']:
                available_sources.append('Google Custom Search')
            
            # 总是可用的免费源
            available_sources.extend([
                'Hacker News API',
                'Google News RSS',
                'Product Hunt GraphQL'
            ])
            
            response_data = {
                'service': 'Global News Aggregator API',
                'version': '1.0.0',
                'status': 'online',
                'config': config_status,
                'available_sources': available_sources,
                'endpoints': {
                    '/': 'GET - API首页',
                    '/api/search': 'POST/GET - 搜索全网新闻',
                    '/api/download': 'POST/GET - 下载新闻完整内容',
                    '/api/health': 'GET - 健康检查'
                },
                'usage': {
                    'search': {
                        'method': 'POST/GET',
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
                        'method': 'POST/GET', 
                        'url': '/api/download',
                        'body': {
                            'news_url': '新闻URL（必需）',
                            'include_images': 'true/false（默认true）',
                            'include_banners': 'true/false（默认true）'
                        }
                    }
                },
                'documentation': 'https://github.com/clkhoo5211/upgraded-octo-fortnight'
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
                'error': str(e),
                'traceback': error_trace,
                'service': 'Global News Aggregator API'
            }
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
