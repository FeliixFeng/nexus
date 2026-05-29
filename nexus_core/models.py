from django.db import models


class Activity(models.Model):
    """首页动态"""
    text = models.CharField('动态内容', max_length=200)
    date_label = models.CharField('日期标签', max_length=20, help_text='如 2026.05、2026.04')
    sort_order = models.IntegerField('排序', default=0)
    is_visible = models.BooleanField('是否显示', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '动态'
        verbose_name_plural = '动态'
        ordering = ['-sort_order', '-created_at']

    def __str__(self):
        return f'{self.date_label} - {self.text}'
