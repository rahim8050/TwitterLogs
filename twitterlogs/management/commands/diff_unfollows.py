from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from twitter_unfollow.models import FollowerSnapshot


def _extract_ids(snapshot: FollowerSnapshot) -> set[str]:
    followers: list[dict[str, Any]] = snapshot.data.get("followers") or []
    return {str(u["id"]) for u in followers if "id" in u}


class Command(BaseCommand):
    help = "Diff the last two snapshots and print users who unfollowed since the previous snapshot."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("user_id", type=str, help="Twitter user ID to diff")

    def handle(self, *args: Any, **options: Any) -> None:
        user_id: str = options["user_id"]
        snaps = list(
            FollowerSnapshot.objects.filter(owner_user_id=user_id).order_by(
                "-created_at"
            )[:2]
        )

        if len(snaps) < 2:
            self.stdout.write(
                self.style.WARNING("Need at least two snapshots to compute diffs")
            )
            return

        latest, previous = snaps[0], snaps[1]
        latest_ids = _extract_ids(latest)
        previous_ids = _extract_ids(previous)

        unfollowed = previous_ids - latest_ids

        if not unfollowed:
            self.stdout.write(
                self.style.SUCCESS(
                    "No unfollows detected between the last two snapshots."
                )
            )
            return

        self.stdout.write(self.style.WARNING(f"Detected {len(unfollowed)} unfollows:"))
        for uid in unfollowed:
            self.stdout.write(uid)
