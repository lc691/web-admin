from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.templates import templates

from .service import delete_file, get_file, list_files, update_file

router = APIRouter()


# =======================
# LIST FILES
# =======================
@router.get("/files", response_class=HTMLResponse)
def list_files_view(request: Request, q: str | None = None):
    files = list_files()

    # filter di memory (cache hit → NO DB)
    if q:
        q_lower = q.lower()
        files = [f for f in files if q_lower in (f.get("file_name") or "").lower()]

    return templates.TemplateResponse(
        "files/list.html",
        {
            "request": request,
            "files": files,
            "q": q or "",
        },
    )


# =======================
# EDIT FILE FORM
# =======================
@router.get("/files/edit/{file_id}", response_class=HTMLResponse)
def edit_file_form(request: Request, file_id: int):
    file = get_file(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File tidak ditemukan")

    return templates.TemplateResponse(
        "files/edit.html",
        {
            "request": request,
            "file": file,
        },
    )


# =======================
# UPDATE FILE
# =======================
@router.post("/files/edit/{file_id}")
def update_file_handler(
    file_id: int,
    file_name: str = Form(...),
    file_type: str = Form(...),
    file_size: int = Form(...),
    main_title: str = Form(...),
    channel_username: str = Form(...),
    message_id: str | None = Form(None),
    show_id: str | None = Form(None),
    q: str | None = Query(None),
):
    update_file(
        file_id=file_id,
        file_name=file_name,
        file_type=file_type,
        file_size=file_size,
        main_title=main_title,
        channel_username=channel_username,
        message_id=int(message_id) if message_id else None,
        show_id=int(show_id) if show_id else None,
    )

    return RedirectResponse(
        url=f"/files?q={q}" if q else "/files",
        status_code=303,
    )


# =======================
# DELETE FILE
# =======================
@router.post("/files/delete/{file_id}")
def delete_file_handler(file_id: int):
    delete_file(file_id)
    return RedirectResponse(
        url="/files",
        status_code=303,
    )
