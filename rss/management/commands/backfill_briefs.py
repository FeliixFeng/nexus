from __future__ import annotations

from datetime import date as date_cls

from django.core.management.base import BaseCommand, CommandError

from rss import data as pull
from rss import llm as llm_mod


class Command(BaseCommand):
    help = "Backfill daily briefs for given dates (skips dates that already have one unless --force)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dates",
            required=True,
            help="comma list of YYYY-MM-DD, or an inclusive range start:end",
        )
        parser.add_argument("--force", action="store_true", help="regenerate even if brief exists")

    def handle(self, *args, **options):
        days = self._parse_dates(options["dates"])
        for day in days:
            items = pull.items_for_brief_day(day)
            stats = llm_mod.generate_daily_brief(items, force=options["force"], brief_date=day)
            note = " DEGRADED(fallback list)" if stats.get("degraded") else ""
            self.stdout.write(
                self.style.SUCCESS(
                    f"brief: date={stats['date']} items={stats['items']} "
                    f"action={stats['action']}{note}"
                )
            )

    @staticmethod
    def _parse_dates(spec: str) -> list[date_cls]:
        spec = spec.strip()
        try:
            if ":" in spec:
                start_s, end_s = spec.split(":", 1)
                start = date_cls.fromisoformat(start_s)
                end = date_cls.fromisoformat(end_s)
                if end < start:
                    raise ValueError("range end before start")
                days, cur = [], start
                while cur <= end:
                    days.append(cur)
                    cur = date_cls.fromordinal(cur.toordinal() + 1)
                return days
            return [date_cls.fromisoformat(p) for p in spec.split(",") if p.strip()]
        except ValueError as exc:
            raise CommandError(f"bad --dates {spec!r}: {exc}") from exc
