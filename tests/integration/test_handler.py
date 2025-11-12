"""
测试Vercel Python运行时格式
"""
def handler(request):
    """最简单的测试handler"""
    return "Hello from Vercel", {"Content-Type": "text/plain"}

