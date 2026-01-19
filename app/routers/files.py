from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.services.files_service import (
    delete_file_service,
    get_file_service,
    list_files_service,
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
):
    update_file_service(
        file_id,
        {
            "file_name": file_name.strip(),
            "main_title": main_title.strip() if main_title else None,
            "is_paid": bool(int(is_paid)),
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
