import time
from typing import Optional
from urllib.parse import urlparse

import httpx
import requests
from diskcache import Cache
from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse

from app.files.crud import get_file_by_id
from app.shows.crud import get_all_shows, get_show_by_id, update_show
from app.templates import templates
from config import BOT_TOKEN, DEFAULT_THUMBNAIL_FILE_ID
from configs.logging_setup import log

cache = Cache("./.thumb_cache")
router = APIRouter()

# 🔗 Default thumbnail URL
DEFAULT_THUMBNAIL_URL = "https://example.com/default.jpg"

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
# PROXY TELEGRAM FILE
# ------------------------
@router.get("/proxy/{file_id}")
async def proxy_telegram_file(file_id: str):
    # Skip jika kosong atau sama dengan default
    if not file_id or file_id == DEFAULT_THUMBNAIL_FILE_ID:
        raise HTTPException(status_code=404, detail="Thumbnail default tidak perlu proxy.")

    # Ambil dari cache
    if file_id in cache:
        content, content_type = cache[file_id]
        if content == b"":  # error cache
            raise HTTPException(status_code=404, detail="Thumbnail tidak ditemukan (cached).")
        return StreamingResponse(iter([content]), media_type=content_type)

    file_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
    async with httpx.AsyncClient() as client:
        try:
            # Ambil path file
            res = await client.get(file_url)
            res.raise_for_status()
            data = res.json()
            if "result" not in data:
                cache.set(file_id, (b"", "image/jpeg"), expire=6 * 3600)
                raise HTTPException(status_code=404, detail="File tidak ditemukan di Telegram.")

            file_path = data["result"]["file_path"]
            file_download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

            # Download
            file_response = await client.get(file_download_url)
            file_response.raise_for_status()
            content = await file_response.aread()
            content_type = file_response.headers.get("Content-Type", "image/jpeg")

            # Cache sukses
            cache.set(file_id, (content, content_type), expire=6 * 3600)
            return StreamingResponse(iter([content]), media_type=content_type)

        except Exception as e:
            throttled_log(file_id, f"Gagal proxy file_id: {file_id} → {e}", level="warning")
            cache.set(file_id, (b"", "image/jpeg"), expire=6 * 3600)
            raise HTTPException(status_code=404, detail="Gagal memuat gambar.")


# ------------------------
# RESOLVE THUMBNAIL
# ------------------------
async def resolve_thumbnail(thumbnail: Optional[str], for_web: bool = False) -> str:
    """Return URL final untuk thumbnail, langsung pakai default kalau invalid."""
    if not thumbnail:
        return DEFAULT_THUMBNAIL_URL if for_web else DEFAULT_THUMBNAIL_FILE_ID

    if not thumbnail.startswith("http"):
        # Kalau default thumbnail, langsung return default
        if thumbnail == DEFAULT_THUMBNAIL_FILE_ID:
            return DEFAULT_THUMBNAIL_URL if for_web else DEFAULT_THUMBNAIL_FILE_ID
        return f"/proxy/{thumbnail}" if for_web else thumbnail

    if is_valid_url(thumbnail):
        try:
            if await is_image_url_accessible(thumbnail):
                return thumbnail
        except Exception as e:
            throttled_log(thumbnail, f"resolve_thumbnail: Gagal cek URL gambar: {e}", level="warning")

    return DEFAULT_THUMBNAIL_URL if for_web else DEFAULT_THUMBNAIL_FILE_ID


def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False


async def is_image_url_accessible(url: str, timeout: int = 5) -> bool:
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        content_type = response.headers.get("Content-Type", "").lower()
        return response.status_code == 200 and content_type.startswith("image/")
    except requests.RequestException:
        return False


# ------------------------
# ROUTES
# ------------------------
@router.get("/shows", response_class=HTMLResponse)
async def show_list(request: Request):
    shows_raw = get_all_shows()
    shows = []
    for s in shows_raw:
        s_dict = dict(s)
        s_dict["resolved_thumbnail"] = await resolve_thumbnail(s.get("thumbnail"), for_web=True)
        shows.append(s_dict)
    return templates.TemplateResponse("shows/list.html", {"request": request, "shows": shows})


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
    show["resolved_thumbnail"] = await resolve_thumbnail(show.get("thumbnail"), for_web=True)
    return templates.TemplateResponse("shows/edit.html", {"request": request, "show": show})


@router.post("/shows/edit/{show_id}")
async def update_show_data(
    request: Request,
    show_id: int,
    title: str = Form(""),
    sinopsis: str = Form(""),
    genre: str = Form(""),
    hashtags: str = Form(""),
    thumbnail: str = Form(""),
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
    if thumbnail.strip():
        if not is_valid_url(thumbnail.strip()):
            raise HTTPException(status_code=400, detail="Thumbnail harus berupa URL valid")
        show_data["thumbnail"] = thumbnail.strip()
    if is_adult is not None:
        show_data["is_adult"] = is_adult

    update_show(show_id, show_data)
    return RedirectResponse(url="/shows", status_code=303)
