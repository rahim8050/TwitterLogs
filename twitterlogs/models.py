from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from django.db.models import Manager


class FollowerSnapshot(models.Model):
    owner_user_id: models.CharField = models.CharField(max_length=50)
    data: models.JSONField = models.JSONField()
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    # Type hint for MyPy to recognize the manager
    if TYPE_CHECKING:
        objects: Manager[FollowerSnapshot]

    def __str__(self) -> str:
        return f"Snapshot({self.owner_user_id})"
