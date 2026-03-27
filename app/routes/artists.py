from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND

from app.templates import templates
from db.connect import get_dict_cursor, get_dict_cursor_dep

router = APIRouter()


# ---------------------------
# List Artists
# ---------------------------
@router.get("/artists", response_class=HTMLResponse)
async def list_artists(request: Request):

    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            """
            SELECT artists.*, channels.name AS channel_name
            FROM artists
            JOIN channels ON artists.channel_id = channels.id
            ORDER BY artists.created_at DESC
        """
        )
        artists = cursor.fetchall()

    return templates.TemplateResponse(
        "artists/list.html",
        {"request": request, "artists": artists},
    )


# ---------------------------
# Form Create Artist
# ---------------------------
@router.get("/artists/new", response_class=HTMLResponse)
def new_artist_form(request: Request):

    with get_dict_cursor() as (cursor, _):
        cursor.execute("SELECT * FROM channels ORDER BY name")
        channels = cursor.fetchall()

    return templates.TemplateResponse(
        "artists/form.html",
        {"request": request, "channels": channels},
    )


# ---------------------------
# Create Artist
# ---------------------------
@router.post("/artists/new")
def create_artist(
    channel_id: int = Form(...),
    name: str = Form(...),
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    cursor.execute(
        """
        INSERT INTO artists (channel_id, name)
        VALUES (%s, %s)
        """,
        (channel_id, name),
    )

    conn.commit()

    return RedirectResponse("/artists", status_code=HTTP_302_FOUND)


# ---------------------------
# Delete Artist
# ---------------------------
@router.post("/artists/{id}/delete")
def delete_artist(id: int, db=Depends(get_dict_cursor_dep)):
    cursor, conn = db

    cursor.execute("DELETE FROM artists WHERE id=%s", (id,))
    conn.commit()

    return RedirectResponse("/artists", status_code=HTTP_302_FOUND)
