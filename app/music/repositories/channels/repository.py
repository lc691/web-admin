"""
Channel Repository
"""

from typing import Any


class ChannelRepository:
    """
    Repository utama untuk tabel channels.
    """

    # =====================================================
    # READ
    # =====================================================

    @staticmethod
    def get_by_id(cursor, channel_id: int):
        cursor.execute("""
            SELECT
                c.id,
                c.name,
                c.email,
                c.password,
                c.vermuk,
                c.notes,
                c.created_at,
                c.updated_at,

                COUNT(DISTINCT a.id) AS total_artists,
                COUNT(DISTINCT s.id) AS total_songs,

                COUNT(
                    DISTINCT CASE
                        WHEN s.youtube_url IS NOT NULL
                        THEN s.id
                    END
                ) AS uploaded_songs,

                COUNT(
                    DISTINCT CASE
                        WHEN s.youtube_url IS NULL
                        THEN s.id
                    END
                ) AS pending_songs

            FROM channels c

            LEFT JOIN artists a
                ON a.channel_id = c.id

            LEFT JOIN songs s
                ON s.artist_id = a.id

            WHERE c.id = %s

            GROUP BY
                c.id,
                c.name,
                c.email,
                c.password,
                c.vermuk,
                c.notes,
                c.created_at,
                c.updated_at
        """, (channel_id,))

        row = cursor.fetchone()

        return dict(row) if row else None

    @staticmethod
    def get_by_name(cursor, name: str):
        cursor.execute("""
            SELECT *
            FROM channels
            WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s))
        """, (name,))
        return cursor.fetchone()

    @staticmethod
    def get_by_email(cursor, email: str):
        cursor.execute("""
            SELECT *
            FROM channels
            WHERE email = %s
        """, (email,))
        return cursor.fetchone()

    @staticmethod
    def get_all(cursor):
        cursor.execute("""
            SELECT
                id,
                name,
                email,
                vermuk,
                notes,
                created_at,
                updated_at
            FROM channels
            ORDER BY name
        """)
        return cursor.fetchall()

    # =====================================================
    # CREATE
    # =====================================================

    @staticmethod
    def create(
        cursor,
        *,
        name: str,
        email: str | None = None,
        password: str | None = None,
        vermuk: bool = False,
        notes: str | None = None,
    ):
        cursor.execute("""
            INSERT INTO channels
            (
                name,
                email,
                password,
                vermuk,
                notes
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING id
        """, (
            name,
            email,
            password,
            vermuk,
            notes,
        ))

        return cursor.fetchone()["id"]

    # =====================================================
    # UPDATE
    # =====================================================

    @staticmethod
    def update(
        cursor,
        channel_id: int,
        *,
        name: str,
        email: str | None = None,
        password: str | None = None,
        vermuk: bool = False,
        notes: str | None = None,
    ) -> bool:

        cursor.execute("""
            UPDATE channels
            SET
                name = %s,
                email = %s,
                password = %s,
                vermuk = %s,
                notes = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (
            name,
            email,
            password,
            vermuk,
            notes,
            channel_id,
        ))

        return cursor.rowcount > 0

    # =====================================================
    # DELETE
    # =====================================================

    @staticmethod
    def delete(cursor, channel_id: int) -> bool:
        cursor.execute("""
            DELETE FROM channels
            WHERE id = %s
        """, (channel_id,))

        return cursor.rowcount > 0

    # =====================================================
    # EXISTS
    # =====================================================

    @staticmethod
    def exists(cursor, channel_id: int) -> bool:
        cursor.execute("""
            SELECT EXISTS(
                SELECT 1
                FROM channels
                WHERE id = %s
            )
        """, (channel_id,))

        return cursor.fetchone()[0]

    @staticmethod
    def exists_name(
        cursor,
        name: str,
        exclude_id: int | None = None,
    ) -> bool:

        if exclude_id is None:
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1
                    FROM channels
                    WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s))
                )
            """, (name,))
        else:
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1
                    FROM channels
                    WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s))
                      AND id <> %s
                )
            """, (
                name,
                exclude_id,
            ))

        return cursor.fetchone()[0]

    @staticmethod
    def exists_email(
        cursor,
        email: str,
        exclude_id: int | None = None,
    ) -> bool:

        if exclude_id is None:
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1
                    FROM channels
                    WHERE email = %s
                )
            """, (email,))
        else:
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1
                    FROM channels
                    WHERE email = %s
                      AND id <> %s
                )
            """, (
                email,
                exclude_id,
            ))

        return cursor.fetchone()[0]