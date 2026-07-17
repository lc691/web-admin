"""
Songs Filter Service
====================

Business logic untuk filter Songs.

Service tidak mengandung query SQL.
"""

from __future__ import annotations

from app.music.repositories.songs.filters import (
    get_song_filters,
)
from app.music.repositories.songs.types import (
    SongFilters,
)


# ==========================================================
# DEFAULT FILTERS
# ==========================================================


def default_filters() -> SongFilters:
    """
    Return default search filters.
    """

    return {
        "keyword": None,
        "channel_id": None,
        "artist_id": None,
        "status": None,
    }


# ==========================================================
# BUILD FILTERS
# ==========================================================


def build_filters(
    *,
    keyword: str | None = None,
    channel_id: int | None = None,
    artist_id: int | None = None,
    status: str | None = None,
) -> SongFilters:
    """
    Build search filters.
    """

    filters = default_filters()

    filters["keyword"] = (
        keyword.strip()
        if keyword
        else None
    )

    filters["channel_id"] = channel_id
    filters["artist_id"] = artist_id
    filters["status"] = status

    return filters


# ==========================================================
# AVAILABLE FILTERS
# ==========================================================


def available_filters() -> dict:
    """
    Return available filters
    for Songs page.
    """

    return get_song_filters()


# ==========================================================
# RESET FILTERS
# ==========================================================


def reset_filters() -> SongFilters:
    """
    Reset all filters.
    """

    return default_filters()