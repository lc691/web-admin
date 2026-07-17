from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from app.templates import templates
from app.utils.logger import log

from .repositories.master.joki_repo import JokiRepository
from .repositories.master.kloter_repo import KloterRepository
from .repositories.transaksi.catatan_repo import CatatanRepository
from .repositories.laporan.rekap_repo import RekapRepository


router = APIRouter(
    prefix="/catatan",
    tags=["Catatan"],
)


# ==========================================================
# HELPER
# ==========================================================

def validate_tanggal(tanggal: str) -> str:
    """Validasi format tanggal."""
    try:
        datetime.strptime(tanggal, "%Y-%m-%d")
        return tanggal
    except ValueError:
        raise HTTPException(400, "Format tanggal harus YYYY-MM-DD")


# ==========================================================
# INDEX
# ==========================================================

@router.get("", response_class=HTMLResponse)
def index(
    request: Request,
    tanggal: str | None = None,
    page: int = Query(1, ge=1),
):
    if tanggal is None:
        tanggal = date.today().isoformat()
    else:
        validate_tanggal(tanggal)

    result = CatatanRepository.get_all(
        tanggal=tanggal,
        page=page,
        per_page=20,
    )

    summary = RekapRepository.get_total_harian(tanggal=tanggal)

    return templates.TemplateResponse(
        "catatan/index.html",
        {
            "request": request,
            "title": "Catatan Harian",
            "tanggal": tanggal,
            "page": page,
            "pagination": result,
            "data": result["items"],
            "summary": summary,
            "joki": JokiRepository.get_active(),
            "kloter": KloterRepository.get_active(),
        },
    )


# ==========================================================
# ADD
# ==========================================================

@router.post("/add")
def add(
    tanggal: str = Form(...),
    joki_id: int = Form(...),
    kloter_id: int = Form(...),
    jumlah_judul: int = Form(...),
    keterangan: str = Form(""),
):
    validate_tanggal(tanggal)
    
    if jumlah_judul <= 0:
        raise HTTPException(400, "Jumlah judul harus lebih dari 0.")
    
    if joki_id <= 0:
        raise HTTPException(400, "Joki harus dipilih.")
    
    if kloter_id <= 0:
        raise HTTPException(400, "Kloter harus dipilih.")

    log.info(f"[CATATAN] tambah: joki_id={joki_id}, kloter_id={kloter_id}, jumlah={jumlah_judul}")

    CatatanRepository.create(
        tanggal=tanggal,
        joki_id=joki_id,
        kloter_id=kloter_id,
        jumlah_judul=jumlah_judul,
        keterangan=keterangan,
    )

    log.info(f"[CATATAN] berhasil tambah untuk tanggal {tanggal}")

    return RedirectResponse(
        url=f"/catatan?tanggal={tanggal}&success=1",
        status_code=303,
    )


# ==========================================================
# EDIT FORM
# ==========================================================

@router.get("/edit/{catatan_id}", response_class=HTMLResponse)
def edit(
    request: Request,
    catatan_id: int,
):
    item = CatatanRepository.get_by_id(catatan_id)
    if item is None:
        raise HTTPException(404, "Catatan tidak ditemukan.")

    return templates.TemplateResponse(
        "catatan/form.html",
        {
            "request": request,
            "title": "Edit Catatan",
            "item": item,
            "joki": JokiRepository.get_active(),
            "kloter": KloterRepository.get_active(),
        },
    )


# ==========================================================
# UPDATE
# ==========================================================

