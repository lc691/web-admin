from datetime import date

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.templates import templates

from .repositories.laporan.rekap_repo import RekapRepository


router = APIRouter(
    prefix="/laporan",
    tags=["Laporan"],
)


# ==========================================================
# LAPORAN
# ==========================================================

@router.get(
    "",
    response_class=HTMLResponse,
)
def index(

    request: Request,

    periode: str = "harian",

    tanggal: str | None = None,

    bulan: int | None = None,

    tahun: int | None = None,

):

    today = date.today()

    if tanggal is None:

        tanggal = today.isoformat()

    if bulan is None:

        bulan = today.month

    if tahun is None:

        tahun = today.year

    # ------------------------------------------
    # Summary
    # ------------------------------------------

    if periode == "harian":

        summary = RekapRepository.get_total_harian(
            tanggal=tanggal,
        )

        data = RekapRepository.get_rekap_joki(
            tanggal=tanggal,
        )

    elif periode == "bulanan":

        summary = RekapRepository.get_total_bulanan(
            bulan=bulan,
            tahun=tahun,
        )

        data = RekapRepository.get_rekap_bulanan(
            bulan=bulan,
            tahun=tahun,
        )

    else:

        summary = RekapRepository.get_total_tahunan(
            tahun=tahun,
        )

        data = RekapRepository.get_rekap_tahunan(
            tahun=tahun,
        )

    return templates.TemplateResponse(
        "laporan/index.html",
        {
            "request": request,
            "title": "Laporan",

            "periode": periode,
            "tanggal": tanggal,
            "bulan": bulan,
            "tahun": tahun,
            "current_year": date.today().year,

            "summary": summary,
            "data": data,

            "rekap_kloter": RekapRepository.get_rekap_kloter(
                periode=periode,
                tanggal=tanggal,
                bulan=bulan,
                tahun=tahun,
            ),
        },
    )

# ==========================================================
# DETAIL JOKI
# ==========================================================

@router.get(
    "/joki/{joki_id}",
    response_class=HTMLResponse,
)
def detail_joki(

    request: Request,

    joki_id: int,

    periode: str = "harian",

    tanggal: str | None = None,

    bulan: int | None = None,

    tahun: int | None = None,

):

    today = date.today()

    if tanggal is None:

        tanggal = today.isoformat()

    if bulan is None:

        bulan = today.month

    if tahun is None:

        tahun = today.year

    if periode == "harian":

        data = RekapRepository.get_detail_joki(

            joki_id=joki_id,

            periode="harian",

            tanggal=tanggal,

        )

    elif periode == "bulanan":

        data = RekapRepository.get_detail_joki(

            joki_id=joki_id,

            periode="bulanan",

            bulan=bulan,

            tahun=tahun,

        )

    else:

        data = RekapRepository.get_detail_joki(

            joki_id=joki_id,

            periode="tahunan",

            tahun=tahun,

        )

    if not data:

        raise HTTPException(

            status_code=404,

            detail="Data joki tidak ditemukan.",

        )

    return templates.TemplateResponse(

        "laporan/detail_joki.html",

        {

            "request": request,

            "title": "Detail Joki",

            "periode": periode,

            "tanggal": tanggal,

            "bulan": bulan,

            "tahun": tahun,

            "item": data[0],

            "data": data,

        },

    )

# ==========================================================
# DETAIL KLOTER
# ==========================================================

@router.get(
    "/kloter/{kloter_id}",
    response_class=HTMLResponse,
)
def detail_kloter(

    request: Request,

    kloter_id: int,

    periode: str = "harian",

    tanggal: str | None = None,

    bulan: int | None = None,

    tahun: int | None = None,

):

    today = date.today()

    if tanggal is None:

        tanggal = today.isoformat()

    if bulan is None:

        bulan = today.month

    if tahun is None:

        tahun = today.year

    if periode == "harian":

        data = RekapRepository.get_detail_kloter(

            kloter_id=kloter_id,

            periode="harian",

            tanggal=tanggal,

        )

    elif periode == "bulanan":

        data = RekapRepository.get_detail_kloter(

            kloter_id=kloter_id,

            periode="bulanan",

            bulan=bulan,

            tahun=tahun,

        )

    else:

        data = RekapRepository.get_detail_kloter(

            kloter_id=kloter_id,

            periode="tahunan",

            tahun=tahun,

        )

    if not data:

        raise HTTPException(

            status_code=404,

            detail="Data kloter tidak ditemukan.",

        )

    return templates.TemplateResponse(

        "laporan/detail_kloter.html",

        {

            "request": request,

            "title": "Detail Kloter",

            "periode": periode,

            "tanggal": tanggal,

            "bulan": bulan,

            "tahun": tahun,

            "item": data[0],

            "data": data,

        },

    )

# from datetime import date

# from fastapi import APIRouter, Request
# from fastapi.responses import HTMLResponse

# from app.templates import templates

# from .repositories.laporan.rekap_repo import RekapRepository


# router = APIRouter(
#     prefix="/laporan",
#     tags=["Laporan"],
# )


