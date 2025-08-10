from typing import Optional
from urllib.parse import urlparse

import httpx
import requests
from diskcache import Cache
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse

from app.files.crud import get_file_by_id
from app.shows.crud import get_all_shows, get_dict_cursor
from app.templates import templates
from config import BOT_TOKEN, DEFAULT_THUMBNAIL_FILE_ID
from configs.logging_setup import log

cache = Cache("./.thumb_cache")  # folder cache lokal

router = APIRouter()



@router.get("/proxy/{file_id}")
async def proxy_telegram_file(file_id: str):
    if file_id in cache:
        content, content_type = cache[file_id]
        return StreamingResponse(
            iter([content]),
            media_type=content_type
        )

    file_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
    async with httpx.AsyncClient() as client:
        try:
            # Ambil path file dari Telegram
            res = await client.get(file_url)
            res.raise_for_status()
            file_path = res.json()["result"]["file_path"]
            file_download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

            # Download gambar
            file_response = await client.get(file_download_url)
            file_response.raise_for_status()
            content = await file_response.aread()
            content_type = file_response.headers.get("Content-Type", "image/jpeg")

            # Cache selama 6 jam
            cache.set(file_id, (content, content_type), expire=6 * 3600)

            return StreamingResponse(
                iter([content]),
                media_type=content_type
            )
        except Exception as e:
            log.warning(f"Gagal proxy file_id: {file_id} → {e}")
            raise HTTPException(status_code=404, detail="Gagal memuat gambar.")

# ⛳ Ganti `@app.get` → `@router.get`
@router.get("/shows", response_class=HTMLResponse)
async def show_list(request: Request):
    shows_raw = get_all_shows()
    shows = []

    for s in shows_raw:
        s_dict = dict(s)
        s_dict["resolved_thumbnail"] = await resolve_thumbnail(s.get("thumbnail"), for_web=True)
        shows.append(s_dict)

    return templates.TemplateResponse("shows/list.html", {
        "request": request,
        "shows": shows,
    })


@router.get("/files/edit/{file_id}", response_class=HTMLResponse)
def edit_file_form(request: Request, file_id: int):
    file = get_file_by_id(file_id)
    shows = get_all_shows()
    return templates.TemplateResponse("files/edit.html", {
        "request": request, "file": file, "shows": shows
    })


# 🔗 Default thumbnail untuk ditampilkan di web jika file_id kosong atau URL tidak valid
DEFAULT_THUMBNAIL_URL = "https://example.com/default.jpg"


async def resolve_thumbnail(thumbnail: Optional[str], for_web: bool = False) -> str:
    if not thumbnail:
        return DEFAULT_THUMBNAIL_URL if for_web else DEFAULT_THUMBNAIL_FILE_ID

    if not thumbnail.startswith("http"):
        return f"/proxy/{thumbnail}" if for_web else thumbnail

    if is_valid_url(thumbnail):
        try:
            if await is_image_url_accessible(thumbnail):
                return thumbnail
        except Exception as e:
            log.warning(f"resolve_thumbnail: Gagal cek URL gambar: {e}")

    return DEFAULT_THUMBNAIL_URL if for_web else DEFAULT_THUMBNAIL_FILE_ID


def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False


def is_image_url_accessible(url: str, timeout: int = 5) -> bool:
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        content_type = response.headers.get("Content-Type", "").lower()
        return response.status_code == 200 and content_type.startswith("image/")
    except (requests.RequestException, Exception):
        return False

from fastapi import Form
from fastapi.responses import RedirectResponse
from app.shows.crud import get_show_by_id, update_show

@router.get("/shows/edit/{show_id}", response_class=HTMLResponse)
async def edit_show_form(request: Request, show_id: int):
    show = get_show_by_id(show_id)
    if not show:
        raise HTTPException(status_code=404, detail="Show tidak ditemukan")

    show = dict(show)
    show["resolved_thumbnail"] = await resolve_thumbnail(show.get("thumbnail"), for_web=True)

    return templates.TemplateResponse("shows/edit.html", {
        "request": request,
        "show": show
    })


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

    # Convert ke dict supaya bisa dimodifikasi
    show_data = dict(show)

    # Update hanya field yang diisi
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

    # Simpan ke DB
    update_show(show_id, show_data)

    return RedirectResponse(url="/shows", status_code=303)