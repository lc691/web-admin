"""
Songs Repository Types
======================

TypedDict definitions untuk feature Songs.
"""

from __future__ import annotations

from datetime import date
from datetime import datetime
from typing import Literal
from typing_extensions import TypedDict


# ==========================================================
# SONG STATUS
# ==========================================================

SongStatus = Literal[
    "Live",
    "Review",
    "Approved",
]


# ==========================================================
# SONG
# ==========================================================

class SongRow(TypedDict):
    """
    Song list row.
    """

    id: int
    title: str

    artist_id: int
    artist: str

    channel_id: int
    channel: str

    status: SongStatus
    release_date: date | None


# ==========================================================
# SONG DETAIL
# ==========================================================

class SongDetail(TypedDict):
    """
    Song detail.
    """

    id: int

    title: str

    artist_id: int
    artist: str

    channel_id: int
    channel: str

    status: SongStatus
    release_date: date | None

    created_at: datetime
    updated_at: datetime | None


# ==========================================================
# CREATE SONG
# ==========================================================

class CreateSong(TypedDict):
    """
    Create song payload.
    """

    artist_id: int
    title: str
    status: SongStatus
    release_date: date | None


# ==========================================================
# UPDATE SONG
# ==========================================================

class UpdateSong(TypedDict):
    """
    Update song payload.
    """

    artist_id: int
    title: str
    status: SongStatus
    release_date: date | None


# ==========================================================
# SONG FILTERS
# ==========================================================

class SongFilters(TypedDict):
    """
    Song search filters.
    """

    keyword: str | None

    channel_id: int | None
    artist_id: int | None

    status: SongStatus | None


# ==========================================================
# SONG LIST RESULT
# ==========================================================

class SongListResult(TypedDict):
    """
    DataTables result.
    """

    total: int
    filtered: int

    songs: list[SongRow]


# ==========================================================
# SONG STATISTICS
# ==========================================================

class SongStatistics(TypedDict):
    """
    Dashboard statistics.
    """

    total: int
    live: int
    review: int
    approved: int


# ==========================================================
# PUBLIC EXPORTS
# ==========================================================

__all__ = [
    "CreateSong",
    "SongDetail",
    "SongFilters",
    "SongListResult",
    "SongRow",
    "SongStatistics",
    "SongStatus",
    "UpdateSong",
]