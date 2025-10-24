from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from django.utils import timezone
from twitter_unfollow.models import FollowerSnapshot
from twitter_unfollow.services.twitter_client import TwitterClient


class Command(BaseCommand):
    help = "Take a snapshot of followers for a given Twitter user ID and store it in the database."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("user_id", type=str, help="Twitter user ID to snapshot")

    def handle(self, *args: Any, **options: Any) -> None:
        user_id: str = options["user_id"]

        with TwitterClient() as client:
            self.stdout.write(f"Fetching followers for user {user_id}...")
            followers: list[str] = client.followers(user_id)

        now = timezone.now()
        payload: dict[str, Any] = {
            "fetched_at": now.isoformat(),
            "followers": followers,
        }

        # Tell MyPy explicitly that this is a Django model instance
        snap: FollowerSnapshot = FollowerSnapshot.objects.create(
            owner_user_id=user_id,
            data=payload,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Saved snapshot id={snap.pk} with {len(followers)} followers"
            )
        )
