"""
Export Status Service
=====================

Business logic untuk status export.
"""

from __future__ import annotations

from app.music.repositories.export.get_status import (
    get_export_status,
)

from .types import (
    ExportMode,
)

# ==========================================================
# EXPORT STATUS
# ==========================================================


def get_status(
    *,
    mode: ExportMode,
) -> list[dict]:
    """
    Return export status.
    """

    rows = [
        dict(row)
        for row in get_export_status(
            mode=mode,
        )
    ]

    for row in rows:

        target = row["target"]

        duplicate = max(
            row["duplicate"],
            1,
        )

        target_unique = (
            target + duplicate - 1
        ) // duplicate

        row["target_unique"] = target_unique

        row["remaining"] = max(
            target_unique - row["exported"],
            0,
        )

        row["completed"] = (
            row["exported"] >= target_unique
        )

    return rows