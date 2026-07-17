from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
import logging

from .repositories.master.kloter_repo import KloterRepository
from app.templates import templates

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/kloter",
    tags=["Master Kloter"],
)


# ==========================================================
# INDEX (DENGAN PAGINATION)
# ==========================================================

@router.get("", response_class=HTMLResponse)
def index(
    request: Request,
    keyword: Optional[str] = "",
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
):
    try:
        # ✅ Repository return dict
        result = KloterRepository.get_all_paginated(
            keyword=keyword if keyword else None,
            page=page,
            per_page=per_page
        )
        
        data = result["data"]
        total = result["total"]
        total_pages = result["total_pages"]
        
    except Exception as e:
        logger.error(f"Error fetching kloter data: {str(e)}")
        raise HTTPException(500, f"Gagal mengambil data kloter: {str(e)}")

    stats = KloterRepository.get_statistics()

    return templates.TemplateResponse(
        "kloter/index.html",
        {
            "request": request,
            "title": "Master Kloter",
            "data": data,
            "stats": stats,
            "keyword": keyword,
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        },
    )

# ==========================================================
# ADD FORM
# ==========================================================

@router.get("/add", response_class=HTMLResponse)
def add_form(request: Request):
    return templates.TemplateResponse(
        "kloter/form.html",
        {
            "request": request,
            "title": "Tambah Kloter",
            "mode": "add",
            "item": None,
        },
    )


# ==========================================================
# ADD SUBMIT
# ==========================================================

@router.post("/add")
def add(
    kode: str = Form(...),
    nama: str = Form(...),
    keterangan: str = Form(""),
    urutan: int = Form(0),
    aktif: bool = Form(True),
):
    try:
        if KloterRepository.exists_kode(kode):
            raise HTTPException(400, "Kode sudah digunakan.")
        
        if KloterRepository.exists_nama(nama):
            raise HTTPException(400, "Nama sudah digunakan.")
        
        KloterRepository.create(
            kode=kode,
            nama=nama,
            keterangan=keterangan,
            urutan=urutan,
            aktif=aktif,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding kloter: {str(e)}")
        raise HTTPException(500, f"Gagal menambah data kloter: {str(e)}")

    return RedirectResponse("/kloter?success=1", status_code=303)


# ==========================================================
# EDIT FORM
# ==========================================================

@router.get("/edit/{kloter_id}", response_class=HTMLResponse)
def edit_form(request: Request, kloter_id: int):
    try:
        item = KloterRepository.get_by_id(kloter_id)
        if not item:
            raise HTTPException(404, f"Data kloter dengan ID {kloter_id} tidak ditemukan.")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching kloter by ID {kloter_id}: {str(e)}")
        raise HTTPException(500, f"Gagal mengambil data kloter: {str(e)}")

    return templates.TemplateResponse(
        "kloter/form.html",
        {
            "request": request,
            "title": "Edit Kloter",
            "mode": "edit",
            "item": item,
        },
    )


# ==========================================================
# EDIT SUBMIT
# ==========================================================

@router.post("/edit/{kloter_id}")
def edit(
    kloter_id: int,
    kode: str = Form(...),
    nama: str = Form(...),
    keterangan: str = Form(""),
    urutan: int = Form(0),
    aktif: bool = Form(True),
):
    try:
        existing_item = KloterRepository.get_by_id(kloter_id)
        if not existing_item:
            raise HTTPException(404, f"Data kloter dengan ID {kloter_id} tidak ditemukan.")
        
        if KloterRepository.exists_kode(kode, exclude_id=kloter_id):
            raise HTTPException(400, "Kode sudah digunakan.")
        
        if KloterRepository.exists_nama(nama, exclude_id=kloter_id):
            raise HTTPException(400, "Nama sudah digunakan.")
        
        KloterRepository.update(
            kloter_id=kloter_id,
            kode=kode,
            nama=nama,
            keterangan=keterangan,
            urutan=urutan,
            aktif=aktif,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating kloter ID {kloter_id}: {str(e)}")
        raise HTTPException(500, f"Gagal mengupdate data kloter: {str(e)}")

    return RedirectResponse("/kloter?success=1", status_code=303)


# ==========================================================
# TOGGLE STATUS
# ==========================================================

@router.post("/toggle/{kloter_id}")
def toggle(kloter_id: int):
    try:
        existing_item = KloterRepository.get_by_id(kloter_id)
        if not existing_item:
            raise HTTPException(404, f"Data kloter dengan ID {kloter_id} tidak ditemukan.")
        
        KloterRepository.toggle_status(kloter_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling kloter ID {kloter_id}: {str(e)}")
        raise HTTPException(500, f"Gagal mengubah status kloter: {str(e)}")

    return RedirectResponse("/kloter?toggled=1", status_code=303)


# ==========================================================
# DELETE
# ==========================================================

@router.post("/delete/{kloter_id}")
def delete(kloter_id: int):
    try:
        existing_item = KloterRepository.get_by_id(kloter_id)
        if not existing_item:
            raise HTTPException(404, f"Data kloter dengan ID {kloter_id} tidak ditemukan.")
        
        KloterRepository.delete(kloter_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting kloter ID {kloter_id}: {str(e)}")
        raise HTTPException(500, f"Gagal menghapus data kloter: {str(e)}")

    return RedirectResponse("/kloter?deleted=1", status_code=303)


# ==========================================================
# BULK DELETE
# ==========================================================

@router.post("/bulk-delete")
def bulk_delete(ids: str = Form(...)):
    if not ids:
        raise HTTPException(400, "IDs tidak boleh kosong")

    id_list = [int(i) for i in ids.split(",") if i.isdigit()]
    if not id_list:
        raise HTTPException(400, "IDs tidak valid")

    deleted = 0
    for kloter_id in id_list:
        try:
            KloterRepository.delete(kloter_id)
            deleted += 1
        except Exception as e:
            logger.error(f"Error deleting kloter {kloter_id}: {str(e)}")

    return RedirectResponse(f"/kloter?deleted={deleted}", status_code=303)


# ==========================================================
# BULK UPDATE STATUS
# ==========================================================

@router.post("/bulk-status")
def bulk_status(
    ids: str = Form(...),
    aktif: bool = Form(...),
):
    if not ids:
        raise HTTPException(400, "IDs tidak boleh kosong")

    id_list = [int(i) for i in ids.split(",") if i.isdigit()]
    if not id_list:
        raise HTTPException(400, "IDs tidak valid")

    updated = KloterRepository.bulk_update_status(id_list, aktif)

    return RedirectResponse(f"/kloter?updated={updated}", status_code=303)


# ==========================================================
# API ENDPOINTS
# ==========================================================

@router.get("/api")
def api_get_all(keyword: str = ""):
    data = KloterRepository.get_all(keyword)
    return {
        "success": True,
        "data": data,
        "total": len(data),
    }


@router.get("/api/{kloter_id}")
def api_get_by_id(kloter_id: int):
    item = KloterRepository.get_by_id(kloter_id)
    if not item:
        raise HTTPException(404, "Kloter tidak ditemukan")
    return {"success": True, "data": item}


@router.get("/api/stats")
def api_get_stats():
    stats = KloterRepository.get_statistics()
    return {"success": True, "data": stats}