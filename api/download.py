"""
新闻内容下载API端点
"""
import os
import json
import sys
import asyncio
from http.server import BaseHTTPRequestHandler

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.news_tools import ContentDownloader

# 全局下载器实例
content_downloader = None

def get_content_downloader():
    """获取内容下载器实例"""
    global content_downloader
    if content_downloader is None:
        content_downloader = ContentDownloader()
    return content_downloader

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        self._handle_request()
    
    def do_POST(self):
        self._handle_request()
    
    def _handle_request(self):
        """处理下载请求"""
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
            
            news_url = data.get('news_url')
            if not news_url:
                error_response = {
                    'success': False,
                    'error': 'news_url参数是必需的'
                }
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
                return
            
            include_images = data.get('include_images', 'true').lower() == 'true'
            include_banners = data.get('include_banners', 'true').lower() == 'true'
            
            # 获取下载器
            downloader = get_content_downloader()
            
            # 异步下载内容
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    downloader.download_news_content(
                        news_url=news_url,
                        include_images=include_images,
                        include_banners=include_banners
                    )
                )
            finally:
                loop.close()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"下载错误: {error_trace}")
            
            data = {}
            if self.command == 'POST':
                try:
                    content_length = int(self.headers.get('Content-Length', 0))
                    if content_length > 0:
                        body = self.rfile.read(content_length).decode('utf-8')
                        data = json.loads(body) if body else {}
                except:
                    pass
            
            error_response = {
                'url': data.get('news_url', ''),
                'title': '',
                'content': '',
                'images': [],
                'banners': [],
                'success': False,
                'error': str(e),
                'traceback': error_trace
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