@router.post("/edit/{catatan_id}")
def update(
    catatan_id: int,
    tanggal: str = Form(...),
    joki_id: int = Form(...),
    kloter_id: int = Form(...),
    jumlah_judul: int = Form(...),
    keterangan: str = Form(""),
):
    item = CatatanRepository.get_by_id(catatan_id)
    if item is None:
        raise HTTPException(404, "Catatan tidak ditemukan.")
    
    validate_tanggal(tanggal)
    
    if jumlah_judul <= 0:
        raise HTTPException(400, "Jumlah judul harus lebih dari 0.")
    
    if joki_id <= 0:
        raise HTTPException(400, "Joki harus dipilih.")
    
    if kloter_id <= 0:
        raise HTTPException(400, "Kloter harus dipilih.")

    log.info(f"[CATATAN] update id={catatan_id}")

    CatatanRepository.update(
        catatan_id=catatan_id,
        tanggal=tanggal,
        joki_id=joki_id,
        kloter_id=kloter_id,
        jumlah_judul=jumlah_judul,
        keterangan=keterangan,
    )

    log.info(f"[CATATAN] berhasil update id={catatan_id}")

    return RedirectResponse(
        url=f"/catatan?tanggal={tanggal}&success=1",
        status_code=303,
    )


# ==========================================================
# DELETE
# ==========================================================

@router.post("/delete/{catatan_id}")
def delete(catatan_id: int):
    item = CatatanRepository.get_by_id(catatan_id)
    if item is None:
        raise HTTPException(404, "Catatan tidak ditemukan.")

    log.info(f"[CATATAN] delete id={catatan_id}")

    CatatanRepository.delete(catatan_id)

    log.info(f"[CATATAN] berhasil delete id={catatan_id}")

    return RedirectResponse(
        url=f"/catatan?tanggal={item['tanggal']}&deleted=1",
        status_code=303,
    )


# ==========================================================
# BULK DELETE
# ==========================================================

@router.post("/bulk-delete")
def bulk_delete(ids: str = Form(...)):
    """Hapus multiple catatan sekaligus."""
    if not ids:
        raise HTTPException(400, "IDs tidak boleh kosong")
    
    id_list = [int(i) for i in ids.split(",") if i.isdigit()]
    if not id_list:
        raise HTTPException(400, "IDs tidak valid")
    
    # Ambil tanggal pertama untuk redirect
    first_item = CatatanRepository.get_by_id(id_list[0])
    
    deleted = 0
    for catatan_id in id_list:
        try:
            CatatanRepository.delete(catatan_id)
            deleted += 1
        except Exception as e:
            log.error(f"[CATATAN] gagal delete id={catatan_id}: {str(e)}")
    
    log.info(f"[CATATAN] bulk delete: {deleted} catatan dihapus")
    
    tanggal = first_item["tanggal"] if first_item else date.today().isoformat()
    
    return RedirectResponse(
        url=f"/catatan?tanggal={tanggal}&deleted={deleted}",
        status_code=303,
    )


# ==========================================================
# EXPORT CSV
# ==========================================================

@router.get("/export")
def export_csv(tanggal: str | None = None):
    """Export catatan ke CSV."""
    if tanggal is None:
        tanggal = date.today().isoformat()
    
    validate_tanggal(tanggal)
    
    result = CatatanRepository.get_all(tanggal=tanggal)
    data = result["items"]
    
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "ID", "Tanggal", "Joki", "Kloter", 
        "Jumlah Judul", "Harga per Judul", "Total", "Keterangan"
    ])
    
    # Data
    for item in data:
        writer.writerow([
            item["id"],
            item["tanggal"],
            item["joki_nama"],
            item["kloter_nama"],
            item["jumlah_judul"],
            item["harga_per_judul"],
            item["jumlah_judul"] * item["harga_per_judul"],
            item["keterangan"] or "",
        ])
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=catatan_{tanggal}.csv"
        },
    )


# ==========================================================
# API - GET BY DATE
# ==========================================================

@router.get("/api")
def api_get_by_date(
    tanggal: str | None = None,
    page: int = Query(1, ge=1),
):
    """API endpoint untuk mendapatkan catatan per tanggal."""
    if tanggal is None:
        tanggal = date.today().isoformat()
    
    validate_tanggal(tanggal)
    
    result = CatatanRepository.get_all(
        tanggal=tanggal,
        page=page,
        per_page=20,
    )
    
    return {
        "success": True,
        "data": result["items"],
        "pagination": {
            "page": result["page"],
            "per_page": result["per_page"],
            "total": result["total"],
            "total_pages": result["total_pages"],
        },
        "summary": RekapRepository.get_total_harian(tanggal=tanggal),
    }