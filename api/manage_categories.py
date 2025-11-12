"""
分类管理API端点
支持动态添加、删除、更新分类和关键词
"""
import os
import json
import sys
from http.server import BaseHTTPRequestHandler

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.news_tools.category_manager import CategoryManager

# 全局分类管理器实例
category_manager = None

def get_category_manager():
    """获取分类管理器实例"""
    global category_manager
    if category_manager is None:
        category_manager = CategoryManager()
    return category_manager

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """获取分类信息"""
        try:
            manager = get_category_manager()
            
            # 解析查询参数
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(self.path)
            query_params = parse_qs(parsed.query)
            
            category = query_params.get('category', [None])[0]
            
            if category:
                # 获取特定分类信息
                result = manager.get_category_info(category)
            else:
                # 列出所有分类
                result = manager.list_all_categories()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"获取分类信息错误: {error_trace}")
            
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
    
    def do_POST(self):
        """添加分类或关键词"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body) if body else {}
            else:
                data = {}
            
            manager = get_category_manager()
            
            action = data.get('action', 'add_category')  # add_category, add_keywords
            
            if action == 'add_category':
                # 添加新分类或更新现有分类
                category = data.get('category')
                keywords = data.get('keywords', [])
                merge = data.get('merge', False)  # 是否合并关键词
                
                if not category or not keywords:
                    result = {
                        'success': False,
                        'error': 'category和keywords参数是必需的'
                    }
                else:
                    result = manager.add_category(category, keywords, merge)
            
            elif action == 'add_keywords':
                # 向现有分类添加关键词
                category = data.get('category')
                keywords = data.get('keywords', [])
                
                if not category or not keywords:
                    result = {
                        'success': False,
                        'error': 'category和keywords参数是必需的'
                    }
                else:
                    result = manager.add_keywords_to_category(category, keywords)
            
            else:
                result = {
                    'success': False,
                    'error': f'未知操作: {action}'
                }
            
            status_code = 200 if result.get('success', False) else 400
            
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"添加分类错误: {error_trace}")
            
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
    
    def do_DELETE(self):
        """删除分类或关键词"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body) if body else {}
            else:
                data = {}
            
            manager = get_category_manager()
            
            action = data.get('action', 'remove_category')  # remove_category, remove_keywords
            
            if action == 'remove_category':
                # 删除分类
                category = data.get('category')
                
                if not category:
                    result = {
                        'success': False,
                        'error': 'category参数是必需的'
                    }
                else:
                    result = manager.remove_category(category)
            
            elif action == 'remove_keywords':
                # 从分类中删除关键词
                category = data.get('category')
                keywords = data.get('keywords', [])
                
                if not category or not keywords:
                    result = {
                        'success': False,
                        'error': 'category和keywords参数是必需的'
                    }
                else:
                    result = manager.remove_keywords_from_category(category, keywords)
            
            else:
                result = {
                    'success': False,
                    'error': f'未知操作: {action}'
                }
            
            status_code = 200 if result.get('success', False) else 400
            
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"删除分类错误: {error_trace}")
            
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
    
    def do_PUT(self):
        """更新分类（等同于POST add_category with merge=False）"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body) if body else {}
            else:
                data = {}
            
            manager = get_category_manager()
            
            category = data.get('category')
            keywords = data.get('keywords', [])
            
            if not category or not keywords:
                result = {
                    'success': False,
                    'error': 'category和keywords参数是必需的'
                }
            else:
                # PUT请求默认替换关键词
                result = manager.add_category(category, keywords, merge=False)
            
            status_code = 200 if result.get('success', False) else 400
            
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"更新分类错误: {error_trace}")
            
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

