"""
Songs Bulk Repository
=====================

Repository untuk operasi massal pada Songs.

Repository hanya bertanggung jawab menjalankan
query PostgreSQL.
"""

from __future__ import annotations

from app.core.database import get_dict_cursor

from .types import SongStatus

# ==========================================================
# BULK UPDATE STATUS
# ==========================================================


def bulk_update_status(
    song_ids: list[int],
    status: SongStatus,
) -> int:
    """
    Update status for multiple songs.

    Returns:
        Number of affected rows.
    """

    if not song_ids:
        return 0

    with get_dict_cursor() as (cursor, conn):
        cursor.execute(
            """
            UPDATE songs
            SET
                status = %s,
                updated_at = NOW()
            WHERE
                id = ANY(%s)
            """,
            (
                status,
                song_ids,
            ),
        )

        affected = cursor.rowcount

        conn.commit()

        return affected


# ==========================================================
# BULK DELETE
# ==========================================================


def bulk_delete(
    song_ids: list[int],
) -> int:
    """
    Delete multiple songs.

    Returns:
        Number of affected rows.
    """

    if not song_ids:
        return 0

    with get_dict_cursor() as (cursor, conn):
        cursor.execute(
            """
            DELETE
            FROM songs
            WHERE
                id = ANY(%s)
            """,
            (song_ids,),
        )

        affected = cursor.rowcount

        conn.commit()

        return affected


# ==========================================================
# BULK UPDATE ARTIST
# ==========================================================


def bulk_update_artist(
    song_ids: list[int],
    artist_id: int,
) -> int:
    """
    Move multiple songs to another artist.

    Returns:
        Number of affected rows.
    """

    if not song_ids:
        return 0

    with get_dict_cursor() as (cursor, conn):
        cursor.execute(
            """
            UPDATE songs
            SET
                artist_id = %s,
                updated_at = NOW()
            WHERE
                id = ANY(%s)
            """,
            (
                artist_id,
                song_ids,
            ),
        )

        affected = cursor.rowcount

        conn.commit()

        return affected


# ==========================================================
# BULK UPDATE RELEASE DATE
# ==========================================================


def bulk_update_release_date(
    song_ids: list[int],
    release_date,
) -> int:
    """
    Update release date for multiple songs.

    Returns:
        Number of affected rows.
    """

    if not song_ids:
        return 0

    with get_dict_cursor() as (cursor, conn):
        cursor.execute(
            """
            UPDATE songs
            SET
                release_date = %s,
                updated_at = NOW()
            WHERE
                id = ANY(%s)
            """,
            (
                release_date,
                song_ids,
            ),
        )

        affected = cursor.rowcount

        conn.commit()

        return affected
