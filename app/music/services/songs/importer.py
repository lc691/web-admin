"""
Songs Import Service
====================

Business logic untuk import lagu.

Service ini bertanggung jawab melakukan:

- Validasi data import
- Validasi artist
- Validasi duplicate
- Membuat lagu baru
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
)
from app.music.repositories.songs.types import (
    CreateSong,
)

from .validator import (
    validate_create_song,
)

# ==========================================================
# IMPORT SONG
# ==========================================================


def import_song(
    data: CreateSong,
) -> bool:
    """
    Import single song.

    Duplicate songs will be skipped.

    Returns
    -------
    bool
        True if imported.
        False if skipped.
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
        return False

    create_song(data)

    return True


# ==========================================================
# IMPORT SONGS
# ==========================================================


def import_songs(
    songs: list[CreateSong],
) -> dict:
    """
    Import multiple songs.

    Returns
    -------
    {
        imported,
        skipped,
        total,
    }
    """

    imported = 0
    skipped = 0

    for song in songs:

        if import_song(song):
            imported += 1
        else:
            skipped += 1

    return {
        "total": len(songs),
        "imported": imported,
        "skipped": skipped,
    }
