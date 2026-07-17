"""
Songs Channels Repository
=========================

Repository untuk data Channel yang digunakan
oleh feature Songs.

Repository hanya bertanggung jawab menjalankan
query PostgreSQL.
"""

from __future__ import annotations

from app.core.database import get_dict_cursor

# ==========================================================
# GET CHANNELS
# ==========================================================


def get_channels() -> list[dict]:
    """
    Return all channels.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                c.id,
                c.name,
                c.youtube_url,

                COUNT(a.id) AS artist_count,

                COUNT(s.id) AS song_count

            FROM channels c

            LEFT JOIN artists a
                ON c.id = a.channel_id

            LEFT JOIN songs s
                ON a.id = s.artist_id

            GROUP BY
                c.id,
                c.name,
                c.youtube_url

            ORDER BY
                c.name
            """
        )

        return cursor.fetchall()


# ==========================================================
# GET CHANNEL
# ==========================================================


def get_channel(
    channel_id: int,
) -> dict | None:
    """
    Return channel detail.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                id,
                name,
                youtube_url,
                created_at,
                updated_at
            FROM channels
            WHERE id = %s
            """,
            (channel_id,),
        )

        return cursor.fetchone()


# ==========================================================
# GET CHANNEL OPTIONS
# ==========================================================


def get_channel_options() -> list[dict]:
    """
    Return channel options for dropdown.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                id,
                name
            FROM channels
            ORDER BY
                name
            """
        )

        return cursor.fetchall()


# ==========================================================
# CHANNEL EXISTS
# ==========================================================


def channel_exists(
    channel_id: int,
) -> bool:
    """
    Return True if channel exists.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT EXISTS
            (
                SELECT 1
                FROM channels
                WHERE id = %s
            ) AS exists
            """,
            (channel_id,),
        )

        return cursor.fetchone()["exists"]


# ==========================================================
# GET CHANNEL SONG COUNT
# ==========================================================


def get_channel_song_count(
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
