"""
GitHub归档模块
负责新闻分类、格式化和提交到GitHub
"""
import os
from github import Github, GithubException
from typing import List, Dict, Any
from datetime import datetime
import base64


class GitHubArchiver:
    """GitHub归档器类"""
    
    def __init__(self, github_token: str, repo_name: str = "clkhoo5211/upgraded-octo-fortnight"):
        """
        初始化GitHub归档器
        
        Args:
            github_token: GitHub Personal Access Token
            repo_name: GitHub仓库名称 (owner/repo)
        """
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.repo_name = repo_name
        
        if not self.github_token:
            raise ValueError("GitHub Token未提供")
        
        self.github = Github(self.github_token)
        self.repo = self.github.get_repo(self.repo_name)
    
    def classify_and_save_news(
        self,
        news_data: List[Dict[str, Any]],
        save_format: str = 'md_with_html',
        target_date: str = None
    ) -> Dict[str, Any]:
        """
        分类并保存新闻到GitHub
        
        Args:
            news_data: 新闻数据列表
            save_format: 保存格式 (md_with_html/md_with_xml)
            target_date: 目标日期 (YYYY-MM-DD)，默认为今天
            
        Returns:
            保存结果
        """
        # 使用目标日期或当前日期
        if target_date:
            date_obj = datetime.strptime(target_date, '%Y-%m-%d')
        else:
            date_obj = datetime.now()
        
        year = date_obj.strftime('%Y')
        month = date_obj.strftime('%m')
        day = date_obj.strftime('%d')
        
        # 按分类组织新闻
        categorized_news = self._categorize_news(news_data)
        
        # 生成文件
        saved_files = []
        errors = []
        
        for category, news_list in categorized_news.items():
            if not news_list:
                continue
            
            # 生成文件路径
            file_path = f"{year}/{month}/{day}/{category}.md"
            
            # 生成文件内容
            content = self._generate_markdown(
                news_list,
                category,
                date_obj,
                save_format
            )
            
            # 保存到GitHub
            try:
                self._save_to_github(file_path, content, date_obj)
                saved_files.append(file_path)
            except Exception as e:
                errors.append({
                    'file': file_path,
                    'error': str(e)
                })
        
        return {
            'success': len(errors) == 0,
            'saved_files': saved_files,
            'errors': errors,
            'total_news': len(news_data),
            'date': f"{year}-{month}-{day}"
        }
    
    def _categorize_news(self, news_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """按分类组织新闻"""
        # 动态获取所有分类（包括自定义分类）
        from .category_manager import CategoryManager
        category_manager = CategoryManager()
        all_categories = category_manager.get_all_categories()
        
        # 初始化分类字典
        categories = {cat: [] for cat in all_categories.keys()}
        # 添加默认的social分类作为兜底
        if 'social' not in categories:
            categories['social'] = []
        
        for news in news_data:
            category = news.get('category', 'social')
            if category in categories:
                categories[category].append(news)
            else:
                # 未知分类归入social
                categories['social'].append(news)
        
        return categories
    
    def _generate_markdown(
        self,
        news_list: List[Dict[str, Any]],
        category: str,
        date_obj: datetime,
        save_format: str
    ) -> str:
        """生成Markdown内容"""
        # 分类名称映射（默认映射）
        default_category_names = {
            'politics': '政治',
            'finance': '财经',
            'crypto': '加密货币',
            'blockchain': '区块链',
            'fengshui': '风水',
            'tech': '科技',
            'social': '社会',
            'international': '国际'
        }
        
        # 如果分类不在默认映射中，使用分类名称本身
        category_name = default_category_names.get(category, category.replace('_', ' ').title())
        date_str = date_obj.strftime('%Y年%m月%d日')
        
        lines = [
            f"# {category_name}新闻 - {date_str}",
            "",
            f"**归档日期：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**新闻数量：** {len(news_list)}条  ",
            f"**分类：** {category_name}",
            "",
            "---",
            ""
        ]
        
        # 添加每条新闻
        for i, news in enumerate(news_list, 1):
            lines.extend(self._format_news_item(news, i, save_format))
        
        return '\n'.join(lines)
    
    def _format_news_item(
        self,
        news: Dict[str, Any],
        index: int,
        save_format: str
    ) -> List[str]:
        """格式化单条新闻"""
        lines = [
            f"## {index}. {news.get('title', '无标题')}",
            "",
            f"**来源：** {news.get('source', '未知')}  ",
            f"**时间：** {news.get('published_at', '未知')}  ",
            f"**分类：** {news.get('category', '未分类')}  ",
            f"**语言：** {news.get('language', '未知')}  ",
            ""
        ]
        
        # 摘要
        if news.get('description'):
            lines.extend([
                "### 摘要",
                "",
                news['description'],
                ""
            ])
        
        # 正文
        if news.get('content'):
            lines.extend([
                "### 正文",
                "",
                news['content'],
                ""
            ])
        
        # 图片
        if news.get('images') or news.get('image_url'):
            lines.append("### 相关图片")
            lines.append("")
            
            images = news.get('images', [])
            if news.get('image_url') and news['image_url'] not in images:
                images.insert(0, news['image_url'])
            
            for img_url in images[:5]:  # 最多5张图片
                lines.append(f"![图片]({img_url})")
            
            lines.append("")
        
        # 视频
        if news.get('videos'):
            lines.append("### 相关视频")
            lines.append("")
            
            for video in news.get('videos', [])[:3]:  # 最多3个视频
                video_url = video.get('url', '') if isinstance(video, dict) else video
                video_type = video.get('type', 'unknown') if isinstance(video, dict) else 'unknown'
                lines.append(f"- **{video_type.upper()}视频**: [{video_url}]({video_url})")
            
            lines.append("")
        
        # HTML Body（如果存在）
        if news.get('html_body'):
            lines.extend([
                "### HTML原始内容",
                "",
                "```html",
                news['html_body'][:5000],  # 限制长度避免文件过大
                "```",
                "",
                f"*（完整HTML内容已保存，长度: {len(news['html_body'])} 字符）*",
                ""
            ])
        
        # HTML格式
        if save_format == 'md_with_html':
            lines.extend(self._generate_html_block(news))
        
        # XML格式
        if save_format == 'md_with_xml':
            lines.extend(self._generate_xml_block(news))
        
        # 原文链接
        if news.get('url'):
            lines.extend([
                f"**原文链接：** [{news['url']}]({news['url']})",
                ""
            ])
        
        lines.extend([
            "---",
            ""
        ])
        
        return lines
    
    def _generate_html_block(self, news: Dict[str, Any]) -> List[str]:
        """生成HTML代码块"""
        html = f"""<article class="news-article">
    <header>
        <h1>{self._escape_html(news.get('title', ''))}</h1>
        <div class="meta">
            <span class="source">{self._escape_html(news.get('source', ''))}</span>
            <time datetime="{news.get('published_at', '')}">{news.get('published_at', '')}</time>
        </div>
    </header>
    <section class="summary">
        <p>{self._escape_html(news.get('description', ''))}</p>
    </section>
    <section class="content">
        {self._html_paragraphs(news.get('content', ''))}
    </section>
    {self._html_images(news.get('images', []) or [news.get('image_url', '')])}
    <footer>
        <a href="{news.get('url', '')}" target="_blank">阅读原文</a>
    </footer>
</article>"""
        
        return [
            "### HTML格式",
            "",
            "```html",
            html,
            "```",
            ""
        ]
    
    def _generate_xml_block(self, news: Dict[str, Any]) -> List[str]:
        """生成XML代码块"""
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<news>
    <title>{self._escape_xml(news.get('title', ''))}</title>
    <source>{self._escape_xml(news.get('source', ''))}</source>
    <published_at>{news.get('published_at', '')}</published_at>
    <category>{news.get('category', '')}</category>
    <language>{news.get('language', '')}</language>
    <description>{self._escape_xml(news.get('description', ''))}</description>
    <content>{self._escape_xml(news.get('content', ''))}</content>
    <url>{news.get('url', '')}</url>
    {self._xml_images(news.get('images', []) or [news.get('image_url', '')])}
</news>"""
        
        return [
            "### XML格式",
            "",
            "```xml",
            xml,
            "```",
            ""
        ]
    
    def _escape_html(self, text: str) -> str:
        """转义HTML特殊字符"""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))
    
    def _escape_xml(self, text: str) -> str:
        """转义XML特殊字符"""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&apos;'))
    
    def _html_paragraphs(self, content: str) -> str:
        """将文本转换为HTML段落"""
        if not content:
            return ""
        
        paragraphs = content.split('\n\n')
        html_parts = []
        for p in paragraphs:
            if p.strip():
                html_parts.append(f"        <p>{self._escape_html(p.strip())}</p>")
        
        return '\n'.join(html_parts)
    
    def _html_images(self, images: List[str]) -> str:
        """生成HTML图片标签"""
        if not images or not any(images):
            return ""
        
        img_tags = []
        for img_url in images:
            if img_url:
                img_tags.append(f'        <img src="{img_url}" alt="新闻图片" />')
        
        if img_tags:
            return f"\n    <div class=\"images\">\n" + '\n'.join(img_tags) + "\n    </div>"
        
        return ""
    
    def _xml_images(self, images: List[str]) -> str:
        """生成XML图片标签"""
        if not images or not any(images):
            return ""
        
        xml_parts = ["    <images>"]
        for img_url in images:
            if img_url:
                xml_parts.append(f"        <image>{img_url}</image>")
        xml_parts.append("    </images>")
        
        return '\n'.join(xml_parts)
    
    def _save_to_github(self, file_path: str, content: str, date_obj: datetime):
        """保存文件到GitHub"""
        commit_message = f"chore: archive news for {date_obj.strftime('%Y-%m-%d')}"
        
        try:
            # 尝试获取现有文件
            try:
                existing_file = self.repo.get_contents(file_path)
                # 更新现有文件
                self.repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    sha=existing_file.sha
                )
            except GithubException as e:
                if e.status == 404:
                    # 文件不存在，创建新文件
                    self.repo.create_file(
                        path=file_path,
                        message=commit_message,
                        content=content
                    )
                else:
                    raise
                    
        except Exception as e:
            raise Exception(f"保存到GitHub失败: {str(e)}")
