"""
Artist Bulk Repository - Complete Implementation

Repository untuk operasi bulk Artist dengan:
- Bulk delete with validation
- Bulk update (channel, name)
- Bulk insert with conflict handling
- Bulk exists checking
- Batch processing
- Detailed results with success/failure tracking
"""

from typing import Any, List, Dict, Optional, Tuple, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ArtistBulkRepository:
    """
    Repository untuk operasi bulk Artist.
    """

    # =====================================================
    # BULK DELETE
    # =====================================================

    @staticmethod
    def bulk_delete(
        cursor,
        artist_ids: List[int],
        return_details: bool = False
    ) -> Union[int, Dict[str, Any]]:
        """
        Hapus banyak artist sekaligus.
        
        Args:
            cursor: Database cursor
            artist_ids: List of artist IDs
            return_details: Return detailed results
            
        Returns:
            - If return_details=False: Number of artists deleted
            - If return_details=True: Dict with deletion details
        """
        if not artist_ids:
            return 0 if not return_details else {
                'deleted_count': 0,
                'deleted_ids': [],
                'not_found': [],
                'artists_with_songs': []
            }

        # Get existing IDs
        existing_ids = ArtistBulkRepository.existing_ids(cursor, artist_ids)
        not_found = [id for id in artist_ids if id not in existing_ids]

        if not existing_ids:
            return 0 if not return_details else {
                'deleted_count': 0,
                'deleted_ids': [],
                'not_found': not_found,
                'artists_with_songs': []
            }

        # Check artists with songs
        artists_with_songs = ArtistBulkRepository.artists_with_songs(
            cursor, existing_ids
        )
        artists_with_songs_ids = [row['id'] for row in artists_with_songs]

        # Filter IDs that can be deleted (no songs)
        ids_to_delete = [
            id for id in existing_ids 
            if id not in artists_with_songs_ids
        ]

        if not ids_to_delete:
            logger.warning(f"No artists to delete (all have songs): {artist_ids}")
            return 0 if not return_details else {
                'deleted_count': 0,
                'deleted_ids': [],
                'not_found': not_found,
                'artists_with_songs': artists_with_songs
            }

        # Get artist names before deletion (for logging)
        if return_details:
            cursor.execute("""
                SELECT id, name
                FROM artists
                WHERE id = ANY(%s)
            """, (ids_to_delete,))
            deleted_info = [dict(row) for row in cursor.fetchall()]

        # Execute deletion
        cursor.execute("""
            DELETE FROM artists
            WHERE id = ANY(%s)
            RETURNING id, name
        """, (ids_to_delete,))

        deleted_rows = cursor.fetchall()
        deleted_count = len(deleted_rows)

        logger.info(f"Bulk deleted {deleted_count} artists")

        if return_details:
            return {
                'deleted_count': deleted_count,
                'deleted_ids': [row['id'] for row in deleted_rows],
                'deleted_names': [row['name'] for row in deleted_rows],
                'not_found': not_found,
                'artists_with_songs': artists_with_songs,
                'total_requested': len(artist_ids)
            }

        return deleted_count

    @staticmethod
    def bulk_delete_force(
        cursor,
        artist_ids: List[int],
        cascade_delete_songs: bool = True
    ) -> Dict[str, Any]:
        """
        Force delete artists including their songs.
        
        Args:
            cursor: Database cursor
            artist_ids: List of artist IDs
            cascade_delete_songs: Delete songs too (cascade)
            
        Returns:
            Dict with deletion details
        """
        if not artist_ids:
            return {
                'deleted_artists': 0,
                'deleted_songs': 0,
                'deleted_ids': [],
                'not_found': []
            }

        # Get existing IDs
        existing_ids = ArtistBulkRepository.existing_ids(cursor, artist_ids)
        not_found = [id for id in artist_ids if id not in existing_ids]

        if not existing_ids:
            return {
                'deleted_artists': 0,
                'deleted_songs': 0,
                'deleted_ids': [],
                'not_found': not_found
            }

        # Count songs before deletion
        song_count = ArtistBulkRepository.total_songs(cursor, existing_ids)

        # Delete artists (cascade will delete songs if ON DELETE CASCADE)
        cursor.execute("""
            DELETE FROM artists
            WHERE id = ANY(%s)
            RETURNING id, name
        """, (existing_ids,))

        deleted_rows = cursor.fetchall()

        return {
            'deleted_artists': len(deleted_rows),
            'deleted_songs': song_count,
            'deleted_ids': [row['id'] for row in deleted_rows],
            'deleted_names': [row['name'] for row in deleted_rows],
            'not_found': not_found,
            'total_requested': len(artist_ids)
        }

    # =====================================================
    # BULK UPDATE
    # =====================================================

    @staticmethod
    def bulk_update_channel(
        cursor,
        artist_ids: List[int],
        channel_id: int,
        validate_exists: bool = True
    ) -> Dict[str, Any]:
        """
        Bulk update channel for artists.
        
        Args:
            cursor: Database cursor
            artist_ids: List of artist IDs
            channel_id: New channel ID
            validate_exists: Validate IDs exist
            
        Returns:
            Dict with update results
        """
        if not artist_ids:
            return {
                'updated_count': 0,
                'updated_ids': [],
                'not_found': [],
                'skipped': []
            }

        ids_list = list(set(artist_ids))  # Remove duplicates

        # Validate existence
        not_found = []
        if validate_exists:
            existing_ids = ArtistBulkRepository.existing_ids(cursor, ids_list)
            not_found = [id for id in ids_list if id not in existing_ids]
            ids_to_update = existing_ids
        else:
            ids_to_update = ids_list

        if not ids_to_update:
            return {
                'updated_count': 0,
                'updated_ids': [],
                'not_found': not_found,
                'skipped': []
            }

        # Execute update
        cursor.execute("""
            UPDATE artists
            SET
                channel_id = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ANY(%s)
            RETURNING id, name
        """, (channel_id, ids_to_update))

        updated_rows = cursor.fetchall()

        logger.info(f"Bulk updated channel to {channel_id} for {len(updated_rows)} artists")

        return {
            'updated_count': len(updated_rows),
            'updated_ids': [row['id'] for row in updated_rows],
            'updated_names': [row['name'] for row in updated_rows],
            'not_found': not_found,
            'total_requested': len(ids_list)
        }

    @staticmethod
    def bulk_update_name(
        cursor,
        updates: Dict[int, str]
    ) -> Dict[str, Any]:
        """
        Bulk update names for artists.
        
        Args:
            cursor: Database cursor
            updates: Dict mapping artist_id -> new_name
            
        Returns:
            Dict with update results
        """
        if not updates:
            return {
                'updated_count': 0,
                'updated_ids': [],
                'failed': []
            }

        artist_ids = list(updates.keys())
        existing_ids = ArtistBulkRepository.existing_ids(cursor, artist_ids)
        not_found = [id for id in artist_ids if id not in existing_ids]

        updated_ids = []
        failed = []

        for artist_id in existing_ids:
            try:
                new_name = updates[artist_id]
                cursor.execute("""
                    UPDATE artists
                    SET
                        name = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    RETURNING id
                """, (new_name, artist_id))

                if cursor.rowcount > 0:
                    updated_ids.append(artist_id)
                else:
                    failed.append({'id': artist_id, 'reason': 'Update failed'})

            except Exception as e:
                failed.append({'id': artist_id, 'reason': str(e)})

        logger.info(f"Bulk updated names for {len(updated_ids)} artists")

        return {
            'updated_count': len(updated_ids),
            'updated_ids': updated_ids,
            'not_found': not_found,
            'failed': failed
        }

    @staticmethod
    def bulk_update_multiple_fields(
        cursor,
        updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Bulk update multiple fields for artists.
        
        Args:
            cursor: Database cursor
            updates: List of dicts with 'id' and fields to update
            
        Returns:
            Dict with update results
        """
        if not updates:
            return {
                'updated_count': 0,
                'updated_ids': [],
                'failed': []
            }

        allowed_fields = {'name', 'channel_id'}
        failed = []
        updated_ids = []

        for update_data in updates:
            artist_id = update_data.get('id')
            if not artist_id:
                failed.append({'data': update_data, 'reason': 'Missing ID'})
                continue

            # Filter allowed fields
            fields_to_update = {
                k: v for k, v in update_data.items()
                if k in allowed_fields and k != 'id'
            }

            if not fields_to_update:
                failed.append({'id': artist_id, 'reason': 'No valid fields to update'})
                continue

            try:
                # Build SET clause dynamically
                set_clause = []
                params = []

                for field, value in fields_to_update.items():
                    set_clause.append(f"{field} = %s")
                    params.append(value)

                # Add updated_at
                set_clause.append("updated_at = CURRENT_TIMESTAMP")
                params.append(artist_id)

                query = f"""
                    UPDATE artists
                    SET {', '.join(set_clause)}
                    WHERE id = %s
                    RETURNING id
                """

                cursor.execute(query, params)

                if cursor.rowcount > 0:
                    updated_ids.append(artist_id)
                else:
                    failed.append({'id': artist_id, 'reason': 'Artist not found'})

            except Exception as e:
                failed.append({'id': artist_id, 'reason': str(e)})

        logger.info(f"Bulk updated {len(updated_ids)} artists")

        return {
            'updated_count': len(updated_ids),
            'updated_ids': updated_ids,
            'failed': failed
        }

    # =====================================================
    # BULK INSERT
    # =====================================================

    @staticmethod
    def bulk_insert(
        cursor,
        artists: List[Dict[str, Any]],
        skip_duplicates: bool = True,
        return_ids: bool = True
    ) -> Dict[str, Any]:
        """
        Bulk insert multiple artists.
        
        Args:
            cursor: Database cursor
            artists: List of artist dicts with channel_id and name
            skip_duplicates: Skip duplicate names instead of failing
            return_ids: Return inserted IDs
            
        Returns:
            Dict with insert results
        """
        if not artists:
            return {
                'inserted_count': 0,
                'inserted_ids': [],
                'skipped': [],
                'failed': []
            }

        inserted = []
        skipped = []
        failed = []

        for artist_data in artists:
            try:
                # Validate required fields
                if not artist_data.get('channel_id') or not artist_data.get('name'):
                    failed.append({
                        'data': artist_data,
                        'reason': 'Missing required fields: channel_id and/or name'
                    })
                    continue

                artist_data['name'] = artist_data['name'].strip()

                # Check for duplicate name
                if skip_duplicates:
                    from .repository import ArtistRepository
                    exists = ArtistRepository.exists_by_name(
                        cursor,
                        channel_id=artist_data['channel_id'],
                        name=artist_data['name']
                    )
                    if exists:
                        skipped.append({
                            'name': artist_data['name'],
                            'channel_id': artist_data['channel_id'],
                            'reason': 'Duplicate name in channel'
                        })
                        continue

                # Insert artist
                cursor.execute("""
                    INSERT INTO artists (channel_id, name)
                    VALUES (%s, %s)
                    RETURNING id
                """, (
                    artist_data['channel_id'],
                    artist_data['name']
                ))

                inserted_id = cursor.fetchone()[0]
                inserted.append({
                    'id': inserted_id,
                    'name': artist_data['name'],
                    'channel_id': artist_data['channel_id']
                })

            except Exception as e:
                failed.append({
                    'data': artist_data,
                    'reason': str(e)
                })

        logger.info(
            f"Bulk insert: inserted {len(inserted)}, "
            f"skipped {len(skipped)}, failed {len(failed)}"
        )

        return {
            'inserted_count': len(inserted),
            'inserted_ids': [item['id'] for item in inserted] if return_ids else [],
            'inserted_details': inserted if not return_ids else None,
            'skipped': skipped,
            'failed': failed,
            'total_requested': len(artists)
        }

    @staticmethod
    def bulk_upsert(
        cursor,
        artists: List[Dict[str, Any]],
        conflict_column: str = 'name'
    ) -> Dict[str, Any]:
        """
        Bulk upsert artists (insert or update on conflict).
        
        Args:
            cursor: Database cursor
            artists: List of artist dicts
            conflict_column: Column to check for conflicts ('name' or 'id')
            
        Returns:
            Dict with upsert results
        """
        if not artists:
            return {
                'inserted_count': 0,
                'updated_count': 0,
                'total_processed': 0
            }

        inserted_count = 0
        updated_count = 0

        for artist_data in artists:
            try:
                if conflict_column == 'id':
                    # Upsert by ID
                    cursor.execute("""
                        INSERT INTO artists (id, channel_id, name)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (id)
                        DO UPDATE SET
                            channel_id = EXCLUDED.channel_id,
                            name = EXCLUDED.name,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE artists.id = %s
                        RETURNING id,
                            CASE
                                WHEN xmax = 0 THEN 'inserted'::text
                                ELSE 'updated'::text
                            END as action
                    """, (
                        artist_data['id'],
                        artist_data.get('channel_id'),
                        artist_data.get('name'),
                        artist_data['id']
                    ))
                else:
                    # Upsert by name (per channel)
                    cursor.execute("""
                        INSERT INTO artists (channel_id, name)
                        VALUES (%s, %s)
                        ON CONFLICT (channel_id, LOWER(TRIM(name)))
                        DO UPDATE SET
                            name = EXCLUDED.name,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE artists.channel_id = %s
                          AND LOWER(TRIM(artists.name)) = LOWER(TRIM(%s))
                        RETURNING id,
                            CASE
                                WHEN xmax = 0 THEN 'inserted'::text
                                ELSE 'updated'::text
                            END as action
                    """, (
                        artist_data.get('channel_id'),
                        artist_data.get('name'),
                        artist_data.get('channel_id'),
                        artist_data.get('name')
                    ))

                result = cursor.fetchone()
                if result and result.get('action') == 'inserted':
                    inserted_count += 1
                else:
                    updated_count += 1

            except Exception as e:
                logger.error(f"Error upserting artist {artist_data.get('name')}: {e}")
                raise

        logger.info(f"Upsert complete: inserted {inserted_count}, updated {updated_count}")

        return {
            'inserted_count': inserted_count,
            'updated_count': updated_count,
            'total_processed': inserted_count + updated_count
        }

    # =====================================================
    # BULK CHECK FUNCTIONS
    # =====================================================

    @staticmethod
    def artists_with_songs(
        cursor,
        artist_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """
        Get artists that have songs.
        
        Args:
            cursor: Database cursor
            artist_ids: List of artist IDs
            
        Returns:
            List of artists with song counts
        """
        if not artist_ids:
            return []

        cursor.execute("""
            SELECT
                a.id,
                a.name,
                COUNT(s.id) AS song_count
            FROM artists a
            INNER JOIN songs s ON s.artist_id = a.id
            WHERE a.id = ANY(%s)
            GROUP BY a.id, a.name
            ORDER BY LOWER(a.name)
        """, (artist_ids,))

        return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def artists_without_songs(
        cursor,
        artist_ids: List[int]
    ) -> List[int]:
        """
        Get artists that have no songs.
        
        Args:
            cursor: Database cursor
            artist_ids: List of artist IDs
            
        Returns:
            List of artist IDs with no songs
        """
        if not artist_ids:
            return []

        with_songs = ArtistBulkRepository.artists_with_songs(cursor, artist_ids)
        with_songs_ids = [row['id'] for row in with_songs]

        return [id for id in artist_ids if id not in with_songs_ids]

    @staticmethod
    def existing_ids(
        cursor,
        artist_ids: List[int]
    ) -> List[int]:
        """
        Mengembalikan ID artist yang benar-benar ada.
        
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
    def existing_ids_with_details(
        cursor,
        artist_ids: List[int]
    ) -> Dict[int, bool]:
        """
        Check existence with detailed results per ID.
        
        Args:
            cursor: Database cursor
            artist_ids: List of artist IDs
            
        Returns:
            Dict mapping ID -> exists (True/False)
        """
        if not artist_ids:
            return {}

        ids_list = list(set(artist_ids))
        cursor.execute("""
            SELECT id
            FROM artists
            WHERE id = ANY(%s)
        """, (ids_list,))

        existing_ids = {row[0] for row in cursor.fetchall()}

        return {id: id in existing_ids for id in ids_list}

    # =====================================================
    # TOTAL SONGS
    # =====================================================

    @staticmethod
    def total_songs(
        cursor,
        artist_ids: List[int]
    ) -> int:
        """
        Total lagu dari sekumpulan artist.
        
        Args:
            cursor: Database cursor
            artist_ids: List of artist IDs
            
        Returns:
            Total songs count
        """
        if not artist_ids:
            return 0

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM songs
            WHERE artist_id = ANY(%s)
        """, (artist_ids,))

        return cursor.fetchone()['total']

    @staticmethod
    def total_songs_by_status(
        cursor,
        artist_ids: List[int]
    ) -> Dict[str, int]:
        """
        Total songs by status for a list of artists.
        
        Args:
            cursor: Database cursor
            artist_ids: List of artist IDs
            
        Returns:
            Dict with status -> count
        """
        if not artist_ids:
            return {}

        cursor.execute("""
            SELECT
                status,
                COUNT(*) as count
            FROM songs
            WHERE artist_id = ANY(%s)
            GROUP BY status
        """, (artist_ids,))

        return {row['status']: row['count'] for row in cursor.fetchall()}

    # =====================================================
    # SUMMARY
    # =====================================================

    @staticmethod
    def summary(
        cursor,
        artist_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Ringkasan artist yang dipilih.
        
        Args:
            cursor: Database cursor
            artist_ids: List of artist IDs
            
        Returns:
            Dict with summary data
        """
        if not artist_ids:
            return {
                'artists': 0,
                'songs': 0,
                'artists_with_songs': 0,
                'artists_without_songs': 0,
                'status_breakdown': {}
            }

        # Get existing IDs
        existing_ids = ArtistBulkRepository.existing_ids(cursor, artist_ids)

        if not existing_ids:
            return {
                'artists': 0,
                'songs': 0,
                'artists_with_songs': 0,
                'artists_without_songs': 0,
                'status_breakdown': {}
            }

        # Get summary
        cursor.execute("""
            SELECT
                COUNT(DISTINCT a.id) AS artists,
                COUNT(DISTINCT s.id) AS songs,
                COUNT(DISTINCT a.id) FILTER (
                    WHERE EXISTS (SELECT 1 FROM songs s2 WHERE s2.artist_id = a.id)
                ) AS artists_with_songs
            FROM artists a
            LEFT JOIN songs s ON s.artist_id = a.id
            WHERE a.id = ANY(%s)
        """, (existing_ids,))

        row = cursor.fetchone()

        # Get status breakdown
        status_breakdown = ArtistBulkRepository.total_songs_by_status(
            cursor, existing_ids
        )

        artists_count = row['artists'] or 0
        artists_with_songs = row['artists_with_songs'] or 0

        return {
            'artists': artists_count,
            'songs': row['songs'] or 0,
            'artists_with_songs': artists_with_songs,
            'artists_without_songs': artists_count - artists_with_songs,
            'status_breakdown': status_breakdown,
            'existing_ids': existing_ids,
            'not_found': [id for id in artist_ids if id not in existing_ids]
        }

    # =====================================================
    # BATCH PROCESSING
    # =====================================================

    @staticmethod
    def batch_process(
        cursor,
        artist_ids: List[int],
        batch_size: int = 100,
        process_func: callable = None,
        **process_kwargs
    ) -> Dict[str, Any]:
        """
        Process artists in batches.
        
        Args:
            cursor: Database cursor
            artist_ids: List of artist IDs
            batch_size: Number of items per batch
            process_func: Function to process each batch
            **process_kwargs: Additional arguments for process_func
            
        Returns:
            Dict with batch processing results
        """
        if not artist_ids:
            return {
                'total_processed': 0,
                'total_batches': 0,
                'results': []
            }

        ids_list = list(set(artist_ids))
        total_batches = (len(ids_list) + batch_size - 1) // batch_size
        results = []
        total_processed = 0

        for i in range(0, len(ids_list), batch_size):
            batch = ids_list[i:i + batch_size]
            batch_num = i // batch_size + 1

            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} items)")

            if process_func:
                # Execute process function with batch
                result = process_func(cursor, batch, **process_kwargs)
                results.append({
                    'batch': batch_num,
                    'size': len(batch),
                    'result': result
                })
                total_processed += len(batch)
            else:
                # Default: just validate existence
                existing = ArtistBulkRepository.existing_ids(cursor, batch)
                results.append({
                    'batch': batch_num,
                    'size': len(batch),
                    'existing': existing,
                    'not_found': [id for id in batch if id not in existing]
                })
                total_processed += len(existing)

        return {
            'total_processed': total_processed,
            'total_batches': total_batches,
            'results': results
        }

    # =====================================================
    # VALIDATION
    # =====================================================

    @staticmethod
    def validate_ids(
        cursor,
        artist_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Validate artist IDs.
        
        Args:
            cursor: Database cursor
            artist_ids: List of artist IDs
            
        Returns:
            Dict with validation results
        """
        if not artist_ids:
            return {
                'valid': True,
                'existing_ids': [],
                'not_found': [],
                'total_checked': 0
            }

        ids_list = list(set(artist_ids))
        existing = ArtistBulkRepository.existing_ids(cursor, ids_list)
        not_found = [id for id in ids_list if id not in existing]

        return {
            'valid': len(not_found) == 0,
            'existing_ids': existing,
            'not_found': not_found,
            'total_checked': len(ids_list),
            'valid_count': len(existing),
            'invalid_count': len(not_found)
        }

    # =====================================================
    # EXPORT
    # =====================================================

    @staticmethod
    def export_artists(
        cursor,
        artist_ids: List[int],
        include_songs: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Export artist data.
        
        Args:
            cursor: Database cursor
            artist_ids: List of artist IDs
            include_songs: Include song details
            
        Returns:
            List of artist data
        """
        if not artist_ids:
            return []

        query = """
            SELECT
                a.id,
                a.channel_id,
                c.name AS channel_name,
                a.name,
                a.created_at,
                a.updated_at
        """

        if include_songs:
            query += """
                ,
                COUNT(DISTINCT s.id) AS song_count,
                COUNT(DISTINCT s.id) FILTER (
                    WHERE s.status IN ('released', 'topic', 'live', 'no_ads')
                ) AS uploaded_songs,
                COUNT(DISTINCT s.id) FILTER (
                    WHERE s.status IN ('draft', 'review', 'approved', 'scheduled', 'unreleased')
                ) AS pending_songs
            """

        query += """
            FROM artists a
            INNER JOIN channels c ON c.id = a.channel_id
        """

        if include_songs:
            query += " LEFT JOIN songs s ON s.artist_id = a.id"

        query += """
            WHERE a.id = ANY(%s)
            GROUP BY a.id, a.channel_id, c.name, a.name, a.created_at, a.updated_at
            ORDER BY LOWER(a.name)
        """

        cursor.execute(query, (artist_ids,))
        return [dict(row) for row in cursor.fetchall()]


# =====================================================
# EXPORT
# =====================================================

__all__ = [
    'ArtistBulkRepository',
]