from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

import requests
from django.conf import settings


class HubError(RuntimeError):
    pass


def _iso_z(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_hub_time(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.strip()
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except (TypeError, ValueError):
        pass
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None


def fetch_items(since: datetime | None = None, limit: int = 50) -> dict[str, Any]:
    base = (settings.RSS_HUB_URL or "").rstrip("/")
    if not base:
        raise HubError("RSS_HUB_URL is empty")
    if not settings.RSS_API_KEY:
        raise HubError("RSS_API_KEY is empty")

    params: dict[str, Any] = {"limit": limit}
    if since is not None:
        params["since"] = _iso_z(since)

    try:
        resp = requests.get(
            f"{base}/api/v1/items",
            params=params,
            headers={"X-API-Key": settings.RSS_API_KEY},
            timeout=30,
        )
    except requests.RequestException as exc:
        raise HubError(f"hub request failed: {exc}") from exc

    if resp.status_code == 401:
        raise HubError("hub 401: bad RSS_API_KEY")
    if resp.status_code >= 400:
        raise HubError(f"hub HTTP {resp.status_code}: {resp.text[:200]}")

    try:
        data = resp.json()
    except ValueError as exc:
        raise HubError(f"hub non-JSON response: {resp.text[:200]}") from exc

    if not data.get("ok", False):
        raise HubError(f"hub not ok: {data}")

    items = data.get("items") or []
    if not isinstance(items, list):
        raise HubError("hub items is not a list")

    return {
        "items": items,
        "count": int(data.get("count") or len(items)),
        "server_time": parse_hub_time(data.get("server_time")),
    }


def health() -> dict[str, Any]:
    base = (settings.RSS_HUB_URL or "").rstrip("/")
    if not base:
        return {"ok": False, "error": "RSS_HUB_URL is empty"}
    try:
        resp = requests.get(f"{base}/health", timeout=10)
        data = resp.json()
        return {"ok": bool(data.get("ok")), **data}
    except (requests.RequestException, ValueError) as exc:
        return {"ok": False, "error": str(exc)}
