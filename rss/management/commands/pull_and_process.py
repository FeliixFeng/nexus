from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from rss import data as pull
from rss.hub_client import HubError


class Command(BaseCommand):
    help = "Daily pipeline: pull hub, trim per-source limits, generate brief (--llm), purge >7d items."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=200)
        parser.add_argument("--llm", action="store_true", help="generate daily brief via LLM")
        parser.add_argument("--force-brief", action="store_true", help="regenerate today's brief")
        parser.add_argument("--reset-cursor", action="store_true")

    def handle(self, *args, **options):
        try:
            stats = pull.pull_items(
                limit=options["limit"],
                reset_cursor=options["reset_cursor"],
            )
        except HubError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"pull ok: fetched={stats['fetched']} created={stats['created']} "
                f"updated={stats['updated']} since={stats['since']}"
            )
        )

        trimmed = pull.apply_source_limits()
        if trimmed:
            self.stdout.write(self.style.SUCCESS(f"source limits trimmed: {trimmed}"))

        if options["llm"]:
            from rss import llm as llm_mod

            items = pull.items_for_brief()
            brief_stats = llm_mod.generate_daily_brief(items, force=options["force_brief"])
            note = " DEGRADED(fallback list)" if brief_stats.get("degraded") else ""
            self.stdout.write(
                self.style.SUCCESS(
                    f"brief: date={brief_stats['date']} items={brief_stats['items']} "
                    f"action={brief_stats['action']}{note}"
                )
            )

        purged = pull.purge_old_items()
        self.stdout.write(self.style.SUCCESS(f"purged items older than 7d: {purged}"))
