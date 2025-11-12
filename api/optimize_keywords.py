"""
关键词优化API端点
从多个搜索引擎和社交平台抓取关键词，自动扩展关键词列表
"""
import os
import json
import sys
import asyncio
from http.server import BaseHTTPRequestHandler

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.news_tools.news_searcher import NewsSearcher
from src.news_tools.keyword_optimizer import KeywordOptimizer

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """处理关键词优化请求"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body) if body else {}
            else:
                data = {}
            
            # 获取参数
            categories = data.get('categories')  # 要优化的分类列表，None表示全部
            max_new_per_category = int(data.get('max_new_per_category', 30))
            search_sources = data.get('search_sources', ['google', 'bing', 'reddit', 'hackernews'])
            
            # 获取当前关键词
            searcher = NewsSearcher()
            category_keywords = searcher.CATEGORY_KEYWORDS
            
            # 如果指定了分类，只优化这些分类
            if categories:
                category_keywords = {
                    cat: keywords 
                    for cat, keywords in category_keywords.items() 
                    if cat in categories
                }
            
            # 创建优化器
            optimizer = KeywordOptimizer()
            
            # 异步优化
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                results = loop.run_until_complete(
                    optimizer.optimize_all_categories(
                        category_keywords,
                        max_new_per_category
                    )
                )
            finally:
                loop.close()
                asyncio.set_event_loop(None)
            
            # 构建响应
            response_data = {
                'success': True,
                'optimized_categories': len(results),
                'results': results,
                'summary': {}
            }
            
            # 生成摘要
            total_original = 0
            total_new = 0
            total_final = 0
            
            for category, result in results.items():
                if 'error' not in result:
                    total_original += result['original_count']
                    total_new += len(result['new_keywords'])
                    total_final += result['total_count']
            
            response_data['summary'] = {
                'total_original_keywords': total_original,
                'total_new_keywords': total_new,
                'total_final_keywords': total_final,
                'improvement_rate': f"{(total_new / total_original * 100):.1f}%" if total_original > 0 else "0%"
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"关键词优化错误: {error_trace}")
            
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
    
    def do_GET(self):
        """获取当前关键词统计"""
        try:
            searcher = NewsSearcher()
            category_keywords = searcher.CATEGORY_KEYWORDS
            
            stats = {
                'total_categories': len(category_keywords),
                'categories': {}
            }
            
            for category, keywords in category_keywords.items():
                stats['categories'][category] = {
                    'keyword_count': len(keywords),
                    'sample_keywords': keywords[:10]  # 显示前10个关键词作为示例
                }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(stats, ensure_ascii=False).encode('utf-8'))
        
        except Exception as e:
            error_response = {
                'success': False,
                'error': str(e)
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))

