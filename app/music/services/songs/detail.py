"""
Song Detail Service
===================

Business logic untuk mengambil detail lagu.
"""

from __future__ import annotations

from fastapi import HTTPException

from app.music.repositories.songs.songs import get_song as repository_get_song
from app.music.repositories.songs.types import SongDetail


def get_song(
    song_id: int,
) -> SongDetail:
    """
    Get song by id.
    """

    song = repository_get_song(song_id)

    if song is None:
        raise HTTPException(
            status_code=404,
            detail="Song not found.",
        )

    return song