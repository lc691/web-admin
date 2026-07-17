"""
Export YouTube Helper
=====================

Helper untuk membangun URL pencarian YouTube
berdasarkan judul dan artis.

Tidak mengandung business logic export.
"""

from __future__ import annotations

from urllib.parse import quote_plus

from app.music.repositories.export.types import SongRow


# ==========================================================
# NORMALIZE
# ==========================================================


def normalize_text(
    value: str,
) -> str:
    """
    Normalize text for YouTube search.
    """

    return " ".join(
        value.strip().lower().split()
    )


# ==========================================================
# SEARCH QUERY
# ==========================================================


def build_search_query(
    title: str,
    artist: str,
) -> str:
    """
    Build YouTube search query.

    Example

        hello adele
    """

    title = normalize_text(title)
    artist = normalize_text(artist)

    return f"{title} {artist}"


# ==========================================================
# SEARCH QUERY FROM SONG
# ==========================================================


def build_song_query(
    song: SongRow,
) -> str:
    """
    Build search query from SongRow.
    """

    return build_search_query(
        song["title"],
        song["artist"],
    )


# ==========================================================
# YOUTUBE URL
# ==========================================================


def build_youtube_url(
    title: str,
    artist: str,
) -> str:
    """
    Build YouTube search URL.
    """

    query = build_search_query(
        title,
        artist,
    )

    return (
        "https://www.youtube.com/results"
        f"?search_query={quote_plus(query)}"
    )


# ==========================================================
# YOUTUBE URL FROM SONG
# ==========================================================


def build_song_youtube_url(
    song: SongRow,
) -> str:
    """
    Build YouTube search URL from SongRow.
    """

    return build_youtube_url(
        song["title"],
        song["artist"],
    )