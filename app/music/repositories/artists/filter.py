"""
Artist Filter Repository - Complete Implementation

Repository untuk filtering dan pencarian Artist dengan:
- DataTable support
- Advanced filtering
- Multi-column sorting
- Search with relevance
- Filter by channel, status, date range
- Pagination
"""

from typing import Any, List, Dict, Optional, Tuple
from datetime import datetime

from app.music.constants.status import VALID_STATUS
from app.music.services.artists.exceptions import (
    InvalidArtistStatusError,
)

import logging

logger = logging.getLogger(__name__)


class ArtistFilterRepository:
    """
    Repository untuk filtering Artist.
    """

    # =====================================================
    # CONSTANTS
    # =====================================================

    SORTABLE_COLUMNS = {
        0: "a.id",              # checkbox (tidak dipakai)
        1: "LOWER(a.name)",     # Artist
        2: "channel_name",      # Channel
        3: "song_count",        # Status (sorting berdasarkan jumlah lagu)
        4: "song_count",        # Songs
        5: "uploaded_songs",    # Progress
        6: "last_song_date",    # Last Song
        7: "a.updated_at",      # Updated
        8: "a.id",              # Actions (dummy)
    }

    SORTABLE_COLUMNS_NAMED = {
        "id": "a.id",
        "name": "LOWER(a.name)",
        "channel": "channel_name",
        "song_count": "song_count",
        "uploaded_songs": "uploaded_songs",
        "pending_songs": "pending_songs",
        "created_at": "a.created_at",
        "updated_at": "a.updated_at",
    }

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
        channel_id: Optional[int] = None,
        has_songs: Optional[bool] = None,
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        order_column: int = 1,
        order_dir: str = "desc",
        include_stats: bool = True,
    ) -> Dict[str, Any]:
        """
        DataTables Artist.
        status = Song Status (draft, review, released, dst)
        """

        # =====================================================
        # VALIDASI STATUS LAGU
        # =====================================================

        if status:
            status = status.strip().lower()

            if status not in VALID_STATUS:
                raise InvalidArtistStatusError(
                    status=status,
                    valid_statuses=sorted(VALID_STATUS),
                )

        # =====================================================
        # BASE QUERY
        # =====================================================

        base_query = """
            FROM artists a
            INNER JOIN channels c
                ON c.id = a.channel_id
        """

        if include_stats:
            base_query += """
            LEFT JOIN songs s
                ON s.artist_id = a.id
            
            LEFT JOIN LATERAL (
                SELECT status
                FROM songs sl
                WHERE sl.artist_id = a.id
                ORDER BY
                    COALESCE(sl.updated_at, sl.created_at) DESC,
                    sl.id DESC
                LIMIT 1
            ) last_song ON TRUE
            """

        base_query += """
            WHERE 1=1
        """

        params: List[Any] = []

        # =====================================================
        # FILTER CHANNEL
        # =====================================================

        if channel_id:
            base_query += " AND a.channel_id = %s"
            params.append(channel_id)

        # =====================================================
        # SEARCH
        # =====================================================

        if search:
            keyword = f"%{search.strip()}%"
            base_query += """
                AND (
                    a.name ILIKE %s
                    OR c.name ILIKE %s
                )
            """
            params.extend([keyword, keyword])

        # =====================================================
        # FILTER HAS SONGS
        # =====================================================

        if has_songs is not None:
            if has_songs:
                base_query += """
                    AND EXISTS (
                        SELECT 1
                        FROM songs s2
                        WHERE s2.artist_id = a.id
                    )
                """
            else:
                base_query += """
                    AND NOT EXISTS (
                        SELECT 1
                        FROM songs s2
                        WHERE s2.artist_id = a.id
                    )
                """

        # =====================================================
        # FILTER SONG STATUS
        # =====================================================

        if status:
            base_query += """
                AND EXISTS (
                    SELECT 1
                    FROM songs s2
                    WHERE s2.artist_id = a.id
                    AND s2.status = %s
                )
            """
            params.append(status)

        # =====================================================
        # FILTER DATE
        # =====================================================

        if date_from:
            base_query += " AND a.created_at >= %s"
            params.append(date_from)

        if date_to:
            base_query += " AND a.created_at <= %s"
            params.append(date_to)

        # =====================================================
        # TOTAL FILTERED
        # =====================================================

        cursor.execute(
            f"""
            SELECT COUNT(DISTINCT a.id) AS total
            {base_query}
            """,
            params,
        )

        filtered = cursor.fetchone()["total"]

        # =====================================================
        # ORDER
        # =====================================================

        order_by = ArtistFilterRepository.SORTABLE_COLUMNS.get(
            order_column,
            "LOWER(a.name)",
        )

        direction = "DESC" if order_dir.lower() == "desc" else "ASC"

        # =====================================================
        # SELECT
        # =====================================================

        select_fields = """
            a.id,
            a.channel_id,
            c.name AS channel_name,
            c.vermuk AS channel_vermuk,
            a.name,
            a.created_at,
            a.updated_at
        """

        if include_stats:
            select_fields += """
                ,
                COUNT(DISTINCT s.id) AS song_count,

                COUNT(DISTINCT s.id) FILTER (
                    WHERE s.status IN (
                        'released',
                        'topic',
                        'live',
                        'no_ads'
                    )
                ) AS uploaded_songs,

                COUNT(DISTINCT s.id) FILTER (
                    WHERE s.status IN (
                        'draft',
                        'review',
                        'approved',
                        'scheduled',
                        'unreleased'
                    )
                ) AS pending_songs,

                COUNT(DISTINCT s.id) FILTER (
                    WHERE s.status = 'take_down'
                ) AS takedown_songs,

                last_song.status AS song_status,

                MAX(s.created_at) AS last_song_date
            """

        # =====================================================
        # DATA
        # =====================================================

        cursor.execute(
            f"""
            SELECT
                {select_fields}

            {base_query}

            GROUP BY
                a.id,
                a.channel_id,
                c.name,
                c.vermuk,
                a.name,
                a.created_at,
                a.updated_at,
                last_song.status
                


            ORDER BY
                {order_by} {direction}

            LIMIT %s
            OFFSET %s
            """,
            params + [length, start],
        )

        rows = cursor.fetchall()

        if rows:
            print(rows[0].keys())
            print(dict(rows[0]))

        # =====================================================
        # TOTAL
        # =====================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM artists
        """)

        total = cursor.fetchone()["total"]

        return {
            "recordsTotal": total,
            "recordsFiltered": filtered,
            "rows": rows,
        }

    # =====================================================
    # ADVANCED FILTER
    # =====================================================

    @staticmethod
    def filter(
        cursor,
        *,
        keyword: Optional[str] = None,
        channel_id: Optional[int] = None,
        has_songs: Optional[bool] = None,
        status: Optional[str] = None,
        min_songs: Optional[int] = None,
        max_songs: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        order_by: str = "name",
        order_dir: str = "asc",
        start: int = 0,
        length: int = 20,
    ) -> Dict[str, Any]:
        """
        Advanced filter for artists.
        
        Args:
            keyword: Search keyword
            channel_id: Filter by channel
            has_songs: Filter by songs existence
            status: Filter by song status
            min_songs: Minimum songs
            max_songs: Maximum songs
            date_from: Creation date from
            date_to: Creation date to
            order_by: Sort column
            order_dir: Sort direction
            start: Pagination offset
            length: Pagination limit
            
        Returns:
            Dict with data and metadata
        """
        # Build base query
        query = """
            SELECT
                a.id,
                a.channel_id,
                c.name AS channel_name,
                a.name,
                COUNT(DISTINCT s.id) AS song_count,
                COUNT(DISTINCT s.id) FILTER (
                    WHERE s.status IN ('released', 'topic', 'live', 'no_ads')
                ) AS uploaded_songs,
                a.created_at,
                a.updated_at
            FROM artists a
            INNER JOIN channels c ON c.id = a.channel_id
            LEFT JOIN songs s ON s.artist_id = a.id
            WHERE 1=1
        """
        params: List[Any] = []

        # Keyword search
        if keyword:
            keyword_pattern = f"%{keyword.strip()}%"
            query += """
                AND (a.name ILIKE %s OR c.name ILIKE %s)
            """
            params.extend([keyword_pattern, keyword_pattern])

        # Channel filter
        if channel_id:
            query += " AND a.channel_id = %s"
            params.append(channel_id)

        # Has songs filter
        if has_songs is not None:
            if has_songs:
                query += " AND EXISTS (SELECT 1 FROM songs s2 WHERE s2.artist_id = a.id)"
            else:
                query += " AND NOT EXISTS (SELECT 1 FROM songs s2 WHERE s2.artist_id = a.id)"

        # Status filter
        if status:
            query += """
                AND EXISTS (
                    SELECT 1 FROM songs s2
                    WHERE s2.artist_id = a.id AND s2.status = %s
                )
            """
            params.append(status)

        # Date range
        if date_from:
            query += " AND a.created_at >= %s"
            params.append(date_from)
        if date_to:
            query += " AND a.created_at <= %s"
            params.append(date_to)

        query += """
            GROUP BY a.id, a.channel_id, c.name, a.name, a.created_at, a.updated_at
        """

        # Having clauses for min/max songs
        having = []
        if min_songs is not None:
            having.append("COUNT(DISTINCT s.id) >= %s")
            params.append(min_songs)
        if max_songs is not None:
            having.append("COUNT(DISTINCT s.id) <= %s")
            params.append(max_songs)

        if having:
            query += " HAVING " + " AND ".join(having)

        # Order by
        order_column = ArtistFilterRepository.SORTABLE_COLUMNS_NAMED.get(
            order_by, "LOWER(a.name)"
        )
        order_direction = "ASC" if order_dir.lower() == "asc" else "DESC"
        query += f" ORDER BY {order_column} {order_direction}"

        # Count total
        count_query = query.replace(
            "SELECT",
            "SELECT COUNT(*) AS total"
        ).replace(
            "ORDER BY", ""
        ).rsplit("LIMIT", 1)[0] if "LIMIT" in query else query
        
        cursor.execute(count_query, params)
        total = cursor.fetchone()["total"] if cursor.description else 0

        # Pagination
        query += " LIMIT %s OFFSET %s"
        params.extend([length, start])

        cursor.execute(query, params)
        rows = [dict(row) for row in cursor.fetchall()]

        return {
            "data": rows,
            "meta": {
                "total": total,
                "start": start,
                "length": length,
                "page": (start // length) + 1 if length > 0 else 1,
                "total_pages": (total + length - 1) // length if length > 0 else 0,
            }
        }

    # =====================================================
    # SEARCH
    # =====================================================

    @staticmethod
    def search(
        cursor,
        keyword: str,
        channel_id: Optional[int] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Simple search for artists.
        
        Args:
            cursor: Database cursor
            keyword: Search keyword
            channel_id: Optional channel filter
            limit: Max results
            
        Returns:
            List of matching artists
        """
        query = """
            SELECT
                a.id,
                a.name,
                a.channel_id,
                c.name AS channel_name,
                COUNT(s.id) AS song_count
            FROM artists a
            INNER JOIN channels c ON c.id = a.channel_id
            LEFT JOIN songs s ON s.artist_id = a.id
            WHERE a.name ILIKE %s
        """
        params: List[Any] = [f"%{keyword.strip()}%"]

        if channel_id:
            query += " AND a.channel_id = %s"
            params.append(channel_id)

        query += """
            GROUP BY a.id, a.name, a.channel_id, c.name
            ORDER BY LOWER(a.name)
            LIMIT %s
        """
        params.append(limit)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def search_by_channel(
        cursor,
        channel_id: int,
        keyword: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Search artists within a specific channel.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            keyword: Search keyword
            limit: Max results
            
        Returns:
            List of matching artists
        """
        return ArtistFilterRepository.search(
            cursor,
            keyword=keyword,
            channel_id=channel_id,
            limit=limit
        )

    # =====================================================
    # FILTER BY CHANNEL
    # =====================================================

    @staticmethod
    def by_channel(
        cursor,
        channel_id: int,
        limit: int = 100,
        offset: int = 0,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get artists by channel with pagination.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            limit: Max records
            offset: Pagination offset
            search: Search keyword
            
        Returns:
            List of artists
        """
        query = """
            SELECT
                a.id,
                a.name,
                COUNT(s.id) AS song_count,
                COUNT(s.id) FILTER (
                    WHERE s.status IN ('released', 'topic', 'live', 'no_ads')
                ) AS uploaded_songs,
                a.created_at,
                a.updated_at
            FROM artists a
            LEFT JOIN songs s ON s.artist_id = a.id
            WHERE a.channel_id = %s
        """
        params: List[Any] = [channel_id]

        if search:
            query += " AND a.name ILIKE %s"
            params.append(f"%{search.strip()}%")

        query += """
            GROUP BY a.id, a.name, a.created_at, a.updated_at
            ORDER BY LOWER(a.name)
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def by_channel_simple(
        cursor,
        channel_id: int,
    ) -> List[Dict[str, Any]]:
        """
        Get simple list of artists by channel.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            
        Returns:
            List of artists with name and id
        """
        cursor.execute("""
            SELECT
                a.id,
                a.name,
                COUNT(s.id) AS song_count
            FROM artists a
            LEFT JOIN songs s ON s.artist_id = a.id
            WHERE a.channel_id = %s
            GROUP BY a.id, a.name
            ORDER BY LOWER(a.name)
        """, (channel_id,))

        return [dict(row) for row in cursor.fetchall()]

    # =====================================================
    # FILTER WITH STATS
    # =====================================================

    @staticmethod
    def with_stats(
        cursor,
        channel_id: Optional[int] = None,
        min_songs: int = 0,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Get artists with detailed statistics.
        
        Args:
            cursor: Database cursor
            channel_id: Optional channel filter
            min_songs: Minimum songs
            limit: Max records
            
        Returns:
            List of artists with statistics
        """
        query = """
            SELECT
                a.id,
                a.name,
                a.channel_id,
                c.name AS channel_name,
                COUNT(DISTINCT s.id) AS total_songs,
                COUNT(DISTINCT s.id) FILTER (
                    WHERE s.status IN ('released', 'topic', 'live', 'no_ads')
                ) AS uploaded_songs,
                COUNT(DISTINCT s.id) FILTER (
                    WHERE s.status IN ('draft', 'review', 'approved', 'scheduled', 'unreleased')
                ) AS pending_songs,
                COUNT(DISTINCT s.id) FILTER (
                    WHERE s.status = 'take_down'
                ) AS takedown_songs,
                MIN(s.created_at) AS first_song,
                MAX(s.created_at) AS last_song,
                a.created_at,
                a.updated_at
            FROM artists a
            INNER JOIN channels c ON c.id = a.channel_id
            LEFT JOIN songs s ON s.artist_id = a.id
            WHERE 1=1
        """
        params: List[Any] = []

        if channel_id:
            query += " AND a.channel_id = %s"
            params.append(channel_id)

        query += """
            GROUP BY a.id, a.name, a.channel_id, c.name, a.created_at, a.updated_at
            HAVING COUNT(DISTINCT s.id) >= %s
            ORDER BY total_songs DESC
            LIMIT %s
        """
        params.extend([min_songs, limit])

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # =====================================================
    # FILTER OPTIONS
    # =====================================================

    @staticmethod
    def get_filter_options(cursor) -> Dict[str, Any]:
        """
        Get available filter options for UI.
        
        Args:
            cursor: Database cursor
            
        Returns:
            Dict with filter options
        """
        # Get unique channels
        cursor.execute("""
            SELECT
                c.id,
                c.name,
                COUNT(a.id) AS artist_count
            FROM channels c
            LEFT JOIN artists a ON a.channel_id = c.id
            GROUP BY c.id, c.name
            ORDER BY c.name
        """)
        channels = [dict(row) for row in cursor.fetchall()]

        # Get unique statuses
        cursor.execute("""
            SELECT DISTINCT status
            FROM songs
            WHERE status IS NOT NULL
            ORDER BY status
        """)
        statuses = [row['status'] for row in cursor.fetchall()]

        # Get date range
        cursor.execute("""
            SELECT
                MIN(created_at) AS earliest,
                MAX(created_at) AS latest
            FROM artists
        """)
        date_range = dict(cursor.fetchone())

        return {
            "channels": channels,
            "statuses": statuses,
            "date_range": date_range,
            "sortable_columns": list(ArtistFilterRepository.SORTABLE_COLUMNS_NAMED.keys()),
        }

    # =====================================================
    # COUNT HELPERS
    # =====================================================

    @staticmethod
    def count_by_channel(cursor) -> Dict[int, int]:
        """
        Count artists by channel.
        
        Args:
            cursor: Database cursor
            
        Returns:
            Dict mapping channel_id -> count
        """
        cursor.execute("""
            SELECT
                channel_id,
                COUNT(*) AS count
            FROM artists
            GROUP BY channel_id
        """)
        
        return {row['channel_id']: row['count'] for row in cursor.fetchall()}

    @staticmethod
    def count_by_status(cursor) -> Dict[str, int]:
        """
        Count artists by song status (artists that have songs with specific status).
        
        Args:
            cursor: Database cursor
            
        Returns:
            Dict mapping status -> count
        """
        cursor.execute("""
            SELECT
                s.status,
                COUNT(DISTINCT a.id) AS artist_count
            FROM artists a
            INNER JOIN songs s ON s.artist_id = a.id
            GROUP BY s.status
            ORDER BY s.status
        """)
        
        return {row['status']: row['artist_count'] for row in cursor.fetchall()}