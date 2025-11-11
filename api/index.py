"""
Vercel Serverless Functions入口
提供HTTP API访问全网新闻服务
"""
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def index():
    """API首页"""
    return jsonify({
        'service': 'Global News Aggregator API',
        'version': '1.0.0',
        'endpoints': {
            '/api/search': 'POST - 搜索全网新闻',
            '/api/download': 'POST - 下载新闻完整内容',
            '/api/health': 'GET - 健康检查'
        },
        'documentation': 'https://github.com/clkhoo5211/upgraded-octo-fortnight',
        'status': 'online'
    })

@app.route('/api/health')
def health():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'service': 'global-news-mcp',
        'version': '1.0.0'
    })

# Vercel入口
def handler(request):
    """Vercel Serverless Function入口"""
    return app(request.environ, lambda *args: None)

if __name__ == '__main__':
    app.run(debug=True)
