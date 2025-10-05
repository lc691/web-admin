import time
from typing import Optional
from urllib.parse import urlparse
from db.connect import get_dict_cursor, get_db_cursor
import httpx
from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from app.files.crud import get_file_by_id
from app.shows.crud import get_all_shows, get_show_by_id, update_show, insert_show, delete_show_by_id
from app.templates import templates
from configs.logging_setup import log

router = APIRouter()

# 🔗 Default thumbnail URL
DEFAULT_THUMB = "https://example.com/default.jpg"

# ------------------------
# UTIL LOG THROTTLE
# ------------------------
_last_log = {}

def throttled_log(key, message, level="warning", interval=60):
    """Log dengan batasan interval supaya tidak spam."""
    now = time.time()
    if key not in _last_log or now - _last_log[key] > interval:
        getattr(log, level)(message)
        _last_log[key] = now


# ------------------------
# RESOLVE THUMBNAIL (URL ONLY, ASYNC)
# ------------------------
async def resolve_thumbnail(url: str | None, for_web: bool = False) -> str:
    if not url:
        return DEFAULT_THUMB

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MyBot/1.0)",
        "Accept": "image/*,*/*;q=0.8"
    }

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            # HEAD request
            resp = await client.head(url, headers=headers)
            content_type = resp.headers.get("content-type", "").lower()
            if resp.status_code == 200 and content_type.startswith("image/"):
                return url
    except Exception as e:
        if not for_web:  # hanya log di non-web mode
            print(f"[WARNING] Thumbnail check gagal: {url} → {e}")

    return DEFAULT_THUMB

async def resolve_thumbnail_for_web(thumbnail_url: str):
    """Khusus dipakai di web (langsung return URL tanpa proxy/download)."""
    if not thumbnail_url:
        return None
    return thumbnail_url

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False


async def is_image_url_accessible(url: str, timeout: int = 10) -> bool:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MyBot/1.0)",
        "Accept": "image/*,*/*;q=0.8"
    }
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
            # Coba HEAD dulu
            try:
                response = await client.head(url, headers=headers)
                content_type = response.headers.get("content-type", "").lower()
                if response.status_code == 200 and content_type.startswith("image/"):
                    return True
            except httpx.RequestError:
                # HEAD gagal → fallback GET (ambil 1KB aja)
                response = await client.get(url, headers=headers, timeout=timeout, follow_redirects=True)
                content_type = response.headers.get("content-type", "").lower()
                return response.status_code in (200, 206) and content_type.startswith("image/")
    except Exception as e:
        throttled_log(url, f"Thumbnail check gagal: {e}", level="warning")
        return False


# ------------------------
# ROUTES
# ------------------------
@router.get("/shows", response_class=HTMLResponse)
async def show_list(request: Request):
    """
    Menampilkan daftar show lengkap, dengan thumbnail yang sudah di-resolve.
    DataTables akan handle sorting/pagination di sisi client.
    """
    # Ambil semua data show
    with get_dict_cursor() as (cursor, _):
        cursor.execute("""
            SELECT id, title, thumbnail_url, sinopsis,
                   genre, hashtags, is_adult
            FROM shows
            ORDER BY id DESC
        """)
        shows_raw = cursor.fetchall()

    # Resolve thumbnail secara async
    shows = []
    for show in shows_raw:
        s_dict = dict(show)
        # pastikan key ada sebelum dipanggil
        thumb_url = s_dict.get("thumbnail_url")
        s_dict["resolved_thumbnail"] = await resolve_thumbnail_for_web(thumb_url)
        shows.append(s_dict)

    return templates.TemplateResponse(
        "shows/list.html",
        {
            "request": request,
            "shows": shows
        }
    )



@router.get("/files/edit/{file_id}", response_class=HTMLResponse)
def edit_file_form(request: Request, file_id: int):
    file = get_file_by_id(file_id)
    shows = get_all_shows()
    return templates.TemplateResponse("files/edit.html", {"request": request, "file": file, "shows": shows})


@router.get("/shows/edit/{show_id}", response_class=HTMLResponse)
async def edit_show_form(request: Request, show_id: int):
    show = get_show_by_id(show_id)
    if not show:
        raise HTTPException(status_code=404, detail="Show tidak ditemukan")
    show = dict(show)
    show["resolved_thumbnail"] = await resolve_thumbnail(
        show.get("thumbnail_url"), for_web=True
    )
    return templates.TemplateResponse("shows/edit.html", {"request": request, "show": show})


@router.post("/shows/edit/{show_id}")
async def update_show_data(
    request: Request,
    show_id: int,
    title: str = Form(""),
    sinopsis: str = Form(""),
    genre: str = Form(""),
    hashtags: str = Form(""),
    thumbnail_url: str = Form(""),
    is_adult: Optional[int] = Form(None),
):
    show = get_show_by_id(show_id)
    if not show:
        raise HTTPException(status_code=404, detail="Show tidak ditemukan")

    show_data = dict(show)

    if title.strip():
        show_data["title"] = title.strip()
    if sinopsis.strip():
        show_data["sinopsis"] = sinopsis.strip()
    if genre.strip():
        show_data["genre"] = genre.strip()
    if hashtags.strip():
        show_data["hashtags"] = hashtags.strip()

    # Thumbnail: kalau kosong biarkan, kalau ada cek valid URL
    if thumbnail_url.strip():
        if not is_valid_url(thumbnail_url.strip()):
            raise HTTPException(status_code=400, detail="Thumbnail URL tidak valid")
        show_data["thumbnail_url"] = thumbnail_url.strip()

    if is_adult is not None:
        show_data["is_adult"] = is_adult

    update_show(show_id, show_data)
    return RedirectResponse(url="/shows", status_code=303)



@router.get("/shows/add")
async def add_show_form(request: Request):
    return templates.TemplateResponse("shows/add.html", {"request": request})

@router.post("/shows/add")
async def create_show(
    request: Request,
    title: str = Form(...),
    sinopsis: str = Form(""),
    genre: str = Form(""),
    hashtags: str = Form(""),
    thumbnail_url: str = Form(""),
    is_adult: Optional[int] = Form(None),
):
    if not title.strip():
        raise HTTPException(status_code=400, detail="Judul tidak boleh kosong")

    show_data = {
        "title": title.strip(),
        "sinopsis": sinopsis.strip(),
        "genre": genre.strip(),
        "hashtags": hashtags.strip(),
        "is_adult": bool(is_adult) if is_adult is not None else False,
    }

    # Thumbnail opsional → hanya simpan kalau valid
    if thumbnail_url.strip():
        if not is_valid_url(thumbnail_url.strip()):
            raise HTTPException(status_code=400, detail="Thumbnail URL tidak valid")
        show_data["thumbnail_url"] = thumbnail_url.strip()

    # fungsi insert ke DB (silakan sesuaikan)
    new_id = insert_show(show_data)

    return RedirectResponse(url="/shows", status_code=303)


@router.get("/shows/delete/{show_id}")
async def delete_show(request: Request, show_id: int):
    show = get_show_by_id(show_id)
    if not show:
        raise HTTPException(status_code=404, detail="Show tidak ditemukan")

    delete_show_by_id(show_id)
    return RedirectResponse(url="/shows", status_code=303)
