"""
Export Song Duplicate
=====================

Business logic untuk menduplikasi lagu hasil seleksi.

Duplicate dilakukan pada tahap formatting,
bukan disimpan ke database.
"""

from __future__ import annotations

from app.music.repositories.export.types import SongRow


# ==========================================================
# DUPLICATE SONGS
# ==========================================================


def duplicate_songs(
    songs: list[SongRow],
    *,
    target: int,
    duplicate: int,
) -> list[SongRow]:
    """
    Duplicate selected songs.

    Example

        duplicate = 2

        A
        B
        C

        ↓

        A
        A
        B
        B
        C
        C

    The final result is truncated to the requested target.
    """

    if not songs:
        return []

    if duplicate <= 1:
        return songs[:target]

    duplicated: list[SongRow] = []

    for song in songs:
        duplicated.extend([song] * duplicate)

    return duplicated[:target]