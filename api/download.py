"""
新闻内容下载API端点
"""
import os
import json
import sys
import asyncio

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

def handler(request):
    """
    下载完整新闻内容
    
    请求参数:
        news_url: 新闻URL（必需）
        include_images: 是否包含图片，默认true
        include_banners: 是否包含横幅，默认true
    
    返回:
        {
            "url": "...",
            "title": "...",
            "content": "...",
            "images": [...],
            "banners": [...],
            "success": true
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
            data = request.get('queryStringParameters') if isinstance(request, dict) else {}
            data = (data or {}).copy()
        
        news_url = data.get('news_url')
        if not news_url:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': False,
                    'error': 'news_url参数是必需的'
                }, ensure_ascii=False)
            }
        
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
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result, ensure_ascii=False)
        }
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"下载错误: {error_trace}")
        
        data = {}
        if isinstance(request, dict):
            body = request.get('body', '{}')
            if isinstance(body, str):
                try:
                    data = json.loads(body)
                except:
                    pass
            else:
                data = body
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'url': data.get('news_url', ''),
                'title': '',
                'content': '',
                'images': [],
                'banners': [],
                'success': False,
                'error': str(e),
                'traceback': error_trace
            }, ensure_ascii=False)
        }
