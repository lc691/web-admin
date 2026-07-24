"""
Artist Repository - Complete Implementation

Repository untuk tabel artists dengan:
- CRUD operations
- Filtering dan pagination
- Statistics
- Bulk operations
- Optimized queries
"""

from typing import Any, Optional, List, Dict, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ArtistRepository:
    """
    Repository utama untuk tabel artists.
    """

    # =====================================================
    # READ - Single
    # =====================================================

    @staticmethod
    def get_by_id(cursor, artist_id: int) -> Optional[Dict[str, Any]]:
        """
        Get artist by ID with song count.
        
        Args:
            cursor: Database cursor
            artist_id: Artist ID
            
        Returns:
            Artist data with song count or None
        """
        cursor.execute("""
            SELECT
                a.id,
                a.channel_id,
                c.name AS channel_name,
                c.vermuk AS channel_vermuk,
                a.name,
                a.created_at,
                a.updated_at,
                COUNT(DISTINCT s.id) AS song_count,
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
            FROM artists a
            INNER JOIN channels c ON c.id = a.channel_id
            LEFT JOIN songs s ON s.artist_id = a.id
            WHERE a.id = %s
            GROUP BY
                a.id,
                a.channel_id,
                c.name,
                c.vermuk,
                a.name,
                a.created_at,
                a.updated_at
        """, (artist_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_detail(cursor, artist_id: int) -> Optional[Dict[str, Any]]:
        """
        Alias untuk halaman detail artist dengan data lengkap.
        """
        return ArtistRepository.get_by_id(cursor, artist_id)

    @staticmethod
    def get_by_channel_and_name(
        cursor,
        channel_id: int,
        name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get artist by channel ID and name (case-insensitive, trimmed).
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            name: Artist name
            
        Returns:
            Artist data or None
        """
        cursor.execute("""
            SELECT
                id,
                channel_id,
                name,
                created_at,
                updated_at
            FROM artists
            WHERE channel_id = %s
              AND LOWER(TRIM(name)) = LOWER(TRIM(%s))
            LIMIT 1
        """, (channel_id, name))
        
        row = cursor.fetchone()
        return dict(row) if row else None

    # =====================================================
    # READ - List
    # =====================================================

    @staticmethod
    def get_all(
        cursor,
        limit: int = 100,
        offset: int = 0,
        search: Optional[str] = None,
        channel_id: Optional[int] = None,
        order_by: str = "name",
        order_dir: str = "asc"
    ) -> List[Dict[str, Any]]:
        """
        Get all artists with filtering and pagination.
        
        Args:
            cursor: Database cursor
            limit: Max records
            offset: Pagination offset
            search: Search keyword
            channel_id: Filter by channel
            order_by: Sort column
            order_dir: Sort direction
            
        Returns:
            List of artists
        """
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
        params = []
        
        if search:
            query += " AND LOWER(a.name) LIKE LOWER(%s)"
            params.append(f"%{search}%")
        
        if channel_id:
            query += " AND a.channel_id = %s"
            params.append(channel_id)
        
        query += " GROUP BY a.id, a.channel_id, c.name, a.name, a.created_at, a.updated_at"
        
        # Order by
        valid_order_columns = {
            "id": "a.id",
            "name": "LOWER(a.name)",
            "channel": "c.name",
            "song_count": "song_count",
            "created_at": "a.created_at",
            "updated_at": "a.updated_at"
        }
        
        order_column = valid_order_columns.get(order_by, "LOWER(a.name)")
        order_direction = "ASC" if order_dir.lower() == "asc" else "DESC"
        query += f" ORDER BY {order_column} {order_direction}"
        
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_by_channel(
        cursor,
        channel_id: int,
        limit: int = 100,
        offset: int = 0,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all artists for a specific channel.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            limit: Max records
            offset: Pagination offset
            search: Search keyword
            
        Returns:
            List of artists
        """
        return ArtistRepository.get_all(
            cursor,
            limit=limit,
            offset=offset,
            search=search,
            channel_id=channel_id
        )

    @staticmethod
    def get_simple_list(cursor, channel_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get simple list of artists (id, name) for dropdowns.
        
        Args:
            cursor: Database cursor
            channel_id: Optional channel filter
            
        Returns:
            List of {id, name, channel_name}
        """
        query = """
            SELECT
                a.id,
                a.name,
                c.name AS channel_name
            FROM artists a
            INNER JOIN channels c ON c.id = a.channel_id
        """
        params = []
        
        if channel_id:
            query += " WHERE a.channel_id = %s"
            params.append(channel_id)
        
        query += " ORDER BY LOWER(a.name)"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_with_stats(
        cursor,
        artist_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get artist with detailed statistics.
        
        Args:
            cursor: Database cursor
            artist_id: Artist ID
            
        Returns:
            Artist with statistics
        """
        cursor.execute(
            """
            WITH artist_stats AS (
                SELECT
                    a.id,
                    a.channel_id,
                    c.name AS channel_name,
                    c.vermuk AS channel_vermuk,
                    a.name,
                    a.created_at,
                    a.updated_at,

                    COUNT(DISTINCT s.id) AS total_songs,

                    COUNT(DISTINCT s.id) FILTER (
                        WHERE s.status IN ('released', 'topic', 'live', 'no_ads')
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

                    MIN(s.release_date) AS earliest_release,
                    MAX(s.release_date) AS latest_release,

                    MIN(s.created_at) AS first_song,
                    MAX(s.created_at) AS last_song,

                    (
                        SELECT COALESCE(
                            jsonb_object_agg(x.status::text, x.cnt),
                            '{}'::jsonb
                        )
                        FROM (
                            SELECT
                                s2.status,
                                COUNT(*) AS cnt
                            FROM songs s2
                            WHERE s2.artist_id = a.id
                            GROUP BY s2.status
                        ) AS x
                    ) AS status_breakdown

                FROM artists a
                INNER JOIN channels c
                    ON c.id = a.channel_id
                LEFT JOIN songs s
                    ON s.artist_id = a.id

                WHERE a.id = %s

                GROUP BY
                    a.id,
                    a.channel_id,
                    c.name,
                    c.vermuk,
                    a.name,
                    a.created_at,
                    a.updated_at
            )

            SELECT
                *,
                COALESCE(
                    EXTRACT(
                        DAY FROM COALESCE(last_song, created_at) - first_song
                    ),
                    0
                )::INT AS days_active
            FROM artist_stats;
            """
        , (artist_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None

    # =====================================================
    # READ - Existence
    # =====================================================

    @staticmethod
    def exists(cursor, artist_id: int) -> bool:
        """
        Check if artist exists by ID.
        
        Args:
            cursor: Database cursor
            artist_id: Artist ID
            
        Returns:
            True if exists, False otherwise
        """
        cursor.execute("""
            SELECT EXISTS(
                SELECT 1
                FROM artists
                WHERE id = %s
            )
        """, (artist_id,))
        return cursor.fetchone()[0]

    @staticmethod
    def exists_by_name(
        cursor,
        channel_id: int,
        name: str,
        exclude_id: Optional[int] = None,
    ) -> bool:
        """
        Check if artist name exists in a channel.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            name: Artist name
            exclude_id: ID to exclude (for updates)
            
        Returns:
            True if exists, False otherwise
        """
        query = """
            SELECT EXISTS(
                SELECT 1
                FROM artists
                WHERE channel_id = %s
                  AND LOWER(TRIM(name)) = LOWER(TRIM(%s))
        """
        params = [channel_id, name]
        
        if exclude_id is not None:
            query += " AND id <> %s"
            params.append(exclude_id)
        
        query += ")"
        
        cursor.execute(query, params)
        return cursor.fetchone()[0]

    # =====================================================
    # CREATE
    # =====================================================

    @staticmethod
    def create(
        cursor,
        channel_id: int,
        name: str,
    ) -> int:
        """
        Create a new artist.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            name: Artist name
            
        Returns:
            ID of created artist
        """
        cursor.execute("""
            INSERT INTO artists (channel_id, name)
            VALUES (%s, %s)
            RETURNING id
        """, (channel_id, name))
        
        return cursor.fetchone()["id"]

    @staticmethod
    def create_bulk(
        cursor,
        artists: List[Dict[str, Any]]
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Bulk create artists.
        
        Args:
            cursor: Database cursor
            artists: List of artist dicts with channel_id and name
            
        Returns:
            Tuple of (success_count, failed_items)
        """
        success_count = 0
        failed = []
        
        for artist in artists:
            try:
                ArtistRepository.create(
                    cursor,
                    channel_id=artist['channel_id'],
                    name=artist['name']
                )
                success_count += 1
            except Exception as e:
                artist['error'] = str(e)
                failed.append(artist)
        
        return success_count, failed

    # =====================================================
    # UPDATE
    # =====================================================

    @staticmethod
    def update(
        cursor,
        artist_id: int,
        channel_id: int,
        name: str,
    ) -> bool:
        """
        Update an artist.
        
        Args:
            cursor: Database cursor
            artist_id: Artist ID
            channel_id: New channel ID
            name: New name
            
        Returns:
            True if updated, False otherwise
        """
        cursor.execute("""
            UPDATE artists
            SET
                channel_id = %s,
                name = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (channel_id, name, artist_id))
        
        return cursor.rowcount > 0

    @staticmethod
    def update_name(
        cursor,
        artist_id: int,
        name: str
    ) -> bool:
        """
        Update only artist name.
        
        Args:
            cursor: Database cursor
            artist_id: Artist ID
            name: New name
            
        Returns:
            True if updated, False otherwise
        """
        cursor.execute("""
            UPDATE artists
            SET
                name = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (name, artist_id))
        
        return cursor.rowcount > 0

    @staticmethod
    def update_channel(
        cursor,
        artist_id: int,
        channel_id: int
    ) -> bool:
        """
        Update only artist channel.
        
        Args:
            cursor: Database cursor
            artist_id: Artist ID
            channel_id: New channel ID
            
        Returns:
            True if updated, False otherwise
        """
        cursor.execute("""
            UPDATE artists
            SET
                channel_id = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (channel_id, artist_id))
        
        return cursor.rowcount > 0

    # =====================================================
    # DELETE
    # =====================================================

    @staticmethod
    def delete(cursor, artist_id: int) -> bool:
        """
        Delete an artist (cascade deletes songs).
        
        Args:
            cursor: Database cursor
            artist_id: Artist ID
            
        Returns:
            True if deleted, False otherwise
        """
        cursor.execute("""
            DELETE FROM artists
            WHERE id = %s
        """, (artist_id,))
        
        return cursor.rowcount > 0

    @staticmethod
    def delete_bulk(cursor, artist_ids: List[int]) -> int:
        """
        Bulk delete artists.
        
        Args:
            cursor: Database cursor
            artist_ids: List of artist IDs
            
        Returns:
            Number of artists deleted
        """
        if not artist_ids:
            return 0
        
        cursor.execute("""
            DELETE FROM artists
            WHERE id = ANY(%s)
        """, (artist_ids,))
        
        return cursor.rowcount

    @staticmethod
    def delete_by_channel(cursor, channel_id: int) -> int:
        """
        Delete all artists in a channel.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            
        Returns:
            Number of artists deleted
        """
        cursor.execute("""
            DELETE FROM artists
            WHERE channel_id = %s
        """, (channel_id,))
        
        return cursor.rowcount

    # =====================================================
    # STATISTICS
    # =====================================================

    @staticmethod
    def count_all(
        cursor,
        search: Optional[str] = None,
        channel_id: Optional[int] = None
    ) -> int:
        """
        Count total artists with filters.
        
        Args:
            cursor: Database cursor
            search: Search keyword
            channel_id: Filter by channel
            
        Returns:
            Total count
        """
        query = "SELECT COUNT(*) FROM artists WHERE 1=1"
        params = []
        
        if search:
            query += " AND LOWER(name) LIKE LOWER(%s)"
            params.append(f"%{search}%")
        
        if channel_id:
            query += " AND channel_id = %s"
            params.append(channel_id)
        
        cursor.execute(query, params)
        return cursor.fetchone()[0]

    @staticmethod
    def total_songs(cursor, artist_id: int) -> int:
        """
        Get total songs for an artist.
        
        Args:
            cursor: Database cursor
            artist_id: Artist ID
            
        Returns:
            Total songs
        """
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM songs
            WHERE artist_id = %s
        """, (artist_id,))
        
        return cursor.fetchone()["total"]

    @staticmethod
    def get_status_breakdown(cursor, artist_id: int) -> List[Dict[str, Any]]:
        """
        Get song status breakdown for an artist.
        
        Args:
            cursor: Database cursor
            artist_id: Artist ID
            
        Returns:
            List of status breakdown
        """
        cursor.execute("""
            SELECT
                status,
                COUNT(*) AS count
            FROM songs
            WHERE artist_id = %s
            GROUP BY status
            ORDER BY count DESC
        """, (artist_id,))
        
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_top_artists(
        cursor,
        channel_id: Optional[int] = None,
        limit: int = 10,
        min_songs: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get top artists by song count.
        
        Args:
            cursor: Database cursor
            channel_id: Optional channel filter
            limit: Number of artists
            min_songs: Minimum songs
            
        Returns:
            List of top artists
        """
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
                MIN(s.created_at) AS first_song,
                MAX(s.created_at) AS last_song
            FROM artists a
            INNER JOIN channels c ON c.id = a.channel_id
            LEFT JOIN songs s ON s.artist_id = a.id
            WHERE 1=1
        """
        params = []
        
        if channel_id:
            query += " AND a.channel_id = %s"
            params.append(channel_id)
        
        query += """
            GROUP BY a.id, a.name, a.channel_id, c.name
            HAVING COUNT(DISTINCT s.id) >= %s
            ORDER BY song_count DESC
            LIMIT %s
        """
        params.extend([min_songs, limit])
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # =====================================================
    # CHANNEL HELPERS
    # =====================================================

    @staticmethod
    def get_channels(cursor) -> List[Dict[str, Any]]:
        """
        Get all channels for dropdown.
        
        Args:
            cursor: Database cursor
            
        Returns:
            List of channels
        """
        cursor.execute("""
            SELECT
                id,
                name
            FROM channels
            ORDER BY LOWER(name)
        """)
        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_channel(cursor, channel_id: int) -> Optional[Dict[str, Any]]:
        """
        Get channel by ID.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            
        Returns:
            Channel data or None
        """
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
        
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def get_channel_stats(cursor, channel_id: int) -> Dict[str, Any]:
        """
        Get channel statistics for artists.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            
        Returns:
            Channel stats
        """
        cursor.execute("""
            SELECT
                COUNT(DISTINCT a.id) AS total_artists,
                COUNT(DISTINCT a.id) FILTER (
                    WHERE EXISTS (SELECT 1 FROM songs s WHERE s.artist_id = a.id)
                ) AS artists_with_songs,
                COUNT(DISTINCT s.id) AS total_songs,
                AVG(song_counts.song_count)::DECIMAL(10,2) AS avg_songs_per_artist
            FROM channels c
            LEFT JOIN artists a ON a.channel_id = c.id
            LEFT JOIN songs s ON s.artist_id = a.id
            LEFT JOIN (
                SELECT artist_id, COUNT(*) AS song_count
                FROM songs
                GROUP BY artist_id
            ) song_counts ON song_counts.artist_id = a.id
            WHERE c.id = %s
            GROUP BY c.id
        """, (channel_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else {}

    # =====================================================
    # SEARCH / FILTER
    # =====================================================

    @staticmethod
    def search(
        cursor,
        keyword: str,
        channel_id: Optional[int] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search artists by keyword.
        
        Args:
            cursor: Database cursor
            keyword: Search keyword
            channel_id: Optional channel filter
            limit: Max records
            
        Returns:
            List of matching artists
        """
        query = """
            SELECT
                a.id,
                a.channel_id,
                c.name AS channel_name,
                a.name,
                COUNT(DISTINCT s.id) AS song_count
            FROM artists a
            INNER JOIN channels c ON c.id = a.channel_id
            LEFT JOIN songs s ON s.artist_id = a.id
            WHERE LOWER(a.name) LIKE LOWER(%s)
        """
        params = [f"%{keyword}%"]
        
        if channel_id:
            query += " AND a.channel_id = %s"
            params.append(channel_id)
        
        query += """
            GROUP BY a.id, a.channel_id, c.name, a.name
            ORDER BY LOWER(a.name)
            LIMIT %s
        """
        params.append(limit)
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # =====================================================
    # BULK OPERATIONS
    # =====================================================

    @staticmethod
    def bulk_exists(cursor, artist_ids: List[int]) -> List[int]:
        """
        Get existing artist IDs from a list.
        
        Args:
            cursor: Database cursor
            artist_ids: List of artist IDs
            
        Returns:
            List of existing IDs
        """
        if not artist_ids:
            return []
        
        cursor.execute("""
            SELECT id
            FROM artists
            WHERE id = ANY(%s)
            ORDER BY id
        """, (artist_ids,))
        
        return [row[0] for row in cursor.fetchall()]

    @staticmethod
    def bulk_update_channel(
        cursor,
        artist_ids: List[int],
        channel_id: int
    ) -> int:
        """
        Bulk update channel for artists.
        
        Args:
            cursor: Database cursor
            artist_ids: List of artist IDs
            channel_id: New channel ID
            
        Returns:
            Number of artists updated
        """
        if not artist_ids:
            return 0
        
        cursor.execute("""
            UPDATE artists
            SET
                channel_id = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ANY(%s)
        """, (channel_id, artist_ids))
        
        return cursor.rowcount

    # =====================================================
    # EXPORT
    # =====================================================

    @staticmethod
    def export_by_channel(
        cursor,
        channel_id: int,
        format: str = "csv"
    ) -> List[Dict[str, Any]]:
        """
        Export all artists in a channel.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            format: Export format (csv or json)
            
        Returns:
            List of artists with song counts
        """
        cursor.execute("""
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
            ORDER BY LOWER(a.name)
        """, (channel_id,))
        
        return [dict(row) for row in cursor.fetchall()]

    # =====================================================
    # VALIDATION HELPERS
    # =====================================================

    @staticmethod
    def validate_name(name: str) -> str:
        """
        Validate and clean artist name.
        
        Args:
            name: Artist name
            
        Returns:
            Cleaned name
            
        Raises:
            ValueError: If name is invalid
        """
        if not name:
            raise ValueError("Artist name is required")
        
        name = name.strip()
        
        if len(name) < 2:
            raise ValueError("Artist name must be at least 2 characters")
        
        if len(name) > 255:
            raise ValueError("Artist name must be less than 255 characters")
        
        return name