# # ==========================================================
# # LAPORAN
# # ==========================================================

# @router.get(
#     "",
#     response_class=HTMLResponse,
# )
# def index(

#     request: Request,

#     periode: str = "harian",

#     tanggal: str | None = None,

#     bulan: int | None = None,

#     tahun: int | None = None,

# ):

#     today = date.today()

#     if tanggal is None:

#         tanggal = today.isoformat()

#     if bulan is None:

#         bulan = today.month

#     if tahun is None:

#         tahun = today.year

#     # ------------------------------------------
#     # Summary
#     # ------------------------------------------

#     if periode == "harian":

#         summary = RekapRepository.get_total_harian(
#             tanggal=tanggal,
#         )

#         data = RekapRepository.get_rekap_joki(
#             tanggal=tanggal,
#         )

#     elif periode == "bulanan":

#         summary = RekapRepository.get_total_bulanan(
#             bulan=bulan,
#             tahun=tahun,
#         )

#         data = RekapRepository.get_rekap_bulanan(
#             bulan=bulan,
#             tahun=tahun,
#         )

#     else:

#         summary = RekapRepository.get_total_tahunan(
#             tahun=tahun,
#         )

#         data = RekapRepository.get_rekap_tahunan(
#             tahun=tahun,
#         )

#     return templates.TemplateResponse(
#         "laporan/index.html",
#         {
#             "request": request,
#             "title": "Laporan",

#             "periode": periode,
#             "tanggal": tanggal,
#             "bulan": bulan,
#             "tahun": tahun,
#             "current_year": date.today().year,

#             "summary": summary,
#             "data": data,

#             "rekap_kloter": RekapRepository.get_rekap_kloter(
#                 periode=periode,
#                 tanggal=tanggal,
#                 bulan=bulan,
#                 tahun=tahun,
#             ),
#         },
#     )

# # ==========================================================
# # DETAIL JOKI
# # ==========================================================

# @router.get(
#     "/joki/{joki_id}",
#     response_class=HTMLResponse,
# )
# def detail_joki(

#     request: Request,

#     joki_id: int,

#     periode: str = "harian",

#     tanggal: str | None = None,

#     bulan: int | None = None,

#     tahun: int | None = None,

# ):

#     today = date.today()

#     if tanggal is None:

#         tanggal = today.isoformat()

#     if bulan is None:

#         bulan = today.month

#     if tahun is None:

#         tahun = today.year

#     if periode == "harian":

#         data = RekapRepository.get_detail_joki(

#             joki_id=joki_id,

#             periode="harian",

#             tanggal=tanggal,

#         )

#     elif periode == "bulanan":

#         data = RekapRepository.get_detail_joki(

#             joki_id=joki_id,

#             periode="bulanan",

#             bulan=bulan,

#             tahun=tahun,

#         )

#     else:

#         data = RekapRepository.get_detail_joki(

#             joki_id=joki_id,

#             periode="tahunan",

#             tahun=tahun,

#         )

#     if not data:

#         raise HTTPException(

#             status_code=404,

#             detail="Data joki tidak ditemukan.",

#         )

#     return templates.TemplateResponse(

#         "laporan/detail_joki.html",

#         {

#             "request": request,

#             "title": "Detail Joki",

#             "periode": periode,

#             "tanggal": tanggal,

#             "bulan": bulan,

#             "tahun": tahun,

#             "item": data[0],

#             "data": data,

#         },

#     )

# # ==========================================================
# # DETAIL KLOTER
# # ==========================================================

# @router.get(
#     "/kloter/{kloter_id}",
#     response_class=HTMLResponse,
# )
# def detail_kloter(

#     request: Request,

#     kloter_id: int,

#     periode: str = "harian",

#     tanggal: str | None = None,

#     bulan: int | None = None,

#     tahun: int | None = None,

# ):

#     today = date.today()

#     if tanggal is None:

#         tanggal = today.isoformat()

#     if bulan is None:

#         bulan = today.month

#     if tahun is None:

#         tahun = today.year

#     if periode == "harian":

#         data = RekapRepository.get_detail_kloter(

#             kloter_id=kloter_id,

#             periode="harian",

#             tanggal=tanggal,

#         )

#     elif periode == "bulanan":

#         data = RekapRepository.get_detail_kloter(

#             kloter_id=kloter_id,

#             periode="bulanan",

#             bulan=bulan,

#             tahun=tahun,

#         )

#     else:

#         data = RekapRepository.get_detail_kloter(

#             kloter_id=kloter_id,

#             periode="tahunan",

#             tahun=tahun,

#         )

#     if not data:

#         raise HTTPException(

#             status_code=404,

#             detail="Data kloter tidak ditemukan.",

#         )

#     return templates.TemplateResponse(

#         "laporan/detail_kloter.html",

#         {

#             "request": request,

#             "title": "Detail Kloter",

#             "periode": periode,

#             "tanggal": tanggal,

#             "bulan": bulan,

#             "tahun": tahun,

#             "item": data[0],

#             "data": data,

#         },

#     )