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
    
    # 将markdown转为HTML，启用常用扩展
    html = md.markdown(
        text,
        extensions=[
            'markdown.extensions.fenced_code',    # ```代码块```
            'markdown.extensions.codehilite',      # 代码高亮
            'markdown.extensions.tables',          # 表格
            'markdown.extensions.toc',             # 目录
            'markdown.extensions.nl2br',           # 换行转<br>
            'markdown.extensions.sane_lists',      # 更好的列表
            'markdown.extensions.smarty',          # 智能标点
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
