from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND

from app.templates import templates
from app.utils.flash import get_flash, set_flash
from db.connect import get_dict_cursor, get_dict_cursor_dep

router = APIRouter()


# ==========================================================
# LIST ALL SOURCES
# ==========================================================
@router.get("/platform", response_class=HTMLResponse)
async def list_sources(request: Request):
    with get_dict_cursor() as (cursor, _):
        cursor.execute("SELECT * FROM request_sources ORDER BY id DESC")
        sources = cursor.fetchall()

    return templates.TemplateResponse(
        "platform/list.html",
        {
            "request": request,
            "sources": sources,
            "title": "Request Platform",
            "flash": get_flash(request),
        },
    )


# ==========================================================
# CREATE SOURCE - FORM
# ==========================================================
@router.get("/platform/create", response_class=HTMLResponse)
async def create_source_form(request: Request):
    return templates.TemplateResponse(
        "platform/create.html",
        {
            "request": request,
            "flash": get_flash(request),
        },
    )


# ==========================================================
# CREATE SOURCE - SUBMIT
# ==========================================================
@router.post("/platform/create")
async def create_source(
    request: Request,
    code: str = Form(...),
    label: str = Form(...),
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    try:
        cursor.execute(
            """
            INSERT INTO request_sources (code, label)
            VALUES (%s, %s)
            """,
            (code.strip().lower(), label.strip()),
        )
        conn.commit()

        set_flash(request, "Source berhasil ditambahkan", "success")
        return RedirectResponse("/platform", status_code=HTTP_302_FOUND)

    except Exception as e:
        conn.rollback()
        set_flash(request, f"Gagal insert: {str(e)}", "danger")
        return RedirectResponse("/platform/create", status_code=HTTP_302_FOUND)


# ==========================================================
# EDIT SOURCE - FORM
# ==========================================================
@router.get("/platform/{source_id}/edit", response_class=HTMLResponse)
async def edit_source_form(source_id: int, request: Request):
    with get_dict_cursor() as (cursor, _):
        cursor.execute(
            "SELECT * FROM request_sources WHERE id = %s",
            (source_id,),
        )
        source = cursor.fetchone()

    if not source:
        raise HTTPException(status_code=404, detail="Source tidak ditemukan")

    return templates.TemplateResponse(
        "platform/edit.html",
        {
            "request": request,
            "source": source,
            "flash": get_flash(request),
        },
    )


# ==========================================================
# EDIT SOURCE - SUBMIT
# ==========================================================
@router.post("/platform/{source_id}/edit")
async def update_source(
    request: Request,
    source_id: int,
    code: str = Form(...),
    label: str = Form(...),
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    try:
        cursor.execute(
            """
            UPDATE request_sources
            SET code = %s,
                label = %s
            WHERE id = %s
            """,
            (code.strip().lower(), label.strip(), source_id),
        )

        if cursor.rowcount == 0:
            set_flash(request, "Source tidak ditemukan", "warning")
        else:
            conn.commit()
            set_flash(request, "Source berhasil diupdate", "success")

    except Exception as e:
        conn.rollback()
        set_flash(request, f"Gagal update: {str(e)}", "danger")

    return RedirectResponse("/platform", status_code=HTTP_302_FOUND)


# ==========================================================
# DELETE SOURCE
# ==========================================================
@router.post("/platform/{source_id}/delete")
async def delete_source(
    request: Request,
    source_id: int,
    db=Depends(get_dict_cursor_dep),
):
    cursor, conn = db

    try:
        cursor.execute(
            "DELETE FROM request_sources WHERE id = %s",
            (source_id,),
        )

        if cursor.rowcount == 0:
            set_flash(request, "Source tidak ditemukan", "warning")
        else:
            conn.commit()
            set_flash(request, "Source berhasil dihapus", "success")

    except Exception as e:
        conn.rollback()
        set_flash(request, f"Gagal delete: {str(e)}", "danger")

    return RedirectResponse("/platform", status_code=HTTP_302_FOUND)
