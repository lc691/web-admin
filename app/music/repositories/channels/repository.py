from typing import Optional, List, Dict, Any


class ChannelRepository:
    def __init__(self, cursor):
        self.cursor = cursor

    # =====================================================
    # SELECT
    # =====================================================

    def find_all(
        self,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        query = """
            SELECT
                c.id,
                c.name,
                c.youtube_url,
                c.created_at,
                COUNT(DISTINCT a.id) AS total_artists,
                COUNT(s.id) AS total_songs,
                COUNT(CASE WHEN s.status = 'Live' THEN 1 END) AS live_songs,
                COUNT(CASE WHEN s.status = 'Approved' THEN 1 END) AS approved_songs,
                COUNT(CASE WHEN s.status = 'Review' THEN 1 END) AS review_songs,
                COUNT(CASE WHEN s.status = 'Take Down' THEN 1 END) AS takedown_songs,
                COUNT(CASE WHEN s.status = 'Topic' THEN 1 END) AS topic_songs
            FROM channels c
            LEFT JOIN artists a
                ON a.channel_id = c.id
            LEFT JOIN songs s
                ON s.artist_id = a.id
        """

        params = []

        if search:
            query += " WHERE c.name ILIKE %s"
            params.append(f"%{search}%")

        query += """
            GROUP BY
                c.id,
                c.name,
                c.youtube_url,
                c.created_at
            ORDER BY c.created_at DESC
        """

        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)

        if offset is not None:
            query += " OFFSET %s"
            params.append(offset)

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def find_by_id(self, channel_id: int) -> Optional[Dict[str, Any]]:
        self.cursor.execute(
            """
            SELECT
                id,
                name,
                youtube_url,
                created_at
            FROM channels
            WHERE id = %s
            """,
            (channel_id,),
        )
        return self.cursor.fetchone()

    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        self.cursor.execute(
            """
            SELECT
                id,
                name,
                youtube_url
            FROM channels
            WHERE LOWER(name) = LOWER(%s)
            """,
            (name,),
        )
        return self.cursor.fetchone()

    def exists_name(self, name: str, exclude_id: Optional[int] = None) -> bool:
        query = """
            SELECT id
            FROM channels
            WHERE LOWER(name) = LOWER(%s)
        """

        params = [name]

        if exclude_id is not None:
            query += " AND id != %s"
            params.append(exclude_id)

        query += " LIMIT 1"

        self.cursor.execute(query, params)
        return self.cursor.fetchone() is not None

    def get_artists(self, channel_id: int) -> List[Dict[str, Any]]:
        self.cursor.execute(
            """
            SELECT
                a.id,
                a.name,
                COUNT(s.id) AS song_count,
                COUNT(CASE WHEN s.status = 'Live' THEN 1 END) AS live_songs
            FROM artists a
            LEFT JOIN songs s
                ON s.artist_id = a.id
            WHERE a.channel_id = %s
            GROUP BY
                a.id,
                a.name
            ORDER BY a.name
            """,
            (channel_id,),
        )

        return self.cursor.fetchall()

    def get_recent_songs(
        self,
        channel_id: int,
        limit: int = 200
    ) -> List[Dict[str, Any]]:
        self.cursor.execute(
            """
            SELECT
                s.id,
                s.title,
                s.status,
                s.release_date,
                s.created_at,
                a.name AS artist_name
            FROM songs s
            JOIN artists a
                ON a.id = s.artist_id
            WHERE a.channel_id = %s
            ORDER BY s.created_at DESC
            LIMIT %s
            """,
            (channel_id, limit),
        )

        return self.cursor.fetchall()

    # =====================================================
    # INSERT
    # =====================================================

    def create(self, name: str, youtube_url: Optional[str]) -> int:
        self.cursor.execute(
            """
            INSERT INTO channels (
                name,
                youtube_url,
                created_at
            )
            VALUES (
                %s,
                %s,
                CURRENT_TIMESTAMP
            )
            RETURNING id
            """,
            (name, youtube_url),
        )

        return self.cursor.fetchone()["id"]

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        channel_id: int,
        name: str,
        youtube_url: Optional[str],
    ) -> None:
        self.cursor.execute(
            """
            UPDATE channels
            SET
                name = %s,
                youtube_url = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (name, youtube_url, channel_id),
        )

    # =====================================================
    # DELETE
    # =====================================================

    def delete_songs(self, channel_id: int) -> None:
        self.cursor.execute(
            """
            DELETE FROM songs
            WHERE artist_id IN (
                SELECT id
                FROM artists
                WHERE channel_id = %s
            )
            """,
            (channel_id,),
        )

    def delete_artists(self, channel_id: int) -> None:
        self.cursor.execute(
            """
            DELETE FROM artists
            WHERE channel_id = %s
            """,
            (channel_id,),
        )

    def delete(self, channel_id: int) -> None:
        self.cursor.execute(
            """
            DELETE FROM channels
            WHERE id = %s
            """,
            (channel_id,),
        )