import re

import bleach
import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_MD_EXTS = [
    "fenced_code",
    "codehilite",
    "tables",
    "sane_lists",
    "nl2br",
]

_ALLOWED_TAGS = [
    "p", "br", "hr",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li",
    "blockquote",
    "pre", "code", "span", "div",
    "strong", "em", "b", "i", "del",
    "a", "img",
    "table", "thead", "tbody", "tr", "th", "td",
]
_ALLOWED_ATTRS = {
    "a": ["href", "title", "rel", "target"],
    "img": ["src", "alt", "title"],
    "code": ["class"],
    "pre": ["class"],
    "div": ["class"],
    "span": ["class"],
    "th": ["align"],
    "td": ["align"],
}
_ALLOWED_PROTOCOLS = ["http", "https", "mailto"]

_SENT_END = tuple("。！？…；;!?．.")
_HEADING_MAX = 24
_CODE_FENCE = "```"
_CAPTION_RE = re.compile(r"[（(]来源[：:]")
_LIST_RE = re.compile(r"^(?:[-*+]|\d+[.)])\s+")
_MD_HEADING_RE = re.compile(r"^#{1,6}\s+")
_MD_STRONG_RE = re.compile(r"\*\*[^*]+\*\*")
_MD_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")


def _looks_markdown(text: str) -> bool:
    if text.count(_CODE_FENCE) >= 2:
        return True
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return False
    heading_hits = sum(1 for ln in lines if _MD_HEADING_RE.match(ln))
    if heading_hits >= 2:
        return True
    list_hits = sum(1 for ln in lines if _LIST_RE.match(ln))
    if list_hits >= 4:
        return True
    if _MD_LINK_RE.search(text) and heading_hits + list_hits >= 1:
        return True
    if re.search(r"^>\s+\S", text, re.M) and text.count("\n\n") >= 2:
        return True
    return False


def _is_caption(line: str) -> bool:
    return bool(_CAPTION_RE.search(line)) and len(line) <= 60


def _is_heading(line: str) -> bool:
    if _MD_HEADING_RE.match(line):
        return False
    if _LIST_RE.match(line) or line.startswith(_CODE_FENCE):
        return False
    if len(line) > _HEADING_MAX:
        return False
    if line[-1] in _SENT_END:
        return False
    if re.search(r"[A-Za-z0-9]", line) and len(line) > 18:
        return False
    return True


def _is_list(line: str) -> bool:
    return bool(_LIST_RE.match(line))


def _is_codeish(text: str) -> bool:
    if _CODE_FENCE in text:
        return True
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if len(lines) < 3:
        return False
    code_hints = 0
    for ln in lines:
        s = ln.strip()
        if s.startswith(("# ", "#!", "import ", "from ", "def ", "class ", "const ", "function ", "var ", "$ ", "// ", "#/")):
            code_hints += 1
        elif s.startswith("#") and not s.startswith("# "):
            if re.match(r"^#\s*(///|!|\w+)", s) or s.endswith("=") or '"' in s or "'" in s:
                code_hints += 1
    return code_hints >= 3


def _md_to_html(text: str) -> str:
    raw = md.markdown(
        text,
        extensions=_MD_EXTS,
        extension_configs={
            "codehilite": {"css_class": "highlight", "guess_lang": True, "linenums": False},
        },
    )
    return bleach.clean(
        raw,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRS,
        protocols=_ALLOWED_PROTOCOLS,
        strip=True,
    )


def _join_lines(lines: list[str]) -> str:
    out = ""
    for ln in lines:
        if not out:
            out = ln
            continue
        if out[-1] in _SENT_END or out[-1].isascii():
            if ln[0].isascii() or out[-1].isascii():
                out = out.rstrip() + " " + ln.lstrip()
            else:
                out = out.rstrip() + ln.lstrip()
        elif ln[0].isascii() and out[-1].isascii():
            out = out + " " + ln
        else:
            out = out + ln
    return out.strip()


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _plain_to_html(text: str) -> str:
    chunks: list[str] = []
    paragraphs = re.split(r"\n\s*\n", text)
    for para in paragraphs:
        lines = [ln.strip() for ln in para.splitlines() if ln.strip()]
        if not lines:
            continue

        if _is_codeish("\n".join(lines)) and any(_CODE_FENCE in ln for ln in lines):
            chunks.append(_md_to_html("\n".join(lines)))
            continue

        buf: list[str] = []

        def flush() -> None:
            nonlocal buf
            if buf:
                joined = _join_lines(buf)
                if joined:
                    chunks.append(f"<p>{_escape(joined)}</p>")
                buf = []

        for i, line in enumerate(lines):
            if line.startswith(_CODE_FENCE):
                flush()
                rest = "\n".join(lines[i:])
                chunks.append(_md_to_html(rest))
                return "".join(chunks)
            if _is_caption(line):
                flush()
                chunks.append(f'<p class="feed-caption">{_escape(line)}</p>')
                continue
            if _is_list(line):
                flush()
                list_lines = [line]
                for nxt in lines[i + 1 :]:
                    if _is_list(nxt):
                        list_lines.append(nxt)
                    else:
                        break
                items = "".join(f"<li>{_escape(_LIST_RE.sub('', ln))}</li>" for ln in list_lines)
                chunks.append(f"<ul>{items}</ul>")
                continue
            if _is_heading(line):
                flush()
                if _MD_HEADING_RE.match(line):
                    content = _MD_HEADING_RE.sub("", line)
                    level = min(6, len(line) - len(line.lstrip("#")) or 3)
                else:
                    content = line
                    level = 3
                chunks.append(f"<h{level}>{_escape(content.strip())}</h{level}>")
                continue

            if buf and _is_heading(buf[-1]) is False:
                prev = buf[-1]
                if prev[-1] in _SENT_END and len(_join_lines(buf)) >= 40:
                    flush()
            buf.append(line)

        flush()

    if not chunks and text.strip():
        chunks.append(f"<p>{_escape(text.strip())}</p>")
    return "".join(chunks)


@register.filter
def render_body(value: str):
    if not value:
        return ""
    text = value.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        return ""
    html = _md_to_html(text) if _looks_markdown(text) else _plain_to_html(text)
    return mark_safe(html)


@register.filter
def split_body(value: str):
    if not value:
        return []
    parts = re.split(r"\n\s*\n|\n", value)
    return [p.strip() for p in parts if p.strip()]


@register.filter
def is_caption(value: str) -> bool:
    return bool(value) and _is_caption(value)
