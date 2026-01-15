from datetime import datetime

from fastapi import APIRouter, Form, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse, RedirectResponse

from app.templates import templates

from .crud import delete_vip_log, get_all_vip_logs, get_log_by_id, update_vip_log

router = APIRouter()


# =====================================================
# LIST VIP LOGS
# =====================================================
@router.get("/vip_logs", response_class=HTMLResponse)
async def list_vip_logs(request: Request):
    logs = await run_in_threadpool(get_all_vip_logs)

    return templates.TemplateResponse(
        "vip_logs/list.html",
        {
            "request": request,
            "logs": logs,
            "title": "Log Aktivasi VIP",
        },
    )


# =====================================================
# EDIT FORM
# =====================================================
@router.get("/vip_logs/{log_id}/edit", response_class=HTMLResponse)
async def edit_vip_log_form(request: Request, log_id: int):
    log = await run_in_threadpool(get_log_by_id, log_id)

    if not log:
        return RedirectResponse("/vip_logs", status_code=302)

    return templates.TemplateResponse(
        "vip_logs/edit.html",
        {
            "request": request,
            "log": log,
            "title": "Edit VIP Log",
        },
    )


# =====================================================
# EDIT SUBMIT
# =====================================================
@router.post("/vip_logs/{log_id}/edit")
async def edit_vip_log_submit(
    log_id: int,
    target_user_id: int = Form(...),
    paket: str = Form(...),
    durasi_hari: int = Form(...),
    expired_baru: str = Form(...),
    keterangan: str | None = Form(None),
):
    expired_dt = datetime.fromisoformat(expired_baru)

    await run_in_threadpool(
        update_vip_log,
        log_id,
        {
            "target_user_id": target_user_id,
            "paket": paket,
            "durasi_hari": durasi_hari,
            "expired_baru": expired_dt,
            "keterangan": keterangan,
        },
    )

    return RedirectResponse("/vip_logs", status_code=303)


# =====================================================
# DELETE
# =====================================================
@router.post("/vip_logs/{log_id}/delete")
async def delete_vip_log_handler(log_id: int):
    await run_in_threadpool(delete_vip_log, log_id)
    return RedirectResponse("/vip_logs", status_code=303)
