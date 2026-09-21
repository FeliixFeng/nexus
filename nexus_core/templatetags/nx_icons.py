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
    """走本站 /icon/ 代理；取不到时前端回退 emoji。"""
    try:
        host = urlparse(url or '').netloc
    except Exception:
        host = ''
    if not host:
        return ''
    return f'/icon/?host={host}'
