"""
Channel Bulk Repository - Complete Implementation

Repository untuk operasi bulk pada channels dengan:
- Bulk delete with validation
- Bulk update (vermuk, notes, etc.)
- Bulk insert with conflict handling
- Bulk exists checking
- Batch processing for large datasets
- Transaction support
- Detailed results with success/failure tracking
"""

from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ChannelBulkRepository:
    """
    Repository untuk semua operasi bulk pada tabel channels.
    """
    
    # =====================================================
    # BULK DELETE
    # =====================================================
    
    @staticmethod
    def bulk_delete(
        cursor,
        ids: Sequence[int],
        validate_exists: bool = True,
        return_deleted: bool = False
    ) -> Union[int, Dict[str, Any]]:
        """
        Menghapus banyak channel sekaligus.
        
        Args:
            cursor: Database cursor
            ids: List of channel IDs to delete
            validate_exists: Check if IDs exist before deleting
            return_deleted: Return deleted channel details
            
        Returns:
            - If return_deleted=False: Number of channels deleted
            - If return_deleted=True: Dict with deleted_count and deleted_ids
        """
        try:
            if not ids:
                return 0 if not return_deleted else {
                    'deleted_count': 0,
                    'deleted_ids': [],
                    'not_found': []
                }
            
            ids_list = list(ids)
            
            # Validate existence if requested
            not_found = []
            if validate_exists:
                existing_ids = ChannelBulkRepository.bulk_exists(cursor, ids_list)
                not_found = [id for id in ids_list if id not in existing_ids]
                
                if not existing_ids:
                    logger.warning(f"No channels found to delete for IDs: {ids_list}")
                    return 0 if not return_deleted else {
                        'deleted_count': 0,
                        'deleted_ids': [],
                        'not_found': ids_list
                    }
                
                ids_to_delete = existing_ids
            else:
                ids_to_delete = ids_list
            
            # Get channel names before deletion (for logging)
            if return_deleted:
                cursor.execute("""
                    SELECT id, name, email
                    FROM channels
                    WHERE id = ANY(%s)
                """, (ids_to_delete,))
                deleted_info = [dict(row) for row in cursor.fetchall()]
            
            # Execute deletion
            cursor.execute("""
                DELETE FROM channels
                WHERE id = ANY(%s)
                RETURNING id, name
            """, (ids_to_delete,))
            
            deleted_rows = cursor.fetchall()
            deleted_count = len(deleted_rows)
            
            logger.info(f"Deleted {deleted_count} channels: {[row['name'] for row in deleted_rows]}")
            
            if return_deleted:
                return {
                    'deleted_count': deleted_count,
                    'deleted_ids': [row['id'] for row in deleted_rows],
                    'deleted_names': [row['name'] for row in deleted_rows],
                    'not_found': not_found,
                    'total_requested': len(ids_list)
                }
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error bulk deleting channels: {e}")
            raise
    
    @staticmethod
    def safe_bulk_delete(
        cursor,
        ids: Sequence[int],
        min_id: Optional[int] = None,
        max_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Safe bulk delete with additional safeguards.
        
        Args:
            cursor: Database cursor
            ids: List of channel IDs to delete
            min_id: Minimum ID allowed to delete (safety)
            max_id: Maximum ID allowed to delete (safety)
            
        Returns:
            Dict with deletion results
        """
        try:
            if not ids:
                return {
                    'deleted_count': 0,
                    'deleted_ids': [],
                    'not_found': [],
                    'skipped': [],
                    'errors': []
                }
            
            # Filter IDs based on min/max
            filtered_ids = []
            skipped = []
            
            for channel_id in ids:
                if min_id is not None and channel_id < min_id:
                    skipped.append({
                        'id': channel_id,
                        'reason': f'ID below minimum ({min_id})'
                    })
                elif max_id is not None and channel_id > max_id:
                    skipped.append({
                        'id': channel_id,
                        'reason': f'ID above maximum ({max_id})'
                    })
                else:
                    filtered_ids.append(channel_id)
            
            if not filtered_ids:
                return {
                    'deleted_count': 0,
                    'deleted_ids': [],
                    'not_found': [],
                    'skipped': skipped,
                    'errors': []
                }
            
            # Check if channels exist
            existing_ids = ChannelBulkRepository.bulk_exists(cursor, filtered_ids)
            not_found = [id for id in filtered_ids if id not in existing_ids]
            
            if not existing_ids:
                return {
                    'deleted_count': 0,
                    'deleted_ids': [],
                    'not_found': not_found,
                    'skipped': skipped,
                    'errors': []
                }
            
            # Execute deletion
            cursor.execute("""
                DELETE FROM channels
                WHERE id = ANY(%s)
                RETURNING id, name
            """, (existing_ids,))
            
            deleted_rows = cursor.fetchall()
            
            logger.warning(
                f"Safe delete: Deleted {len(deleted_rows)} channels, "
                f"skipped {len(skipped)}, not found {len(not_found)}"
            )
            
            return {
                'deleted_count': len(deleted_rows),
                'deleted_ids': [row['id'] for row in deleted_rows],
                'deleted_names': [row['name'] for row in deleted_rows],
                'not_found': not_found,
                'skipped': skipped,
                'errors': []
            }
            
        except Exception as e:
            logger.error(f"Error in safe bulk delete: {e}")
            return {
                'deleted_count': 0,
                'deleted_ids': [],
                'not_found': [],
                'skipped': [],
                'errors': [str(e)]
            }
    
    # =====================================================
    # BULK UPDATE
    # =====================================================
    
    @staticmethod
    def bulk_update_vermuk(
        cursor,
        ids: Sequence[int],
        vermuk: bool,
        validate_exists: bool = True
    ) -> Dict[str, Any]:
        """
        Update status vermuk beberapa channel.
        
        Args:
            cursor: Database cursor
            ids: List of channel IDs
            vermuk: Vermuk status to set
            validate_exists: Check if IDs exist before updating
            
        Returns:
            Dict with update results
        """
        try:
            if not ids:
                return {
                    'updated_count': 0,
                    'updated_ids': [],
                    'not_found': [],
                    'skipped': []
                }
            
            ids_list = list(ids)
            
            # Validate existence if requested
            if validate_exists:
                existing_ids = ChannelBulkRepository.bulk_exists(cursor, ids_list)
                not_found = [id for id in ids_list if id not in existing_ids]
                
                if not existing_ids:
                    logger.warning(f"No channels found to update for IDs: {ids_list}")
                    return {
                        'updated_count': 0,
                        'updated_ids': [],
                        'not_found': ids_list,
                        'skipped': []
                    }
                
                ids_to_update = existing_ids
            else:
                ids_to_update = ids_list
                not_found = []
            
            # Get current status to skip unnecessary updates
            cursor.execute("""
                SELECT id, vermuk
                FROM channels
                WHERE id = ANY(%s)
            """, (ids_to_update,))
            
            current_statuses = {row['id']: row['vermuk'] for row in cursor.fetchall()}
            
            # Filter IDs that need updating
            need_update = []
            skipped = []
            
            for channel_id in ids_to_update:
                if channel_id in current_statuses:
                    if current_statuses[channel_id] != vermuk:
                        need_update.append(channel_id)
                    else:
                        skipped.append({
                            'id': channel_id,
                            'reason': f'Already vermuk={vermuk}'
                        })
                else:
                    skipped.append({
                        'id': channel_id,
                        'reason': 'Not found'
                    })
            
            if not need_update:
                return {
                    'updated_count': 0,
                    'updated_ids': [],
                    'not_found': not_found,
                    'skipped': skipped
                }
            
            # Execute update
            cursor.execute("""
                UPDATE channels
                SET
                    vermuk = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ANY(%s)
                RETURNING id, name
            """, (vermuk, need_update))
            
            updated_rows = cursor.fetchall()
            
            logger.info(f"Updated vermuk to {vermuk} for {len(updated_rows)} channels")
            
            return {
                'updated_count': len(updated_rows),
                'updated_ids': [row['id'] for row in updated_rows],
                'updated_names': [row['name'] for row in updated_rows],
                'not_found': not_found,
                'skipped': skipped,
                'total_requested': len(ids_list)
            }
            
        except Exception as e:
            logger.error(f"Error bulk updating vermuk: {e}")
            raise
    
    @staticmethod
    def bulk_update_notes(
        cursor,
        updates: Dict[int, str]
    ) -> Dict[str, Any]:
        """
        Bulk update notes for multiple channels.
        
        Args:
            cursor: Database cursor
            updates: Dict mapping channel_id -> new_notes
            
        Returns:
            Dict with update results
        """
        try:
            if not updates:
                return {
                    'updated_count': 0,
                    'updated_ids': [],
                    'failed': []
                }
            
            channel_ids = list(updates.keys())
            
            # Validate existence
            existing_ids = ChannelBulkRepository.bulk_exists(cursor, channel_ids)
            not_found = [id for id in channel_ids if id not in existing_ids]
            
            failed = []
            updated_ids = []
            
            # Update one by one (or batch update)
            for channel_id in existing_ids:
                try:
                    notes = updates[channel_id]
                    cursor.execute("""
                        UPDATE channels
                        SET
                            notes = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        RETURNING id
                    """, (notes, channel_id))
                    
                    if cursor.rowcount > 0:
                        updated_ids.append(channel_id)
                    else:
                        failed.append({'id': channel_id, 'reason': 'Update failed'})
                        
                except Exception as e:
                    failed.append({'id': channel_id, 'reason': str(e)})
            
            logger.info(f"Updated notes for {len(updated_ids)} channels")
            
            return {
                'updated_count': len(updated_ids),
                'updated_ids': updated_ids,
                'not_found': not_found,
                'failed': failed
            }
            
        except Exception as e:
            logger.error(f"Error bulk updating notes: {e}")
            raise
    
    @staticmethod
    def bulk_update_multiple_fields(
        cursor,
        updates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Bulk update multiple fields for channels.
        
        Args:
            cursor: Database cursor
            updates: List of dicts with 'id' and fields to update
            
        Returns:
            Dict with update results
        """
        try:
            if not updates:
                return {
                    'updated_count': 0,
                    'updated_ids': [],
                    'failed': []
                }
            
            allowed_fields = {'name', 'email', 'password', 'vermuk', 'notes'}
            failed = []
            updated_ids = []
            
            for update_data in updates:
                channel_id = update_data.get('id')
                if not channel_id:
                    failed.append({'data': update_data, 'reason': 'Missing ID'})
                    continue
                
                # Filter allowed fields
                fields_to_update = {
                    k: v for k, v in update_data.items()
                    if k in allowed_fields and k != 'id'
                }
                
                if not fields_to_update:
                    failed.append({'id': channel_id, 'reason': 'No valid fields to update'})
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
                    
                    params.append(channel_id)
                    
                    query = f"""
                        UPDATE channels
                        SET {', '.join(set_clause)}
                        WHERE id = %s
                        RETURNING id
                    """
                    
                    cursor.execute(query, params)
                    
                    if cursor.rowcount > 0:
                        updated_ids.append(channel_id)
                    else:
                        failed.append({'id': channel_id, 'reason': 'Channel not found'})
                        
                except Exception as e:
                    failed.append({'id': channel_id, 'reason': str(e)})
            
            logger.info(f"Updated {len(updated_ids)} channels")
            
            return {
                'updated_count': len(updated_ids),
                'updated_ids': updated_ids,
                'failed': failed
            }
            
        except Exception as e:
            logger.error(f"Error in bulk update multiple fields: {e}")
            raise
    
    # =====================================================
    # BULK INSERT
    # =====================================================
    
    @staticmethod
    def bulk_insert(
        cursor,
        channels: List[Dict[str, Any]],
        skip_duplicates: bool = True,
        return_ids: bool = True
    ) -> Dict[str, Any]:
        """
        Bulk insert multiple channels.
        
        Args:
            cursor: Database cursor
            channels: List of channel dictionaries
            skip_duplicates: Skip duplicate names instead of failing
            return_ids: Return inserted IDs
            
        Returns:
            Dict with insert results
        """
        try:
            if not channels:
                return {
                    'inserted_count': 0,
                    'inserted_ids': [],
                    'skipped': [],
                    'failed': []
                }
            
            inserted = []
            skipped = []
            failed = []
            
            for channel_data in channels:
                try:
                    # Validate required fields
                    if not channel_data.get('name'):
                        failed.append({
                            'data': channel_data,
                            'reason': 'Missing required field: name'
                        })
                        continue
                    
                    # Check for duplicate name
                    if skip_duplicates:
                        cursor.execute("""
                            SELECT EXISTS(
                                SELECT 1 FROM channels
                                WHERE LOWER(TRIM(name)) = LOWER(TRIM(%s))
                            )
                        """, (channel_data['name'],))
                        
                        if cursor.fetchone()[0]:
                            skipped.append({
                                'name': channel_data['name'],
                                'reason': 'Duplicate name'
                            })
                            continue
                    
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
                        channel_data.get('name'),
                        channel_data.get('email'),
                        channel_data.get('password'),
                        channel_data.get('vermuk', False),
                        channel_data.get('notes'),
                    ))
                    
                    inserted_id = cursor.fetchone()[0]
                    inserted.append({
                        'id': inserted_id,
                        'name': channel_data['name']
                    })
                    
                except Exception as e:
                    failed.append({
                        'data': channel_data,
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
                'total_requested': len(channels)
            }
            
        except Exception as e:
            logger.error(f"Error in bulk insert: {e}")
            raise
    
    @staticmethod
    def bulk_upsert(
        cursor,
        channels: List[Dict[str, Any]],
        conflict_column: str = 'name'
    ) -> Dict[str, Any]:
        """
        Bulk upsert channels (insert or update on conflict).
        
        Args:
            cursor: Database cursor
            channels: List of channel dictionaries
            conflict_column: Column to check for conflicts ('name' or 'email')
            
        Returns:
            Dict with upsert results
        """
        try:
            if not channels:
                return {
                    'inserted_count': 0,
                    'updated_count': 0,
                    'total_processed': 0
                }
            
            inserted_count = 0
            updated_count = 0
            
            for channel_data in channels:
                try:
                    # Determine conflict target
                    if conflict_column == 'email' and channel_data.get('email'):
                        conflict_target = "email"
                        conflict_value = channel_data['email']
                    else:
                        conflict_target = "name"
                        conflict_value = channel_data['name']
                    
                    # Build UPSERT query
                    cursor.execute(f"""
                        INSERT INTO channels
                        (
                            name,
                            email,
                            password,
                            vermuk,
                            notes
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT ({conflict_target})
                        DO UPDATE SET
                            name = EXCLUDED.name,
                            email = EXCLUDED.email,
                            password = EXCLUDED.password,
                            vermuk = EXCLUDED.vermuk,
                            notes = EXCLUDED.notes,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE channels.{conflict_target} = %s
                        RETURNING id, 
                            CASE 
                                WHEN xmax = 0 THEN 'inserted'::text
                                ELSE 'updated'::text
                            END as action
                    """, (
                        channel_data.get('name'),
                        channel_data.get('email'),
                        channel_data.get('password'),
                        channel_data.get('vermuk', False),
                        channel_data.get('notes'),
                        conflict_value
                    ))
                    
                    result = cursor.fetchone()
                    if result and result.get('action') == 'inserted':
                        inserted_count += 1
                    else:
                        updated_count += 1
                    
                except Exception as e:
                    logger.error(f"Error upserting channel {channel_data.get('name')}: {e}")
                    raise
            
            logger.info(f"Upsert complete: inserted {inserted_count}, updated {updated_count}")
            
            return {
                'inserted_count': inserted_count,
                'updated_count': updated_count,
                'total_processed': inserted_count + updated_count
            }
            
        except Exception as e:
            logger.error(f"Error in bulk upsert: {e}")
            raise
    
    # =====================================================
    # BULK EXISTS
    # =====================================================
    
    @staticmethod
    def bulk_exists(
        cursor,
        ids: Sequence[int]
    ) -> List[int]:
        """
        Mengembalikan daftar ID yang benar-benar ada di database.
        
        Args:
            cursor: Database cursor
            ids: List of channel IDs to check
            
        Returns:
            List of existing IDs (preserved order)
        """
        if not ids:
            return []
        
        try:
            cursor.execute("""
                SELECT id
                FROM channels
                WHERE id = ANY(%s)
                ORDER BY id
            """, (list(ids),))
            
            return [row[0] for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Error checking bulk existence: {e}")
            raise
    
    @staticmethod
    def bulk_exists_with_details(
        cursor,
        ids: Sequence[int]
    ) -> Dict[int, bool]:
        """
        Check existence with detailed results per ID.
        
        Args:
            cursor: Database cursor
            ids: List of channel IDs to check
            
        Returns:
            Dict mapping ID -> exists (True/False)
        """
        if not ids:
            return {}
        
        try:
            ids_list = list(ids)
            cursor.execute("""
                SELECT id
                FROM channels
                WHERE id = ANY(%s)
            """, (ids_list,))
            
            existing_ids = {row[0] for row in cursor.fetchall()}
            
            return {id: id in existing_ids for id in ids_list}
            
        except Exception as e:
            logger.error(f"Error checking bulk existence with details: {e}")
            raise
    
    # =====================================================
    # BATCH PROCESSING
    # =====================================================
    
    @staticmethod
    def batch_process(
        cursor,
        ids: Sequence[int],
        batch_size: int = 100,
        process_func: callable = None,
        **process_kwargs
    ) -> Dict[str, Any]:
        """
        Process channels in batches.
        
        Args:
            cursor: Database cursor
            ids: List of channel IDs
            batch_size: Number of items per batch
            process_func: Function to process each batch
            **process_kwargs: Additional arguments for process_func
            
        Returns:
            Dict with batch processing results
        """
        try:
            if not ids:
                return {
                    'total_processed': 0,
                    'total_batches': 0,
                    'results': []
                }
            
            ids_list = list(ids)
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
                    existing = ChannelBulkRepository.bulk_exists(cursor, batch)
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
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            raise
    
    # =====================================================
    # VALIDATION
    # =====================================================
    
    @staticmethod
    def validate_ids(
        cursor,
        ids: Sequence[int]
    ) -> Dict[str, Any]:
        """
        Validate channel IDs.
        
        Returns:
            Dict with validation results
        """
        try:
            if not ids:
                return {
                    'valid': True,
                    'existing_ids': [],
                    'not_found': [],
                    'total_checked': 0
                }
            
            ids_list = list(ids)
            existing = ChannelBulkRepository.bulk_exists(cursor, ids_list)
            not_found = [id for id in ids_list if id not in existing]
            
            return {
                'valid': len(not_found) == 0,
                'existing_ids': existing,
                'not_found': not_found,
                'total_checked': len(ids_list),
                'valid_count': len(existing),
                'invalid_count': len(not_found)
            }
            
        except Exception as e:
            logger.error(f"Error validating IDs: {e}")
            raise