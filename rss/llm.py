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

DOMAIN_LABELS = {
    "ai": "AI",
    "security": "安全",
    "dev": "开发",
    "product": "产品",
    "community": "社区",
    "paper": "论文",
    "other": "其他",
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


_MD_LINK_RE = re.compile(r"\]\((https?://[^)\s]+)\)")
_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")


def _linkify_titles(body: str, items: list[FeedItem]) -> str:
    """模型常把 **[标题](url)** 写成 **标题**：按标题反查条目回填链接。"""
    for span in _BOLD_RE.findall(body):
        if "](" in span:
            continue
        match = next((o for o in items if o.title == span), None)
        if match is None and len(span) >= 20:
            cands = [o for o in items if o.title.startswith(span)]
            if len(cands) == 1:
                match = cands[0]
        if match is not None:
            body = body.replace(
                f"**{span}**", f"**[{match.title}]({match.url})**", 1
            )
    return body


def _complete_coverage(body: str, items: list[FeedItem]) -> str:
    """模型常漏写条目：把 body 里没有链接的条目按领域补回对应分组。"""
    have = set(_MD_LINK_RE.findall(body))
    missing = [o for o in items if o.url not in have]
    if not missing:
        return body

    sections: list[tuple[str | None, list[str]]] = []
    header: str | None = None
    buf: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            sections.append((header, buf))
            header, buf = line[3:].strip(), []
        else:
            buf.append(line)
    sections.append((header, buf))

    for o in missing:
        label = DOMAIN_LABELS.get(o.domain or "other", "其他")
        entry = f"- **[{o.title}]({o.url})** — {o.source}"
        for h, sec_buf in sections:
            if h == label:
                sec_buf.append(entry)
                break
        else:
            sections.append((label, [entry]))

    out: list[str] = []
    for h, sec_buf in sections:
        if h is not None:
            out.append(f"## {h}")
        out.extend(sec_buf)
    return "\n".join(out).strip()


def _parse_brief_markdown(raw: str, items: list[FeedItem], today: date) -> dict[str, Any]:
    """把模型输出的日报 Markdown 拆成 title/lead/body，并按链接反查覆盖的条目。"""
    text = raw.strip()
    text = re.sub(r"^```(?:markdown|md)?\s*\n", "", text)
    text = re.sub(r"\n```\s*$", "", text).strip()
    lines = text.splitlines()

    title = f"{today.isoformat()} 资讯日报"
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith("# "):
            title = line[2:].strip() or title
            body_start = i + 1
            break
    else:
        raise LlmError("brief missing '#' title line")

    lead_lines: list[str] = []
    j = body_start
    while j < len(lines) and lines[j].startswith(">"):
        lead_lines.append(lines[j].lstrip("> ").strip())
        j += 1
    body = "\n".join(lines[j:]).strip()
    if not body:
        raise LlmError("brief body empty")

    body = _linkify_titles(body, items)
    body = _complete_coverage(body, items)
    urls = set(_MD_LINK_RE.findall(body))
    used = [o.hub_id for o in items if o.url in urls] or [o.hub_id for o in items]
    return {"title": title, "lead": " ".join(lead_lines).strip(), "body": body, "used": used}


def _body_snippet(body: str, limit: int = 1200) -> str:
    body = body or ""
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    if len(body) <= limit:
        return body
    return body[:limit] + "…"


def _item_payload(obj: FeedItem, idx: int, *, with_excerpt: bool = True) -> dict[str, Any]:
    data: dict[str, Any] = {
        "idx": idx,
        "source": obj.source,
        "domain": obj.domain or "other",
        "title": obj.title,
        "url": obj.url,
    }
    if with_excerpt:
        data["excerpt"] = _body_snippet(obj.body, 400)
    return data


_SYSTEM_PROMPT = (
    "你是中文科技资讯日报编辑。根据给定条目写一份中文日报，直接输出 Markdown 正文，"
    "不要代码围栏、不要 JSON、不要任何前言或解释。\n"
    "结构必须严格如下:\n"
    "# 含日期的标题，加一句当日主题（不超过12字）\n"
    "> 80-120字总起，概括今天最重要的2-3条线索\n"
    "## 领域中文名\n"
    "**[条目标题](条目url)** — 40-60字中文热点说明\n"
    "（同领域条目连续排列，再起下一个 ## 分组）\n"
    "要求:\n"
    "- 领域名用给定 domain 的中文名（AI/安全/开发/产品/社区/论文/其他）\n"
    "- 必须覆盖全部给定条目（完全重复的合并为一条），不得遗漏；"
    "条目多于40条时说明压缩到20-30字\n"
    "- 链接必须原样使用给定 url，标题原样使用给定 title，不得编造条目外事实"
)


def _fallback_brief(items: list[FeedItem], today: date) -> dict[str, str]:
    """LLM 不可用时的降级：纯标题分组列表，保证日报不断档。"""
    lines: list[str] = []
    by_domain: dict[str, list[FeedItem]] = {}
    for obj in items:
        by_domain.setdefault(obj.domain or "other", []).append(obj)
    for domain, objs in by_domain.items():
        lines.append(f"## {DOMAIN_LABELS.get(domain, domain)}")
        for o in objs:
            lines.append(f"- **[{o.title}]({o.url})** — {o.source}")
        lines.append("")
    return {
        "title": f"{today.isoformat()} 资讯日报",
        "lead": "",
        "body": "\n".join(lines).strip(),
    }


def generate_daily_brief(items: list[FeedItem], *, force: bool = False) -> dict[str, Any]:
    """一次 LLM 调用把当天条目综合成日报。items 为空且已有日报时返回 exists。"""
    today = timezone.localdate()
    existing = DailyBrief.objects.filter(brief_date=today).first()
    if existing and not force:
        return {
            "date": today.isoformat(),
            "items": len(existing.item_ids or []),
            "action": "exists",
        }
    if not items:
        return {"date": today.isoformat(), "items": 0, "action": "empty"}

    # 智谱 1301 内容过滤常被正文 excerpt 触发：先带 excerpt，被拦则去 excerpt 重试一次
    brief: dict[str, Any] | None = None
    last_err: Exception | None = None
    for with_excerpt in (True, False):
        payload = [_item_payload(o, i, with_excerpt=with_excerpt) for i, o in enumerate(items)]
        user = json.dumps({"date": today.isoformat(), "items": payload}, ensure_ascii=False)
        try:
            raw = chat(
                [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user},
                ],
                temperature=0.4,
                max_tokens=4096,
            )
            brief = _parse_brief_markdown(raw, items, today)
            break
        except (LlmError, ValueError, TypeError) as exc:
            last_err = exc
            continue

    if brief is not None:
        title, lead, body, used = brief["title"], brief["lead"], brief["body"], brief["used"]
        degraded = False
    else:
        fb = _fallback_brief(items, today)
        title, lead, body = fb["title"], fb["lead"], fb["body"]
        used = [o.hub_id for o in items]
        degraded = True
        print(f"brief degraded: {type(last_err).__name__}: {last_err}")

    DailyBrief.objects.update_or_create(
        brief_date=today,
        defaults={"title": title, "lead": lead, "body": body, "item_ids": used},
    )
    return {
        "date": today.isoformat(),
        "items": len(used),
        "action": "created",
        "degraded": degraded,
    }
