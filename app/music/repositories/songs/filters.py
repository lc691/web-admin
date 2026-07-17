"""
Songs Filters Repository
========================

Repository untuk data filter pada halaman Songs.

Repository hanya bertanggung jawab menjalankan
query PostgreSQL.
"""

from __future__ import annotations

from app.core.database import get_dict_cursor


# ==========================================================
# STATUS FILTERS
# ==========================================================


def get_status_filters() -> list[dict]:
    """
    Return available song status filters.
    """

    return [
        {
            "value": "Live",
            "label": "Live",
        },
        {
            "value": "Review",
            "label": "Review",
        },
        {
            "value": "Approved",
            "label": "Approved",
        },
    ]


# ==========================================================
# CHANNEL FILTERS
# ==========================================================


def get_channel_filters() -> list[dict]:
    """
    Return available channel filters.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                c.id,
                c.name,

                COUNT(s.id) AS song_count

            FROM channels c

            LEFT JOIN artists a
                ON c.id = a.channel_id

            LEFT JOIN songs s
                ON a.id = s.artist_id

            GROUP BY
                c.id,
                c.name

            ORDER BY
                c.name
            """
        )

        return cursor.fetchall()


# ==========================================================
# ARTIST FILTERS
# ==========================================================


def get_artist_filters() -> list[dict]:
    """
    Return available artist filters.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                a.id,
                a.name,

                c.id AS channel_id,
                c.name AS channel,

                COUNT(s.id) AS song_count

            FROM artists a

            JOIN channels c
                ON a.channel_id = c.id

            LEFT JOIN songs s
                ON a.id = s.artist_id

            GROUP BY
                a.id,
                a.name,
                c.id,
                c.name

            ORDER BY
                c.name,
                a.name
            """
        )

        return cursor.fetchall()


# ==========================================================
# ALL FILTERS
# ==========================================================


def get_song_filters() -> dict:
    """
    Return all filters for Songs page.
    """

    return {
        "statuses": get_status_filters(),
        "channels": get_channel_filters(),
        "artists": get_artist_filters(),
    }
