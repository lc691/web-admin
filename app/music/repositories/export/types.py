"""
Export repository type definitions.
"""

from __future__ import annotations

from typing import Literal, TypedDict

# ==========================================================
# EXPORT MODE
# ==========================================================

ExportMode = Literal[
    "normal",
    "clean",
    "blacklist",
]


# ==========================================================
# SONG
# ==========================================================

class SongRow(TypedDict):
    """
    Song returned by export repositories.
    """

    id: int
    title: str
    artist: str
    channel_id: int
    channel: str


# ==========================================================
# EXPORT BATCH
# ==========================================================

class ExportBatch(TypedDict):
    """
    Export batch metadata.
    """

    id: int
    day: int
    mode: ExportMode

    target: int
    duplicate: int
    channel_limit: int
    selected_unique: int

    excluded_channels: list[int]

    status: str

    created_at: object
    completed_at: object | None


# ==========================================================
# EXPORT BATCH ITEM
# ==========================================================

class ExportBatchItem(TypedDict):
    """
    Export batch item.
    """

    id: int
    batch_id: int
    song_id: int
    order_index: int


# ==========================================================
# EXPORT INFORMATION
# ==========================================================

class ExportInformation(TypedDict):
    """
    Export statistics.
    """

    remaining: int
    already_exported: bool
    unique_songs: int
    total_available: int

    day: int
    mode: ExportMode


# ==========================================================
# PUBLIC EXPORTS
# ==========================================================

__all__ = [
    "ExportBatch",
    "ExportBatchItem",
    "ExportInformation",
    "ExportMode",
    "SongRow",
]
