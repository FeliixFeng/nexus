from __future__ import annotations

from datetime import date

from django.http import Http404
from django.shortcuts import render

from nexus_core.pin_utils import is_pin_verified

from . import mock_data


def _base(request, active: str, title: str) -> dict:
    return {
        "is_editor": is_pin_verified(request),
        "view": active,
        "page_title": title,
        "today_label": date.today().isoformat(),
        "new_count": len(mock_data.unread_items()),
    }


def today(request):
    ctx = _base(request, "today", "精选")
    ctx.update(
        brief=mock_data.daily_brief(),
        featured=mock_data.featured_items(),
        secondary=mock_data.secondary_items(),
    )
    return render(request, "rss/today.html", ctx)


def unread(request):
    ctx = _base(request, "unread", "待读")
    ctx.update(items=mock_data.pending_items())
    return render(request, "rss/unread.html", ctx)


def stream(request):
    ctx = _base(request, "stream", "全部")
    ctx.update(
        items=mock_data.all_items_sorted(),
        sources=mock_data.sources(),
        domains=mock_data.domains(),
    )
    return render(request, "rss/stream.html", ctx)


def article(request, item_id: str):
    item = mock_data.get_item(item_id)
    if item is None:
        raise Http404("article not found")
    ctx = _base(request, "", item["title"])
    ctx.update(item=item)
    return render(request, "rss/article.html", ctx)


def brief(request):
    ctx = _base(request, "brief", "资讯日报")
    ctx.update(brief=mock_data.daily_brief())
    return render(request, "rss/brief.html", ctx)
