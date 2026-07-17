"""
Songs Artists Repository
========================

Repository untuk data Artist yang digunakan
oleh feature Songs.

Repository hanya bertanggung jawab menjalankan
query PostgreSQL.
"""

from __future__ import annotations

from app.core.database import get_dict_cursor

# ==========================================================
# GET ARTISTS
# ==========================================================


def get_artists() -> list[dict]:
    """
    Return all artists.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                a.id,
                a.name,

                c.id AS channel_id,
                c.name AS channel

            FROM artists a

            JOIN channels c
                ON a.channel_id = c.id

            ORDER BY
                c.name,
                a.name
            """
        )

        return cursor.fetchall()


# ==========================================================
# GET ARTIST
# ==========================================================


def get_artist(
    artist_id: int,
) -> dict | None:
    """
    Return artist detail.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                a.id,
                a.name,

                c.id AS channel_id,
                c.name AS channel

            FROM artists a

            JOIN channels c
                ON a.channel_id = c.id

            WHERE
                a.id = %s
            """,
            (artist_id,),
        )

        return cursor.fetchone()


# ==========================================================
# GET ARTIST OPTIONS
# ==========================================================


def get_artist_options() -> list[dict]:
    """
    Return artist options for dropdown.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                id,
                name

            FROM artists

            ORDER BY
                name
            """
        )

        return cursor.fetchall()


# ==========================================================
# GET ARTISTS BY CHANNEL
# ==========================================================


def get_artists_by_channel(
    channel_id: int,
) -> list[dict]:
    """
    Return artists by channel.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                id,
                name

            FROM artists

            WHERE
                channel_id = %s

            ORDER BY
                name
            """,
            (channel_id,),
        )

        return cursor.fetchall()


# ==========================================================
# ARTIST EXISTS
# ==========================================================


def artist_exists(
    artist_id: int,
) -> bool:
    """
    Return True if artist exists.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT EXISTS
            (
                SELECT 1
                FROM artists
                WHERE id = %s
            ) AS exists
            """,
            (artist_id,),
        )

        return cursor.fetchone()["exists"]
