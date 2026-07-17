from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND

from app.templates import templates
from app.utils.logger import log

from .repositories.master.joki_repo import JokiRepository

router = APIRouter(
    prefix="/joki",
    tags=["Master Joki"],
)


# ==========================================================
# INDEX (DENGAN PAGINATION)
# ==========================================================

@router.get("", response_class=HTMLResponse)
def index(
    request: Request,
    keyword: str = Query("", description="Kata kunci pencarian"),
    page: int = Query(1, ge=1, description="Halaman"),
    per_page: int = Query(20, ge=5, le=100, description="Jumlah per halaman"),
):
    """
    Menampilkan daftar joki dengan fitur pencarian dan pagination.
    """
    result = JokiRepository.get_paginated(
        keyword=keyword,
        page=page,
        per_page=per_page,
    )
    stats = JokiRepository.get_statistics()

    return templates.TemplateResponse(
        "joki/index.html",
        {
            "request": request,
            "title": "Master Joki",
            "data": result["data"],
            "stats": stats,
            "keyword": keyword,
            "page": result["page"],
            "per_page": result["per_page"],
            "total": result["total"],
            "total_pages": result["total_pages"],
        },
    )


# ==========================================================
# ADD FORM
# ==========================================================

@router.get("/add", response_class=HTMLResponse)
def add_form(request: Request):
    """
    Menampilkan form untuk menambah data joki baru.
    """
    return templates.TemplateResponse(
        "joki/form.html",
        {
            "request": request,
            "title": "Tambah Joki",
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
    harga_per_judul: float = Form(...),
    no_hp: str = Form(""),
    keterangan: str = Form(""),
    aktif: bool = Form(True),
):
    """
    Menyimpan data joki baru ke database.
    Melakukan validasi kode dan nama tidak boleh duplikat.
    """
    log.info(f"[JOKI] tambah: kode={kode}, nama={nama}")

    # Validasi kode
    if JokiRepository.exists_kode(kode):
        raise HTTPException(400, "Kode sudah digunakan.")

    # Validasi nama
    if JokiRepository.exists_nama(nama):
        raise HTTPException(400, "Nama sudah digunakan.")

    # Validasi harga
    if harga_per_judul <= 0:
        raise HTTPException(400, "Harga per judul harus lebih dari 0.")

    JokiRepository.create(
        kode=kode,
        nama=nama,
        no_hp=no_hp,
        harga_per_judul=harga_per_judul,
        keterangan=keterangan,
        aktif=aktif,
    )

    log.info(f"[JOKI] berhasil tambah: {kode}")

    return RedirectResponse(
        "/joki?success=1",
        status_code=HTTP_302_FOUND,
    )


# ==========================================================
# EDIT FORM
# ==========================================================

@router.get("/edit/{joki_id}", response_class=HTMLResponse)
def edit_form(request: Request, joki_id: int):
    """
    Menampilkan form edit data joki berdasarkan ID.
    """
    item = JokiRepository.get_by_id(joki_id)
    if not item:
        raise HTTPException(404, "Joki tidak ditemukan.")

    return templates.TemplateResponse(
        "joki/form.html",
        {
            "request": request,
            "title": "Edit Joki",
            "mode": "edit",
            "item": item,
        },
    )


# ==========================================================
# EDIT SUBMIT
# ==========================================================

@router.post("/edit/{joki_id}")
def edit(
    joki_id: int,
    kode: str = Form(...),
    nama: str = Form(...),
    harga_per_judul: float = Form(...),
    no_hp: str = Form(""),
    keterangan: str = Form(""),
    aktif: bool = Form(True),
):
    """
    Memperbarui data joki yang sudah ada.
    Melakukan validasi kode dan nama tidak boleh duplikat dengan data lain.
    """
    log.info(f"[JOKI] update id={joki_id}")

    # Cek apakah joki ada
    item = JokiRepository.get_by_id(joki_id)
    if not item:
        raise HTTPException(404, "Joki tidak ditemukan.")

    # Validasi kode (kecuali dirinya sendiri)
    if JokiRepository.exists_kode(kode, joki_id):
        raise HTTPException(400, "Kode sudah digunakan.")

    # Validasi nama (kecuali dirinya sendiri)
    if JokiRepository.exists_nama(nama, joki_id):
        raise HTTPException(400, "Nama sudah digunakan.")

    # Validasi harga
    if harga_per_judul <= 0:
        raise HTTPException(400, "Harga per judul harus lebih dari 0.")

    JokiRepository.update(
        joki_id=joki_id,
        kode=kode,
        nama=nama,
        harga_per_judul=harga_per_judul,
        no_hp=no_hp,
        keterangan=keterangan,
        aktif=aktif,
    )

    log.info(f"[JOKI] berhasil update id={joki_id}")

    return RedirectResponse(
        "/joki?success=1",
        status_code=HTTP_302_FOUND,
    )


# ==========================================================
# DELETE
# ==========================================================

@router.post("/delete/{joki_id}")
def delete(joki_id: int):
    """
    Menghapus data joki berdasarkan ID.
    """
    log.info(f"[JOKI] delete id={joki_id}")

    # Cek apakah joki ada
    item = JokiRepository.get_by_id(joki_id)
    if not item:
        raise HTTPException(404, "Joki tidak ditemukan.")

    JokiRepository.delete(joki_id)

    log.info(f"[JOKI] berhasil delete id={joki_id}")

    return RedirectResponse(
        "/joki?deleted=1",
        status_code=HTTP_302_FOUND,
    )


# ==========================================================
# TOGGLE STATUS
# ==========================================================

@router.post("/toggle/{joki_id}")
def toggle(joki_id: int):
    """
    Mengubah status aktif/non-aktif joki berdasarkan ID.
    """
    log.info(f"[JOKI] toggle id={joki_id}")

    # Cek apakah joki ada
    item = JokiRepository.get_by_id(joki_id)
    if not item:
        raise HTTPException(404, "Joki tidak ditemukan.")

    new_status = JokiRepository.toggle_status(joki_id)

    log.info(f"[JOKI] status baru id={joki_id}: {new_status}")

    return RedirectResponse(
        "/joki?toggled=1",
        status_code=HTTP_302_FOUND,
    )


# ==========================================================
# BULK DELETE
# ==========================================================

@router.post("/bulk-delete")
def bulk_delete(ids: str = Form(...)):
    """
    Menghapus multiple joki sekaligus.
    """
    if not ids:
        raise HTTPException(400, "IDs tidak boleh kosong")

    id_list = [int(i) for i in ids.split(",") if i.isdigit()]
    if not id_list:
        raise HTTPException(400, "IDs tidak valid")

    log.info(f"[JOKI] bulk delete: {len(id_list)} joki")

    deleted = 0
    for joki_id in id_list:
        try:
            JokiRepository.delete(joki_id)
            deleted += 1
        except Exception as e:
            log.error(f"[JOKI] gagal delete id={joki_id}: {str(e)}")

    log.info(f"[JOKI] berhasil bulk delete: {deleted} joki")

    return RedirectResponse(
        f"/joki?deleted={deleted}",
        status_code=HTTP_302_FOUND,
    )


# ==========================================================
# BULK UPDATE STATUS
# ==========================================================

@router.post("/bulk-status")
def bulk_status(
    ids: str = Form(...),
    aktif: bool = Form(...),
):
    """
    Update status multiple joki sekaligus.
    """
    if not ids:
        raise HTTPException(400, "IDs tidak boleh kosong")

    id_list = [int(i) for i in ids.split(",") if i.isdigit()]
    if not id_list:
        raise HTTPException(400, "IDs tidak valid")

    log.info(f"[JOKI] bulk update status: {len(id_list)} joki to {aktif}")

    updated = JokiRepository.bulk_update_status(id_list, aktif)

    log.info(f"[JOKI] berhasil bulk update status: {updated} joki")

    return RedirectResponse(
        f"/joki?updated={updated}",
        status_code=HTTP_302_FOUND,
    )


# ==========================================================
# API ENDPOINTS (JSON)
# ==========================================================

@router.get("/api")
def api_get_all(keyword: str = ""):
    """API endpoint untuk mendapatkan data joki."""
    data = JokiRepository.get_all(keyword)
    return {
        "success": True,
        "data": data,
        "total": len(data),
    }


@router.get("/api/{joki_id}")
def api_get_by_id(joki_id: int):
    """API endpoint untuk mendapatkan joki by ID."""
    item = JokiRepository.get_by_id(joki_id)
    if not item:
        raise HTTPException(404, "Joki tidak ditemukan")
    return {"success": True, "data": item}


@router.get("/api/stats")
def api_get_stats():
    """API endpoint untuk mendapatkan statistik joki."""
    stats = JokiRepository.get_statistics()
    return {"success": True, "data": stats}