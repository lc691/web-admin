import logging
from fastapi import APIRouter, Form, HTTPException, Request, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse

from app.templates import templates
from app.core.database import get_dict_cursor

from .file_import import import_show_files
from .service import (
    bulk_update_shows,
    create_show,
    delete_show,
    get_show,
    list_shows,
    search_shows,
    update_show,
)
from .validators import is_valid_url

logger = logging.getLogger(__name__)
router = APIRouter()


# ==========================================================
# HELPERS
# ==========================================================

def validate_show_data(data: dict) -> bool:
    """Centralized validation for show data."""
    title = data.get("title", "").strip()
    if not title:
        raise HTTPException(400, "Judul wajib diisi")
    
    if len(title) < 3:
        raise HTTPException(400, "Judul minimal 3 karakter")
    
    if len(title) > 255:
        raise HTTPException(400, "Judul maksimal 255 karakter")
    
    if data.get("source_id") and not isinstance(data["source_id"], int):
        raise HTTPException(400, "Source ID tidak valid")
    
    return True


async def resolve_thumbnail_for_web(thumbnail_url: str | None):
    """Pass-through thumbnail URL for web."""
    return thumbnail_url


def get_sources() -> list[dict]:
    """Get all request sources for dropdown."""
    with get_dict_cursor() as (cur, _):
        cur.execute("SELECT id, label FROM request_sources ORDER BY label ASC")
        return cur.fetchall()


# ==========================================================
# LIST SHOWS (DENGAN PAGINATION)
# ==========================================================
@router.get("/shows", response_class=HTMLResponse)
async def show_list(
    request: Request,
    page: int = Query(1, ge=1, description="Halaman"),
    per_page: int = Query(20, ge=5, le=100, description="Jumlah per halaman"),
    search: str | None = Query(None, description="Cari berdasarkan judul/genre"),
):
    result = list_shows(
        page=page,
        per_page=per_page,
        search=search,
        include_stats=True,  # Set False untuk lebih cepat
    )
    
    return templates.TemplateResponse(
        "shows/list.html",
        {
            "request": request,
            "shows": result["data"],
            "total": result["total"],
            "page": result["page"],
            "per_page": result["per_page"],
            "total_pages": result["total_pages"],
            "search": search,
        },
    )


# ==========================================================
# SHOWS API (JSON)
# ==========================================================
@router.get("/shows/api")
async def shows_api(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=5, le=100),
    search: str | None = None,
):
    result = list_shows(page=page, per_page=per_page, search=search)
    return result

# ==========================================================
# ADD SHOW FORM
# ==========================================================
@router.get("/shows/add", response_class=HTMLResponse)
async def add_show_form(request: Request):
    return templates.TemplateResponse(
        "shows/add.html",
        {
            "request": request,
            "show": None,
            "sources": get_sources(),
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

    # Validate
    validate_show_data(data)

    logger.info(f"Creating show: {title}")
    create_show(data)
    logger.info(f"Show created successfully: {title}")

    return RedirectResponse("/shows", status_code=303)


# ==========================================================
# EDIT SHOW FORM
# ==========================================================
@router.get("/shows/edit/{show_id}", response_class=HTMLResponse)
async def edit_show_form(request: Request, show_id: int):
    show = get_show(show_id)
    if not show:
        raise HTTPException(status_code=404, detail="Show tidak ditemukan")

    shows = list_shows()
    sources = get_sources()

    s = dict(show)
    s["resolved_thumbnail"] = await resolve_thumbnail_for_web(s.get("thumbnail_url"))

    return templates.TemplateResponse(
        "shows/edit.html",
        {
            "request": request,
            "show": s,
            "shows": shows,
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

    # Validate
    if "title" in data:
        validate_show_data(data)

    logger.info(f"Updating show {show_id}")
    update_show(show_id, data)
    logger.info(f"Show {show_id} updated successfully")

    return RedirectResponse("/shows", status_code=303)


# ==========================================================
# BULK EDIT FORM
# ==========================================================
@router.get("/shows/bulk-edit", response_class=HTMLResponse)
def bulk_edit_form(request: Request, ids: str):
    if not ids:
        raise HTTPException(status_code=400, detail="IDs kosong")

    return templates.TemplateResponse(
        "shows/bulk_edit.html",
        {
            "request": request,
            "ids": ids,
            "sources": get_sources(),
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
        logger.info(f"Bulk updating {len(id_list)} shows")
        bulk_update_shows(id_list, data)
        logger.info(f"Bulk update completed")
    except ValueError as e:
        raise HTTPException(400, str(e))

    return RedirectResponse("/shows", status_code=303)


# ==========================================================
# BULK DELETE SHOWS
# ==========================================================
@router.post("/shows/bulk-delete")
async def bulk_delete_shows(
    ids: str = Form(...),
):
    """
    Bulk delete multiple shows.
    """
    if not ids:
        raise HTTPException(status_code=400, detail="IDs tidak boleh kosong")

    # Parse IDs
    id_list = [int(i.strip()) for i in ids.split(",") if i.strip().isdigit()]
    if not id_list:
        raise HTTPException(status_code=400, detail="IDs tidak valid")

    # Hapus satu per satu
    deleted = 0
    errors = []

    for show_id in id_list:
        try:
            delete_show(show_id)
            deleted += 1
        except ValueError as e:
            errors.append(f"ID {show_id}: {str(e)}")
        except Exception as e:
            errors.append(f"ID {show_id}: {str(e)}")

    if errors and not deleted:
        raise HTTPException(
            status_code=400, 
            detail=f"Gagal menghapus semua show: {', '.join(errors[:3])}"
        )

    # Redirect dengan parameter status
    return RedirectResponse(
        url=f"/shows?deleted={deleted}&errors={len(errors)}",
        status_code=303,
    )

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

    logger.info(f"Imported {inserted} files to show {show_id}")

    return RedirectResponse(
        url=f"/shows/edit/{show_id}?imported={inserted}",
        status_code=303,
    )


# =====================================================
# DELETE SHOW
# =====================================================
@router.post("/shows/delete/{show_id}")
async def delete_show_route(show_id: int):
    try:
        logger.info(f"Deleting show {show_id}")
        delete_show(show_id)
        logger.info(f"Show {show_id} deleted successfully")

        return RedirectResponse(url="/shows", status_code=status.HTTP_303_SEE_OTHER)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        logger.error(f"Error deleting show {show_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Terjadi kesalahan saat menghapus show"
        )