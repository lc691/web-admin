"""
Songs Service
=============

Main orchestrator untuk feature Songs.

Seluruh endpoint hanya berinteraksi dengan
service ini.

Service ini mengorkestrasi seluruh business logic
dari sub-service.
"""

from __future__ import annotations

from app.music.repositories.songs.types import (
    CreateSong,
    SongDetail,
    SongFilters,
    SongListResult,
    SongStatistics,
    SongStatus,
    UpdateSong,
)

from .bulk import (
    bulk_delete,
    bulk_update_artist,
    bulk_update_release_date,
    bulk_update_status,
)
from .create import (
    create,
)
from .delete import (
    delete,
)
from .filter import (
    build_filters,
)
from .importer import (
    import_songs,
)

from .detail import (
    get_song as get_song_detail,
)

from .search import (
    search,
)
from .statistics import (
    get_song_statistics,
)
from .update import (
    update,
)

# ==========================================================
# CREATE
# ==========================================================


def create_song(
    data: CreateSong,
) -> SongDetail:
    """
    Create song.
    """

    return create(data)


# ==========================================================
# UPDATE
# ==========================================================


def update_song(
    song_id: int,
    data: UpdateSong,
) -> SongDetail:
    """
    Update song.
    """

    return update(
        song_id,
        data,
    )


# ==========================================================
# DELETE
# ==========================================================


def delete_song(
    song_id: int,
) -> SongDetail:
    """
    Delete song.
    """

    return delete(song_id)

# ==========================================================
# DETAIL
# ==========================================================


def get_song(
    song_id: int,
) -> SongDetail | None:
    """
    Get single song.
    """

    return get_song_detail(song_id)

# ==========================================================
# SEARCH
# ==========================================================


def search_songs(
    *,
    filters: SongFilters,
    start: int,
    length: int,
    order_by: str = "s.id",
    descending: bool = True,
) -> SongListResult:
    """
    Search songs.
    """

    return search(
        filters=filters,
        start=start,
        length=length,
        order_by=order_by,
        descending=descending,
    )


# ==========================================================
# FILTERS
# ==========================================================


def get_filters(
    *,
    keyword: str | None = None,
    channel_id: int | None = None,
    artist_id: int | None = None,
    status: SongStatus | None = None,
) -> SongFilters:
    """
    Build filters.
    """

    return build_filters(
        keyword=keyword,
        channel_id=channel_id,
        artist_id=artist_id,
        status=status,
    )


# ==========================================================
# STATISTICS
# ==========================================================


def get_statistics() -> SongStatistics:
    """
    Return dashboard statistics.
    """

    return get_song_statistics()


# ==========================================================
# IMPORT
# ==========================================================


def import_song_list(
    songs: list[CreateSong],
) -> dict:
    """
    Import songs.
    """

    return import_songs(
        songs,
    )

# ==========================================================
# BULK
# ==========================================================


def bulk_update_song_status(
    song_ids: list[int],
    status: SongStatus,
) -> int:
    """
    Bulk update status.
    """

    return bulk_update_status(
        song_ids,
        status,
    )


def bulk_update_song_artist(
    song_ids: list[int],
    artist_id: int,
) -> int:
    """
    Bulk update artist.
    """

    return bulk_update_artist(
        song_ids,
        artist_id,
    )


def bulk_update_song_release_date(
    song_ids: list[int],
    release_date,
) -> int:
    """
    Bulk update release date.
    """

    return bulk_update_release_date(
        song_ids,
        release_date,
    )


def bulk_delete_songs(
    song_ids: list[int],
) -> int:
    """
    Bulk delete songs.
    """

    return bulk_delete(
        song_ids,
    )

