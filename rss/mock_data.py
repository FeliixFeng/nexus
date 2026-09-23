from __future__ import annotations

from datetime import date
from typing import Any

LONG_BODY = """这是一篇用于本地界面联调的示例正文，用来检验阅读页排版、行宽和中英混排。

背景：rss-hub 已在 lunar 上按小时抓取 6 个信源，抽取网页全文后写入 SQLite，并只保留长度不低于 500 字的条目。下游阅读器负责按游标增量拉取、本地去重，再交给模型筛选与日报生成。

当前阶段只搭界面：数据全部来自本地 mock，不请求 HUB_URL，也不调用大模型。等配置与数据链路就绪后，再接入打分与日报文案。

阅读体验上，正文区建议控制在约 65–75 个字符宽度，段落间距略松，标题层级清楚；顶栏固定导航：首页 · 链接 · 状态 · 资讯 · 其他。源名与领域标签只作辅助信息，不应抢正文的注意力。

去重约定：同一篇文章以内容地址哈希作为 id，重复拉取只更新内容、不产生第二行。游标使用服务端时间，本地失败时不推进游标。

保留策略：上游只留三十天滚动窗口；阅读器若要长期归档，需要自己落库。展示层可以只显示摘要卡片，点进文章页再读全文。

下一步：接真数据 → 模型打分筛选 → 日报成稿 → 反馈标记。界面先按「每天只看几条」设计，避免做成无限信息流。
"""

_ITEMS: list[dict[str, Any]] = [
    {
        "id": "a1qbitai00000001",
        "source": "量子位",
        "domain": "ai",
        "icon": "🤖",
        "title": "开源模型再提速：小参数量在端侧推理上的新平衡",
        "url": "https://www.qbitai.com/",
        "score": 9,
        "reason": "和毕设端侧部署直接相关，有可复现的数据。",
        "published_at": "2026-09-23T08:00:00Z",
        "fetched_at": "2026-09-23T06:00:00Z",
        "body": LONG_BODY,
        "featured": True,
        "unread": True,
    },
    {
        "id": "a2hn000000000002",
        "source": "Hacker News",
        "domain": "community",
        "icon": "🟧",
        "title": "Show HN: A tiny pipeline that turns RSS into a daily brief",
        "url": "https://news.ycombinator.com/",
        "score": 8,
        "reason": "和我们在做的日报形态高度同构，可对照实现取舍。",
        "published_at": "2026-09-23T07:30:00Z",
        "fetched_at": "2026-09-23T06:00:00Z",
        "body": LONG_BODY,
        "featured": True,
        "unread": True,
    },
    {
        "id": "a3infoq0000000003",
        "source": "InfoQ",
        "domain": "dev",
        "icon": "📐",
        "title": "从抓取到阅读：个人知识管道的边界该画在哪里",
        "url": "https://www.infoq.cn/",
        "score": 8,
        "reason": "讲清上游聚合与下游筛选分工，面试可当案例讲。",
        "published_at": "2026-09-23T06:00:00Z",
        "fetched_at": "2026-09-23T06:00:00Z",
        "body": LONG_BODY,
        "featured": True,
        "unread": True,
    },
    {
        "id": "a4sspai0000000004",
        "source": "少数派",
        "domain": "product",
        "icon": "✨",
        "title": "如何为「每天只看十条」设计信息入口",
        "url": "https://sspai.com/",
        "score": 7,
        "reason": "产品视角的信息降噪，和日报阈值设计可互相印证。",
        "published_at": "2026-09-22T22:00:00Z",
        "fetched_at": "2026-09-23T06:00:00Z",
        "body": LONG_BODY,
        "featured": True,
        "unread": True,
    },
    {
        "id": "a5ruanyifeng0005",
        "source": "阮一峰的网络日志",
        "domain": "dev",
        "icon": "📖",
        "title": "科技爱好者周刊（第 00 期）：工具的克制",
        "url": "https://www.ruanyifeng.com/blog/",
        "score": 7,
        "reason": "周刊节奏稳，适合当低噪声基线源。",
        "published_at": "2026-09-22T12:00:00Z",
        "fetched_at": "2026-09-23T06:00:00Z",
        "body": LONG_BODY,
        "featured": True,
        "unread": True,
    },
    {
        "id": "a6githubblog00006",
        "source": "GitHub Blog",
        "domain": "dev",
        "icon": "🐙",
        "title": "How we structure monorepo CI for parallel checks",
        "url": "https://github.blog/",
        "score": 6,
        "reason": "工程实践，可作稍后翻翻，不进今日重点。",
        "published_at": "2026-09-22T18:00:00Z",
        "fetched_at": "2026-09-23T06:00:00Z",
        "body": LONG_BODY,
        "featured": False,
        "unread": True,
    },
    {
        "id": "a7hn000000000007",
        "source": "Hacker News",
        "domain": "community",
        "icon": "🟧",
        "title": "Ask HN: What does your personal RSS setup look like in 2026?",
        "url": "https://news.ycombinator.com/newest",
        "score": 6,
        "reason": "同行配置对照，收集过滤与保留策略灵感。",
        "published_at": "2026-09-23T05:00:00Z",
        "fetched_at": "2026-09-23T06:00:00Z",
        "body": LONG_BODY,
        "featured": False,
        "unread": True,
    },
    {
        "id": "a8qbitai00000008",
        "source": "量子位",
        "domain": "ai",
        "icon": "🤖",
        "title": "一周 AI 开源项目速览：检索增强的轻量实现",
        "url": "https://www.qbitai.com/",
        "score": 6,
        "reason": "综述素材；是否深读取决于是否含可复现 baseline。",
        "published_at": "2026-09-23T04:00:00Z",
        "fetched_at": "2026-09-23T06:00:00Z",
        "body": LONG_BODY,
        "featured": False,
        "unread": True,
    },
    {
        "id": "a9sspai0000000009",
        "source": "少数派",
        "domain": "product",
        "icon": "✨",
        "title": "效率工具周报：本地优先笔记的同步取舍",
        "url": "https://sspai.com/tag/%E6%95%88%E7%8E%87",
        "score": 5,
        "reason": "工具向，有空再看。",
        "published_at": "2026-09-21T10:00:00Z",
        "fetched_at": "2026-09-23T06:00:00Z",
        "body": LONG_BODY,
        "featured": False,
        "unread": False,
    },
    {
        "id": "a10infoq0000000010",
        "source": "InfoQ",
        "domain": "dev",
        "icon": "📐",
        "title": "数据库选型清单：什么时候 SQLite 仍然够用",
        "url": "https://www.infoq.cn/topic/Database",
        "score": 7,
        "reason": "和 hub / reader 存储边界直接相关。",
        "published_at": "2026-09-21T08:00:00Z",
        "fetched_at": "2026-09-23T06:00:00Z",
        "body": LONG_BODY,
        "featured": False,
        "unread": False,
    },
    {
        "id": "a11githubblog00011",
        "source": "GitHub Blog",
        "domain": "dev",
        "icon": "🐙",
        "title": "Security updates for Actions runners",
        "url": "https://github.blog/category/security/",
        "score": 4,
        "reason": "公告类，优先级低。",
        "published_at": "2026-09-20T16:00:00Z",
        "fetched_at": "2026-09-23T06:00:00Z",
        "body": LONG_BODY,
        "featured": False,
        "unread": False,
    },
    {
        "id": "a12ruanyifeng0012",
        "source": "阮一峰的网络日志",
        "domain": "dev",
        "icon": "📖",
        "title": "Python 异步编程的常见误区",
        "url": "https://www.ruanyifeng.com/blog/atom.xml",
        "score": 5,
        "reason": "基础巩固，非紧急。",
        "published_at": "2026-09-19T12:00:00Z",
        "fetched_at": "2026-09-23T06:00:00Z",
        "body": LONG_BODY,
        "featured": False,
        "unread": False,
    },
]


