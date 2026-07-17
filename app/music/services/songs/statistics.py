"""
Songs Statistics Service
========================

Business logic untuk statistik Songs.
"""

from __future__ import annotations

from app.music.repositories.songs.statistics import (
    get_statistics,
)
from app.music.repositories.songs.types import (
    SongStatistics,
)

from .formatter import (
    format_statistics,
)

# ==========================================================
# GET STATISTICS
# ==========================================================


def get_song_statistics() -> SongStatistics:
    """
    Return formatted song statistics.
    """

    statistics = get_statistics()

    return format_statistics(
        statistics,
    )


# ==========================================================
# BUILD STATISTICS
# ==========================================================


def build_statistics() -> dict:
    """
    Build statistics for dashboard.
    """

    statistics = get_song_statistics()

    return {
        "total": statistics["total"],
        "live": statistics["live"],
        "review": statistics["review"],
        "approved": statistics["approved"],
    }


# ==========================================================
# SUMMARY
# ==========================================================


def build_summary() -> dict:
    """
    Build summary information.
    """

    statistics = get_song_statistics()

    return {
        "statistics": statistics,
        "has_live": statistics["live"] > 0,
        "has_review": statistics["review"] > 0,
        "has_approved": statistics["approved"] > 0,
    }
