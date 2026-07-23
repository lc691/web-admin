"""
Channel Service - Complete Implementation

Business logic layer untuk Channel dengan:
- CRUD operations dengan validasi
- Detail dengan enrichment
- DataTable dengan filtering dan sorting
- Bulk operations
- Statistics dan analytics
- Activity scoring
- Error handling dan logging
"""

from typing import Any, Dict, List, Optional, Union
import logging

from app.core.datatable import DataTable

from app.music.repositories.channels.bulk import ChannelBulkRepository
from app.music.repositories.channels.filter import ChannelFilterRepository
from app.music.repositories.channels.repository import ChannelRepository
from app.music.repositories.channels.statistics import ChannelStatisticsRepository

from .exceptions import (
    ChannelNotFoundError,
    ChannelError,
    BulkChannelError,
    InvalidChannelDataError,
    DuplicateChannelNameError,
    DuplicateChannelEmailError,
    BulkValidationError,
    ChannelsNotFoundError,
    InvalidChannelNotesError,
    InvalidFilterError,
    InvalidSortError, 
    InvalidPaginationError,
)
from .validator import ChannelValidator
from .mapper import (
    ChannelMapper,
    ChannelDTO,
    ChannelStatsDTO,
    ChannelActivityDTO,
    ChannelListDTO,
    ChannelCreateDTO,
    ChannelUpdateDTO,
    ChannelFilterDTO,
)

logger = logging.getLogger(__name__)


