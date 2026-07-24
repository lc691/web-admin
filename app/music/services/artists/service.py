"""
Artist Service - Complete Implementation

Business logic layer untuk Artist dengan:
- CRUD operations dengan validasi
- Detail dengan enrichment
- DataTable dengan filtering dan sorting
- Bulk operations
- Statistics dan analytics
- Error handling dan logging
"""

from typing import Any, Dict, List, Optional, Union
import logging

from app.core.database import get_dict_cursor, get_dict_cursor_with_commit

from app.music.repositories.artists.repository import ArtistRepository
from app.music.repositories.artists.filter import ArtistFilterRepository
from app.music.repositories.artists.statistics import ArtistStatisticsRepository
from app.music.repositories.artists.bulk import ArtistBulkRepository
from app.music.services.channels.service import ChannelService

from app.music.services.artists.mapper import ArtistMapper
from app.music.services.artists.validator import ArtistValidator

from app.music.constants.status import VALID_STATUS

from app.music.services.artists.exceptions import (
    ArtistAlreadyExistsError,
    ArtistDatabaseError,
    ArtistDeleteError,
    ArtistHasSongsError,
    ArtistNotFoundError,
    ArtistsNotFoundError,
    BulkDeleteError,
    BulkUpdateError,
    BulkInsertError,
    EmptySelectionError,
    InvalidArtistNameError,
    InvalidChannelError,
    ChannelNotFoundError,
    ArtistConnectionError,
    ArtistTransactionError,
    InvalidArtistStatusError,
)

logger = logging.getLogger(__name__)


