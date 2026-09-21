from django import template
from urllib.parse import urlparse

register = template.Library()


@register.filter
def host_of(url):
    try:
        return urlparse(url or '').netloc
    except Exception:
        return ''


@register.filter
def favicon_url(url):
    """按域名取站点图标；失败时前端回退 emoji。"""
    host = (url or '').split('//')[-1].split('/')[0]
    if not host:
        return ''
    return f'https://icons.duckduckgo.com/ip3/{host}.ico'
