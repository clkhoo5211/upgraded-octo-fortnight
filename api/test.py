"""
最简单的测试端点
"""
import json

def handler(request):
    """最简单的测试handler"""
    try:
        return json.dumps({
            'status': 'ok',
            'message': 'Test endpoint works',
            'handler_format': 'tuple_return'
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
