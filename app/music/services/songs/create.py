"""
Songs Create Service
====================

Business logic untuk membuat lagu baru.
"""

from __future__ import annotations

from app.music.repositories.songs.artists import (
    artist_exists,
)
from app.music.repositories.songs.duplicate import (
    find_duplicate_title,
)
from app.music.repositories.songs.songs import (
    create_song,
    get_song,
)
from app.music.repositories.songs.types import (
    CreateSong,
    SongDetail,
)

from .validator import (
    validate_create_song,
)

# ==========================================================
# CREATE SONG
# ==========================================================


def create(
    data: CreateSong,
) -> SongDetail:
    """
    Create new song.

    Workflow

    1. Validate payload
    2. Validate artist
    3. Check duplicate
    4. Insert song
    5. Return created song
    """

    validate_create_song(data)

    if not artist_exists(
        data["artist_id"],
    ):
        raise ValueError(
            "Artist not found."
        )

    if find_duplicate_title(
        artist_id=data["artist_id"],
        title=data["title"],
    ):
        raise ValueError(
            "Song already exists."
        )

    song_id = create_song(data)

    return get_song(song_id)
