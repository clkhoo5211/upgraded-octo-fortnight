"""
分类管理器
支持动态添加、删除、更新分类和关键词
"""
import os
import json
from typing import Dict, List, Optional
from datetime import datetime


class CategoryManager:
    """分类管理器类"""
    
    def __init__(self, config_file: str = None):
        """
        初始化分类管理器
        
        Args:
            config_file: 自定义分类配置文件路径（可选）
        """
        self.config_file = config_file or os.path.join(
            os.path.dirname(__file__), 
            '..', 
            '..', 
            'custom_categories.json'
        )
        
        # 默认分类（从news_searcher导入）
        from .news_searcher import NewsSearcher
        self.default_categories = NewsSearcher.CATEGORY_KEYWORDS.copy()
        
        # 加载自定义分类
        self.custom_categories = self._load_custom_categories()
    
    def _load_custom_categories(self) -> Dict[str, List[str]]:
        """加载自定义分类"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载自定义分类失败: {e}")
                return {}
        return {}
    
    def _save_custom_categories(self):
        """保存自定义分类到文件"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_categories, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存自定义分类失败: {e}")
            return False
    
    def get_all_categories(self) -> Dict[str, List[str]]:
        """获取所有分类（默认+自定义）"""
        all_categories = self.default_categories.copy()
        
        # 合并自定义分类
        for category, keywords in self.custom_categories.items():
            if category in all_categories:
                # 如果分类已存在，合并关键词
                existing_keywords = set(all_categories[category])
                new_keywords = set(keywords)
                all_categories[category] = list(existing_keywords | new_keywords)
            else:
                # 新分类
                all_categories[category] = keywords
        
        return all_categories
    
    def add_category(
        self,
        category: str,
        keywords: List[str],
        merge: bool = False
    ) -> Dict[str, any]:
        """
        添加新分类或更新现有分类
        
        Args:
            category: 分类名称
            keywords: 关键词列表
            merge: 如果分类已存在，是否合并关键词（True）还是替换（False）
            
        Returns:
            操作结果
        """
        if not category or not keywords:
            return {
                'success': False,
                'error': '分类名称和关键词不能为空'
            }
        
        # 清理关键词（去重、去空）
        cleaned_keywords = list(set([kw.strip() for kw in keywords if kw.strip()]))
        
        if not cleaned_keywords:
            return {
                'success': False,
                'error': '关键词列表不能为空'
            }
        
        # 检查是否已存在
        if category in self.custom_categories:
            if merge:
                # 合并关键词
                existing_keywords = set(self.custom_categories[category])
                new_keywords = set(cleaned_keywords)
                self.custom_categories[category] = list(existing_keywords | new_keywords)
                action = 'merged'
            else:
                # 替换关键词
                self.custom_categories[category] = cleaned_keywords
                action = 'updated'
        else:
            # 新分类
            self.custom_categories[category] = cleaned_keywords
            action = 'created'
        
        # 保存到文件
        if self._save_custom_categories():
            return {
                'success': True,
                'action': action,
                'category': category,
                'keyword_count': len(self.custom_categories[category]),
                'keywords': self.custom_categories[category]
            }
        else:
            return {
                'success': False,
                'error': '保存分类失败'
            }
    
    def add_keywords_to_category(
        self,
        category: str,
        keywords: List[str]
    ) -> Dict[str, any]:
        """
        向现有分类添加关键词
        
        Args:
            category: 分类名称
            keywords: 要添加的关键词列表
            
        Returns:
            操作结果
        """
        if not category:
            return {
                'success': False,
                'error': '分类名称不能为空'
            }
        
        # 清理关键词
        cleaned_keywords = list(set([kw.strip() for kw in keywords if kw.strip()]))
        
        if not cleaned_keywords:
            return {
                'success': False,
                'error': '关键词列表不能为空'
            }
        
        # 如果分类不存在，创建它
        if category not in self.custom_categories:
            if category in self.default_categories:
                # 从默认分类复制
                self.custom_categories[category] = self.default_categories[category].copy()
            else:
                # 创建新分类
                self.custom_categories[category] = []
        
        # 添加关键词
        existing_keywords = set(self.custom_categories[category])
        new_keywords = set(cleaned_keywords)
        self.custom_categories[category] = list(existing_keywords | new_keywords)
        
        # 保存
        if self._save_custom_categories():
            return {
                'success': True,
                'action': 'keywords_added',
                'category': category,
                'added_count': len(new_keywords - existing_keywords),
                'total_keywords': len(self.custom_categories[category]),
                'keywords': self.custom_categories[category]
            }
        else:
            return {
                'success': False,
                'error': '保存分类失败'
            }
    
    def remove_category(self, category: str) -> Dict[str, any]:
        """
        删除自定义分类
        
        Args:
            category: 分类名称
            
        Returns:
            操作结果
        """
        if category not in self.custom_categories:
            return {
                'success': False,
                'error': f'分类 {category} 不存在或为默认分类'
            }
        
        # 删除分类
        del self.custom_categories[category]
        
        # 保存
        if self._save_custom_categories():
            return {
                'success': True,
                'action': 'deleted',
                'category': category
            }
        else:
            return {
                'success': False,
                'error': '保存分类失败'
            }
    
    def remove_keywords_from_category(
        self,
        category: str,
        keywords: List[str]
    ) -> Dict[str, any]:
        """
        从分类中删除关键词
        
        Args:
            category: 分类名称
            keywords: 要删除的关键词列表
            
        Returns:
            操作结果
        """
        if category not in self.custom_categories:
            if category in self.default_categories:
                # 从默认分类复制，然后删除
                self.custom_categories[category] = self.default_categories[category].copy()
            else:
                return {
                    'success': False,
                    'error': f'分类 {category} 不存在'
                }
        
        # 删除关键词
        keywords_to_remove = set([kw.strip() for kw in keywords if kw.strip()])
        existing_keywords = set(self.custom_categories[category])
        removed_keywords = existing_keywords & keywords_to_remove
        
        self.custom_categories[category] = list(existing_keywords - keywords_to_remove)
        
        # 如果分类为空，删除它
        if not self.custom_categories[category]:
            del self.custom_categories[category]
        
        # 保存
        if self._save_custom_categories():
            return {
                'success': True,
                'action': 'keywords_removed',
                'category': category,
                'removed_count': len(removed_keywords),
                'remaining_keywords': len(self.custom_categories.get(category, [])),
                'removed_keywords': list(removed_keywords)
            }
        else:
            return {
                'success': False,
                'error': '保存分类失败'
            }
    
    def get_category_info(self, category: str) -> Dict[str, any]:
        """
        获取分类信息
        
        Args:
            category: 分类名称
            
        Returns:
            分类信息
        """
        all_categories = self.get_all_categories()
        
        if category not in all_categories:
            return {
                'exists': False,
                'error': f'分类 {category} 不存在'
            }
        
        is_custom = category in self.custom_categories
        is_default = category in self.default_categories
        
        return {
            'exists': True,
            'category': category,
            'is_custom': is_custom,
            'is_default': is_default,
            'keyword_count': len(all_categories[category]),
            'keywords': all_categories[category],
            'default_keywords': self.default_categories.get(category, []),
            'custom_keywords': self.custom_categories.get(category, [])
        }
    
    def list_all_categories(self) -> Dict[str, any]:
        """列出所有分类"""
        all_categories = self.get_all_categories()
        
        result = {
            'total_categories': len(all_categories),
            'default_categories': len(self.default_categories),
            'custom_categories': len(self.custom_categories),
            'categories': {}
        }
        
        for category, keywords in all_categories.items():
            result['categories'][category] = {
                'keyword_count': len(keywords),
                'is_custom': category in self.custom_categories,
                'is_default': category in self.default_categories,
                'sample_keywords': keywords[:10]  # 显示前10个关键词
            }
        
        return result

