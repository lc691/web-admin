from datetime import date

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.templates import templates

from .repositories.laporan.rekap_repo import RekapRepository


router = APIRouter(
    prefix="/rekap",
    tags=["Rekap"],
)


# ==========================================================
# REKAP HARIAN
# ==========================================================

@router.get(
    "",
    response_class=HTMLResponse,
)
def index(
    request: Request,
    tanggal: str | None = None,
):

    if tanggal is None:

        tanggal = date.today().isoformat()

    summary = RekapRepository.get_total_harian(
        tanggal=tanggal,
    )

    rekap = RekapRepository.get_rekap_joki(
        tanggal=tanggal,
    )

    return templates.TemplateResponse(
        "rekap/index.html",
        {
            "request": request,
            "title": "Rekap Harian",
            "tanggal": tanggal,
            "summary": summary,
            "data": rekap,
        },
    )


# ==========================================================
# REKAP JOKI
# ==========================================================

@router.get(
    "/joki",
    response_class=HTMLResponse,
)
def rekap_joki(

    request: Request,

    tanggal: str | None = None,

):

    if tanggal is None:

        tanggal = date.today().isoformat()

    return templates.TemplateResponse(

        "rekap/joki.html",

        {

            "request": request,

            "title": "Rekap Joki",

            "tanggal": tanggal,

            "summary": RekapRepository.get_total_harian(
                tanggal=tanggal,
            ),

            "data": RekapRepository.get_rekap_joki(
                tanggal=tanggal,
            ),

        },

    )


# ==========================================================
# REKAP KLOTER
# ==========================================================

@router.get(
    "/kloter",
    response_class=HTMLResponse,
)
def rekap_kloter(

    request: Request,

    tanggal: str | None = None,

):

    if tanggal is None:

        tanggal = date.today().isoformat()

    return templates.TemplateResponse(

        "rekap/kloter.html",

        {

            "request": request,

            "title": "Rekap Kloter",

            "tanggal": tanggal,

            "summary": RekapRepository.get_total_harian(
                tanggal=tanggal,
            ),

            "data": RekapRepository.get_rekap_kloter(
                tanggal=tanggal,
            ),

        },

    )