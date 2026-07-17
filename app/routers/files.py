import logging
from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.services.files_service import (
    bulk_delete_files_service,
    delete_file_service,
    get_file_service,
    get_file_stats_service,
    list_files_service,
    sync_show_files_service,
    update_file_service,
)
from app.templates import templates

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/files", tags=["Files"])


# ==========================================================
# LIST FILES (DENGAN PAGINATION)
# ==========================================================
@router.get("/", response_class=HTMLResponse)
def list_files_view(
    request: Request,
    page: int = Query(1, ge=1, description="Halaman"),
    per_page: int = Query(20, ge=5, le=100, description="Jumlah per halaman"),
    search: str | None = Query(None, description="Cari berdasarkan nama/title"),
    show_id: int | None = Query(None, description="Filter by show ID"),
    file_type: str | None = Query(None, description="Filter by file type"),
    is_paid: bool | None = Query(None, description="Filter by paid status"),
):
    result = list_files_service(
        page=page,
        per_page=per_page,
        search=search,
        show_id=show_id,
        file_type=file_type,
        is_paid=is_paid,
    )

    # ✅ Ambil stats
    stats = get_file_stats_service()

    return templates.TemplateResponse(
        "files/list.html",
        {
            "request": request,
            "files": result["data"],
            "total": result["total"],
            "page": result["page"],
            "per_page": result["per_page"],
            "total_pages": result["total_pages"],
            "search": search,
            "show_id": show_id,
            "file_type": file_type,
            "is_paid": is_paid,
            "stats": stats,  # ✅ Kirim stats ke template
        },
    )

# ==========================================================
# EDIT FILE - FORM
# ==========================================================
@router.get("/edit/{file_id}", response_class=HTMLResponse)
def edit_file_form(request: Request, file_id: int):
    file = get_file_service(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File tidak ditemukan")

    return templates.TemplateResponse(
        "files/edit.html",
        {"request": request, "file": file},
    )


# ==========================================================
# EDIT FILE - SUBMIT
# ==========================================================
@router.post("/edit/{file_id}")
def update_file_handler(
    file_id: int,
    file_name: str = Form(...),
    main_title: str | None = Form(None),
    is_paid: int = Form(...),
    show_id: str | None = Form(None),
):
    if not file_name or not file_name.strip():
        raise HTTPException(400, "File name wajib diisi")

    try:
        update_file_service(
            file_id,
            {
                "file_name": file_name.strip(),
                "main_title": main_title.strip() if main_title else None,
                "is_paid": is_paid == 1,
                "show_id": int(show_id) if show_id else None,
            },
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Error updating file {file_id}: {str(e)}")
        raise HTTPException(500, f"Gagal mengupdate file: {str(e)}")

    return RedirectResponse("/files", status_code=303)


# ==========================================================
# DELETE FILE
# ==========================================================
@router.post("/delete/{file_id}")
def delete_file_handler(file_id: int):
    try:
        delete_file_service(file_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        logger.error(f"Error deleting file {file_id}: {str(e)}")
        raise HTTPException(500, f"Gagal menghapus file: {str(e)}")

    return RedirectResponse("/files", status_code=303)


# ==========================================================
# BULK DELETE FILES
# ==========================================================
@router.post("/bulk-delete")
def bulk_delete_files_handler(ids: str = Form(...)):
    if not ids:
        raise HTTPException(status_code=400, detail="No file ids provided")

    id_list = [int(i) for i in ids.split(",") if i.isdigit()]
    if not id_list:
        raise HTTPException(status_code=400, detail="Invalid file ids")

    try:
        result = bulk_delete_files_service(id_list)
        logger.info(f"Bulk deleted {result} files")
    except Exception as e:
        logger.error(f"Error bulk deleting files: {str(e)}")
        raise HTTPException(500, f"Gagal menghapus file: {str(e)}")

    return RedirectResponse("/files", status_code=303)


# ==========================================================
# BULK EDIT - FORM
# ==========================================================
@router.get("/bulk-edit", response_class=HTMLResponse)
def bulk_edit_form(request: Request, ids: str):
    if not ids:
        raise HTTPException(status_code=400, detail="IDs kosong")

    id_list = [int(i) for i in ids.split(",") if i.isdigit()]
    if not id_list:
        raise HTTPException(status_code=400, detail="IDs tidak valid")

    return templates.TemplateResponse(
        "files/bulk_edit.html",
        {
            "request": request,
            "ids": ids,
            "file_count": len(id_list),
        },
    )


# ==========================================================
# BULK EDIT - SUBMIT
# ==========================================================
@router.post("/bulk-edit")
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

    updated = 0
    for file_id in id_list:
        try:
            update_file_service(file_id, data)
            updated += 1
        except Exception as e:
            logger.error(f"Error updating file {file_id}: {str(e)}")

    logger.info(f"Bulk updated {updated} files")
    return RedirectResponse("/files", status_code=303)


# ==========================================================
# SYNC SHOW FILES
# ==========================================================
@router.post("/sync-show-files")
def sync_show_files_handler(show_id: int = Form(...)):
    try:
        inserted = sync_show_files_service(show_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Show tidak ditemukan")
    except Exception as e:
        logger.error(f"Error syncing show files: {str(e)}")
        raise HTTPException(500, f"Gagal sinkronisasi: {str(e)}")

    return RedirectResponse(
        url=f"/files?sync={inserted}",
        status_code=303,
    )


# ==========================================================
# API ENDPOINTS (JSON)
# ==========================================================
@router.get("/api")
def list_files_api(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=5, le=100),
    search: str | None = None,
    show_id: int | None = None,
    file_type: str | None = None,
    is_paid: bool | None = None,
):
    result = list_files_service(
        page=page,
        per_page=per_page,
        search=search,
        show_id=show_id,
        file_type=file_type,
        is_paid=is_paid,
    )
    return {
        "success": True,
        "data": result["data"],
        "total": result["total"],
        "page": result["page"],
        "per_page": result["per_page"],
        "total_pages": result["total_pages"],
    }


@router.get("/api/{file_id}")
def get_file_api(file_id: int):
    file = get_file_service(file_id)
    if not file:
        raise HTTPException(404, "File tidak ditemukan")
    return {"success": True, "data": file}


@router.get("/api/stats")
def get_file_stats_api():
    stats = get_file_stats_service()
    return {"success": True, "data": stats}