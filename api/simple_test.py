"""
最简单的测试端点 - 不导入任何外部模块
"""
import json

def handler(request):
    """最简单的handler，不依赖任何外部模块"""
    try:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'status': 'ok',
                'message': 'Simple test endpoint works',
                'python_version': '3.12'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': str(e),
                'type': type(e).__name__
            })
        }

