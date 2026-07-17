"""
Usage Types
===========

Shared type definitions untuk feature Usage.
"""

from __future__ import annotations

from typing import Literal
from typing import TypedDict

# ==========================================================
# MODE
# ==========================================================

UsageMode = Literal[
    "normal",
    "clean",
    "blacklist",
]

# ==========================================================
# SONG
# ==========================================================


class UsageSong(
    TypedDict,
):
    """
    Song inside export batch.
    """

    song_id: int
    title: str
    artist: str
    channel: str
    order_index: int


# ==========================================================
# BATCH
# ==========================================================


class UsageBatch(
    TypedDict,
):
    """
    Export batch information.
    """

    id: int
    day: int
    mode: UsageMode
    target: int
    duplicate: int
    selected_unique: int
    channel_limit: int
    created_at: str | None
    completed_at: str | None


# ==========================================================
# STATISTICS
# ==========================================================


class UsageStatistics(
    TypedDict,
):
    """
    Usage statistics.
    """

    total_songs: int
    total_channels: int
    total_artists: int
    total_unique: int


# ==========================================================
# RESULT
# ==========================================================


class UsageResult(
    TypedDict,
):
    """
    Usage response.
    """

    batch: UsageBatch
    statistics: UsageStatistics
    songs: list[UsageSong]