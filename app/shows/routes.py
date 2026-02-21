from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.templates import templates
from db.connect import get_dict_cursor

from .file_import import import_show_files
from .service import (
    bulk_update_shows,
    create_show,
    delete_show,
    get_show,
    list_shows,
    update_show,
)
from .validators import is_valid_url

router = APIRouter()


async def resolve_thumbnail_for_web(thumbnail_url: str | None):
    # web TIDAK download, hanya pass-through
    return thumbnail_url


# ==========================================================
# LIST SHOWS
# ==========================================================
@router.get("/shows", response_class=HTMLResponse)
async def show_list(request: Request):
    shows = list_shows()
    return templates.TemplateResponse(
        "shows/list.html",
        {"request": request, "shows": shows},
    )


# ==========================================================
# ADD SHOW FORM
# ==========================================================
@router.get("/shows/add", response_class=HTMLResponse)
async def add_show_form(request: Request):

    # ambil semua source untuk dropdown
    with get_dict_cursor() as (cur, _):
        cur.execute("SELECT id, label FROM request_sources ORDER BY label ASC")
        sources = cur.fetchall()

    return templates.TemplateResponse(
        "shows/add.html",
        {
            "request": request,
            "show": None,
            "sources": sources,
        },
    )


# ==========================================================
# CREATE SHOW
# ==========================================================
@router.post("/shows/add")
async def create_show_post(
    title: str = Form(...),
    sinopsis: str = Form(""),
    genre: str = Form(""),
    source_id: int = Form(...),
    hashtags: str = Form(""),
    thumbnail_url: str = Form(""),
    is_adult: int | None = Form(None),
):
    title = title.strip()
    if not title:
        raise HTTPException(400, "Judul wajib diisi")

    data = {
        "title": title,
        "sinopsis": sinopsis.strip(),
        "genre": genre.strip(),
        "source_id": source_id,
        "hashtags": hashtags.strip(),
        "is_adult": bool(is_adult),
    }

    if thumbnail_url.strip():
        if not is_valid_url(thumbnail_url.strip()):
            raise HTTPException(400, "Thumbnail URL tidak valid")
        data["thumbnail_url"] = thumbnail_url.strip()
    else:
        data["thumbnail_url"] = None

    create_show(data)

    return RedirectResponse("/shows", status_code=303)


# ==========================================================
# EDIT SHOW FORM
# ==========================================================
@router.get("/shows/edit/{show_id}", response_class=HTMLResponse)
async def edit_show_form(request: Request, show_id: int):

    show = get_show(show_id)
    if not show:
        raise HTTPException(status_code=404)

    # 🔥 Tambahkan ini kembali
    shows = list_shows()

    with get_dict_cursor() as (cur, _):
        cur.execute("SELECT id, label FROM request_sources ORDER BY label ASC")
        sources = cur.fetchall()

    s = dict(show)
    s["resolved_thumbnail"] = await resolve_thumbnail_for_web(s.get("thumbnail_url"))

    return templates.TemplateResponse(
        "shows/edit.html",
        {
            "request": request,
            "show": s,
            "shows": shows,  # 🔥 WAJIB ADA
            "sources": sources,
        },
    )


# ==========================================================
# UPDATE SHOW
# ==========================================================
@router.post("/shows/edit/{show_id}")
async def update_show_post(
    show_id: int,
    title: str = Form(""),
    sinopsis: str = Form(""),
    genre: str = Form(""),
    source_id: int = Form(...),
    hashtags: str = Form(""),
    thumbnail_url: str = Form(""),
    is_adult: int = Form(0),
):
    data = {}

    if title.strip():
        data["title"] = title.strip()

    data["sinopsis"] = sinopsis.strip()
    data["genre"] = genre.strip()
    data["source_id"] = source_id
    data["hashtags"] = hashtags.strip()

    if thumbnail_url.strip() == "":
        data["thumbnail_url"] = None
    else:
        if not is_valid_url(thumbnail_url.strip()):
            raise HTTPException(400, "Thumbnail URL tidak valid")
        data["thumbnail_url"] = thumbnail_url.strip()

    data["is_adult"] = bool(int(is_adult))

    update_show(show_id, data)

    return RedirectResponse("/shows", status_code=303)


