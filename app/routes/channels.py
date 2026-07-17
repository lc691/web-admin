from fastapi import APIRouter, Depends, Form, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.status import HTTP_302_FOUND
from typing import Optional, List
import re

from app.templates import templates
from app.core.database import get_dict_cursor, get_dict_cursor_dep

router = APIRouter()

# =====================================================
# CONSTANTS
# =====================================================

VALID_STATUS = ["Review", "Approved", "Live", "Take Down", "Topic"]


# =====================================================
# HELPER FUNCTIONS
# =====================================================


def safe_commit(conn):
    """Commit database safely with rollback on error"""
    try:
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def validate_channel_name(name: str) -> str:
    """Validate channel name"""
    name = name.strip()

    if not name:
        raise HTTPException(status_code=400, detail="Nama channel wajib diisi")

    if len(name) > 255:
        raise HTTPException(
            status_code=400, detail="Nama channel maksimal 255 karakter"
        )

    return name


def validate_youtube_url(url: Optional[str]) -> Optional[str]:
    """Validate YouTube URL"""

    if not url:
        return None

    url = url.strip()

    if not url:
        return None

    youtube_patterns = [
        r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/",
        r"(https?://)?(www\.)?(m\.youtube\.com)/",
    ]

    for pattern in youtube_patterns:
        if re.match(pattern, url):
            return url

    raise HTTPException(status_code=400, detail="URL YouTube tidak valid")


# =====================================================
# LIST CHANNELS
# =====================================================


