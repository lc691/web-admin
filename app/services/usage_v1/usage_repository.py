"""
Repository Song Usage.

Seluruh query PostgreSQL
berada di file ini.
"""

from __future__ import annotations

from app.music.services.export.types import ExportMode

from app.core.database import get_dict_cursor

from .types import (
    UsageRow,
    UsageStatistics,
)


# ==========================================================
# DETAIL
# ==========================================================


def get_day_usage(
    *,
    day: int,
    mode: ExportMode,
    channel_id: int | None = None,
) -> list[UsageRow]:
    """
    Mengambil seluruh lagu
    yang digunakan pada
    hari tertentu.
    """

    query = """
    SELECT
        u.id AS usage_id,

        s.id AS song_id,
        s.title,
        s.status,
        s.status::text AS status_text,
        s.release_date,

        a.id AS artist_id,
        a.name AS artist,

        c.id AS channel_id,
        c.name AS channel,

        u.day,
        u.mode,
        u.used_at

    FROM song_usage u

    JOIN songs s
        ON u.song_id = s.id

    JOIN artists a
        ON s.artist_id = a.id

    JOIN channels c
        ON a.channel_id = c.id

    WHERE
        u.day = %s
        AND u.mode = %s
    """

    params: list = [
        day,
        mode,
    ]

    if channel_id is not None:

        query += """
        AND c.id = %s
        """

        params.append(channel_id)

    query += """
    ORDER BY
        u.used_at DESC,
        u.id DESC
    """

    with get_dict_cursor() as (cursor, conn):

        cursor.execute(
            query,
            params,
        )

        return cursor.fetchall()


# ==========================================================
# SUMMARY
# ==========================================================


def get_day_usage_stats(
    *,
    day: int,
    mode: ExportMode,
    channel_id: int | None = None,
) -> UsageStatistics:
    """
    Statistik penggunaan lagu
    pada hari tertentu.
    """

    query = """
    SELECT

        COUNT(*) AS total_usage,

        COUNT(DISTINCT c.id)
            AS total_channels,

        COUNT(DISTINCT a.id)
            AS total_artists,

        COUNT(
            CASE
                WHEN s.status = 'Live'
                THEN 1
            END
        ) AS live_songs,

        COUNT(
            CASE
                WHEN s.status = 'Approved'
                THEN 1
            END
        ) AS approved_songs,

        COUNT(
            CASE
                WHEN s.status = 'Review'
                THEN 1
            END
        ) AS review_songs,

        COUNT(
            CASE
                WHEN s.status = 'Take Down'
                THEN 1
            END
        ) AS takedown_songs,

        COUNT(
            CASE
                WHEN s.status = 'Topic'
                THEN 1
            END
        ) AS topic_songs,

        MIN(u.used_at)
            AS first_used,

        MAX(u.used_at)
            AS last_used

    FROM song_usage u

    JOIN songs s
        ON u.song_id = s.id

    JOIN artists a
        ON s.artist_id = a.id

    JOIN channels c
        ON a.channel_id = c.id

    WHERE
        u.day = %s
        AND u.mode = %s
    """

    params: list = [
        day,
        mode,
    ]

    if channel_id is not None:

        query += """
        AND c.id = %s
        """

        params.append(channel_id)

    with get_dict_cursor() as (cursor, conn):

        cursor.execute(
            query,
            params,
        )

        return cursor.fetchone()


# ==========================================================
# USED DAYS
# ==========================================================


def get_used_days(
    mode: ExportMode,
) -> list[int]:
    """
    Mengambil daftar hari
    yang sudah pernah
    diexport pada mode tertentu.
    """

    with get_dict_cursor() as (cursor, conn):

        cursor.execute(
            """
            SELECT DISTINCT
                day

            FROM song_usage

            WHERE
                mode = %s

            ORDER BY
                day
            """,
            (mode,),
        )

        return [
            row["day"]
            for row in cursor.fetchall()
        ]