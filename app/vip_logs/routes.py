from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.templates import templates
from db.connect import get_dict_cursor

router = APIRouter()

@router.get("/vip_logs", response_class=HTMLResponse)
async def list_vip_logs(request: Request):
    with get_dict_cursor() as (cursor, _):
        cursor.execute("""
            SELECT
                l.id,
                l.target_user_id,
                u.username,
                l.admin_user_id,
                l.paket,
                l.durasi_hari,
                l.expired_baru,
                l.keterangan,
                l.timestamp,
                l.source
            FROM vip_logs l
            LEFT JOIN vip_users u ON l.target_user_id = u.user_id
            ORDER BY l.timestamp DESC
        """)
        logs = cursor.fetchall()

    return templates.TemplateResponse("vip_logs/list.html", {
        "request": request,
        "logs": logs,
        "title": "Log Aktivasi VIP"
    })

@router.get("/vip_logs/{log_id}/edit", response_class=HTMLResponse)
async def edit_vip_log_form(request: Request, log_id: int):
    with get_dict_cursor() as (cursor, _):
        cursor.execute("SELECT * FROM vip_logs WHERE id = %s", (log_id,))
        log = cursor.fetchone()
    if not log:
        return RedirectResponse("/vip_logs", status_code=302)
    return templates.TemplateResponse("vip_logs/edit.html", {
        "request": request,
        "log": log,
        "title": "Edit VIP Log"
    })

@router.post("/vip_logs/{log_id}/edit")
async def edit_vip_log_submit(
    log_id: int,
    target_user_id: int = Form(...),
    paket: str = Form(...),
    durasi_hari: int = Form(...),
    expired_baru: str = Form(...),
    keterangan: str = Form(None)
):
    with get_dict_cursor() as (cursor, conn):
        cursor.execute("""
            UPDATE vip_logs
            SET target_user_id = %s,
                paket = %s,
                durasi_hari = %s,
                expired_baru = %s,
                keterangan = %s
            WHERE id = %s
        """, (target_user_id, paket, durasi_hari, expired_baru, keterangan, log_id))
        conn.commit()
    return RedirectResponse("/vip_logs", status_code=303)

@router.post("/vip_logs/{log_id}/delete")
async def delete_vip_log(log_id: int):
    with get_dict_cursor() as (cursor, conn):
        cursor.execute("DELETE FROM vip_logs WHERE id = %s", (log_id,))
        conn.commit()

    return RedirectResponse("/vip_logs", status_code=303)