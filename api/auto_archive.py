"""
自动归档API端点
用于Vercel Cron定时任务，自动将前一日的内容转换为MD文档并保存
"""
import os
import json
import sys
import asyncio
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timedelta

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
    def do_GET(self):
        """处理自动归档请求（由Vercel Cron调用）"""
        try:
            # 获取前一日日期
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            # 获取参数（从查询字符串或环境变量）
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(self.path)
            query_params = parse_qs(parsed.query)
            
            categories = query_params.get('categories', [None])[0]
            if categories:
                categories = categories.split(',')
            else:
                # 默认归档所有分类
                from src.news_tools.category_manager import CategoryManager
                category_manager = CategoryManager()
                all_categories = category_manager.get_all_categories()
                categories = list(all_categories.keys())
            
            languages = query_params.get('languages', ['all'])[0]
            max_results = int(query_params.get('max_results', ['100'])[0])
            download_content = query_params.get('download_content', ['true'])[0].lower() == 'true'
            save_format = query_params.get('save_format', ['md_with_html'])[0]
            
            # 步骤1: 搜索前一日新闻（仅昨日和今日的新闻）
            searcher = get_news_searcher()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                news_list = loop.run_until_complete(
                    searcher.search_news(
                        keywords=None,  # 搜索所有新闻
                        categories=categories,
                        languages=languages,
                        date_range='yesterday',  # 仅前一日
                        max_results=max_results
                    )
                )
            finally:
                loop.close()
            
            if not news_list:
                result = {
                    'success': True,
                    'message': f'前一日({yesterday})没有找到新闻',
                    'date': yesterday,
                    'news_count': 0,
                    'saved_files': []
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
                return
            
            # 步骤2: 下载完整内容（如果需要）
            if download_content:
                downloader = get_content_downloader()
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    urls = [news.get('url') for news in news_list if news.get('url')]
                    downloaded_contents = loop.run_until_complete(
                        downloader.download_multiple(urls, include_images=True, include_banners=True)
                    )
                    
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
            
            # 步骤3: 保存到GitHub
            archiver = get_github_archiver()
            save_result = archiver.classify_and_save_news(
                news_list,
                save_format=save_format,
                target_date=yesterday  # 保存到前一日目录
            )
            
            # 返回结果
            response_data = {
                'success': save_result.get('success', False),
                'message': f'前一日({yesterday})新闻归档完成',
                'date': yesterday,
                'news_count': len(news_list),
                'saved_files': save_result.get('saved_files', []),
                'errors': save_result.get('errors', []),
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
            
            status_code = 200 if response_data['success'] else 500
            
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"自动归档错误: {error_trace}")
            
            error_response = {
                'success': False,
                'error': str(e),
                'traceback': error_trace,
                'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))

