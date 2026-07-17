"""
Usage Delete Repository
=======================

Repository untuk menghapus export batch beserta
seluruh data yang berhubungan.
"""

from __future__ import annotations

from app.core.database import get_db_connection

from .types import (
    UsageMode,
)

# ==========================================================
# DELETE BATCH
# ==========================================================


def delete_batch(
    *,
    day: int,
    mode: UsageMode,
) -> bool:
    """
    Delete export batch and all related records.
    """

    with get_db_connection() as conn:

        with conn.cursor() as cursor:

            # ==============================================
            # Get Batch
            # ==============================================

            cursor.execute(
                """
                SELECT
                    id
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

            if row is None:

                return False

            batch_id = row[0]

            # ==============================================
            # Delete Batch Items
            # ==============================================

            cursor.execute(
                """
                DELETE FROM
                    song_export_batch_items
                WHERE
                    batch_id = %s
                """,
                (
                    batch_id,
                ),
            )

            # ==============================================
            # Delete Usage
            # ==============================================

            cursor.execute(
                """
                DELETE FROM
                    song_usage
                WHERE
                    day = %s
                    AND mode = %s
                """,
                (
                    day,
                    mode,
                ),
            )

            # ==============================================
            # Delete Batch
            # ==============================================

            cursor.execute(
                """
                DELETE FROM
                    song_export_batches
                WHERE
                    id = %s
                """,
                (
                    batch_id,
                ),
            )

        conn.commit()

    return True