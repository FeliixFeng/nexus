from django import template

register = template.Library()


@register.filter
def split_body(value: str):
    if not value:
        return []
    return [p.strip() for p in value.split("\n\n") if p.strip()]
