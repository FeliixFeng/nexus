from django import template
from django.utils.safestring import mark_safe
import markdown as md
import re

register = template.Library()


@register.filter(name='markdown')
def markdown_filter(text):
    """将Markdown文本转换为HTML"""
    if not text:
        return ''

    html = md.markdown(
        text,
        extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.tables',
            'markdown.extensions.toc',
            'markdown.extensions.nl2br',
            'markdown.extensions.sane_lists',
            'markdown.extensions.smarty',
        ],
        extension_configs={
            'markdown.extensions.codehilite': {
                'css_class': 'highlight',
                'guess_lang': True,
                'linenums': False,
            }
        }
    )

    return mark_safe(html)


@register.filter(name='reading_time')
def reading_time(text):
    """估算阅读时长（中文按每分钟300字）"""
    if not text:
        return 1
    clean = re.sub(r'[#*`\[\]()>!|_\-\n\r]', '', text)
    clean = re.sub(r'\s+', '', clean)
    return max(1, round(len(clean) / 300))


@register.filter(name='striptags_truncate')
def striptags_truncate(text, length=150):
    """去掉HTML标签并截取指定长度"""
    if not text:
        return ''
    clean = re.sub(r'<[^>]+>', '', str(text))
    clean = re.sub(r'\s+', ' ', clean).strip()
    if len(clean) > length:
        return clean[:length] + '...'
    return clean
