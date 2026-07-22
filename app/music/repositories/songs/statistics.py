"""
Songs Statistics Repository
===========================

Repository untuk statistik Songs.

Repository hanya bertanggung jawab menjalankan
query PostgreSQL.
"""

from __future__ import annotations

from app.core.database import get_dict_cursor

from .types import SongStatistics

# ==========================================================
# SONG STATISTICS
# ==========================================================


def get_statistics() -> SongStatistics:
    """
    Return song statistics.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total,

                COUNT(*) FILTER (
                    WHERE status = 'live'
                ) AS live,

                COUNT(*) FILTER (
                    WHERE status = 'review'
                ) AS review,

                COUNT(*) FILTER (
                    WHERE status = 'approved'
                ) AS approved

            FROM songs
            """
        )

        return cursor.fetchone()


# ==========================================================
# COUNT ALL
# ==========================================================


def count_all() -> int:
    """
    Return total songs.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total
            FROM songs
            """
        )

        return cursor.fetchone()["total"]


# ==========================================================
# COUNT LIVE
# ==========================================================


def count_live() -> int:
    """
    Return total Live songs.
    """

    return count_by_status("Live")


# ==========================================================
# COUNT REVIEW
# ==========================================================


def count_review() -> int:
    """
    Return total Review songs.
    """

    return count_by_status("Review")


# ==========================================================
# COUNT APPROVED
# ==========================================================


def count_approved() -> int:
    """
    Return total Approved songs.
    """

    return count_by_status("Approved")


# ==========================================================
# COUNT BY STATUS
# ==========================================================


def count_by_status(
    status: str,
) -> int:
    """
    Return song count by status.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total
            FROM songs
            WHERE status = %s
            """,
            (status,),
        )

        return cursor.fetchone()["total"]


# ==========================================================
# COUNT BY CHANNEL
# ==========================================================


def count_by_channel(
    channel_id: int,
) -> int:
    """
    Return total songs in a channel.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total

            FROM songs s

            JOIN artists a
                ON s.artist_id = a.id

            WHERE
                a.channel_id = %s
            """,
            (channel_id,),
        )

        return cursor.fetchone()["total"]
