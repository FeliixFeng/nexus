#!/usr/bin/env python3
"""
科技日报生成脚本
数据源：RSSHub 公共实例 + GitHub API
"""
import sys
import os
import re
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path.home() / 'projects' / 'nexus'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from blog.models import Post, Tag

# RSSHub 公共实例
RSSHUB_BASE = "https://rsshub.rssforever.com"

# RSS 源配置（可随时添加新源）
RSS_FEEDS = [
    {"name": "36氪快讯", "route": "/36kr/newsflashes", "limit": 10},
    {"name": "少数派Matrix", "route": "/sspai/matrix", "limit": 10},
    {"name": "虎嗅", "route": "/huxiu/article", "limit": 10},
    {"name": "知乎热榜", "route": "/zhihu/hot", "limit": 10},
    {"name": "Readhub日报", "route": "/readhub/daily", "limit": 10},
    {"name": "Readhub热榜", "route": "/readhub/hot", "limit": 10},
]


def fetch_rsshub(route, limit=10):
    """从 RSSHub 获取 RSS 数据"""
    url = f"{RSSHUB_BASE}{route}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Nexus-Daily-News'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            xml_data = resp.read().decode('utf-8')

        root = ET.fromstring(xml_data)
        items = root.findall('.//item')

        articles = []
        for item in items[:limit]:
            title = (item.find('title').text or '').strip()
            link = (item.find('link').text or '').strip()
            desc_elem = item.find('description')
            desc_raw = (desc_elem.text or '') if desc_elem is not None else ''

            # 清理 HTML 标签
            desc_clean = re.sub(r'<[^>]+>', '', desc_raw).strip()
            desc_clean = re.sub(r'\s+', ' ', desc_clean)[:150]

            if title:
                articles.append({
                    'title': title,
                    'url': link,
                    'snippet': desc_clean,
                })
        return articles
    except Exception as e:
        print(f"Error fetching {route}: {e}")
        return []


def fetch_github_trending(limit=8):
    """通过 GitHub API 获取近期热门新项目"""
    since = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    url = f"https://api.github.com/search/repositories?q=created:>{since}+stars:>50&sort=stars&order=desc&per_page={limit}"

    try:
        req = urllib.request.Request(url, headers={
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Nexus-Daily-News'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        repos = []
        for r in data.get('items', [])[:limit]:
            lang = r.get('language') or ''
            repos.append({
                'title': f"{r['full_name']} ⭐{r.get('stargazers_count', 0)} [{lang}]",
                'url': r.get('html_url', ''),
                'snippet': (r.get('description', '') or '')[:120],
            })
        return repos
    except Exception as e:
        print(f"GitHub API error: {e}")
        return []


def generate_daily_content():
    """生成科技日报内容"""
    today = datetime.now().strftime('%Y-%m-%d')

    # 抓取所有源
    all_articles = {}
    for feed in RSS_FEEDS:
        print(f"Fetching {feed['name']}...")
        articles = fetch_rsshub(feed['route'], feed['limit'])
        key = feed['route'].split('/')[1]
        if key not in all_articles:
            all_articles[key] = []
        all_articles[key].extend(articles)

    print("Fetching GitHub Trending...")
    all_articles['github'] = fetch_github_trending(8)

    # 构建 Markdown
    content = f"# 科技日报 {today}\n\n"
    content += f"> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"

    # 今日头条（36氪前2 + 少数派前1）
    content += "## 🔥 今日头条\n\n"
    top_news = []
    if all_articles.get('36kr'):
        top_news.extend(all_articles['36kr'][:2])
    if all_articles.get('sspai'):
        top_news.extend(all_articles['sspai'][:1])

    for i, article in enumerate(top_news[:3], 1):
        content += f"**{i}. {article['title']}**\n\n"
        if article.get('snippet'):
            content += f"{article['snippet']}\n\n"
        if article.get('url'):
            content += f"🔗 [阅读原文]({article['url']})\n\n"

    # 技术前沿（虎嗅 + 知乎热榜）
    content += "## 💻 技术前沿\n\n"
    tech_news = []
    if all_articles.get('huxiu'):
        tech_news.extend(all_articles['huxiu'][:3])
    if all_articles.get('zhihu'):
        tech_news.extend(all_articles['zhihu'][:2])

    for i, article in enumerate(tech_news[:5], 1):
        content += f"**{i}. {article['title']}**\n\n"
        if article.get('snippet'):
            content += f"{article['snippet']}\n\n"
        if article.get('url'):
            content += f"🔗 [文章]({article['url']})\n\n"

    # 科技热点（Readhub）
    content += "## 🛠️ 科技热点\n\n"
    readhub_news = []
    if all_articles.get('readhub'):
        readhub_news.extend(all_articles['readhub'][:5])

    for i, article in enumerate(readhub_news[:5], 1):
        content += f"**{i}. {article['title']}**\n\n"
        if article.get('snippet'):
            content += f"{article['snippet']}\n\n"
        if article.get('url'):
            content += f"🔗 [文章]({article['url']})\n\n"

    # GitHub 热门项目
    if all_articles.get('github'):
        content += "## 🐙 GitHub 热门项目\n\n"
        for i, article in enumerate(all_articles['github'][:5], 1):
            content += f"**{i}. {article['title']}**\n\n"
            if article.get('snippet'):
                content += f"{article['snippet']}\n\n"
            if article.get('url'):
                content += f"🔗 [项目地址]({article['url']})\n\n"

    # 一句话快讯（36氪后续 + 知乎后续）
    content += "## 📰 一句话快讯\n\n"
    quick_news = []
    if all_articles.get('36kr'):
        quick_news.extend(all_articles['36kr'][2:5])
    if all_articles.get('zhihu'):
        quick_news.extend(all_articles['zhihu'][2:5])

    for article in quick_news[:6]:
        content += f"- **{article['title']}**"
        if article.get('snippet'):
            content += f" — {article['snippet'][:40]}"
        if article.get('url'):
            content += f" [详情]({article['url']})"
        content += "\n"

    content += "\n---\n\n*数据来源：36氪、少数派、虎嗅、知乎、Readhub、GitHub Trending*\n"

    return content, top_news, all_articles.get('github', [])


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


def generate_summary(top_news, github_repos):
    """生成推送摘要"""
    today = datetime.now().strftime('%Y-%m-%d')

    summary = f"📡 科技日报 {today}\n\n"
    summary += "🔥 今日头条：\n"

    for i, article in enumerate(top_news[:3], 1):
        summary += f"{i}. {article['title']}\n"
        if article.get('url'):
            summary += f"   🔗 {article['url']}\n"

    if github_repos:
        summary += "\n🐙 GitHub 热门：\n"
        for i, repo in enumerate(github_repos[:3], 1):
            summary += f"{i}. {repo['title']}\n"
            if repo.get('url'):
                summary += f"   🔗 {repo['url']}\n"

    summary += f"\n完整版：https://felixfeng.online/blog/"

    return summary


def main():
    """主函数"""
    print(f"=== 科技日报生成 {datetime.now()} ===")

    content, top_news, github_repos = generate_daily_content()
    post = save_to_nexus(content)
    summary = generate_summary(top_news, github_repos)

    print("\n=== 推送摘要 ===")
    print(summary)

    return summary


if __name__ == '__main__':
    main()
