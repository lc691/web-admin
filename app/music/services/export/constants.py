"""
Export Constants
================

Konstanta yang digunakan
oleh seluruh modul export.
"""

from __future__ import annotations

# ==========================================================
# PLAYLIST
# ==========================================================

#: Jumlah lagu dalam satu grup.
GROUP_SIZE: int = 10

#: Prefix setiap judul lagu.
SONG_PREFIX: str = "🇺🇲 Judul:"

#: Separator antar grup.
GROUP_SEPARATOR: str = "================="

#: Label sebelum separator.
GROUP_LABEL_PREFIX: str = "NAMA ABSEN :"


# ==========================================================
# EXPORT
# ==========================================================

#: Target default jumlah lagu unik.
DEFAULT_TARGET: int = 140

#: Jumlah duplikasi default.
DEFAULT_DUPLICATE: int = 2

#: Maksimal lagu dari satu channel.
DEFAULT_MAX_SONG_PER_CHANNEL: int = 1


# ==========================================================
# FILE
# ==========================================================

#: Template nama file hasil export.
EXPORT_FILENAME_TEMPLATE: str = "playlist_day_{day}_{mode}.txt"

#: MIME Type file export.
EXPORT_MEDIA_TYPE: str = "text/plain; charset=utf-8"


# ==========================================================
# YOUTUBE
# ==========================================================

#: Prefix URL pencarian YouTube.
YOUTUBE_SEARCH_URL: str = (
    "https://www.youtube.com/results?search_query="
)


# ==========================================================
# GROUP LABELS
# ==========================================================

#: Jumlah maksimal grup dalam satu playlist.
MAX_GROUP_COUNT: int = 30