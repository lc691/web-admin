from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.templates import templates

from .file_import import import_show_files
from .service import create_show, delete_show, get_show, list_shows, update_show
from .validators import is_valid_url

router = APIRouter()


async def resolve_thumbnail_for_web(thumbnail_url: str | None):
    # web TIDAK download, hanya pass-through
    return thumbnail_url


@router.get("/shows", response_class=HTMLResponse)
async def show_list(request: Request):
    shows = list_shows()
    return templates.TemplateResponse(
        "shows/list.html",
        {"request": request, "shows": shows},
    )


@router.get("/shows/add", response_class=HTMLResponse)
async def add_show_form(request: Request):
    return templates.TemplateResponse(
        "shows/add.html",
        {
            "request": request,
            "show": None,  # penting untuk template
        },
    )


@router.post("/shows/add")
async def create_show_post(
    title: str = Form(...),
    sinopsis: str = Form(""),
    genre: str = Form(""),
    source: str = Form(""),
    hashtags: str = Form(""),
    thumbnail_url: str = Form(""),
    is_adult: int | None = Form(None),
):
    title = title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Judul wajib diisi")

    data = {
        "title": title,
        "sinopsis": sinopsis.strip(),
        "genre": genre.strip(),
        "source": source.strip() or "Dramabox",
        "hashtags": hashtags.strip(),
        "is_adult": bool(is_adult),
    }

    # Thumbnail optional
    if thumbnail_url.strip():
        if not is_valid_url(thumbnail_url.strip()):
            raise HTTPException(
                status_code=400,
                detail="Thumbnail URL tidak valid",
            )
        data["thumbnail_url"] = thumbnail_url.strip()

    create_show(data)

    return RedirectResponse(
        url="/shows",
        status_code=303,
    )


@router.get("/shows/edit/{show_id}", response_class=HTMLResponse)
async def edit_show_form(request: Request, show_id: int):
    show = get_show(show_id)
    if not show:
        raise HTTPException(status_code=404)

    shows = list_shows()  # ← ini penting

    s = dict(show)
    s["resolved_thumbnail"] = await resolve_thumbnail_for_web(s.get("thumbnail_url"))

    return templates.TemplateResponse(
        "shows/edit.html",
        {
            "request": request,
            "show": s,
            "shows": shows,
        },
    )


@router.post("/shows/edit/{show_id}")
async def update_show_post(
    show_id: int,
    title: str = Form(""),
    sinopsis: str = Form(""),
    genre: str = Form(""),
    source: str = Form(""),
    hashtags: str = Form(""),
    thumbnail_url: str = Form(""),
    is_adult: int = Form(0),
):
    data = {}

    if title.strip():
        data["title"] = title.strip()

    data["sinopsis"] = sinopsis.strip()
    data["genre"] = genre.strip()
    data["source"] = source.strip()
    data["hashtags"] = hashtags.strip()

    # thumbnail logic (sesuai placeholder di template)
    if thumbnail_url.strip() == "":
        data["thumbnail_url"] = None
    else:
        if not is_valid_url(thumbnail_url.strip()):
            raise HTTPException(
                status_code=400,
                detail="Thumbnail URL tidak valid",
            )
        data["thumbnail_url"] = thumbnail_url.strip()

    data["is_adult"] = bool(int(is_adult))

    update_show(show_id, data)

    return RedirectResponse(
        url="/shows",
        status_code=303,
    )


@router.post("/shows/{show_id}/import-files")
async def import_files_post(
    request: Request,
    show_id: int,
    source_show_id: int = Form(...),
    message_id: int = Form(...),
):
    if show_id == source_show_id:
        raise HTTPException(status_code=400, detail="Source dan target show tidak boleh sama")

    inserted = import_show_files(
        source_show_id=source_show_id,
        target_show_id=show_id,
        message_id=message_id,
    )

    return RedirectResponse(
        url=f"/shows/edit/{show_id}?imported={inserted}",
        status_code=303,
    )


@router.get("/shows/delete/{show_id}")
async def delete_show_post(show_id: int):
    delete_show(show_id)
    return RedirectResponse("/shows", status_code=303)
