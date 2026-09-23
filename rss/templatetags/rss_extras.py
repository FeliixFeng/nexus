import re

from django import template

register = template.Library()


@register.filter
def split_body(value: str):
    if not value:
        return []
    parts = re.split(r"\n\s*\n|\n", value)
    return [p.strip() for p in parts if p.strip()]


@register.filter
def is_caption(value: str) -> bool:
    return bool(value) and ("（来源：" in value or "(来源：" in value)
