"""
Channel Filter Repository
"""

from typing import Optional, List, Dict, Any, Tuple


class ChannelFilterRepository:
    def __init__(self, cursor):
        self.cursor = cursor

    # =====================================================
    # PRIVATE
    # =====================================================

    def _build_where(
        self,
        keyword: Optional[str],
        has_youtube: Optional[bool],
    ) -> Tuple[str, List[Any]]:
        where = []
        params: List[Any] = []

        if keyword:
            keyword = f"%{keyword.strip()}%"
            where.append(
                "(c.name ILIKE %s OR c.youtube_url ILIKE %s)"
            )
            params.extend([keyword, keyword])

        if has_youtube is True:
            where.append(
                "c.youtube_url IS NOT NULL AND c.youtube_url <> ''"
            )

        elif has_youtube is False:
            where.append(
                "(c.youtube_url IS NULL OR c.youtube_url = '')"
            )

        if where:
            return "WHERE " + " AND ".join(where), params

        return "", params

    def _build_having(
        self,
        has_artists: Optional[bool],
        has_songs: Optional[bool],
    ) -> str:
        having = []

        if has_artists is True:
            having.append("COUNT(DISTINCT a.id) > 0")
        elif has_artists is False:
            having.append("COUNT(DISTINCT a.id) = 0")

        if has_songs is True:
            having.append("COUNT(s.id) > 0")
        elif has_songs is False:
            having.append("COUNT(s.id) = 0")

        if having:
            return "HAVING " + " AND ".join(having)

        return ""

    # =====================================================
    # FILTER
    # =====================================================

    def apply(
        self,
        keyword: Optional[str] = None,
        has_youtube: Optional[bool] = None,
        has_artists: Optional[bool] = None,
        has_songs: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:

        where_sql, params = self._build_where(
            keyword,
            has_youtube,
        )

        having_sql = self._build_having(
            has_artists,
            has_songs,
        )

        query = f"""
            SELECT
                c.id,
                c.name,
                c.youtube_url,
                c.created_at,

                COUNT(DISTINCT a.id) AS total_artists,
                COUNT(s.id) AS total_songs,

                COUNT(*) FILTER (
                    WHERE s.status = 'Released'
                ) AS released_songs,

                COUNT(*) FILTER (
                    WHERE s.status = 'Review'
                ) AS review_songs,

                COUNT(*) FILTER (
                    WHERE s.status = 'Rejected'
                ) AS rejected_songs

            FROM channels c

            LEFT JOIN artists a
                ON a.channel_id = c.id

            LEFT JOIN songs s
                ON s.artist_id = a.id

            {where_sql}

            GROUP BY
                c.id,
                c.name,
                c.youtube_url,
                c.created_at

            {having_sql}

            ORDER BY
                c.name ASC
        """

        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)

        if offset is not None:
            query += " OFFSET %s"
            params.append(offset)

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    # =====================================================
    # COUNT
    # =====================================================

    def count_filtered(
        self,
        keyword: Optional[str] = None,
        has_youtube: Optional[bool] = None,
        has_artists: Optional[bool] = None,
        has_songs: Optional[bool] = None,
    ) -> int:

        where_sql, params = self._build_where(
            keyword,
            has_youtube,
        )

        having_sql = self._build_having(
            has_artists,
            has_songs,
        )

        query = f"""
            SELECT COUNT(*)
            FROM (

                SELECT
                    c.id

                FROM channels c

                LEFT JOIN artists a
                    ON a.channel_id = c.id

                LEFT JOIN songs s
                    ON s.artist_id = a.id

                {where_sql}

                GROUP BY c.id

                {having_sql}

            ) AS filtered
        """

        self.cursor.execute(query, params)

        result = self.cursor.fetchone()
        return result["count"] if result else 0