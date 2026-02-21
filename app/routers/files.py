from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.services.files_service import (
    delete_file_service,
    get_file_service,
    list_files_service,
    sync_show_files_service,
    update_file_service,
)
from app.templates import templates

router = APIRouter()


@router.get("/files", response_class=HTMLResponse)
def list_files_view(request: Request):
    files = list_files_service()
    return templates.TemplateResponse(
        "files/list.html",
        {"request": request, "files": files},
    )


@router.get("/files/edit/{file_id}", response_class=HTMLResponse)
def edit_file_form(request: Request, file_id: int):
    file = get_file_service(file_id)
    if not file:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        "files/edit.html",
        {"request": request, "file": file},
    )


@router.post("/files/edit/{file_id}")
def update_file_handler(
    file_id: int,
    file_name: str = Form(...),
    main_title: str | None = Form(None),
    is_paid: int = Form(...),
    show_id: str | None = Form(None),
):
    update_file_service(
        file_id,
        {
            "file_name": file_name.strip(),
            "main_title": main_title.strip() if main_title else None,
            "is_paid": is_paid == 1,
            "show_id": int(show_id) if show_id else None,
        },
    )

    return RedirectResponse("/files", status_code=303)


# =======================
# DELETE FILE
# =======================
@router.post("/files/delete/{file_id}")
def delete_file_handler(file_id: int):
    delete_file_service(file_id)
    return RedirectResponse(
        url="/files",
        status_code=303,
    )


# =======================
# BULK DELETE FILES
# =======================
@router.post("/files/bulk-delete")
def bulk_delete_files(
    ids: str = Form(...),
):
    if not ids:
        raise HTTPException(status_code=400, detail="No file ids provided")

    id_list = [int(i) for i in ids.split(",") if i.isdigit()]

    if not id_list:
        raise HTTPException(status_code=400, detail="Invalid file ids")

    for file_id in id_list:
        delete_file_service(file_id)

    return RedirectResponse(
        url="/files",
        status_code=303,
    )


@router.get("/files/bulk-edit", response_class=HTMLResponse)
def bulk_edit_form(request: Request, ids: str):
    if not ids:
        raise HTTPException(status_code=400)

    return templates.TemplateResponse(
        "files/bulk_edit.html",
        {
            "request": request,
            "ids": ids,
            "files": [],
        },
    )


@router.post("/files/bulk-edit")
def bulk_edit_submit(
    ids: str = Form(...),
    apply_main_title: str | None = Form(None),
    main_title: str | None = Form(None),
    apply_is_paid: str | None = Form(None),
    is_paid: int | None = Form(None),
    apply_show_id: str | None = Form(None),
    show_id: int | None = Form(None),
):
    if not ids:
        raise HTTPException(status_code=400, detail="IDs tidak boleh kosong")

    id_list = [int(i) for i in ids.split(",") if i.isdigit()]
    if not id_list:
        raise HTTPException(status_code=400, detail="IDs tidak valid")

    data = {}

    if apply_main_title:
        if not main_title or not main_title.strip():
            raise HTTPException(status_code=400, detail="Main Title wajib diisi")
        data["main_title"] = main_title.strip()

    if apply_is_paid:
        if is_paid is None:
            raise HTTPException(status_code=400, detail="Pilih Free atau Paid")
        data["is_paid"] = is_paid == 1

    if apply_show_id:
        if show_id is None:
            raise HTTPException(status_code=400, detail="Show ID wajib diisi")
        data["show_id"] = show_id

    if not data:
        return RedirectResponse("/files", status_code=303)

    for file_id in id_list:
        update_file_service(file_id, data)

    return RedirectResponse("/files", status_code=303)


@router.post("/files/sync-show-files")
def sync_show_files_handler(
    show_id: int = Form(...),
):
    try:
        inserted = sync_show_files_service(show_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Show tidak ditemukan")

    return RedirectResponse(
        url=f"/files?sync={inserted}",
        status_code=303,
    )
