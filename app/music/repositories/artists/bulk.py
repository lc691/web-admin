"""
Artist Bulk Repository
"""

from typing import Any


class ArtistBulkRepository:
    """
    Repository untuk operasi bulk Artist.
    """

    # =====================================================
    # BULK DELETE
    # =====================================================

    @staticmethod
    def bulk_delete(
        cursor,
        artist_ids: list[int],
    ) -> int:
        """
        Hapus banyak artist.
        """

        if not artist_ids:
            return 0

        placeholders = ",".join(["%s"] * len(artist_ids))

        cursor.execute(
            f"""
            DELETE
            FROM artists
            WHERE id IN ({placeholders})
            """,
            artist_ids,
        )

        return cursor.rowcount

    # =====================================================
    # CHECK SONGS
    # =====================================================

    @staticmethod
    def artists_with_songs(
        cursor,
        artist_ids: list[int],
    ):
        """
        Artist yang masih memiliki lagu.
        """

        if not artist_ids:
            return []

        placeholders = ",".join(["%s"] * len(artist_ids))

        cursor.execute(
            f"""
            SELECT
                a.id,
                a.name,
                COUNT(s.id) AS song_count
            FROM artists a
            INNER JOIN songs s
                ON s.artist_id = a.id
            WHERE a.id IN ({placeholders})
            GROUP BY
                a.id,
                a.name
            ORDER BY
                LOWER(a.name)
            """,
            artist_ids,
        )

        return cursor.fetchall()

    # =====================================================
    # EXISTS
    # =====================================================

    @staticmethod
    def existing_ids(
        cursor,
        artist_ids: list[int],
    ) -> list[int]:
        """
        Mengembalikan ID artist yang benar-benar ada.
        """

        if not artist_ids:
            return []

        placeholders = ",".join(["%s"] * len(artist_ids))

        cursor.execute(
            f"""
            SELECT
                id
            FROM artists
            WHERE id IN ({placeholders})
            """,
            artist_ids,
        )

        return [row["id"] for row in cursor.fetchall()]

    # =====================================================
    # TOTAL SONGS
    # =====================================================

    @staticmethod
    def total_songs(
        cursor,
        artist_ids: list[int],
    ) -> int:
        """
        Total lagu dari sekumpulan artist.
        """

        if not artist_ids:
            return 0

        placeholders = ",".join(["%s"] * len(artist_ids))

        cursor.execute(
            f"""
            SELECT
                COUNT(*) AS total
            FROM songs
            WHERE artist_id IN ({placeholders})
            """,
            artist_ids,
        )

        return cursor.fetchone()["total"]

    # =====================================================
    # SUMMARY
    # =====================================================

    @staticmethod
    def summary(
        cursor,
        artist_ids: list[int],
    ):
        """
        Ringkasan artist yang dipilih.
        """

        if not artist_ids:
            return {
                "artists": 0,
                "songs": 0,
            }

        placeholders = ",".join(["%s"] * len(artist_ids))

        cursor.execute(
            f"""
            SELECT
                COUNT(DISTINCT a.id) AS artists,
                COUNT(DISTINCT s.id) AS songs
            FROM artists a
            LEFT JOIN songs s
                ON s.artist_id = a.id
            WHERE a.id IN ({placeholders})
            """,
            artist_ids,
        )

        row = cursor.fetchone()

        return {
            "artists": row["artists"] or 0,
            "songs": row["songs"] or 0,
        }