"""
Songs Formatter
===============

Formatter untuk feature Songs.

Formatter hanya bertanggung jawab mengubah
hasil repository menjadi format yang digunakan
oleh UI atau API.
"""

from __future__ import annotations

from app.music.repositories.songs.types import (
    SongDetail,
    SongListResult,
    SongRow,
    SongStatistics,
)

# ==========================================================
# SONG
# ==========================================================


def format_song(
    song: SongDetail | SongRow | None,
):
    """
    Format single song.
    """

    if song is None:
        return None

    return dict(song)


# ==========================================================
# SONG LIST
# ==========================================================


def format_song_list(
    result: SongListResult,
) -> SongListResult:
    """
    Format song list.
    """

    return {
        "total": result["total"],
        "filtered": result["filtered"],
        "songs": [
            format_song(song)
            for song in result["songs"]
        ],
    }


# ==========================================================
# STATISTICS
# ==========================================================


def format_statistics(
    statistics: SongStatistics,
) -> SongStatistics:
    """
    Format statistics.
    """

    return {
        "total": statistics["total"],
        "live": statistics["live"],
        "review": statistics["review"],
        "approved": statistics["approved"],
    }


# ==========================================================
# DATATABLE
# ==========================================================


def format_datatable(
    result: SongListResult,
) -> dict:
    """
    Format DataTables response.
    """

    return {
        "recordsTotal": result["total"],
        "recordsFiltered": result["filtered"],
        "data": [
            format_song(song)
            for song in result["songs"]
        ],
    }
