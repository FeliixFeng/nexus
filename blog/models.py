from django.db import models


class Tag(models.Model):
    """标签"""
    name = models.CharField('标签名', max_length=50, unique=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['name']

    def __str__(self):
        return self.name


class Post(models.Model):
    """文章"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
        ('hidden', '隐藏'),
    ]

    title = models.CharField('标题', max_length=200)
    slug = models.SlugField('URL别名', max_length=200, unique=True, blank=True)
    content = models.TextField('内容', help_text='Markdown格式')
    summary = models.TextField('摘要', blank=True, max_length=500)
    cover_image = models.ImageField('封面图', upload_to='blog/covers/', blank=True)
    tags = models.ManyToManyField(Tag, verbose_name='标签', blank=True)
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='draft')
    is_pinned = models.BooleanField('置顶', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    published_at = models.DateTimeField('发布时间', null=True, blank=True)

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-is_pinned', '-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            self.slug = slugify(self.title) or str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)
