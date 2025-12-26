from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.templates import templates
from db.connect import get_dict_cursor

router = APIRouter()

@router.get("/vip_users", response_class=HTMLResponse)
async def list_vip_users(request: Request):
    with get_dict_cursor() as (cursor, _):
        cursor.execute("""
            SELECT id, user_id, username, paket, start_date, end_date, status, source_bot, updated_at
            FROM vip_users
            ORDER BY end_date DESC
        """)
        vip_users = cursor.fetchall()

    return templates.TemplateResponse("vip_users/list.html", {
        "request": request,
        "title": "Daftar VIP Users",
        "users": vip_users,
    })
