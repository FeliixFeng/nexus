from django.db import models


class Link(models.Model):
    """链接"""
    CATEGORY_CHOICES = [
        ('service', '服务器服务'),
        ('external', '外部链接'),
        ('project', '个人项目'),
    ]

    name = models.CharField('名称', max_length=100)
    description = models.CharField('说明', max_length=200, blank=True)
    url = models.URLField('链接地址')
    icon = models.CharField('图标', max_length=50, blank=True, help_text='图标类名或emoji')
    category = models.CharField('分类', max_length=20, choices=CATEGORY_CHOICES, default='external')
    sort_order = models.IntegerField('排序', default=0)
    is_visible = models.BooleanField('是否显示', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '链接'
        verbose_name_plural = '链接'
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        return self.name
