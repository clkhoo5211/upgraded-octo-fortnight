"""
最简单的测试端点 - 不导入任何外部模块
"""
import json

def handler(request):
    """最简单的handler"""
    try:
        return json.dumps({
            'status': 'ok',
            'message': 'Simple test endpoint works',
            'python_version': '3.12'
        }), {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    except Exception as e:
        return json.dumps({
            'error': str(e),
            'type': type(e).__name__
        }), {
            'Content-Type': 'application/json'
        }
