"""
Songs Router
============

HTTP endpoints untuk feature Songs.
"""

from __future__ import annotations

import random
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import JSONResponse, Response

from app.core.database import get_dict_cursor_dep, get_dict_cursor
from app.music.constants.status import VALID_STATUS
from app.music.repositories.export.types import ExportMode
from app.music.repositories.songs.types import CreateSong, SongStatus, UpdateSong
from app.music.services.export.service import export, status
from app.music.services.songs import service
from app.music.services.songs.search import build_response
from app.music.services.usage import service as usage_service
from app.music.services.usage.types import UsageMode
from app.music.songs.schema import BulkUpdateStatusRequest

router = APIRouter(
    prefix="/songs",
    tags=["Songs"],
)

# ==========================================================
# 1. LIST (STATIC)
# ==========================================================

@router.get("")
def list_songs(
    request: Request,
    draw: int = Query(1),
    keyword: str | None = Query(None),
    channel_id: int | None = Query(None),
    artist_id: int | None = Query(None),
    status: SongStatus | None = Query(None),
    start: int = Query(0, ge=0),
    length: int = Query(25, ge=1, le=100),
    order_by: str = Query("s.id"),
    descending: bool = Query(True),
):
    filters = service.get_filters(
        keyword=keyword,
        channel_id=channel_id,
        artist_id=artist_id,
        status=status,
    )
    return build_response(
        draw=draw,
        filters=filters,
        start=start,
        length=length,
        order_by=order_by,
        descending=descending,
    )


# ==========================================================
# 2. DATA (STATIC)
# ==========================================================

@router.get("/data")
def songs_data(
    request: Request,
    draw: int = Query(1),
    start: int = Query(0, ge=0),
    length: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    channel_id: Optional[int] = Query(None),
    order_column: int = Query(0, alias="order[0][column]"),
    order_dir: str = Query("desc", alias="order[0][dir]"),
    db=Depends(get_dict_cursor_dep),
):
    """Server-side DataTables endpoint"""
    cursor, _ = db
    
    if status and status not in VALID_STATUS:
        return JSONResponse(
            status_code=400, 
            content={"error": f"Invalid status: {status}"}
        )

    base_query = """
        FROM songs s
        JOIN artists a ON s.artist_id = a.id
        JOIN channels c ON a.channel_id = c.id
        WHERE 1=1
    """
    params = []

    if status:
        base_query += " AND s.status = %s"
        params.append(status)

    if channel_id:
        base_query += " AND a.channel_id = %s"
        params.append(channel_id)

    if search:
        keyword = f"%{search}%"
        base_query += """
            AND (
                s.title ILIKE %s
                OR a.name ILIKE %s
                OR c.name ILIKE %s
            )
        """
        params.extend([keyword, keyword, keyword])

    cursor.execute("SELECT COUNT(*) AS total FROM songs")
    total_records = cursor.fetchone()["total"]

    cursor.execute(f"SELECT COUNT(*) AS total {base_query}", params)
    filtered_records = cursor.fetchone()["total"]

    order_columns = {
        0: "s.id",
        1: "s.id",
        2: "a.name",
        3: "s.title",
        4: "s.status",
        5: "s.release_date",
    }
    order_by = order_columns.get(order_column, "s.id")
    order_direction = "DESC" if order_dir.lower() == "desc" else "ASC"

    data_query = f"""
        SELECT
            s.id,
            s.title,
            s.status,
            s.release_date,
            s.created_at,
            a.name AS artist_name,
            c.name AS channel_name
        {base_query}
        ORDER BY {order_by} {order_direction}
        LIMIT %s OFFSET %s
    """
    final_params = params + [length, start]
    cursor.execute(data_query, final_params)
    songs = cursor.fetchall()

    data = []
    for song in songs:
        data.append({
            "id": song["id"],
            "title": song["title"],
            "status": song["status"],
            "release_date": song["release_date"].strftime("%Y-%m-%d") if song["release_date"] else "-",
            "created_at": song["created_at"].strftime("%Y-%m-%d %H:%M") if song["created_at"] else "-",
            "artist_name": song["artist_name"],
            "channel_name": song["channel_name"],
        })

    return {
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": data
    }


# ==========================================================
# 3. STATISTICS (STATIC)
# ==========================================================

@router.get("/statistics")
def statistics():
    return service.get_statistics()


# ==========================================================
# 4. FILTERS (STATIC)
# ==========================================================

@router.get("/filters")
def get_filters(
    db=Depends(get_dict_cursor_dep),
):
    """Get all filters for Songs page."""
    from app.music.repositories.songs.filters import get_song_filters
    return get_song_filters()


@router.get("/channels")
def get_channels(
    db=Depends(get_dict_cursor_dep),
):
    """Get all channels for dropdown."""
    from app.music.repositories.songs.channels import get_channel_options
    return get_channel_options()


@router.get("/artists")
def get_artists(
    channel_id: Optional[int] = Query(None),
    db=Depends(get_dict_cursor_dep),
):
    """Get all artists, optionally filtered by channel."""
    from app.music.repositories.songs.artists import get_artist_options, get_artists_by_channel
    
    if channel_id:
        return get_artists_by_channel(channel_id)
    
    return get_artist_options()


# ==========================================================
# 5. IMPORT (STATIC)
# ==========================================================

