"""
Export Usage Repository
=======================

Repository untuk pengelolaan song_usage.

Repository hanya bertanggung jawab menjalankan query PostgreSQL.
"""

from __future__ import annotations

from app.core.database import get_dict_cursor

from .types import (
    ExportMode,
    SongRow,
)

# ==========================================================
# SAVE SONG USAGE
# ==========================================================


def save_song_usage(
    songs: list[SongRow],
    mode: ExportMode,
    day: int,
) -> None:
    """
    Save exported songs into song_usage.
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
# RESET SONG USAGE
# ==========================================================


def reset_song_usage(
    mode: ExportMode,
) -> None:
    """
    Reset song usage for a specific export mode.
    """

    with get_dict_cursor() as (cursor, conn):
        cursor.execute(
            """
            DELETE
            FROM song_usage
            WHERE mode = %s
            """,
            (mode,),
        )

        conn.commit()