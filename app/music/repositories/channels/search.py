from typing import Optional


class ChannelSearchRepository:
    def __init__(self, cursor):
        self.cursor = cursor

    def search(
        self,
        keyword: str,
        limit: int = 10,
    ):
        self.cursor.execute(
            """
            SELECT
                id,
                name,
                youtube_url
            FROM channels
            WHERE name ILIKE %s
            ORDER BY name
            LIMIT %s
            """,
            (
                f"%{keyword}%",
                limit,
            ),
        )

        return self.cursor.fetchall()

    def autocomplete(
        self,
        keyword: str,
        limit: int = 20,
    ):
        self.cursor.execute(
            """
            SELECT
                id,
                name
            FROM channels
            WHERE name ILIKE %s
            ORDER BY
                CASE
                    WHEN LOWER(name) = LOWER(%s) THEN 0
                    WHEN LOWER(name) LIKE LOWER(%s) THEN 1
                    ELSE 2
                END,
                name
            LIMIT %s
            """,
            (
                f"%{keyword}%",
                keyword,
                f"{keyword}%",
                limit,
            ),
        )

        return self.cursor.fetchall()

    def by_name(
        self,
        name: str,
    ):
        self.cursor.execute(
            """
            SELECT
                id,
                name,
                youtube_url
            FROM channels
            WHERE LOWER(name) = LOWER(%s)
            LIMIT 1
            """,
            (name,),
        )

        return self.cursor.fetchone()

    def exists(
        self,
        name: str,
        exclude_id: Optional[int] = None,
    ) -> bool:
        query = """
            SELECT 1
            FROM channels
            WHERE LOWER(name) = LOWER(%s)
        """

        params = [name]

        if exclude_id is not None:
            query += " AND id <> %s"
            params.append(exclude_id)

        query += " LIMIT 1"

        self.cursor.execute(query, params)

        return self.cursor.fetchone() is not None