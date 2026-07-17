"""
Export Formatter
================

Build TXT export output.
"""

from __future__ import annotations

from app.music.repositories.export.types import SongRow

from .labels import (
    build_group_separator,
    get_group_number,
    is_group_end,
)
from .youtube import build_song_youtube_url

# ==========================================================
# SONG LINE
# ==========================================================


def build_song_line(
    number: int,
    song: SongRow,
) -> str:
    """
    Build one song entry.
    """

    title = song["title"].strip().lower()
    artist = song["artist"].strip().lower()

    youtube_url = build_song_youtube_url(song)

    return (
        f"{number}. 🇺🇲 Judul: {title} {artist}\n"
        f"{youtube_url}"
    )


# ==========================================================
# EXPORT TEXT
# ==========================================================


def build_txt(
    songs: list[SongRow],
    *,
    group_size: int = 10,
) -> str:
    """
    Build TXT export.
    """

    if not songs:
        return ""

    lines: list[str] = []

    for index, song in enumerate(songs, start=1):

        number = ((index - 1) % group_size) + 1

        lines.append(
            build_song_line(
                number,
                song,
            )
        )

        if is_group_end(
            index,
            group_size=group_size,
        ):
            lines.append(
                build_group_separator(
                    get_group_number(
                        index,
                        group_size=group_size,
                    )
                )
            )

    return "\n\n".join(lines)