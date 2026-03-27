from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.templates import templates

from .repository import ChannelAdminRepository

router = APIRouter(prefix="/channel", tags=["channel"])
repo = ChannelAdminRepository()


# ==========================================================
# LIST + SEARCH + PAGINATION
# ==========================================================
@router.get("/", response_class=HTMLResponse)
def list_channels(
    request: Request,
    q: str | None = Query(None),
    is_active: bool | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    channels = repo.search(keyword=q, is_active=is_active)

    total = len(channels)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = channels[start:end]

    return templates.TemplateResponse(
        "channel/list.html",
        {
            "request": request,
            "channels": paginated,
            "q": q or "",
            "is_active": is_active,
            "page": page,
            "per_page": per_page,
            "total": total,
        },
    )


# ==========================================================
# CREATE FORM
# ==========================================================
@router.get("/create", response_class=HTMLResponse)
def create_channel_form(request: Request):
    return templates.TemplateResponse(
        "channel/create.html",
        {"request": request},
    )


# ==========================================================
# CREATE HANDLER
# ==========================================================
@router.post("/create")
def create_channel_handler(
    nama_variabel: str = Form(...),
    nilai: int = Form(...),
    alias: str = Form(""),
    keterangan: str = Form(""),
    is_active: bool | None = Form(False),
):
    try:
        repo.create(
            nama_variabel=nama_variabel.strip(),
            nilai=nilai,
            alias=alias.strip() or None,
            keterangan=keterangan.strip() or None,
            is_active=is_active,
            created_by=None,  # bisa diisi user session nanti
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat channel: {e}")

    return RedirectResponse(url="/channel/", status_code=303)


# ==========================================================
# EDIT FORM
# ==========================================================
@router.get("/edit/{channel_id}", response_class=HTMLResponse)
def edit_channel_form(request: Request, channel_id: int):
    channel = repo.get_by_id(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel tidak ditemukan")

    return templates.TemplateResponse(
        "channel/edit.html",
        {"request": request, "channel": channel},
    )


# ==========================================================
# UPDATE HANDLER
# ==========================================================
@router.post("/edit/{channel_id}")
def update_channel_handler(
    channel_id: int,
    nama_variabel: str = Form(...),
    nilai: int = Form(...),
    alias: str = Form(""),
    keterangan: str = Form(""),
    is_active: bool | None = Form(False),
):
    channel = repo.get_by_id(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel tidak ditemukan")

    try:
        affected = repo.update(
            channel_id,
            {
                "nama_variabel": nama_variabel.strip(),
                "nilai": nilai,
                "alias": alias.strip() or None,
                "keterangan": keterangan.strip() or None,
                "is_active": is_active,
            },
        )

        if affected == 0:
            raise HTTPException(status_code=400, detail="Tidak ada perubahan data")

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal update channel: {e}")

    return RedirectResponse(url="/channel/", status_code=303)


# ==========================================================
# SET ACTIVE (Dedicated Endpoint)
# ==========================================================
@router.post("/set_active")
def set_active_handler(channel_id: int = Form(...)):
    try:
        repo.set_active(channel_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal set active: {e}")

    return RedirectResponse(url="/channel/", status_code=303)


# ==========================================================
# DELETE
# ==========================================================
@router.post("/delete/{channel_id}")
def delete_channel(channel_id: int):
    channel = repo.get_by_id(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel tidak ditemukan")

    repo.delete(channel_id)
    return RedirectResponse(url="/channel/", status_code=303)
