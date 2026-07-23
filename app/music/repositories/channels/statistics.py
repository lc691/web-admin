"""
Channel Statistics Repository - Complete Implementation

Repository untuk berbagai statistik dan agregasi data channels dengan:
- Statistik dashboard (summary)
- Statistik per channel
- Statistik time-series (harian, mingguan, bulanan)
- Statistik status songs
- Performance optimized queries
- Rich data visualization support
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ChannelStatisticsRepository:
    """
    Repository untuk semua operasi statistik terkait channels, artists, dan songs.
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
    def summary(cursor) -> Dict[str, Any]:
        """
        Get comprehensive dashboard summary for channels.
        
        Returns:
            Dict with all summary statistics
        """
        try:
            cursor.execute("""
                SELECT
                    -- Channel counts
                    COUNT(DISTINCT c.id)::INTEGER AS total_channels,
                    COUNT(DISTINCT c.id) FILTER (WHERE c.vermuk = TRUE)::INTEGER AS total_vermuk,
                    COUNT(DISTINCT c.id) FILTER (WHERE c.vermuk = FALSE)::INTEGER AS total_normal,
                    
                    -- Channel with artists/songs
                    COUNT(DISTINCT c.id) FILTER (
                        WHERE EXISTS (
                            SELECT 1 FROM artists a WHERE a.channel_id = c.id
                        )
                    )::INTEGER AS channels_with_artists,
                    
                    COUNT(DISTINCT c.id) FILTER (
                        WHERE EXISTS (
                            SELECT 1 FROM songs s 
                            JOIN artists a ON s.artist_id = a.id 
                            WHERE a.channel_id = c.id
                        )
                    )::INTEGER AS channels_with_songs,
                    
                    -- Artist counts
                    COUNT(DISTINCT a.id)::INTEGER AS total_artists,
                    COUNT(DISTINCT a.id) FILTER (
                        WHERE EXISTS (SELECT 1 FROM songs s WHERE s.artist_id = a.id)
                    )::INTEGER AS artists_with_songs,
                    
                    -- Song counts by status
                    COUNT(DISTINCT s.id)::INTEGER AS total_songs,
                    COUNT(DISTINCT s.id) FILTER (WHERE s.status = ANY(%s::release_status[]))::INTEGER AS uploaded_songs,
                    COUNT(DISTINCT s.id) FILTER (WHERE s.status = ANY(%s::release_status[]))::INTEGER AS pending_songs,
                    COUNT(DISTINCT s.id) FILTER (WHERE s.status = ANY(%s::release_status[]))::INTEGER AS takedown_songs,
                    
                    -- Song status breakdown
                    jsonb_object_agg(
                        COALESCE(CAST(s.status AS text), 'no_songs'),
                        COUNT(DISTINCT s.id)
                    ) FILTER (WHERE s.id IS NOT NULL) AS status_breakdown,
                    
                    -- Timestamps
                    MIN(c.created_at) AS oldest_channel,
                    MAX(c.created_at) AS newest_channel,
                    MIN(s.created_at) AS oldest_song,
                    MAX(s.created_at) AS newest_song,
                    
                    -- Averages
                    AVG(artist_counts.artist_count)::DECIMAL(10,2) AS avg_artists_per_channel,
                    AVG(song_counts.song_count)::DECIMAL(10,2) AS avg_songs_per_channel,
                    AVG(songs_per_artist.song_count)::DECIMAL(10,2) AS avg_songs_per_artist
                    
                FROM channels c
                
                LEFT JOIN artists a ON a.channel_id = c.id
                LEFT JOIN songs s ON s.artist_id = a.id
                
                LEFT JOIN (
                    SELECT channel_id, COUNT(*) as artist_count
                    FROM artists
                    GROUP BY channel_id
                ) artist_counts ON artist_counts.channel_id = c.id
                
                LEFT JOIN (
                    SELECT channel_id, COUNT(s.id) as song_count
                    FROM artists a
                    LEFT JOIN songs s ON s.artist_id = a.id
                    GROUP BY a.channel_id
                ) song_counts ON song_counts.channel_id = c.id
                
                LEFT JOIN (
                    SELECT artist_id, COUNT(*) as song_count
                    FROM songs
                    GROUP BY artist_id
                ) songs_per_artist ON songs_per_artist.artist_id = a.id
                
                GROUP BY 
                    artist_counts.artist_count,
                    song_counts.song_count,
                    songs_per_artist.song_count
            """, (
                list(ChannelStatisticsRepository.UPLOADED_STATUSES),
                list(ChannelStatisticsRepository.PENDING_STATUSES),
                list(ChannelStatisticsRepository.TAKEDOWN_STATUS)
            ))
            
            result = dict(cursor.fetchone())
            
            # Calculate derived metrics
            if result.get('total_channels', 0) > 0:
                result['utilization_rate'] = round(
                    (result.get('channels_with_songs', 0) / result['total_channels']) * 100, 
                    2
                )
            else:
                result['utilization_rate'] = 0.0
                
            # Calculate growth metrics
            result['has_data'] = result.get('total_songs', 0) > 0
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting dashboard summary: {e}")
            raise
    
    @staticmethod
    def summary_simple(cursor) -> Dict[str, Any]:
        """
        Get simple summary (faster, less detailed).
        
        Returns:
            Dict with basic summary statistics
        """
        try:
            cursor.execute("""
                SELECT
                    COUNT(*)::INTEGER AS total_channels,
                    COUNT(*) FILTER (WHERE vermuk = TRUE)::INTEGER AS total_vermuk,
                    COUNT(*) FILTER (WHERE vermuk = FALSE)::INTEGER AS total_normal,
                    (
                        SELECT COUNT(*)::INTEGER FROM artists
                    ) AS total_artists,
                    (
                        SELECT COUNT(*)::INTEGER FROM songs
                    ) AS total_songs,
                    (
                        SELECT COUNT(*)::INTEGER 
                        FROM songs 
                        WHERE status = ANY(%s::release_status[])
                    ) AS uploaded_songs,
                    (
                        SELECT COUNT(*)::INTEGER 
                        FROM songs 
                        WHERE status = ANY(%s::release_status[])
                    ) AS pending_songs,
                    (
                        SELECT COUNT(*)::INTEGER
                        FROM songs
                        WHERE status = ANY(%s::release_status[])
                    ) AS takedown_songs
                FROM channels
            """, (
                list(ChannelStatisticsRepository.UPLOADED_STATUSES),
                list(ChannelStatisticsRepository.PENDING_STATUSES),
                list(ChannelStatisticsRepository.TAKEDOWN_STATUS)
            ))
            
            return dict(cursor.fetchone())
            
        except Exception as e:
            logger.error(f"Error getting simple summary: {e}")
            raise
    
    # =====================================================
    # CHANNEL-SPECIFIC STATISTICS
    # =====================================================
    
    @staticmethod
    def get_channel_stats(cursor, channel_id: int) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive statistics for a specific channel.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            
        Returns:
            Dict with channel statistics or None if channel not found
        """
        try:
            cursor.execute("""
                WITH channel_stats AS (
                    SELECT
                        c.id,
                        c.name,
                        c.vermuk,
                        c.created_at,
                        c.updated_at,
                        
                        -- Artists
                        COUNT(DISTINCT a.id) AS total_artists,
                        COUNT(DISTINCT a.id) FILTER (
                            WHERE EXISTS (SELECT 1 FROM songs s WHERE s.artist_id = a.id)
                        ) AS artists_with_songs,
                        
                        -- Songs
                        COUNT(DISTINCT s.id) AS total_songs,
                        
                        -- Songs by status
                        COUNT(DISTINCT s.id) FILTER (WHERE s.status = ANY(%s::release_status[])) AS uploaded_songs,
                        COUNT(DISTINCT s.id) FILTER (WHERE s.status = ANY(%s::release_status[])) AS pending_songs,
                        COUNT(DISTINCT s.id) FILTER (WHERE s.status = ANY(%s::release_status[])) AS takedown_songs,
                        
                        -- Song date range
                        MIN(s.release_date) AS earliest_release,
                        MAX(s.release_date) AS latest_release,
                        MIN(s.created_at) AS oldest_song,
                        MAX(s.created_at) AS newest_song,
                        
                        -- Status breakdown as JSON
                        jsonb_object_agg(
                            COALESCE(CAST(s.status AS text), 'no_songs'),
                            COUNT(DISTINCT s.id)
                        ) FILTER (WHERE s.id IS NOT NULL) AS status_breakdown,
                        
                        -- Release stats
                        COUNT(DISTINCT s.id) FILTER (
                            WHERE s.release_date IS NOT NULL
                        ) AS songs_with_release_date,
                        
                        COUNT(DISTINCT s.id) FILTER (
                            WHERE s.release_date > CURRENT_DATE
                        ) AS upcoming_releases,
                        
                        COUNT(DISTINCT s.id) FILTER (
                            WHERE s.release_date <= CURRENT_DATE
                              AND s.status = 'released'::release_status
                        ) AS released_songs
                        
                    FROM channels c
                    LEFT JOIN artists a ON a.channel_id = c.id
                    LEFT JOIN songs s ON s.artist_id = a.id
                    WHERE c.id = %s
                    GROUP BY c.id, c.name, c.vermuk, c.created_at, c.updated_at
                )
                SELECT * FROM channel_stats
            """, (
                list(ChannelStatisticsRepository.UPLOADED_STATUSES),
                list(ChannelStatisticsRepository.PENDING_STATUSES),
                list(ChannelStatisticsRepository.TAKEDOWN_STATUS),
                channel_id
            ))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            result = dict(row)

            numeric_fields = [
                "recent_songs",
                "avg_songs_per_month",
                "upload_rate",
                "songs_last_90_days",
                "songs_previous_90_days",
                "total_songs",
                "total_artists",
                "recency_score",
                "consistency_score",
                "engagement_score",
                "growth_score",
            ]

            for field in numeric_fields:
                if result.get(field) is None:
                    result[field] = 0
            
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
            if result.get('oldest_song') and result.get('newest_song'):
                days_active = (result['newest_song'] - result['oldest_song']).days
                result['days_active'] = days_active
                if days_active > 0:
                    result['songs_per_day'] = round(total_songs / days_active, 2)
                else:
                    result['songs_per_day'] = total_songs
            else:
                result['days_active'] = 0
                result['songs_per_day'] = 0.0
                
            return result
            
        except Exception as e:
            logger.error(f"Error getting stats for channel {channel_id}: {e}")
            raise
    
    @staticmethod
    def get_channel_growth(cursor, channel_id: int, months: int = 12) -> List[Dict[str, Any]]:
        """
        Get monthly growth statistics for a channel.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            months: Number of months to look back
            
        Returns:
            List of monthly growth data
        """
        try:
            cursor.execute("""
                WITH monthly_data AS (
                    SELECT
                        DATE_TRUNC('month', s.created_at) AS month,
                        COUNT(DISTINCT s.id) AS new_songs,
                        COUNT(DISTINCT a.id) AS new_artists
                    FROM artists a
                    JOIN songs s ON s.artist_id = a.id
                    WHERE a.channel_id = %s
                      AND s.created_at >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '%s months'
                    GROUP BY DATE_TRUNC('month', s.created_at)
                    ORDER BY month DESC
                ),
                cumulative AS (
                    SELECT
                        month,
                        new_songs,
                        new_artists,
                        SUM(new_songs) OVER (ORDER BY month ROWS UNBOUNDED PRECEDING) AS cumulative_songs,
                        SUM(new_artists) OVER (ORDER BY month ROWS UNBOUNDED PRECEDING) AS cumulative_artists
                    FROM monthly_data
                )
                SELECT
                    TO_CHAR(month, 'YYYY-MM') AS month_label,
                    month,
                    new_songs,
                    new_artists,
                    cumulative_songs,
                    cumulative_artists
                FROM cumulative
                ORDER BY month DESC
            """, (channel_id, months))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error getting growth data for channel {channel_id}: {e}")
            raise
    
    # =====================================================
    # TIME-SERIES STATISTICS
    # =====================================================
    
    @staticmethod
    def get_daily_stats(
        cursor,
        days: int = 30,
        channel_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get daily statistics for the last N days.
        
        Args:
            cursor: Database cursor
            days: Number of days to look back
            channel_id: Optional channel filter
            
        Returns:
            List of daily statistics
        """
        try:
            channel_filter = ""
            params = [days]
            
            if channel_id:
                channel_filter = "AND a.channel_id = %s"
                params.append(channel_id)
            
            cursor.execute(f"""
                WITH daily_data AS (
                    SELECT
                        DATE(s.created_at) AS day,
                        COUNT(DISTINCT s.id) AS songs_created,
                        COUNT(DISTINCT s.id) FILTER (WHERE s.status = ANY(%s::release_status[])) AS songs_uploaded,
                        COUNT(DISTINCT s.id) FILTER (WHERE s.status = ANY(%s::release_status[])) AS songs_pending,
                        COUNT(DISTINCT a.id) AS artists_created,
                        COUNT(DISTINCT c.id) AS channels_created
                    FROM songs s
                    JOIN artists a ON s.artist_id = a.id
                    JOIN channels c ON c.id = a.channel_id
                    WHERE s.created_at >= CURRENT_DATE - INTERVAL '%s days'
                    {channel_filter}
                    GROUP BY DATE(s.created_at)
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
                    COALESCE(dd.songs_created, 0) AS songs_created,
                    COALESCE(dd.songs_uploaded, 0) AS songs_uploaded,
                    COALESCE(dd.songs_pending, 0) AS songs_pending,
                    COALESCE(dd.artists_created, 0) AS artists_created,
                    COALESCE(dd.channels_created, 0) AS channels_created
                FROM days_series ds
                LEFT JOIN daily_data dd ON dd.day = ds.day
                ORDER BY ds.day DESC
            """, (
                list(ChannelStatisticsRepository.UPLOADED_STATUSES),
                list(ChannelStatisticsRepository.PENDING_STATUSES),
                days,
                days,
                *params[1:]  # Additional params (channel_id if exists)
            ))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            raise
    
    @staticmethod
    def get_weekly_stats(cursor, weeks: int = 12) -> List[Dict[str, Any]]:
        """
        Get weekly statistics.
        
        Args:
            cursor: Database cursor
            weeks: Number of weeks to look back
            
        Returns:
            List of weekly statistics
        """
        try:
            cursor.execute("""
                WITH weekly_data AS (
                    SELECT
                        DATE_TRUNC('week', s.created_at) AS week,
                        COUNT(DISTINCT s.id) AS songs_created,
                        COUNT(DISTINCT s.id) FILTER (WHERE s.status = ANY(%s::release_status[])) AS songs_uploaded,
                        COUNT(DISTINCT a.id) AS artists_created,
                        COUNT(DISTINCT c.id) AS channels_created
                    FROM songs s
                    JOIN artists a ON s.artist_id = a.id
                    JOIN channels c ON c.id = a.channel_id
                    WHERE s.created_at >= DATE_TRUNC('week', CURRENT_DATE) - INTERVAL '%s weeks'
                    GROUP BY DATE_TRUNC('week', s.created_at)
                )
                SELECT
                    TO_CHAR(week, 'YYYY-WW') AS week_label,
                    week,
                    songs_created,
                    songs_uploaded,
                    artists_created,
                    channels_created,
                    SUM(songs_created) OVER (ORDER BY week) AS cumulative_songs
                FROM weekly_data
                ORDER BY week DESC
            """, (
                list(ChannelStatisticsRepository.UPLOADED_STATUSES),
                weeks
            ))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error getting weekly stats: {e}")
            raise
    
    # =====================================================
    # STATUS BREAKDOWN
    # =====================================================
    
    @staticmethod
    def get_status_breakdown(cursor) -> Dict[str, Any]:
        """
        Get breakdown of all songs by status across all channels.
        
        Returns:
            Dict with status breakdown
        """
        try:
            cursor.execute("""
                SELECT
                    status,
                    COUNT(*)::INTEGER AS count,
                    ROUND((COUNT(*)::DECIMAL / SUM(COUNT(*)) OVER () * 100), 2) AS percentage
                FROM songs
                GROUP BY status
                ORDER BY count DESC
            """)
            
            rows = [dict(row) for row in cursor.fetchall()]
            
            # Summary
            total = sum(row['count'] for row in rows)
            
            return {
                'breakdown': rows,
                'total': total,
                'statuses': [row['status'] for row in rows],
                'counts': [row['count'] for row in rows],
                'percentages': [row['percentage'] for row in rows]
            }
            
        except Exception as e:
            logger.error(f"Error getting status breakdown: {e}")
            raise
    
    @staticmethod
    def get_status_breakdown_by_channel(cursor, channel_id: int) -> List[Dict[str, Any]]:
        """
        Get status breakdown for a specific channel.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            
        Returns:
            List of status breakdown by channel
        """
        try:
            cursor.execute("""
                SELECT
                    s.status,
                    COUNT(*)::INTEGER AS count,
                    ROUND((COUNT(*)::DECIMAL / SUM(COUNT(*)) OVER () * 100), 2) AS percentage
                FROM songs s
                JOIN artists a ON s.artist_id = a.id
                WHERE a.channel_id = %s
                GROUP BY s.status
                ORDER BY count DESC
            """, (channel_id,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error getting status breakdown for channel {channel_id}: {e}")
            raise
    
    # =====================================================
    # RANKING / TOP LISTS
    # =====================================================
    
    @staticmethod
    def get_top_channels_by_songs(
        cursor,
        limit: int = 10,
        min_songs: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get top channels by number of songs.
        
        Args:
            cursor: Database cursor
            limit: Number of channels to return
            min_songs: Minimum songs filter
            
        Returns:
            List of top channels
        """
        try:
            cursor.execute("""
                SELECT
                    c.id,
                    c.name,
                    c.vermuk,
                    c.created_at,
                    COUNT(DISTINCT a.id) AS artist_count,
                    COUNT(DISTINCT s.id) AS song_count,
                    COUNT(DISTINCT s.id) FILTER (WHERE s.status = ANY(%s::release_status[])) AS uploaded,
                    COUNT(DISTINCT s.id) FILTER (WHERE s.status = ANY(%s::release_status[])) AS pending,
                    MIN(s.created_at) AS first_song,
                    MAX(s.created_at) AS last_song
                FROM channels c
                JOIN artists a ON a.channel_id = c.id
                JOIN songs s ON s.artist_id = a.id
                GROUP BY c.id, c.name, c.vermuk, c.created_at
                HAVING COUNT(DISTINCT s.id) >= %s
                ORDER BY song_count DESC
                LIMIT %s
            """, (
                list(ChannelStatisticsRepository.UPLOADED_STATUSES),
                list(ChannelStatisticsRepository.PENDING_STATUSES),
                min_songs,
                limit
            ))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error getting top channels: {e}")
            raise
    
    @staticmethod
    def get_top_artists_by_songs(
        cursor,
        channel_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top artists by number of songs.
        
        Args:
            cursor: Database cursor
            channel_id: Optional channel filter
            limit: Number of artists to return
            
        Returns:
            List of top artists
        """
        try:
            channel_filter = ""
            params = []
            
            if channel_id:
                channel_filter = "WHERE a.channel_id = %s"
                params.append(channel_id)
            
            cursor.execute(f"""
                SELECT
                    a.id,
                    a.name,
                    a.channel_id,
                    c.name AS channel_name,
                    COUNT(DISTINCT s.id) AS song_count,
                    COUNT(DISTINCT s.id) FILTER (WHERE s.status = ANY(%s::release_status[])) AS uploaded,
                    COUNT(DISTINCT s.id) FILTER (WHERE s.status = ANY(%s::release_status[])) AS pending,
                    MIN(s.created_at) AS first_song,
                    MAX(s.created_at) AS last_song
                FROM artists a
                JOIN songs s ON s.artist_id = a.id
                JOIN channels c ON c.id = a.channel_id
                {channel_filter}
                GROUP BY a.id, a.name, a.channel_id, c.name
                ORDER BY song_count DESC
                LIMIT %s
            """, (
                list(ChannelStatisticsRepository.UPLOADED_STATUSES),
                list(ChannelStatisticsRepository.PENDING_STATUSES),
                *params,
                limit
            ))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error getting top artists: {e}")
            raise
    
    # =====================================================
    # COMPARATIVE STATISTICS
    # =====================================================
    
    @staticmethod
    def compare_channels(
        cursor,
        channel_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Compare multiple channels side by side.
        
        Args:
            cursor: Database cursor
            channel_ids: List of channel IDs to compare
            
        Returns:
            Dict with comparison data
        """
        try:
            if not channel_ids:
                return {'channels': [], 'metrics': []}
            
            cursor.execute("""
                WITH channel_stats AS (
                    SELECT
                        c.id,
                        c.name,
                        c.vermuk,
                        COUNT(DISTINCT a.id) AS artists,
                        COUNT(DISTINCT s.id) AS songs,
                        COUNT(DISTINCT s.id) FILTER (WHERE s.status = ANY(%s::release_status[])) AS uploaded,
                        COUNT(DISTINCT s.id) FILTER (WHERE s.status = ANY(%s::release_status[])) AS pending,
                        COUNT(DISTINCT s.id) FILTER (WHERE s.status = ANY(%s::release_status[])) AS takedown,
                        MIN(s.created_at) AS first_song,
                        MAX(s.created_at) AS last_song,
                        EXTRACT(DAY FROM MAX(s.created_at) - MIN(s.created_at)) AS days_active
                    FROM channels c
                    LEFT JOIN artists a ON a.channel_id = c.id
                    LEFT JOIN songs s ON s.artist_id = a.id
                    WHERE c.id = ANY(%s)
                    GROUP BY c.id, c.name, c.vermuk
                )
                SELECT *
                FROM channel_stats
                ORDER BY songs DESC
            """, (
                list(ChannelStatisticsRepository.UPLOADED_STATUSES),
                list(ChannelStatisticsRepository.PENDING_STATUSES),
                list(ChannelStatisticsRepository.TAKEDOWN_STATUS),
                channel_ids
            ))
            
            channels = [dict(row) for row in cursor.fetchall()]
            
            # Calculate metrics for comparison
            metrics = {
                'total_channels': len(channels),
                'total_songs': sum(c['songs'] for c in channels),
                'total_artists': sum(c['artists'] for c in channels),
                'avg_songs_per_channel': round(
                    sum(c['songs'] for c in channels) / len(channels), 2
                ) if channels else 0
            }
            
            return {
                'channels': channels,
                'metrics': metrics
            }
            
        except Exception as e:
            logger.error(f"Error comparing channels: {e}")
            raise
    
    # =====================================================
    # BASIC COUNTS (Simple methods)
    # =====================================================
    
    @staticmethod
    def total_channels(cursor) -> int:
        """Get total number of channels."""
        try:
            cursor.execute("SELECT COUNT(*) FROM channels")
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error counting total channels: {e}")
            raise
    
    @staticmethod
    def total_artists(cursor) -> int:
        """Get total number of artists."""
        try:
            cursor.execute("SELECT COUNT(*) FROM artists")
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error counting total artists: {e}")
            raise
    
    @staticmethod
    def total_songs(cursor) -> int:
        """Get total number of songs."""
        try:
            cursor.execute("SELECT COUNT(*) FROM songs")
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error counting total songs: {e}")
            raise
    
    @staticmethod
    def total_vermuk(cursor) -> int:
        """Get total number of vermuk channels."""
        try:
            cursor.execute("SELECT COUNT(*) FROM channels WHERE vermuk = TRUE")
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error counting vermuk channels: {e}")
            raise
    
    @staticmethod
    def total_normal(cursor) -> int:
        """Get total number of normal (non-vermuk) channels."""
        try:
            cursor.execute("SELECT COUNT(*) FROM channels WHERE vermuk = FALSE")
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error counting normal channels: {e}")
            raise
    
    @staticmethod
    def total_songs_by_status(cursor, status: str) -> int:
        """Get total songs by status."""
        try:
            cursor.execute("SELECT COUNT(*) FROM songs WHERE status = %s", (status,))
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error counting songs by status {status}: {e}")
            raise
    
    # =====================================================
    # ADVANCED ANALYTICS
    # =====================================================
    
    @staticmethod
    def get_channel_activity_score(cursor, channel_id: int) -> Dict[str, Any]:
        """
        Calculate activity score for a channel based on various metrics.
        
        Returns:
            Dict with activity scores
        """
        try:
            cursor.execute("""
                WITH metrics AS (
                    SELECT
                        -- Recency score (last 30 days)
                        COUNT(DISTINCT s.id) FILTER (
                            WHERE s.created_at >= CURRENT_DATE - INTERVAL '30 days'
                        ) AS recent_songs,
                        
                        -- Consistency score (songs per month average)
                        COUNT(DISTINCT s.id)::DECIMAL / 
                        NULLIF(EXTRACT(MONTH FROM AGE(CURRENT_DATE, MIN(s.created_at))) + 1, 0) 
                        AS avg_songs_per_month,
                        
                        -- Engagement score (upload rate)
                        COUNT(DISTINCT s.id) FILTER (WHERE s.status = ANY(%s::release_status[]))::DECIMAL /
                        NULLIF(COUNT(DISTINCT s.id), 0) * 100 AS upload_rate,
                        
                        -- Growth score
                        COUNT(DISTINCT s.id) FILTER (
                            WHERE s.created_at >= CURRENT_DATE - INTERVAL '90 days'
                        ) AS songs_last_90_days,
                        
                        COUNT(DISTINCT s.id) FILTER (
                            WHERE s.created_at BETWEEN 
                            CURRENT_DATE - INTERVAL '180 days' AND 
                            CURRENT_DATE - INTERVAL '91 days'
                        ) AS songs_previous_90_days,
                        
                        -- Total metrics
                        COUNT(DISTINCT s.id) AS total_songs,
                        COUNT(DISTINCT a.id) AS total_artists,
                        MAX(s.created_at) AS last_activity
                        
                    FROM artists a
                    LEFT JOIN songs s ON s.artist_id = a.id
                    WHERE a.channel_id = %s
                )
                SELECT
                    *,
                    -- Calculate scores (0-100)
                    CASE 
                        WHEN recent_songs >= 30 THEN 100
                        WHEN recent_songs >= 20 THEN 80
                        WHEN recent_songs >= 10 THEN 60
                        WHEN recent_songs >= 5 THEN 40
                        WHEN recent_songs >= 1 THEN 20
                        ELSE 0
                    END AS recency_score,
                    
                    CASE 
                        WHEN avg_songs_per_month >= 20 THEN 100
                        WHEN avg_songs_per_month >= 10 THEN 75
                        WHEN avg_songs_per_month >= 5 THEN 50
                        WHEN avg_songs_per_month >= 1 THEN 25
                        ELSE 0
                    END AS consistency_score,
                    
                    CASE 
                        WHEN upload_rate >= 90 THEN 100
                        WHEN upload_rate >= 70 THEN 80
                        WHEN upload_rate >= 50 THEN 60
                        WHEN upload_rate >= 30 THEN 40
                        WHEN upload_rate >= 10 THEN 20
                        ELSE 0
                    END AS engagement_score,
                    
                    CASE 
                        WHEN songs_last_90_days > songs_previous_90_days THEN 100
                        WHEN songs_last_90_days = songs_previous_90_days THEN 50
                        ELSE 0
                    END AS growth_score
                    
                FROM metrics
            """, (
                list(ChannelStatisticsRepository.UPLOADED_STATUSES),
                channel_id
            ))
            
            row = cursor.fetchone()
            if not row:
                return {
                    'total_songs': 0,
                    'total_artists': 0,
                    'recent_songs': 0,
                    'recency_score': 0,
                    'consistency_score': 0,
                    'engagement_score': 0,
                    'growth_score': 0,
                    'overall_score': 0,
                    'level': 'Inactive'
                }
            
            result = dict(row)
            
            # Calculate overall score
            result['overall_score'] = round(
                (result.get('recency_score', 0) * 0.35 +
                 result.get('consistency_score', 0) * 0.25 +
                 result.get('engagement_score', 0) * 0.25 +
                 result.get('growth_score', 0) * 0.15),
                2
            )
            
            # Determine level
            score = result['overall_score']
            if score >= 80:
                result['level'] = 'Highly Active'
            elif score >= 60:
                result['level'] = 'Active'
            elif score >= 40:
                result['level'] = 'Moderately Active'
            elif score >= 20:
                result['level'] = 'Low Activity'
            else:
                result['level'] = 'Inactive'
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating activity score for channel {channel_id}: {e}")
            raise
    
    # =====================================================
    # EXPORT / REPORTING
    # =====================================================
    
    @staticmethod
    def export_channel_report(cursor, channel_id: int) -> Dict[str, Any]:
        """
        Generate a complete report for a channel.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            
        Returns:
            Dict with complete channel report
        """
        try:
            report = {}
            
            # Basic info
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
                WHERE id = %s
            """, (channel_id,))
            
            report['channel'] = dict(cursor.fetchone())
            
            # Statistics
            report['stats'] = ChannelStatisticsRepository.get_channel_stats(
                cursor, channel_id
            )
            
            # Status breakdown
            report['status_breakdown'] = ChannelStatisticsRepository.get_status_breakdown_by_channel(
                cursor, channel_id
            )
            
            # Top artists
            report['top_artists'] = ChannelStatisticsRepository.get_top_artists_by_songs(
                cursor, channel_id=channel_id, limit=5
            )
            
            # Activity score
            report['activity'] = ChannelStatisticsRepository.get_channel_activity_score(
                cursor, channel_id
            )
            
            # Growth data (last 6 months)
            report['growth'] = ChannelStatisticsRepository.get_channel_growth(
                cursor, channel_id, months=6
            )
            
            # Timestamp
            report['generated_at'] = datetime.now().isoformat()
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report for channel {channel_id}: {e}")
            raise