#!/usr/bin/env python3
"""
科技日报生成脚本（国内版）
只抓取国内 RSS 源，无需翻译
"""
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path.home() / 'projects' / 'nexus'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from blog.models import Post, Tag

# 国内 RSS 源配置
RSS_FEEDS = [
    {
        "name": "36氪",
        "url": "https://36kr.com/feed",
        "limit": 8
    },
    {
        "name": "少数派",
        "url": "https://sspai.com/feed",
        "limit": 8
    },
    {
        "name": "V2EX",
        "url": "https://www.v2ex.com/feed/tab/tech.xml",
        "limit": 8
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
    """解析 RSS 输出"""
    articles = []
    lines = output.split('\n')
    
    current_article = {}
    for line in lines:
        line = line.strip()
        
        if line.startswith('### '):
            if current_article and current_article.get('title'):
                articles.append(current_article)
            current_article = {
                'title': line[4:].strip(),
                'url': '',
                'snippet': ''
            }
        elif line.startswith('URL: '):
            current_article['url'] = line[5:].strip()
        elif line.startswith('<p>') and current_article:
            import re
            text = re.sub(r'<[^>]+>', '', line)
            if text and not current_article.get('snippet'):
                current_article['snippet'] = text[:100]
    
    if current_article and current_article.get('title'):
        articles.append(current_article)
    
    return articles

def generate_daily_content():
    """生成科技日报内容"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    all_articles = {
        '36kr': [],
        'sspai': [],
        'v2ex': []
    }
    
    for feed_config in RSS_FEEDS:
        print(f"Fetching {feed_config['name']}...")
        output = fetch_rss(feed_config['url'], feed_config['limit'])
        
        if output:
            articles = parse_rss_output(output)
            
            if '36氪' in feed_config['name']:
                all_articles['36kr'] = articles[:8]
            elif '少数派' in feed_config['name']:
                all_articles['sspai'] = articles[:8]
            elif 'V2EX' in feed_config['name']:
                all_articles['v2ex'] = articles[:8]
    
    content = f"# 科技日报 {today}\n\n"
    content += f"> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    # 今日头条
    content += "## 🔥 今日头条\n\n"
    top_news = []
    if all_articles['36kr']:
        top_news.extend(all_articles['36kr'][:2])
    if all_articles['sspai']:
        top_news.extend(all_articles['sspai'][:1])
    
    for i, article in enumerate(top_news[:3], 1):
        content += f"**{i}. {article['title']}**\n\n"
        if article.get('snippet'):
            content += f"{article['snippet']}\n\n"
        if article.get('url'):
            content += f"🔗 [阅读原文]({article['url']})\n\n"
    
    # 技术前沿
    content += "## 💻 技术前沿\n\n"
    tech_news = []
    if all_articles['36kr']:
        tech_news.extend(all_articles['36kr'][2:5])
    if all_articles['v2ex']:
        tech_news.extend(all_articles['v2ex'][:3])
    
    for i, article in enumerate(tech_news[:5], 1):
        content += f"**{i}. {article['title']}**\n\n"
        if article.get('snippet'):
            content += f"{article['snippet']}\n\n"
        if article.get('url'):
            content += f"🔗 [文章]({article['url']})\n\n"
    
    # 效率工具
    content += "## 🛠️ 效率工具\n\n"
    tools_news = []
    if all_articles['sspai']:
        tools_news.extend(all_articles['sspai'][1:4])
    
    for i, article in enumerate(tools_news[:3], 1):
        content += f"**{i}. {article['title']}**\n\n"
        if article.get('snippet'):
            content += f"{article['snippet']}\n\n"
        if article.get('url'):
            content += f"🔗 [文章]({article['url']})\n\n"
    
    # 一句话快讯
    content += "## 📰 一句话快讯\n\n"
    quick_news = []
    if all_articles['36kr']:
        quick_news.extend(all_articles['36kr'][5:8])
    if all_articles['v2ex']:
        quick_news.extend(all_articles['v2ex'][3:6])
    
    for article in quick_news[:6]:
        content += f"- **{article['title']}**"
        if article.get('snippet'):
            content += f" — {article['snippet'][:30]}"
        if article.get('url'):
            content += f" [详情]({article['url']})"
        content += "\n"
    
    content += f"\n---\n\n*数据来源：36氪、少数派、V2EX*\n"
    
    return content, top_news

def save_to_nexus(content):
    """保存到 Nexus 笔记"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    existing = Post.objects.filter(
        title=f'科技日报 {today}',
        tags__name='科技日报'
    ).first()
    
    if existing:
        existing.content = content
        existing.summary = f'科技日报 {today}'
        existing.save()
        print(f"Updated existing daily: {existing.id}")
        return existing
    else:
        post = Post.objects.create(
            title=f'科技日报 {today}',
            content=content,
            summary=f'科技日报 {today}',
            status='published',
        )
        
        tag, _ = Tag.objects.get_or_create(name='科技日报')
        post.tags.add(tag)
        
        for tag_name in ['科技', '新闻']:
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
    print(f"=== 科技日报生成（国内版）{datetime.now()} ===")
    
    content, top_news = generate_daily_content()
    post = save_to_nexus(content)
    summary = generate_summary(top_news)
    
    print("\n=== 推送摘要 ===")
    print(summary)
    
    return summary

if __name__ == '__main__':
    main()