def all_items() -> list[dict[str, Any]]:
    return list(_ITEMS)


def featured_items() -> list[dict[str, Any]]:
    return [i for i in _ITEMS if i.get("featured")]


def secondary_items() -> list[dict[str, Any]]:
    return [i for i in _ITEMS if not i.get("featured") and i.get("unread")]


def unread_items() -> list[dict[str, Any]]:
    return [i for i in _ITEMS if i.get("unread")]


def pending_items() -> list[dict[str, Any]]:
    today = date.today().isoformat()
    unread: list[dict[str, Any]] = []
    read_today: list[dict[str, Any]] = []
    for i in _ITEMS:
        day = (i.get("published_at") or "")[:10]
        if i.get("unread"):
            unread.append(i)
        elif day == today:
            read_today.append(i)
    unread.sort(key=lambda i: i.get("published_at") or "", reverse=True)
    read_today.sort(key=lambda i: i.get("published_at") or "", reverse=True)
    return unread + read_today


def all_items_sorted() -> list[dict[str, Any]]:
    return sorted(
        _ITEMS,
        key=lambda i: i.get("published_at") or "",
        reverse=True,
    )


def get_item(item_id: str) -> dict[str, Any] | None:
    for i in _ITEMS:
        if i["id"] == item_id:
            return i
    return None


def sources() -> list[str]:
    seen: list[str] = []
    for i in _ITEMS:
        if i["source"] not in seen:
            seen.append(i["source"])
    return seen


def domains() -> list[str]:
    seen: list[str] = []
    for i in _ITEMS:
        if i["domain"] not in seen:
            seen.append(i["domain"])
    return seen


_BRIEF_ITEM_IDS = [
    "a1qbitai00000001",
    "a2hn000000000002",
    "a3infoq0000000003",
    "a4sspai0000000004",
    "a10infoq0000000010",
]

_BRIEF_BODY = """今天没有爆炸性新闻，整体偏「工程与产品」：端侧推理怎么权衡参数量，RSS 到日报的流水线怎么切边界，以及个人知识管道里抓取和筛选该分开到什么程度。

端侧侧重点在轻量模型：小参数量在推理速度和精度之间重新找了平衡，若毕设要落端侧部署，这条值得对着实验数据看一遍。RSS→日报那条和我们正在做的形态几乎同构，适合对照取舍：上游只做抓取和全文抽取，下游才碰打分与成稿。

知识管道边界、SQLite 是否仍然够用，两篇都在回答同一个问题——数据留在哪一层。结论不必全信，但和 hub / reader 的分工可以互相印证。

下面五条为今日精选，点标题进入系统内详情（算已读）；全文与原文链接在详情页。"""

def daily_brief() -> dict[str, Any]:
    picks = [i for iid in _BRIEF_ITEM_IDS if (i := get_item(iid))]
    return {
        "id": "brief-2026-09-23",
        "type": "brief",
        "date": "2026-09-23",
        "title": "2026-09-23 资讯日报",
        "lead": "今天信息管道偏「工程与产品」：端侧推理、RSS→日报同构实现、知识管道边界，以及 SQLite 够不够用。5 条重点已标出，点进即算已读。",
        "body": _BRIEF_BODY,
        "items": picks,
        "unread": True,
    }
