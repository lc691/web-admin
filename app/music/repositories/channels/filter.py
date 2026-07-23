"""
Channel Filter Repository - Complete Implementation

Repository untuk filtering, sorting, dan pagination channels dengan:
- Advanced filtering (keyword, vermuk, date range, etc.)
- Multiple sort options
- Efficient pagination with total count
- Filter presets for common use cases
- Performance optimized queries
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, date
from psycopg2 import sql
import logging

logger = logging.getLogger(__name__)


class ChannelFilterRepository:
    """
    Repository untuk operasi filter, sort, dan pagination pada channels.
    """
    
    # =====================================================
    # CONSTANTS
    # =====================================================
    
    # Columns that can be sorted
    SORTABLE_COLUMNS = {
        "id": "c.id",
        "name": "c.name",
        "email": "c.email",
        "created_at": "c.created_at",
        "updated_at": "c.updated_at",
        "artists": "total_artists",
        "songs": "total_songs",
        "vermuk": "c.vermuk",
        "uploaded_songs": "uploaded_songs",
    }
    
    # Default values
    DEFAULT_SORT = "created_at"
    DEFAULT_DIRECTION = "DESC"
    DEFAULT_LIMIT = 20
    MAX_LIMIT = 1000
    
    # Filter presets
    PRESETS = {
        "recent": {"order_by": "created_at", "order_dir": "desc"},
        "oldest": {"order_by": "created_at", "order_dir": "asc"},
        "most_artists": {"order_by": "artists", "order_dir": "desc"},
        "most_songs": {"order_by": "songs", "order_dir": "desc"},
        "least_active": {"order_by": "songs", "order_dir": "asc"},
        "by_name_asc": {"order_by": "name", "order_dir": "asc"},
        "by_name_desc": {"order_by": "name", "order_dir": "desc"},
    }
    
    # =====================================================
    # MAIN FILTER METHOD
    # =====================================================
    
    @classmethod
    def apply(
        cls,
        cursor,
        *,
        keyword: Optional[str] = None,
        vermuk: Optional[bool] = None,
        email: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        has_artists: Optional[bool] = None,
        has_songs: Optional[bool] = None,
        min_artists: Optional[int] = None,
        max_artists: Optional[int] = None,
        min_songs: Optional[int] = None,
        max_songs: Optional[int] = None,
        order_by: str = DEFAULT_SORT,
        order_dir: str = DEFAULT_DIRECTION,
        start: int = 0,
        length: int = DEFAULT_LIMIT,
        include_stats: bool = True,
    ) -> Dict[str, Any]:
        """
        Apply filters and pagination to channels query.
        
        Args:
            cursor: Database cursor
            keyword: Search keyword (name, email, notes)
            vermuk: Filter by vermuk status
            email: Filter by exact email
            date_from: Filter channels created after this date
            date_to: Filter channels created before this date
            has_artists: Filter channels with/without artists
            has_songs: Filter channels with/without songs
            min_artists: Minimum number of artists
            max_artists: Maximum number of artists
            min_songs: Minimum number of songs
            max_songs: Maximum number of songs
            order_by: Sort column
            order_dir: Sort direction (asc/desc)
            start: Pagination offset
            length: Pagination limit
            include_stats: Include statistics (artists/songs count)
            
        Returns:
            Dict with 'data' (list of channels) and 'meta' (pagination info)
        """
        try:
            # Build WHERE clause
            where = []
            params = {}
            
            # Keyword search
            if keyword:
                where.append("""
                    (
                        c.name ILIKE %(keyword)s
                        OR c.email ILIKE %(keyword)s
                        OR COALESCE(c.notes, '') ILIKE %(keyword)s
                    )
                """)
                params["keyword"] = f"%{keyword}%"
            
            # Vermuk filter
            if vermuk is not None:
                where.append("c.vermuk = %(vermuk)s")
                params["vermuk"] = vermuk
            
            # Email exact match
            if email:
                where.append("c.email = %(email)s")
                params["email"] = email
            
            # Date range
            if date_from:
                where.append("c.created_at >= %(date_from)s")
                params["date_from"] = date_from
            
            if date_to:
                where.append("c.created_at <= %(date_to)s")
                params["date_to"] = date_to
            
            where_sql = " AND ".join(where) if where else "1=1"
            
            # Build ORDER BY
            order_column = cls.SORTABLE_COLUMNS.get(
                order_by,
                cls.SORTABLE_COLUMNS[cls.DEFAULT_SORT]
            )
            
            order_direction = "ASC" if str(order_dir).lower() == "asc" else "DESC"
            
            # Validate limit
            length = min(length, cls.MAX_LIMIT)
            
            # Build SELECT fields
            select_fields = """
                c.id,
                c.name,
                c.email,
                c.vermuk,
                c.notes,
                c.created_at,
                c.updated_at
            """
            
            if include_stats:
                select_fields += """
                    ,
                    COUNT(DISTINCT a.id) AS total_artists,
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
                    MIN(s.created_at) AS first_song_date,
                    MAX(s.created_at) AS last_song_date
                """
            
            # Additional filters for stats (HAVING clause)
            having = []
            having_params = {}
            
            if has_artists is not None:
                if has_artists:
                    having.append("COUNT(DISTINCT a.id) > 0")
                else:
                    having.append("COUNT(DISTINCT a.id) = 0")
            
            if has_songs is not None:
                if has_songs:
                    having.append("COUNT(DISTINCT s.id) > 0")
                else:
                    having.append("COUNT(DISTINCT s.id) = 0")
            
            if min_artists is not None:
                having.append("COUNT(DISTINCT a.id) >= %(min_artists)s")
                having_params["min_artists"] = min_artists
            
            if max_artists is not None:
                having.append("COUNT(DISTINCT a.id) <= %(max_artists)s")
                having_params["max_artists"] = max_artists
            
            if min_songs is not None:
                having.append("COUNT(DISTINCT s.id) >= %(min_songs)s")
                having_params["min_songs"] = min_songs
            
            if max_songs is not None:
                having.append("COUNT(DISTINCT s.id) <= %(max_songs)s")
                having_params["max_songs"] = max_songs
            
            having_sql = " AND ".join(having) if having else ""
            having_clause = f"HAVING {having_sql}" if having_sql else ""
            
            # Build main query
            query = f"""
            SELECT
                {select_fields}
            FROM channels c
            LEFT JOIN artists a ON a.channel_id = c.id
            LEFT JOIN songs s ON s.artist_id = a.id
            WHERE {where_sql}
            GROUP BY c.id, c.name, c.email, c.vermuk, c.notes, c.created_at, c.updated_at
            {having_clause}
            ORDER BY {order_column} {order_direction}
            LIMIT %(limit)s OFFSET %(offset)s
            """
            
            params["limit"] = length
            params["offset"] = start
            
            # Merge having params
            params.update(having_params)
            
            # Execute query
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Get total count (without pagination)
            total = cls.count_filtered(
                cursor,
                keyword=keyword,
                vermuk=vermuk,
                email=email,
                date_from=date_from,
                date_to=date_to,
                has_artists=has_artists,
                has_songs=has_songs,
                min_artists=min_artists,
                max_artists=max_artists,
                min_songs=min_songs,
                max_songs=max_songs,
            )
            
            # Prepare result
            data = [dict(row) for row in rows]
            
            return {
                "data": data,
                "meta": {
                    "total": total,
                    "filtered": total,  # same as total since we filtered
                    "start": start,
                    "length": length,
                    "page": (start // length) + 1 if length > 0 else 1,
                    "total_pages": (total + length - 1) // length if length > 0 else 0,
                    "order_by": order_by,
                    "order_dir": order_dir,
                    "filters": {
                        "keyword": keyword,
                        "vermuk": vermuk,
                        "email": email,
                        "date_from": date_from.isoformat() if date_from else None,
                        "date_to": date_to.isoformat() if date_to else None,
                        "has_artists": has_artists,
                        "has_songs": has_songs,
                        "min_artists": min_artists,
                        "max_artists": max_artists,
                        "min_songs": min_songs,
                        "max_songs": max_songs,
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            raise
    
    # =====================================================
    # COUNT FILTERED
    # =====================================================
    
    @staticmethod
    def count_filtered(
        cursor,
        *,
        keyword: Optional[str] = None,
        vermuk: Optional[bool] = None,
        email: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        has_artists: Optional[bool] = None,
        has_songs: Optional[bool] = None,
        min_artists: Optional[int] = None,
        max_artists: Optional[int] = None,
        min_songs: Optional[int] = None,
        max_songs: Optional[int] = None,
    ) -> int:
        """
        Count total channels matching filters (without pagination).
        
        Returns:
            Total count of matching channels
        """
        try:
            # Build WHERE clause
            where = []
            params = {}
            
            if keyword:
                where.append("""
                    (
                        name ILIKE %(keyword)s
                        OR email ILIKE %(keyword)s
                        OR COALESCE(notes, '') ILIKE %(keyword)s
                    )
                """)
                params["keyword"] = f"%{keyword}%"
            
            if vermuk is not None:
                where.append("vermuk = %(vermuk)s")
                params["vermuk"] = vermuk
            
            if email:
                where.append("email = %(email)s")
                params["email"] = email
            
            if date_from:
                where.append("created_at >= %(date_from)s")
                params["date_from"] = date_from
            
            if date_to:
                where.append("created_at <= %(date_to)s")
                params["date_to"] = date_to
            
            where_sql = " AND ".join(where) if where else "1=1"
            
            # Build query with subquery for stats filters
            if any([has_artists is not None, has_songs is not None, 
                   min_artists, max_artists, min_songs, max_songs]):
                
                # Need to join artists and songs for counting
                having = []
                having_params = {}
                
                if has_artists is not None:
                    if has_artists:
                        having.append("COUNT(DISTINCT a.id) > 0")
                    else:
                        having.append("COUNT(DISTINCT a.id) = 0")
                
                if has_songs is not None:
                    if has_songs:
                        having.append("COUNT(DISTINCT s.id) > 0")
                    else:
                        having.append("COUNT(DISTINCT s.id) = 0")
                
                if min_artists is not None:
                    having.append("COUNT(DISTINCT a.id) >= %(min_artists)s")
                    having_params["min_artists"] = min_artists
                
                if max_artists is not None:
                    having.append("COUNT(DISTINCT a.id) <= %(max_artists)s")
                    having_params["max_artists"] = max_artists
                
                if min_songs is not None:
                    having.append("COUNT(DISTINCT s.id) >= %(min_songs)s")
                    having_params["min_songs"] = min_songs
                
                if max_songs is not None:
                    having.append("COUNT(DISTINCT s.id) <= %(max_songs)s")
                    having_params["max_songs"] = max_songs
                
                having_sql = " AND ".join(having) if having else ""
                having_clause = f"HAVING {having_sql}" if having_sql else ""
                
                params.update(having_params)
                
                query = f"""
                SELECT COUNT(*)
                FROM (
                    SELECT c.id
                    FROM channels c
                    LEFT JOIN artists a ON a.channel_id = c.id
                    LEFT JOIN songs s ON s.artist_id = a.id
                    WHERE {where_sql}
                    GROUP BY c.id
                    {having_clause}
                ) filtered_channels
                """
                
            else:
                # Simple count without joins
                query = f"""
                SELECT COUNT(*)
                FROM channels
                WHERE {where_sql}
                """
            
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            return row[0] if row else 0
            
        except Exception as e:
            logger.error(f"Error counting filtered channels: {e}")
            raise
    
    # =====================================================
    # PRESET FILTERS
    # =====================================================
    
    @classmethod
    def apply_preset(
        cls,
        cursor,
        preset: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Apply a preset filter configuration.
        
        Args:
            cursor: Database cursor
            preset: Preset name ('recent', 'most_songs', etc.)
            **kwargs: Additional filter parameters
            
        Returns:
            Filtered channels with metadata
        """
        if preset not in cls.PRESETS:
            raise ValueError(f"Unknown preset: {preset}. Available: {list(cls.PRESETS.keys())}")
        
        preset_config = cls.PRESETS[preset].copy()
        
        # Override with kwargs if provided
        if 'order_by' in kwargs:
            preset_config['order_by'] = kwargs.pop('order_by')
        if 'order_dir' in kwargs:
            preset_config['order_dir'] = kwargs.pop('order_dir')
        
        # Merge with kwargs
        return cls.apply(cursor, **preset_config, **kwargs)
    
    # =====================================================
    # SIMPLE FILTERS
    # =====================================================
    
    @classmethod
    def filter_by_vermuk(
        cls,
        cursor,
        vermuk: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get channels by vermuk status.
        
        Args:
            cursor: Database cursor
            vermuk: Vermuk status to filter
            **kwargs: Additional filter parameters
            
        Returns:
            Filtered channels
        """
        return cls.apply(cursor, vermuk=vermuk, **kwargs)
    
    @classmethod
    def search(
        cls,
        cursor,
        keyword: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Search channels by keyword.
        
        Args:
            cursor: Database cursor
            keyword: Search keyword
            **kwargs: Additional filter parameters
            
        Returns:
            Filtered channels
        """
        return cls.apply(cursor, keyword=keyword, **kwargs)
    
    @classmethod
    def get_recent(
        cls,
        cursor,
        days: int = 7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get recently created channels.
        
        Args:
            cursor: Database cursor
            days: Number of days to look back
            **kwargs: Additional filter parameters
            
        Returns:
            Filtered channels
        """
        from datetime import date, timedelta
        
        date_from = date.today() - timedelta(days=days)
        return cls.apply(
            cursor,
            date_from=date_from,
            order_by="created_at",
            order_dir="desc",
            **kwargs
        )
    
    @classmethod
    def get_active(
        cls,
        cursor,
        min_songs: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get active channels (with at least min_songs).
        
        Args:
            cursor: Database cursor
            min_songs: Minimum number of songs
            **kwargs: Additional filter parameters
            
        Returns:
            Filtered channels
        """
        return cls.apply(
            cursor,
            has_songs=True,
            min_songs=min_songs,
            order_by="songs",
            order_dir="desc",
            **kwargs
        )
    
    @classmethod
    def get_inactive(
        cls,
        cursor,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get inactive channels (no songs).
        
        Args:
            cursor: Database cursor
            **kwargs: Additional filter parameters
            
        Returns:
            Filtered channels
        """
        return cls.apply(
            cursor,
            has_songs=False,
            order_by="created_at",
            order_dir="asc",
            **kwargs
        )
    
    # =====================================================
    # ADVANCED FILTERS
    # =====================================================
    
    @classmethod
    def filter_with_artist_stats(
        cls,
        cursor,
        min_songs_per_artist: Optional[float] = None,
        max_songs_per_artist: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Filter channels by average songs per artist.
        
        Args:
            cursor: Database cursor
            min_songs_per_artist: Minimum average songs per artist
            max_songs_per_artist: Maximum average songs per artist
            **kwargs: Additional filter parameters
            
        Returns:
            Filtered channels with stats
        """
        try:
            # Build base filter
            result = cls.apply(cursor, include_stats=True, **kwargs)
            
            if not result['data']:
                return result
            
            # Filter in Python (since we already have the data)
            filtered_data = []
            
            for channel in result['data']:
                total_artists = channel.get('total_artists', 0)
                total_songs = channel.get('total_songs', 0)
                
                if total_artists == 0:
                    avg = 0
                else:
                    avg = total_songs / total_artists
                
                if min_songs_per_artist is not None and avg < min_songs_per_artist:
                    continue
                
                if max_songs_per_artist is not None and avg > max_songs_per_artist:
                    continue
                
                channel['avg_songs_per_artist'] = round(avg, 2)
                filtered_data.append(channel)
            
            result['data'] = filtered_data
            result['meta']['filtered'] = len(filtered_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error filtering with artist stats: {e}")
            raise
    
    @classmethod
    def filter_by_date_range(
        cls,
        cursor,
        start_date: date,
        end_date: date,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Filter channels by creation date range.
        
        Args:
            cursor: Database cursor
            start_date: Start date
            end_date: End date
            **kwargs: Additional filter parameters
            
        Returns:
            Filtered channels
        """
        return cls.apply(
            cursor,
            date_from=start_date,
            date_to=end_date,
            **kwargs
        )
    
    # =====================================================
    # UTILITY METHODS
    # =====================================================
    
    @staticmethod
    def get_filter_options(cursor) -> Dict[str, Any]:
        """
        Get available filter options for UI.
        
        Returns:
            Dict with available options
        """
        try:
            # Get unique vermuk values
            cursor.execute("""
                SELECT 
                    vermuk,
                    COUNT(*) as count
                FROM channels
                GROUP BY vermuk
            """)
            vermuk_options = [dict(row) for row in cursor.fetchall()]
            
            # Get date range
            cursor.execute("""
                SELECT 
                    MIN(created_at) as earliest,
                    MAX(created_at) as latest
                FROM channels
            """)
            date_range = dict(cursor.fetchone())
            
            # Get status counts
            cursor.execute("""
                SELECT 
                    'total' as type,
                    COUNT(*) as count
                FROM channels
                UNION ALL
                SELECT 
                    'with_artists' as type,
                    COUNT(DISTINCT c.id) as count
                FROM channels c
                JOIN artists a ON a.channel_id = c.id
                UNION ALL
                SELECT 
                    'with_songs' as type,
                    COUNT(DISTINCT c.id) as count
                FROM channels c
                JOIN artists a ON a.channel_id = c.id
                JOIN songs s ON s.artist_id = a.id
            """)
            status_counts = {row['type']: row['count'] for row in cursor.fetchall()}
            
            return {
                'vermuk': vermuk_options,
                'date_range': {
                    'min': date_range.get('earliest'),
                    'max': date_range.get('latest'),
                },
                'counts': status_counts,
                'sortable_columns': list(ChannelFilterRepository.SORTABLE_COLUMNS.keys()),
                'presets': list(ChannelFilterRepository.PRESETS.keys()),
                'defaults': {
                    'order_by': ChannelFilterRepository.DEFAULT_SORT,
                    'order_dir': ChannelFilterRepository.DEFAULT_DIRECTION,
                    'limit': ChannelFilterRepository.DEFAULT_LIMIT,
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting filter options: {e}")
            raise
    
    @staticmethod
    def validate_order_by(order_by: str) -> bool:
        """
        Validate if order_by column is valid.
        
        Args:
            order_by: Column name to sort by
            
        Returns:
            True if valid, False otherwise
        """
        return order_by in ChannelFilterRepository.SORTABLE_COLUMNS
    
    @staticmethod
    def validate_order_dir(order_dir: str) -> bool:
        """
        Validate if order_dir is valid.
        
        Args:
            order_dir: Sort direction ('asc' or 'desc')
            
        Returns:
            True if valid, False otherwise
        """
        return str(order_dir).lower() in ('asc', 'desc')