class ArtistService:
    """
    Service Artist untuk semua business logic.
    """

    # =====================================================
    # GET BY ID
    # =====================================================

    @staticmethod
    def get_by_id(
        artist_id: int,
        include_stats: bool = False,
    ) -> Dict[str, Any]:
        """
        Get artist by ID.
        
        Args:
            artist_id: Artist ID
            include_stats: Include statistics
            
        Returns:
            Artist data
            
        Raises:
            ArtistNotFoundError: If artist not found
            ArtistDatabaseError: For database errors
        """
        try:
            with get_dict_cursor() as (cursor, conn):
                logger.debug(f"Getting artist by ID: {artist_id}")

                if include_stats:
                    artist = ArtistRepository.get_with_stats(cursor, artist_id)
                else:
                    artist = ArtistRepository.get_by_id(cursor, artist_id)

                if not artist:
                    raise ArtistNotFoundError(artist_id=artist_id)

                if include_stats:
                    return ArtistMapper.to_response_with_stats(
                        artist, artist
                    )
                
                return ArtistMapper.to_response(artist)

        except ArtistNotFoundError:
            raise
        except Exception as exc:
            logger.error(f"Error getting artist {artist_id}: {exc}")
            raise ArtistDatabaseError(f"Failed to get artist: {str(exc)}")

    # =====================================================
    # DETAIL
    # =====================================================

    @staticmethod
    def get_detail(
        artist_id: int,
        include_songs: bool = True,
    ) -> Dict[str, Any]:
        """
        Get detailed artist information.
        
        Args:
            artist_id: Artist ID
            include_songs: Include song details
            
        Returns:
            Detailed artist data
            
        Raises:
            ArtistNotFoundError: If artist not found
            ArtistDatabaseError: For database errors
        """
        try:
            with get_dict_cursor() as (cursor, conn):
                logger.debug(f"Getting artist detail: {artist_id}")

                # Get artist with stats
                artist = ArtistRepository.get_with_stats(cursor, artist_id)

                if not artist:
                    raise ArtistNotFoundError(artist_id=artist_id)

                # Get song status breakdown
                status_breakdown = []
                if include_songs:
                    status_breakdown = ArtistStatisticsRepository.song_status(
                        cursor, artist_id
                    )

                # Format detail
                detail = ArtistMapper.to_detail(artist)
                detail['status_breakdown'] = status_breakdown

                return detail

        except ArtistNotFoundError:
            raise
        except Exception as exc:
            logger.error(f"Error getting artist detail {artist_id}: {exc}")
            raise ArtistDatabaseError(f"Failed to get artist detail: {str(exc)}")

    # =====================================================
    # GET ALL
    # =====================================================

    @staticmethod
    def get_all(
        channel_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
        search: Optional[str] = None,
        order_by: str = "name",
        order_dir: str = "asc",
    ) -> List[Dict[str, Any]]:
        """
        Get all artists with filters.
        
        Args:
            channel_id: Optional channel filter
            limit: Max records
            offset: Pagination offset
            search: Search keyword
            order_by: Sort column
            order_dir: Sort direction
            
        Returns:
            List of artists
            
        Raises:
            ArtistDatabaseError: For database errors
        """
        try:
            with get_dict_cursor() as (cursor, conn):
                logger.debug("Getting all artists")

                rows = ArtistRepository.get_all(
                    cursor,
                    limit=limit,
                    offset=offset,
                    search=search,
                    channel_id=channel_id,
                    order_by=order_by,
                    order_dir=order_dir,
                )

                return ArtistMapper.to_list(rows)

        except Exception as exc:
            logger.error(f"Error getting all artists: {exc}")
            raise ArtistDatabaseError(f"Failed to get artists: {str(exc)}")

    # =====================================================
    # GET BY CHANNEL
    # =====================================================

    @staticmethod
    def get_by_channel(
        channel_id: int,
        limit: int = 100,
        offset: int = 0,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get artists by channel.
        
        Args:
            channel_id: Channel ID
            limit: Max records
            offset: Pagination offset
            search: Search keyword
            
        Returns:
            List of artists
            
        Raises:
            ChannelNotFoundError: If channel not found
            ArtistDatabaseError: For database errors
        """
        try:
            with get_dict_cursor() as (cursor, conn):
                logger.debug(f"Getting artists by channel: {channel_id}")

                # Validate channel exists
                ChannelService.get_channel(cursor, channel_id)

                rows = ArtistRepository.get_by_channel(
                    cursor,
                    channel_id=channel_id,
                    limit=limit,
                    offset=offset,
                    search=search,
                )

                return ArtistMapper.to_list(rows)

        except ChannelNotFoundError:
            raise
        except Exception as exc:
            logger.error(f"Error getting artists by channel {channel_id}: {exc}")
            raise ArtistDatabaseError(f"Failed to get artists: {str(exc)}")

    # =====================================================
    # DATATABLE
    # =====================================================

    @staticmethod
    def datatable(
        *,
        draw: int = 0,
        start: int = 0,
        length: int = 10,
        search: str = "",
        channel_id: Optional[int] = None,
        has_songs: Optional[bool] = None,
        status: Optional[str] = None,
        order_column: int = 1,
        order_dir: str = "desc",
    ) -> Dict[str, Any]:
        """
        DataTable endpoint.

        Raises:
            InvalidArtistStatusError:
                Jika song status tidak valid.

            ArtistDatabaseError:
                Jika terjadi kesalahan database.
        """

        try:
            with get_dict_cursor() as (cursor, conn):

                logger.debug(
                    "DataTable request: draw=%s search='%s' status=%s",
                    draw,
                    search,
                    status,
                )

                # ==========================================
                # VALIDASI SONG STATUS
                # ==========================================

                if status:
                    status = status.strip().lower()

                    if status not in VALID_STATUS:
                        raise InvalidArtistStatusError(
                            status=status,
                            valid_statuses=sorted(VALID_STATUS),
                        )

                # ==========================================
                # VALIDASI SORT
                # ==========================================

                order_dir = order_dir.lower()

                if order_dir not in ("asc", "desc"):
                    order_dir = "desc"

                # ==========================================
                # LOAD DATA
                # ==========================================

                result = ArtistFilterRepository.datatable(
                    cursor=cursor,
                    start=start,
                    length=length,
                    search=search,
                    channel_id=channel_id,
                    has_songs=has_songs,
                    status=status,
                    order_column=order_column,
                    order_dir=order_dir,
                )

                mapped = ArtistMapper.to_list(result["rows"])

                if mapped:
                    print(mapped[0])

                return {
                    "draw": draw,
                    "recordsTotal": result["recordsTotal"],
                    "recordsFiltered": result["recordsFiltered"],
                    "data": mapped,
                }

        except InvalidArtistStatusError:
            raise

        except ArtistDatabaseError:
            raise

        except Exception as exc:
            logger.exception("Error loading artist datatable")

            raise ArtistDatabaseError(
                f"Failed to load datatable: {exc}"
            ) from exc

    # =====================================================
    # SEARCH
    # =====================================================

    @staticmethod
    def search(
        keyword: str,
        channel_id: Optional[int] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Search artists by keyword.
        
        Args:
            keyword: Search keyword
            channel_id: Optional channel filter
            limit: Max results
            
        Returns:
            List of matching artists
            
        Raises:
            ArtistDatabaseError: For database errors
        """
        try:
            with get_dict_cursor() as (cursor, conn):
                logger.debug(f"Searching artists: '{keyword}'")

                rows = ArtistFilterRepository.search(
                    cursor,
                    keyword=keyword,
                    channel_id=channel_id,
                    limit=limit,
                )

                return ArtistMapper.to_select(rows)

        except Exception as exc:
            logger.error(f"Error searching artists: {exc}")
            raise ArtistDatabaseError(f"Failed to search artists: {str(exc)}")

    # =====================================================
    # FILTER
    # =====================================================

    @staticmethod
    def filter_artists(
        *,
        keyword: Optional[str] = None,
        channel_id: Optional[int] = None,
        has_songs: Optional[bool] = None,
        status: Optional[str] = None,
        min_songs: Optional[int] = None,
        max_songs: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        order_by: str = "name",
        order_dir: str = "asc",
        start: int = 0,
        length: int = 20,
    ) -> Dict[str, Any]:
        """
        Advanced filter for artists.
        
        Returns:
            Dict with data and metadata
            
        Raises:
            ArtistDatabaseError: For database errors
        """
        try:
            with get_dict_cursor() as (cursor, conn):
                logger.debug("Filtering artists")

                result = ArtistFilterRepository.filter(
                    cursor,
                    keyword=keyword,
                    channel_id=channel_id,
                    has_songs=has_songs,
                    status=status,
                    min_songs=min_songs,
                    max_songs=max_songs,
                    date_from=date_from,
                    date_to=date_to,
                    order_by=order_by,
                    order_dir=order_dir,
                    start=start,
                    length=length,
                )

                # Format data
                result['data'] = ArtistMapper.to_list(result['data'])

                return result

        except Exception as exc:
            logger.error(f"Error filtering artists: {exc}")
            raise ArtistDatabaseError(f"Failed to filter artists: {str(exc)}")

    # =====================================================
    # CHANNELS
    # =====================================================

    @staticmethod
    def get_channels() -> List[Dict[str, Any]]:
        """
        Get all channels for dropdown.
        
        Returns:
            List of channels
            
        Raises:
            ArtistDatabaseError: For database errors
        """
        try:
            with get_dict_cursor() as (cursor, conn):
                logger.debug("Getting channels for dropdown")

                rows = ArtistRepository.get_channels(cursor)
                return ArtistMapper.channels(rows)

        except Exception as exc:
            logger.error(f"Error getting channels: {exc}")
            raise ArtistDatabaseError(f"Failed to get channels: {str(exc)}")

    @staticmethod
    def get_channel(
        cursor,
        channel_id: int,
    ) -> Dict[str, Any]:
        """
        Get channel by ID.
        
        Args:
            cursor: Database cursor
            channel_id: Channel ID
            
        Returns:
            Channel data
            
        Raises:
            ChannelNotFoundError: If channel not found
            ArtistDatabaseError: For database errors
        """
        try:
            logger.debug(f"Getting channel: {channel_id}")

            row = ArtistRepository.get_channel(cursor, channel_id)

            if not row:
                raise ChannelNotFoundError(
                    channel_id=channel_id
                )

            return ArtistMapper.channel(row)

        except ChannelNotFoundError:
            raise
        except Exception as exc:
            logger.error(f"Error getting channel {channel_id}: {exc}")
            raise ArtistDatabaseError(f"Failed to get channel: {str(exc)}")

    # =====================================================
    # CREATE
    # =====================================================

    @staticmethod
    def create(
        *,
        channel_id: int,
        name: str,
    ) -> Dict[str, Any]:
        """
        Create a new artist.
        
        Args:
            channel_id: Channel ID
            name: Artist name
            
        Returns:
            Created artist data
            
        Raises:
            InvalidArtistNameError: If name is invalid
            InvalidChannelError: If channel not found
            ArtistAlreadyExistsError: If name already exists
            ArtistDatabaseError: For database errors
        """
        try:
            with get_dict_cursor_with_commit() as (cursor, conn):
                logger.info(f"Creating artist: '{name}' in channel {channel_id}")

                # Validate
                data = ArtistValidator.validate_create(
                    cursor,
                    channel_id=channel_id,
                    name=name,
                )

                # Create
                result = ArtistRepository.create(
                    cursor,
                    channel_id=data["channel_id"],
                    name=data["name"],
                )

                # Get created artist
                artist_id = result if isinstance(result, int) else result.get('id')
                artist = ArtistRepository.get_detail(cursor, artist_id)

                logger.info(f"Artist created: ID={artist_id}, Name='{name}'")

                return ArtistMapper.to_detail(artist)

        except (
            ArtistNotFoundError,
            ArtistAlreadyExistsError,
            InvalidArtistNameError,
            InvalidChannelError,
        ):
            raise
        except Exception as exc:
            logger.error(f"Error creating artist '{name}': {exc}")
            raise ArtistDatabaseError(f"Failed to create artist: {str(exc)}")

    # =====================================================
    # UPDATE
    # =====================================================

    @staticmethod
    def update(
        *,
        artist_id: int,
        channel_id: int,
        name: str,
    ) -> Dict[str, Any]:
        """
        Update an artist.
        
        Args:
            artist_id: Artist ID
            channel_id: New channel ID
            name: New name
            
        Returns:
            Updated artist data
            
        Raises:
            ArtistNotFoundError: If artist not found
            InvalidArtistNameError: If name is invalid
            InvalidChannelError: If channel not found
            ArtistAlreadyExistsError: If name already exists
            ArtistDatabaseError: For database errors
        """
        try:
            with get_dict_cursor_with_commit() as (cursor, conn):
                logger.info(f"Updating artist ID={artist_id}")

                # Validate
                data = ArtistValidator.validate_update(
                    cursor,
                    artist_id=artist_id,
                    channel_id=channel_id,
                    name=name,
                )

                # Update
                updated = ArtistRepository.update(
                    cursor,
                    artist_id=data["artist_id"],
                    channel_id=data["channel_id"],
                    name=data["name"],
                )

                if not updated:
                    raise ArtistNotFoundError(artist_id=artist_id)

                # Get updated artist
                artist = ArtistRepository.get_detail(cursor, artist_id)

                logger.info(f"Artist updated: ID={artist_id}, Name='{name}'")

                return ArtistMapper.to_detail(artist)

        except (
            ArtistNotFoundError,
            ArtistAlreadyExistsError,
            InvalidArtistNameError,
            InvalidChannelError,
        ):
            raise
        except Exception as exc:
            logger.error(f"Error updating artist {artist_id}: {exc}")
            raise ArtistDatabaseError(f"Failed to update artist: {str(exc)}")

    # =====================================================
    # DELETE
    # =====================================================

    @staticmethod
    def delete(
        artist_id: int,
        force: bool = False,
    ) -> Dict[str, Any]:
        """
        Delete an artist.
        
        Args:
            artist_id: Artist ID
            force: Force delete even if has songs (cascade)
            
        Returns:
            Deletion result
            
        Raises:
            ArtistNotFoundError: If artist not found
            ArtistHasSongsError: If artist has songs and force=False
            ArtistDeleteError: If deletion fails
            ArtistDatabaseError: For database errors
        """
        try:
            with get_dict_cursor_with_commit() as (cursor, conn):
                logger.warning(f"Deleting artist ID={artist_id}, force={force}")

                # Validate artist exists
                ArtistValidator.validate_delete(cursor, artist_id)

                # Check songs if not force
                if not force:
                    songs = ArtistRepository.total_songs(cursor, artist_id)
                    if songs > 0:
                        raise ArtistHasSongsError(
                            artist_id=artist_id,
                            song_count=songs
                        )

                # Delete
                deleted = ArtistRepository.delete(cursor, artist_id)

                if not deleted:
                    raise ArtistDeleteError(artist_id=artist_id)

                logger.warning(f"Artist deleted: ID={artist_id}")

                return {
                    "success": True,
                    "message": "Artist berhasil dihapus.",
                    "deleted_id": artist_id,
                }

        except (
            ArtistNotFoundError,
            ArtistHasSongsError,
            ArtistDeleteError,
        ):
            raise
        except Exception as exc:
            logger.error(f"Error deleting artist {artist_id}: {exc}")
            raise ArtistDatabaseError(f"Failed to delete artist: {str(exc)}")

    # =====================================================
    # BULK DELETE
    # =====================================================

    @staticmethod
    def bulk_delete(
        artist_ids: List[int],
        force: bool = False,
    ) -> Dict[str, Any]:
        """
        Bulk delete artists.
        
        Args:
            artist_ids: List of artist IDs
            force: Force delete even if has songs
            
        Returns:
            Bulk deletion result
            
        Raises:
            EmptySelectionError: If no IDs provided
            ArtistNotFoundError: If any artist not found
            ArtistHasSongsError: If artists have songs and force=False
            BulkDeleteError: For bulk deletion errors
        """
        try:
            with get_dict_cursor_with_commit() as (cursor, conn):
                if not artist_ids:
                    raise EmptySelectionError()

                logger.warning(f"Bulk deleting {len(artist_ids)} artists, force={force}")

                # Validate
                validation = ArtistValidator.validate_bulk_delete(
                    cursor,
                    artist_ids,
                    allow_with_songs=force,
                )

                # Delete
                if force:
                    deleted = ArtistBulkRepository.bulk_delete_force(
                        cursor,
                        validation['existing_ids'],
                    )
                else:
                    deleted = ArtistBulkRepository.bulk_delete(
                        cursor,
                        validation['existing_ids'],
                        return_details=True,
                    )

                return {
                    "success": True,
                    "deleted": deleted.get('deleted_count', 0),
                    "message": f"{deleted.get('deleted_count', 0)} artist berhasil dihapus.",
                    "details": deleted,
                }

        except (
            EmptySelectionError,
            ArtistNotFoundError,
            ArtistHasSongsError,
        ):
            raise
        except Exception as exc:
            logger.error(f"Error bulk deleting artists: {exc}")
            raise BulkDeleteError(str(exc))

    # =====================================================
    # BULK UPDATE CHANNEL
    # =====================================================

    @staticmethod
    def bulk_update_channel(
        artist_ids: List[int],
        channel_id: int,
    ) -> Dict[str, Any]:
        """
        Bulk update channel for artists.
        
        Args:
            artist_ids: List of artist IDs
            channel_id: New channel ID
            
        Returns:
            Bulk update result
            
        Raises:
            EmptySelectionError: If no IDs provided
            ArtistNotFoundError: If any artist not found
            InvalidChannelError: If channel not found
            BulkUpdateError: For bulk update errors
        """
        try:
            with get_dict_cursor_with_commit() as (cursor, conn):
                if not artist_ids:
                    raise EmptySelectionError()

                logger.warning(f"Bulk updating channel to {channel_id} for {len(artist_ids)} artists")

                # Validate channel
                ArtistValidator.validate_channel(cursor, channel_id)

                # Validate artists exist
                existing_ids = ArtistValidator.validate_artists_exist(
                    cursor, artist_ids
                )

                # Update
                updated = ArtistBulkRepository.bulk_update_channel(
                    cursor,
                    existing_ids,
                    channel_id,
                )

                return {
                    "success": True,
                    "updated": updated.get('updated_count', 0),
                    "message": f"{updated.get('updated_count', 0)} artist berhasil diupdate.",
                    "details": updated,
                }

        except (
            EmptySelectionError,
            ArtistNotFoundError,
            InvalidChannelError,
        ):
            raise
        except Exception as exc:
            logger.error(f"Error bulk updating channel: {exc}")
            raise BulkUpdateError(str(exc))

    # =====================================================
    # BULK UPDATE NAMES
    # =====================================================

    @staticmethod
    def bulk_update_names(
        updates: Dict[int, str],
    ) -> Dict[str, Any]:
        """
        Bulk update names for artists.
        
        Args:
            updates: Dict mapping artist_id -> new_name
            
        Returns:
            Bulk update result
            
        Raises:
            EmptySelectionError: If no updates provided
            InvalidArtistNameError: If any name is invalid
            ArtistNotFoundError: If any artist not found
            BulkUpdateError: For bulk update errors
        """
        try:
            with get_dict_cursor_with_commit() as (cursor, conn):
                if not updates:
                    raise EmptySelectionError()

                logger.warning(f"Bulk updating names for {len(updates)} artists")

                # Validate names
                validated_updates = {}
                for artist_id, name in updates.items():
                    validated_name = ArtistValidator.validate_name(name)
                    validated_updates[artist_id] = validated_name

                # Validate artists exist
                artist_ids = list(validated_updates.keys())
                ArtistValidator.validate_artists_exist(cursor, artist_ids)

                # Update
                result = ArtistBulkRepository.bulk_update_name(
                    cursor,
                    validated_updates,
                )

                return {
                    "success": True,
                    "updated": result.get('updated_count', 0),
                    "message": f"{result.get('updated_count', 0)} artist berhasil diupdate.",
                    "details": result,
                }

        except (
            EmptySelectionError,
            InvalidArtistNameError,
            ArtistNotFoundError,
        ):
            raise
        except Exception as exc:
            logger.error(f"Error bulk updating names: {exc}")
            raise BulkUpdateError(str(exc))

    # =====================================================
    # BULK INSERT
    # =====================================================

    @staticmethod
    def bulk_insert(
        artists: List[Dict[str, Any]],
        skip_duplicates: bool = True,
    ) -> Dict[str, Any]:
        """
        Bulk insert artists.
        
        Args:
            artists: List of artist data
            skip_duplicates: Skip duplicates
            
        Returns:
            Bulk insert result
            
        Raises:
            EmptySelectionError: If no artists provided
            InvalidArtistDataError: If any data is invalid
            BulkInsertError: For bulk insert errors
        """
        try:
            with get_dict_cursor_with_commit() as (cursor, conn):
                if not artists:
                    raise EmptySelectionError()

                logger.info(f"Bulk inserting {len(artists)} artists")

                # Validate
                validation = ArtistValidator.validate_create_bulk(
                    cursor,
                    artists,
                    skip_duplicates=skip_duplicates,
                )

                # Insert
                result = ArtistBulkRepository.bulk_insert(
                    cursor,
                    validation['validated_artists'],
                    skip_duplicates=skip_duplicates,
                    return_ids=True,
                )

                return {
                    "success": True,
                    "inserted": result.get('inserted_count', 0),
                    "message": f"{result.get('inserted_count', 0)} artist berhasil ditambahkan.",
                    "details": result,
                }

        except (
            EmptySelectionError,
            InvalidArtistNameError,
            InvalidChannelError,
            ArtistAlreadyExistsError,
        ):
            raise
        except Exception as exc:
            logger.error(f"Error bulk inserting artists: {exc}")
            raise BulkInsertError(str(exc))

    # =====================================================
    # STATISTICS
    # =====================================================

    @staticmethod
    def statistics(
        channel_id: Optional[int] = None,
        detailed: bool = False,
    ) -> Dict[str, Any]:
        """
        Get artist statistics.

        Args:
            channel_id: Optional channel filter
            detailed: Get detailed statistics

        Returns:
            Statistics data

        Raises:
            ArtistDatabaseError: For database errors
        """
        try:
            with get_dict_cursor() as (cursor, conn):

                logger.debug(
                    f"Getting artist statistics, channel={channel_id}"
                )

                stats = ArtistStatisticsRepository.statistics(
                    cursor,
                    channel_id,
                )

                return ArtistMapper.to_statistics(stats)

        except Exception as exc:
            logger.error(f"Error getting statistics: {exc}")
            raise ArtistDatabaseError(
                f"Failed to get statistics: {str(exc)}"
            )
    
    # =====================================================
    # TOTAL ARTISTS
    # =====================================================

    @staticmethod
    def total_artists(
        channel_id: Optional[int] = None,
    ) -> int:
        """
        Get total artists count.
        
        Args:
            channel_id: Optional channel filter
            
        Returns:
            Total artists count
            
        Raises:
            ArtistDatabaseError: For database errors
        """
        try:
            with get_dict_cursor() as (cursor, conn):
                return ArtistStatisticsRepository.total_artists(
                    cursor,
                    channel_id,
                )

        except Exception as exc:
            logger.error(f"Error getting total artists: {exc}")
            raise ArtistDatabaseError(f"Failed to get total artists: {str(exc)}")

    # =====================================================
    # TOTAL SONGS
    # =====================================================

    @staticmethod
    def total_songs(
        artist_id: int,
    ) -> int:
        """
        Get total songs for an artist.
        
        Args:
            artist_id: Artist ID
            
        Returns:
            Total songs count
            
        Raises:
            ArtistDatabaseError: For database errors
        """
        try:
            with get_dict_cursor() as (cursor, conn):
                return ArtistStatisticsRepository.total_songs(
                    cursor,
                    artist_id,
                )

        except Exception as exc:
            logger.error(f"Error getting total songs for artist {artist_id}: {exc}")
            raise ArtistDatabaseError(f"Failed to get total songs: {str(exc)}")

    # =====================================================
    # ACTIVE CHANNELS
    # =====================================================

    @staticmethod
    def active_channels() -> int:
        """
        Get active channels count.
        
        Returns:
            Active channels count
            
        Raises:
            ArtistDatabaseError: For database errors
        """
        try:
            with get_dict_cursor() as (cursor, conn):
                return ArtistStatisticsRepository.active_channels(cursor)

        except Exception as exc:
            logger.error(f"Error getting active channels: {exc}")
            raise ArtistDatabaseError(f"Failed to get active channels: {str(exc)}")

    # =====================================================
    # SONG STATUS
    # =====================================================

    @staticmethod
    def song_status(
        artist_id: int,
    ) -> List[Dict[str, Any]]:
        """
        Get song status breakdown for an artist.
        
        Args:
            artist_id: Artist ID
            
        Returns:
            List of status breakdown
            
        Raises:
            ArtistNotFoundError: If artist not found
            ArtistDatabaseError: For database errors
        """
        try:
            with get_dict_cursor() as (cursor, conn):
                # Check artist exists
                ArtistValidator.validate_artist_exists(cursor, artist_id)

                return ArtistStatisticsRepository.song_status(
                    cursor,
                    artist_id,
                )

        except ArtistNotFoundError:
            raise
        except Exception as exc:
            logger.error(f"Error getting song status for artist {artist_id}: {exc}")
            raise ArtistDatabaseError(f"Failed to get song status: {str(exc)}")

    # =====================================================
    # CHANNEL SUMMARY
    # =====================================================

    @staticmethod
    def channel_summary(
        channel_id: int,
    ) -> Dict[str, Any]:
        """
        Get channel summary.
        
        Args:
            channel_id: Channel ID
            
        Returns:
            Channel summary data
            
        Raises:
            ChannelNotFoundError: If channel not found
            ArtistDatabaseError: For database errors
        """
        try:
            with get_dict_cursor() as (cursor, conn):
                logger.debug(f"Getting channel summary: {channel_id}")

                # Validate channel exists
                ChannelService.get_channel(cursor, channel_id)

                summary = ArtistStatisticsRepository.channel_summary(
                    cursor,
                    channel_id,
                )

                return ArtistMapper.to_channel_statistics(summary)

        except ChannelNotFoundError:
            raise
        except Exception as exc:
            logger.error(f"Error getting channel summary {channel_id}: {exc}")
            raise ArtistDatabaseError(f"Failed to get channel summary: {str(exc)}")

    # =====================================================
    # TOP ARTISTS
    # =====================================================

    @staticmethod
    def top_artists(
        channel_id: Optional[int] = None,
        limit: int = 10,
        min_songs: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Get top artists by song count.
        
        Args:
            channel_id: Optional channel filter
            limit: Number of artists
            min_songs: Minimum songs
            
        Returns:
            List of top artists
            
        Raises:
            ArtistDatabaseError: For database errors
        """
        try:
            with get_dict_cursor() as (cursor, conn):
                logger.debug(f"Getting top artists, channel={channel_id}")

                artists = ArtistStatisticsRepository.top_artists(
                    cursor,
                    channel_id=channel_id,
                    limit=limit,
                    min_songs=min_songs,
                )

                return ArtistMapper.to_list_with_stats(artists)

        except Exception as exc:
            logger.error(f"Error getting top artists: {exc}")
            raise ArtistDatabaseError(f"Failed to get top artists: {str(exc)}")

    # =====================================================
    # EXPORT
    # =====================================================

    @staticmethod
    def export_by_channel(
        channel_id: int,
        format: str = "json",
    ) -> Union[List[Dict[str, Any]], str]:
        """
        Export artists by channel.
        
        Args:
            channel_id: Channel ID
            format: Export format (json or csv)
            
        Returns:
            Export data
            
        Raises:
            ChannelNotFoundError: If channel not found
            ArtistDatabaseError: For database errors
        """
        try:
            with get_dict_cursor() as (cursor, conn):
                logger.debug(f"Exporting artists for channel {channel_id}")

                # Validate channel exists
                ChannelService.get_channel(cursor, channel_id)

                artists = ArtistStatisticsRepository.export_channel_artists(
                    cursor,
                    channel_id,
                )

                if format == "csv":
                    # TODO: Implement CSV export
                    return artists
                
                return artists

        except ChannelNotFoundError:
            raise
        except Exception as exc:
            logger.error(f"Error exporting artists: {exc}")
            raise ArtistDatabaseError(f"Failed to export artists: {str(exc)}")

    # =====================================================
    # BULK EXISTS
    # =====================================================

    @staticmethod
    def bulk_exists(
        artist_ids: List[int],
    ) -> Dict[int, bool]:
        """
        Check existence of multiple artists.
        
        Args:
            artist_ids: List of artist IDs
            
        Returns:
            Dict mapping ID -> exists
            
        Raises:
            ArtistDatabaseError: For database errors
        """
        try:
            with get_dict_cursor() as (cursor, conn):
                if not artist_ids:
                    return {}

                return ArtistBulkRepository.existing_ids_with_details(
                    cursor,
                    artist_ids,
                )

        except Exception as exc:
            logger.error(f"Error checking bulk existence: {exc}")
            raise ArtistDatabaseError(f"Failed to check existence: {str(exc)}")


