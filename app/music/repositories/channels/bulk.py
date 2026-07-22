"""
Channel Bulk Repository
"""

from typing import List
from psycopg2.extras import execute_values


class ChannelBulkRepository:
    def __init__(self, cursor):
        self.cursor = cursor

    # =====================================================
    # BULK DELETE
    # =====================================================

    def delete_songs(self, channel_ids: List[int]) -> None:
        """Delete all songs for given channel IDs."""
        if not channel_ids:
            return
            
        self.cursor.execute(
            """
            DELETE FROM songs
            WHERE artist_id IN (
                SELECT id
                FROM artists
                WHERE channel_id = ANY(%s)
            )
            """,
            (channel_ids,),
        )

    def delete_artists(self, channel_ids: List[int]) -> None:
        """Delete all artists for given channel IDs."""
        if not channel_ids:
            return
            
        self.cursor.execute(
            """
            DELETE FROM artists
            WHERE channel_id = ANY(%s)
            """,
            (channel_ids,),
        )

    def delete_channels(self, channel_ids: List[int]) -> None:
        """Delete channels by IDs."""
        if not channel_ids:
            return
            
        self.cursor.execute(
            """
            DELETE FROM channels
            WHERE id = ANY(%s)
            """,
            (channel_ids,),
        )

    # =====================================================
    # BULK EXISTS
    # =====================================================

    def count_existing(self, channel_ids: List[int]) -> int:
        """Count how many of the given IDs exist."""
        if not channel_ids:
            return 0
            
        self.cursor.execute(
            """
            SELECT COUNT(*) as count
            FROM channels
            WHERE id = ANY(%s)
            """,
            (channel_ids,),
        )

        result = self.cursor.fetchone()
        return result["count"] if result else 0

    def get_existing_ids(self, channel_ids: List[int]) -> List[int]:
        """Get list of existing channel IDs."""
        if not channel_ids:
            return []
            
        self.cursor.execute(
            """
            SELECT id
            FROM channels
            WHERE id = ANY(%s)
            """,
            (channel_ids,),
        )

        return [row["id"] for row in self.cursor.fetchall()]

    # =====================================================
    # BULK UPDATE
    # =====================================================

    def bulk_update_youtube(self, updates: List[tuple]) -> None:
        """
        Bulk update YouTube URLs.
        updates: List of (youtube_url, id) tuples
        """
        if not updates:
            return

        execute_values(
            self.cursor,
            """
            UPDATE channels
            SET youtube_url = data.youtube_url
            FROM (VALUES %s) AS data(youtube_url, id)
            WHERE channels.id = data.id
            """,
            updates,
        )