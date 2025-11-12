"""
最简单的测试端点 - 验证Vercel Python运行时格式
"""
def handler(request):
    """最简单的测试handler"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': '{"status": "ok", "message": "Test endpoint works"}'
    }

