"""
新闻内容下载模块
支持下载完整新闻内容、图片和横幅
"""
import httpx
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
import asyncio


class ContentDownloader:
    """内容下载器类"""
    
    def __init__(self):
        """初始化内容下载器"""
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
    
    async def download_news_content(
        self,
        news_url: str,
        include_images: bool = True,
        include_banners: bool = True
    ) -> Dict[str, Any]:
        """
        下载完整新闻内容
        
        Args:
            news_url: 新闻链接
            include_images: 是否下载图片
            include_banners: 是否下载横幅
            
        Returns:
            包含完整内容的字典
        """
        try:
            # 下载页面内容
            response = await self.client.get(news_url)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 提取标题
            title = self._extract_title(soup)
            
            # 提取正文
            content = self._extract_content(soup)
            
            # 提取图片
            images = []
            banners = []
            
            if include_images or include_banners:
                all_images = self._extract_images(soup, news_url)
                
                if include_banners and all_images:
                    # 第一张图作为横幅
                    banners = [all_images[0]]
                
                if include_images:
                    images = all_images
            
            return {
                'url': news_url,
                'title': title,
                'content': content,
                'images': images,
                'banners': banners,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            return {
                'url': news_url,
                'title': '',
                'content': '',
                'images': [],
                'banners': [],
                'success': False,
                'error': str(e)
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取标题"""
        # 尝试多种选择器
        selectors = [
            'h1',
            'title',
            'meta[property="og:title"]',
            'meta[name="twitter:title"]',
            '.article-title',
            '.post-title'
        ]
        
        for selector in selectors:
            if selector.startswith('meta'):
                element = soup.select_one(selector)
                if element and element.get('content'):
                    return element.get('content').strip()
            else:
                element = soup.select_one(selector)
                if element and element.get_text(strip=True):
                    return element.get_text(strip=True)
        
        return ''
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """提取正文内容"""
        # 移除不需要的元素
        for element in soup.select('script, style, nav, header, footer, aside, .ad, .advertisement'):
            element.decompose()
        
        # 尝试多种选择器
        content_selectors = [
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.content',
            'main',
            '#content'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                # 提取所有段落
                paragraphs = element.find_all(['p', 'h2', 'h3', 'h4', 'h5', 'h6'])
                content_parts = []
                
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:  # 过滤太短的段落
                        content_parts.append(text)
                
                if content_parts:
                    return '\n\n'.join(content_parts)
        
        # 如果找不到特定容器，提取所有段落
        paragraphs = soup.find_all('p')
        content_parts = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) > 20:
                content_parts.append(text)
        
        return '\n\n'.join(content_parts) if content_parts else ''
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """提取图片URL"""
        images = []
        
        # 查找所有img标签
        img_tags = soup.find_all('img')
        
        for img in img_tags:
            # 尝试多个属性
            img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            
            if img_url:
                # 处理相对URL
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    from urllib.parse import urljoin
                    img_url = urljoin(base_url, img_url)
                
                # 过滤小图标和广告
                if not any(x in img_url.lower() for x in ['icon', 'logo', 'avatar', 'ad-']):
                    if img_url.startswith('http'):
                        images.append(img_url)
        
        # 去重并返回
        return list(dict.fromkeys(images))
    
    async def download_multiple(
        self,
        urls: List[str],
        include_images: bool = True,
        include_banners: bool = True
    ) -> List[Dict[str, Any]]:
        """批量下载新闻内容"""
        tasks = [
            self.download_news_content(url, include_images, include_banners)
            for url in urls
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    'url': '',
                    'title': '',
                    'content': '',
                    'images': [],
                    'banners': [],
                    'success': False,
                    'error': str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
