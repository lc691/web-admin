"""
Usage Songs Service
===================

Business logic untuk
Usage Songs.
"""

from __future__ import annotations

from app.music.repositories.usage.songs import (
    count_usage_songs,
    get_usage_songs,
)

from .types import (
    UsageSong,
)

# ==========================================================
# SONGS
# ==========================================================


def songs(
    *,
    batch_id: int,
) -> list[UsageSong]:
    """
    Return songs inside export batch.
    """

    return get_usage_songs(
        batch_id=batch_id,
    )


# ==========================================================
# COUNT
# ==========================================================


def count(
    *,
    batch_id: int,
) -> int:
    """
    Return total songs inside batch.
    """

    return count_usage_songs(
        batch_id=batch_id,
    )