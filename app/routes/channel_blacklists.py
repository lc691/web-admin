from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse

from fastapi import Request
from starlette.templating import _TemplateResponse

from app.templates import templates
from app.core.database import get_dict_cursor
from app.core.database import get_dict_cursor_dep

router = APIRouter()


# =========================================================
# LIST
# =========================================================

@router.get(
    "/channel-blacklists",
    response_class=HTMLResponse,
)
def list_blacklists(
    request: Request,
):

    with get_dict_cursor() as (cursor, _):

        cursor.execute(
            """
            SELECT
                b.id,
                b.created_at,
                c.id AS channel_id,
                c.name AS channel_name
            FROM channel_blacklists b
            JOIN channels c ON b.channel_id = c.id
            ORDER BY c.name
            """
        )

        rows = cursor.fetchall()

        cursor.execute(
            """
            SELECT id, name
            FROM channels
            WHERE id NOT IN (
                SELECT channel_id
                FROM channel_blacklists
            )
            ORDER BY name
            """
        )

        channels = cursor.fetchall()

    return templates.TemplateResponse(
        "channel_blacklists/list.html",
        {
            "request": request,
            "rows": rows,
            "channels": channels,
        },
    )


# =========================================================
# CREATE
# =========================================================

@router.post("/channel-blacklists")
def create_blacklist(
    request: Request,  # Tambahkan request
    channel_id: int = Form(...),
    db=Depends(get_dict_cursor_dep),
):

    cursor, conn = db

    cursor.execute(
        "SELECT id FROM channels WHERE id = %s",
        (channel_id,),
    )

    if not cursor.fetchone():
        raise HTTPException(404, "Channel tidak ditemukan")

    try:

        cursor.execute(
            """
            INSERT INTO channel_blacklists (
                channel_id
            )
            VALUES (%s)
            ON CONFLICT (channel_id)
            DO NOTHING
            """,
            (channel_id,),
        )

        conn.commit()

    except Exception as e:

        conn.rollback()

        raise HTTPException(
            500,
            f"Gagal menambah blacklist: {str(e)}",
        )

    # Tambahkan flash message
    request.session["flash"] = {
        "message": f"Channel berhasil diblacklist",
        "type": "success"
    }

    return RedirectResponse(
        "/channel-blacklists",
        status_code=303,
    )


# =========================================================
# DELETE
# =========================================================

@router.post(
    "/channel-blacklists/{id}/delete"
)
def delete_blacklist(
    request: Request,
    id: int,
    db=Depends(get_dict_cursor_dep),
):

    cursor, conn = db

    try:

        cursor.execute(
            "DELETE FROM channel_blacklists WHERE id = %s",
            (id,),
        )

        conn.commit()

    except Exception as e:

        conn.rollback()

        raise HTTPException(
            500,
            f"Gagal menghapus blacklist: {str(e)}",
        )

    request.session["flash"] = {
        "message": f"Channel berhasil diunblock",
        "type": "success"
    }

    return RedirectResponse(
        "/channel-blacklists",
        status_code=303,
    )