"""
Channel Filter Repository
"""

from psycopg2 import sql


class ChannelFilterRepository:
    SORTABLE_COLUMNS = {
        "id": "c.id",
        "name": "c.name",
        "email": "c.email",
        "created_at": "c.created_at",
        "updated_at": "c.updated_at",
        "artists": "total_artists",
        "songs": "total_songs",
    }

    @classmethod
    def apply(
        cls,
        cursor,
        *,
        keyword: str | None = None,
        vermuk: bool | None = None,
        order_by: str = "created_at",
        order_dir: str = "desc",
        start: int = 0,
        length: int = 20,
    ):
        where = []
        params = {}

        if keyword:
            where.append("""
                (
                    c.name ILIKE %(keyword)s
                    OR c.email ILIKE %(keyword)s
                    OR COALESCE(c.notes,'') ILIKE %(keyword)s
                )
            """)
            params["keyword"] = f"%{keyword}%"

        if vermuk is not None:
            where.append("c.vermuk = %(vermuk)s")
            params["vermuk"] = vermuk

        where_sql = ""
        if where:
            where_sql = "WHERE " + " AND ".join(where)

        order_column = cls.SORTABLE_COLUMNS.get(
            order_by,
            "c.created_at"
        )

        order_direction = (
            "ASC"
            if str(order_dir).lower() == "asc"
            else "DESC"
        )

        query = f"""
        SELECT
            c.id,
            c.name,
            c.email,
            c.vermuk,
            c.notes,
            c.created_at,
            c.updated_at,

            COUNT(DISTINCT a.id) AS total_artists,
            COUNT(s.id)          AS total_songs

        FROM channels c

        LEFT JOIN artists a
            ON a.channel_id = c.id

        LEFT JOIN songs s
            ON s.artist_id = a.id

        {where_sql}

        GROUP BY c.id

        ORDER BY {order_column} {order_direction}

        LIMIT %(limit)s
        OFFSET %(offset)s
        """

        params["limit"] = length
        params["offset"] = start

        cursor.execute(query, params)

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    @staticmethod
    def count_filtered(
        cursor,
        *,
        keyword: str | None = None,
        vermuk: bool | None = None,
    ) -> int:

        where = []
        params = {}

        if keyword:
            where.append("""
                (
                    name ILIKE %(keyword)s
                    OR email ILIKE %(keyword)s
                    OR COALESCE(notes,'') ILIKE %(keyword)s
                )
            """)
            params["keyword"] = f"%{keyword}%"

        if vermuk is not None:
            where.append("vermuk = %(vermuk)s")
            params["vermuk"] = vermuk

        where_sql = ""
        if where:
            where_sql = "WHERE " + " AND ".join(where)

        query = f"""
        SELECT COUNT(*)
        FROM channels
        {where_sql}
        """

        cursor.execute(query, params)

        row = cursor.fetchone()

        return row[0] if row else 0