@router.get("/channels", response_class=HTMLResponse, name="list_channels")
def list_channels(
    request: Request,
    search: Optional[str] = Query(default=None, description="Search channels by name"),
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    query = """
        SELECT
            c.id,
            c.name,
            c.youtube_url,
            c.created_at,

            COUNT(DISTINCT a.id) AS total_artists,
            COUNT(s.id) AS total_songs,

            COUNT(
                CASE
                    WHEN s.status = 'Live' THEN 1
                END
            ) AS live_songs,

            COUNT(
                CASE
                    WHEN s.status = 'Approved' THEN 1
                END
            ) AS approved_songs,

            COUNT(
                CASE
                    WHEN s.status = 'Review' THEN 1
                END
            ) AS review_songs,

            COUNT(
                CASE
                    WHEN s.status = 'Take Down' THEN 1
                END
            ) AS takedown_songs,

            COUNT(
                CASE
                    WHEN s.status = 'Topic' THEN 1
                END
            ) AS topic_songs

        FROM channels c
        LEFT JOIN artists a
            ON a.channel_id = c.id
        LEFT JOIN songs s
            ON s.artist_id = a.id
    """

    params = []

    if search:
        query += " WHERE c.name ILIKE %s"
        params.append(f"%{search}%")

    query += """
        GROUP BY
            c.id,
            c.name,
            c.youtube_url,
            c.created_at

        ORDER BY c.created_at DESC
    """

    cursor.execute(query, params)
    channels = cursor.fetchall()

    total_artists = sum(ch.get("total_artists", 0) or 0 for ch in channels)

    total_songs = sum(ch.get("total_songs", 0) or 0 for ch in channels)

    total_live_songs = sum(ch.get("live_songs", 0) or 0 for ch in channels)

    return templates.TemplateResponse(
        "channels/list.html",
        {
            "request": request,
            "channels": channels,
            "search": search,
            "total_channels": len(channels),
            "total_artists": total_artists,
            "total_songs": total_songs,
            "total_live_songs": total_live_songs,
        },
    )


# =====================================================
# FORM CREATE CHANNEL
# =====================================================


@router.get("/channels/new", response_class=HTMLResponse)
def new_channel_form(request: Request):
    return templates.TemplateResponse(
        "channels/form.html",
        {
            "request": request,
            "channel": None,
        },
    )


# =====================================================
# CREATE CHANNEL
# =====================================================


@router.post("/channels/new")
def create_channel(
    name: str = Form(...),
    youtube_url: Optional[str] = Form(None),
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    try:
        name = validate_channel_name(name)
        youtube_url = validate_youtube_url(youtube_url)

        # duplicate check
        cursor.execute(
            """
            SELECT id
            FROM channels
            WHERE LOWER(name) = LOWER(%s)
            """,
            (name,),
        )

        if cursor.fetchone():
            raise HTTPException(
                status_code=400, detail="Channel dengan nama ini sudah ada"
            )

        # insert
        cursor.execute(
            """
            INSERT INTO channels (
                name,
                youtube_url,
                created_at
            )
            VALUES (
                %s,
                %s,
                CURRENT_TIMESTAMP
            )
            RETURNING id
            """,
            (name, youtube_url),
        )

        new_channel_id = cursor.fetchone()["id"]

        safe_commit(conn)

    except HTTPException:
        raise

    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500, detail=f"Gagal menyimpan channel: {str(e)}"
        )

    return RedirectResponse(
        url=f"/channels/{new_channel_id}", status_code=HTTP_302_FOUND
    )

# =====================================================
# GET OR CREATE CHANNEL
# =====================================================

def get_or_create_channel(
    cursor,
    channel_id=None,
    new_channel: str = None,
):
    """
    Return existing channel id
    or create new channel automatically.
    """

    # =========================================
    # EXISTING CHANNEL
    # =========================================
    if channel_id:

        try:
            channel_id = int(channel_id)
        except (TypeError, ValueError):
            raise HTTPException(400, "Channel tidak valid")

        cursor.execute(
            """
            SELECT id, name
            FROM channels
            WHERE id = %s
            """,
            (channel_id,),
        )

        channel = cursor.fetchone()

        if not channel:
            raise HTTPException(404, "Channel tidak ditemukan")

        return channel

    # =========================================
    # CREATE NEW CHANNEL
    # =========================================
    if new_channel:

        new_channel = new_channel.strip()

        if not new_channel:
            raise HTTPException(400, "Nama channel baru kosong")

        if len(new_channel) > 255:
            raise HTTPException(
                400,
                "Nama channel maksimal 255 karakter",
            )

        # cek existing
        cursor.execute(
            """
            SELECT id, name
            FROM channels
            WHERE LOWER(name) = LOWER(%s)
            """,
            (new_channel,),
        )

        existing = cursor.fetchone()

        if existing:
            return existing

        # create new
        cursor.execute(
            """
            INSERT INTO channels (
                name,
                created_at
            )
            VALUES (
                %s,
                CURRENT_TIMESTAMP
            )
            RETURNING id, name
            """,
            (new_channel,),
        )

        return cursor.fetchone()

    raise HTTPException(
        400,
        "Channel wajib dipilih atau dibuat baru",
    )

# =====================================================
# FORM EDIT CHANNEL
# =====================================================


@router.get("/channels/{channel_id}/edit", response_class=HTMLResponse)
def edit_channel_form(
    channel_id: int,
    request: Request,
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    cursor.execute(
        """
        SELECT
            id,
            name,
            youtube_url
        FROM channels
        WHERE id = %s
        """,
        (channel_id,),
    )

    channel = cursor.fetchone()

    if not channel:
        raise HTTPException(status_code=404, detail="Channel tidak ditemukan")

    return templates.TemplateResponse(
        "channels/form.html",
        {
            "request": request,
            "channel": channel,
        },
    )


# =====================================================
# UPDATE CHANNEL
# =====================================================


@router.post("/channels/{channel_id}/edit")
def update_channel(
    channel_id: int,
    name: str = Form(...),
    youtube_url: Optional[str] = Form(None),
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    try:
        name = validate_channel_name(name)
        youtube_url = validate_youtube_url(youtube_url)

        cursor.execute("SELECT id FROM channels WHERE id = %s", (channel_id,))

        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Channel tidak ditemukan")

        cursor.execute(
            """
            SELECT id
            FROM channels
            WHERE LOWER(name) = LOWER(%s)
            AND id != %s
            """,
            (name, channel_id),
        )

        if cursor.fetchone():
            raise HTTPException(
                status_code=400, detail="Channel dengan nama ini sudah ada"
            )

        cursor.execute(
            """
            UPDATE channels
            SET
                name = %s,
                youtube_url = %s
            WHERE id = %s
            """,
            (name, youtube_url, channel_id),
        )

        safe_commit(conn)

    except HTTPException:
        raise

    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500, detail=f"Gagal mengupdate channel: {str(e)}"
        )

    return RedirectResponse(url=f"/channels/{channel_id}", status_code=HTTP_302_FOUND)


# =====================================================
# CHANNEL DETAIL
# =====================================================
@router.get("/channels/{channel_id}", response_class=HTMLResponse)
def channel_detail(channel_id: int, request: Request):

    with get_dict_cursor() as (cursor, _):

        # ===== Channel =====
        cursor.execute(
            "SELECT * FROM channels WHERE id=%s",
            (channel_id,),
        )
        channel = cursor.fetchone()

        if not channel:
            raise HTTPException(404, "Channel tidak ditemukan")

        # ===== Artists + Song Count =====
        cursor.execute(
            """
            SELECT
                a.id,
                a.name,
                COUNT(s.id) AS song_count
            FROM artists a
            LEFT JOIN songs s
                ON s.artist_id = a.id
            WHERE a.channel_id = %s
            GROUP BY a.id, a.name
            ORDER BY a.name
            """,
            (channel_id,),
        )
        artists = cursor.fetchall()

        # ===== Songs =====
        cursor.execute(
            """
            SELECT
                s.id,
                s.title,
                s.status,
                s.release_date,
                s.created_at,
                a.name AS artist_name
            FROM songs s
            JOIN artists a ON s.artist_id = a.id
            WHERE a.channel_id=%s
            ORDER BY s.created_at DESC
            LIMIT 200
            """,
            (channel_id,),
        )
        songs = cursor.fetchall()

    return templates.TemplateResponse(
        "channels/details.html",
        {
            "request": request,
            "channel": channel,
            "artists": artists,
            "songs": songs,
        },
    )


# =====================================================
# DELETE CHANNEL
# =====================================================
@router.post("/channels/{channel_id}/delete")
def delete_channel(
    channel_id: int,
    request: Request,
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    try:
        cursor.execute(
            """
            SELECT id
            FROM channels
            WHERE id = %s
            """,
            (channel_id,),
        )

        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Channel tidak ditemukan")

        # delete songs
        cursor.execute(
            """
            DELETE FROM songs
            WHERE artist_id IN (
                SELECT id
                FROM artists
                WHERE channel_id = %s
            )
            """,
            (channel_id,),
        )

        # delete artists
        cursor.execute(
            """
            DELETE FROM artists
            WHERE channel_id = %s
            """,
            (channel_id,),
        )

        # delete channel
        cursor.execute(
            """
            DELETE FROM channels
            WHERE id = %s
            """,
            (channel_id,),
        )

        safe_commit(conn)

    except HTTPException:
        raise

    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500, detail=f"Gagal menghapus channel: {str(e)}"
        )

    return RedirectResponse(
        url=request.url_for("list_channels"), status_code=HTTP_302_FOUND
    )


# =====================================================
# BULK DELETE CHANNELS
# =====================================================
@router.post("/channels/bulk-delete")
def bulk_delete_channels(
    request: Request,
    channel_ids: List[int] = Form(...),
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    if not channel_ids:
        raise HTTPException(status_code=400, detail="Tidak ada channel yang dipilih")

    try:
        cursor.execute(
            """
            DELETE FROM songs
            WHERE artist_id IN (
                SELECT id
                FROM artists
                WHERE channel_id = ANY(%s)
            )
            """,
            (channel_ids,),
        )

        cursor.execute(
            """
            DELETE FROM artists
            WHERE channel_id = ANY(%s)
            """,
            (channel_ids,),
        )

        cursor.execute(
            """
            DELETE FROM channels
            WHERE id = ANY(%s)
            """,
            (channel_ids,),
        )

        safe_commit(conn)

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal bulk delete: {str(e)}")

    return RedirectResponse(
        url=request.url_for("list_channels"), status_code=HTTP_302_FOUND
    )


# =====================================================
# API SEARCH CHANNELS
# =====================================================
@router.get("/channels/api/search")
def search_channels_api(
    q: str = Query(..., min_length=1),
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    cursor.execute(
        """
        SELECT
            id,
            name,
            youtube_url
        FROM channels
        WHERE name ILIKE %s
        ORDER BY name
        LIMIT 10
        """,
        (f"%{q}%",),
    )

    channels = cursor.fetchall()

    return JSONResponse({"success": True, "data": channels, "total": len(channels)})


# =====================================================
# API STATS
# =====================================================
@router.get("/channels/api/stats")
def channel_stats_api(
    db=Depends(get_dict_cursor_dep),
):
    cursor, _ = db

    cursor.execute("""
        SELECT
            COUNT(*) AS total_channels,
            COUNT(DISTINCT a.id) AS total_artists,
            COUNT(s.id) AS total_songs,

            COUNT(
                CASE
                    WHEN s.status = 'Live' THEN 1
                END
            ) AS live_songs,

            COUNT(
                CASE
                    WHEN s.status = 'Approved' THEN 1
                END
            ) AS approved_songs

        FROM channels c
        LEFT JOIN artists a
            ON a.channel_id = c.id
        LEFT JOIN songs s
            ON s.artist_id = a.id
        """)

    stats = cursor.fetchone()

    return JSONResponse({"success": True, "data": stats})
