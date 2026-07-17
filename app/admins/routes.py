import logging
from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_302_FOUND

from app.templates import templates
from app.core.database import get_dict_cursor
from .services import (
    activate_admin,
    count_admins,
    create_admin,
    deactivate_admin,
    delete_admin,
    get_admin,
    list_admins,
    update_admin,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admins", tags=["Admin Management"])


# ==========================================================
# LIST ADMINS
# ==========================================================
@router.get("/", response_class=HTMLResponse)
async def list_admins_page(
    request: Request,
    only_active: bool = Query(False, description="Only show active admins"),
):
    admins = list_admins(only_active=only_active)
    total = count_admins()
    active = count_admins(only_active=True)

    return templates.TemplateResponse(
        "admins/list.html",
        {
            "request": request,
            "admins": admins,
            "total": total,
            "active": active,
            "only_active": only_active,
            "title": "Daftar Admin",
        },
    )


# ==========================================================
# ADD ADMIN - FORM
# ==========================================================
@router.get("/add", response_class=HTMLResponse)
async def add_admin_form(request: Request):
    return templates.TemplateResponse(
        "admins/add.html",
        {"request": request, "title": "Tambah Admin Baru"},
    )


# ==========================================================
# ADD ADMIN - SUBMIT
# ==========================================================
@router.post("/add")
async def add_admin_submit(
    request: Request,
    user_id: int = Form(...),
    first_name: str = Form(...),
    username: str = Form(...),
    is_active: bool = Form(True),
):
    # Validasi
    if not first_name or not first_name.strip():
        raise HTTPException(400, "First name wajib diisi")

    if not username or not username.strip():
        raise HTTPException(400, "Username wajib diisi")

    if user_id <= 0:
        raise HTTPException(400, "User ID harus lebih dari 0")

    try:
        create_admin(
            user_id=user_id,
            first_name=first_name.strip(),
            username=username.strip(),
            is_active=is_active,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Error creating admin: {str(e)}")
        raise HTTPException(500, f"Gagal menambahkan admin: {str(e)}")

    return RedirectResponse("/admins", status_code=HTTP_302_FOUND)


# ==========================================================
# EDIT ADMIN - FORM
# ==========================================================
@router.get("/edit/{user_id}", response_class=HTMLResponse)
async def edit_admin_form(request: Request, user_id: int):
    admin = get_admin(user_id)
    if not admin:
        raise HTTPException(404, "Admin tidak ditemukan")

    return templates.TemplateResponse(
        "admins/edit.html",
        {"request": request, "admin": admin, "title": "Edit Admin"},
    )


# ==========================================================
# EDIT ADMIN - SUBMIT
# ==========================================================
@router.post("/edit/{user_id}")
async def edit_admin_submit(
    request: Request,
    user_id: int,
    first_name: str = Form(...),
    username: str = Form(...),
    is_active: bool = Form(True),
):
    # Validasi
    if not first_name or not first_name.strip():
        raise HTTPException(400, "First name wajib diisi")

    if not username or not username.strip():
        raise HTTPException(400, "Username wajib diisi")

    try:
        update_admin(
            user_id=user_id,
            first_name=first_name.strip(),
            username=username.strip(),
            is_active=is_active,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Error updating admin: {str(e)}")
        raise HTTPException(500, f"Gagal mengupdate admin: {str(e)}")

    return RedirectResponse("/admins", status_code=HTTP_302_FOUND)


# ==========================================================
# DELETE ADMIN
# ==========================================================
@router.post("/delete/{user_id}")
async def delete_admin_submit(request: Request, user_id: int):
    try:
        deleted = delete_admin(user_id)
        if not deleted:
            raise HTTPException(404, "Admin tidak ditemukan")
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        logger.error(f"Error deleting admin: {str(e)}")
        raise HTTPException(500, f"Gagal menghapus admin: {str(e)}")

    return RedirectResponse("/admins", status_code=HTTP_302_FOUND)


# ==========================================================
# TOGGLE ADMIN STATUS
# ==========================================================
@router.post("/{user_id}/toggle")
async def toggle_admin_status(request: Request, user_id: int):
    admin = get_admin(user_id)
    if not admin:
        raise HTTPException(404, "Admin tidak ditemukan")

    try:
        if admin["is_active"]:
            deactivate_admin(user_id)
        else:
            activate_admin(user_id)
    except Exception as e:
        logger.error(f"Error toggling admin status: {str(e)}")
        raise HTTPException(500, f"Gagal mengubah status admin: {str(e)}")

    return RedirectResponse("/admins", status_code=HTTP_302_FOUND)


# ==========================================================
# RETENTION DASHBOARD
# ==========================================================
@router.get("/retention", response_class=HTMLResponse)
async def retention_dashboard(request: Request):
    with get_dict_cursor() as (cursor, _):
        # Total reminder
        cursor.execute("""
            SELECT COUNT(*)
            FROM retention_log
            WHERE stage = 'strong_10d'
        """)
        total = cursor.fetchone()["count"]

        # Total converted
        cursor.execute("""
            SELECT COUNT(*)
            FROM retention_log
            WHERE stage = 'strong_10d'
            AND converted = TRUE
        """)
        converted = cursor.fetchone()["count"]

        # 14 hari terakhir
        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE converted = TRUE) AS converted
            FROM retention_log
            WHERE stage = 'strong_10d'
            AND sent_at >= NOW() - INTERVAL '14 days'
        """)
        last_14 = cursor.fetchone()

        # Adaptive distribution
        cursor.execute("""
            SELECT offset_days, COUNT(*) AS users
            FROM retention_adaptive
            GROUP BY offset_days
            ORDER BY offset_days
        """)
        adaptive = cursor.fetchall()

    rate_all = (converted / total * 100) if total else 0
    rate_14 = (last_14["converted"] / last_14["total"] * 100) if last_14["total"] else 0

    return templates.TemplateResponse(
        "admins/retention_base.html",
        {
            "request": request,
            "path": request.url.path,
            "title": "Retention Dashboard",
            "total": total,
            "converted": converted,
            "rate_all": round(rate_all, 2),
            "rate_14": round(rate_14, 2),
            "adaptive": adaptive,
        },
    )


# ==========================================================
# API ENDPOINTS (JSON)
# ==========================================================
@router.get("/api")
async def list_admins_api(
    only_active: bool = Query(False),
):
    admins = list_admins(only_active=only_active)
    return {
        "success": True,
        "data": admins,
        "total": len(admins),
        "filters": {"only_active": only_active},
    }


@router.get("/api/{user_id}")
async def get_admin_api(user_id: int):
    admin = get_admin(user_id)
    if not admin:
        raise HTTPException(404, "Admin tidak ditemukan")
    return {"success": True, "data": admin}


@router.get("/api/stats")
async def get_admin_stats():
    return {
        "success": True,
        "data": {
            "total": count_admins(),
            "active": count_admins(only_active=True),
            "inactive": count_admins(only_active=False) - count_admins(only_active=True),
        },
    }