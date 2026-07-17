"""
Songs Duplicate Repository
==========================

Repository untuk pengecekan lagu duplikat.

Repository hanya bertanggung jawab menjalankan
query PostgreSQL.
"""

from __future__ import annotations

from app.core.database import get_dict_cursor


# ==========================================================
# FIND DUPLICATE TITLE
# ==========================================================


def find_duplicate_title(
    *,
    artist_id: int,
    title: str,
    exclude_song_id: int | None = None,
) -> bool:
    """
    Return True if duplicate title exists
    for the same artist.
    """

    sql = """
        SELECT EXISTS
        (
            SELECT 1
            FROM songs
            WHERE
                artist_id = %s
                AND LOWER(TRIM(title))
                    = LOWER(TRIM(%s))
    """

    params: list[object] = [
        artist_id,
        title,
    ]

    if exclude_song_id is not None:
        sql += """
            AND id <> %s
        """
        params.append(exclude_song_id)

    sql += """
        ) AS exists
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            sql,
            params,
        )

        return cursor.fetchone()["exists"]


# ==========================================================
# FIND DUPLICATE SONG
# ==========================================================


def find_duplicate_song(
    *,
    artist_id: int,
    title: str,
    exclude_song_id: int | None = None,
) -> dict | None:
    """
    Return duplicate song if exists.
    """

    sql = """
        SELECT
            id,
            artist_id,
            title,
            status,
            release_date
        FROM songs
        WHERE
            artist_id = %s
            AND LOWER(TRIM(title))
                = LOWER(TRIM(%s))
    """

    params: list[object] = [
        artist_id,
        title,
    ]

    if exclude_song_id is not None:
        sql += """
            AND id <> %s
        """
        params.append(exclude_song_id)

    sql += """
        LIMIT 1
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            sql,
            params,
        )

        return cursor.fetchone()


# ==========================================================
# FIND DUPLICATES
# ==========================================================


def find_duplicates() -> list[dict]:
    """
    Return all duplicate songs grouped by
    artist and title.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                artist_id,
                LOWER(TRIM(title)) AS normalized_title,
                COUNT(*) AS total
            FROM songs
            GROUP BY
                artist_id,
                LOWER(TRIM(title))
            HAVING COUNT(*) > 1
            ORDER BY
                total DESC,
                normalized_title
            """
        )

        return cursor.fetchall()