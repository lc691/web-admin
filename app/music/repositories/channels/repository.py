"""
Channel Repository - Complete Implementation

Repository pattern untuk tabel channels dengan:
- Optimasi query (subquery vs JOIN)
- Validasi data lengkap
- Error handling yang baik
- Type hints lengkap
- Documentation jelas
- Performance optimized
"""

from typing import Any, Optional, List, Dict, Tuple
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)


class ChannelRepository:
    """
    Repository untuk operasi CRUD dan query kompleks pada tabel channels.
    
    Semua method menggunakan cursor dari connection pool.
    Mengembalikan data dalam bentuk dictionary untuk memudahkan serialisasi.
    """
    
    # =====================================================
    # CONSTANTS - Status yang sering dipakai
    # =====================================================
    
    UPLOADED_STATUSES = ('released', 'topic', 'live', 'no_ads')
    PENDING_STATUSES = ('draft', 'review', 'approved', 'scheduled', 'unreleased')
    TAKEDOWN_STATUS = ('take_down',)
    ALL_STATUSES = UPLOADED_STATUSES + PENDING_STATUSES + TAKEDOWN_STATUS
    
    # =====================================================
    # READ - Basic Queries
    # =====================================================
    
    @staticmethod
    def get_by_id(
        cursor,
        channel_id: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Get channel by ID beserta statistik.

        Args:
            cursor: Database cursor
            channel_id: Channel ID

        Returns:
            Dict channel atau None jika tidak ditemukan.
        """
        try:
            logger.debug(
                "Getting channel ID=%s",
                channel_id,
            )

            cursor.execute("""
                SELECT
                    c.id,
                    c.name,
                    c.email,
                    c.password,
                    c.vermuk,
                    c.notes,
                    c.created_at,
                    c.updated_at,

                    -- ==========================================
                    -- TOTAL ARTISTS
                    -- ==========================================

                    (
                        SELECT COUNT(*)
                        FROM artists a
                        WHERE a.channel_id = c.id
                    ) AS total_artists,

                    -- ==========================================
                    -- TOTAL SONGS
                    -- ==========================================

                    (
                        SELECT COUNT(*)
                        FROM songs s
                        JOIN artists a
                            ON a.id = s.artist_id
                        WHERE a.channel_id = c.id
                    ) AS total_songs,

                    -- ==========================================
                    -- UPLOADED
                    -- ==========================================

                    (
                        SELECT COUNT(*)
                        FROM songs s
                        JOIN artists a
                            ON a.id = s.artist_id
                        WHERE a.channel_id = c.id
                        AND s.status = ANY(%s::release_status[])
                    ) AS uploaded_songs,

                    -- ==========================================
                    -- PENDING
                    -- ==========================================

                    (
                        SELECT COUNT(*)
                        FROM songs s
                        JOIN artists a
                            ON a.id = s.artist_id
                        WHERE a.channel_id = c.id
                        AND s.status = ANY(%s::release_status[])
                    ) AS pending_songs,

                    -- ==========================================
                    -- TAKE DOWN
                    -- ==========================================

                    (
                        SELECT COUNT(*)
                        FROM songs s
                        JOIN artists a
                            ON a.id = s.artist_id
                        WHERE a.channel_id = c.id
                        AND s.status = ANY(%s::release_status[])
                    ) AS take_down_songs,

                    -- ==========================================
                    -- STATUS BREAKDOWN
                    -- ==========================================

                    COALESCE(
                        (
                            SELECT jsonb_object_agg(status, total)
                            FROM (
                                SELECT
                                    s.status,
                                    COUNT(*) AS total
                                FROM songs s
                                JOIN artists a
                                    ON a.id = s.artist_id
                                WHERE a.channel_id = c.id
                                GROUP BY s.status
                            ) x
                        ),
                        '{}'::jsonb
                    ) AS status_breakdown

                FROM channels c
                WHERE c.id = %s
            """, (
                list(ChannelRepository.UPLOADED_STATUSES),
                list(ChannelRepository.PENDING_STATUSES),
                list(ChannelRepository.TAKEDOWN_STATUS),
                channel_id,
            ))

            row = cursor.fetchone()

            return dict(row) if row else None

        except Exception:
            logger.exception(
                "Failed to get channel ID=%s",
                channel_id,
            )
            raise
    
    @staticmethod
    def get_by_name(cursor, name: str) -> Optional[Dict[str, Any]]:
        """
        Get channel by name (case-insensitive, trimmed).
        
        Args:
            cursor: Database cursor
            name: Nama channel yang dicari
            
        Returns:
            Dict channel atau None jika tidak ditemukan
        """
        try:
            cursor.execute("""
                SELECT 
                    id,
                    name,
                    email,
                    password,
                    vermuk,
                    notes,
                    created_at,
                    updated_at
                FROM channels
                WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s))
            """, (name,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
            
        except Exception as e:
            logger.error(f"Error getting channel by name '{name}': {e}")
            raise
    
    @staticmethod
    def get_by_email(cursor, email: str) -> Optional[Dict[str, Any]]:
        """
        Get channel by email (exact match, case-sensitive for email).
        
        Args:
            cursor: Database cursor
            email: Email channel yang dicari
            
        Returns:
            Dict channel atau None jika tidak ditemukan
        """
        try:
            cursor.execute("""
                SELECT 
                    id,
                    name,
                    email,
                    password,
                    vermuk,
                    notes,
                    created_at,
                    updated_at
                FROM channels
                WHERE email = %s
            """, (email,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
            
        except Exception as e:
            logger.error(f"Error getting channel by email '{email}': {e}")
            raise
    
    @staticmethod
    def get_all(
        cursor,
        limit: int = 100,
        offset: int = 0,
        search: Optional[str] = None,
        vermuk: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all channels with filtering and pagination.
        
        Args:
            cursor: Database cursor
            limit: Max records per page (default 100)
            offset: Number of records to skip
            search: Search term for name or email
            vermuk: Filter by vermuk status
            
        Returns:
            List of channel dictionaries
        """
        try:
            query = """
                SELECT 
                    id,
                    name,
                    email,
                    vermuk,
                    notes,
                    created_at,
                    updated_at
                FROM channels
                WHERE 1=1
            """
            params = []
            
            # Search filter
            if search:
                query += """
                    AND (
                        LOWER(name) LIKE LOWER(%s) 
                        OR LOWER(email) LIKE LOWER(%s)
                    )
                """
                search_pattern = f'%{search}%'
                params.extend([search_pattern, search_pattern])
            
            # Vermuk filter
            if vermuk is not None:
                query += " AND vermuk = %s"
                params.append(vermuk)
            
            # Order dan pagination
            query += " ORDER BY name LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error getting all channels: {e}")
            raise
    
    @staticmethod
    def get_simple_list(cursor) -> List[Dict[str, Any]]:
        """
        Get simple list of channels (id, name) untuk dropdown/select.
        
        Args:
            cursor: Database cursor
            
        Returns:
            List of {id, name} dictionaries
        """
        try:
            cursor.execute("""
                SELECT 
                    id,
                    name
                FROM channels
                ORDER BY name
            """)
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error getting simple channel list: {e}")
            raise
    
    # =====================================================
    # READ - Advanced / Statistics
    # =====================================================
    
    @staticmethod
    def get_detailed_stats(cursor, channel_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed statistics for a channel.
        
        Args:
            cursor: Database cursor
            channel_id: ID channel
            
        Returns:
            Dict dengan statistik detail atau None jika channel tidak ditemukan
        """
        try:
            # Cek apakah channel exists
            if not ChannelRepository.exists(cursor, channel_id):
                return None
            
            result = {}
            
            # 1. Basic info
            cursor.execute("""
                SELECT 
                    id,
                    name,
                    email,
                    vermuk,
                    created_at,
                    updated_at
                FROM channels
                WHERE id = %s
            """, (channel_id,))
            result['channel'] = dict(cursor.fetchone())
            
            # 2. Artist count
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM artists
                WHERE channel_id = %s
            """, (channel_id,))
            result['total_artists'] = cursor.fetchone()['count']
            
            # 3. Song statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_songs,
                    COUNT(*) FILTER (WHERE s.status = ANY(%s::release_status[])) as uploaded,
                    COUNT(*) FILTER (WHERE s.status = ANY(%s::release_status[])) as pending,
                    COUNT(*) FILTER (WHERE s.status = ANY(%s::release_status[])) as takedown,
                    MIN(s.created_at) as first_song,
                    MAX(s.created_at) as last_song
                FROM songs s
                INNER JOIN artists a ON s.artist_id = a.id
                WHERE a.channel_id = %s
            """, (
                list(ChannelRepository.UPLOADED_STATUSES),
                list(ChannelRepository.PENDING_STATUSES),
                list(ChannelRepository.TAKEDOWN_STATUS),
                channel_id
            ))
            
            stats = cursor.fetchone()
            result.update(dict(stats) if stats else {})
            
            # 4. Status breakdown
            cursor.execute("""
                SELECT 
                    s.status,
                    COUNT(*) as count,
                    MIN(s.created_at) as oldest,
                    MAX(s.created_at) as newest
                FROM songs s
                INNER JOIN artists a ON s.artist_id = a.id
                WHERE a.channel_id = %s
                GROUP BY s.status
                ORDER BY s.status
            """, (channel_id,))
            
            result['status_breakdown'] = [dict(row) for row in cursor.fetchall()]
            
            # 5. Artist dengan songs terbanyak
            cursor.execute("""
                SELECT 
                    a.id,
                    a.name,
                    COUNT(s.id) as song_count,
                    MIN(s.created_at) as first_song,
                    MAX(s.created_at) as last_song
                FROM artists a
                LEFT JOIN songs s ON s.artist_id = a.id
                WHERE a.channel_id = %s
                GROUP BY a.id, a.name
                ORDER BY song_count DESC
                LIMIT 10
            """, (channel_id,))
            
            result['top_artists'] = [dict(row) for row in cursor.fetchall()]
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting detailed stats for channel {channel_id}: {e}")
            raise
    
    @staticmethod
    def get_status_summary(cursor) -> List[Dict[str, Any]]:
        """
        Get summary of channels by status.
        
        Returns:
            List of channel status summaries
        """
        try:
            cursor.execute("""
                SELECT 
                    c.id,
                    c.name,
                    c.vermuk,
                    COUNT(DISTINCT a.id) as artist_count,
                    COUNT(s.id) as song_count,
                    COUNT(s.id) FILTER (WHERE s.status = ANY(%s::release_status[])) as uploaded,
                    COUNT(s.id) FILTER (WHERE s.status = ANY(%s::release_status[])) as pending,
                    COUNT(s.id) FILTER (WHERE s.status = ANY(%s::release_status[])) as takedown
                FROM channels c
                LEFT JOIN artists a ON a.channel_id = c.id
                LEFT JOIN songs s ON s.artist_id = a.id
                GROUP BY c.id, c.name, c.vermuk
                ORDER BY c.name
            """, (
                list(ChannelRepository.UPLOADED_STATUSES),
                list(ChannelRepository.PENDING_STATUSES),
                list(ChannelRepository.TAKEDOWN_STATUS)
            ))
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error getting status summary: {e}")
            raise
    
    # =====================================================
    # CREATE
    # =====================================================
    
    @staticmethod
    def create(
        cursor,
        *,
        name: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        vermuk: bool = False,
        notes: Optional[str] = None,
    ) -> int:
        """
        Create a new channel with validation.
        
        Args:
            cursor: Database cursor
            name: Channel name (required, unique)
            email: Channel email (optional, unique if provided)
            password: Channel password (optional)
            vermuk: Vermuk status (default False)
            notes: Additional notes (optional)
            
        Returns:
            ID of newly created channel
            
        Raises:
            ValueError: If name or email already exists
        """
        try:
            # Validate name is provided
            if not name or not name.strip():
                raise ValueError("Channel name is required")
            
            name = name.strip()
            
            # Check name uniqueness
            if ChannelRepository.exists_name(cursor, name):
                raise ValueError(f"Channel with name '{name}' already exists")
            
            # Check email uniqueness (if provided)
            if email:
                email = email.strip()
                if ChannelRepository.exists_email(cursor, email):
                    raise ValueError(f"Channel with email '{email}' already exists")
            
            # Insert channel
            cursor.execute("""
                INSERT INTO channels
                (
                    name,
                    email,
                    password,
                    vermuk,
                    notes
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                name,
                email,
                password,
                vermuk,
                notes,
            ))
            
            channel_id = cursor.fetchone()['id']
            logger.info(f"Created channel '{name}' with ID {channel_id}")
            return channel_id
            
        except ValueError as e:
            logger.warning(f"Validation error creating channel: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating channel '{name}': {e}")
            raise
    
    @staticmethod
    def create_bulk(
        cursor,
        channels: List[Dict[str, Any]]
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Bulk create multiple channels.
        
        Args:
            cursor: Database cursor
            channels: List of channel dictionaries
            
        Returns:
            Tuple of (success_count, failed_channels)
        """
        success_count = 0
        failed = []
        
        for channel_data in channels:
            try:
                ChannelRepository.create(
                    cursor,
                    name=channel_data['name'],
                    email=channel_data.get('email'),
                    password=channel_data.get('password'),
                    vermuk=channel_data.get('vermuk', False),
                    notes=channel_data.get('notes'),
                )
                success_count += 1
            except Exception as e:
                channel_data['error'] = str(e)
                failed.append(channel_data)
        
        return success_count, failed
    
    # =====================================================
    # UPDATE
    # =====================================================
    
    @staticmethod
    def update(
        cursor,
        channel_id: int,
        *,
        name: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        vermuk: bool = False,
        notes: Optional[str] = None,
    ) -> bool:
        """
        Update an existing channel with validation.
        
        Args:
            cursor: Database cursor
            channel_id: ID of channel to update
            name: Channel name (required)
            email: Channel email (optional)
            password: Channel password (optional)
            vermuk: Vermuk status
            notes: Additional notes (optional)
            
        Returns:
            True if updated successfully
            
        Raises:
            ValueError: If name or email already exists for different channel
            ValueError: If channel not found
        """
        try:
            # Validate name
            if not name or not name.strip():
                raise ValueError("Channel name is required")
            
            name = name.strip()
            
            # Check if channel exists
            if not ChannelRepository.exists(cursor, channel_id):
                raise ValueError(f"Channel with ID {channel_id} not found")
            
            # Check name uniqueness (exclude current channel)
            if ChannelRepository.exists_name(cursor, name, exclude_id=channel_id):
                raise ValueError(f"Channel with name '{name}' already exists")
            
            # Check email uniqueness (if provided, exclude current channel)
            if email:
                email = email.strip()
                if ChannelRepository.exists_email(cursor, email, exclude_id=channel_id):
                    raise ValueError(f"Channel with email '{email}' already exists")
            
            # Update channel
            cursor.execute("""
                UPDATE channels
                SET
                    name = %s,
                    email = %s,
                    password = %s,
                    vermuk = %s,
                    notes = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (
                name,
                email,
                password,
                vermuk,
                notes,
                channel_id,
            ))
            
            updated = cursor.rowcount > 0
            if updated:
                logger.info(f"Updated channel {channel_id}: '{name}'")
            return updated
            
        except ValueError as e:
            logger.warning(f"Validation error updating channel {channel_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error updating channel {channel_id}: {e}")
            raise
    
    @staticmethod
    def update_vermuk_bulk(cursor, channel_ids: List[int], vermuk: bool) -> int:
        """
        Bulk update vermuk status for multiple channels.
        
        Args:
            cursor: Database cursor
            channel_ids: List of channel IDs
            vermuk: Vermuk status to set
            
        Returns:
            Number of channels updated
        """
        try:
            if not channel_ids:
                return 0
            
            cursor.execute("""
                UPDATE channels
                SET 
                    vermuk = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ANY(%s)
            """, (vermuk, channel_ids))
            
            updated_count = cursor.rowcount
            logger.info(f"Updated vermuk to {vermuk} for {updated_count} channels")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error bulk updating vermuk: {e}")
            raise
    
    @staticmethod
    def update_notes(cursor, channel_id: int, notes: str) -> bool:
        """
        Update notes only for a channel.
        
        Args:
            cursor: Database cursor
            channel_id: ID of channel
            notes: New notes text
            
        Returns:
            True if updated successfully
        """
        try:
            cursor.execute("""
                UPDATE channels
                SET 
                    notes = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (notes, channel_id))
            
            return cursor.rowcount > 0
            
        except Exception as e:
            logger.error(f"Error updating notes for channel {channel_id}: {e}")
            raise
    
    # =====================================================
    # DELETE
    # =====================================================
    
    @staticmethod
    def delete(cursor, channel_id: int) -> bool:
        """
        Delete a channel (cascade will delete artists and songs).
        
        Args:
            cursor: Database cursor
            channel_id: ID of channel to delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            ValueError: If channel not found
        """
        try:
            # Check if channel exists
            if not ChannelRepository.exists(cursor, channel_id):
                raise ValueError(f"Channel with ID {channel_id} not found")
            
            cursor.execute("""
                DELETE FROM channels
                WHERE id = %s
            """, (channel_id,))
            
            deleted = cursor.rowcount > 0
            if deleted:
                logger.warning(f"Deleted channel {channel_id}")
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting channel {channel_id}: {e}")
            raise
    
    @staticmethod
    def delete_bulk(cursor, channel_ids: List[int]) -> int:
        """
        Bulk delete multiple channels.
        
        Args:
            cursor: Database cursor
            channel_ids: List of channel IDs to delete
            
        Returns:
            Number of channels deleted
        """
        try:
            if not channel_ids:
                return 0
            
            cursor.execute("""
                DELETE FROM channels
                WHERE id = ANY(%s)
            """, (channel_ids,))
            
            deleted_count = cursor.rowcount
            logger.warning(f"Deleted {deleted_count} channels")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error bulk deleting channels: {e}")
            raise
    
    # =====================================================
    # EXISTS
    # =====================================================
    
    @staticmethod
    def exists(cursor, channel_id: int) -> bool:
        """
        Check if a channel exists by ID.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID to check
            
        Returns:
            True if channel exists, False otherwise
        """
        try:
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1
                    FROM channels
                    WHERE id = %s
                )
            """, (channel_id,))
            
            return cursor.fetchone()[0]
            
        except Exception as e:
            logger.error(f"Error checking existence for channel {channel_id}: {e}")
            raise
    
    @staticmethod
    def exists_name(
        cursor,
        name: str,
        exclude_id: Optional[int] = None,
    ) -> bool:
        """
        Check if a channel name exists (case-insensitive, trimmed).
        
        Args:
            cursor: Database cursor
            name: Channel name to check
            exclude_id: Optional channel ID to exclude from check
            
        Returns:
            True if name exists (not counting excluded), False otherwise
        """
        try:
            if exclude_id is None:
                cursor.execute("""
                    SELECT EXISTS(
                        SELECT 1
                        FROM channels
                        WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s))
                    )
                """, (name,))
            else:
                cursor.execute("""
                    SELECT EXISTS(
                        SELECT 1
                        FROM channels
                        WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s))
                          AND id <> %s
                    )
                """, (name, exclude_id))
            
            return cursor.fetchone()[0]
            
        except Exception as e:
            logger.error(f"Error checking name existence for '{name}': {e}")
            raise
    
    @staticmethod
    def exists_email(
        cursor,
        email: str,
        exclude_id: Optional[int] = None,
    ) -> bool:
        """
        Check if a channel email exists (exact match, case-sensitive).
        
        Args:
            cursor: Database cursor
            email: Email to check
            exclude_id: Optional channel ID to exclude from check
            
        Returns:
            True if email exists (not counting excluded), False otherwise
        """
        try:
            if not email:
                return False
            
            if exclude_id is None:
                cursor.execute("""
                    SELECT EXISTS(
                        SELECT 1
                        FROM channels
                        WHERE email = %s
                    )
                """, (email,))
            else:
                cursor.execute("""
                    SELECT EXISTS(
                        SELECT 1
                        FROM channels
                        WHERE email = %s
                          AND id <> %s
                    )
                """, (email, exclude_id))
            
            return cursor.fetchone()[0]
            
        except Exception as e:
            logger.error(f"Error checking email existence for '{email}': {e}")
            raise
    
    # =====================================================
    # COUNT
    # =====================================================
    
    @staticmethod
    def count_all(
        cursor,
        search: Optional[str] = None,
        vermuk: Optional[bool] = None
    ) -> int:
        """
        Get total count of channels with filters.
        
        Args:
            cursor: Database cursor
            search: Search term for name or email
            vermuk: Filter by vermuk status
            
        Returns:
            Total count
        """
        try:
            query = "SELECT COUNT(*) FROM channels WHERE 1=1"
            params = []
            
            if search:
                query += """
                    AND (LOWER(name) LIKE LOWER(%s) OR LOWER(email) LIKE LOWER(%s))
                """
                search_pattern = f'%{search}%'
                params.extend([search_pattern, search_pattern])
            
            if vermuk is not None:
                query += " AND vermuk = %s"
                params.append(vermuk)
            
            cursor.execute(query, params)
            return cursor.fetchone()[0]
            
        except Exception as e:
            logger.error(f"Error counting channels: {e}")
            raise
    
    @staticmethod
    def count_by_vermuk(cursor) -> Dict[str, int]:
        """
        Count channels by vermuk status.
        
        Returns:
            Dict with 'true' and 'false' counts
        """
        try:
            cursor.execute("""
                SELECT 
                    vermuk,
                    COUNT(*) as count
                FROM channels
                GROUP BY vermuk
            """)
            
            results = {row['vermuk']: row['count'] for row in cursor.fetchall()}
            return {
                'true': results.get(True, 0),
                'false': results.get(False, 0),
                'total': results.get(True, 0) + results.get(False, 0)
            }
            
        except Exception as e:
            logger.error(f"Error counting by vermuk: {e}")
            raise
    
    # =====================================================
    # UTILITY
    # =====================================================
    
    @staticmethod
    def get_or_create(
        cursor,
        *,
        name: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        vermuk: bool = False,
        notes: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], bool]:
        """
        Get a channel by name, or create it if it doesn't exist.
        
        Args:
            cursor: Database cursor
            name: Channel name
            email: Channel email
            password: Channel password
            vermuk: Vermuk status
            notes: Additional notes
            
        Returns:
            Tuple of (channel_dict, created_flag)
        """
        try:
            # Try to get existing channel
            existing = ChannelRepository.get_by_name(cursor, name)
            if existing:
                return existing, False
            
            # Create new channel
            channel_id = ChannelRepository.create(
                cursor,
                name=name,
                email=email,
                password=password,
                vermuk=vermuk,
                notes=notes,
            )
            
            # Get the created channel
            channel = ChannelRepository.get_by_id(cursor, channel_id)
            return channel, True
            
        except Exception as e:
            logger.error(f"Error in get_or_create for '{name}': {e}")
            raise