from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from . import mock_data
from .hub_client import fetch_items, parse_hub_time
from .models import DailyBrief, FeedItem, PullCursor

SOURCE_ICONS = {
    "量子位": "🤖",
    "Hacker News": "🟧",
    "InfoQ": "📐",
    "少数派": "✨",
    "阮一峰的网络日志": "📖",
    "阮一峰的网络日志": "📖",
    "GitHub Blog": "🐙",
    "GitHub": "🐙",
}

SOURCE_DOMAINS = {
    "量子位": "ai",
    "Hacker News": "community",
    "InfoQ": "dev",
    "少数派": "product",
    "阮一峰的网络日志": "dev",
    "GitHub Blog": "dev",
    "GitHub": "dev",
}

# 每源每日入库上限（中文源无热度参数，入口限额兜底；未列出的源不限）
SOURCE_DAILY_LIMITS = {
    "InfoQ": 3,
    "量子位": 3,
    "少数派": 2,
}

ITEM_RETENTION_DAYS = 7


def _icon_for(source: str) -> str:
    if source in SOURCE_ICONS:
        return SOURCE_ICONS[source]
    return "📰"


def _domain_for(source: str) -> str:
    return SOURCE_DOMAINS.get(source, "dev")


def upsert_item(raw: dict[str, Any]) -> tuple[FeedItem, str]:
    hub_id = str(raw.get("id") or "").strip()
    if not hub_id:
        raise ValueError("hub item missing id")

    title = str(raw.get("title") or "").strip()
    url = str(raw.get("url") or "").strip()
    source = str(raw.get("source") or "unknown").strip()
    body = str(raw.get("summary") or raw.get("body") or "")
    published = parse_hub_time(raw.get("published_at"))
    fetched = parse_hub_time(raw.get("fetched_at"))

    defaults = {
        "source": source,
        "title": title,
        "url": url,
        "body": body,
        "domain": _domain_for(source),
        "icon": _icon_for(source),
        "published_at": published,
        "fetched_at": fetched,
    }

    obj, created = FeedItem.objects.update_or_create(
        hub_id=hub_id,
        defaults=defaults,
    )
    return obj, "created" if created else "updated"


def pull_items(limit: int = 50, reset_cursor: bool = False) -> dict[str, Any]:
    cursor = PullCursor.get_since("hub_items")
    if reset_cursor:
        cursor.since = None
        cursor.save(update_fields=["since", "updated_at"])

    since = cursor.since
    result = fetch_items(since=since, limit=limit)
    items = result["items"]

    created = updated = 0
    newest = since
    with transaction.atomic():
        for raw in items:
            _, action = upsert_item(raw)
            if action == "created":
                created += 1
            else:
                updated += 1
            pub = parse_hub_time(raw.get("published_at")) or parse_hub_time(raw.get("fetched_at"))
            if pub and (newest is None or pub > newest):
                newest = pub

        # advance cursor only after successful upserts
        advance_to = result.get("server_time") or newest
        if advance_to and (cursor.since is None or advance_to > cursor.since):
            cursor.since = advance_to
            cursor.save(update_fields=["since", "updated_at"])

    return {
        "fetched": result["count"],
        "created": created,
        "updated": updated,
        "since": cursor.since.isoformat() if cursor.since else "",
    }


def apply_source_limits(today: Any = None) -> dict[str, int]:
    if today is None:
        today = timezone.localdate()
    trimmed: dict[str, int] = {}
    for source, cap in SOURCE_DAILY_LIMITS.items():
        qs = FeedItem.objects.filter(source=source, pulled_at__date=today)
        keep = list(qs.order_by("-published_at", "-fetched_at").values_list("id", flat=True)[:cap])
        drop = qs.exclude(id__in=keep)
        n, _ = drop.delete()
        if n:
            trimmed[source] = n
    return trimmed


def purge_old_items(days: int = ITEM_RETENTION_DAYS) -> int:
    cutoff = timezone.now() - timedelta(days=days)
    n, _ = FeedItem.objects.filter(pulled_at__lt=cutoff).delete()
    return n


def items_for_brief(hours: int = 24, cap: int = 40) -> list[FeedItem]:
    since = timezone.now() - timedelta(hours=hours)
    fresh = FeedItem.objects.filter(
        Q(published_at__gte=since) | Q(published_at__isnull=True, pulled_at__gte=since)
    )
    return list(fresh.order_by("-published_at")[:cap])


def has_real_data() -> bool:
    return FeedItem.objects.exists()


def get_item(item_id: str) -> dict | None:
    obj = FeedItem.objects.filter(hub_id=item_id).first()
    if obj is not None:
        return obj.as_view_dict()
    return mock_data.get_item(item_id)


def _brief_row(obj: DailyBrief, resolve_items: bool) -> dict:
    items: list[dict] = []
    if resolve_items and obj.item_ids:
        rows = FeedItem.objects.filter(hub_id__in=obj.item_ids)
        by_id = {r.hub_id: r for r in rows}
        items = [by_id[hid] for hid in obj.item_ids if hid in by_id]
        items = [o.as_view_dict() for o in items]
    return obj.as_view_dict(items)


def brief_list(limit: int = 30) -> list[dict]:
    if not has_real_data():
        return [mock_data.daily_brief()]
    qs = DailyBrief.objects.order_by("-brief_date")[:limit]
    return [_brief_row(o, resolve_items=False) for o in qs]


def brief_detail(day: str | None = None) -> dict | None:
    if not has_real_data():
        return mock_data.daily_brief()
    qs = DailyBrief.objects.all()
    if day:
        qs = qs.filter(brief_date=day)
    obj = qs.order_by("-brief_date").first()
    if obj is None:
        return None
    return _brief_row(obj, resolve_items=True)


def new_count() -> int:
    if has_real_data():
        today = timezone.localdate()
        return FeedItem.objects.filter(pulled_at__date=today).count()
    return len(mock_data.unread_items())
