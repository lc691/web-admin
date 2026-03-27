from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND

from app.templates import templates
from db.connect import get_dict_cursor, get_dict_cursor_dep

router = APIRouter()


# ===========================
# Helper
# ===========================
def safe_commit(conn):
    try:
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Database error: {e}")


# ===========================
# List Channels
# ===========================
@router.get("/channels", response_class=HTMLResponse, name="list_channels")
def list_channels(request: Request):
    with get_dict_cursor() as (cursor, _):

        cursor.execute(
            """
            SELECT 
                c.id,
                c.name,
                c.youtube_url,
                c.created_at,
                COUNT(DISTINCT a.id) AS total_artists,
                COUNT(s.id) AS total_songs
            FROM channels c
            LEFT JOIN artists a ON a.channel_id = c.id
            LEFT JOIN songs s ON s.artist_id = a.id
            GROUP BY c.id
            ORDER BY c.created_at DESC
        """
        )

        channels = cursor.fetchall()

    return templates.TemplateResponse(
        "channels/list.html",
        {"request": request, "channels": channels},
    )


# ===========================
# Channel Detail
# ===========================
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

        # ===== Artists =====
        cursor.execute(
            """
            SELECT id, name
            FROM artists
            WHERE channel_id=%s
            ORDER BY name
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


# ===========================
# Form Create Channel
# ===========================
@router.get("/channels/new", response_class=HTMLResponse)
def new_channel_form(request: Request):
    return templates.TemplateResponse(
        "channels/form.html",
        {"request": request},
    )


# ===========================
# Create Channel
# ===========================
@router.post("/channels/new")
def create_channel(
    request: Request,
    name: str = Form(...),
    youtube_url: str = Form(None),
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    name = name.strip()
    if not name:
        raise HTTPException(400, "Nama channel wajib diisi")

    youtube_url = youtube_url.strip() if youtube_url else None

    try:
        # ===== Anti duplicate =====
        cursor.execute(
            "SELECT id FROM channels WHERE LOWER(name)=LOWER(%s)",
            (name,),
        )
        if cursor.fetchone():
            raise HTTPException(400, "Channel sudah ada")

        cursor.execute(
            """
            INSERT INTO channels (name, youtube_url)
            VALUES (%s, %s)
            """,
            (name, youtube_url),
        )

        safe_commit(conn)

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Gagal menyimpan channel: {e}")

    return RedirectResponse(
        request.url_for("list_channels"), status_code=HTTP_302_FOUND
    )


# ===========================
# Delete Channel
# ===========================
@router.post("/channels/{id}/delete")
def delete_channel(
    id: int,
    request: Request,
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    try:
        cursor.execute("SELECT id FROM channels WHERE id=%s", (id,))
        if not cursor.fetchone():
            raise HTTPException(404, "Channel tidak ditemukan")

        # ===== Delete cascade manual =====
        cursor.execute(
            """
            DELETE FROM songs
            WHERE artist_id IN (
                SELECT id FROM artists WHERE channel_id=%s
            )
        """,
            (id,),
        )

        cursor.execute("DELETE FROM artists WHERE channel_id=%s", (id,))

        cursor.execute("DELETE FROM channels WHERE id=%s", (id,))

        safe_commit(conn)

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Gagal hapus channel: {e}")

    return RedirectResponse(
        request.url_for("list_channels"), status_code=HTTP_302_FOUND
    )
