import time
from typing import Optional
from urllib.parse import urlparse
from db.connect import get_dict_cursor
import httpx
from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from app.files.crud import get_file_by_id
from app.shows.crud import get_all_shows, get_show_by_id, update_show, insert_show, delete_show_by_id
from app.templates import templates
from configs.logging_setup import log

router = APIRouter()

DEFAULT_THUMB = "https://example.com/default.jpg"
_last_log = {}


# --------------- UTIL LOG THROTTLE -----------------
def throttled_log(key, message, level="warning", interval=60):
    now = time.time()
    if key not in _last_log or now - _last_log[key] > interval:
        getattr(log, level)(message)
        _last_log[key] = now


# --------------- VALIDASI URL ----------------------
def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False


# --------------- RESOLVE THUMB (NO DOWNLOAD) -------
async def resolve_thumbnail_for_web(thumbnail_url: str):
    if not thumbnail_url:
        return None
    return thumbnail_url


# --------------- ROUTES ----------------------------

# LIST SHOWS
@router.get("/shows", response_class=HTMLResponse)
async def show_list(request: Request):

    with get_dict_cursor() as (cursor, _):
        cursor.execute("""
            SELECT id, title, thumbnail_url, sinopsis,
                   genre, hashtags, source, is_adult
            FROM shows
            ORDER BY id DESC
        """)
        shows_raw = cursor.fetchall()

    shows = []
    for show in shows_raw:
        s = dict(show)
        s["resolved_thumbnail"] = await resolve_thumbnail_for_web(s.get("thumbnail_url"))
        shows.append(s)

    return templates.TemplateResponse(
        "shows/list.html",
        {"request": request, "shows": shows}
    )


# EDIT FILE FORM
@router.get("/files/edit/{file_id}", response_class=HTMLResponse)
def edit_file_form(request: Request, file_id: int):
    file = get_file_by_id(file_id)
    shows = get_all_shows()
    return templates.TemplateResponse("files/edit.html", {"request": request, "file": file, "shows": shows})


# EDIT SHOW FORM
@router.get("/shows/edit/{show_id}", response_class=HTMLResponse)
async def edit_show_form(request: Request, show_id: int):
    show = get_show_by_id(show_id)
    if not show:
        raise HTTPException(status_code=404, detail="Show tidak ditemukan")

    show = dict(show)
    show["resolved_thumbnail"] = await resolve_thumbnail_for_web(show.get("thumbnail_url"))

    return templates.TemplateResponse("shows/edit.html", {"request": request, "show": show})


# UPDATE SHOW
@router.post("/shows/edit/{show_id}")
async def update_show_data(
    request: Request,
    show_id: int,
    title: str = Form(""),
    sinopsis: str = Form(""),
    genre: str = Form(""),
    hashtags: str = Form(""),
    source: str = Form(""),
    thumbnail_url: str = Form(""),
    is_adult: Optional[int] = Form(None),
):
    show = get_show_by_id(show_id)
    if not show:
        raise HTTPException(status_code=404, detail="Show tidak ditemukan")

    show_data = dict(show)

    if title.strip(): show_data["title"] = title.strip()
    if sinopsis.strip(): show_data["sinopsis"] = sinopsis.strip()
    if genre.strip(): show_data["genre"] = genre.strip()
    if hashtags.strip(): show_data["hashtags"] = hashtags.strip()
    if source.strip(): show_data["source"] = source.strip()

    if thumbnail_url.strip():
        if not is_valid_url(thumbnail_url.strip()):
            raise HTTPException(status_code=400, detail="Thumbnail URL tidak valid")
        show_data["thumbnail_url"] = thumbnail_url.strip()

    if is_adult is not None:
        show_data["is_adult"] = is_adult

    update_show(show_id, show_data)
    return RedirectResponse(url="/shows", status_code=303)


# ADD SHOW FORM
@router.get("/shows/add")
async def add_show_form(request: Request):
    return templates.TemplateResponse("shows/add.html", {"request": request})


# CREATE SHOW
@router.post("/shows/add")
async def create_show(
    request: Request,
    title: str = Form(...),
    sinopsis: str = Form(""),
    genre: str = Form(""),
    hashtags: str = Form(""),
    source: str = Form(""),
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
        "source": source.strip(),
        "is_adult": bool(is_adult) if is_adult is not None else False,
    }

    if thumbnail_url.strip():
        if not is_valid_url(thumbnail_url.strip()):
            raise HTTPException(status_code=400, detail="Thumbnail URL tidak valid")
        show_data["thumbnail_url"] = thumbnail_url.strip()

    insert_show(show_data)

    return RedirectResponse(url="/shows", status_code=303)


# DELETE SHOW
@router.get("/shows/delete/{show_id}")
async def delete_show(request: Request, show_id: int):
    show = get_show_by_id(show_id)
    if not show:
        raise HTTPException(status_code=404, detail="Show tidak ditemukan")

    delete_show_by_id(show_id)
    return RedirectResponse(url="/shows", status_code=303)
