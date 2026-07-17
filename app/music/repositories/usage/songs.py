"""
Usage Songs Repository
======================

Repository untuk daftar lagu
yang berada di dalam export batch.
"""

from __future__ import annotations

from app.core.database import get_dict_cursor

from .types import (
    UsageSong,
)

# ==========================================================
# GET USAGE SONGS
# ==========================================================


def get_usage_songs(
    *,
    batch_id: int,
) -> list[UsageSong]:
    """
    Return songs inside export batch.
    """

    with get_dict_cursor() as (cursor, _):

        cursor.execute(
            """
            SELECT

                bi.song_id,

                s.title,

                a.name AS artist,

                c.name AS channel,

                bi.order_index

            FROM song_export_batch_items bi

            JOIN songs s
                ON s.id = bi.song_id

            JOIN artists a
                ON a.id = s.artist_id

            JOIN channels c
                ON c.id = a.channel_id

            WHERE
                bi.batch_id = %s

            ORDER BY
                bi.order_index
            """,
            (
                batch_id,
            ),
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]


# ==========================================================
# COUNT SONGS
# ==========================================================


def count_usage_songs(
    *,
    batch_id: int,
) -> int:
    """
    Return total songs inside batch.
    """

    with get_dict_cursor() as (cursor, _):

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total
            FROM song_export_batch_items
            WHERE
                batch_id = %s
            """,
            (
                batch_id,
            ),
        )

        return cursor.fetchone()["total"]