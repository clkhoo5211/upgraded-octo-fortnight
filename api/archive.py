"""
完整新闻归档API端点
整合搜索、下载、分类和保存功能
"""
import os
import json
import sys
import asyncio
from http.server import BaseHTTPRequestHandler
from datetime import datetime

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.news_tools import NewsSearcher, ContentDownloader
from src.news_tools.github_archiver import GitHubArchiver

# 全局实例
news_searcher = None
content_downloader = None
github_archiver = None

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

def get_github_archiver():
    """获取GitHub归档器实例"""
    global github_archiver
    if github_archiver is None:
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            raise ValueError("GITHUB_TOKEN环境变量未设置")
        repo_name = os.getenv('GITHUB_REPO', 'clkhoo5211/upgraded-octo-fortnight')
        github_archiver = GitHubArchiver(github_token, repo_name)
    return github_archiver

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """处理归档请求"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body) if body else {}
            else:
                data = {}
            
            # 获取参数
            keywords = data.get('keywords')
            categories = data.get('categories')
            languages = data.get('languages', 'all')
            date_range = data.get('date_range', 'last_7_days')
            max_results = int(data.get('max_results', 50))
            download_content = data.get('download_content', True)  # 是否下载完整内容
            save_to_github = data.get('save_to_github', False)  # 是否保存到GitHub
            save_format = data.get('save_format', 'md_with_html')  # 保存格式
            target_date = data.get('target_date')  # 目标日期 YYYY-MM-DD
            
            # 步骤1: 搜索新闻
            searcher = get_news_searcher()
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
            
            # 步骤2: 下载完整内容（如果需要）
            if download_content:
                downloader = get_content_downloader()
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    # 批量下载内容
                    urls = [news.get('url') for news in news_list if news.get('url')]
                    downloaded_contents = loop.run_until_complete(
                        downloader.download_multiple(urls, include_images=True, include_banners=True)
                    )
                    
                    # 合并内容到新闻列表
                    url_to_content = {item['url']: item for item in downloaded_contents}
                    for news in news_list:
                        url = news.get('url')
                        if url and url in url_to_content:
                            content_data = url_to_content[url]
                            news['content'] = content_data.get('content', news.get('content', ''))
                            news['html_body'] = content_data.get('html_body', '')
                            news['images'] = content_data.get('images', [])
                            news['banners'] = content_data.get('banners', [])
                            news['videos'] = content_data.get('videos', [])
                finally:
                    loop.close()
            
            # 步骤3: 保存到GitHub（如果需要）
            saved_files = []
            if save_to_github:
                try:
                    archiver = get_github_archiver()
                    save_result = archiver.classify_and_save_news(
                        news_list,
                        save_format=save_format,
                        target_date=target_date
                    )
                    saved_files = save_result.get('saved_files', [])
                except Exception as e:
                    # GitHub保存失败不影响返回结果
                    print(f"GitHub保存失败: {e}")
            
            # 返回结果
            response_data = {
                'success': True,
                'search_results': {
                    'count': len(news_list),
                    'news': news_list
                },
                'download_enabled': download_content,
                'github_save_enabled': save_to_github,
                'saved_files': saved_files,
                'summary': {
                    'total_news': len(news_list),
                    'with_content': sum(1 for n in news_list if n.get('content')),
                    'with_html': sum(1 for n in news_list if n.get('html_body')),
                    'with_images': sum(1 for n in news_list if n.get('images')),
                    'with_videos': sum(1 for n in news_list if n.get('videos')),
                    'categories': {}
                }
            }
            
            # 统计分类
            for news in news_list:
                category = news.get('category', 'unknown')
                response_data['summary']['categories'][category] = \
                    response_data['summary']['categories'].get(category, 0) + 1
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"归档错误: {error_trace}")
            
            error_response = {
                'success': False,
                'error': str(e),
                'traceback': error_trace
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))

