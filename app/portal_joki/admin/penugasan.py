"""
Portal Joki - Admin Penugasan Routes

Routes untuk mengelola penugasan portal joki.
"""

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import JSONResponse, RedirectResponse
from app.templates import templates

from app.dependencies.auth import require_admin
from app.portal_joki.services.penugasan.list import (
    PortalJokiListService,
)
from app.portal_joki.services.penugasan.create import (
    PortalJokiCreateService,
)
from app.portal_joki.services.penugasan.update import (
    PortalJokiUpdateService,
)
from app.portal_joki.services.penugasan.delete import (
    PortalJokiDeleteService,
)
from app.portal_joki.services.penugasan.detail import (
    PortalJokiDetailService,
)
from app.portal_joki.services.penugasan.progress import (
    PortalJokiProgressService,
)
from app.portal_joki.repositories.auth.auth_repo import (
    PortalJokiAuthRepository,
)
from app.portal_joki.repositories.penugasan.kloter_repo import (
    PortalJokiKloterRepository,
)
from app.utils.logger import log

# ==========================================================
# ROUTER & TEMPLATES
# ==========================================================
router = APIRouter(
    prefix="/admin/portal-joki/penugasan",
    tags=["Portal Joki Admin"],
)


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================
def get_status_label(status: int) -> str:
    """Get status label."""
    status_map = {0: "Pending", 1: "Upload", 2: "Revisi", 3: "Selesai"}
    return status_map.get(status, "Unknown")

def get_status_color(status: int) -> str:
    """Get status color."""
    color_map = {0: "warning", 1: "info", 2: "danger", 3: "success"}
    return color_map.get(status, "secondary")


