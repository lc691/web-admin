from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.services.show_files_service import (
    get_show_file_service,
    list_show_files_service,
    update_show_file_service,
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
):
    update_show_file_service(show_file_id, show_id, message_id)
    return RedirectResponse("/show_files", status_code=303)
