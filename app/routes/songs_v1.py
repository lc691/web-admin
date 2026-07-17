import random
import re
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from pydantic import BaseModel
from starlette.status import HTTP_302_FOUND

from app.templates import templates
from app.core.database import get_dict_cursor, get_dict_cursor_dep
from .channels import get_or_create_channel
from ..music.services.export.service import has_day_export
from ..music.services.export.repository import get_export_information
from ..music.services.export.types import ExportMode
from ..services.usage.usage_repository import get_day_usage, get_day_usage_stats

router = APIRouter()

# ===========================
# CONSTANTS
# ===========================
VALID_STATUS = {"Review", "Approved", "Live", "Take Down", "Topic"}

STATUS_STYLES = {
    "Live": {"badge": "success", "icon": "fa-play-circle"},
    "Approved": {"badge": "warning", "icon": "fa-check-circle"},
    "Take Down": {"badge": "danger", "icon": "fa-ban"},
    "Topic": {"badge": "info", "icon": "fa-tag"},
    "Review": {"badge": "secondary", "icon": "fa-clock"},
}


# ===========================
# PYDANTIC MODELS
# ===========================
class ExportPreviewPayload(BaseModel):
    duplicate_count: int = 2
    target_count: int = 30
    max_song_per_channel: int = 1
    excluded_channels: Optional[List[int]] = []
    exclude_mode: str = "blacklist"


