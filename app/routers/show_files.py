import re

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.services.show_files_service import (
    delete_show_files_bulk_service,
    get_show_file_service,
    list_show_files_service,
    update_show_file_service,
    update_show_files_bulk_service,
)
from app.templates import templates

router = APIRouter()


@router.get("/show_files", response_class=HTMLResponse)
def list_show_files_view(request: Request):
    rows = list_show_files_service()
    return templates.TemplateResponse(
        "show_files/list.html",
        {"request": request, "rows": rows},
    )


@router.get("/show_files/edit/{show_file_id}", response_class=HTMLResponse)
def edit_show_file_form(request: Request, show_file_id: int):
    row = get_show_file_service(show_file_id)
    if not row:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        "show_files/edit.html",
        {"request": request, "row": row},
    )


@router.post("/show_files/edit/{show_file_id}")
def update_show_file_handler(
    show_file_id: int,
    show_id: int | None = Form(None),
    message_id: int | None = Form(None),
    alias_name: str | None = Form(None),
):
    data = {}

    if show_id is not None:
        data["show_id"] = show_id

    if message_id is not None:
        data["message_id"] = message_id

    if alias_name is not None:
        data["alias_name"] = alias_name

    update_show_file_service(show_file_id, data)

    return RedirectResponse("/show_files", status_code=303)


# ==========================================================
# BULK EDIT FORM
# ==========================================================
@router.get("/show_files/bulk-edit", response_class=HTMLResponse)
def bulk_edit_form(request: Request, ids: str):
    if not ids:
        raise HTTPException(status_code=400, detail="IDs kosong")

    return templates.TemplateResponse(
        "show_files/bulk_edit.html",
        {
            "request": request,
            "ids": ids,
        },
    )


@router.post("/show_files/bulk-edit")
def bulk_edit_show_files(
    ids: str = Form(...),
    apply_show_id: str | None = Form(None),
    show_id: int | None = Form(None),
    apply_message_id: str | None = Form(None),
    message_id: int | None = Form(None),
    apply_alias_name: str | None = Form(None),
    alias_name: str | None = Form(None),
):
    if not ids:
        raise HTTPException(status_code=400, detail="IDs kosong")

    id_list = [int(i) for i in ids.split(",") if i.isdigit()]
    if not id_list:
        raise HTTPException(status_code=400, detail="IDs tidak valid")

    data = {}

    if apply_show_id:
        if show_id is None:
            raise HTTPException(status_code=400, detail="Show ID wajib diisi")
        data["show_id"] = show_id

    if apply_message_id:
        data["message_id"] = message_id

    if apply_alias_name:
        data["alias_name"] = alias_name

    if not data:
        return RedirectResponse("/show_files", status_code=303)

    updated = update_show_files_bulk_service(id_list, data)

    return RedirectResponse(
        url=f"/show_files?updated={updated}",
        status_code=303,
    )


@router.post("/show_files/bulk-delete")
def bulk_delete_show_files(ids: str = Form(...)):

    if not ids:
        raise HTTPException(status_code=400, detail="IDs kosong")

    # Aman & fleksibel parsing
    id_list = [int(x) for x in re.findall(r"\d+", ids)]

    if not id_list:
        raise HTTPException(status_code=400, detail="IDs tidak valid")

    deleted = delete_show_files_bulk_service(id_list)

    return RedirectResponse(
        url=f"/show_files?deleted={deleted}",
        status_code=303,
    )
