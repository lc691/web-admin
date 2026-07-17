"""
Songs Delete Service
====================

Business logic untuk menghapus lagu.
"""

from __future__ import annotations

from app.music.repositories.songs.songs import (
    delete_song,
    get_song,
    song_exists,
)
from app.music.repositories.songs.types import (
    SongDetail,
)

from .validator import (
    validate_delete_song,
)

# ==========================================================
# DELETE SONG
# ==========================================================


def delete(
    song_id: int,
) -> SongDetail:
    """
    Delete a song.

    Workflow

    1. Validate request
    2. Validate song exists
    3. Load song
    4. Delete song
    5. Return deleted song
    """

    validate_delete_song(
        song_id,
    )

    if not song_exists(song_id):
        raise ValueError(
            "Song not found."
        )

    song = get_song(song_id)

    delete_song(
        song_id,
    )

    return song


# ==========================================================
# DELETE MULTIPLE
# ==========================================================


def delete_multiple(
    song_ids: list[int],
) -> int:
    """
    Delete multiple songs.

    Returns
        Number of deleted songs.
    """

    from app.music.repositories.songs.bulk import (
        bulk_delete,
    )

    from .validator import (
        validate_bulk_song_ids,
    )

    validate_bulk_song_ids(
        song_ids,
    )

    return bulk_delete(
        song_ids,
    )
