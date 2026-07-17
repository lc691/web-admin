"""
Songs Repository
================

Repository untuk operasi CRUD lagu.

Repository hanya bertanggung jawab menjalankan
query PostgreSQL.
"""

from __future__ import annotations

from app.core.database import get_dict_cursor

from .types import (
    CreateSong,
    SongDetail,
    SongRow,
    UpdateSong,
)

# ==========================================================
# GET SONG
# ==========================================================


def get_song(
    song_id: int,
) -> SongDetail | None:
    """
    Return song detail.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                s.id,
                s.title,

                s.artist_id,
                a.name AS artist,

                c.id AS channel_id,
                c.name AS channel,

                s.status,
                s.release_date,

                s.created_at,
                s.updated_at

            FROM songs s

            JOIN artists a
                ON s.artist_id = a.id

            JOIN channels c
                ON a.channel_id = c.id

            WHERE
                s.id = %s
            """,
            (song_id,),
        )

        row = cursor.fetchone()

        print("TYPE =", type(row))
        print("ROW =", row)

        return dict(row)


# ==========================================================
# GET SONG BY ID
# ==========================================================


def get_song_by_id(
    song_id: int,
) -> SongDetail | None:
    """
    Alias of get_song().
    """

    return get_song(song_id)


# ==========================================================
# CREATE SONG
# ==========================================================


def create_song(
    data: CreateSong,
) -> int:
    """
    Create new song.
    """

    with get_dict_cursor() as (cursor, conn):
        cursor.execute(
            """
            INSERT INTO songs
            (
                artist_id,
                title,
                status,
                release_date
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
            RETURNING id
            """,
            (
                data["artist_id"],
                data["title"],
                data["status"],
                data["release_date"],
            ),
        )

        song_id = cursor.fetchone()["id"]

        conn.commit()

        return song_id


# ==========================================================
# UPDATE SONG
# ==========================================================


def update_song(
    song_id: int,
    data: UpdateSong,
) -> None:
    """
    Update song.
    """

    with get_dict_cursor() as (cursor, conn):
        cursor.execute(
            """
            UPDATE songs
            SET
                artist_id = %s,
                title = %s,
                status = %s,
                release_date = %s,
                updated_at = NOW()
            WHERE
                id = %s
            """,
            (
                data["artist_id"],
                data["title"],
                data["status"],
                data["release_date"],
                song_id,
            ),
        )

        conn.commit()


# ==========================================================
# DELETE SONG
# ==========================================================


def delete_song(
    song_id: int,
) -> None:
    """
    Delete song.
    """

    with get_dict_cursor() as (cursor, conn):
        cursor.execute(
            """
            DELETE
            FROM songs
            WHERE id = %s
            """,
            (song_id,),
        )

        conn.commit()


# ==========================================================
# SONG EXISTS
# ==========================================================


def song_exists(
    song_id: int,
) -> bool:
    """
    Return True if song exists.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT EXISTS
            (
                SELECT 1
                FROM songs
                WHERE id = %s
            ) AS exists
            """,
            (song_id,),
        )

        return cursor.fetchone()["exists"]


# ==========================================================
# SONG TITLE EXISTS
# ==========================================================


def song_title_exists(
    *,
    artist_id: int,
    title: str,
    exclude_song_id: int | None = None,
) -> bool:
    """
    Return True if song title already exists
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
        cursor.execute(sql, params)

        return cursor.fetchone()["exists"]
