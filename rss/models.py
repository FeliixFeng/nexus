from __future__ import annotations

from django.db import models


class FeedItem(models.Model):
    hub_id = models.CharField(max_length=64, unique=True, db_index=True)
    source = models.CharField(max_length=64, db_index=True)
    title = models.TextField()
    url = models.URLField(max_length=1024)
    body = models.TextField(blank=True)
    domain = models.CharField(max_length=32, blank=True, db_index=True)
    icon = models.CharField(max_length=8, blank=True)
    score = models.IntegerField(null=True, blank=True, db_index=True)
    reason = models.TextField(blank=True)
    summary_short = models.TextField(blank=True)
    featured = models.BooleanField(default=False, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    fetched_at = models.DateTimeField(null=True, blank=True)
    pulled_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-published_at", "-fetched_at"]

    def as_view_dict(self) -> dict:
        return {
            "id": self.hub_id,
            "source": self.source,
            "domain": self.domain or "dev",
            "icon": self.icon or "📰",
            "title": self.title,
            "url": self.url,
            "score": self.score if self.score is not None else "-",
            "reason": self.reason or self.summary_short or "",
            "published_at": self.iso_published(),
            "fetched_at": self.iso_fetched(),
            "body": self.body,
            "featured": self.featured,
            "unread": True,
        }

    def iso_published(self) -> str:
        if not self.published_at:
            return ""
        return self.published_at.isoformat().replace("+00:00", "Z")

    def iso_fetched(self) -> str:
        if not self.fetched_at:
            return ""
        return self.fetched_at.isoformat().replace("+00:00", "Z")


class DailyBrief(models.Model):
    brief_date = models.DateField(unique=True, db_index=True)
    title = models.CharField(max_length=200)
    lead = models.TextField(blank=True)
    body = models.TextField(blank=True)
    item_ids = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def as_view_dict(self, items: list[dict]) -> dict:
        return {
            "id": f"brief-{self.brief_date.isoformat()}",
            "type": "brief",
            "date": self.brief_date.isoformat(),
            "title": self.title,
            "lead": self.lead,
            "body": self.body,
            "items": items,
            "unread": True,
        }


class PullCursor(models.Model):
    name = models.CharField(max_length=64, primary_key=True)
    since = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_since(cls, name: str = "hub_items"):
        obj, _ = cls.objects.get_or_create(name=name)
        return obj
