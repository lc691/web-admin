"""
Artist Validator - Complete Implementation

Validator untuk semua business rules Artist dengan:
- Field-level validation
- Cross-field validation
- Database uniqueness checks
- Bulk validation
- Detailed error messages
- Integration with exceptions
"""

import re
from typing import Any, Dict, List, Optional, Tuple, Union

from fastapi import HTTPException

from app.music.repositories.artists.repository import ArtistRepository
from app.music.repositories.artists.bulk import ArtistBulkRepository
from app.music.services.artists.exceptions import (
    ArtistNotFoundError,
    ArtistsNotFoundError,
    ArtistAlreadyExistsError,
    ArtistNameConflictError,
    InvalidArtistNameError,
    InvalidChannelError,
    InvalidArtistDataError,
    ArtistHasSongsError,
    EmptySelectionError,
    BulkValidationError,
    ArtistDatabaseError,
    InvalidFilterError,
    InvalidSortError,
)


class ArtistValidator:
    """
    Validator Artist untuk semua business rules.
    """

    # =====================================================
    # CONSTANTS
    # =====================================================

    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 255
    MAX_BULK_SIZE = 1000

    INVALID_PATTERN = re.compile(r"[<>'\"`]")
    NAME_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_.()&]+$')

    # =====================================================
    # NAME VALIDATION
    # =====================================================

    @classmethod
    def validate_name(cls, name: str) -> str:
        """
        Validasi nama artist.
        
        Args:
            name: Artist name to validate
            
        Returns:
            Trimmed and validated name
            
        Raises:
            InvalidArtistNameError: If name is invalid
            ValueError: For simple validation errors
        """
        if name is None:
            raise InvalidArtistNameError(
                name='',
                reason="Nama artist wajib diisi."
            )

        name = name.strip()

        if not name:
            raise InvalidArtistNameError(
                name='',
                reason="Nama artist tidak boleh kosong."
            )

        if len(name) < cls.MIN_NAME_LENGTH:
            raise InvalidArtistNameError(
                name=name,
                reason=f"Nama artist minimal {cls.MIN_NAME_LENGTH} karakter."
            )

        if len(name) > cls.MAX_NAME_LENGTH:
            raise InvalidArtistNameError(
                name=name,
                reason=f"Nama artist maksimal {cls.MAX_NAME_LENGTH} karakter."
            )

        if cls.INVALID_PATTERN.search(name):
            raise InvalidArtistNameError(
                name=name,
                reason="Nama artist mengandung karakter yang tidak diperbolehkan."
            )

        if not cls.NAME_PATTERN.match(name):
            raise InvalidArtistNameError(
                name=name,
                reason="Nama artist mengandung karakter yang tidak valid. Gunakan huruf, angka, spasi, dan tanda baca dasar."
            )

        return name

    # =====================================================
    # CHANNEL VALIDATION
    # =====================================================

    @staticmethod
    def validate_channel(
        cursor,
        channel_id: int,
    ) -> int:
        """
        Pastikan channel ada.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID to validate
            
        Returns:
            Validated channel_id
            
        Raises:
            InvalidChannelError: If channel not found
        """
        if channel_id is None or channel_id <= 0:
            raise InvalidChannelError(
                channel_id=channel_id,
                reason="Channel ID tidak valid"
            )

        from app.music.repositories.channels.repository import ChannelRepository
        
        if not ChannelRepository.exists(cursor, channel_id):
            raise InvalidChannelError(
                channel_id=channel_id,
                reason="Channel tidak ditemukan"
            )

        return channel_id

    @staticmethod
    def validate_channel_exists(
        cursor,
        channel_id: int,
    ) -> None:
        """
        Alias untuk validate_channel.
        """
        ArtistValidator.validate_channel(cursor, channel_id)

    # =====================================================
    # ARTIST EXISTENCE VALIDATION
    # =====================================================

    @staticmethod
    def validate_artist_exists(
        cursor,
        artist_id: int,
    ) -> None:
        """
        Pastikan artist ada.
        
        Args:
            cursor: Database cursor
            artist_id: Artist ID
            
        Raises:
            ArtistNotFoundError: If artist not found
        """
        if not ArtistRepository.exists(cursor, artist_id):
            raise ArtistNotFoundError(artist_id=artist_id)

    @staticmethod
    def validate_artists_exist(
        cursor,
        artist_ids: List[int],
    ) -> List[int]:
        """
        Pastikan semua artist ada.
        
        Args:
            cursor: Database cursor
            artist_ids: List of artist IDs
            
        Returns:
            List of existing IDs
            
        Raises:
            ArtistsNotFoundError: If any artist not found
        """
        if not artist_ids:
            return []

        existing_ids = ArtistBulkRepository.existing_ids(cursor, artist_ids)
        not_found = [id for id in artist_ids if id not in existing_ids]

        if not_found:
            raise ArtistsNotFoundError(
                artist_ids=artist_ids,
                not_found=not_found
            )

        return existing_ids

    # =====================================================
    # DUPLICATE VALIDATION
    # =====================================================

    @staticmethod
    def validate_duplicate(
        cursor,
        *,
        channel_id: int,
        name: str,
        exclude_id: Optional[int] = None,
    ) -> None:
        """
        Pastikan nama artist tidak duplikat pada channel yang sama.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            name: Artist name
            exclude_id: ID to exclude (for updates)
            
        Raises:
            ArtistAlreadyExistsError: If name already exists
        """
        exists = ArtistRepository.exists_by_name(
            cursor=cursor,
            channel_id=channel_id,
            name=name,
            exclude_id=exclude_id,
        )

        if exists:
            # Get existing artist info for better error message
            existing = None
            try:
                existing_artist = ArtistRepository.get_by_name(
                    cursor, channel_id, name
                )
                if existing_artist:
                    existing = dict(existing_artist)
            except:
                pass

            raise ArtistAlreadyExistsError(
                name=name,
                channel_id=channel_id,
                existing_id=existing.get('id') if existing else None
            )

    @staticmethod
    def validate_duplicate_bulk(
        cursor,
        artists: List[Dict[str, Any]],
    ) -> Dict[int, List[str]]:
        """
        Validasi duplikat untuk bulk insert.
        
        Args:
            cursor: Database cursor
            artists: List of artist data
            
        Returns:
            Dict with validation errors per index
        """
        errors = {}
        
        for idx, artist in enumerate(artists):
            channel_id = artist.get('channel_id')
            name = artist.get('name')
            
            if not channel_id or not name:
                continue
                
            try:
                exists = ArtistRepository.exists_by_name(
                    cursor,
                    channel_id=channel_id,
                    name=name
                )
                if exists:
                    if idx not in errors:
                        errors[idx] = []
                    errors[idx].append(f"Artist '{name}' sudah ada di channel ini")
            except:
                pass
        
        return errors

    # =====================================================
    # DELETE VALIDATION
    # =====================================================

    @staticmethod
    def validate_delete(
        cursor,
        artist_id: int,
    ) -> None:
        """
        Pastikan artist ada sebelum dihapus.
        
        Args:
            cursor: Database cursor
            artist_id: Artist ID
            
        Raises:
            ArtistNotFoundError: If artist not found
        """
        ArtistValidator.validate_artist_exists(cursor, artist_id)

    @staticmethod
    def validate_delete_with_songs(
        cursor,
        artist_id: int,
        allow_with_songs: bool = False,
    ) -> None:
        """
        Validasi delete dengan pengecekan songs.
        
        Args:
            cursor: Database cursor
            artist_id: Artist ID
            allow_with_songs: Allow deletion even if artist has songs
            
        Raises:
            ArtistHasSongsError: If artist has songs and not allowed
        """
        ArtistValidator.validate_artist_exists(cursor, artist_id)

        if not allow_with_songs:
            song_count = ArtistRepository.total_songs(cursor, artist_id)
            if song_count > 0:
                raise ArtistHasSongsError(
                    artist_id=artist_id,
                    song_count=song_count
                )

    @staticmethod
    def validate_bulk_delete(
        cursor,
        artist_ids: List[int],
        allow_with_songs: bool = False,
    ) -> Dict[str, Any]:
        """
        Validasi bulk delete.
        
        Args:
            cursor: Database cursor
            artist_ids: List of artist IDs
            allow_with_songs: Allow deletion even if artists have songs
            
        Returns:
            Dict with validation results
            
        Raises:
            EmptySelectionError: If no IDs provided
            ArtistsNotFoundError: If any artist not found
            ArtistHasSongsError: If artists have songs and not allowed
        """
        if not artist_ids:
            raise EmptySelectionError()

        if len(artist_ids) > ArtistValidator.MAX_BULK_SIZE:
            raise BulkValidationError(
                validation_errors={
                    'bulk': [f"Maksimal {ArtistValidator.MAX_BULK_SIZE} artist dalam satu operasi"]
                }
            )

        # Check existence
        existing_ids = ArtistValidator.validate_artists_exist(cursor, artist_ids)

        # Check songs
        if not allow_with_songs:
            artists_with_songs = ArtistBulkRepository.artists_with_songs(
                cursor, existing_ids
            )
            
            if artists_with_songs:
                song_counts = {row['id']: row['song_count'] for row in artists_with_songs}
                raise ArtistHasSongsError(
                    artist_id=0,
                    song_count=0,
                    details={
                        'artist_ids': list(song_counts.keys()),
                        'song_counts': song_counts,
                        'total_songs': sum(song_counts.values())
                    }
                )

        return {
            'valid': True,
            'existing_ids': existing_ids,
            'total': len(existing_ids)
        }

    # =====================================================
    # CREATE VALIDATION
    # =====================================================

    @classmethod
    def validate_create(
        cls,
        cursor,
        *,
        channel_id: int,
        name: str,
    ) -> Dict[str, Any]:
        """
        Validasi create artist.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            name: Artist name
            
        Returns:
            Dict with validated data
            
        Raises:
            InvalidArtistNameError: If name is invalid
            InvalidChannelError: If channel not found
            ArtistAlreadyExistsError: If name already exists
        """
        # Validate name
        validated_name = cls.validate_name(name)

        # Validate channel
        cls.validate_channel(cursor, channel_id)

        # Validate duplicate
        cls.validate_duplicate(
            cursor,
            channel_id=channel_id,
            name=validated_name,
        )

        return {
            "channel_id": channel_id,
            "name": validated_name,
        }

    @classmethod
    def validate_create_bulk(
        cls,
        cursor,
        artists: List[Dict[str, Any]],
        skip_duplicates: bool = False,
    ) -> Dict[str, Any]:
        """
        Validasi bulk create artist.
        
        Args:
            cursor: Database cursor
            artists: List of artist data
            skip_duplicates: Skip duplicates instead of failing
            
        Returns:
            Dict with validation results
            
        Raises:
            InvalidArtistDataError: If any data is invalid
            BulkValidationError: If validation fails
        """
        if not artists:
            raise EmptySelectionError()

        if len(artists) > ArtistValidator.MAX_BULK_SIZE:
            raise BulkValidationError(
                validation_errors={
                    'bulk': [f"Maksimal {ArtistValidator.MAX_BULK_SIZE} artist dalam satu operasi"]
                }
            )

        errors = {}
        validated_artists = []

        for idx, artist in enumerate(artists):
            artist_errors = []

            # Validate channel_id
            channel_id = artist.get('channel_id')
            if not channel_id:
                artist_errors.append("Channel ID wajib diisi")
            elif channel_id <= 0:
                artist_errors.append("Channel ID tidak valid")
            else:
                try:
                    cls.validate_channel(cursor, channel_id)
                except InvalidChannelError as e:
                    artist_errors.append(str(e))

            # Validate name
            name = artist.get('name')
            if not name:
                artist_errors.append("Nama artist wajib diisi")
            else:
                try:
                    validated_name = cls.validate_name(name)
                    
                    # Check duplicate if not skipping
                    if not skip_duplicates:
                        try:
                            cls.validate_duplicate(
                                cursor,
                                channel_id=channel_id,
                                name=validated_name
                            )
                        except ArtistAlreadyExistsError as e:
                            artist_errors.append(str(e))
                    
                    artist['name'] = validated_name
                except InvalidArtistNameError as e:
                    artist_errors.append(str(e))

            if artist_errors:
                errors[idx] = artist_errors
            else:
                validated_artists.append(artist)

        if errors:
            raise BulkValidationError(
                validation_errors=errors
            )

        return {
            'validated_artists': validated_artists,
            'valid_count': len(validated_artists),
            'total': len(artists)
        }

    # =====================================================
    # UPDATE VALIDATION
    # =====================================================

    @classmethod
    def validate_update(
        cls,
        cursor,
        *,
        artist_id: int,
        channel_id: int,
        name: str,
    ) -> Dict[str, Any]:
        """
        Validasi update artist.
        
        Args:
            cursor: Database cursor
            artist_id: Artist ID
            channel_id: Channel ID
            name: Artist name
            
        Returns:
            Dict with validated data
            
        Raises:
            ArtistNotFoundError: If artist not found
            InvalidArtistNameError: If name is invalid
            InvalidChannelError: If channel not found
            ArtistAlreadyExistsError: If name already exists
        """
        # Check artist exists
        cls.validate_artist_exists(cursor, artist_id)

        # Validate name
        validated_name = cls.validate_name(name)

        # Validate channel
        cls.validate_channel(cursor, channel_id)

        # Validate duplicate (exclude current artist)
        cls.validate_duplicate(
            cursor,
            channel_id=channel_id,
            name=validated_name,
            exclude_id=artist_id,
        )

        return {
            "artist_id": artist_id,
            "channel_id": channel_id,
            "name": validated_name,
        }

    @classmethod
    def validate_update_bulk(
        cls,
        cursor,
        updates: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Validasi bulk update artist.
        
        Args:
            cursor: Database cursor
            updates: List of update data
            
        Returns:
            Dict with validation results
            
        Raises:
            BulkValidationError: If validation fails
        """
        if not updates:
            raise EmptySelectionError()

        if len(updates) > ArtistValidator.MAX_BULK_SIZE:
            raise BulkValidationError(
                validation_errors={
                    'bulk': [f"Maksimal {ArtistValidator.MAX_BULK_SIZE} artist dalam satu operasi"]
                }
            )

        errors = {}
        validated_updates = []
        artist_ids = []

        for idx, update in enumerate(updates):
            update_errors = []
            artist_id = update.get('id')

            if not artist_id:
                update_errors.append("Artist ID wajib diisi")
            elif artist_id <= 0:
                update_errors.append("Artist ID tidak valid")
            else:
                artist_ids.append(artist_id)

            # Validate channel_id if provided
            channel_id = update.get('channel_id')
            if channel_id is not None:
                if channel_id <= 0:
                    update_errors.append("Channel ID tidak valid")
                else:
                    try:
                        cls.validate_channel(cursor, channel_id)
                    except InvalidChannelError as e:
                        update_errors.append(str(e))

            # Validate name if provided
            name = update.get('name')
            if name is not None:
                try:
                    validated_name = cls.validate_name(name)
                    update['name'] = validated_name
                except InvalidArtistNameError as e:
                    update_errors.append(str(e))

            if update_errors:
                errors[idx] = update_errors
            else:
                validated_updates.append(update)

        # Check artist existence
        if artist_ids:
            try:
                cls.validate_artists_exist(cursor, artist_ids)
            except ArtistsNotFoundError as e:
                errors['artists'] = [str(e)]

        # Check duplicate names for each update
        for idx, update in enumerate(validated_updates):
            if idx in errors:
                continue
                
            artist_id = update.get('id')
            channel_id = update.get('channel_id')
            name = update.get('name')
            
            if channel_id and name:
                try:
                    cls.validate_duplicate(
                        cursor,
                        channel_id=channel_id,
                        name=name,
                        exclude_id=artist_id,
                    )
                except ArtistAlreadyExistsError as e:
                    if idx not in errors:
                        errors[idx] = []
                    errors[idx].append(str(e))

        if errors:
            raise BulkValidationError(
                validation_errors=errors
            )

        return {
            'validated_updates': validated_updates,
            'valid_count': len(validated_updates),
            'total': len(updates)
        }

    # =====================================================
    # FILTER VALIDATION
    # =====================================================

    @staticmethod
    def validate_filter_params(filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validasi parameter filter.
        
        Args:
            filters: Filter parameters
            
        Returns:
            Validated filters
            
        Raises:
            InvalidFilterError: If any filter is invalid
        """
        validated = {}
        
        # Keyword
        if filters.get('keyword'):
            keyword = str(filters['keyword']).strip()
            if keyword:
                validated['keyword'] = keyword
        
        # Channel ID
        if filters.get('channel_id') is not None:
            try:
                channel_id = int(filters['channel_id'])
                if channel_id <= 0:
                    raise ValueError("Channel ID must be positive")
                validated['channel_id'] = channel_id
            except (ValueError, TypeError) as e:
                raise InvalidFilterError(
                    filter_param='channel_id',
                    filter_value=filters['channel_id'],
                    reason=f"Invalid channel ID: {e}"
                )
        
        # Has songs
        if 'has_songs' in filters and filters['has_songs'] is not None:
            try:
                validated['has_songs'] = bool(filters['has_songs'])
            except:
                raise InvalidFilterError(
                    filter_param='has_songs',
                    filter_value=filters['has_songs'],
                    reason="Must be a boolean value"
                )
        
        # Min/Max songs
        for param in ['min_songs', 'max_songs']:
            if param in filters and filters[param] is not None:
                try:
                    value = int(filters[param])
                    if value < 0:
                        raise ValueError(f"{param} cannot be negative")
                    validated[param] = value
                except (ValueError, TypeError) as e:
                    raise InvalidFilterError(
                        filter_param=param,
                        filter_value=filters[param],
                        reason=f"Must be a positive integer: {e}"
                    )
        
        # Status
        if filters.get('status'):
            status = str(filters['status']).strip()
            if status:
                validated['status'] = status
        
        # Date range
        if filters.get('date_from'):
            validated['date_from'] = filters['date_from']
        
        if filters.get('date_to'):
            validated['date_to'] = filters['date_to']
        
        return validated

    @staticmethod
    def validate_sort_params(
        order_by: str,
        order_dir: str
    ) -> Tuple[str, str]:
        """
        Validasi parameter sort.
        
        Args:
            order_by: Sort column
            order_dir: Sort direction
            
        Returns:
            Tuple of (validated_order_by, validated_order_dir)
            
        Raises:
            InvalidSortError: If sort parameters are invalid
        """
        valid_columns = {
            'id', 'name', 'channel', 'song_count', 
            'uploaded_songs', 'pending_songs', 'created_at', 'updated_at'
        }
        
        if order_by not in valid_columns:
            raise InvalidSortError(
                sort_column=order_by,
                reason=f"Invalid sort column. Allowed: {', '.join(valid_columns)}"
            )
        
        order_dir = str(order_dir).lower()
        if order_dir not in ('asc', 'desc'):
            raise InvalidSortError(
                sort_column=order_by,
                sort_direction=order_dir,
                reason="Sort direction must be 'asc' or 'desc'"
            )
        
        return order_by, order_dir

    # =====================================================
    # BULK VALIDATION HELPERS
    # =====================================================

    @staticmethod
    def validate_bulk_size(ids: List[int]) -> None:
        """
        Validasi ukuran bulk operation.
        
        Args:
            ids: List of IDs
            
        Raises:
            BulkValidationError: If size exceeds limit
        """
        if len(ids) > ArtistValidator.MAX_BULK_SIZE:
            raise BulkValidationError(
                validation_errors={
                    'bulk': [f"Maksimal {ArtistValidator.MAX_BULK_SIZE} item dalam satu operasi"]
                }
            )

    @staticmethod
    def validate_not_empty(ids: List[int], message: str = "Tidak ada data yang dipilih") -> None:
        """
        Validasi bahwa list tidak kosong.
        
        Args:
            ids: List of IDs
            message: Error message
            
        Raises:
            EmptySelectionError: If list is empty
        """
        if not ids:
            raise EmptySelectionError(message)

    @staticmethod
    def validate_artist_ids(
        cursor,
        artist_ids: List[int],
        allow_empty: bool = False
    ) -> Dict[str, Any]:
        """
        Validasi artist IDs.
        
        Args:
            cursor: Database cursor
            artist_ids: List of artist IDs
            allow_empty: Allow empty list
            
        Returns:
            Dict with validation results
            
        Raises:
            EmptySelectionError: If empty and not allowed
            ArtistsNotFoundError: If any ID not found
        """
        if not artist_ids:
            if allow_empty:
                return {'valid': True, 'existing_ids': [], 'not_found': []}
            raise EmptySelectionError()

        # Remove duplicates
        unique_ids = list(set(artist_ids))
        
        # Check existence
        existing_ids = ArtistBulkRepository.existing_ids(cursor, unique_ids)
        not_found = [id for id in unique_ids if id not in existing_ids]

        if not_found:
            raise ArtistsNotFoundError(
                artist_ids=unique_ids,
                not_found=not_found
            )

        return {
            'valid': True,
            'existing_ids': existing_ids,
            'total': len(existing_ids)
        }

    # =====================================================
    # GET VALIDATION SUMMARY
    # =====================================================

    @staticmethod
    def get_validation_summary(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get summary of validation results.
        
        Args:
            data: Data to summarize
            
        Returns:
            Dict with validation summary
        """
        summary = {
            'valid': True,
            'errors': 0,
            'warnings': 0,
            'fields': {}
        }

        for key, value in data.items():
            if isinstance(value, dict) and 'errors' in value:
                summary['valid'] = False
                summary['errors'] += len(value['errors'])
                summary['fields'][key] = {
                    'valid': False,
                    'error_count': len(value['errors'])
                }
            else:
                summary['fields'][key] = {
                    'valid': True,
                    'error_count': 0
                }

        return summary