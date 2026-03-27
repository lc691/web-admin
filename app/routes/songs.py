from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from starlette.status import HTTP_302_FOUND

from app.templates import templates
from db.connect import get_dict_cursor, get_dict_cursor_dep

router = APIRouter()

VALID_STATUS = {"Review", "Approved", "Live"}


# ===========================
# LIST SONGS
# ===========================
@router.get("/songs", response_class=HTMLResponse)
def list_songs(request: Request):

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
        SELECT 
            s.id, s.title, s.status, s.release_date, s.created_at,
            a.name AS artist_name,
            c.name AS channel_name
        FROM songs s
        JOIN artists a ON s.artist_id = a.id
        JOIN channels c ON a.channel_id = c.id
        ORDER BY s.created_at DESC
        LIMIT 200
        """
        )

        songs = cursor.fetchall()

    return templates.TemplateResponse(
        "songs/list.html",
        {"request": request, "songs": songs},
    )


# ===========================
# FORM CREATE SONG
# ===========================
@router.get("/songs/new", response_class=HTMLResponse)
def new_song_form(request: Request):

    with get_dict_cursor() as (cursor, _):
        cursor.execute("SELECT id, name FROM artists ORDER BY name")
        artists = cursor.fetchall()

    return templates.TemplateResponse(
        "songs/form.html",
        {"request": request, "artists": artists},
    )


# ===========================
# CREATE SONG
# ===========================
@router.post("/songs/new")
def create_song(
    artist_id: int = Form(...),
    title: str = Form(...),
    status: str = Form(...),
    release_date: str = Form(None),
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    title = title.strip()
    if not title:
        raise HTTPException(400, "Judul wajib diisi")

    if status not in VALID_STATUS:
        raise HTTPException(400, "Status tidak valid")

    try:
        cursor.execute(
            """
            INSERT INTO songs (artist_id, title, status, release_date)
            VALUES (%s, %s, %s, %s)
            """,
            (artist_id, title, status, release_date or None),
        )
        conn.commit()

    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"DB Error: {e}")

    return RedirectResponse("/songs", status_code=HTTP_302_FOUND)


# ===========================
# DELETE SONG
# ===========================
@router.post("/songs/{id}/delete")
def delete_song(id: int, db=Depends(get_dict_cursor_dep)):
    cursor, conn = db

    try:
        cursor.execute("DELETE FROM songs WHERE id=%s", (id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Gagal hapus: {e}")

    return RedirectResponse("/songs", status_code=HTTP_302_FOUND)


# ===========================
# EXPORT TXT
# ===========================
@router.post("/songs/export-txt")
def export_txt(song_ids: list[int] = Form(...)):

    if not song_ids:
        raise HTTPException(400, "Tidak ada lagu dipilih")

    with get_dict_cursor() as (cursor, _):

        placeholders = ",".join(["%s"] * len(song_ids))

        query = f"""
        SELECT songs.title, artists.name AS artist
        FROM songs
        JOIN artists ON songs.artist_id = artists.id
        WHERE songs.id IN ({placeholders})
        ORDER BY songs.id
        """

        cursor.execute(query, tuple(song_ids))
        songs = cursor.fetchall()

    lines = []

    for i, song in enumerate(songs, start=1):

        title = song["title"].strip().lower()
        artist = song["artist"].strip().lower()

        query = f"{title} {artist}".replace(" ", "+")
        yt_url = f"https://www.youtube.com/results?search_query={query}"

        lines.append(f"{i}. 🇺🇲 Judul: {title} {artist}\n{yt_url}")

    text = "\n\n".join(lines)
    filename = datetime.now().strftime("%d-%m-%Y") + ".txt"

    return Response(
        content=text,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ===========================
# IMPORT FORM
# ===========================
@router.get("/songs/import", response_class=HTMLResponse)
def import_form(request: Request):
    return templates.TemplateResponse("songs/import.html", {"request": request})


# ===========================
# IMPORT SONGS (ANTI DUPLIKAT)
# ===========================
@router.post("/songs/import")
def import_songs(
    channel_name: str = Form(...),
    data: str = Form(...),
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    STATUS_MAP = {
        "review": "Review",
        "approved": "Approved",
        "live": "Live",
    }

    try:
        # ===== CHANNEL =====
        cursor.execute("SELECT id FROM channels WHERE name=%s", (channel_name,))
        row = cursor.fetchone()

        if row:
            channel_id = row["id"]
        else:
            cursor.execute(
                "INSERT INTO channels (name) VALUES (%s) RETURNING id",
                (channel_name,),
            )
            channel_id = cursor.fetchone()["id"]

        lines = data.strip().splitlines()

        inserted = 0
        skipped = 0

        for line in lines:

            if not line.strip():
                continue

            parts = line.split("\t")

            if len(parts) < 2:
                skipped += 1
                continue

            title = parts[0].strip()
            artist_name = parts[1].strip()

            if not title or not artist_name:
                skipped += 1
                continue

            status = "Review"
            if len(parts) >= 3:
                status = STATUS_MAP.get(parts[2].lower(), "Review")

            # ===== ARTIST =====
            cursor.execute(
                "SELECT id FROM artists WHERE name=%s AND channel_id=%s",
                (artist_name, channel_id),
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
                    (channel_id, artist_name),
                )
                artist_id = cursor.fetchone()["id"]

            # ===== ANTI DUPLIKAT =====
            cursor.execute(
                """
                SELECT id FROM songs
                WHERE artist_id=%s AND LOWER(title)=LOWER(%s)
                """,
                (artist_id, title),
            )

            if cursor.fetchone():
                skipped += 1
                continue

            # ===== INSERT =====
            cursor.execute(
                """
                INSERT INTO songs (artist_id, title, status)
                VALUES (%s, %s, %s)
                """,
                (artist_id, title, status),
            )

            inserted += 1

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise HTTPException(500, f"Import gagal: {e}")

    return RedirectResponse(
        f"/songs?inserted={inserted}&skipped={skipped}",
        status_code=HTTP_302_FOUND,
    )
