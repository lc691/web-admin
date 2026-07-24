"""
Artist Statistics Repository - Complete Implementation

Repository untuk statistik Artist dengan:
- Dashboard statistics
- Channel statistics
- Artist-specific statistics
- Status breakdown
- Top rankings
- Time-series analysis
- Performance metrics
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ArtistStatisticsRepository:
    """
    Repository statistik Artist.
    """

    # =====================================================
    # CONSTANTS
    # =====================================================

    UPLOADED_STATUSES = ('released', 'topic', 'live', 'no_ads')
    PENDING_STATUSES = ('draft', 'review', 'approved', 'scheduled', 'unreleased')
    TAKEDOWN_STATUS = ('take_down',)

    # =====================================================
    # DASHBOARD / SUMMARY
    # =====================================================

    @staticmethod
    def statistics(
        cursor,
        channel_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Statistik Artist secara keseluruhan atau per channel.
        
        Args:
            cursor: Database cursor
            channel_id: Optional channel filter
            
        Returns:
            Dict with statistics
        """
        sql = """
            SELECT
                COUNT(DISTINCT a.id) AS total_artists,
                COUNT(DISTINCT s.id) AS total_songs,
                COUNT(DISTINCT c.id) AS active_channels,
                COUNT(DISTINCT a.id) FILTER (
                    WHERE EXISTS (SELECT 1 FROM songs s2 WHERE s2.artist_id = a.id)
                ) AS artists_with_songs,
                COUNT(DISTINCT a.id) FILTER (
                    WHERE NOT EXISTS (SELECT 1 FROM songs s2 WHERE s2.artist_id = a.id)
                ) AS artists_without_songs,
                AVG(song_counts.song_count)::DECIMAL(10,2) AS avg_songs_per_artist
            FROM artists a
            INNER JOIN channels c ON c.id = a.channel_id
            LEFT JOIN songs s ON s.artist_id = a.id
            LEFT JOIN (
                SELECT artist_id, COUNT(*) AS song_count
                FROM songs
                GROUP BY artist_id
            ) song_counts ON song_counts.artist_id = a.id
            WHERE TRUE
        """

        params = []

        if channel_id is not None:
            sql += " AND a.channel_id = %s"
            params.append(channel_id)

        cursor.execute(sql, params)

        row = cursor.fetchone()

        return {
            "total_artists": row["total_artists"] or 0,
            "total_songs": row["total_songs"] or 0,
            "active_channels": row["active_channels"] or 0,
            "artists_with_songs": row["artists_with_songs"] or 0,
            "artists_without_songs": row["artists_without_songs"] or 0,
            "avg_songs_per_artist": float(row["avg_songs_per_artist"] or 0),
        }

    @staticmethod
    def summary_simple(cursor) -> Dict[str, Any]:
        """
        Simple summary statistics (faster).
        
        Args:
            cursor: Database cursor
            
        Returns:
            Dict with basic statistics
        """
        cursor.execute("""
            SELECT
                COUNT(*) AS total_artists,
                (
                    SELECT COUNT(*)
                    FROM songs
                ) AS total_songs,
                (
                    SELECT COUNT(DISTINCT channel_id)
                    FROM artists
                ) AS active_channels
            FROM artists
        """)

        row = cursor.fetchone()

        return {
            "total_artists": row["total_artists"] or 0,
            "total_songs": row["total_songs"] or 0,
            "active_channels": row["active_channels"] or 0,
        }

    # =====================================================
    # TOTAL COUNTS
    # =====================================================

    @staticmethod
    def total_artists(
        cursor,
        channel_id: Optional[int] = None
    ) -> int:
        """
        Total artists, optionally filtered by channel.
        
        Args:
            cursor: Database cursor
            channel_id: Optional channel filter
            
        Returns:
            Total artists count
        """
        sql = "SELECT COUNT(*) AS total FROM artists WHERE TRUE"
        params = []

        if channel_id is not None:
            sql += " AND channel_id = %s"
            params.append(channel_id)

        cursor.execute(sql, params)
        return cursor.fetchone()["total"]

    @staticmethod
    def total_songs(cursor, artist_id: int) -> int:
        """
        Total songs for an artist.
        
        Args:
            cursor: Database cursor
            artist_id: Artist ID
            
        Returns:
            Total songs count
        """
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM songs
            WHERE artist_id = %s
        """, (artist_id,))

        return cursor.fetchone()["total"]

    @staticmethod
    def active_channels(cursor) -> int:
        """
        Jumlah channel yang memiliki minimal satu artist.
        
        Args:
            cursor: Database cursor
            
        Returns:
            Active channels count
        """
        cursor.execute("""
            SELECT COUNT(DISTINCT channel_id) AS total
            FROM artists
        """)

        return cursor.fetchone()["total"]

    @staticmethod
    def total_artists_by_channel(cursor) -> Dict[int, int]:
        """
        Total artists per channel.
        
        Args:
            cursor: Database cursor
            
        Returns:
            Dict mapping channel_id -> artist_count
        """
        cursor.execute("""
            SELECT
                channel_id,
                COUNT(*) AS artist_count
            FROM artists
            GROUP BY channel_id
            ORDER BY artist_count DESC
        """)

        return {row['channel_id']: row['artist_count'] for row in cursor.fetchall()}

    # =====================================================
    # ARTIST-SPECIFIC STATISTICS
    # =====================================================

    @staticmethod
    def artist_detail_stats(cursor, artist_id: int) -> Dict[str, Any]:
        """
        Detailed statistics for a specific artist.
        
        Args:
            cursor: Database cursor
            artist_id: Artist ID
            
        Returns:
            Dict with detailed statistics
        """
        cursor.execute("""
            SELECT
                a.id,
                a.name,
                a.channel_id,
                c.name AS channel_name,
                c.vermuk AS channel_vermuk,
                a.created_at,
                a.updated_at,
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
                MIN(s.release_date) AS earliest_release,
                MAX(s.release_date) AS latest_release,
                MIN(s.created_at) AS first_song,
                MAX(s.created_at) AS last_song,
                COUNT(DISTINCT s.id) FILTER (
                    WHERE s.release_date IS NOT NULL
                ) AS songs_with_release_date,
                COUNT(DISTINCT s.id) FILTER (
                    WHERE s.release_date > CURRENT_DATE
                ) AS upcoming_releases,
                COUNT(DISTINCT s.id) FILTER (
                    WHERE s.release_date <= CURRENT_DATE
                      AND s.status = 'released'
                ) AS released_songs
            FROM artists a
            INNER JOIN channels c ON c.id = a.channel_id
            LEFT JOIN songs s ON s.artist_id = a.id
            WHERE a.id = %s
            GROUP BY
                a.id,
                a.name,
                a.channel_id,
                c.name,
                c.vermuk,
                a.created_at,
                a.updated_at
        """, (artist_id,))

        row = cursor.fetchone()

        if not row:
            return {}

        result = dict(row)

        # Calculate derived metrics
        total_songs = result.get('total_songs', 0)
        if total_songs > 0:
            result['upload_rate'] = round(
                (result.get('uploaded_songs', 0) / total_songs) * 100, 2
            )
            result['pending_rate'] = round(
                (result.get('pending_songs', 0) / total_songs) * 100, 2
            )
        else:
            result['upload_rate'] = 0.0
            result['pending_rate'] = 0.0

        # Activity days
        if result.get('first_song') and result.get('last_song'):
            days_active = (result['last_song'] - result['first_song']).days
            result['days_active'] = days_active
            if days_active > 0:
                result['songs_per_day'] = round(total_songs / days_active, 2)
            else:
                result['songs_per_day'] = total_songs
        else:
            result['days_active'] = 0
            result['songs_per_day'] = 0.0

        return result

    # =====================================================
    # SONG STATUS
    # =====================================================

    @staticmethod
    def song_status(cursor, artist_id: int) -> List[Dict[str, Any]]:
        """
        Statistik status lagu per artist.
        
        Args:
            cursor: Database cursor
            artist_id: Artist ID
            
        Returns:
            List of status breakdown
        """
        cursor.execute("""
            SELECT
                status,
                COUNT(*) AS total,
                ROUND((COUNT(*)::DECIMAL / SUM(COUNT(*)) OVER () * 100), 2) AS percentage
            FROM songs
            WHERE artist_id = %s
            GROUP BY status
            ORDER BY total DESC
        """, (artist_id,))

        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def song_status_by_channel(
        cursor,
        channel_id: int
    ) -> List[Dict[str, Any]]:
        """
        Statistik status lagu per channel.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            
        Returns:
            List of status breakdown
        """
        cursor.execute("""
            SELECT
                s.status,
                COUNT(*) AS total,
                ROUND((COUNT(*)::DECIMAL / SUM(COUNT(*)) OVER () * 100), 2) AS percentage
            FROM songs s
            INNER JOIN artists a ON s.artist_id = a.id
            WHERE a.channel_id = %s
            GROUP BY s.status
            ORDER BY total DESC
        """, (channel_id,))

        return [dict(row) for row in cursor.fetchall()]

    # =====================================================
    # CHANNEL SUMMARY
    # =====================================================

    @staticmethod
    def channel_summary(cursor, channel_id: int) -> Dict[str, Any]:
        """
        Ringkasan artist dalam satu channel.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            
        Returns:
            Dict with channel summary
        """
        cursor.execute("""
            SELECT
                COUNT(DISTINCT a.id) AS total_artists,
                COUNT(DISTINCT s.id) AS total_songs,
                COUNT(DISTINCT a.id) FILTER (
                    WHERE EXISTS (SELECT 1 FROM songs s2 WHERE s2.artist_id = a.id)
                ) AS artists_with_songs,
                COUNT(DISTINCT a.id) FILTER (
                    WHERE NOT EXISTS (SELECT 1 FROM songs s2 WHERE s2.artist_id = a.id)
                ) AS artists_without_songs,
                AVG(song_counts.song_count)::DECIMAL(10,2) AS avg_songs_per_artist,
                MIN(a.created_at) AS oldest_artist,
                MAX(a.created_at) AS newest_artist
            FROM artists a
            LEFT JOIN songs s ON s.artist_id = a.id
            LEFT JOIN (
                SELECT artist_id, COUNT(*) AS song_count
                FROM songs
                GROUP BY artist_id
            ) song_counts ON song_counts.artist_id = a.id
            WHERE a.channel_id = %s
        """, (channel_id,))

        return dict(cursor.fetchone())

    @staticmethod
    def channel_artist_list(
        cursor,
        channel_id: int,
        order_by: str = "song_count",
        order_dir: str = "desc",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List artists in a channel with stats.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            order_by: Sort column
            order_dir: Sort direction
            limit: Max records
            
        Returns:
            List of artists with stats
        """
        valid_columns = {
            "id": "a.id",
            "name": "LOWER(a.name)",
            "song_count": "song_count",
            "uploaded_songs": "uploaded_songs",
            "created_at": "a.created_at",
            "updated_at": "a.updated_at"
        }

        order_column = valid_columns.get(order_by, "song_count")
        order_direction = "ASC" if order_dir.lower() == "asc" else "DESC"

        cursor.execute(f"""
            SELECT
                a.id,
                a.name,
                COUNT(DISTINCT s.id) AS song_count,
                COUNT(DISTINCT s.id) FILTER (
                    WHERE s.status IN ('released', 'topic', 'live', 'no_ads')
                ) AS uploaded_songs,
                COUNT(DISTINCT s.id) FILTER (
                    WHERE s.status IN ('draft', 'review', 'approved', 'scheduled', 'unreleased')
                ) AS pending_songs,
                MIN(s.created_at) AS first_song,
                MAX(s.created_at) AS last_song,
                a.created_at,
                a.updated_at
            FROM artists a
            LEFT JOIN songs s ON s.artist_id = a.id
            WHERE a.channel_id = %s
            GROUP BY a.id, a.name, a.created_at, a.updated_at
            ORDER BY {order_column} {order_direction}
            LIMIT %s
        """, (channel_id, limit))

        return [dict(row) for row in cursor.fetchall()]

    # =====================================================
    # TOP RANKINGS
    # =====================================================

    @staticmethod
    def top_artists(
        cursor,
        channel_id: Optional[int] = None,
        limit: int = 10,
        min_songs: int = 1,
        order_by: str = "song_count"
    ) -> List[Dict[str, Any]]:
        """
        Get top artists by song count.
        
        Args:
            cursor: Database cursor
            channel_id: Optional channel filter
            limit: Number of artists
            min_songs: Minimum songs
            order_by: Sort column (song_count, uploaded_songs, pending_songs)
            
        Returns:
            List of top artists
        """
        valid_order = {
            "song_count": "song_count",
            "uploaded_songs": "uploaded_songs",
            "pending_songs": "pending_songs"
        }
        order_column = valid_order.get(order_by, "song_count")

        query = """
            SELECT
                a.id,
                a.name,
                a.channel_id,
                c.name AS channel_name,
                COUNT(DISTINCT s.id) AS song_count,
                COUNT(DISTINCT s.id) FILTER (
                    WHERE s.status IN ('released', 'topic', 'live', 'no_ads')
                ) AS uploaded_songs,
                COUNT(DISTINCT s.id) FILTER (
                    WHERE s.status IN ('draft', 'review', 'approved', 'scheduled', 'unreleased')
                ) AS pending_songs,
                MIN(s.created_at) AS first_song,
                MAX(s.created_at) AS last_song,
                a.created_at,
                a.updated_at
            FROM artists a
            INNER JOIN channels c ON c.id = a.channel_id
            LEFT JOIN songs s ON s.artist_id = a.id
            WHERE 1=1
        """
        params = []

        if channel_id:
            query += " AND a.channel_id = %s"
            params.append(channel_id)

        query += f"""
            GROUP BY a.id, a.name, a.channel_id, c.name, a.created_at, a.updated_at
            HAVING COUNT(DISTINCT s.id) >= %s
            ORDER BY {order_column} DESC
            LIMIT %s
        """
        params.extend([min_songs, limit])

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def top_channels_by_artists(
        cursor,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top channels by number of artists.
        
        Args:
            cursor: Database cursor
            limit: Number of channels
            
        Returns:
            List of top channels
        """
        cursor.execute("""
            SELECT
                c.id,
                c.name,
                COUNT(DISTINCT a.id) AS artist_count,
                COUNT(DISTINCT s.id) AS song_count,
                COUNT(DISTINCT a.id) FILTER (
                    WHERE EXISTS (SELECT 1 FROM songs s2 WHERE s2.artist_id = a.id)
                ) AS artists_with_songs,
                MIN(a.created_at) AS oldest_artist,
                MAX(a.created_at) AS newest_artist
            FROM channels c
            INNER JOIN artists a ON a.channel_id = c.id
            LEFT JOIN songs s ON s.artist_id = a.id
            GROUP BY c.id, c.name
            ORDER BY artist_count DESC
            LIMIT %s
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    # =====================================================
    # TIME-SERIES ANALYSIS
    # =====================================================

    @staticmethod
    def growth_by_channel(
        cursor,
        channel_id: int,
        months: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Monthly growth of artists in a channel.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            months: Number of months
            
        Returns:
            List of monthly growth data
        """
        cursor.execute("""
            WITH monthly_data AS (
                SELECT
                    DATE_TRUNC('month', a.created_at) AS month,
                    COUNT(DISTINCT a.id) AS new_artists
                FROM artists a
                WHERE a.channel_id = %s
                  AND a.created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '%s months'
                GROUP BY DATE_TRUNC('month', a.created_at)
                ORDER BY month DESC
            ),
            cumulative AS (
                SELECT
                    month,
                    new_artists,
                    SUM(new_artists) OVER (ORDER BY month ROWS UNBOUNDED PRECEDING) AS cumulative_artists
                FROM monthly_data
            )
            SELECT
                TO_CHAR(month, 'YYYY-MM') AS month_label,
                month,
                new_artists,
                cumulative_artists
            FROM cumulative
            ORDER BY month DESC
        """, (channel_id, months))

        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def daily_activity(
        cursor,
        days: int = 30,
        channel_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Daily artist creation activity.
        
        Args:
            cursor: Database cursor
            days: Number of days
            channel_id: Optional channel filter
            
        Returns:
            List of daily activity data
        """
        query = """
            WITH daily_data AS (
                SELECT
                    DATE(a.created_at) AS day,
                    COUNT(DISTINCT a.id) AS artists_created
                FROM artists a
                WHERE a.created_at >= CURRENT_DATE - INTERVAL '%s days'
            """
        params = [days]

        if channel_id:
            query += " AND a.channel_id = %s"
            params.append(channel_id)

        query += """
                GROUP BY DATE(a.created_at)
            ),
            days_series AS (
                SELECT generate_series(
                    CURRENT_DATE - INTERVAL '%s days',
                    CURRENT_DATE,
                    '1 day'::interval
                )::DATE AS day
            )
            SELECT
                ds.day,
                COALESCE(dd.artists_created, 0) AS artists_created
            FROM days_series ds
            LEFT JOIN daily_data dd ON dd.day = ds.day
            ORDER BY ds.day DESC
        """
        params.append(days)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # =====================================================
    # COMPARATIVE ANALYSIS
    # =====================================================

    @staticmethod
    def compare_artists(
        cursor,
        artist_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Compare multiple artists.
        
        Args:
            cursor: Database cursor
            artist_ids: List of artist IDs
            
        Returns:
            Dict with comparison data
        """
        if not artist_ids:
            return {'artists': [], 'metrics': {}}

        cursor.execute("""
            SELECT
                a.id,
                a.name,
                a.channel_id,
                c.name AS channel_name,
                COUNT(DISTINCT s.id) AS song_count,
                COUNT(DISTINCT s.id) FILTER (
                    WHERE s.status IN ('released', 'topic', 'live', 'no_ads')
                ) AS uploaded_songs,
                COUNT(DISTINCT s.id) FILTER (
                    WHERE s.status IN ('draft', 'review', 'approved', 'scheduled', 'unreleased')
                ) AS pending_songs,
                MIN(s.created_at) AS first_song,
                MAX(s.created_at) AS last_song,
                EXTRACT(DAY FROM MAX(s.created_at) - MIN(s.created_at)) AS days_active,
                a.created_at,
                a.updated_at
            FROM artists a
            INNER JOIN channels c ON c.id = a.channel_id
            LEFT JOIN songs s ON s.artist_id = a.id
            WHERE a.id = ANY(%s)
            GROUP BY a.id, a.name, a.channel_id, c.name, a.created_at, a.updated_at
            ORDER BY song_count DESC
        """, (artist_ids,))

        artists = [dict(row) for row in cursor.fetchall()]

        # Calculate metrics
        metrics = {
            'total_artists': len(artists),
            'total_songs': sum(a.get('song_count', 0) for a in artists),
            'total_uploaded': sum(a.get('uploaded_songs', 0) for a in artists),
            'avg_songs_per_artist': round(
                sum(a.get('song_count', 0) for a in artists) / len(artists), 2
            ) if artists else 0
        }

        return {
            'artists': artists,
            'metrics': metrics
        }

    # =====================================================
    # EXPORT FUNCTIONS
    # =====================================================

    @staticmethod
    def export_channel_artists(
        cursor,
        channel_id: int,
        include_songs: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Export all artists in a channel with their songs.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            include_songs: Include song details
            
        Returns:
            List of artists with data
        """
        query = """
            SELECT
                a.id,
                a.name,
                a.created_at,
                a.updated_at,
                COUNT(DISTINCT s.id) AS song_count
        """

        if include_songs:
            query += """
                ,
                STRING_AGG(DISTINCT s.title, ', ') AS song_titles,
                STRING_AGG(DISTINCT s.status, ', ') AS song_statuses
            """

        query += """
            FROM artists a
            LEFT JOIN songs s ON s.artist_id = a.id
            WHERE a.channel_id = %s
            GROUP BY a.id, a.name, a.created_at, a.updated_at
            ORDER BY LOWER(a.name)
        """

        cursor.execute(query, (channel_id,))
        return [dict(row) for row in cursor.fetchall()]