@router.post("/import")
def import_songs(
    payload: list[CreateSong],
):
    return service.import_song_list(payload)


# ==========================================================
# 6. BULK OPERATIONS (STATIC)
# ==========================================================



@router.post("/bulk-update")
def bulk_update_songs(
    payload: BulkUpdateStatusRequest,
):
    try:
        updated = service.bulk_update_song_status(
            song_ids=payload.ids,
            status=payload.status,
        )

        return {
            "success": True,
            "message": f"Berhasil mengupdate {updated} lagu",
            "updated_count": updated,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Gagal melakukan bulk update.",
        )

@router.patch("/bulk/artist")
def bulk_update_artist(
    song_ids: list[int],
    artist_id: int,
):
    return {
        "updated": service.bulk_update_song_artist(
            song_ids,
            artist_id,
        )
    }


@router.patch("/bulk/release-date")
def bulk_update_release_date(
    song_ids: list[int],
    release_date: str | None = None,
):
    return {
        "updated": service.bulk_update_song_release_date(
            song_ids,
            release_date,
        )
    }


@router.delete("/bulk")
def bulk_delete_songs(
    song_ids: list[int],
):
    return {
        "deleted": service.bulk_delete_songs(
            song_ids,
        )
    }


# ==========================================================
# 7. EXPORT (STATIC)
# ==========================================================

@router.post("/export-txt")
def export_txt(
    song_ids: list[int] = Form(...),
    db=Depends(get_dict_cursor_dep),
):
    if not song_ids:
        raise HTTPException(400, "Tidak ada lagu dipilih")

    cursor, _ = db
    
    placeholders = ",".join(["%s"] * len(song_ids))
    cursor.execute(
        f"""
        SELECT songs.id, songs.title, artists.name AS artist
        FROM songs
        JOIN artists ON songs.artist_id = artists.id
        WHERE songs.id IN ({placeholders})
        """,
        tuple(song_ids),
    )
    songs = cursor.fetchall()

    if not songs:
        raise HTTPException(404, "Lagu tidak ditemukan")

    # Shuffle and pair
    random.shuffle(songs)
    paired_songs = []
    for song in songs:
        paired_songs.extend([song, song])

    lines = []
    total = len(paired_songs)

    for i, song in enumerate(paired_songs, start=1):
        num = ((i - 1) % 10) + 1
        title = song["title"].strip().lower()
        artist = song["artist"].strip().lower()
        query = f"{title} {artist}".replace(" ", "+")
        yt_url = f"https://www.youtube.com/results?search_query={query}"
        lines.append(f"{num}. 🇺🇲 Judul: {title} {artist}\n{yt_url}")

        if i % 10 == 0 and i != total:
            lines.append("=======================")

    text = "\n\n".join(lines)
    filename = datetime.now().strftime("%d-%m-%Y") + ".txt"

    return Response(
        content=text,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/export/status")
def export_status(
    mode: ExportMode = "normal",
):
    return status(mode=mode)


@router.get("/export/day/{day}")
def export_playlist(
    day: int,
    mode: ExportMode = Query("normal"),
    target: int = Query(160, ge=1, le=1000),
    duplicate: int = Query(2, ge=1, le=20),
    channel_limit: int = Query(2, ge=1),
    excluded_channels: list[int] = Query([]),
) -> Response:
    text = export(
        day=day,
        mode=mode,
        target=target,
        duplicate=duplicate,
        channel_limit=channel_limit,
        excluded_channels=excluded_channels,
    )
    filename = f"{mode}_day_{day}.txt"
    return Response(
        content=text,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ==========================================================
# 8. USAGE (STATIC)
# ==========================================================

@router.get("/usage")
def usage_batches(
    mode: UsageMode = "normal",
):
    return usage_service.usage_batches(mode=mode)


@router.get("/usage/day/{day}")
def usage(
    day: int,
    mode: UsageMode = "normal",
):
    result = usage_service.usage(day=day, mode=mode)
    if result is None:
        raise HTTPException(status_code=404, detail="Export batch not found.")
    return result


@router.delete("/usage/day/{day}")
def delete_usage(
    day: int,
    mode: UsageMode = "normal",
):
    deleted = usage_service.delete_batch(day=day, mode=mode)
    if not deleted:
        raise HTTPException(status_code=404, detail="Export batch not found.")
    return {"deleted": True, "day": day, "mode": mode}


@router.delete("/usage")
def reset_usage(
    mode: UsageMode = "normal",
):
    deleted = usage_service.reset_batches(mode=mode)
    return {"deleted": deleted, "mode": mode}


# ==========================================================
# 9. CREATE (STATIC)
# ==========================================================

@router.post("")
def create_song(
    payload: CreateSong,
):
    return service.create_song(payload)


# ==========================================================
# 10. CRUD WITH PATH PARAM (HARUS DI BAWAH SEMUA STATIC ROUTES)
# ==========================================================

@router.get("/{song_id}")
def get_song(
    song_id: int,
):
    from app.music.repositories.songs.songs import get_song
    song = get_song(song_id)
    if song is None:
        raise HTTPException(status_code=404, detail="Song not found.")
    return song


@router.put("/{song_id}")
def update_song(
    song_id: int,
    payload: UpdateSong,
):
    return service.update_song(song_id, payload)


@router.delete("/{song_id}")
def delete_song(
    song_id: int,
):
    return service.delete_song(song_id)