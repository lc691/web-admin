from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from app.dependencies.auth import (
    get_current_joki,
)

from app.portal_joki.services.penugasan.list import (
    PortalJokiListService,
)


router = APIRouter(
    prefix="/portal-joki/penugasan",
    tags=["Portal Joki Penugasan"],
)

templates = Jinja2Templates(
    directory="app/portal_joki/templates"
)


# ==========================================================
# LIST PAGE
# ==========================================================

@router.get(
    "",
    name="portal_joki_penugasan",
)
async def penugasan_page(
    request: Request,
    user=Depends(get_current_joki),
):

    return templates.TemplateResponse(
        "portal_joki/penugasan_list.html",
        {
            "request": request,
            "title": "Penugasan",
            "user": user,
        },
    )


# ==========================================================
# DATATABLE
# ==========================================================

@router.get(
    "/data",
    name="portal_joki_penugasan_data",
)
async def penugasan_data(
    request: Request,
    user=Depends(get_current_joki),
):

    data = PortalJokiListService.by_joki(
        user["id"],
    )

    return JSONResponse(
        {
            "success": data.success,
            "message": data.message,
            "data": data.data,
        }
    )


# ==========================================================
# DETAIL
# ==========================================================

from fastapi import Form

from app.portal_joki.services.penugasan.detail import (
    PortalJokiDetailService,
)

from app.portal_joki.services.penugasan.create import (
    PortalJokiCreateService,
)


@router.get(
    "/{penugasan_id}",
    name="portal_joki_penugasan_detail",
)
async def penugasan_detail(
    request: Request,
    penugasan_id: int,
    user=Depends(get_current_joki),
):

    result = PortalJokiDetailService.execute(
        penugasan_id,
    )

    if not result.success:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": result.message,
            },
        )

    return templates.TemplateResponse(
        "portal_joki/penugasan_detail.html",
        {
            "request": request,
            "title": "Detail Penugasan",
            "user": user,
            "penugasan": result.data,
        },
    )


# ==========================================================
# CREATE PAGE
# ==========================================================

@router.get(
    "/create",
    name="portal_joki_penugasan_create",
)
async def create_page(
    request: Request,
    user=Depends(get_current_joki),
):

    return templates.TemplateResponse(
        "portal_joki/penugasan_form.html",
        {
            "request": request,
            "title": "Tambah Penugasan",
            "user": user,
            "mode": "create",
        },
    )


# ==========================================================
# CREATE
# ==========================================================

@router.post(
    "/create",
    name="portal_joki_penugasan_store",
)
async def create(
    tanggal: str = Form(...),
    joki_id: int = Form(...),
    kloter_id: int = Form(...),

    absen_awal: int = Form(...),
    absen_akhir: int = Form(...),

    target_judul: int = Form(...),

    instruksi: str = Form(...),

    deadline: str | None = Form(None),

    request: Request = None,
    user=Depends(get_current_joki),
):

    result = PortalJokiCreateService.execute(
        tanggal=tanggal,
        joki_id=joki_id,
        kloter_id=kloter_id,

        absen_awal=absen_awal,
        absen_akhir=absen_akhir,

        target_judul=target_judul,

        instruksi=instruksi,

        deadline=deadline,

        created_by=user["kode"],
    )

    if not result.success:

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": result.message,
            },
        )

    return JSONResponse(
        {
            "success": True,
            "message": result.message,
        }
    )