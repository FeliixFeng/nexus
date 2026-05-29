from django.db import models


class NowItem(models.Model):
    """当前在做"""
    text = models.CharField('内容', max_length=100)
    icon = models.CharField('图标', max_length=4, default='📌')
    sort_order = models.IntegerField('排序', default=0)

    class Meta:
        verbose_name = '当前在做'
        verbose_name_plural = '当前在做'
        ordering = ['sort_order']

    def __str__(self):
        return f'{self.icon} {self.text}'


class Activity(models.Model):
    """里程碑/时间线"""
    text = models.CharField('内容', max_length=200)
    icon = models.CharField('图标', max_length=4, default='📌')
    date_label = models.CharField('日期标签', max_length=20, help_text='如 2026.05、2026.04')
    sort_order = models.IntegerField('排序', default=0)
    is_visible = models.BooleanField('是否显示', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '里程碑'
        verbose_name_plural = '里程碑'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.icon} {self.date_label} - {self.text}'
