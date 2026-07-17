"""
Songs Bulk Service
==================

Business logic untuk operasi massal Songs.
"""

from __future__ import annotations

from datetime import date

from app.music.repositories.songs.bulk import (
    bulk_delete,
    bulk_update_artist,
    bulk_update_release_date,
    bulk_update_status,
)
from app.music.repositories.songs.artists import (
    artist_exists,
)
from app.music.repositories.songs.types import (
    SongStatus,
)

from .validator import (
    validate_artist_id,
    validate_bulk_song_ids,
    validate_status,
)

# ==========================================================
# BULK UPDATE STATUS
# ==========================================================


def update_status(
    song_ids: list[int],
    status: SongStatus,
) -> int:
    """
    Update status for multiple songs.
    """

    validate_bulk_song_ids(
        song_ids,
    )

    validate_status(
        status,
    )

    return bulk_update_status(
        song_ids,
        status,
    )


# ==========================================================
# BULK UPDATE ARTIST
# ==========================================================


def update_artist(
    song_ids: list[int],
    artist_id: int,
) -> int:
    """
    Move multiple songs to another artist.
    """

    validate_bulk_song_ids(
        song_ids,
    )

    validate_artist_id(
        artist_id,
    )

    if not artist_exists(
        artist_id,
    ):
        raise ValueError(
            "Artist not found."
        )

    return bulk_update_artist(
        song_ids,
        artist_id,
    )


# ==========================================================
# BULK UPDATE RELEASE DATE
# ==========================================================


def update_release_date(
    song_ids: list[int],
    release_date: date | None,
) -> int:
    """
    Update release date for multiple songs.
    """

    validate_bulk_song_ids(
        song_ids,
    )

    return bulk_update_release_date(
        song_ids,
        release_date,
    )


# ==========================================================
# BULK DELETE
# ==========================================================


def delete(
    song_ids: list[int],
) -> int:
    """
    Delete multiple songs.
    """

    validate_bulk_song_ids(
        song_ids,
    )

    return bulk_delete(
        song_ids,
    )