# ==========================================================
# PENUGASAN LIST PAGE
# ==========================================================
@router.get(
    "/",
    name="portal_joki_admin_penugasan",
)
async def penugasan_list(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[int] = Query(None),
    joki_id: Optional[int] = Query(None),
    tanggal: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    """
    Admin penugasan list page.
    """
    log.info(f"Admin penugasan list: page={page}, limit={limit}, status={status}")

    try:
        admin = require_admin(request)

        offset = (page - 1) * limit

        # Parse date if provided
        start_date = None
        end_date = None
        if tanggal:
            try:
                tanggal_date = datetime.strptime(tanggal, "%Y-%m-%d").date()
                start_date = tanggal_date
                end_date = tanggal_date
            except ValueError:
                pass

        # Get data
        result = PortalJokiListService.all(
            limit=limit,
            offset=offset,
            status=status,
            joki_id=joki_id,
            start_date=start_date,
            end_date=end_date,
        )

        # Get joki list for filter
        joki_list = PortalJokiAuthRepository.get_active()

        # Calculate pagination
        total_pages = (result.total + limit - 1) // limit if result.total > 0 else 1

        return templates.TemplateResponse(
            "portal_joki/admin/penugasan_list.html",
            {
                "request": request,
                "title": "Daftar Penugasan",
                "admin": admin,
                "penugasan": result.data,
                "total": result.total,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "status": status,
                "joki_id": joki_id,
                "tanggal": tanggal,
                "joki_list": joki_list,
                "search": search,
                "get_status_label": get_status_label,
                "get_status_color": get_status_color,
                "generated_at": datetime.now(),
            },
        )

    except Exception as e:
        log.error(f"Failed to load penugasan list: {e}")
        return templates.TemplateResponse(
            "portal_joki/admin/penugasan_list.html",
            {
                "request": request,
                "title": "Daftar Penugasan",
                "error": str(e),
                "penugasan": [],
                "total": 0,
                "page": 1,
                "limit": 20,
                "total_pages": 1,
                "joki_list": [],
                "generated_at": datetime.now(),
            },
        )

# ==========================================================
# CREATE PENUGASAN PAGE
# ==========================================================
@router.get(
    "/create",
    name="portal_joki_admin_penugasan_create",
)
async def penugasan_create_page(
    request: Request,
):
    """
    Admin create penugasan page.
    """
    log.info("Admin penugasan create page")

    try:
        admin = require_admin(request)

        # Get active joki and kloter for dropdown
        joki_list = PortalJokiAuthRepository.get_active()
        kloter_list = PortalJokiKloterRepository.get_active()

        return templates.TemplateResponse(
            "portal_joki/admin/penugasan_form.html",
            {
                "request": request,
                "title": "Tambah Penugasan",
                "admin": admin,
                "mode": "create",
                "joki_list": joki_list,
                "kloter_list": kloter_list,
                "generated_at": datetime.now(),
            },
        )

    except Exception as e:
        log.error(f"Failed to load create penugasan page: {e}")
        return RedirectResponse(
            url="/admin/portal-joki/penugasan?error=" + str(e),
            status_code=303,
        )

# ==========================================================
# PENUGASAN DETAIL PAGE
# ==========================================================
@router.get(
    "/{penugasan_id}",
    name="portal_joki_admin_penugasan_detail",
)
async def penugasan_detail(
    request: Request,
    penugasan_id: int,
):
    """
    Admin penugasan detail page.
    """
    log.info(f"Admin penugasan detail: ID={penugasan_id}")

    try:
        admin = require_admin(request)

        result = PortalJokiDetailService.execute(
            penugasan_id=penugasan_id,
            include_related=True,
        )

        if not result.success:
            return templates.TemplateResponse(
                "portal_joki/admin/penugasan_detail.html",
                {
                    "request": request,
                    "title": "Detail Penugasan",
                    "error": result.message,
                    "admin": admin,
                    "penugasan": None,
                    "related": {},
                    "get_status_label": get_status_label,
                    "get_status_color": get_status_color,
                },
            )

        return templates.TemplateResponse(
            "portal_joki/admin/penugasan_detail.html",
            {
                "request": request,
                "title": "Detail Penugasan",
                "admin": admin,
                "penugasan": result.data,
                "related": result.related,
                "get_status_label": get_status_label,
                "get_status_color": get_status_color,
                "generated_at": datetime.now(),
            },
        )

    except Exception as e:
        log.error(f"Failed to load penugasan detail: {e}")
        return templates.TemplateResponse(
            "portal_joki/admin/penugasan_detail.html",
            {
                "request": request,
                "title": "Detail Penugasan",
                "error": str(e),
                "admin": admin,
                "penugasan": None,
                "related": {},
                "get_status_label": get_status_label,
                "get_status_color": get_status_color,
            },
        )
# ==========================================================
# EDIT PENUGASAN PAGE
# ==========================================================
@router.get(
    "/{penugasan_id}/edit",
    name="portal_joki_admin_penugasan_edit",
)
async def penugasan_edit_page(
    request: Request,
    penugasan_id: int,
):
    """
    Admin edit penugasan page.
    """
    log.info(f"Admin penugasan edit page: ID={penugasan_id}")

    try:
        admin = require_admin(request)

        # Get penugasan detail
        result = PortalJokiDetailService.execute(
            penugasan_id=penugasan_id,
            include_related=False,
        )

        if not result.success:
            return RedirectResponse(
                url="/admin/portal-joki/penugasan?error=" + result.message,
                status_code=303,
            )

        # Get active joki and kloter for dropdown
        joki_list = PortalJokiAuthRepository.get_active()
        kloter_list = PortalJokiKloterRepository.get_active()

        return templates.TemplateResponse(
            "portal_joki/admin/penugasan_form.html",
            {
                "request": request,
                "title": "Edit Penugasan",
                "admin": admin,
                "mode": "edit",
                "penugasan": result.data,
                "joki_list": joki_list,
                "kloter_list": kloter_list,
                "generated_at": datetime.now(),
            },
        )

    except Exception as e:
        log.error(f"Failed to load edit penugasan page: {e}")
        return RedirectResponse(
            url="/admin/portal-joki/penugasan?error=" + str(e),
            status_code=303,
        )


# ==========================================================
# CREATE PENUGASAN (POST)
# ==========================================================
@router.post(
    "/create",
    name="portal_joki_admin_penugasan_create_post",
)
async def penugasan_create(
    request: Request,
    tanggal: str = Form(...),
    joki_id: int = Form(...),
    kloter_id: int = Form(...),
    absen_awal: int = Form(...),
    absen_akhir: int = Form(...),
    target_judul: int = Form(...),
    instruksi: str = Form(...),
    deadline: Optional[str] = Form(None),
):
    """
    Create penugasan.
    """
    log.info(f"Create penugasan: joki_id={joki_id}, tanggal={tanggal}")

    try:
        admin = require_admin(request)

        # Parse date
        try:
            tanggal_date = datetime.strptime(tanggal, "%Y-%m-%d").date()
        except ValueError:
            return RedirectResponse(
                url="/admin/portal-joki/penugasan/create?error=Format tanggal tidak valid",
                status_code=303,
            )

        # Parse deadline
        deadline_date = None
        if deadline:
            try:
                deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
            except ValueError:
                pass

        # Create
        result = PortalJokiCreateService.execute(
            tanggal=tanggal_date,
            joki_id=joki_id,
            kloter_id=kloter_id,
            absen_awal=absen_awal,
            absen_akhir=absen_akhir,
            target_judul=target_judul,
            instruksi=instruksi,
            deadline=deadline_date,
            created_by=admin.get("username", "admin"),
        )

        if result.success:
            return RedirectResponse(
                url=f"/admin/portal-joki/penugasan/{result.penugasan_id}?success=Penugasan berhasil dibuat",
                status_code=303,
            )
        else:
            return RedirectResponse(
                url=f"/admin/portal-joki/penugasan/create?error={result.message}",
                status_code=303,
            )

    except Exception as e:
        log.error(f"Failed to create penugasan: {e}")
        return RedirectResponse(
            url=f"/admin/portal-joki/penugasan/create?error={str(e)}",
            status_code=303,
        )


# ==========================================================
# UPDATE PENUGASAN (POST)
# ==========================================================
@router.post(
    "/{penugasan_id}/update",
    name="portal_joki_admin_penugasan_update_post",
)
async def penugasan_update(
    request: Request,
    penugasan_id: int,
    tanggal: str = Form(...),
    joki_id: int = Form(...),
    kloter_id: int = Form(...),
    absen_awal: int = Form(...),
    absen_akhir: int = Form(...),
    target_judul: int = Form(...),
    instruksi: str = Form(...),
    deadline: Optional[str] = Form(None),
):
    """
    Update penugasan.
    """
    log.info(f"Update penugasan: ID={penugasan_id}")

    try:
        admin = require_admin(request)

        # Parse date
        try:
            tanggal_date = datetime.strptime(tanggal, "%Y-%m-%d").date()
        except ValueError:
            return RedirectResponse(
                url=f"/admin/portal-joki/penugasan/{penugasan_id}/edit?error=Format tanggal tidak valid",
                status_code=303,
            )

        # Parse deadline
        deadline_date = None
        if deadline:
            try:
                deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date()
            except ValueError:
                pass

        # Update
        result = PortalJokiUpdateService.execute(
            penugasan_id=penugasan_id,
            tanggal=tanggal_date,
            joki_id=joki_id,
            kloter_id=kloter_id,
            absen_awal=absen_awal,
            absen_akhir=absen_akhir,
            target_judul=target_judul,
            instruksi=instruksi,
            deadline=deadline_date,
            updated_by=admin.get("username", "admin"),
        )

        if result.success:
            return RedirectResponse(
                url=f"/admin/portal-joki/penugasan/{penugasan_id}?success=Penugasan berhasil diperbarui",
                status_code=303,
            )
        else:
            return RedirectResponse(
                url=f"/admin/portal-joki/penugasan/{penugasan_id}/edit?error={result.message}",
                status_code=303,
            )

    except Exception as e:
        log.error(f"Failed to update penugasan: {e}")
        return RedirectResponse(
            url=f"/admin/portal-joki/penugasan/{penugasan_id}/edit?error={str(e)}",
            status_code=303,
        )


# ==========================================================
# DELETE PENUGASAN (POST)
# ==========================================================
@router.post(
    "/{penugasan_id}/delete",
    name="portal_joki_admin_penugasan_delete_post",
)
async def penugasan_delete(
    request: Request,
    penugasan_id: int,
):
    """
    Delete penugasan.
    """
    log.info(f"Delete penugasan: ID={penugasan_id}")

    try:
        require_admin(request)

        result = PortalJokiDeleteService.execute(
            penugasan_id=penugasan_id,
            force=True,
            delete_related=True,
        )

        if result.success:
            return RedirectResponse(
                url="/admin/portal-joki/penugasan?success=Penugasan berhasil dihapus",
                status_code=303,
            )
        else:
            return RedirectResponse(
                url=f"/admin/portal-joki/penugasan/{penugasan_id}?error={result.message}",
                status_code=303,
            )

    except Exception as e:
        log.error(f"Failed to delete penugasan: {e}")
        return RedirectResponse(
            url=f"/admin/portal-joki/penugasan/{penugasan_id}?error={str(e)}",
            status_code=303,
        )


# ==========================================================
# UPDATE STATUS (AJAX)
# ==========================================================
@router.post(
    "/{penugasan_id}/status",
    name="portal_joki_admin_penugasan_status",
)
async def penugasan_update_status(
    request: Request,
    penugasan_id: int,
    status: int = Form(...),
):
    """
    Update status penugasan (AJAX).
    """
    log.info(f"Update status penugasan: ID={penugasan_id}, status={status}")

    try:
        admin = require_admin(request)

        result = PortalJokiProgressService.execute(
            penugasan_id=penugasan_id,
            status=status,
            updated_by=admin.get("username", "admin"),
            force=True,
        )

        if result.success:
            return JSONResponse({
                "success": True,
                "message": result.message,
                "status": result.status,
                "status_label": get_status_label(result.status),
                "status_color": get_status_color(result.status),
            })
        else:
            return JSONResponse({
                "success": False,
                "error": result.message,
            }, status_code=400)

    except Exception as e:
        log.error(f"Failed to update status: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)