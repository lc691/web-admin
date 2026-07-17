"""
Repository export.

Seluruh query PostgreSQL berada di file ini.
"""

from typing import Any

from app.core.database import get_dict_cursor

from .types import (
    ExportInformation,
    ExportMode,
    SongRow,
)

# ==========================================================
# EXPORT EXISTENCE
# ==========================================================


def day_export_exists(
    day: int,
    mode: ExportMode,
) -> bool:
    """
    Mengecek apakah export sudah pernah dilakukan.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM song_usage
                WHERE day=%s
                  AND mode=%s
            ) AS exists
            """,
            (day, mode),
        )

        return cursor.fetchone()["exists"]


# ==========================================================
# EXISTING EXPORT
# ==========================================================


def get_existing_export(
    day: int,
    mode: ExportMode,
) -> list[SongRow]:
    """
    Mengambil playlist yang sudah pernah diexport.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                s.id,
                s.title,
                a.name  AS artist,
                c.id    AS channel_id,
                c.name  AS channel
            FROM song_usage u
            JOIN songs s
                ON u.song_id=s.id
            JOIN artists a
                ON s.artist_id=a.id
            JOIN channels c
                ON a.channel_id=c.id
            WHERE
                u.day=%s
                AND u.mode=%s
                AND s.status='Live'
            ORDER BY u.id
            """,
            (day, mode),
        )

        return cursor.fetchall()


# ==========================================================
# AVAILABLE SONGS
# ==========================================================


def get_available_songs(
    *,
    mode: ExportMode,
    include_channel_ids: list[int] | None = None,
    exclude_channel_ids: list[int] | None = None,
) -> list[SongRow]:
    """
    Mengambil lagu Live yang belum pernah dipakai.
    """

    where = [
        "u.song_id IS NULL",
        "s.status='Live'",
    ]

    params: list[Any] = [mode]

    if include_channel_ids:
        placeholders = ",".join(["%s"] * len(include_channel_ids))
        where.append(f"c.id IN ({placeholders})")
        params.extend(include_channel_ids)

    if exclude_channel_ids:
        placeholders = ",".join(["%s"] * len(exclude_channel_ids))
        where.append(f"c.id NOT IN ({placeholders})")
        params.extend(exclude_channel_ids)

    sql = f"""
        SELECT
            s.id,
            s.title,
            a.name  AS artist,
            c.id    AS channel_id,
            c.name  AS channel
        FROM songs s
        JOIN artists a
            ON s.artist_id=a.id
        JOIN channels c
            ON a.channel_id=c.id
        LEFT JOIN song_usage u
            ON s.id=u.song_id
           AND u.mode=%s
        WHERE {' AND '.join(where)}
        ORDER BY RANDOM()
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(sql, params)
        return cursor.fetchall()


# ==========================================================
# SAVE USAGE
# ==========================================================


def save_song_usage(
    songs: list[SongRow],
    day: int,
    mode: ExportMode,
) -> None:
    """
    Menyimpan song_usage.
    """

    if not songs:
        return

    values = [
        (
            song["id"],
            day,
            mode,
        )
        for song in songs
    ]

    with get_dict_cursor() as (cursor, conn):
        cursor.executemany(
            """
            INSERT INTO song_usage
            (
                song_id,
                day,
                mode
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            values,
        )

        conn.commit()


# ==========================================================
# REMAINING SONG
# ==========================================================


def get_remaining_song_count(
    mode: ExportMode,
) -> int:
    """
    Jumlah lagu yang belum pernah dipakai.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM songs s
            LEFT JOIN song_usage u
                ON s.id=u.song_id
               AND u.mode=%s
            WHERE
                s.status='Live'
                AND u.song_id IS NULL
            """,
            (mode,),
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
    Statistik export.
    """

    remaining = get_remaining_song_count(mode)

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM song_usage
            WHERE day=%s
              AND mode=%s
            """,
            (day, mode),
        )

        unique = cursor.fetchone()["total"]

    return {
        "remaining": remaining,
        "already_exported": unique > 0,
        "unique_songs": unique,
        "total_available": remaining,
        "day": day,
        "mode": mode,
    }


# ==========================================================
# SAVE EXPORT BATCH
# ==========================================================


def save_export_batch(
    day: int,
    target: int,
    duplicate: int,
    max_song_per_channel: int,
    excluded_channels: list[int],
    songs: list[SongRow],
) -> int:
    """
    Menyimpan metadata export.
    """

    with get_dict_cursor() as (cursor, conn):

        cursor.execute(
            """
            INSERT INTO song_export_batches
            (
                day,
                duplicate_count,
                target_count,
                max_song_per_channel,
                excluded_channels,
                created_at
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                NOW()
            )
            RETURNING id
            """,
            (
                day,
                duplicate,
                target,
                max_song_per_channel,
                excluded_channels,
            ),
        )

        batch_id = cursor.fetchone()["id"]

        values = [
            (
                batch_id,
                song["id"],
                index,
            )
            for index, song in enumerate(songs)
        ]

        cursor.executemany(
            """
            INSERT INTO song_export_batch_items
            (
                batch_id,
                song_id,
                order_index
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            values,
        )

        conn.commit()

        return batch_id