"""
Songs Search Service
====================

Business logic untuk pencarian Songs.
"""

from __future__ import annotations

from app.music.repositories.songs.search import (
    search_songs,
)
from app.music.repositories.songs.types import (
    SongFilters,
    SongListResult,
)

from .formatter import (
    format_song_list,
)

# ==========================================================
# SEARCH SONGS
# ==========================================================


def search(
    *,
    filters: SongFilters,
    start: int,
    length: int,
    order_by: str = "s.id",
    descending: bool = True,
) -> SongListResult:
    """
    Search songs.

    Workflow

    1. Query repository
    2. Format result
    3. Return result
    """

    result = search_songs(
        filters=filters,
        start=start,
        length=length,
        order_by=order_by,
        descending=descending,
    )

    return format_song_list(
        result,
    )


# ==========================================================
# BUILD RESPONSE
# ==========================================================


def build_response(
    *,
    draw: int,
    filters: SongFilters,
    start: int,
    length: int,
    order_by: str = "s.id",
    descending: bool = True,
) -> dict:
    """
    Build DataTables response.
    """

    result = search(
        filters=filters,
        start=start,
        length=length,
        order_by=order_by,
        descending=descending,
    )

    return {
        "draw": draw,
        "recordsTotal": result["total"],
        "recordsFiltered": result["filtered"],
        "data": result["songs"],
    }
