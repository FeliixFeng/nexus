from django.db import models


class Paper(models.Model):
    """论文卡片"""
    STATUS_CHOICES = [
        ('unread', '待读'),
        ('reading', '在读'),
        ('finished', '已读'),
        ('archived', '归档'),
    ]

    title = models.CharField('标题', max_length=500)
    authors = models.CharField('作者', max_length=500, blank=True, default='')
    doi = models.CharField('DOI', max_length=200, blank=True, default='')
    url = models.URLField('链接', blank=True, default='')
    venue = models.CharField('发表于', max_length=200, blank=True, default='')
    year = models.IntegerField('年份', null=True, blank=True)
    takeaway = models.TextField('核心贡献', blank=True, default='')
    notes = models.TextField('详细笔记 (Markdown)', blank=True, default='')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='unread')
    tags = models.CharField('标签', max_length=500, blank=True, default='',
                            help_text='逗号分隔，如：RAG,LLM,Agent')
    rating = models.IntegerField('评分 (1-5)', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '论文'
        verbose_name_plural = '论文'

    def __str__(self):
        return self.title

    def tag_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]


class Experiment(models.Model):
    """实验日志"""
    name = models.CharField('实验名称', max_length=200)
    paper = models.ForeignKey(Paper, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='experiments', verbose_name='关联论文')
    model_name = models.CharField('模型/方法', max_length=200, blank=True, default='')
    params = models.TextField('参数配置', blank=True, default='',
                              help_text='如 lr=0.001, batch=32, epochs=100')
    metrics = models.TextField('指标结果', blank=True, default='',
                               help_text='如 Accuracy=0.95, F1=0.92')
    dataset = models.CharField('数据集', max_length=200, blank=True, default='')
    notes = models.TextField('备注', blank=True, default='')
    gpu_hours = models.FloatField('GPU 小时', null=True, blank=True)
    checkpoint = models.CharField('权重路径', max_length=500, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '实验'
        verbose_name_plural = '实验'

    def __str__(self):
        return f"{self.name} ({self.created_at.strftime('%m-%d')})"
