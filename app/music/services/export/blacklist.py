"""
Export Blacklist Helper
=======================

Helper untuk menentukan filter channel berdasarkan mode export.

Tidak melakukan query database.
Tidak mengandung business process.

Digunakan oleh repository dan service.
"""

from __future__ import annotations

from app.music.repositories.export.types import ExportMode

# ==========================================================
# MODE FILTER
# ==========================================================


def include_blacklist(mode: ExportMode) -> bool:
    """
    Return True if blacklist channels should be included.

    normal      -> True
    clean       -> False
    blacklist   -> True
    """

    return mode in (
        "normal",
        "blacklist",
    )


def only_blacklist(mode: ExportMode) -> bool:
    """
    Return True if only blacklist channels are allowed.

    normal      -> False
    clean       -> False
    blacklist   -> True
    """

    return mode == "blacklist"


def exclude_blacklist(mode: ExportMode) -> bool:
    """
    Return True if blacklist channels must be excluded.

    normal      -> False
    clean       -> True
    blacklist   -> False
    """

    return mode == "clean"


# ==========================================================
# SQL FILTER
# ==========================================================


def build_mode_filter(
    mode: ExportMode,
) -> str:
    """
    Return SQL condition for export mode.

    normal
        No blacklist filter.

    clean
        Exclude blacklist channels.

    blacklist
        Only blacklist channels.
    """

    if mode == "clean":
        return "cb.channel_id IS NULL"

    if mode == "blacklist":
        return "cb.channel_id IS NOT NULL"

    return "TRUE"