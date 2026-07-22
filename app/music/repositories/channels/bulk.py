"""
Channel Bulk Repository
"""

from typing import Sequence


class ChannelBulkRepository:
    """
    Repository untuk operasi bulk pada Channel.
    """

    @staticmethod
    def bulk_delete(cursor, ids: Sequence[int]) -> int:
        """
        Menghapus banyak channel sekaligus.

        Returns:
            Jumlah data yang terhapus.
        """
        if not ids:
            return 0

        cursor.execute("""
            DELETE FROM channels
            WHERE id = ANY(%s)
        """, (list(ids),))

        return cursor.rowcount

    @staticmethod
    def bulk_update_vermuk(
        cursor,
        ids: Sequence[int],
        vermuk: bool,
    ) -> int:
        """
        Update status vermuk beberapa channel.

        Returns:
            Jumlah data yang diupdate.
        """
        if not ids:
            return 0

        cursor.execute("""
            UPDATE channels
            SET
                vermuk = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ANY(%s)
        """, (
            vermuk,
            list(ids),
        ))

        return cursor.rowcount

    @staticmethod
    def bulk_exists(cursor, ids: Sequence[int]) -> list[int]:
        """
        Mengembalikan daftar ID yang benar-benar ada di database.
        """
        if not ids:
            return []

        cursor.execute("""
            SELECT id
            FROM channels
            WHERE id = ANY(%s)
            ORDER BY id
        """, (list(ids),))

        return [row[0] for row in cursor.fetchall()]