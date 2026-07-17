"""
Usage Statistics Repository
===========================

Repository untuk statistik
export usage.
"""

from __future__ import annotations

from app.core.database import get_dict_cursor

from .types import (
    UsageStatistics,
)

# ==========================================================
# STATISTICS
# ==========================================================

def get_statistics(
    *,
    batch_id: int,
) -> UsageStatistics:
    """
    Return usage statistics.
    """

    with get_dict_cursor() as (cursor, _):

        cursor.execute(
            """
            SELECT

                COUNT(*) AS total_songs,

                COUNT(
                    DISTINCT s.artist_id
                ) AS total_artists,

                COUNT(
                    DISTINCT a.channel_id
                ) AS total_channels,

                COUNT(
                    DISTINCT bi.song_id
                ) AS total_unique

            FROM song_export_batch_items bi

            JOIN songs s
                ON s.id = bi.song_id

            JOIN artists a
                ON a.id = s.artist_id

            WHERE
                bi.batch_id = %s
            """,
            (
                batch_id,
            ),
        )

        row = cursor.fetchone()

        return dict(row) if row else {
            "total_songs": 0,
            "total_artists": 0,
            "total_channels": 0,
            "total_unique": 0,
        }