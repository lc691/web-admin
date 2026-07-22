"""
Artist Repository
"""

from typing import Any


class ArtistRepository:
    """
    Repository utama untuk tabel artists.
    """

    # =====================================================
    # READ
    # =====================================================

    @staticmethod
    def get_by_id(cursor, artist_id: int):
        cursor.execute(
            """
            SELECT
                a.id,
                a.channel_id,
                c.name AS channel_name,
                a.name,
                a.created_at,
                a.updated_at,
                COUNT(s.id) AS song_count
            FROM artists a
            INNER JOIN channels c
                ON c.id = a.channel_id
            LEFT JOIN songs s
                ON s.artist_id = a.id
            WHERE a.id = %s
            GROUP BY
                a.id,
                a.channel_id,
                c.name,
                a.name,
                a.created_at,
                a.updated_at
            """,
            (artist_id,),
        )
        return cursor.fetchone()

    @staticmethod
    def get_detail(cursor, artist_id: int):
        """
        Alias untuk halaman detail artist.
        """
        return ArtistRepository.get_by_id(cursor, artist_id)

    @staticmethod
    def get_all(cursor):
        cursor.execute(
            """
            SELECT
                a.id,
                a.channel_id,
                c.name AS channel_name,
                a.name,
                COUNT(s.id) AS song_count,
                a.created_at,
                a.updated_at
            FROM artists a
            INNER JOIN channels c
                ON c.id = a.channel_id
            LEFT JOIN songs s
                ON s.artist_id = a.id
            GROUP BY
                a.id,
                a.channel_id,
                c.name,
                a.name,
                a.created_at,
                a.updated_at
            ORDER BY
                LOWER(a.name)
            """
        )
        return cursor.fetchall()

    @staticmethod
    def exists(cursor, artist_id: int) -> bool:
        cursor.execute(
            """
            SELECT 1
            FROM artists
            WHERE id = %s
            LIMIT 1
            """,
            (artist_id,),
        )
        return cursor.fetchone() is not None

    @staticmethod
    def get_by_name(cursor, channel_id: int, name: str):
        cursor.execute(
            """
            SELECT
                id,
                channel_id,
                name
            FROM artists
            WHERE channel_id = %s
              AND LOWER(TRIM(name)) = LOWER(TRIM(%s))
            LIMIT 1
            """,
            (channel_id, name),
        )
        return cursor.fetchone()

    @staticmethod
    def exists_by_name(
        cursor,
        channel_id: int,
        name: str,
        exclude_id: int | None = None,
    ) -> bool:

        sql = """
            SELECT 1
            FROM artists
            WHERE channel_id = %s
              AND LOWER(TRIM(name)) = LOWER(TRIM(%s))
        """

        params: list[Any] = [channel_id, name]

        if exclude_id is not None:
            sql += " AND id <> %s"
            params.append(exclude_id)

        sql += " LIMIT 1"

        cursor.execute(sql, params)
        return cursor.fetchone() is not None

    @staticmethod
    def get_channels(cursor):
        """
        Digunakan untuk dropdown form artist.
        """
        cursor.execute(
            """
            SELECT
                id,
                name
            FROM channels
            ORDER BY LOWER(name)
            """
        )
        return cursor.fetchall()

    # =====================================================
    # CREATE
    # =====================================================

    @staticmethod
    def create(
        cursor,
        channel_id: int,
        name: str,
    ):
        cursor.execute(
            """
            INSERT INTO artists
            (
                channel_id,
                name
            )
            VALUES
            (
                %s,
                %s
            )
            RETURNING id
            """,
            (
                channel_id,
                name,
            ),
        )

        return cursor.fetchone()["id"]

    # =====================================================
    # UPDATE
    # =====================================================

    @staticmethod
    def update(
        cursor,
        artist_id: int,
        channel_id: int,
        name: str,
    ):
        cursor.execute(
            """
            UPDATE artists
            SET
                channel_id = %s,
                name = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (
                channel_id,
                name,
                artist_id,
            ),
        )

        return cursor.rowcount > 0

    # =====================================================
    # DELETE
    # =====================================================

    @staticmethod
    def delete(cursor, artist_id: int):
        cursor.execute(
            """
            DELETE
            FROM artists
            WHERE id = %s
            """,
            (artist_id,),
        )

        return cursor.rowcount > 0


    @staticmethod
    def total_songs(cursor, artist_id: int):
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM songs
            WHERE artist_id = %s
            """,
            (artist_id,),
        )

        return cursor.fetchone()["total"]