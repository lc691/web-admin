from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND
from typing import List, Optional
import re

from app.templates import templates
from app.core.database import get_dict_cursor, get_dict_cursor_dep

router = APIRouter()


# ===========================
# HELPER FUNCTIONS
# ===========================
def validate_artist_data(name: str, channel_id: int):
    """Validasi data artist"""
    # Validate name
    name = name.strip()
    if not name:
        raise HTTPException(400, "Nama artist tidak boleh kosong")

    if len(name) < 2:
        raise HTTPException(400, "Nama artist minimal 2 karakter")

    if len(name) > 255:
        raise HTTPException(400, "Nama artist maksimal 255 karakter")

    # Check for invalid characters
    invalid_chars = re.search(r"[<>\'\"`]", name)
    if invalid_chars:
        raise HTTPException(400, "Nama artist mengandung karakter tidak valid")

    return name, channel_id


def format_artist_response(artist: dict) -> dict:
    """Format response artist untuk DataTables"""
    return {
        "id": artist["id"],
        "channel_name": artist.get("channel_name", "-"),
        "name": artist.get("name", "Unknown"),
        "song_count": artist.get("song_count", 0),
        "created_at": (
            artist["created_at"].strftime("%Y-%m-%d %H:%M")
            if artist.get("created_at") and hasattr(artist["created_at"], "strftime")
            else None
        ),
    }


# ===========================
# LIST ARTISTS (Main Page)
# ===========================
@router.get("/artists", response_class=HTMLResponse)
async def list_artists(request: Request):
    return templates.TemplateResponse(
        "artists/list.html",
        {"request": request},
    )


# ===========================
# DATATABLES SERVER-SIDE DATA
# ===========================
@router.get("/artists/data")
def artists_data(
    request: Request,
    draw: int = Query(...),
    start: int = Query(0, ge=0),
    length: int = Query(10, ge=1, le=100),
    search: str = Query("", alias="search[value]"),
    channel_id: Optional[int] = Query(None),
    order_column: int = Query(1, alias="order[0][column]"),
    order_dir: str = Query("desc", alias="order[0][dir]"),
    db=Depends(get_dict_cursor_dep),
):
    """
    Server-side DataTables endpoint untuk halaman Artists
    """
    cursor, _ = db

    # Base query
    base_query = """
        FROM artists a
        JOIN channels c ON a.channel_id = c.id
        LEFT JOIN songs s ON s.artist_id = a.id
        WHERE 1=1
    """
    params = []

    # Filter channel
    if channel_id:
        base_query += " AND a.channel_id = %s"
        params.append(channel_id)

    # Search filter
    if search:
        keyword = f"%{search}%"
        base_query += """
            AND (
                a.name ILIKE %s
                OR c.name ILIKE %s
            )
        """
        params.extend([keyword, keyword])

    # Total records (without filters)
    cursor.execute("SELECT COUNT(*) AS total FROM artists")
    total_records = cursor.fetchone()["total"]

    # Filtered records
    cursor.execute(f"SELECT COUNT(DISTINCT a.id) AS total {base_query}", params)
    filtered_records = cursor.fetchone()["total"]

    # Ordering
    order_columns = {
        0: "a.id",  # checkbox
        1: "a.id",  # ID
        2: "c.name",  # Channel
        3: "a.name",  # Artist Name
        4: "song_count",  # Total Songs
        5: "a.created_at",  # Created At
    }
    order_by = order_columns.get(order_column, "a.id")
    order_direction = "DESC" if str(order_dir).lower() == "desc" else "ASC"

    # Main data query
    data_query = f"""
        SELECT
            a.id,
            a.name,
            a.created_at,
            c.name AS channel_name,
            COUNT(DISTINCT s.id) AS song_count
        {base_query}
        GROUP BY a.id, a.name, a.created_at, c.name
        ORDER BY {order_by} {order_direction}
        LIMIT %s OFFSET %s
    """
    final_params = params + [length, start]
    cursor.execute(data_query, final_params)
    artists = cursor.fetchall()

    # Format response
    data = [format_artist_response(artist) for artist in artists]

    return {
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": data,
    }


