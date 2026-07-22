"""
Channel Service
"""

from app.core.datatable import DataTable

from app.music.repositories.channels.bulk import ChannelBulkRepository
from app.music.repositories.channels.filter import ChannelFilterRepository
from app.music.repositories.channels.repository import ChannelRepository
from app.music.repositories.channels.statistics import (
    ChannelStatisticsRepository,
)

from .exceptions import ChannelNotFoundError
from .validator import ChannelValidator


class ChannelService:
    """
    Business logic untuk Channel.
    """

    SORT_COLUMNS = [
        None,
        "id",
        "name",
        "email",
        "artists",
        "songs",
        "vermuk",
        "updated_at",
        None,
    ]

    # =====================================================
    # CRUD
    # =====================================================

    @staticmethod
    def create(
        cursor,
        *,
        name: str,
        email: str | None = None,
        password: str | None = None,
        vermuk: bool = False,
        notes: str | None = None,
    ) -> int:

        ChannelValidator.validate_create(
            cursor,
            name=name,
            email=email,
        )

        return ChannelRepository.create(
            cursor,
            name=ChannelValidator.validate_name(name),
            email=ChannelValidator.validate_email(email),
            password=ChannelValidator.validate_password(password),
            vermuk=vermuk,
            notes=ChannelValidator.validate_notes(notes),
        )

    @staticmethod
    def update(
        cursor,
        *,
        channel_id: int,
        name: str,
        email: str | None = None,
        password: str | None = None,
        vermuk: bool = False,
        notes: str | None = None,
    ) -> bool:

        ChannelValidator.validate_update(
            cursor,
            channel_id=channel_id,
            name=name,
            email=email,
        )

        return ChannelRepository.update(
            cursor,
            channel_id=channel_id,
            name=ChannelValidator.validate_name(name),
            email=ChannelValidator.validate_email(email),
            password=ChannelValidator.validate_password(password),
            vermuk=vermuk,
            notes=ChannelValidator.validate_notes(notes),
        )

    @staticmethod
    def delete(
        cursor,
        channel_id: int,
    ) -> bool:

        if not ChannelRepository.exists(cursor, channel_id):
            raise ChannelNotFoundError(
                "Channel tidak ditemukan."
            )

        return ChannelRepository.delete(
            cursor,
            channel_id,
        )

    # =====================================================
    # DETAIL
    # =====================================================


    @staticmethod
    def detail(
        cursor,
        channel_id: int,
    ):

        channel = ChannelRepository.get_by_id(
            cursor,
            channel_id,
        )

        if channel is None:
            raise ChannelNotFoundError(
                "Channel tidak ditemukan."
            )

        return channel

    # =====================================================
    # DATATABLE
    # =====================================================

    @classmethod
    def datatable(
        cls,
        cursor,
        dt: DataTable,
    ):

        return ChannelFilterRepository.apply(
            cursor,
            keyword=dt.search,
            vermuk=dt.get_bool("vermuk"),
            order_by=dt.sort_column(cls.SORT_COLUMNS),
            order_dir=dt.sort_direction,
            start=dt.offset,
            length=dt.limit,
        )

    @staticmethod
    def count_filtered(
        cursor,
        dt: DataTable,
    ):

        return ChannelFilterRepository.count_filtered(
            cursor,
            keyword=dt.search,
            vermuk=dt.get_bool("vermuk"),
        )

    # =====================================================
    # BULK
    # =====================================================

    @staticmethod
    def bulk_delete(
        cursor,
        ids,
    ):

        return ChannelBulkRepository.bulk_delete(
            cursor,
            ids,
        )

    @staticmethod
    def bulk_update_vermuk(
        cursor,
        ids,
        vermuk: bool,
    ):

        return ChannelBulkRepository.bulk_update_vermuk(
            cursor,
            ids,
            vermuk,
        )

    # =====================================================
    # STATISTICS
    # =====================================================

    @staticmethod
    def statistics(cursor):

        return ChannelStatisticsRepository.summary(
            cursor,
        )