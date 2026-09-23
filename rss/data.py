from __future__ import annotations

from typing import Any

from django.db import transaction
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


def has_real_data() -> bool:
    return FeedItem.objects.exists()


def featured_items() -> list[dict]:
    if has_real_data():
        qs = FeedItem.objects.filter(featured=True).order_by("-published_at")
        return [o.as_view_dict() for o in qs]
    return mock_data.featured_items()


def secondary_items() -> list[dict]:
    if has_real_data():
        qs = (
            FeedItem.objects.filter(featured=False)
            .order_by("-published_at")[:40]
        )
        return [o.as_view_dict() for o in qs]
    return mock_data.secondary_items()


def pending_items() -> list[dict]:
    if has_real_data():
        qs = FeedItem.objects.order_by("-published_at")[:80]
        rows = [o.as_view_dict() for o in qs]
        for r in rows:
            r["unread"] = True
        return rows
    return mock_data.pending_items()


def all_items_sorted() -> list[dict]:
    if has_real_data():
        qs = FeedItem.objects.order_by("-published_at")
        return [o.as_view_dict() for o in qs]
    return mock_data.all_items_sorted()


def get_item(item_id: str) -> dict | None:
    obj = FeedItem.objects.filter(hub_id=item_id).first()
    if obj is not None:
        return obj.as_view_dict()
    return mock_data.get_item(item_id)


def sources() -> list[str]:
    if has_real_data():
        seen: list[str] = []
        for val in FeedItem.objects.values_list("source", flat=True).distinct():
            if val and val not in seen:
                seen.append(val)
        return seen
    return mock_data.sources()


def domains() -> list[str]:
    if has_real_data():
        seen: list[str] = []
        for val in FeedItem.objects.values_list("domain", flat=True).distinct():
            if val and val not in seen:
                seen.append(val)
        return seen
    return mock_data.domains()


def daily_brief() -> dict | None:
    today = timezone.localdate()
    obj = DailyBrief.objects.filter(brief_date=today).first()
    if obj is None:
        # fall back to most recent brief if today missing? Prefer mock only when no real data at all
        if has_real_data():
            obj = DailyBrief.objects.order_by("-brief_date").first()
            if obj is None:
                return None
        else:
            return mock_data.daily_brief()

    pick_ids = list(obj.item_ids or [])
    items: list[dict] = []
    if pick_ids:
        rows = FeedItem.objects.filter(hub_id__in=pick_ids)
        by_id = {r.hub_id: r for r in rows}
        for hid in pick_ids:
            if hid in by_id:
                items.append(by_id[hid].as_view_dict())
    if not items:
        items = [
            o.as_view_dict()
            for o in FeedItem.objects.filter(featured=True).order_by("-published_at")[:5]
        ]
    return obj.as_view_dict(items)


def new_count() -> int:
    if has_real_data():
        return FeedItem.objects.filter(featured=True).count() or FeedItem.objects.count()
    return len(mock_data.unread_items())
