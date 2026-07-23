"""
Artist Service
"""

from app.core.database import get_dict_cursor

from app.music.repositories.artists.repository import ArtistRepository
from app.music.repositories.artists.filter import ArtistFilterRepository
from app.music.repositories.artists.statistics import ArtistStatisticsRepository
from app.music.repositories.artists.bulk import ArtistBulkRepository
from app.music.services.channels.service import ChannelService

from app.music.services.artists.mapper import ArtistMapper
from app.music.services.artists.validator import (
    ArtistValidator,
)

from app.music.services.artists.exceptions import (
    ArtistAlreadyExistsError,
    ArtistDatabaseError,
    ArtistDeleteError,
    ArtistHasSongsError,
    ArtistNotFoundError,
    BulkDeleteError,
    EmptySelectionError,
    InvalidArtistNameError,
    InvalidChannelError,
    ChannelNotFoundError,
)


class ArtistService:
    """
    Service Artist.
    """

    # =====================================================
    # GET BY ID
    # =====================================================

    @staticmethod
    def get_by_id(artist_id: int):

        try:
            with get_dict_cursor() as (cursor, conn):

                artist = ArtistRepository.get_by_id(
                    cursor,
                    artist_id,
                )

                if not artist:
                    raise ArtistNotFoundError()

                return ArtistMapper.to_response(artist)

        except ArtistNotFoundError:
            raise

        except Exception as exc:
            raise ArtistDatabaseError(str(exc))

    # =====================================================
    # DETAIL
    # =====================================================

    @staticmethod
    def get_detail(artist_id: int):

        try:
            with get_dict_cursor() as (cursor, conn):

                artist = ArtistRepository.get_detail(
                    cursor,
                    artist_id,
                )

                if not artist:
                    raise ArtistNotFoundError()

                return ArtistMapper.to_detail(artist)

        except ArtistNotFoundError:
            raise

        except Exception as exc:
            raise ArtistDatabaseError(str(exc))

    # =====================================================
    # GET ALL
    # =====================================================

    @staticmethod
    def get_all(channel_id: int | None = None):

        try:
            with get_dict_cursor() as (cursor, conn):

                rows = ArtistRepository.get_all(
                    cursor,
                    channel_id=channel_id,
                )

                return ArtistMapper.to_list(rows)

        except Exception as exc:
            raise ArtistDatabaseError(str(exc))

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
        channel_id: int | None = None,
        order_column: int = 1,
        order_dir: str = "desc",
    ):

        try:
            with get_dict_cursor() as (cursor, conn):

                result = ArtistFilterRepository.datatable(
                    cursor=cursor,
                    start=start,
                    length=length,
                    search=search,
                    channel_id=channel_id,
                    order_column=order_column,
                    order_dir=order_dir,
                )

                rows = ArtistMapper.to_list(result["rows"])

                return {
                    "draw": draw,
                    "recordsTotal": result["recordsTotal"],
                    "recordsFiltered": result["recordsFiltered"],
                    "data": rows,
                }

        except Exception as exc:
            raise ArtistDatabaseError(str(exc))

    # =====================================================
    # SEARCH
    # =====================================================

    @staticmethod
    def search(
        keyword: str,
        limit: int = 20,
    ):

        try:
            with get_dict_cursor() as (cursor, conn):

                rows = ArtistFilterRepository.search(
                    cursor,
                    keyword,
                    limit,
                )

                return ArtistMapper.to_select(rows)

        except Exception as exc:
            raise ArtistDatabaseError(str(exc))

    # =====================================================
    # CHANNELS
    # =====================================================

    @staticmethod
    def get_channels():

        try:
            with get_dict_cursor() as (cursor, conn):

                rows = ArtistRepository.get_channels(cursor)

                return ArtistMapper.channels(rows)

        except Exception as exc:
            raise ArtistDatabaseError(str(exc))

    @staticmethod
    def get_channel(
        cursor,
        channel_id: int,
    ):
        try:

            row = ArtistRepository.get_channel(
                cursor,
                channel_id,
            )

            if not row:
                raise ChannelNotFoundError(
                    f"Channel dengan ID {channel_id} tidak ditemukan."
                )

            return ArtistMapper.channel(row)

        except ChannelNotFoundError:
            raise

        except Exception as exc:
            raise ArtistDatabaseError(str(exc))

    # =====================================================
    # CREATE
    # =====================================================

    @staticmethod
    def create(
        *,
        channel_id: int,
        name: str,
    ):

        try:
            with get_dict_cursor(commit=True) as (cursor, conn):

                data = ArtistValidator.validate_create(
                    cursor,
                    channel_id=channel_id,
                    name=name,
                )

                artist = ArtistRepository.create(
                    cursor,
                    channel_id=data["channel_id"],
                    name=data["name"],
                )

                artist = ArtistRepository.get_detail(
                    cursor,
                    artist["id"],
                )

                return ArtistMapper.to_detail(artist)

        except (
            ArtistNotFoundError,
            ArtistAlreadyExistsError,
            InvalidArtistNameError,
            InvalidChannelError,
        ):
            raise

        except Exception as exc:
            raise ArtistDatabaseError(str(exc))

    # =====================================================
    # UPDATE
    # =====================================================

    @staticmethod
    def update(
        *,
        artist_id: int,
        channel_id: int,
        name: str,
    ):

        try:
            with get_dict_cursor(commit=True) as (cursor, conn):

                data = ArtistValidator.validate_update(
                    cursor,
                    artist_id=artist_id,
                    channel_id=channel_id,
                    name=name,
                )

                updated = ArtistRepository.update(
                    cursor,
                    artist_id=data["artist_id"],
                    channel_id=data["channel_id"],
                    name=data["name"],
                )

                if not updated:
                    raise ArtistNotFoundError()

                artist = ArtistRepository.get_detail(
                    cursor,
                    artist_id,
                )

                return ArtistMapper.to_detail(artist)

        except (
            ArtistNotFoundError,
            ArtistAlreadyExistsError,
            InvalidArtistNameError,
            InvalidChannelError,
        ):
            raise

        except Exception as exc:
            raise ArtistDatabaseError(str(exc))

    # =====================================================
    # DELETE
    # =====================================================

    @staticmethod
    def delete(
        artist_id: int,
    ):

        try:
            with get_dict_cursor(commit=True) as (cursor, conn):

                ArtistValidator.validate_delete(
                    cursor,
                    artist_id,
                )

                songs = ArtistRepository.total_songs(
                    cursor,
                    artist_id,
                )

                if songs > 0:
                    raise ArtistHasSongsError()

                deleted = ArtistRepository.delete(
                    cursor,
                    artist_id,
                )

                if not deleted:
                    raise ArtistDeleteError()

                return {
                    "success": True,
                    "message": "Artist berhasil dihapus.",
                }

        except (
            ArtistNotFoundError,
            ArtistHasSongsError,
            ArtistDeleteError,
        ):
            raise

        except Exception as exc:
            raise ArtistDatabaseError(str(exc))


    # =====================================================
    # BULK DELETE
    # =====================================================

    @staticmethod
    def bulk_delete(
        artist_ids: list[int],
    ):

        try:
            with get_dict_cursor(commit=True) as (cursor, conn):

                if not artist_ids:
                    raise EmptySelectionError()

                exists = ArtistBulkRepository.existing_ids(
                    cursor,
                    artist_ids,
                )

                if not exists:
                    raise ArtistNotFoundError()

                artists = ArtistBulkRepository.artists_with_songs(
                    cursor,
                    exists,
                )

                if artists:
                    raise ArtistHasSongsError(
                        "Masih terdapat artist yang memiliki lagu."
                    )

                deleted = ArtistBulkRepository.bulk_delete(
                    cursor,
                    exists,
                )

                return {
                    "success": True,
                    "deleted": deleted,
                    "message": f"{deleted} artist berhasil dihapus.",
                }

        except (
            EmptySelectionError,
            ArtistNotFoundError,
            ArtistHasSongsError,
        ):
            raise

        except Exception as exc:
            raise BulkDeleteError(str(exc))

    # =====================================================
    # STATISTICS
    # =====================================================

    @staticmethod
    def statistics(
        channel_id: int | None = None,
    ):

        try:
            with get_dict_cursor() as (cursor, conn):

                stats = ArtistStatisticsRepository.statistics(
                    cursor,
                    channel_id,
                )

                return ArtistMapper.to_statistics(
                    stats,
                )

        except Exception as exc:
            raise ArtistDatabaseError(str(exc))

    # =====================================================
    # TOTAL ARTISTS
    # =====================================================

    @staticmethod
    def total_artists(
        channel_id: int | None = None,
    ):

        try:
            with get_dict_cursor() as (cursor, conn):

                return ArtistStatisticsRepository.total_artists(
                    cursor,
                    channel_id,
                )

        except Exception as exc:
            raise ArtistDatabaseError(str(exc))

    # =====================================================
    # TOTAL SONGS
    # =====================================================

    @staticmethod
    def total_songs(
        artist_id: int,
    ):

        try:
            with get_dict_cursor() as (cursor, conn):

                return ArtistStatisticsRepository.total_songs(
                    cursor,
                    artist_id,
                )

        except Exception as exc:
            raise ArtistDatabaseError(str(exc))

    # =====================================================
    # ACTIVE CHANNELS
    # =====================================================

    @staticmethod
    def active_channels():

        try:
            with get_dict_cursor() as (cursor, conn):

                return ArtistStatisticsRepository.active_channels(
                    cursor,
                )

        except Exception as exc:
            raise ArtistDatabaseError(str(exc))

    # =====================================================
    # SONG STATUS
    # =====================================================

    @staticmethod
    def song_status(
        artist_id: int,
    ):

        try:
            with get_dict_cursor() as (cursor, conn):

                return ArtistStatisticsRepository.song_status(
                    cursor,
                    artist_id,
                )

        except Exception as exc:
            raise ArtistDatabaseError(str(exc))

    # =====================================================
    # CHANNEL SUMMARY
    # =====================================================

    @staticmethod
    def channel_summary(
        channel_id: int,
    ):

        try:
            with get_dict_cursor() as (cursor, conn):

                return ArtistStatisticsRepository.channel_summary(
                    cursor,
                    channel_id,
                )

        except Exception as exc:
            raise ArtistDatabaseError(str(exc))