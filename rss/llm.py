from __future__ import annotations

import json
import re
import time
from datetime import date
from typing import Any

import requests
from django.conf import settings
from django.utils import timezone

from .models import DailyBrief, FeedItem

DOMAINS = ("ai", "security", "dev", "product", "community", "paper", "other")
THRESHOLDS = {"ai": 7, "security": 6, "dev": 8, "product": 8, "community": 8, "paper": 8, "other": 8}
ICON_BY_DOMAIN = {
    "ai": "🤖",
    "security": "🛡️",
    "dev": "📐",
    "product": "✨",
    "community": "🟧",
    "paper": "📄",
    "other": "📰",
}


class LlmError(RuntimeError):
    pass


def _cfg() -> tuple[str, str, str]:
    key = settings.LLM_API_KEY or ""
    base = (settings.LLM_BASE_URL or "https://open.bigmodel.cn/api/paas/v4").rstrip("/")
    model = settings.LLM_MODEL or "glm-4-flash"
    if not key:
        raise LlmError("LLM_API_KEY empty")
    return key, base, model


def chat(messages: list[dict[str, str]], *, temperature: float = 0.3, max_tokens: int = 2048) -> str:
    key, base, model = _cfg()
    url = f"{base}/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    delay = 1.0
    last_err: Exception | None = None
    for attempt in range(5):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=60)
        except requests.RequestException as exc:
            last_err = exc
            time.sleep(delay)
            delay = min(delay * 2, 30)
            continue

        if resp.status_code == 429:
            time.sleep(delay)
            delay = min(delay * 2, 30)
            continue
        if resp.status_code >= 400:
            raise LlmError(f"LLM HTTP {resp.status_code}: {resp.text[:300]}")

        try:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise LlmError(f"LLM bad response: {resp.text[:300]}") from exc
        return str(content)

    raise LlmError(f"LLM retries exhausted: {last_err}")


def _extract_json(text: str) -> Any:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}|\[.*\]", text, re.S)
        if not m:
            raise
        return json.loads(m.group(0))


def _body_snippet(body: str, limit: int = 1200) -> str:
    body = body or ""
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    if len(body) <= limit:
        return body
    return body[:limit] + "…"


def score_items(items: list[FeedItem]) -> int:
    if not items:
        return 0

    batch = []
    for i, obj in enumerate(items[:8]):
        batch.append(
            {
                "idx": i,
                "source": obj.source,
                "title": obj.title,
                "excerpt": _body_snippet(obj.body),
            }
        )

    system = (
        "你是个人资讯筛选助手。按领域打分并给出一句中文理由。"
        f"领域只能是: {','.join(DOMAINS)}。"
        "分数 1-10。阈值参考: ai>=7, security>=6, 其余>=8 才算重点。"
        "必须只输出 JSON 数组，不要其它文字。"
        '每项: {"idx":int,"domain":str,"score":int,"reason":str,"summary":str}。'
        "summary 为 40-60 字中文摘要。"
    )
    user = json.dumps(batch, ensure_ascii=False)

    raw = chat(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
        max_tokens=4096,
    )
    parsed = _extract_json(raw)
    if not isinstance(parsed, list):
        raise LlmError("L1 expected JSON array")

    by_idx = {}
    for row in parsed:
        if isinstance(row, dict) and "idx" in row:
            try:
                by_idx[int(row["idx"])] = row
            except (TypeError, ValueError):
                continue

    from django.utils import timezone as tz

    n = 0
    for i, obj in enumerate(items[:8]):
        row = by_idx.get(i)
        if not row:
            continue
        domain = str(row.get("domain") or "other")
        if domain not in DOMAINS:
            domain = "other"
        try:
            score = int(row.get("score") or 0)
        except (TypeError, ValueError):
            score = 0
        score = max(1, min(10, score))
        reason = str(row.get("reason") or "").strip()
        summary = str(row.get("summary") or "").strip()
        thr = THRESHOLDS.get(domain, 8)
        obj.domain = domain
        obj.icon = ICON_BY_DOMAIN.get(domain, "📰")
        obj.score = score
        obj.reason = reason
        obj.summary_short = summary
        obj.featured = score >= thr
        obj.processed_at = tz.now()
        obj.save(
            update_fields=[
                "domain",
                "icon",
                "score",
                "reason",
                "summary_short",
                "featured",
                "processed_at",
            ]
        )
        n += 1
    return n


