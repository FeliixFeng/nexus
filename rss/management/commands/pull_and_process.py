from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from rss import data as pull
from rss.hub_client import HubError


class Command(BaseCommand):
    help = "Pull rss-hub since cursor, upsert FeedItem (idempotent). Optional --llm for score+brief."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=50)
        parser.add_argument("--llm", action="store_true", help="run L1 score + L2 brief after pull")
        parser.add_argument("--no-brief", action="store_true", help="skip L2 brief even with --llm")
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

        if options["llm"]:
            from rss import llm as llm_mod

            score_stats = llm_mod.process_unprocessed()
            self.stdout.write(
                self.style.SUCCESS(
                    f"llm L1: scored={score_stats['scored']} failed={score_stats['failed']} "
                    f"skipped={score_stats['skipped']}"
                )
            )
            if not options["no_brief"]:
                brief_stats = llm_mod.ensure_daily_brief()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"llm L2: brief_date={brief_stats['date']} items={brief_stats['items']} "
                        f"action={brief_stats['action']}"
                    )
                )
