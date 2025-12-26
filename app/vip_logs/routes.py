from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.templates import templates
from .crud import (
    get_all_vip_logs,
    get_log_by_id,
    update_vip_log,
    delete_vip_log
)

router = APIRouter()

@router.get("/vip_logs", response_class=HTMLResponse)
async def list_vip_logs(request: Request):
    logs = get_all_vip_logs()
    return templates.TemplateResponse("vip_logs/list.html", {
        "request": request,
        "logs": logs,
        "title": "Log Aktivasi VIP"
    })

@router.get("/vip_logs/{log_id}/edit", response_class=HTMLResponse)
async def edit_vip_log_form(request: Request, log_id: int):
    log = get_log_by_id(log_id)
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
    update_vip_log(log_id, {
        "target_user_id": target_user_id,
        "paket": paket,
        "durasi_hari": durasi_hari,
        "expired_baru": expired_baru,
        "keterangan": keterangan
    })
    return RedirectResponse("/vip_logs", status_code=303)

@router.post("/vip_logs/{log_id}/delete")
async def delete_vip_log_handler(log_id: int):
    delete_vip_log(log_id)
    return RedirectResponse("/vip_logs", status_code=303)
