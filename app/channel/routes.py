from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.templates import templates

from .crud import get_all_channels, set_active_channel, update_channel

router = APIRouter(prefix="/channel", tags=["channel"])


# --------------------------
# List semua channel
# --------------------------
@router.get("/", response_class=HTMLResponse)
def list_channels(request: Request, q: Optional[str] = None):
    channels = get_all_channels()
    if q:
        filtered_channels = [
            c
            for c in channels
            if q.lower() in (c["nama_variabel"] or "").lower()
            or q.lower() in (c["alias"] or "").lower()
        ]
    else:
        filtered_channels = channels
    return templates.TemplateResponse(
        "channel/list.html", {"request": request, "channels": filtered_channels, "q": q or ""}
    )


# --------------------------
# Set channel aktif
# --------------------------
@router.post("/set_active")
def set_active_handler(id: int = Form(...)):
    try:
        set_active_channel(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal set active channel: {e}")
    return RedirectResponse(url="/channel/", status_code=303)


# --------------------------
# Edit channel form
# --------------------------
@router.get("/edit/{channel_id}", response_class=HTMLResponse)
def edit_channel_form(request: Request, channel_id: int):
    channels = get_all_channels()
    channel = next((c for c in channels if c["id"] == channel_id), None)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel tidak ditemukan")
    return templates.TemplateResponse("channel/edit.html", {"request": request, "channel": channel})


# --------------------------
# Update channel
# --------------------------
@router.post("/edit/{channel_id}")
def update_channel_handler(
    channel_id: int,
    alias: str = Form(...),
    keterangan: str = Form(...),
):
    try:
        update_channel(channel_id, alias, keterangan)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal update channel: {e}")
    return RedirectResponse(url="/channel/", status_code=303)
