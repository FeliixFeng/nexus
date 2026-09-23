from __future__ import annotations

from datetime import date

from django.http import Http404
from django.shortcuts import render

from nexus_core.pin_utils import is_pin_verified

from . import data, mock_data


def _base(request, active: str, title: str) -> dict:
    return {
        "is_editor": is_pin_verified(request),
        "view": active,
        "page_title": title,
        "today_label": date.today().isoformat(),
        "new_count": data.new_count(),
        "using_live": data.has_real_data(),
    }


def today(request):
    ctx = _base(request, "today", "精选")
    ctx.update(
        brief=data.daily_brief(),
        featured=data.featured_items(),
        secondary=data.secondary_items(),
    )
    return render(request, "rss/today.html", ctx)


def unread(request):
    ctx = _base(request, "unread", "待读")
    ctx.update(items=data.pending_items())
    return render(request, "rss/unread.html", ctx)


def stream(request):
    ctx = _base(request, "stream", "全部")
    ctx.update(
        items=data.all_items_sorted(),
        sources=data.sources(),
        domains=data.domains(),
    )
    return render(request, "rss/stream.html", ctx)


def article(request, item_id: str):
    item = data.get_item(item_id)
    if item is None:
        raise Http404("article not found")
    ctx = _base(request, "", item["title"])
    ctx.update(item=item, using_live=data.has_real_data())
    return render(request, "rss/article.html", ctx)


def brief(request):
    ctx = _base(request, "brief", "资讯日报")
    brief_data = data.daily_brief()
    if brief_data is None and data.has_real_data():
        raise Http404("brief not found")
    ctx.update(brief=brief_data or mock_data.daily_brief())
    return render(request, "rss/brief.html", ctx)
