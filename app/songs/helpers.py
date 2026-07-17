import re
from datetime import datetime
from typing import Optional

from fastapi import HTTPException

from .constants import STATUS_STYLES, VALID_STATUS


def validate_song_data(title: str, status: str, release_date: Optional[str] = None):
    """Validasi data song"""
    title = title.strip()
    if not title:
        raise HTTPException(400, "Judul lagu tidak boleh kosong")
    if len(title) > 255:
        raise HTTPException(400, "Judul lagu maksimal 255 karakter")

    status = status.strip()
    if status not in VALID_STATUS:
        raise HTTPException(400, f"Status tidak valid. Pilih: {', '.join(VALID_STATUS)}")

    if release_date:
        release_date = release_date.strip()
        if release_date:
            try:
                datetime.strptime(release_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(400, "Format release_date harus YYYY-MM-DD")
    else:
        release_date = None

    return title, status, release_date


def format_song_response(song: dict) -> dict:
    """Format response song untuk DataTables - TABLER VERSION"""
    status = song.get("status", "Review")
    status_info = STATUS_STYLES.get(status, STATUS_STYLES["Review"])

    return {
        "id": song["id"],
        "channel_name": song.get("channel_name", "-"),
        "artist_name": song.get("artist_name", "Unknown"),
        "title": song.get("title", "Untitled"),
        "status": status,
        "status_badge": (
            f'<span class="badge {status_info["badge"]}">'
            f'<i class="fas {status_info["icon"]} me-1"></i>{status}</span>'
        ),
        "release_date": (
            song["release_date"].strftime("%Y-%m-%d")
            if song.get("release_date") and hasattr(song["release_date"], "strftime")
            else None
        ),
        "created_at": (
            song["created_at"].strftime("%Y-%m-%d %H:%M")
            if song.get("created_at") and hasattr(song["created_at"], "strftime")
            else None
        ),
    }


def get_artist_channel_id(cursor, artist_id: int) -> Optional[int]:
    """Get channel_id from artist_id"""
    cursor.execute("SELECT channel_id FROM artists WHERE id = %s", (artist_id,))
    result = cursor.fetchone()
    return result["channel_id"] if result else None