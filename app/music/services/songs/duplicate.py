"""
Songs Duplicate Service
=======================

Business logic untuk validasi lagu duplikat.
"""

from __future__ import annotations

from app.music.repositories.songs.duplicate import (
    find_duplicate_title,
)


# ==========================================================
# CHECK DUPLICATE
# ==========================================================


def check_duplicate(
    *,
    artist_id: int,
    title: str,
    exclude_song_id: int | None = None,
) -> None:
    """
    Raise ValueError if duplicate song exists.
    """

    if find_duplicate_title(
        artist_id=artist_id,
        title=title,
        exclude_song_id=exclude_song_id,
    ):
        raise ValueError(
            "Song already exists."
        )


# ==========================================================
# IS DUPLICATE
# ==========================================================


def is_duplicate(
    *,
    artist_id: int,
    title: str,
    exclude_song_id: int | None = None,
) -> bool:
    """
    Return True if duplicate song exists.
    """

    return find_duplicate_title(
        artist_id=artist_id,
        title=title,
        exclude_song_id=exclude_song_id,
    )
