"""
Export Songs Repository
=======================

Repository khusus query lagu untuk proses export.

Business rules tidak ditulis di repository.
Repository hanya bertanggung jawab menjalankan query PostgreSQL.
"""

from __future__ import annotations

from typing import Any

from app.core.database import get_dict_cursor

from .types import (
    ExportMode,
    SongRow,
)

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
    Return available songs for export.

    Mode:
        normal     -> semua lagu live
        clean      -> live tanpa channel blacklist
        blacklist  -> hanya channel blacklist
    """

    conditions = [
        "s.status = 'live'",
        "u.song_id IS NULL",
    ]

    params: list[Any] = [mode]

    if mode == "clean":
        conditions.append("cb.channel_id IS NULL")

    elif mode == "blacklist":
        conditions.append("cb.channel_id IS NOT NULL")

    if include_channel_ids:
        placeholders = ",".join(["%s"] * len(include_channel_ids))
        conditions.append(f"c.id IN ({placeholders})")
        params.extend(include_channel_ids)

    if exclude_channel_ids:
        placeholders = ",".join(["%s"] * len(exclude_channel_ids))
        conditions.append(f"c.id NOT IN ({placeholders})")
        params.extend(exclude_channel_ids)

    sql = f"""
        SELECT
            s.id,
            s.title,
            a.name AS artist,
            c.id AS channel_id,
            c.name AS channel
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
        WHERE {" AND ".join(conditions)}
        ORDER BY RANDOM()
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(sql, params)
        return cursor.fetchall()


# ==========================================================
# EXPORTED SONGS
# ==========================================================


def get_exported_songs(
    batch_id: int,
) -> list[SongRow]:
    """
    Return exported songs from a batch.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                s.id,
                s.title,
                a.name AS artist,
                c.id AS channel_id,
                c.name AS channel
            FROM song_export_batch_items bi
            JOIN songs s
                ON bi.song_id = s.id
            JOIN artists a
                ON s.artist_id = a.id
            JOIN channels c
                ON a.channel_id = c.id
            WHERE
                bi.batch_id = %s
            ORDER BY
                bi.order_index
            """,
            (batch_id,),
        )

        return cursor.fetchall()