class ChannelService:
    """
    Business logic service untuk Channel.
    
    Menangani semua operasi bisnis dengan:
    - Validasi data
    - Transformasi data
    - Error handling
    - Logging
    """
    
    # =====================================================
    # CONSTANTS
    # =====================================================
    
    SORT_COLUMNS = [
        None,
        "id",
        "name",
        "email",
        "vermuk",
        "artists",
        "songs",
        "uploaded_songs",
        "created_at",
        None,
    ]
    
    MAX_BULK_SIZE = 1000
    DEFAULT_LIMIT = 20
    MAX_LIMIT = 100
    
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
    ) -> Dict[str, Any]:
        """
        Create a new channel with full validation.
        
        Args:
            cursor: Database cursor
            name: Channel name (required)
            email: Channel email (optional)
            password: Channel password (optional)
            vermuk: Vermuk status (default: False)
            notes: Additional notes (optional)
            
        Returns:
            Dict with created channel data
            
        Raises:
            InvalidChannelDataError: If validation fails
            DuplicateChannelNameError: If name already exists
            DuplicateChannelEmailError: If email already exists
            ChannelError: For other errors
        """
        try:
            logger.info(f"Creating new channel: {name}")
            
            # Validate data
            validated = ChannelValidator.validate_create(
                cursor,
                name=name,
                email=email,
                password=password,
                vermuk=vermuk,
                notes=notes,
            )
            
            # Create channel
            channel_id = ChannelRepository.create(
                cursor,
                name=validated['name'],
                email=validated.get('email'),
                password=validated.get('password'),
                vermuk=validated['vermuk'],
                notes=validated.get('notes'),
            )
            
            # Get created channel
            channel = ChannelRepository.get_by_id(cursor, channel_id)
            
            # Convert to DTO
            result = ChannelMapper.from_db_to_dto(channel)
            
            logger.info(f"Channel created successfully: ID={channel_id}, Name={result.name}")
            
            return ChannelMapper.to_response(
                data=result,
                status_code=201,
                message="Channel created successfully"
            )
            
        except (InvalidChannelDataError, DuplicateChannelNameError, 
                DuplicateChannelEmailError) as e:
            logger.warning(f"Validation error creating channel '{name}': {e}")
            return ChannelMapper.to_error_response(
                error=str(e),
                status_code=400,
                details=e.details if hasattr(e, 'details') else None
            )
        except Exception as e:
            logger.error(f"Error creating channel '{name}': {e}")
            raise ChannelError(f"Failed to create channel: {str(e)}")
    
    @staticmethod
    def create_from_dto(
        cursor,
        dto: ChannelCreateDTO
    ) -> Dict[str, Any]:
        """
        Create channel from DTO.
        
        Args:
            cursor: Database cursor
            dto: ChannelCreateDTO object
            
        Returns:
            Dict with created channel data
        """
        return ChannelService.create(
            cursor,
            name=dto.name,
            email=dto.email,
            password=dto.password,
            vermuk=dto.vermuk,
            notes=dto.notes,
        )
    
    # =====================================================
    # UPDATE
    # =====================================================
    
    @staticmethod
    def update(
        cursor,
        *,
        channel_id: int,
        name: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        vermuk: bool = False,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing channel with full validation.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID to update
            name: Channel name (required)
            email: Channel email (optional)
            password: Channel password (optional)
            vermuk: Vermuk status
            notes: Additional notes (optional)
            
        Returns:
            Dict with updated channel data
            
        Raises:
            ChannelNotFoundError: If channel not found
            InvalidChannelDataError: If validation fails
            DuplicateChannelNameError: If name already exists
            DuplicateChannelEmailError: If email already exists
            ChannelError: For other errors
        """
        try:
            logger.info(f"Updating channel ID={channel_id}")
            
            # Validate data
            validated = ChannelValidator.validate_update(
                cursor,
                channel_id=channel_id,
                name=name,
                email=email,
                password=password,
                vermuk=vermuk,
                notes=notes,
            )
            
            # Update channel
            updated = ChannelRepository.update(
                cursor,
                channel_id=channel_id,
                name=validated['name'],
                email=validated.get('email'),
                password=validated.get('password'),
                vermuk=validated['vermuk'],
                notes=validated.get('notes'),
            )
            
            if not updated:
                raise ChannelNotFoundError(channel_id=channel_id)
            
            # Get updated channel
            channel = ChannelRepository.get_by_id(cursor, channel_id)
            
            # Convert to DTO
            result = ChannelMapper.from_db_to_dto(channel)
            
            logger.info(f"Channel updated successfully: ID={channel_id}, Name={result.name}")
            
            return ChannelMapper.to_response(
                data=result,
                status_code=200,
                message="Channel updated successfully"
            )
            
        except (ChannelNotFoundError, InvalidChannelDataError,
                DuplicateChannelNameError, DuplicateChannelEmailError) as e:
            logger.warning(f"Validation error updating channel {channel_id}: {e}")
            return ChannelMapper.to_error_response(
                error=str(e),
                status_code=400,
                details=e.details if hasattr(e, 'details') else None
            )
        except Exception as e:
            logger.error(f"Error updating channel {channel_id}: {e}")
            raise ChannelError(f"Failed to update channel: {str(e)}")
    
    @staticmethod
    def update_from_dto(
        cursor,
        dto: ChannelUpdateDTO
    ) -> Dict[str, Any]:
        """
        Update channel from DTO.
        
        Args:
            cursor: Database cursor
            dto: ChannelUpdateDTO object
            
        Returns:
            Dict with updated channel data
        """
        return ChannelService.update(
            cursor,
            channel_id=dto.id,
            name=dto.name,
            email=dto.email,
            password=dto.password,
            vermuk=dto.vermuk,
            notes=dto.notes,
        )
    
    @staticmethod
    def update_notes(
        cursor,
        channel_id: int,
        notes: str
    ) -> Dict[str, Any]:
        """
        Update only notes for a channel.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            notes: New notes
            
        Returns:
            Dict with updated channel data
        """
        try:
            # Validate channel exists
            ChannelValidator.validate_channel_exists(cursor, channel_id)
            
            # Validate notes
            validated_notes = ChannelValidator.validate_notes(notes)
            
            # Update notes
            updated = ChannelRepository.update_notes(
                cursor,
                channel_id=channel_id,
                notes=validated_notes or ''
            )
            
            if not updated:
                raise ChannelNotFoundError(channel_id=channel_id)
            
            # Get updated channel
            channel = ChannelRepository.get_by_id(cursor, channel_id)
            result = ChannelMapper.from_db_to_dto(channel)
            
            logger.info(f"Updated notes for channel ID={channel_id}")
            
            return ChannelMapper.to_response(
                data=result,
                status_code=200,
                message="Notes updated successfully"
            )
            
        except (ChannelNotFoundError, InvalidChannelNotesError) as e:
            return ChannelMapper.to_error_response(
                error=str(e),
                status_code=400
            )
        except Exception as e:
            logger.error(f"Error updating notes for channel {channel_id}: {e}")
            raise ChannelError(f"Failed to update notes: {str(e)}")
    
    # =====================================================
    # DELETE
    # =====================================================
    
    @staticmethod
    def delete(
        cursor,
        channel_id: int,
        soft_delete: bool = False
    ) -> Dict[str, Any]:
        """
        Delete a channel.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID to delete
            soft_delete: If True, just mark as deleted (not implemented yet)
            
        Returns:
            Dict with deletion result
            
        Raises:
            ChannelNotFoundError: If channel not found
            ChannelError: For other errors
        """
        try:
            logger.warning(f"Deleting channel ID={channel_id}")
            
            # Validate channel exists
            ChannelValidator.validate_channel_exists(cursor, channel_id)
            
            # Get channel info before deletion
            channel = ChannelRepository.get_by_id(cursor, channel_id)
            channel_name = channel.get('name', 'Unknown') if channel else 'Unknown'
            
            # Delete channel
            if soft_delete:
                # TODO: Implement soft delete
                raise NotImplementedError("Soft delete not implemented yet")
            else:
                deleted = ChannelRepository.delete(cursor, channel_id)
            
            if not deleted:
                raise ChannelNotFoundError(channel_id=channel_id)
            
            logger.warning(f"Channel deleted successfully: ID={channel_id}, Name={channel_name}")
            
            return ChannelMapper.to_response(
                data={'deleted_id': channel_id, 'deleted_name': channel_name},
                status_code=200,
                message=f"Channel '{channel_name}' deleted successfully"
            )
            
        except ChannelNotFoundError as e:
            return ChannelMapper.to_error_response(
                error=str(e),
                status_code=404
            )
        except Exception as e:
            logger.error(f"Error deleting channel {channel_id}: {e}")
            raise ChannelError(f"Failed to delete channel: {str(e)}")
    
    # =====================================================
    # GET / DETAIL
    # =====================================================
    
    @staticmethod
    def get_by_id(
        cursor,
        channel_id: int,
        include_stats: bool = True,
        include_activity: bool = False
    ) -> Dict[str, Any]:
        """
        Get channel by ID with optional enrichment.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            include_stats: Include statistics (artists, songs counts)
            include_activity: Include activity scoring
            
        Returns:
            Dict with channel data
            
        Raises:
            ChannelNotFoundError: If channel not found
            ChannelError: For other errors
        """
        try:
            logger.debug(f"Getting channel ID={channel_id}")
            
            # Get channel
            channel = ChannelRepository.get_by_id(cursor, channel_id)
            
            if channel is None:
                raise ChannelNotFoundError(channel_id=channel_id)
            
            # Convert to DTO
            result = ChannelMapper.from_db_to_dto(channel)
            
            # Enrich with activity if requested
            if include_activity:
                try:
                    activity_data = ChannelStatisticsRepository.get_channel_activity_score(
                        cursor, channel_id
                    )
                    if activity_data:
                        result = ChannelMapper.enrich_with_activity(result, activity_data)
                except Exception as e:
                    logger.warning(f"Failed to get activity data for channel {channel_id}: {e}")
            
            return ChannelMapper.to_response(
                data=result,
                status_code=200,
                message="Channel retrieved successfully"
            )
            
        except ChannelNotFoundError as e:
            return ChannelMapper.to_error_response(
                error=str(e),
                status_code=404
            )
        except Exception as e:
            logger.error(f"Error getting channel {channel_id}: {e}")
            raise ChannelError(f"Failed to get channel: {str(e)}")
    
    @staticmethod
    def get_by_name(
        cursor,
        name: str,
        include_stats: bool = False
    ) -> Dict[str, Any]:
        """
        Get channel by name.
        
        Args:
            cursor: Database cursor
            name: Channel name
            include_stats: Include statistics
            
        Returns:
            Dict with channel data
            
        Raises:
            ChannelNotFoundError: If channel not found
        """
        try:
            logger.debug(f"Getting channel by name: {name}")
            
            channel = ChannelRepository.get_by_name(cursor, name)
            
            if channel is None:
                raise ChannelNotFoundError(name=name)
            
            if include_stats:
                channel_id = channel.get('id')
                if channel_id:
                    stats = ChannelRepository.get_by_id(cursor, channel_id)
                    if stats:
                        channel.update(stats)
            
            result = ChannelMapper.from_db_to_dto(channel)
            
            return ChannelMapper.to_response(
                data=result,
                status_code=200,
                message="Channel retrieved successfully"
            )
            
        except ChannelNotFoundError as e:
            return ChannelMapper.to_error_response(
                error=str(e),
                status_code=404
            )
        except Exception as e:
            logger.error(f"Error getting channel by name '{name}': {e}")
            raise ChannelError(f"Failed to get channel: {str(e)}")
    
    @staticmethod
    def get_by_email(
        cursor,
        email: str
    ) -> Dict[str, Any]:
        """
        Get channel by email.
        
        Args:
            cursor: Database cursor
            email: Channel email
            
        Returns:
            Dict with channel data
            
        Raises:
            ChannelNotFoundError: If channel not found
        """
        try:
            logger.debug(f"Getting channel by email: {email}")
            
            channel = ChannelRepository.get_by_email(cursor, email)
            
            if channel is None:
                raise ChannelNotFoundError(email=email)
            
            result = ChannelMapper.from_db_to_dto(channel)
            
            return ChannelMapper.to_response(
                data=result,
                status_code=200,
                message="Channel retrieved successfully"
            )
            
        except ChannelNotFoundError as e:
            return ChannelMapper.to_error_response(
                error=str(e),
                status_code=404
            )
        except Exception as e:
            logger.error(f"Error getting channel by email '{email}': {e}")
            raise ChannelError(f"Failed to get channel: {str(e)}")
    
    @staticmethod
    def get_detail(
        cursor,
        channel_id: int
    ) -> Dict[str, Any]:
        """
        Get detailed channel information with all stats.
        Alias for get_by_id with full enrichment.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            
        Returns:
            Dict with detailed channel data
        """
        return ChannelService.get_by_id(
            cursor,
            channel_id,
            include_stats=True,
            include_activity=True
        )
    
    # =====================================================
    # LIST / DATATABLE
    # =====================================================
    
    @staticmethod
    def list_channels(
        cursor,
        keyword: Optional[str] = None,
        vermuk: Optional[bool] = None,
        email: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        has_artists: Optional[bool] = None,
        has_songs: Optional[bool] = None,
        min_artists: Optional[int] = None,
        max_artists: Optional[int] = None,
        min_songs: Optional[int] = None,
        max_songs: Optional[int] = None,
        order_by: str = "created_at",
        order_dir: str = "desc",
        start: int = 0,
        length: int = 20,
    ) -> Dict[str, Any]:
        """
        List channels with filters and pagination.
        
        Returns:
            Dict with channels list and pagination metadata
        """
        try:
            # Validate filters
            filters = {
                'keyword': keyword,
                'vermuk': vermuk,
                'email': email,
                'date_from': date_from,
                'date_to': date_to,
                'has_artists': has_artists,
                'has_songs': has_songs,
                'min_artists': min_artists,
                'max_artists': max_artists,
                'min_songs': min_songs,
                'max_songs': max_songs,
            }
            
            validated_filters = ChannelValidator.validate_filter_params(filters)
            
            # Validate sort
            order_by, order_dir = ChannelValidator.validate_sort_params(
                order_by, order_dir
            )
            
            # Validate pagination
            start, length = ChannelValidator.validate_pagination_params(
                start, length, max_length=ChannelService.MAX_LIMIT
            )
            
            # Get channels
            result = ChannelFilterRepository.apply(
                cursor,
                **validated_filters,
                order_by=order_by,
                order_dir=order_dir,
                start=start,
                length=length,
            )
            
            # Convert to DTOs
            channels = [
                ChannelMapper.from_db_to_dto(item)
                for item in result['data']
            ]
            
            # Create list DTO
            list_dto = ChannelListDTO(
                data=channels,
                total=result['meta']['total'],
                start=start,
                length=length,
                filters=validated_filters
            )
            
            logger.info(f"Listed {len(channels)} channels (total: {list_dto.total})")
            
            return ChannelMapper.to_response(
                data=list_dto,
                status_code=200,
                message="Channels retrieved successfully"
            )
            
        except (InvalidChannelDataError, InvalidFilterError,
                InvalidSortError, InvalidPaginationError) as e:
            return ChannelMapper.to_error_response(
                error=str(e),
                status_code=400,
                details=e.details if hasattr(e, 'details') else None
            )
        except Exception as e:
            logger.error(f"Error listing channels: {e}")
            raise ChannelError(f"Failed to list channels: {str(e)}")
    
    @classmethod
    def datatable(
        cls,
        cursor,
        dt: DataTable,
    ) -> Dict[str, Any]:
        """
        DataTable endpoint for server-side pagination.
        
        Args:
            cursor: Database cursor
            dt: DataTable object from request
            
        Returns:
            Dict with DataTable response format
        """
        try:
            logger.debug(f"DataTable request: {dt}")
            
            # Get sort column
            order_by = dt.sort_column(cls.SORT_COLUMNS) or "created_at"
            
            # Get channels
            result = ChannelFilterRepository.apply(
                cursor,
                keyword=dt.search,
                vermuk=dt.get_bool("vermuk"),
                order_by=order_by,
                order_dir=dt.sort_direction,
                start=dt.offset,
                length=dt.limit,
            )
            
            # Convert to DTOs
            channels = [
                ChannelMapper.from_db_to_dto(item)
                for item in result['data']
            ]
            
            # Format for DataTable
            return [item.to_json() for item in channels]
            
        except Exception as e:
            logger.error(f"Error in DataTable: {e}")
            return {
                "draw": dt.draw if dt else 0,
                "recordsTotal": 0,
                "recordsFiltered": 0,
                "data": [],
                "error": str(e),
            }
    
    @staticmethod
    def count_filtered(
        cursor,
        dt: DataTable,
    ) -> int:
        """
        Count filtered channels for DataTable.
        
        Args:
            cursor: Database cursor
            dt: DataTable object
            
        Returns:
            Count of filtered channels
        """
        try:
            return ChannelFilterRepository.count_filtered(
                cursor,
                keyword=dt.search,
                vermuk=dt.get_bool("vermuk"),
            )
        except Exception as e:
            logger.error(f"Error counting filtered channels: {e}")
            return 0
    
    # =====================================================
    # BULK OPERATIONS
    # =====================================================
    
    @staticmethod
    def bulk_delete(
        cursor,
        ids: List[int],
        validate_existence: bool = True,
    ) -> Dict[str, Any]:
        """
        Delete multiple channels.
        
        Args:
            cursor: Database cursor
            ids: List of channel IDs
            validate_existence: Validate all IDs exist
            
        Returns:
            Dict with bulk delete results
        """
        try:
            if not ids:
                return ChannelMapper.to_response(
                    data={'deleted_count': 0, 'message': 'No IDs provided'},
                    status_code=200,
                    message='No channels to delete'
                )
            
            if len(ids) > ChannelService.MAX_BULK_SIZE:
                return ChannelMapper.to_error_response(
                    error=f"Too many IDs. Maximum: {ChannelService.MAX_BULK_SIZE}",
                    status_code=400,
                    details={'provided': len(ids), 'max': ChannelService.MAX_BULK_SIZE}
                )
            
            # Validate if needed
            if validate_existence:
                try:
                    ChannelValidator.validate_channels_exist(cursor, ids)
                except ChannelsNotFoundError as e:
                    return ChannelMapper.to_error_response(
                        error=str(e),
                        status_code=400,
                        details=e.details if hasattr(e, 'details') else None
                    )
            
            # Delete channels
            result = ChannelBulkRepository.bulk_delete(
                cursor,
                ids,
                validate_exists=validate_existence,
                return_deleted=True,
            )
            
            logger.warning(f"Bulk deleted {result['deleted_count']} channels")
            
            return ChannelMapper.to_response(
                data=ChannelMapper.format_bulk_result(result, 'deleted'),
                status_code=200,
                message=f"Deleted {result['deleted_count']} channels"
            )
            
        except Exception as e:
            logger.error(f"Error in bulk delete: {e}")
            raise BulkChannelError(f"Bulk delete failed: {str(e)}")
    
    @staticmethod
    def bulk_update_vermuk(
        cursor,
        ids: List[int],
        vermuk: bool,
        validate_existence: bool = True,
    ) -> Dict[str, Any]:
        """
        Bulk update vermuk status.
        
        Args:
            cursor: Database cursor
            ids: List of channel IDs
            vermuk: Vermuk status to set
            validate_existence: Validate all IDs exist
            
        Returns:
            Dict with bulk update results
        """
        try:
            if not ids:
                return ChannelMapper.to_response(
                    data={'updated_count': 0, 'message': 'No IDs provided'},
                    status_code=200,
                    message='No channels to update'
                )
            
            if len(ids) > ChannelService.MAX_BULK_SIZE:
                return ChannelMapper.to_error_response(
                    error=f"Too many IDs. Maximum: {ChannelService.MAX_BULK_SIZE}",
                    status_code=400,
                    details={'provided': len(ids), 'max': ChannelService.MAX_BULK_SIZE}
                )
            
            # Update channels
            result = ChannelBulkRepository.bulk_update_vermuk(
                cursor,
                ids,
                vermuk,
            )
            
            # Validate existence if requested
            if validate_existence:
                missing = []
                for channel_id in ids:
                    if not ChannelRepository.exists(cursor, channel_id):
                        missing.append(channel_id)
                
                if missing:
                    result['not_found'] = missing
                    result['not_found_count'] = len(missing)
            
            logger.info(f"Bulk updated vermuk to {vermuk} for {result['updated_count']} channels")
            
            return ChannelMapper.to_response(
                data=ChannelMapper.format_bulk_result(result, 'updated'),
                status_code=200,
                message=f"Updated {result['updated_count']} channels"
            )
            
        except Exception as e:
            logger.error(f"Error in bulk update vermuk: {e}")
            raise BulkChannelError(f"Bulk update failed: {str(e)}")
    
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
            Dict with bulk update results
        """
        try:
            if not updates:
                return ChannelMapper.to_response(
                    data={'updated_count': 0, 'message': 'No updates provided'},
                    status_code=200,
                    message='No channels to update'
                )
            
            if len(updates) > ChannelService.MAX_BULK_SIZE:
                return ChannelMapper.to_error_response(
                    error=f"Too many updates. Maximum: {ChannelService.MAX_BULK_SIZE}",
                    status_code=400,
                    details={'provided': len(updates), 'max': ChannelService.MAX_BULK_SIZE}
                )
            
            # Validate notes
            for channel_id, notes in updates.items():
                try:
                    ChannelValidator.validate_notes(notes)
                except InvalidChannelNotesError as e:
                    return ChannelMapper.to_error_response(
                        error=f"Invalid notes for channel {channel_id}: {str(e)}",
                        status_code=400
                    )
            
            # Update notes
            result = ChannelBulkRepository.bulk_update_notes(
                cursor,
                updates
            )
            
            logger.info(f"Bulk updated notes for {result['updated_count']} channels")
            
            return ChannelMapper.to_response(
                data=ChannelMapper.format_bulk_result(result, 'updated'),
                status_code=200,
                message=f"Updated notes for {result['updated_count']} channels"
            )
            
        except Exception as e:
            logger.error(f"Error in bulk update notes: {e}")
            raise BulkChannelError(f"Bulk update notes failed: {str(e)}")
    
    # =====================================================
    # STATISTICS
    # =====================================================
    
    @staticmethod
    def get_statistics(
        cursor,
        detailed: bool = False,
    ) -> Dict[str, Any]:
        """
        Get channel statistics.
        
        Args:
            cursor: Database cursor
            detailed: Get detailed statistics
            
        Returns:
            Dict with statistics
        """
        try:
            logger.debug("Getting channel statistics")
            
            if detailed:
                stats_data = ChannelStatisticsRepository.summary(cursor)
            else:
                stats_data = ChannelStatisticsRepository.summary_simple(cursor)
            
            stats_dto = ChannelMapper.from_stats_to_dto(stats_data)

            # print("stats_data =", stats_data)
            # print("dto =", stats_dto.to_dict())
            
            response = ChannelMapper.to_response(
                data=stats_dto.to_dict(),
                status_code=200,
                message="Statistics retrieved successfully"
            )
        
            # print(response)
            return response

        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            raise ChannelError(f"Failed to get statistics: {str(e)}")
    
    @staticmethod
    def get_channel_stats(
        cursor,
        channel_id: int,
    ) -> Dict[str, Any]:
        """
        Get statistics for a specific channel.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            
        Returns:
            Dict with channel statistics
        """
        try:
            logger.debug(f"Getting statistics for channel {channel_id}")
            
            # Validate channel exists
            ChannelValidator.validate_channel_exists(cursor, channel_id)
            
            # Get stats
            stats_data = ChannelStatisticsRepository.get_channel_stats(
                cursor, channel_id
            )
            
            if stats_data is None:
                raise ChannelNotFoundError(channel_id=channel_id)
            
            return ChannelMapper.to_response(
                data=stats_data,
                status_code=200,
                message="Channel statistics retrieved successfully"
            )
            
        except ChannelNotFoundError as e:
            return ChannelMapper.to_error_response(
                error=str(e),
                status_code=404
            )
        except Exception as e:
            logger.error(f"Error getting channel stats for {channel_id}: {e}")
            raise ChannelError(f"Failed to get channel statistics: {str(e)}")
    
    @staticmethod
    def get_activity_score(
        cursor,
        channel_id: int,
    ) -> Dict[str, Any]:
        """
        Get activity score for a channel.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            
        Returns:
            Dict with activity score
        """
        try:
            logger.debug(f"Getting activity score for channel {channel_id}")
            
            # Validate channel exists
            ChannelValidator.validate_channel_exists(cursor, channel_id)
            
            # Get activity data
            activity_data = ChannelStatisticsRepository.get_channel_activity_score(
                cursor, channel_id
            )
            
            if activity_data is None:
                raise ChannelNotFoundError(channel_id=channel_id)
            
            # Get channel name
            channel = ChannelRepository.get_by_id(cursor, channel_id)
            channel_name = channel.get('name', 'Unknown') if channel else 'Unknown'
            
            # Convert to DTO
            activity_dto = ChannelMapper.from_activity_to_dto(
                activity_data, channel_name
            )
            
            return ChannelMapper.to_response(
                data=activity_dto.to_dict(),
                status_code=200,
                message="Activity score retrieved successfully"
            )
            
        except ChannelNotFoundError as e:
            return ChannelMapper.to_error_response(
                error=str(e),
                status_code=404
            )
        except Exception as e:
            logger.error(f"Error getting activity score for {channel_id}: {e}")
            raise ChannelError(f"Failed to get activity score: {str(e)}")
    
    @staticmethod
    def get_status_breakdown(
        cursor,
        channel_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get status breakdown for all channels or a specific channel.
        
        Args:
            cursor: Database cursor
            channel_id: Optional channel ID filter
            
        Returns:
            Dict with status breakdown
        """
        try:
            logger.debug(f"Getting status breakdown for channel {channel_id}")
            
            if channel_id:
                # Validate channel exists
                ChannelValidator.validate_channel_exists(cursor, channel_id)
                breakdown = ChannelStatisticsRepository.get_status_breakdown_by_channel(
                    cursor, channel_id
                )
            else:
                breakdown = ChannelStatisticsRepository.get_status_breakdown(cursor)
            
            return ChannelMapper.to_response(
                data=breakdown,
                status_code=200,
                message="Status breakdown retrieved successfully"
            )
            
        except ChannelNotFoundError as e:
            return ChannelMapper.to_error_response(
                error=str(e),
                status_code=404
            )
        except Exception as e:
            logger.error(f"Error getting status breakdown: {e}")
            raise ChannelError(f"Failed to get status breakdown: {str(e)}")
    
    # =====================================================
    # RANKING / TOP LISTS
    # =====================================================
    
    @staticmethod
    def get_top_channels(
        cursor,
        limit: int = 10,
        min_songs: int = 1,
    ) -> Dict[str, Any]:
        """
        Get top channels by song count.
        
        Args:
            cursor: Database cursor
            limit: Number of channels to return
            min_songs: Minimum songs filter
            
        Returns:
            Dict with top channels
        """
        try:
            logger.debug(f"Getting top {limit} channels")
            
            top_channels = ChannelStatisticsRepository.get_top_channels_by_songs(
                cursor,
                limit=limit,
                min_songs=min_songs,
            )
            
            return ChannelMapper.to_response(
                data=top_channels,
                status_code=200,
                message=f"Top {len(top_channels)} channels retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Error getting top channels: {e}")
            raise ChannelError(f"Failed to get top channels: {str(e)}")
    
    @staticmethod
    def get_top_artists(
        cursor,
        channel_id: Optional[int] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Get top artists by song count.
        
        Args:
            cursor: Database cursor
            channel_id: Optional channel ID filter
            limit: Number of artists to return
            
        Returns:
            Dict with top artists
        """
        try:
            logger.debug(f"Getting top {limit} artists for channel {channel_id}")
            
            if channel_id:
                ChannelValidator.validate_channel_exists(cursor, channel_id)
            
            top_artists = ChannelStatisticsRepository.get_top_artists_by_songs(
                cursor,
                channel_id=channel_id,
                limit=limit,
            )
            
            return ChannelMapper.to_response(
                data=top_artists,
                status_code=200,
                message=f"Top {len(top_artists)} artists retrieved successfully"
            )
            
        except ChannelNotFoundError as e:
            return ChannelMapper.to_error_response(
                error=str(e),
                status_code=404
            )
        except Exception as e:
            logger.error(f"Error getting top artists: {e}")
            raise ChannelError(f"Failed to get top artists: {str(e)}")
    
    # =====================================================
    # TIMESERIES
    # =====================================================
    
    @staticmethod
    def get_daily_stats(
        cursor,
        days: int = 30,
        channel_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get daily statistics.
        
        Args:
            cursor: Database cursor
            days: Number of days to look back
            channel_id: Optional channel ID filter
            
        Returns:
            Dict with daily statistics
        """
        try:
            logger.debug(f"Getting daily stats for last {days} days")
            
            if channel_id:
                ChannelValidator.validate_channel_exists(cursor, channel_id)
            
            daily_stats = ChannelStatisticsRepository.get_daily_stats(
                cursor,
                days=days,
                channel_id=channel_id,
            )
            
            return ChannelMapper.to_response(
                data=daily_stats,
                status_code=200,
                message="Daily statistics retrieved successfully"
            )
            
        except ChannelNotFoundError as e:
            return ChannelMapper.to_error_response(
                error=str(e),
                status_code=404
            )
        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            raise ChannelError(f"Failed to get daily statistics: {str(e)}")
    
    @staticmethod
    def get_growth_data(
        cursor,
        channel_id: int,
        months: int = 12,
    ) -> Dict[str, Any]:
        """
        Get channel growth data.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            months: Number of months to look back
            
        Returns:
            Dict with growth data
        """
        try:
            logger.debug(f"Getting growth data for channel {channel_id}")
            
            ChannelValidator.validate_channel_exists(cursor, channel_id)
            
            growth_data = ChannelStatisticsRepository.get_channel_growth(
                cursor,
                channel_id=channel_id,
                months=months,
            )
            
            return ChannelMapper.to_response(
                data=growth_data,
                status_code=200,
                message="Growth data retrieved successfully"
            )
            
        except ChannelNotFoundError as e:
            return ChannelMapper.to_error_response(
                error=str(e),
                status_code=404
            )
        except Exception as e:
            logger.error(f"Error getting growth data for {channel_id}: {e}")
            raise ChannelError(f"Failed to get growth data: {str(e)}")
    
    # =====================================================
    # COMPARE
    # =====================================================
    
    @staticmethod
    def compare_channels(
        cursor,
        channel_ids: List[int],
    ) -> Dict[str, Any]:
        """
        Compare multiple channels.
        
        Args:
            cursor: Database cursor
            channel_ids: List of channel IDs to compare
            
        Returns:
            Dict with comparison data
        """
        try:
            if not channel_ids:
                return ChannelMapper.to_error_response(
                    error="No channel IDs provided",
                    status_code=400
                )
            
            if len(channel_ids) < 2:
                return ChannelMapper.to_error_response(
                    error="At least 2 channels required for comparison",
                    status_code=400
                )
            
            # Validate channels exist
            ChannelValidator.validate_channels_exist(cursor, channel_ids)
            
            # Get comparison data
            comparison = ChannelStatisticsRepository.compare_channels(
                cursor, channel_ids
            )
            
            return ChannelMapper.to_response(
                data=comparison,
                status_code=200,
                message="Channel comparison retrieved successfully"
            )
            
        except ChannelsNotFoundError as e:
            return ChannelMapper.to_error_response(
                error=str(e),
                status_code=404,
                details=e.details if hasattr(e, 'details') else None
            )
        except Exception as e:
            logger.error(f"Error comparing channels: {e}")
            raise ChannelError(f"Failed to compare channels: {str(e)}")