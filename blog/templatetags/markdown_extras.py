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
    """去掉Markdown语法和HTML标签，截取纯文本摘要"""
    if not text:
        return ''
    # 去除Markdown语法
    clean = str(text)
    # 去除标题标记（# ## ###等）
    clean = re.sub(r'^#{1,6}\s+', '', clean, flags=re.MULTILINE)
    # 去除表格分隔线（| --- | --- | 或 ---）
    clean = re.sub(r'\|[\s\-:]+\|[\s\-:]*\|?', '', clean)
    clean = re.sub(r'[\s]*[-]{3,}[\s]*', ' ', clean)
    # 去除表格竖线
    clean = re.sub(r'\|', ' ', clean)
    # 去除链接语法 [text](url)
    clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean)
    # 去除图片语法 ![alt](url)
    clean = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', clean)
    # 去除粗体/斜体标记
    clean = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', clean)
    clean = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', clean)
    # 去除行内代码
    clean = re.sub(r'`([^`]+)`', r'\1', clean)
    # 去除引用标记
    clean = re.sub(r'^>\s+', '', clean, flags=re.MULTILINE)
    # 去除列表标记
    clean = re.sub(r'^[\s]*[-*+]\s+', '', clean, flags=re.MULTILINE)
    clean = re.sub(r'^[\s]*\d+\.\s+', '', clean, flags=re.MULTILINE)
    # 去除HTML标签
    clean = re.sub(r'<[^>]+>', '', clean)
    # 合并多余空白
    clean = re.sub(r'\s+', ' ', clean).strip()
    if len(clean) > length:
        return clean[:length] + '...'
    return clean
