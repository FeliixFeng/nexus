#!/usr/bin/env python3
"""
RSS 新闻抓取 + AI 总结脚本
每天早上抓取科技新闻，总结后推送并同步到 Nexus 笔记
"""
import feedparser
import json
from datetime import datetime, timedelta
from pathlib import Path

# RSS 源配置（选择国内可访问且速度较快的源）
RSS_FEEDS = [
    {
        "name": "Hacker News",
        "url": "https://hnrss.org/frontpage",
        "category": "技术前沿"
    },
    {
        "name": "V2EX",
        "url": "https://www.v2ex.com/feed/tab/tech.xml",
        "category": "技术社区"
    },
    {
        "name": "GitHub Trending",
        "url": "https://mshibanami.github.io/GitHubTrendingRSS/daily/all.xml",
        "category": "开源项目"
    },
]

def fetch_feeds():
    """抓取所有 RSS 源"""
    articles = []
    
    for feed_config in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_config["url"])
            
            for entry in feed.entries[:5]:  # 每个源取前5篇
                # 解析发布时间
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])
                
                # 只要最近24小时的文章
                if published and (datetime.now() - published) > timedelta(hours=24):
                    continue
                
                articles.append({
                    "source": feed_config["name"],
                    "category": feed_config["category"],
                    "title": entry.get("title", "").strip(),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:200].strip(),
                    "published": published.strftime("%Y-%m-%d %H:%M") if published else "未知",
                })
        except Exception as e:
            print(f"Error fetching {feed_config['name']}: {e}")
            continue
    
    return articles

def format_for_ai(articles):
    """格式化文章列表供 AI 总结"""
    if not articles:
        return "今日暂无科技新闻"
    
    lines = []
    for i, art in enumerate(articles[:15], 1):  # 最多15篇
        lines.append(f"{i}. [{art['source']}] {art['title']}")
        if art['summary']:
            # 清理 HTML
            import re
            clean_summary = re.sub(r'<[^>]+>', '', art['summary'])[:100]
            lines.append(f"   {clean_summary}")
        lines.append(f"   链接: {art['link']}")
        lines.append("")
    
    return "\n".join(lines)

def generate_note_content(articles, summary):
    """生成笔记内容（Markdown）"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    content = f"""# 科技日报 {today}

> 自动生成于 {datetime.now().strftime("%Y-%m-%d %H:%M")}

## 今日摘要

{summary}

## 详细新闻

"""
    for art in articles:
        content += f"### {art['title']}\n"
        content += f"- 来源: {art['source']} ({art['category']})\n"
        content += f"- 时间: {art['published']}\n"
        if art['summary']:
            import re
            clean_summary = re.sub(r'<[^>]+>', '', art['summary'])
            content += f"- 摘要: {clean_summary}\n"
        content += f"- 链接: [{art['title']}]({art['link']})\n\n"
    
    content += "---\n\n*由 Nexus RSS 自动抓取*\n"
    
    return content

if __name__ == "__main__":
    print("=== RSS News Fetcher ===")
    print(f"Time: {datetime.now()}")
    
    # 抓取文章
    articles = fetch_feeds()
    print(f"Fetched {len(articles)} articles")
    
    # 格式化
    formatted = format_for_ai(articles)
    print("\n--- Articles ---")
    print(formatted)
    
    # 保存原始数据
    output_file = Path.home() / "projects" / "nexus" / "scripts" / "rss_articles.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {output_file}")
