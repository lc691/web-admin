"""
Songs Update Service
====================

Business logic untuk memperbarui lagu.
"""

from __future__ import annotations

from app.music.repositories.songs.artists import (
    artist_exists,
)
from app.music.repositories.songs.duplicate import (
    find_duplicate_title,
)
from app.music.repositories.songs.songs import (
    get_song,
    song_exists,
    update_song,
)
from app.music.repositories.songs.types import (
    SongDetail,
    UpdateSong,
)

from .validator import (
    validate_update_song,
)

# ==========================================================
# UPDATE SONG
# ==========================================================


def update(
    song_id: int,
    data: UpdateSong,
) -> SongDetail:
    """
    Update song.

    Workflow

    1. Validate payload
    2. Validate song exists
    3. Validate artist exists
    4. Check duplicate title
    5. Update song
    6. Return updated song
    """

    validate_update_song(
        song_id,
        data,
    )

    if not song_exists(song_id):
        raise ValueError(
            "Song not found."
        )

    if not artist_exists(
        data["artist_id"],
    ):
        raise ValueError(
            "Artist not found."
        )

    if find_duplicate_title(
        artist_id=data["artist_id"],
        title=data["title"],
        exclude_song_id=song_id,
    ):
        raise ValueError(
            "Song already exists."
        )

    update_song(
        song_id,
        data,
    )

    return get_song(song_id)
