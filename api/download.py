"""
新闻内容下载API端点
"""
import os
import sys
import asyncio
from flask import Flask, jsonify, request

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.news_tools import ContentDownloader

app = Flask(__name__)

# 全局下载器实例
content_downloader = None

def get_content_downloader():
    """获取内容下载器实例"""
    global content_downloader
    if content_downloader is None:
        content_downloader = ContentDownloader()
    return content_downloader

@app.route('/api/download', methods=['POST', 'GET'])
def download_content():
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
    app.run(debug=True, port=5002)
