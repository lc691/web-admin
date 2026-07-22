"""
Artist Filter Repository
"""

from typing import Any


class ArtistFilterRepository:
    """
    Repository untuk filtering Artist.
    """

    # =====================================================
    # DATATABLES
    # =====================================================

    @staticmethod
    def datatable(
        cursor,
        *,
        start: int = 0,
        length: int = 10,
        search: str = "",
        channel_id: int | None = None,
        order_column: int = 1,
        order_dir: str = "desc",
    ):
        """
        DataTables Artist
        """

        base_query = """
            FROM artists a
            INNER JOIN channels c
                ON c.id = a.channel_id
            LEFT JOIN songs s
                ON s.artist_id = a.id
            WHERE TRUE
        """

        params: list[Any] = []

        # ==========================================
        # CHANNEL FILTER
        # ==========================================

        if channel_id:
            base_query += """
                AND a.channel_id = %s
            """
            params.append(channel_id)

        # ==========================================
        # SEARCH
        # ==========================================

        if search:
            keyword = f"%{search.strip()}%"

            base_query += """
                AND (
                    a.name ILIKE %s
                    OR c.name ILIKE %s
                )
            """

            params.extend([
                keyword,
                keyword,
            ])

        # ==========================================
        # TOTAL FILTERED
        # ==========================================

        cursor.execute(
            f"""
            SELECT COUNT(DISTINCT a.id) AS total
            {base_query}
            """,
            params,
        )

        filtered = cursor.fetchone()["total"]

        # ==========================================
        # ORDER
        # ==========================================

        order_columns = {
            0: "a.id",
            1: "a.id",
            2: "c.name",
            3: "a.name",
            4: "song_count",
            5: "a.created_at",
        }

        order_by = order_columns.get(order_column, "a.id")

        direction = (
            "DESC"
            if str(order_dir).lower() == "desc"
            else "ASC"
        )

        # ==========================================
        # DATA
        # ==========================================

        cursor.execute(
            f"""
            SELECT
                a.id,
                a.channel_id,
                c.name AS channel_name,
                a.name,
                COUNT(DISTINCT s.id) AS song_count,
                a.created_at,
                a.updated_at

            {base_query}

            GROUP BY
                a.id,
                a.channel_id,
                c.name,
                a.name,
                a.created_at,
                a.updated_at

            ORDER BY
                {order_by} {direction}

            LIMIT %s
            OFFSET %s
            """,
            params + [length, start],
        )

        rows = cursor.fetchall()

        # ==========================================
        # TOTAL
        # ==========================================

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM artists
            """
        )

        total = cursor.fetchone()["total"]

        return {
            "recordsTotal": total,
            "recordsFiltered": filtered,
            "rows": rows,
        }

    # =====================================================
    # SEARCH
    # =====================================================

    @staticmethod
    def search(
        cursor,
        keyword: str,
        limit: int = 20,
    ):
        cursor.execute(
            """
            SELECT
                a.id,
                a.name,
                c.name AS channel_name,
                COUNT(s.id) AS song_count
            FROM artists a
            INNER JOIN channels c
                ON c.id = a.channel_id
            LEFT JOIN songs s
                ON s.artist_id = a.id
            WHERE
                a.name ILIKE %s
            GROUP BY
                a.id,
                a.name,
                c.name
            ORDER BY
                LOWER(a.name)
            LIMIT %s
            """,
            (
                f"%{keyword.strip()}%",
                limit,
            ),
        )

        return cursor.fetchall()

    # =====================================================
    # FILTER CHANNEL
    # =====================================================

    @staticmethod
    def by_channel(
        cursor,
        channel_id: int,
    ):
        cursor.execute(
            """
            SELECT
                a.id,
                a.name,
                COUNT(s.id) AS song_count
            FROM artists a
            LEFT JOIN songs s
                ON s.artist_id = a.id
            WHERE
                a.channel_id = %s
            GROUP BY
                a.id,
                a.name
            ORDER BY
                LOWER(a.name)
            """,
            (channel_id,),
        )

        return cursor.fetchall()