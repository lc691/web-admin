from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
from app.files.crud import (delete_file, get_all_files, get_file_by_id,
                            update_file_by_id)
from app.templates import templates
from fastapi import Query

router = APIRouter()


@router.get("/files", response_class=HTMLResponse)
def list_files(request: Request, q: Optional[str] = None):
    if q:
        all_files = get_all_files()
        # Sesuaikan filter pencarian dengan kebutuhan, contoh:
        filtered_files = [f for f in all_files if q.lower() in f['file_name'].lower()]
        return templates.TemplateResponse("files/list.html", {
            "request": request,
            "files": filtered_files,
            "q": q
        })
    else:
        files = get_all_files()
        return templates.TemplateResponse("files/list.html", {
            "request": request,
            "files": files,
            "q": ""
        })


@router.get("/files/edit/{file_id}", response_class=HTMLResponse)
def edit_file_form(request: Request, file_id: int):
    file = get_file_by_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File tidak ditemukan")
    return templates.TemplateResponse("files/edit.html", {"request": request, "file": file})


@router.post("/files/edit/{file_id}")
def update_file_handler(
    request: Request,
    file_id: int,
    file_name: str = Form(...),
    file_type: str = Form(...),
    file_size: int = Form(...),
    main_title: str = Form(...),
    channel_username: str = Form(...),
    message_id: Optional[str] = Form(None),
    show_id: Optional[str] = Form(None),
    q: Optional[str] = Query(None)  # ← ambil dari query param
):
    # Konversi ke int hanya jika tidak kosong
    msg_id_int = int(message_id) if message_id else None
    show_id_int = int(show_id) if show_id else None

    update_file_by_id(
        file_id=file_id,
        file_name=file_name,
        file_type=file_type,
        file_size=file_size,
        main_title=main_title,
        channel_username=channel_username,
        message_id=msg_id_int,
        show_id=show_id_int
    )

    redirect_url = f"/files?q={q}" if q else "/files"
    return RedirectResponse(url=redirect_url, status_code=303)


@router.post("/files/delete/{file_id}")
def delete_file_handler(request: Request, file_id: int):
    delete_file(file_id)
    return RedirectResponse(url="/files", status_code=303)