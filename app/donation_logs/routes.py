from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.templates import templates
from db.connect import get_dict_cursor

router = APIRouter()


@router.get("/donation_logs", response_class=HTMLResponse)
async def list_donation_logs(request: Request):
    with get_dict_cursor() as (cursor, _):
        cursor.execute("""
            SELECT
                id,
                email,
                amount,
                message,
                user_id,
                paket,
                timestamp,
                type,
                is_notified,
                source_bot,
                status,
                confirmed_at
            FROM donation_log
            ORDER BY timestamp DESC
        """)
        logs = cursor.fetchall()

    return templates.TemplateResponse(
        "donation_logs/list.html",
        {"request": request, "logs": logs, "title": "Donation Logs"},
    )


@router.get("/donation_logs/{log_id}/edit", response_class=HTMLResponse)
async def edit_donation_log_form(request: Request, log_id: int):
    with get_dict_cursor() as (cursor, _):
        cursor.execute("SELECT * FROM donation_log WHERE id = %s", (log_id,))
        log = cursor.fetchone()

    if not log:
        return RedirectResponse("/donation_logs", status_code=302)

    return templates.TemplateResponse(
        "donation_logs/edit.html",
        {"request": request, "log": log, "title": "Edit Donation Log"},
    )


@router.post("/donation_logs/{log_id}/edit")
async def edit_donation_log_submit(
    log_id: int,
    email: str = Form(None),
    amount: int = Form(None),
    message: str = Form(None),
    user_id: int = Form(None),
    paket: str = Form(None),
    type: str = Form(None),
    status: str = Form(None),
    is_notified: bool = Form(False),
):
    with get_dict_cursor() as (cursor, conn):
        cursor.execute(
            """
            UPDATE donation_log
            SET email = %s,
                amount = %s,
                message = %s,
                user_id = %s,
                paket = %s,
                type = %s,
                status = %s,
                is_notified = %s
            WHERE id = %s
        """,
            (email, amount, message, user_id, paket, type, status, is_notified, log_id),
        )
        conn.commit()

    return RedirectResponse("/donation_logs", status_code=303)


@router.post("/donation_logs/{log_id}/delete")
async def delete_donation_log(log_id: int):
    with get_dict_cursor() as (cursor, conn):
        cursor.execute("DELETE FROM donation_log WHERE id = %s", (log_id,))
        conn.commit()

    return RedirectResponse("/donation_logs", status_code=303)
