"""
Usage Batch Repository
======================

Repository untuk metadata export batch.
"""

from __future__ import annotations

from app.core.database import get_dict_cursor

from .types import (
    UsageBatch,
    UsageMode,
)

# ==========================================================
# GET BATCH
# ==========================================================


def get_batch(
    *,
    day: int,
    mode: UsageMode,
) -> UsageBatch | None:
    """
    Return export batch by day.
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
                selected_unique,
                channel_limit,
                created_at,
                completed_at
            FROM song_export_batches
            WHERE
                day = %s
                AND mode = %s
            LIMIT 1
            """,
            (
                day,
                mode,
            ),
        )

        row = cursor.fetchone()

        return dict(row) if row else None


# ==========================================================
# GET BATCHS
# ==========================================================


def get_batches(
    *,
    mode: UsageMode,
) -> list[UsageBatch]:
    """
    Return all export batches.
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
                selected_unique,
                channel_limit,
                created_at,
                completed_at
            FROM song_export_batches
            WHERE
                mode = %s
            ORDER BY
                day
            """,
            (
                mode,
            ),
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]