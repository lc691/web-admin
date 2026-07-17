"""
Export Status Repository
========================

Repository untuk status export per day.
"""

from __future__ import annotations

from app.core.database import get_dict_cursor

from .types import (
    ExportMode,
)

# ==========================================================
# EXPORT STATUS
# ==========================================================


def get_export_status(
    mode: ExportMode,
) -> list[dict]:
    """
    Return export status for every day.
    """

    with get_dict_cursor() as (cursor, _):

        cursor.execute(
            """
            SELECT
                day,
                target,
                duplicate,
                selected_unique AS exported
            FROM song_export_batches
            WHERE mode = %s
            ORDER BY day
            """,
            (
                mode,
            ),
        )

        return cursor.fetchall()