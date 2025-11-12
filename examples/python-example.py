#!/usr/bin/env python3
"""
使用Global News Aggregator API的Python示例
可以在任何Python项目中使用
"""
import requests
import json
from datetime import datetime
from typing import Optional, List, Dict

# API基础地址
API_BASE = "https://upgraded-octo-fortnight.vercel.app"


class NewsAPI:
    """新闻API客户端"""
    
    def __init__(self, base_url: str = API_BASE):
        self.base_url = base_url
    
    def search_news(
        self,
        keywords: Optional[str] = None,
        categories: Optional[List[str]] = None,
        languages: str = "all",
        date_range: str = "today_and_yesterday",
        max_results: int = 50
    ) -> Dict:
        """
        搜索新闻
        
        Args:
            keywords: 搜索关键词
            categories: 分类列表
            languages: 语言 (zh/en/all)
            date_range: 日期范围
            max_results: 最大结果数
        
        Returns:
            包含新闻列表的字典
        """
        url = f"{self.base_url}/api/search"
        payload = {
            "keywords": keywords,
            "categories": categories,
            "languages": languages,
            "date_range": date_range,
            "max_results": max_results
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e), "count": 0, "news": []}
    
    def download_content(
        self,
        news_url: str,
        include_images: bool = True,
        include_banners: bool = True
    ) -> Dict:
        """
        下载新闻完整内容
        
        Args:
            news_url: 新闻URL
            include_images: 是否包含图片
            include_banners: 是否包含横幅
        
        Returns:
            包含完整内容的字典
        """
        url = f"{self.base_url}/api/download"
        payload = {
            "news_url": news_url,
            "include_images": include_images,
            "include_banners": include_banners
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def archive_news(
        self,
        keywords: Optional[str] = None,
        categories: Optional[List[str]] = None,
        max_results: int = 50,
        download_content: bool = True,
        save_to_github: bool = False,
        save_format: str = "md_with_html"
    ) -> Dict:
        """
        完整归档（搜索+下载+保存）
        
        Args:
            keywords: 搜索关键词
            categories: 分类列表
            max_results: 最大结果数
            download_content: 是否下载内容
            save_to_github: 是否保存到GitHub（需要API端配置GITHUB_TOKEN）
            save_format: 保存格式
        
        Returns:
            归档结果字典
        """
        url = f"{self.base_url}/api/archive"
        payload = {
            "keywords": keywords,
            "categories": categories,
            "max_results": max_results,
            "download_content": download_content,
            "save_to_github": save_to_github,
            "save_format": save_format
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def get_categories(self) -> Dict:
        """获取所有分类"""
        url = f"{self.base_url}/api/manage_categories"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def health_check(self) -> Dict:
        """健康检查"""
        url = f"{self.base_url}/api/health"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "unhealthy", "error": str(e)}


def main():
    """示例用法"""
    api = NewsAPI()
    
    # 1. 健康检查
    print("🔍 检查API状态...")
    health = api.health_check()
    print(f"状态: {health.get('status', 'unknown')}")
    print()
    
    # 2. 搜索科技新闻
    print("📰 搜索科技新闻...")
    results = api.search_news(
        keywords="AI",
        categories=["tech"],
        max_results=5,
        date_range="today_and_yesterday"
    )
    
    if results.get('success') and results.get('count', 0) > 0:
        print(f"✅ 找到 {results['count']} 条新闻\n")
        
        # 显示前3条新闻
        for i, news in enumerate(results['news'][:3], 1):
            print(f"{i}. {news.get('title', 'N/A')}")
            print(f"   来源: {news.get('source', 'N/A')}")
            print(f"   链接: {news.get('url', 'N/A')}")
            print()
        
        # 3. 下载第一条新闻的完整内容
        if results['news']:
            first_news = results['news'][0]
            print(f"📥 下载完整内容: {first_news.get('title', '')[:50]}...")
            content = api.download_content(first_news['url'])
            
            if content.get('success'):
                print(f"✅ 内容长度: {len(content.get('content', ''))} 字符")
                print(f"✅ 图片数: {len(content.get('images', []))}")
                print(f"✅ 视频数: {len(content.get('videos', []))}")
            else:
                print(f"❌ 下载失败: {content.get('error')}")
    else:
        print(f"❌ 搜索失败: {results.get('error', '未知错误')}")
    
    # 4. 查看所有分类
    print("\n📁 查看所有分类...")
    categories = api.get_categories()
    if categories.get('success'):
        print(f"✅ 找到 {len(categories.get('categories', {}))} 个分类:")
        for cat, keywords in categories.get('categories', {}).items():
            print(f"   - {cat}: {len(keywords)} 个关键词")
    else:
        print(f"❌ 获取分类失败: {categories.get('error')}")


if __name__ == "__main__":
    main()