# ===========================
# HELPER FUNCTIONS
# ===========================
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
    """Format response song untuk DataTables"""
    status = song.get("status", "Review")
    status_info = STATUS_STYLES.get(status, STATUS_STYLES["Review"])

    return {
        "id": song["id"],
        "channel_name": song.get("channel_name", "-"),
        "artist_name": song.get("artist_name", "Unknown"),
        "title": song.get("title", "Untitled"),
        "status": status,
        "status_badge": (
            f'<span class="badge badge-{status_info["badge"]}">'
            f'<i class="fas {status_info["icon"]} mr-1"></i>{status}</span>'
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


# ===========================
# LIST SONGS (Main Page)
# ===========================
@router.get("/songs", response_class=HTMLResponse)
def list_songs(
    request: Request,
    channel_id: Optional[int] = Query(None, description="Filter by channel"),
):
    with get_dict_cursor() as (cursor, _):
        # Get artists for sidebar
        artist_query = """
            SELECT a.id, a.name, COUNT(s.id) as song_count
            FROM artists a
            LEFT JOIN songs s ON a.id = s.artist_id
        """
        artist_params = []
        
        if channel_id:
            artist_query += " WHERE a.channel_id = %s"
            artist_params.append(channel_id)
        
        artist_query += " GROUP BY a.id, a.name ORDER BY a.name"
        cursor.execute(artist_query, artist_params)
        artists = cursor.fetchall()

        # Get statistics
        stats_query = """
            SELECT 
                COUNT(*) as total_songs,
                COUNT(CASE WHEN s.status = 'Live' THEN 1 END) as live_songs,
                COUNT(CASE WHEN s.status = 'Approved' THEN 1 END) as approved_songs,
                COUNT(CASE WHEN s.status = 'Review' THEN 1 END) as review_songs,
                COUNT(CASE WHEN s.status = 'Take Down' THEN 1 END) as takedown_songs,
                COUNT(CASE WHEN s.status = 'Topic' THEN 1 END) as topic_songs
            FROM songs s
            JOIN artists a ON s.artist_id = a.id
        """
        stats_params = []
        
        if channel_id:
            stats_query += " WHERE a.channel_id = %s"
            stats_params.append(channel_id)
        
        cursor.execute(stats_query, stats_params)
        stats = cursor.fetchone()

        # Get channel info if provided
        channel = None
        if channel_id:
            cursor.execute("SELECT id, name FROM channels WHERE id = %s", (channel_id,))
            channel = cursor.fetchone()

        # Get used days
        cursor.execute("""
            SELECT DISTINCT day
            FROM song_usage
            ORDER BY day
        """)
        used_days = [row["day"] for row in cursor.fetchall()]

    return templates.TemplateResponse(
        "songs/v1/list.html",
        {
            "request": request,
            "artists": artists,
            "channel": channel,
            "total_songs": stats["total_songs"] or 0,
            "live_songs": stats["live_songs"] or 0,
            "approved_songs": stats["approved_songs"] or 0,
            "review_songs": stats["review_songs"] or 0,
            "used_days": used_days,
        },
    )


# ===========================
# DATATABLES SERVER-SIDE DATA
# ===========================
@router.get("/songs/data")
def songs_data(
    request: Request,
    draw: int = Query(...),
    start: int = Query(0, ge=0),
    length: int = Query(10, ge=1, le=100),
    search: str = Query(""),
    status: Optional[str] = Query(None),
    channel_id: Optional[str] = Query(None),
    order_column: int = Query(1, alias="order[0][column]"),
    order_dir: str = Query("desc", alias="order[0][dir]"),
    db=Depends(get_dict_cursor_dep),
):
    """Server-side DataTables endpoint"""
    cursor, _ = db

    if status and status not in VALID_STATUS:
        return JSONResponse(
            status_code=400, content={"error": f"Invalid status: {status}"}
        )

    # Build base query
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

    if channel_id and str(channel_id).isdigit():
        base_query += " AND a.channel_id = %s"
        params.append(int(channel_id))

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

    # Total records
    cursor.execute("SELECT COUNT(*) AS total FROM songs")
    total_records = cursor.fetchone()["total"]

    # Filtered records
    cursor.execute(f"SELECT COUNT(*) AS total {base_query}", params)
    filtered_records = cursor.fetchone()["total"]

    # Ordering
    order_columns = {
        0: "s.id",
        1: "s.id",
        2: "a.name",
        3: "s.title",
        4: "s.status",
        5: "s.release_date",
    }
    order_by = order_columns.get(order_column, "s.id")
    order_direction = "DESC" if str(order_dir).lower() == "desc" else "ASC"

    # Main query
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

    return {
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": [format_song_response(song) for song in songs],
    }


# ===========================
# FORM CREATE SONG
# ===========================
@router.get("/songs/new", response_class=HTMLResponse)
def new_song_form(request: Request, channel_id: Optional[int] = Query(None)):
    with get_dict_cursor() as (cursor, _):
        if channel_id:
            cursor.execute(
                "SELECT id, name FROM artists WHERE channel_id = %s ORDER BY name",
                (channel_id,),
            )
        else:
            cursor.execute("SELECT id, name FROM artists ORDER BY name")
        artists = cursor.fetchall()

        channel = None
        if channel_id:
            cursor.execute("SELECT id, name FROM channels WHERE id = %s", (channel_id,))
            channel = cursor.fetchone()

    return templates.TemplateResponse(
        "songs/v1/form.html",
        {
            "request": request,
            "artists": artists,
            "channel": channel,
            "valid_status": VALID_STATUS,
        },
    )


# ===========================
# CREATE SONG
# ===========================
@router.post("/songs/new")
def create_song(
    artist_id: int = Form(...),
    title: str = Form(...),
    status: str = Form(...),
    release_date: Optional[str] = Form(None),
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    title, status, release_date = validate_song_data(title, status, release_date)

    cursor.execute("SELECT id FROM artists WHERE id = %s", (artist_id,))
    if not cursor.fetchone():
        raise HTTPException(404, "Artist tidak ditemukan")

    try:
        cursor.execute(
            """
            INSERT INTO songs (artist_id, title, status, release_date, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            """,
            (artist_id, title, status, release_date),
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Create song error: {e}")
        raise HTTPException(500, f"Gagal menyimpan lagu: {str(e)}")

    channel_id = get_artist_channel_id(cursor, artist_id)
    redirect_url = f"/songs?channel_id={channel_id}" if channel_id else "/songs"
    return RedirectResponse(redirect_url, status_code=HTTP_302_FOUND)


# ===========================
# EDIT SONG FORM
# ===========================
@router.get("/songs/{id}/edit", response_class=HTMLResponse)
def edit_song_form(id: int, request: Request, db=Depends(get_dict_cursor_dep)):
    cursor, _ = db

    cursor.execute(
        """
        SELECT 
            s.*, 
            a.id as artist_id,
            a.name as artist_name, 
            a.channel_id,
            c.name as channel_name
        FROM songs s
        JOIN artists a ON s.artist_id = a.id
        JOIN channels c ON a.channel_id = c.id
        WHERE s.id = %s
        """,
        (id,),
    )
    song = cursor.fetchone()

    if not song:
        raise HTTPException(404, "Lagu tidak ditemukan")

    cursor.execute(
        "SELECT id, name FROM artists WHERE channel_id = %s ORDER BY name",
        (song["channel_id"],),
    )
    artists = cursor.fetchall()

    return templates.TemplateResponse(
        "songs/v1/edit.html",
        {
            "request": request,
            "song": song,
            "artists": artists,
            "valid_status": VALID_STATUS,
        },
    )


# ===========================
# UPDATE SONG
# ===========================
@router.post("/songs/{id}/edit")
def edit_song_post(
    id: int,
    title: str = Form(...),
    artist_id: int = Form(...),
    status: str = Form(...),
    release_date: Optional[str] = Form(None),
    channel_id: Optional[int] = Form(None),
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    title, status, release_date = validate_song_data(title, status, release_date)

    # Verify song exists and get channel_id
    cursor.execute(
        """
        SELECT s.id, a.channel_id
        FROM songs s
        JOIN artists a ON s.artist_id = a.id
        WHERE s.id = %s
        """,
        (id,),
    )
    song = cursor.fetchone()

    if not song:
        raise HTTPException(404, "Lagu tidak ditemukan")

    # Verify artist belongs to same channel
    cursor.execute(
        "SELECT id FROM artists WHERE id = %s AND channel_id = %s",
        (artist_id, song["channel_id"]),
    )
    if not cursor.fetchone():
        raise HTTPException(400, "Artis tidak valid untuk channel ini")

    try:
        cursor.execute(
            """
            UPDATE songs
            SET title = %s, 
                artist_id = %s,
                status = %s, 
                release_date = %s
            WHERE id = %s
            """,
            (title, artist_id, status, release_date, id),
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Update song error: {e}")
        raise HTTPException(500, f"Gagal mengupdate lagu: {str(e)}")

    redirect_channel_id = channel_id or song["channel_id"]
    return RedirectResponse(f"/songs?channel_id={redirect_channel_id}", status_code=302)


# ===========================
# DELETE SONG
# ===========================
@router.post("/songs/{id}/delete")
def delete_song(
    id: int, 
    channel_id: Optional[int] = Form(None), 
    db=Depends(get_dict_cursor_dep)
):
    cursor, conn = db

    try:
        if not channel_id:
            cursor.execute(
                """
                SELECT a.channel_id 
                FROM songs s
                JOIN artists a ON s.artist_id = a.id
                WHERE s.id = %s
                """,
                (id,),
            )
            result = cursor.fetchone()
            channel_id = result["channel_id"] if result else None

        cursor.execute("DELETE FROM songs WHERE id=%s", (id,))
        if cursor.rowcount == 0:
            raise HTTPException(404, "Lagu tidak ditemukan")
        conn.commit()
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        print(f"Delete song error: {e}")
        raise HTTPException(500, f"Gagal menghapus lagu: {str(e)}")

    if channel_id:
        return RedirectResponse(
            f"/songs?channel_id={channel_id}", status_code=HTTP_302_FOUND
        )
    return RedirectResponse("/songs", status_code=HTTP_302_FOUND)


# ===========================
# SONGS IMPORT PAGE
# ===========================
@router.get("/songs/import", response_class=HTMLResponse)
async def show_import_form(
    request: Request,
    channel_id: Optional[int] = Query(None),
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    cursor.execute(
        "SELECT id, name, youtube_url FROM channels ORDER BY name ASC"
    )
    channels = cursor.fetchall()

    channel = None
    if channel_id:
        cursor.execute(
            "SELECT id, name, youtube_url FROM channels WHERE id = %s",
            (channel_id,),
        )
        channel = cursor.fetchone()
        if not channel:
            raise HTTPException(status_code=404, detail="Channel tidak ditemukan")

    return templates.TemplateResponse(
        "songs/v1/import.html",
        {
            "request": request,
            "channels": channels,
            "channel": channel,
        },
    )


# ===========================
# IMPORT SONGS FROM TEXT
# ===========================
@router.post("/songs/import")
async def import_songs(
    request: Request,
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    try:
        form = await request.form()

        channel_id = form.get("channel_id")
        new_channel = form.get("new_channel") or form.get("channel_name")
        data = form.get("data", "")
        uploaded_file = form.get("file")

        # Handle file upload
        if uploaded_file and uploaded_file.filename:
            raw = await uploaded_file.read()
            try:
                data = raw.decode("utf-8")
            except UnicodeDecodeError:
                data = raw.decode("latin-1")

        if not data.strip():
            raise HTTPException(status_code=400, detail="Data songs kosong")

        # Handle "__new__" special value
        if channel_id == "__new__":
            channel_id = None

        # Get or create channel
        channel = get_or_create_channel(
            cursor=cursor,
            channel_id=int(channel_id) if channel_id else None,
            new_channel=new_channel,
        )

        # Parse lines
        lines = [line.strip() for line in data.splitlines() if line.strip()]
        if not lines:
            raise HTTPException(status_code=400, detail="Tidak ada data valid")

        # Process each line
        imported = 0
        skipped = 0
        errors = []

        for index, line in enumerate(lines, start=1):
            try:
                parts = [
                    p.strip().replace("\u200b", "")
                    for p in re.split(r"\t+", line)
                ]

                if len(parts) < 2:
                    raise ValueError("Minimal Title + Artist")

                title = parts[0]
                artist_name = parts[1]
                status = parts[2] if len(parts) >= 3 and parts[2] else "Review"

                # Validation
                if not title:
                    raise ValueError("Title kosong")
                if not artist_name:
                    raise ValueError("Artist kosong")
                if len(title) > 255:
                    raise ValueError("Title terlalu panjang")
                if status not in VALID_STATUS:
                    raise ValueError(f"Status '{status}' tidak valid")

                # Get or create artist
                cursor.execute(
                    """
                    SELECT id FROM artists
                    WHERE channel_id = %s AND LOWER(name) = LOWER(%s)
                    """,
                    (channel["id"], artist_name),
                )
                artist = cursor.fetchone()

                if artist:
                    artist_id = artist["id"]
                else:
                    cursor.execute(
                        """
                        INSERT INTO artists (channel_id, name)
                        VALUES (%s, %s)
                        RETURNING id
                        """,
                        (channel["id"], artist_name),
                    )
                    artist_id = cursor.fetchone()["id"]

                # Check for duplicate song
                cursor.execute(
                    """
                    SELECT id FROM songs
                    WHERE artist_id = %s AND LOWER(title) = LOWER(%s)
                    """,
                    (artist_id, title),
                )
                if cursor.fetchone():
                    skipped += 1
                    errors.append(f"Baris {index}: '{title}' sudah ada")
                    continue

                # Insert song
                cursor.execute(
                    """
                    INSERT INTO songs (artist_id, title, status, created_at)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                    """,
                    (artist_id, title, status),
                )
                imported += 1

            except Exception as e:
                skipped += 1
                errors.append(f"Baris {index}: {str(e)}")

        conn.commit()

        return JSONResponse({
            "success": True,
            "channel": channel,
            "total": len(lines),
            "imported": imported,
            "skipped": skipped,
            "error_count": len(errors),
            "errors": errors[:50],
            "message": f"Import selesai. {imported} berhasil, {skipped} skipped",
        })

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal import songs: {str(e)}")


# ===========================
# EXPORT TXT
# ===========================
@router.post("/songs/export-txt")
def export_txt(song_ids: list[int] = Form(...)):
    if not song_ids:
        raise HTTPException(400, "Tidak ada lagu dipilih")

    with get_dict_cursor() as (cursor, _):
        placeholders = ",".join(["%s"] * len(song_ids))
        cursor.execute(
            f"""
            SELECT songs.title, artists.name AS artist
            FROM songs
            JOIN artists ON songs.artist_id = artists.id
            WHERE songs.id IN ({placeholders})
            """,
            tuple(song_ids),
        )
        songs = cursor.fetchall()

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


@router.get("/songs/export/day/{day}")
def export_txt_auto(
    day: int,
    target: int = Query(140),
    duplicate: int = Query(2),
    mode: ExportMode = Query("normal"),
):
    return has_day_export(day=day, target=target, duplicate=duplicate, mode=mode)


@router.get("/songs/v1/export/day/{day}/remaining")
def remaining(
    day: int,
    mode: ExportMode = Query("normal"),
):
    """Informasi export"""
    return get_export_information(day=day, mode=mode)


@router.get("/songs/usage/{day}", response_class=HTMLResponse)
def song_usage_day(
    request: Request,
    day: int,
    mode: ExportMode = Query("normal"),
    channel_id: int | None = Query(None),
):
    rows = get_day_usage(day=day, mode=mode, channel_id=channel_id)
    stats = get_day_usage_stats(day=day, mode=mode, channel_id=channel_id)

    return templates.TemplateResponse(
        "songs/v1/usage.html",
        {
            "request": request,
            "rows": rows,
            "day": day,
            "mode": mode,
            "stats": stats,
            "channel_id": channel_id,
            "total_usage": len(rows),
        },
    )


# ===========================
# DELETE USAGE (ROLLBACK)
# ===========================
@router.post("/songs/usage/{usage_id}/delete")
def delete_usage(usage_id: int, day: int = Form(...), db=Depends(get_dict_cursor_dep)):
    cursor, conn = db

    cursor.execute("SELECT id FROM song_usage WHERE id = %s", (usage_id,))
    if not cursor.fetchone():
        raise HTTPException(404, "Data rekap tidak ditemukan")

    try:
        cursor.execute("DELETE FROM song_usage WHERE id = %s", (usage_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Gagal menghapus: {str(e)}")

    return RedirectResponse(url=f"/songs/usage/{day}", status_code=303)


# ===========================
# BULK DELETE USAGE
# ===========================
@router.post("/songs/v1/usage/bulk-delete")
def bulk_delete_usage(
    request: Request,
    day: int = Form(...),
    usage_ids: List[int] = Form(...),
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    if not usage_ids:
        raise HTTPException(400, "Tidak ada data yang dipilih")

    try:
        placeholders = ",".join(["%s"] * len(usage_ids))
        cursor.execute(
            f"DELETE FROM song_usage WHERE id IN ({placeholders})", 
            usage_ids
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Gagal menghapus: {str(e)}")

    return RedirectResponse(url=f"/songs/v1/usage/{day}", status_code=303)


# ===========================
# BULK UPDATE STATUS
# ===========================
@router.post("/songs/v1/bulk-update")
async def bulk_update(request: Request, db=Depends(get_dict_cursor_dep)):
    try:
        body = await request.json()
        ids = body.get("ids", [])
        status = body.get("status")
        channel_id = body.get("channel_id")

        if not ids:
            raise HTTPException(400, "Tidak ada lagu yang dipilih")
        if status not in VALID_STATUS:
            raise HTTPException(
                400, f"Status tidak valid. Pilih: {', '.join(VALID_STATUS)}"
            )

        cursor, conn = db

        query = f"""
            UPDATE songs 
            SET status = %s
            WHERE id IN ({','.join(['%s'] * len(ids))})
        """
        params = [status] + ids

        if channel_id:
            query += " AND artist_id IN (SELECT id FROM artists WHERE channel_id = %s)"
            params.append(channel_id)

        cursor.execute(query, params)
        updated_count = cursor.rowcount
        conn.commit()

        return {
            "success": True,
            "message": f"Berhasil mengupdate {updated_count} lagu",
            "updated_count": updated_count,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Bulk update error: {str(e)}")
        raise HTTPException(500, f"Gagal mengupdate: {str(e)}")


# ===========================
# REKAP SELECTED SONGS
# ===========================
@router.get("/songs/v1/usage/selected", response_class=HTMLResponse)
def song_usage_selected(
    request: Request,
    song_ids: list[int] = Query(...),
    mode: ExportMode = Query("normal"),
    channel_id: int | None = Query(None),
    db=Depends(get_dict_cursor_dep),
):
    """Rekap lagu yang dipilih"""
    if not song_ids:
        raise HTTPException(status_code=400, detail="Tidak ada lagu yang dipilih.")

    cursor, _ = db

    placeholders = ",".join(["%s"] * len(song_ids))
    query = f"""
        SELECT
            s.id AS song_id,
            s.title,
            s.status,
            s.release_date,
            s.created_at,
            a.id AS artist_id,
            a.name AS artist,
            c.id AS channel_id,
            c.name AS channel
        FROM songs s
        JOIN artists a ON s.artist_id = a.id
        JOIN channels c ON a.channel_id = c.id
        WHERE s.id IN ({placeholders})
    """
    params = list(song_ids)

    if channel_id is not None:
        query += " AND c.id = %s"
        params.append(channel_id)

    query += " ORDER BY c.name, a.name, s.title"
    cursor.execute(query, params)
    rows = cursor.fetchall()

    return templates.TemplateResponse(
        "songs/v1/usage_selected.html",
        {
            "request": request,
            "songs": rows,
            "total_songs": len(rows),
            "mode": mode,
            "channel_id": channel_id,
        },
    )


# ===========================
# USAGE STATISTICS API
# ===========================
@router.get("/songs/v1/usage/stats")
def usage_stats(
    day: Optional[int] = Query(None),
    channel_id: Optional[int] = Query(None),
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    query = """
        SELECT 
            COUNT(DISTINCT u.id) as total_usage,
            COUNT(DISTINCT u.day) as total_days,
            COUNT(DISTINCT s.id) as unique_songs,
            COUNT(DISTINCT c.id) as unique_channels,
            COUNT(DISTINCT a.id) as unique_artists,
            COUNT(CASE WHEN s.status = 'Live' THEN 1 END) as live_songs
        FROM song_usage u
        JOIN songs s ON u.song_id = s.id
        JOIN artists a ON s.artist_id = a.id
        JOIN channels c ON a.channel_id = c.id
        WHERE 1=1
    """
    params = []

    if day:
        query += " AND u.day = %s"
        params.append(day)
    if channel_id:
        query += " AND c.id = %s"
        params.append(channel_id)

    cursor.execute(query, params)
    stats = cursor.fetchone()

    daily_trend = []
    if not day:
        cursor.execute("""
            SELECT day, COUNT(*) as usage_count
            FROM song_usage
            GROUP BY day
            ORDER BY day DESC
            LIMIT 10
        """)
        daily_trend = cursor.fetchall()

    return JSONResponse({"success": True, "data": stats, "daily_trend": daily_trend})


@router.get("/songs/v1/youtube-generator", response_class=HTMLResponse)
def youtube_generator_page(request: Request):
    return templates.TemplateResponse("songs/v1/v1/generate.html", {"request": request})


# ===========================
# LIST EXPORT BATCHES
# ===========================
@router.get("/songs/v1/export/batches", response_class=HTMLResponse)
def list_export_batches(
    request: Request,
    page: int = Query(1, ge=1),
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    per_page = 20
    offset = (page - 1) * per_page

    cursor.execute("SELECT COUNT(*) AS total FROM song_export_batches")
    total = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT
            b.id,
            b.day,
            b.duplicate_count,
            b.target_count,
            b.max_song_per_channel,
            b.excluded_channels,
            b.created_at,
            COUNT(i.id) AS total_songs
        FROM song_export_batches b
        LEFT JOIN song_export_batch_items i ON b.id = i.batch_id
        GROUP BY b.id
        ORDER BY b.id DESC
        LIMIT %s OFFSET %s
        """,
        (per_page, offset),
    )
    batches = cursor.fetchall()

    total_pages = (total + per_page - 1) // per_page if total > 0 else 1

    return templates.TemplateResponse(
        "songs/v1/export_batches.html",
        {
            "request": request,
            "batches": batches,
            "page": page,
            "total_pages": total_pages,
            "total": total,
        },
    )


# ===========================
# BATCH DETAIL
# ===========================
@router.get("/songs/v1/export/batches/{batch_id}", response_class=HTMLResponse)
def export_batch_detail(
    batch_id: int,
    request: Request,
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    cursor.execute("SELECT * FROM song_export_batches WHERE id = %s", (batch_id,))
    batch = cursor.fetchone()

    if not batch:
        raise HTTPException(404, "Batch tidak ditemukan")

    cursor.execute(
        """
        SELECT
            i.id,
            i.order_index,
            s.id AS song_id,
            s.title,
            s.status,
            a.id AS artist_id,
            a.name AS artist,
            c.id AS channel_id,
            c.name AS channel
        FROM song_export_batch_items i
        JOIN songs s ON i.song_id = s.id
        JOIN artists a ON s.artist_id = a.id
        JOIN channels c ON a.channel_id = c.id
        WHERE i.batch_id = %s
        ORDER BY i.order_index ASC
        """,
        (batch_id,),
    )
    songs = cursor.fetchall()

    return templates.TemplateResponse(
        "songs/v1/export_batch_detail.html",
        {
            "request": request,
            "batch": batch,
            "songs": songs,
            "total_songs": len(songs),
        },
    )


# ===========================
# DELETE EXPORT BATCH
# ===========================
@router.post("/songs/v1/export/batches/{batch_id}/delete")
def delete_export_batch(
    batch_id: int,
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    cursor.execute("SELECT id FROM song_export_batches WHERE id = %s", (batch_id,))
    if not cursor.fetchone():
        raise HTTPException(404, "Batch tidak ditemukan")

    try:
        cursor.execute("DELETE FROM song_export_batches WHERE id = %s", (batch_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Gagal menghapus batch: {str(e)}")

    return RedirectResponse(url="/songs/v1/export/batches", status_code=HTTP_302_FOUND)


# ===========================
# CLEAR SONG USAGE
# ===========================
@router.post("/songs/v1/usage/clear")
def clear_song_usage(
    confirm: str = Form(...),
    db=Depends(get_dict_cursor_dep),
):
    """RESET TOTAL HISTORI PEMAKAIAN SONG"""
    cursor, conn = db

    if confirm.strip().upper() != "RESET":
        raise HTTPException(400, "Ketik RESET untuk konfirmasi")

    try:
        cursor.execute("DELETE FROM song_usage")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Gagal reset usage: {str(e)}")

    return RedirectResponse(url="/songs/v1/export/batches", status_code=HTTP_302_FOUND)


# ===========================
# CLEAR EXPORT BATCHES
# ===========================
@router.post("/songs/v1/export/batches/clear")
def clear_export_batches(
    confirm: str = Form(...),
    db=Depends(get_dict_cursor_dep),
):
    """RESET SEMUA EXPORT BATCH"""
    cursor, conn = db

    if confirm.strip().upper() != "RESET":
        raise HTTPException(400, "Ketik RESET untuk konfirmasi")

    try:
        cursor.execute("DELETE FROM song_export_batches")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Gagal reset batch: {str(e)}")

    return RedirectResponse(url="/songs/v1/export/batches", status_code=HTTP_302_FOUND)


# ===========================
# EXPORT PREVIEW
# ===========================
@router.post("/songs/v1/export/preview")
def export_preview(
    payload: ExportPreviewPayload,
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    excluded_channels = payload.excluded_channels or []

    # Handle exclusion modes
    if payload.exclude_mode == "blacklist":
        cursor.execute("SELECT channel_id FROM channel_blacklists")
        excluded_channels = [r["channel_id"] for r in cursor.fetchall()]
    elif payload.exclude_mode == "none":
        excluded_channels = []

    # Get total live songs
    cursor.execute("SELECT COUNT(*) AS total FROM songs WHERE status = 'Live'")
    total_live_songs = cursor.fetchone()["total"]

    # Main query - get unused live songs
    query = """
        SELECT
            s.id,
            s.title,
            a.name AS artist,
            c.id AS channel_id,
            c.name AS channel
        FROM songs s
        JOIN artists a ON s.artist_id = a.id
        JOIN channels c ON a.channel_id = c.id
        LEFT JOIN song_usage u ON s.id = u.song_id
        WHERE s.status = 'Live'
        AND u.song_id IS NULL
    """
    params = []

    if excluded_channels:
        placeholders = ",".join(["%s"] * len(excluded_channels))
        query += f" AND c.id NOT IN ({placeholders})"
        params.extend(excluded_channels)

    query += " ORDER BY RANDOM()"
    cursor.execute(query, params)
    rows = cursor.fetchall()

    # Apply channel limit filter
    channel_counter = {}
    selected = []

    for row in rows:
        cid = row["channel_id"]
        count = channel_counter.get(cid, 0)

        if count >= payload.max_song_per_channel:
            continue

        selected.append(row)
        channel_counter[cid] = count + 1

        if len(selected) >= payload.target_count:
            break

    # Calculate metrics
    available_songs = len(rows)
    selected_songs = len(selected)
    estimated_rows = selected_songs * payload.duplicate_count
    unique_channels_used = len(channel_counter)
    excluded_count = len(excluded_channels)

    diversity_score = round(
        (unique_channels_used / selected_songs) * 100 if selected_songs else 0
    )
    pool_health = round(
        (available_songs / total_live_songs) * 100 if total_live_songs else 0
    )
    estimated_days_left = (
        available_songs // payload.target_count if payload.target_count > 0 else 0
    )

    # Generate warnings
    warnings = []
    if selected_songs < payload.target_count:
        warnings.append(
            f"Only {selected_songs} songs available from requested {payload.target_count}"
        )
    if pool_health < 20:
        warnings.append("Song pool is running low (<20%)")
    if diversity_score < 30 and selected_songs > 10:
        warnings.append("Low channel diversity detected")

    # Preview
    preview = [
        {
            "title": s["title"],
            "artist": s["artist"],
            "channel": s["channel"],
        }
        for s in selected[:10]
    ]

    return {
        "available_songs": available_songs,
        "selected_songs": selected_songs,
        "estimated_rows": estimated_rows,
        "excluded_channels": excluded_count,
        "unique_channels_used": unique_channels_used,
        "diversity_score": diversity_score,
        "pool_health": pool_health,
        "estimated_days_left": estimated_days_left,
        "warnings": warnings,
        "preview": preview,
    }