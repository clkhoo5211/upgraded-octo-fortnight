"""
新闻归档调度器模块
提供定时任务配置信息
"""
from typing import List, Dict, Any
from datetime import datetime


class NewsScheduler:
    """新闻调度器类"""
    
    def __init__(self):
        """初始化调度器"""
        pass
    
    def schedule_daily_news_archive(
        self,
        cron_expression: str = "0 1 * * *",
        categories: List[str] = None,
        languages: str = "all"
    ) -> Dict[str, Any]:
        """
        创建每日新闻归档任务配置
        
        Args:
            cron_expression: cron表达式 (默认每日凌晨1点)
            categories: 要归档的分类
            languages: 要归档的语言
            
        Returns:
            调度任务配置信息
        """
        if categories is None:
            categories = ['politics', 'finance', 'crypto', 'blockchain', 
                         'fengshui', 'tech', 'social', 'international']
        
        # 解析cron表达式
        cron_parts = cron_expression.split()
        
        if len(cron_parts) != 5:
            cron_expression = "0 1 * * *"  # 默认值
        
        # 生成配置
        config = {
            'schedule_type': 'daily_archive',
            'cron_expression': cron_expression,
            'cron_description': self._describe_cron(cron_expression),
            'categories': categories,
            'languages': languages,
            'next_run': self._calculate_next_run(cron_expression),
            'created_at': datetime.now().isoformat(),
            
            # GitHub Actions配置
            'github_actions_workflow': self._generate_github_actions_workflow(
                cron_expression, categories, languages
            ),
            
            # Vercel Cron配置
            'vercel_cron_config': self._generate_vercel_cron_config(
                cron_expression
            ),
            
            # 手动执行脚本
            'manual_script': self._generate_manual_script(categories, languages)
        }
        
        return config
    
    def _describe_cron(self, cron_expression: str) -> str:
        """描述cron表达式"""
        parts = cron_expression.split()
        
        if len(parts) != 5:
            return "无效的cron表达式"
        
        minute, hour, day, month, weekday = parts
        
        # 简单的描述生成
        desc_parts = []
        
        if minute == "0" and hour != "*":
            desc_parts.append(f"每天{hour}点整")
        elif hour == "*":
            desc_parts.append("每小时")
        else:
            desc_parts.append(f"每天{hour}:{minute}")
        
        return ''.join(desc_parts)
    
    def _calculate_next_run(self, cron_expression: str) -> str:
        """计算下次运行时间（简化版本）"""
        # 这里只是示例，实际应该使用croniter库
        parts = cron_expression.split()
        
        if len(parts) != 5:
            return "未知"
        
        minute, hour, day, month, weekday = parts
        
        now = datetime.now()
        
        # 简单处理：如果是每日任务
        if day == "*" and month == "*" and weekday == "*":
            try:
                target_hour = int(hour) if hour != "*" else now.hour
                target_minute = int(minute) if minute != "*" else 0
                
                next_run = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
                
                # 如果时间已过，加一天
                if next_run <= now:
                    from datetime import timedelta
                    next_run += timedelta(days=1)
                
                return next_run.isoformat()
            except:
                pass
        
        return "未知"
    
    def _generate_github_actions_workflow(
        self,
        cron_expression: str,
        categories: List[str],
        languages: str
    ) -> str:
        """生成GitHub Actions工作流配置"""
        workflow = f"""name: Daily News Archive

on:
  schedule:
    - cron: '{cron_expression}'
  workflow_dispatch:  # 允许手动触发

jobs:
  archive-news:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install uv
        run: pip install uv
      
      - name: Install dependencies
        run: |
          cd global-news-mcp
          uv sync
      
      - name: Archive yesterday's news
        env:
          GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
          NEWSAPI_KEY: ${{{{ secrets.NEWSAPI_KEY }}}}
          NEWSDATA_KEY: ${{{{ secrets.NEWSDATA_KEY }}}}
        run: |
          cd global-news-mcp
          uv run python -c "
import asyncio
from src.news_tools import NewsSearcher, GitHubArchiver
from datetime import datetime, timedelta

async def main():
    # 搜索昨日新闻
    searcher = NewsSearcher()
    news = await searcher.search_news(
        categories={categories},
        languages='{languages}',
        date_range='yesterday',
        max_results=100
    )
    await searcher.close()
    
    # 归档到GitHub
    archiver = GitHubArchiver(github_token='${{{{ secrets.GITHUB_TOKEN }}}}')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    result = archiver.classify_and_save_news(news, target_date=yesterday)
    
    print(f'归档完成: {{result}}')

asyncio.run(main())
          "
"""
        
        return workflow
    
    def _generate_vercel_cron_config(self, cron_expression: str) -> Dict[str, Any]:
        """生成Vercel Cron配置"""
        return {
            "crons": [
                {
                    "path": "/api/archive-news",
                    "schedule": cron_expression
                }
            ]
        }
    
    def _generate_manual_script(self, categories: List[str], languages: str) -> str:
        """生成手动执行脚本"""
        script = f"""#!/bin/bash
# 手动执行新闻归档脚本

set -e

echo "开始归档昨日新闻..."

cd "$(dirname "$0")"

# 确保环境变量已设置
if [ -z "$GITHUB_TOKEN" ]; then
    echo "错误: GITHUB_TOKEN 环境变量未设置"
    exit 1
fi

# 执行归档
uv run python -c "
import asyncio
from src.news_tools import NewsSearcher, GitHubArchiver
from datetime import datetime, timedelta

async def main():
    print('正在搜索昨日新闻...')
    searcher = NewsSearcher()
    news = await searcher.search_news(
        categories={categories},
        languages='{languages}',
        date_range='yesterday',
        max_results=100
    )
    await searcher.close()
    
    print(f'找到 {{len(news)}} 条新闻')
    
    print('正在归档到GitHub...')
    archiver = GitHubArchiver(github_token='$GITHUB_TOKEN')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    result = archiver.classify_and_save_news(news, target_date=yesterday)
    
    if result['success']:
        print(f'✓ 归档成功!')
        print(f'  保存文件: {{result[\"saved_files\"]}}')
        print(f'  总新闻数: {{result[\"total_news\"]}}')
    else:
        print(f'✗ 归档失败!')
        print(f'  错误: {{result[\"errors\"]}}')
        exit(1)

asyncio.run(main())
"

echo "归档完成!"
"""
        
        return script
