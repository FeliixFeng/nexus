from __future__ import annotations

from django.http import Http404
from django.shortcuts import render

from nexus_core.pin_utils import is_pin_verified

from . import data, mock_data


def _base(request, active: str, title: str) -> dict:
    return {
        "is_editor": is_pin_verified(request),
        "view": active,
        "page_title": title,
        "using_live": data.has_real_data(),
    }


def today(request):
    ctx = _base(request, "today", "资讯日报")
    ctx.update(briefs=data.brief_list())
    return render(request, "rss/today.html", ctx)


def article(request, item_id: str):
    item = data.get_item(item_id)
    if item is None:
        raise Http404("article not found")
    ctx = _base(request, "", item["title"])
    ctx.update(item=item, using_live=data.has_real_data())
    return render(request, "rss/article.html", ctx)


def brief(request, day: str | None = None):
    brief_data = data.brief_detail(day)
    if brief_data is None:
        if day is not None or data.has_real_data():
            raise Http404("brief not found")
        brief_data = mock_data.daily_brief()
    ctx = _base(request, "today", brief_data["title"])
    ctx.update(brief=brief_data)
    return render(request, "rss/brief.html", ctx)


_LAB_HUB_IDS = (
    "68987cf7bfa3a97d",
    "97cbf345f3b21d9c",
    "8af43df9c184e8d8",
)


def lab(request):
    items = []
    for hid in _LAB_HUB_IDS:
        row = data.get_item(hid)
        if row is not None:
            items.append(row)
    ctx = _base(request, "lab", "打开方式试验台")
    ctx.update(items=items)
    return render(request, "rss/lab.html", ctx)
