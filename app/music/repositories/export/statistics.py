"""
Export Statistics Repository
============================

Repository untuk statistik export.

Repository hanya bertanggung jawab menjalankan query PostgreSQL.
"""

from __future__ import annotations

from app.core.database import get_dict_cursor

from .types import (
    ExportInformation,
    ExportMode,
)

# ==========================================================
# EXPORT EXISTENCE
# ==========================================================


def export_exists(
    day: int,
    mode: ExportMode,
) -> bool:
    """
    Return True if export batch already exists.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT EXISTS
            (
                SELECT 1
                FROM song_export_batches
                WHERE
                    day = %s
                    AND mode = %s
            ) AS exists
            """,
            (
                day,
                mode,
            ),
        )

        return cursor.fetchone()["exists"]


# ==========================================================
# REMAINING SONG COUNT
# ==========================================================


def get_remaining_song_count(
    mode: ExportMode,
) -> int:
    """
    Return remaining available songs for export.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total
            FROM songs s
            JOIN artists a
                ON s.artist_id = a.id
            JOIN channels c
                ON a.channel_id = c.id
            LEFT JOIN song_usage u
                ON u.song_id = s.id
               AND u.mode = %s
            LEFT JOIN channel_blacklists cb
                ON cb.channel_id = c.id
            WHERE
                s.status = 'live'
                AND u.song_id IS NULL
                AND (
                    %s = 'normal'
                    OR (
                        %s = 'clean'
                        AND cb.channel_id IS NULL
                    )
                    OR (
                        %s = 'blacklist'
                        AND cb.channel_id IS NOT NULL
                    )
                )
            """,
            (
                mode,
                mode,
                mode,
                mode,
            ),
        )

        return cursor.fetchone()["total"]


# ==========================================================
# TOTAL LIVE SONG COUNT
# ==========================================================


def get_total_song_count(
    mode: ExportMode,
) -> int:
    """
    Return total available Live songs by export mode.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total
            FROM songs s
            JOIN artists a
                ON s.artist_id = a.id
            JOIN channels c
                ON a.channel_id = c.id
            LEFT JOIN channel_blacklists cb
                ON cb.channel_id = c.id
            WHERE
                s.status = 'live'
                AND (
                    %s = 'normal'
                    OR (
                        %s = 'clean'
                        AND cb.channel_id IS NULL
                    )
                    OR (
                        %s = 'blacklist'
                        AND cb.channel_id IS NOT NULL
                    )
                )
            """,
            (
                mode,
                mode,
                mode,
            ),
        )

        return cursor.fetchone()["total"]


# ==========================================================
# EXPORT INFORMATION
# ==========================================================


def get_export_information(
    day: int,
    mode: ExportMode,
) -> ExportInformation:
    """
    Return export information.
    """

    remaining = get_remaining_song_count(mode)
    total = get_total_song_count(mode)

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                selected_unique
            FROM song_export_batches
            WHERE
                day = %s
                AND mode = %s
            """,
            (
                day,
                mode,
            ),
        )

        row = cursor.fetchone()

    unique_songs = (
        row["selected_unique"]
        if row
        else 0
    )

    return {
        "remaining": remaining,
        "already_exported": row is not None,
        "unique_songs": unique_songs,
        "total_available": total,
        "day": day,
        "mode": mode,
    }