def process_unprocessed(batch_size: int = 8) -> dict[str, int]:
    qs = FeedItem.objects.filter(processed_at__isnull=True).order_by("-published_at")
    total = qs.count()
    scored = failed = skipped = 0
    remaining = total
    while remaining > 0:
        batch = list(qs[:batch_size])
        if not batch:
            break
        try:
            scored += score_items(batch)
            remaining = max(0, remaining - len(batch))
        except LlmError:
            failed += len(batch)
            # mark processed to avoid infinite loop on poison batch; leave score null
            from django.utils import timezone as tz

            for obj in batch:
                if obj.processed_at is None:
                    obj.processed_at = tz.now()
                    obj.save(update_fields=["processed_at"])
                    skipped += 1
                    failed -= 1
            remaining = max(0, remaining - len(batch))
    return {"scored": scored, "failed": failed, "skipped": skipped}


def ensure_daily_brief(force: bool = False) -> dict[str, Any]:
    today = timezone.localdate()
    existing = DailyBrief.objects.filter(brief_date=today).first()
    if existing and not force:
        return {
            "date": today.isoformat(),
            "items": len(existing.item_ids or []),
            "action": "exists",
        }

    featured = list(
        FeedItem.objects.filter(featured=True, score__isnull=False).order_by(
            "-score", "-published_at"
        )[:8]
    )
    if not featured:
        featured = list(FeedItem.objects.order_by("-published_at")[:5])

    if not featured:
        return {"date": today.isoformat(), "items": 0, "action": "empty"}

    payload = [
        {
            "idx": i,
            "source": o.source,
            "domain": o.domain,
            "score": o.score,
            "title": o.title,
            "summary": o.summary_short or _body_snippet(o.body, 200),
            "reason": o.reason,
        }
        for i, o in enumerate(featured)
    ]

    system = (
        "你是中文科技资讯日报编辑。根据给定条目写今日日报。"
        "只输出 JSON 对象: {\"title\":str,\"lead\":str,\"body\":str,\"item_idxs\":[int,...]}。"
        "title 含日期与不超过一句主题；lead 80-120 字；body 300-500 字，2-4 段，"
        "覆盖主要线索并点名条目，不要编造条目外事实；item_idxs 为入选 idx 列表（5 条以内）。"
    )
    user = json.dumps({"date": today.isoformat(), "items": payload}, ensure_ascii=False)
    raw = chat(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.4,
        max_tokens=2048,
    )
    data = _extract_json(raw)
    if not isinstance(data, dict):
        raise LlmError("L2 expected JSON object")

    idxs = data.get("item_idxs") or data.get("items") or []
    picked: list[str] = []
    if isinstance(idxs, list):
        for x in idxs:
            try:
                i = int(x)
            except (TypeError, ValueError):
                continue
            if 0 <= i < len(featured):
                picked.append(featured[i].hub_id)
    if not picked:
        picked = [o.hub_id for o in featured[:5]]

    title = str(data.get("title") or f"{today} 资讯日报").strip()
    lead = str(data.get("lead") or "").strip()
    body = str(data.get("body") or "").strip()

    DailyBrief.objects.update_or_create(
        brief_date=today,
        defaults={
            "title": title,
            "lead": lead,
            "body": body,
            "item_ids": picked,
        },
    )
    return {"date": today.isoformat(), "items": len(picked), "action": "created"}
