"""
智能新闻过滤系统
支持纳入/排除规则、内容质量过滤等
"""
from typing import List, Dict, Any, Optional, Set
import re
from urllib.parse import urlparse


class NewsFilter:
    """新闻过滤器类"""
    
    def __init__(
        self,
        include_keywords: Optional[List[str]] = None,
        exclude_keywords: Optional[List[str]] = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        min_content_length: int = 50,
        max_content_length: int = 50000,
        require_image: bool = False,
        language_filter: Optional[str] = None
    ):
        """
        初始化过滤器
        
        Args:
            include_keywords: 必须包含的关键词列表（满足任一即可）
            exclude_keywords: 排除关键词列表（包含任一则排除）
            include_domains: 允许的域名白名单
            exclude_domains: 排除的域名黑名单
            min_content_length: 最小内容长度
            max_content_length: 最大内容长度
            require_image: 是否要求必须有图片
            language_filter: 语言过滤 (zh/en/all)
        """
        self.include_keywords = [k.lower() for k in (include_keywords or [])]
        self.exclude_keywords = [k.lower() for k in (exclude_keywords or [])]
        self.include_domains = set(include_domains or [])
        self.exclude_domains = set(exclude_domains or [])
        self.min_content_length = min_content_length
        self.max_content_length = max_content_length
        self.require_image = require_image
        self.language_filter = language_filter
        
        # 默认排除的垃圾词
        self.spam_keywords = [
            'sponsored', 'advertisement', '广告', 'ad:', '[ad]',
            'promotional content', '推广内容'
        ]
    
    def add_include_keywords(self, keywords: List[str]):
        """添加包含关键词"""
        self.include_keywords.extend([k.lower() for k in keywords])
    
    def add_exclude_keywords(self, keywords: List[str]):
        """添加排除关键词"""
        self.exclude_keywords.extend([k.lower() for k in keywords])
    
    def add_include_domains(self, domains: List[str]):
        """添加允许的域名"""
        self.include_domains.update(domains)
    
    def add_exclude_domains(self, domains: List[str]):
        """添加排除的域名"""
        self.exclude_domains.update(domains)
    
    def filter_news_list(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量过滤新闻列表
        
        Args:
            news_list: 新闻列表
            
        Returns:
            过滤后的新闻列表
        """
        filtered = []
        
        for news in news_list:
            if self.should_include(news):
                # 计算新闻质量分数
                news['quality_score'] = self._calculate_quality_score(news)
                filtered.append(news)
        
        # 按质量分数排序
        filtered.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
        
        return filtered
    
    def should_include(self, news: Dict[str, Any]) -> bool:
        """
        判断是否应该纳入新闻
        
        Args:
            news: 新闻数据字典
            
        Returns:
            True表示应该纳入，False表示应该排除
        """
        # 1. 检查基本字段
        if not news.get('title') or not news.get('url'):
            return False
        
        # 2. 内容长度检查
        content = news.get('content', '') or news.get('description', '')
        content_length = len(content)
        if content_length < self.min_content_length:
            return False
        if content_length > self.max_content_length:
            return False
        
        # 3. 图片要求检查
        if self.require_image:
            if not news.get('image_url'):
                return False
        
        # 4. 语言过滤
        if self.language_filter and self.language_filter != 'all':
            if news.get('language', '') != self.language_filter:
                return False
        
        # 5. 域名检查
        url = news.get('url', '')
        domain = self._extract_domain(url)
        
        # 域名黑名单检查
        if domain in self.exclude_domains:
            return False
        
        # 域名白名单检查（如果设置了白名单）
        if self.include_domains and domain not in self.include_domains:
            return False
        
        # 6. 关键词检查
        text = f"{news.get('title', '')} {news.get('description', '')} {content}".lower()
        
        # 排除垃圾关键词
        for spam in self.spam_keywords:
            if spam in text:
                return False
        
        # 排除关键词检查
        if self.exclude_keywords:
            for keyword in self.exclude_keywords:
                if keyword in text:
                    return False
        
        # 纳入关键词检查（如果设置了，必须包含至少一个）
        if self.include_keywords:
            found = False
            for keyword in self.include_keywords:
                if keyword in text:
                    found = True
                    break
            if not found:
                return False
        
        return True
    
    def _extract_domain(self, url: str) -> str:
        """提取域名"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # 移除www前缀
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return ''
    
    def _calculate_quality_score(self, news: Dict[str, Any]) -> float:
        """
        计算新闻质量分数（0-100）
        
        评分因素：
        - 标题长度适中
        - 有描述和内容
        - 有图片
        - 发布时间明确
        - 来源可靠
        """
        score = 0.0
        
        # 标题评分（0-20分）
        title = news.get('title', '')
        if 10 <= len(title) <= 100:
            score += 20
        elif 5 <= len(title) < 10 or 100 < len(title) <= 150:
            score += 10
        
        # 描述评分（0-20分）
        description = news.get('description', '')
        if len(description) > 50:
            score += 20
        elif len(description) > 20:
            score += 10
        
        # 内容评分（0-20分）
        content = news.get('content', '')
        if len(content) > 500:
            score += 20
        elif len(content) > 200:
            score += 15
        elif len(content) > 100:
            score += 10
        
        # 图片评分（0-15分）
        if news.get('image_url'):
            score += 15
        
        # 时间评分（0-10分）
        if news.get('published_at'):
            score += 10
        
        # 来源评分（0-15分）
        source = news.get('source', '').lower()
        trusted_sources = [
            'bbc', 'cnn', 'reuters', 'bloomberg', 'wsj',
            '新华网', '人民网', '央视', '财新'
        ]
        if any(trusted in source for trusted in trusted_sources):
            score += 15
        elif source:
            score += 10
        
        return min(score, 100.0)
    
    @classmethod
    def create_default_filter(cls) -> 'NewsFilter':
        """创建默认过滤器（较宽松）"""
        return cls(
            min_content_length=50,
            exclude_keywords=['sponsored', 'advertisement', '广告'],
            exclude_domains=['spam.com', 'ads.example.com']
        )
    
    @classmethod
    def create_strict_filter(cls) -> 'NewsFilter':
        """创建严格过滤器"""
        return cls(
            min_content_length=200,
            require_image=True,
            exclude_keywords=[
                'sponsored', 'advertisement', '广告', 
                'promotional', '推广', 'clickbait'
            ]
        )
