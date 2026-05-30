#!/usr/bin/env python3
"""
科技日报生成脚本
每天早上抓取 RSS，生成笔记，推送简要版本
"""
import sys
import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path.home() / 'projects' / 'nexus'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from blog.models import Post, Tag

# RSS 源配置
RSS_FEEDS = [
    {
        "name": "Hacker News",
        "url": "https://hnrss.org/frontpage",
        "limit": 10
    },
    {
        "name": "The Verge",
        "url": "https://www.theverge.com/rss/index.xml",
        "limit": 8
    },
    {
        "name": "Ars Technica",
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "limit": 8
    },
    {
        "name": "GitHub Trending",
        "url": "https://mshibanami.github.io/GitHubTrendingRSS/daily/all.xml",
        "limit": 10
    },
]

def fetch_rss(url, limit=10):
    """抓取 RSS 源"""
    try:
        result = subprocess.run(
            ['node', str(Path.home() / '.hermes' / 'skills' / 'research' / 'rss-reader' / 'scripts' / 'fetch-rss.mjs'),
             url, '--limit', str(limit)],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Error fetching {url}: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception fetching {url}: {e}")
        return None

def parse_rss_output(output):
    """解析 RSS 输出，提取文章信息"""
    articles = []
    lines = output.split('\n')
    
    current_article = {}
    for line in lines:
        line = line.strip()
        
        # 新文章标题
        if line.startswith('### '):
            if current_article and current_article.get('title'):
                articles.append(current_article)
            current_article = {
                'title': line[4:].strip(),
                'url': '',
                'snippet': ''
            }
        
        # URL
        elif line.startswith('URL: '):
            current_article['url'] = line[5:].strip()
        
        # 作者和日期
        elif line.startswith('Author: ') or line.startswith('Date: '):
            pass
        
        # 内容摘要（HTML 格式）
        elif line.startswith('<p>') and current_article:
            # 提取纯文本
            import re
            text = re.sub(r'<[^>]+>', '', line)
            if text and not current_article.get('snippet'):
                current_article['snippet'] = text[:200]
    
    # 添加最后一篇文章
    if current_article and current_article.get('title'):
        articles.append(current_article)
    
    return articles

def generate_daily_content():
    """生成科技日报内容"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 收集所有文章
    all_articles = {
        'hn': [],
        'verge': [],
        'ars': [],
        'github': []
    }
    
    for feed_config in RSS_FEEDS:
        print(f"Fetching {feed_config['name']}...")
        output = fetch_rss(feed_config['url'], feed_config['limit'])
        
        if output:
            articles = parse_rss_output(output)
            
            if 'Hacker News' in feed_config['name']:
                all_articles['hn'] = articles[:10]
            elif 'The Verge' in feed_config['name']:
                all_articles['verge'] = articles[:8]
            elif 'Ars Technica' in feed_config['name']:
                all_articles['ars'] = articles[:8]
            elif 'GitHub Trending' in feed_config['name']:
                all_articles['github'] = articles[:10]
    
    # 生成 Markdown 内容
    content = f"# 科技日报 {today}\n\n"
    content += f"> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    # 今日头条（取前 3 条重要新闻）
    content += "## 🔥 今日头条\n\n"
    top_news = []
    if all_articles['hn']:
        top_news.extend(all_articles['hn'][:2])
    if all_articles['verge']:
        top_news.extend(all_articles['verge'][:1])
    
    for i, article in enumerate(top_news[:3], 1):
        content += f"**{i}. {article['title']}**\n\n"
        if article.get('snippet'):
            content += f"{article['snippet']}\n\n"
        if article.get('url'):
            content += f"🔗 [阅读原文]({article['url']})\n\n"
    
    # 技术前沿
    content += "## 💻 技术前沿\n\n"
    tech_news = []
    if all_articles['hn']:
        tech_news.extend(all_articles['hn'][2:7])
    
    for i, article in enumerate(tech_news[:5], 1):
        content += f"**{i}. {article['title']}**\n\n"
        if article.get('snippet'):
            content += f"{article['snippet']}\n\n"
        if article.get('url'):
            content += f"🔗 [文章]({article['url']})\n\n"
    
    # GitHub Trending
    content += "## 🛠️ GitHub Trending 热门项目\n\n"
    for i, article in enumerate(all_articles['github'][:5], 1):
        content += f"**{i}. {article['title']}** ⭐\n\n"
        if article.get('snippet'):
            content += f"{article['snippet']}\n\n"
        if article.get('url'):
            content += f"🔗 [GitHub]({article['url']})\n\n"
    
    # 一句话快讯
    content += "## 📰 一句话快讯\n\n"
    quick_news = []
    if all_articles['verge']:
        quick_news.extend(all_articles['verge'][1:4])
    if all_articles['ars']:
        quick_news.extend(all_articles['ars'][:3])
    
    for article in quick_news[:6]:
        content += f"- **{article['title']}**"
        if article.get('snippet'):
            content += f" — {article['snippet'][:50]}"
        if article.get('url'):
            content += f" [详情]({article['url']})"
        content += "\n"
    
    content += f"\n---\n\n*数据来源：Hacker News、The Verge、Ars Technica、GitHub Trending*\n"
    
    return content, top_news

def save_to_nexus(content):
    """保存到 Nexus 笔记"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 检查是否已存在今天的日报
    existing = Post.objects.filter(
        title=f'科技日报 {today}',
        tags__name='科技日报'
    ).first()
    
    if existing:
        # 更新现有笔记
        existing.content = content
        existing.summary = f'科技日报 {today}'
        existing.save()
        print(f"Updated existing daily: {existing.id}")
        return existing
    else:
        # 创建新笔记
        post = Post.objects.create(
            title=f'科技日报 {today}',
            content=content,
            summary=f'科技日报 {today}',
            status='published',
        )
        
        # 添加标签
        tag, _ = Tag.objects.get_or_create(name='科技日报')
        post.tags.add(tag)
        
        # 添加其他标签
        for tag_name in ['AI', '技术', '新闻']:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            post.tags.add(tag)
        
        print(f"Created new daily: {post.id}")
        return post

def generate_summary(top_news):
    """生成推送摘要"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    summary = f"📡 科技日报 {today}\n\n"
    summary += "🔥 今日头条：\n"
    
    for i, article in enumerate(top_news[:3], 1):
        summary += f"{i}. {article['title']}\n"
        if article.get('url'):
            summary += f"   🔗 {article['url']}\n"
    
    summary += f"\n完整版：https://felixfeng.online/blog/"
    
    return summary

def main():
    """主函数"""
    print(f"=== 科技日报生成 {datetime.now()} ===")
    
    # 生成内容
    content, top_news = generate_daily_content()
    
    # 保存到 Nexus
    post = save_to_nexus(content)
    
    # 生成摘要
    summary = generate_summary(top_news)
    
    print("\n=== 推送摘要 ===")
    print(summary)
    
    # 返回摘要供外部使用
    return summary

if __name__ == '__main__':
    main()