# ==========================================================
# BULK EDIT FORM
# ==========================================================
@router.get("/shows/bulk-edit", response_class=HTMLResponse)
def bulk_edit_form(request: Request, ids: str):
    if not ids:
        raise HTTPException(status_code=400, detail="IDs kosong")

    with get_dict_cursor() as (cur, _):
        cur.execute("SELECT id, label FROM request_sources ORDER BY label ASC")
        sources = cur.fetchall()

    return templates.TemplateResponse(
        "shows/bulk_edit.html",
        {
            "request": request,
            "ids": ids,
            "sources": sources,
        },
    )


# ==========================================================
# BULK EDIT SUBMIT
# ==========================================================
@router.post("/shows/bulk-edit")
async def bulk_edit_shows(
    ids: str = Form(...),
    apply_title: str | None = Form(None),
    title: str | None = Form(None),
    apply_sinopsis: str | None = Form(None),
    sinopsis: str | None = Form(None),
    apply_genre: str | None = Form(None),
    genre: str | None = Form(None),
    apply_source_id: str | None = Form(None),
    source_id: int | None = Form(None),
    apply_hashtags: str | None = Form(None),
    hashtags: str | None = Form(None),
    apply_thumbnail_url: str | None = Form(None),
    thumbnail_url: str | None = Form(None),
    apply_is_adult: str | None = Form(None),
    is_adult: int | None = Form(None),
):
    # -----------------------------
    # Parse & validate IDs
    # -----------------------------
    raw_ids = [i.strip() for i in ids.split(",")]
    id_list = []

    for raw in raw_ids:
        if not raw:
            continue
        if not raw.isdigit():
            raise HTTPException(400, f"ID tidak valid: {raw}")
        id_list.append(int(raw))

    if not id_list:
        raise HTTPException(400, "IDs tidak valid")

    # -----------------------------
    # Build update data
    # -----------------------------
    data: dict = {}

    if apply_title:
        clean = (title or "").strip()
        if not clean:
            raise HTTPException(400, "Judul wajib diisi")
        data["title"] = clean

    if apply_sinopsis:
        data["sinopsis"] = (sinopsis or "").strip() or None

    if apply_genre:
        if not genre:
            raise HTTPException(400, "Genre wajib dipilih")
        data["genre"] = genre

    if apply_source_id:
        if source_id is None:
            raise HTTPException(400, "Source wajib dipilih")
        data["source_id"] = source_id

    if apply_hashtags:
        data["hashtags"] = (hashtags or "").strip() or None

    if apply_thumbnail_url:
        clean_thumb = (thumbnail_url or "").strip()
        if clean_thumb and not is_valid_url(clean_thumb):
            raise HTTPException(400, "Thumbnail URL tidak valid")
        data["thumbnail_url"] = clean_thumb or None

    if apply_is_adult:
        if is_adult not in (0, 1):
            raise HTTPException(400, "Nilai konten dewasa tidak valid")
        data["is_adult"] = bool(is_adult)

    if not data:
        return RedirectResponse("/shows", status_code=303)

    # -----------------------------
    # Call service
    # -----------------------------
    try:
        bulk_update_shows(id_list, data)
    except ValueError as e:
        raise HTTPException(400, str(e))

    return RedirectResponse("/shows", status_code=303)


# ==========================================================
# IMPORT FILES
# ==========================================================
@router.post("/shows/{show_id}/import-files")
async def import_files_post(
    request: Request,
    show_id: int,
    source_show_id: int = Form(...),
    message_id: int = Form(...),
):
    if show_id == source_show_id:
        raise HTTPException(
            status_code=400,
            detail="Source dan target show tidak boleh sama",
        )

    inserted = import_show_files(
        source_show_id=source_show_id,
        target_show_id=show_id,
        message_id=message_id,
    )

    return RedirectResponse(
        url=f"/shows/edit/{show_id}?imported={inserted}",
        status_code=303,
    )


# ==========================================================
# DELETE SHOW
# ==========================================================
@router.get("/shows/delete/{show_id}")
async def delete_show_post(show_id: int):
    delete_show(show_id)
    return RedirectResponse("/shows", status_code=303)
