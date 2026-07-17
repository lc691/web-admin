"""
Usage Reset Repository
======================

Repository untuk menghapus seluruh export batch
berdasarkan mode.
"""

from __future__ import annotations

from app.core.database import get_db_connection

from .types import (
    UsageMode,
)

# ==========================================================
# RESET MODE
# ==========================================================


def reset_mode(
    *,
    mode: UsageMode,
) -> int:
    """
    Delete all export batches for mode.

    Returns:
        Number of deleted batches.
    """

    with get_db_connection() as conn:

        with conn.cursor() as cursor:

            # ==============================================
            # Count
            # ==============================================

            cursor.execute(
                """
                SELECT
                    COUNT(*)
                FROM
                    song_export_batches
                WHERE
                    mode = %s
                """,
                (
                    mode,
                ),
            )

            total = cursor.fetchone()[0]

            if total == 0:

                conn.commit()

                return 0

            # ==============================================
            # Delete Batch Items
            # ==============================================

            cursor.execute(
                """
                DELETE FROM
                    song_export_batch_items
                WHERE
                    batch_id IN (

                        SELECT
                            id
                        FROM
                            song_export_batches
                        WHERE
                            mode = %s

                    )
                """,
                (
                    mode,
                ),
            )

            # ==============================================
            # Delete Song Usage
            # ==============================================

            cursor.execute(
                """
                DELETE FROM
                    song_usage
                WHERE
                    mode = %s
                """,
                (
                    mode,
                ),
            )

            # ==============================================
            # Delete Batches
            # ==============================================

            cursor.execute(
                """
                DELETE FROM
                    song_export_batches
                WHERE
                    mode = %s
                """,
                (
                    mode,
                ),
            )

        conn.commit()

    return total