# ===========================
# ARTIST STATISTICS
# ===========================
@router.get("/artists/stats")
def artist_stats(
    channel_id: Optional[int] = Query(None),
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    if channel_id:
        cursor.execute(
            """
            SELECT 
                COUNT(DISTINCT a.id) as total_artists,
                COUNT(DISTINCT s.id) as total_songs,
                COUNT(DISTINCT c.id) as active_channels
            FROM artists a
            JOIN channels c ON a.channel_id = c.id
            LEFT JOIN songs s ON s.artist_id = a.id
            WHERE a.channel_id = %s
            """,
            (channel_id,),
        )
    else:
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT a.id) as total_artists,
                COUNT(DISTINCT s.id) as total_songs,
                COUNT(DISTINCT c.id) as active_channels
            FROM artists a
            JOIN channels c ON a.channel_id = c.id
            LEFT JOIN songs s ON s.artist_id = a.id
            """)

    stats = cursor.fetchone()

    return JSONResponse(
        {
            "success": True,
            "data": {
                "total_artists": stats["total_artists"] or 0,
                "total_songs": stats["total_songs"] or 0,
                "active_channels": stats["active_channels"] or 0,
            },
        }
    )


# ===========================
# CHANNELS LIST FOR FILTER
# ===========================
@router.get("/channels/list")
def channels_list(
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    cursor.execute("SELECT id, name FROM channels ORDER BY name")
    channels = cursor.fetchall()

    return JSONResponse(
        {
            "success": True,
            "channels": [{"id": ch["id"], "name": ch["name"]} for ch in channels],
        }
    )


# ===========================
# FORM CREATE ARTIST
# ===========================
@router.get("/artists/new", response_class=HTMLResponse)
def new_artist_form(
    request: Request,
    success: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
):
    with get_dict_cursor() as (cursor, _):
        cursor.execute("SELECT id, name FROM channels ORDER BY name")
        channels = cursor.fetchall()

    return templates.TemplateResponse(
        "artists/form.html",
        {
            "request": request,
            "channels": channels,
            "success": success,
            "artist_name": name,
            "channel_name": channel,
        },
    )


# ===========================
# CREATE ARTIST
# ===========================
@router.post("/artists/new")
def create_artist(
    channel_id: int = Form(...),
    name: str = Form(...),
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    try:
        # Validate data
        name, channel_id = validate_artist_data(name, channel_id)

        # Check if artist already exists in this channel
        cursor.execute(
            """
            SELECT id FROM artists 
            WHERE LOWER(name) = LOWER(%s) AND channel_id = %s
            """,
            (name, channel_id),
        )

        existing = cursor.fetchone()
        if existing:
            raise HTTPException(400, f"Artist '{name}' sudah ada di channel ini")

        # Get channel name for redirect
        cursor.execute("SELECT name FROM channels WHERE id = %s", (channel_id,))
        channel = cursor.fetchone()
        channel_name = channel["name"] if channel else ""

        # Insert artist
        cursor.execute(
            """
            INSERT INTO artists (channel_id, name, created_at, updated_at)
            VALUES (%s, %s, NOW(), NOW())
            RETURNING id
            """,
            (channel_id, name),
        )

        conn.commit()
        artist_id = cursor.fetchone()["id"]

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        print(f"Create artist error: {e}")
        raise HTTPException(500, f"Gagal menyimpan artist: {str(e)}")

    # Redirect with success parameters
    return RedirectResponse(
        f"/artists/new?success=1&name={name}&channel={channel_name}",
        status_code=HTTP_302_FOUND,
    )


# ===========================
# EDIT ARTIST FORM
# ===========================
@router.get("/artists/{id}/edit", response_class=HTMLResponse)
def edit_artist_form(
    id: int,
    request: Request,
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    # Get artist data
    cursor.execute(
        """
        SELECT a.*, c.name as channel_name, c.id as channel_id
        FROM artists a
        JOIN channels c ON a.channel_id = c.id
        WHERE a.id = %s
        """,
        (id,),
    )
    artist = cursor.fetchone()

    if not artist:
        raise HTTPException(404, "Artist tidak ditemukan")

    # Get all channels
    cursor.execute("SELECT id, name FROM channels ORDER BY name")
    channels = cursor.fetchall()

    return templates.TemplateResponse(
        "artists/form.html",
        {
            "request": request,
            "artist": artist,
            "channels": channels,
        },
    )


# ===========================
# UPDATE ARTIST
# ===========================
@router.post("/artists/{id}/edit")
def update_artist(
    id: int,
    channel_id: int = Form(...),
    name: str = Form(...),
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    try:
        # Validate data
        name, channel_id = validate_artist_data(name, channel_id)

        # Check if artist exists
        cursor.execute("SELECT id FROM artists WHERE id = %s", (id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Artist tidak ditemukan")

        # Check for duplicate in same channel (excluding current artist)
        cursor.execute(
            """
            SELECT id FROM artists 
            WHERE LOWER(name) = LOWER(%s) 
            AND channel_id = %s 
            AND id != %s
            """,
            (name, channel_id, id),
        )
        if cursor.fetchone():
            raise HTTPException(400, f"Artist '{name}' sudah ada di channel ini")

        # Update artist
        cursor.execute(
            """
            UPDATE artists 
            SET channel_id = %s, name = %s, updated_at = NOW()
            WHERE id = %s
            """,
            (channel_id, name, id),
        )
        conn.commit()

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        print(f"Update artist error: {e}")
        raise HTTPException(500, f"Gagal mengupdate artist: {str(e)}")

    return RedirectResponse("/artists", status_code=HTTP_302_FOUND)


# ===========================
# DELETE ARTIST
# ===========================
@router.post("/artists/{id}/delete")
def delete_artist(
    id: int,
    channel_id: Optional[int] = Form(None),
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    try:
        # Check if artist has songs
        cursor.execute(
            "SELECT COUNT(*) as count FROM songs WHERE artist_id = %s", (id,)
        )
        result = cursor.fetchone()

        if result and result["count"] > 0:
            raise HTTPException(
                400,
                f"Tidak dapat menghapus artist karena masih memiliki {result['count']} lagu. Hapus lagu terlebih dahulu.",
            )

        cursor.execute("DELETE FROM artists WHERE id = %s", (id,))

        if cursor.rowcount == 0:
            raise HTTPException(404, "Artist tidak ditemukan")

        conn.commit()

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        print(f"Delete artist error: {e}")
        raise HTTPException(500, f"Gagal menghapus artist: {str(e)}")

    if channel_id:
        return RedirectResponse(
            f"/artists?channel_id={channel_id}", status_code=HTTP_302_FOUND
        )

    return RedirectResponse("/artists", status_code=HTTP_302_FOUND)


# ===========================
# BULK DELETE ARTISTS
# ===========================
@router.post("/artists/bulk-delete")
def bulk_delete_artists(
    request: Request,
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    try:
        body = request.json() if hasattr(request, "json") else {}
        if isinstance(body, dict):
            ids = body.get("ids", [])
        else:
            # Fallback for form data
            import json

            body = json.loads(body)
            ids = body.get("ids", [])

        if not ids:
            raise HTTPException(400, "Tidak ada artist yang dipilih")

        # Check if any artist has songs
        placeholders = ",".join(["%s"] * len(ids))
        cursor.execute(
            f"""
            SELECT a.id, a.name, COUNT(s.id) as song_count
            FROM artists a
            LEFT JOIN songs s ON s.artist_id = a.id
            WHERE a.id IN ({placeholders})
            GROUP BY a.id, a.name
            HAVING COUNT(s.id) > 0
            """,
            ids,
        )

        artists_with_songs = cursor.fetchall()
        if artists_with_songs:
            names = [a["name"] for a in artists_with_songs]
            raise HTTPException(
                400,
                f"Tidak dapat menghapus artist berikut karena masih memiliki lagu: {', '.join(names[:5])}",
            )

        # Delete artists
        cursor.execute(f"DELETE FROM artists WHERE id IN ({placeholders})", ids)
        deleted_count = cursor.rowcount
        conn.commit()

        return JSONResponse(
            {
                "success": True,
                "message": f"Berhasil menghapus {deleted_count} artist",
                "deleted_count": deleted_count,
            }
        )

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        print(f"Bulk delete error: {e}")
        raise HTTPException(500, f"Gagal menghapus artist: {str(e)}")


# ===========================
# ARTIST DETAIL (Optional)
# ===========================
@router.get("/artists/{id}", response_class=HTMLResponse)
def artist_detail(
    id: int,
    request: Request,
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    # Get artist details
    cursor.execute(
        """
        SELECT a.*, c.name as channel_name, c.id as channel_id
        FROM artists a
        JOIN channels c ON a.channel_id = c.id
        WHERE a.id = %s
        """,
        (id,),
    )
    artist = cursor.fetchone()

    if not artist:
        raise HTTPException(404, "Artist tidak ditemukan")

    # Get songs by this artist
    cursor.execute(
        """
        SELECT id, title, status, release_date, created_at
        FROM songs
        WHERE artist_id = %s
        ORDER BY created_at DESC
        """,
        (id,),
    )
    songs = cursor.fetchall()

    return templates.TemplateResponse(
        "artists/detail.html",
        {
            "request": request,
            "artist": artist,
            "songs": songs,
            "songs_count": len(songs),
        },
    )


# ===========================
# ARTIST SONGS DATA (for detail page)
# ===========================
@router.get("/artists/{id}/songs-data")
def artist_songs_data(
    id: int,
    draw: int = Query(...),
    start: int = Query(0, ge=0),
    length: int = Query(10, ge=1, le=100),
    search: str = Query("", alias="search[value]"),
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    # Check if artist exists
    cursor.execute("SELECT id FROM artists WHERE id = %s", (id,))
    if not cursor.fetchone():
        raise HTTPException(404, "Artist tidak ditemukan")

    # Base query
    base_query = "FROM songs WHERE artist_id = %s"
    params = [id]

    # Search filter
    if search:
        base_query += " AND title ILIKE %s"
        params.append(f"%{search}%")

    # Total records
    cursor.execute(f"SELECT COUNT(*) as total FROM songs WHERE artist_id = %s", (id,))
    total_records = cursor.fetchone()["total"]

    # Filtered records
    cursor.execute(f"SELECT COUNT(*) as total {base_query}", params)
    filtered_records = cursor.fetchone()["total"]

    # Get songs
    cursor.execute(
        f"""
        SELECT id, title, status, release_date, created_at
        {base_query}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """,
        params + [length, start],
    )
    songs = cursor.fetchall()

    return {
        "draw": draw,
        "recordsTotal": total_records,
        "recordsFiltered": filtered_records,
        "data": [
            {
                "id": s["id"],
                "title": s["title"],
                "status": s["status"],
                "release_date": (
                    s["release_date"].strftime("%Y-%m-%d") if s["release_date"] else "-"
                ),
                "created_at": (
                    s["created_at"].strftime("%Y-%m-%d %H:%M")
                    if s["created_at"]
                    else "-"
                ),
            }
            for s in songs
        ],
    }
