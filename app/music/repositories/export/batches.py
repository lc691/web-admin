"""
Export Batch Repository
=======================

Repository untuk pengelolaan export batch.

Repository hanya bertanggung jawab menjalankan query PostgreSQL.
"""

from __future__ import annotations

from app.core.database import get_dict_cursor

from .types import (
    ExportBatch,
    ExportMode,
    SongRow,
)

# ==========================================================
# CREATE BATCH
# ==========================================================


def create_export_batch(
    *,
    day: int,
    mode: ExportMode,
    target: int,
    duplicate: int,
    channel_limit: int,
    selected_unique: int,
    excluded_channels: list[int],
) -> int:
    """
    Create export batch and return batch id.
    """

    with get_dict_cursor() as (cursor, conn):
        cursor.execute(
            """
            INSERT INTO song_export_batches
            (
                day,
                mode,
                target,
                duplicate,
                channel_limit,
                selected_unique,
                excluded_channels
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING id
            """,
            (
                day,
                mode,
                target,
                duplicate,
                channel_limit,
                selected_unique,
                excluded_channels,
            ),
        )

        batch_id = cursor.fetchone()["id"]

        conn.commit()

        return batch_id


# ==========================================================
# CREATE BATCH ITEMS
# ==========================================================


def create_export_batch_items(
    batch_id: int,
    songs: list[SongRow],
) -> None:
    """
    Save exported songs into batch items.
    """

    if not songs:
        return

    rows = [
        (
            batch_id,
            song["id"],
            order_index,
        )
        for order_index, song in enumerate(songs, start=1)
    ]

    with get_dict_cursor() as (cursor, conn):
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
            rows,
        )

        conn.commit()


# ==========================================================
# GET BATCH
# ==========================================================


def get_export_batch(
    batch_id: int,
) -> ExportBatch | None:
    """
    Return export batch by id.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                id,
                day,
                mode,
                target,
                duplicate,
                channel_limit,
                selected_unique,
                excluded_channels,
                status,
                created_at,
                completed_at
            FROM song_export_batches
            WHERE id = %s
            """,
            (batch_id,),
        )

        return cursor.fetchone()


# ==========================================================
# GET BATCH BY DAY
# ==========================================================


def get_export_batch_by_day(
    day: int,
    mode: ExportMode,
) -> ExportBatch | None:
    """
    Return export batch by day and mode.
    """

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT
                id,
                day,
                mode,
                target,
                duplicate,
                channel_limit,
                selected_unique,
                excluded_channels,
                status,
                created_at,
                completed_at
            FROM song_export_batches
            WHERE
                day = %s
                AND mode = %s
            """,
            (
                day,
                mode,
            ),
        )

        return cursor.fetchone()


# ==========================================================
# COMPLETE BATCH
# ==========================================================


def complete_export_batch(
    batch_id: int,
) -> None:
    """
    Mark batch as completed.
    """

    with get_dict_cursor() as (cursor, conn):
        cursor.execute(
            """
            UPDATE song_export_batches
            SET
                status = 'completed',
                completed_at = NOW()
            WHERE id = %s
            """,
            (batch_id,),
        )

        conn.commit()


# ==========================================================
# DELETE BATCH
# ==========================================================


def delete_export_batch(
    batch_id: int,
) -> None:
    """
    Delete export batch.

    Batch items will be deleted automatically
    by ON DELETE CASCADE.
    """

    with get_dict_cursor() as (cursor, conn):
        cursor.execute(
            """
            DELETE
            FROM song_export_batches
            WHERE id = %s
            """,
            (batch_id,),
        )

        conn.commit()