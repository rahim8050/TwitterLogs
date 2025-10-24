from __future__ import annotations

import logging
from types import TracebackType
from typing import Any

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


class TwitterClient:
    """Typed, production-ready Twitter API client."""

    BASE_URL: str = "https://api.twitter.com/2"

    def __init__(self, bearer_token: str | None = None) -> None:
        token = bearer_token or getattr(settings, "TWITTER_BEARER_TOKEN", "")
        self.bearer_token: str = str(token)  # Cast ensures MyPy sees it as str

        if not self.bearer_token:
            msg = "Twitter bearer token is missing. Set TWITTER_BEARER_TOKEN in environment."
            logger.error(msg)
            raise ValueError(msg)

        self._client = httpx.Client(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bearer {self.bearer_token}"},
            timeout=httpx.Timeout(15.0),
            follow_redirects=True,
        )

    def followers(self, user_id: str) -> list[str]:
        """Fetch followers for a given Twitter user ID."""
        url = f"/users/{user_id}/followers"
        params: dict[str, Any] = {"max_results": 1000, "user.fields": "id"}

        try:
            response = self._client.get(url, params=params)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.exception("HTTP error fetching followers for user %s", user_id)
            raise RuntimeError(f"Twitter API request failed: {exc}") from exc

        data: dict[str, Any] = response.json()
        users = data.get("data", [])
        followers: list[str] = [user["id"] for user in users if "id" in user]

        logger.info("Fetched %d followers for user %s", len(followers), user_id)
        return followers

    def close(self) -> None:
        """Cleanly close the HTTP client."""
        self._client.close()

    def __enter__(self) -> TwitterClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()
