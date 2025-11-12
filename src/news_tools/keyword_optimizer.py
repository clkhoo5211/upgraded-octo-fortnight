"""
关键词优化工具
从多个搜索引擎和社交平台抓取关键词，自动扩展和优化关键词列表
"""
import os
import httpx
import asyncio
import json
from typing import List, Dict, Set, Any
from collections import Counter
import re
from datetime import datetime


class KeywordOptimizer:
    """关键词优化器"""
    
    def __init__(
        self,
        serpapi_key: str = None,
        bing_api_key: str = None,
        google_search_key: str = None,
        google_engine_id: str = None
    ):
        """
        初始化关键词优化器
        
        Args:
            serpapi_key: SerpAPI密钥（支持Google/Bing/百度/Yahoo）
            bing_api_key: Bing Search API密钥
            google_search_key: Google Custom Search API密钥
            google_engine_id: Google Custom Search Engine ID
        """
        self.serpapi_key = serpapi_key or os.getenv('SERPAPI_KEY')
        self.bing_api_key = bing_api_key or os.getenv('BING_API_KEY')
        self.google_search_key = google_search_key or os.getenv('GOOGLE_SEARCH_API_KEY')
        self.google_engine_id = google_engine_id or os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # 社交平台API端点（使用公开API）
        self.social_platforms = {
            'reddit': 'https://www.reddit.com/r/{}/search.json?q={}&sort=relevance&limit=25',
            'twitter': 'https://api.twitter.com/2/tweets/search/recent?query={}&max_results=25',
            'hackernews': 'https://hn.algolia.com/api/v1/search?query={}&tags=story&hitsPerPage=25'
        }
    
    async def search_google_news(self, query: str, max_results: int = 50) -> List[str]:
        """从Google News搜索并提取关键词"""
        keywords = set()
        
        try:
            # 使用SerpAPI搜索Google News
            if self.serpapi_key:
                url = "https://serpapi.com/search"
                params = {
                    'api_key': self.serpapi_key,
                    'engine': 'google_news',
                    'q': query,
                    'num': min(max_results, 100)
                }
                
                response = await self.client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    
                    # 提取标题和描述中的关键词
                    for result in data.get('news_results', [])[:max_results]:
                        title = result.get('title', '')
                        snippet = result.get('snippet', '')
                        
                        # 提取关键词
                        keywords.update(self._extract_keywords(title))
                        keywords.update(self._extract_keywords(snippet))
            
            # 使用Google Custom Search API
            elif self.google_search_key and self.google_engine_id:
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    'key': self.google_search_key,
                    'cx': self.google_engine_id,
                    'q': f"{query} news",
                    'num': min(max_results, 10)
                }
                
                response = await self.client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    
                    for item in data.get('items', []):
                        title = item.get('title', '')
                        snippet = item.get('snippet', '')
                        
                        keywords.update(self._extract_keywords(title))
                        keywords.update(self._extract_keywords(snippet))
        
        except Exception as e:
            print(f"Google News搜索错误: {e}")
        
        return list(keywords)
    
    async def search_bing_news(self, query: str, max_results: int = 50) -> List[str]:
        """从Bing News搜索并提取关键词"""
        keywords = set()
        
        try:
            if self.bing_api_key:
                url = "https://api.bing.microsoft.com/v7.0/news/search"
                headers = {'Ocp-Apim-Subscription-Key': self.bing_api_key}
                params = {
                    'q': query,
                    'count': min(max_results, 100),
                    'mkt': 'en-US'
                }
                
                response = await self.client.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    
                    for article in data.get('value', [])[:max_results]:
                        name = article.get('name', '')
                        description = article.get('description', '')
                        
                        keywords.update(self._extract_keywords(name))
                        keywords.update(self._extract_keywords(description))
        
        except Exception as e:
            print(f"Bing News搜索错误: {e}")
        
        return list(keywords)
    
    async def search_reddit(self, subreddit: str, query: str, max_results: int = 25) -> List[str]:
        """从Reddit搜索并提取关键词"""
        keywords = set()
        
        try:
            url = self.social_platforms['reddit'].format(subreddit, query)
            headers = {'User-Agent': 'KeywordOptimizer/1.0'}
            
            response = await self.client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                
                for post in data.get('data', {}).get('children', [])[:max_results]:
                    post_data = post.get('data', {})
                    title = post_data.get('title', '')
                    selftext = post_data.get('selftext', '')
                    
                    keywords.update(self._extract_keywords(title))
                    keywords.update(self._extract_keywords(selftext))
        
        except Exception as e:
            print(f"Reddit搜索错误: {e}")
        
        return list(keywords)
    
    async def search_hackernews(self, query: str, max_results: int = 25) -> List[str]:
        """从Hacker News搜索并提取关键词"""
        keywords = set()
        
        try:
            url = self.social_platforms['hackernews'].format(query)
            
            response = await self.client.get(url)
            if response.status_code == 200:
                data = response.json()
                
                for hit in data.get('hits', [])[:max_results]:
                    title = hit.get('title', '')
                    story_text = hit.get('story_text', '')
                    
                    keywords.update(self._extract_keywords(title))
                    keywords.update(self._extract_keywords(story_text))
        
        except Exception as e:
            print(f"Hacker News搜索错误: {e}")
        
        return list(keywords)
    
    async def search_twitter_trends(self, query: str) -> List[str]:
        """从Twitter趋势搜索关键词（使用公开API）"""
        keywords = set()
        
        try:
            # 使用Twitter API v2（需要Bearer Token）
            # 如果没有token，跳过
            twitter_token = os.getenv('TWITTER_BEARER_TOKEN')
            if twitter_token:
                url = "https://api.twitter.com/2/tweets/search/recent"
                headers = {'Authorization': f'Bearer {twitter_token}'}
                params = {
                    'query': f"{query} -is:retweet lang:en",
                    'max_results': 25,
                    'tweet.fields': 'text'
                }
                
                response = await self.client.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    
                    for tweet in data.get('data', []):
                        text = tweet.get('text', '')
                        keywords.update(self._extract_keywords(text))
        
        except Exception as e:
            print(f"Twitter搜索错误: {e}")
        
        return list(keywords)
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """从文本中提取关键词"""
        if not text:
            return set()
        
        keywords = set()
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 提取英文单词（2-30个字符，排除常见停用词）
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'what', 'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how',
            'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
            'very', 'can', 'will', 'just', 'don', 'should', 'now', 'the', 'is',
            'are', 'was', 'were', 'been', 'being', 'have', 'has', 'had', 'do',
            'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might'
        }
        
        # 提取英文关键词
        words = re.findall(r'\b[a-zA-Z]{2,30}\b', text.lower())
        for word in words:
            if word not in stop_words and len(word) >= 2:
                keywords.add(word)
        
        # 提取中文关键词（2-10个字符）
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,10}', text)
        for word in chinese_words:
            keywords.add(word)
        
        # 提取数字+字母组合（如5G, AI等）
        alphanumeric = re.findall(r'\b[a-zA-Z]+\d+[a-zA-Z]*\b|\b\d+[a-zA-Z]+\b', text, re.IGNORECASE)
        for word in alphanumeric:
            keywords.add(word.lower())
        
        return keywords
    
    async def optimize_category_keywords(
        self,
        category: str,
        base_keywords: List[str],
        max_new_keywords: int = 50
    ) -> Dict[str, Any]:
        """
        优化特定分类的关键词
        
        Args:
            category: 分类名称
            base_keywords: 基础关键词列表
            max_new_keywords: 最大新关键词数量
            
        Returns:
            优化结果字典
        """
        print(f"\n开始优化分类: {category}")
        print(f"基础关键词数量: {len(base_keywords)}")
        
        all_keywords = set(base_keywords)
        keyword_scores = Counter()
        
        # 对每个基础关键词进行搜索
        search_tasks = []
        for keyword in base_keywords[:10]:  # 限制搜索数量避免API限制
            search_tasks.append(self._search_all_sources(keyword))
        
        # 并行搜索
        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # 收集所有关键词
        for result in results:
            if isinstance(result, list):
                for kw in result:
                    keyword_scores[kw] += 1
                    all_keywords.add(kw)
        
        # 按频率排序，选择高频关键词
        top_keywords = [
            kw for kw, count in keyword_scores.most_common(max_new_keywords)
            if kw not in base_keywords  # 排除已有关键词
        ]
        
        return {
            'category': category,
            'original_count': len(base_keywords),
            'new_keywords': top_keywords,
            'total_count': len(all_keywords),
            'optimized_keywords': list(all_keywords)
        }
    
    async def _search_all_sources(self, query: str) -> List[str]:
        """从所有源搜索关键词"""
        all_keywords = set()
        
        # 并行搜索多个源
        tasks = [
            self.search_google_news(query, max_results=20),
            self.search_bing_news(query, max_results=20),
            self.search_hackernews(query, max_results=15),
            self.search_reddit('all', query, max_results=15)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_keywords.update(result)
        
        return list(all_keywords)
    
    async def optimize_all_categories(
        self,
        category_keywords: Dict[str, List[str]],
        max_new_per_category: int = 50
    ) -> Dict[str, Dict[str, Any]]:
        """
        优化所有分类的关键词
        
        Args:
            category_keywords: 分类关键词字典
            max_new_per_category: 每个分类最大新关键词数量
            
        Returns:
            优化结果字典
        """
        results = {}
        
        for category, keywords in category_keywords.items():
            try:
                result = await self.optimize_category_keywords(
                    category,
                    keywords,
                    max_new_per_category
                )
                results[category] = result
                
                # 避免API限制，添加延迟
                await asyncio.sleep(1)
            
            except Exception as e:
                print(f"优化分类 {category} 时出错: {e}")
                results[category] = {
                    'category': category,
                    'error': str(e),
                    'original_count': len(keywords)
                }
        
        return results
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()


async def main():
    """主函数 - 用于测试"""
    from news_searcher import NewsSearcher
    
    # 创建搜索器获取当前关键词
    searcher = NewsSearcher()
    category_keywords = searcher.CATEGORY_KEYWORDS
    
    # 创建优化器
    optimizer = KeywordOptimizer()
    
    try:
        # 优化所有分类
        print("开始优化关键词...")
        results = await optimizer.optimize_all_categories(
            category_keywords,
            max_new_per_category=30
        )
        
        # 打印结果
        print("\n优化结果:")
        print("=" * 70)
        
        for category, result in results.items():
            if 'error' not in result:
                print(f"\n分类: {category}")
                print(f"  原始关键词数: {result['original_count']}")
                print(f"  新增关键词数: {len(result['new_keywords'])}")
                print(f"  总关键词数: {result['total_count']}")
                print(f"  新增关键词示例: {result['new_keywords'][:10]}")
        
        # 保存结果到文件
        output_file = 'optimized_keywords.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n结果已保存到: {output_file}")
    
    finally:
        await optimizer.close()


if __name__ == '__main__':
    asyncio.run(main())

