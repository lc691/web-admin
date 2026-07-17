"""
Portal Joki - Admin Holiday Routes

Routes untuk mengelola hari libur portal joki.
"""

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import JSONResponse, RedirectResponse
from app.templates import templates

from app.dependencies.auth import require_admin
from app.portal_joki.services.calendar.holiday_service import (
    PortalJokiHolidayService,
)
from app.utils.logger import log

# ==========================================================
# ROUTER & TEMPLATES
# ==========================================================
router = APIRouter(
    prefix="/admin/portal-joki/holiday",
    tags=["Portal Joki Admin"],
)

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================
def get_month_name(month: int) -> str:
    """Get month name in Indonesian."""
    months = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    return months[month - 1] if 1 <= month <= 12 else ""


# ==========================================================
# HOLIDAY LIST PAGE
# ==========================================================
@router.get(
    "/",
    name="portal_joki_admin_holiday",
)
async def holiday_list(
    request: Request,
    year: Optional[int] = Query(None, description="Tahun"),
    month: Optional[int] = Query(None, description="Bulan"),
):
    """
    Admin holiday list page.
    """
    log.info(f"Admin holiday list: year={year}, month={month}")
    
    try:
        admin = require_admin(request)
        
        # Get current date
        now = date.today()
        
        if year is None:
            year = now.year
        if month is None:
            month = now.month
        
        # Validate month
        if month < 1 or month > 12:
            month = now.month
            year = now.year
        
        # Get holidays
        result = PortalJokiHolidayService.month(
            tahun=year,
            bulan=month,
        )
        
        # Extract data safely
        holidays = []
        if result.success and result.data:
            if isinstance(result.data, dict):
                holidays = result.data.get("data", [])
            elif isinstance(result.data, list):
                holidays = result.data
            else:
                holidays = []
        
        # Get all holidays for year (for calendar view)
        all_result = PortalJokiHolidayService.all(year=year)
        all_holidays = []
        if all_result.success and all_result.data:
            if isinstance(all_result.data, dict):
                all_holidays = all_result.data.get("data", [])
            elif isinstance(all_result.data, list):
                all_holidays = all_result.data
        
        month_name = get_month_name(month)
        
        return templates.TemplateResponse(
            "portal_joki/admin/holiday.html",
            {
                "request": request,
                "title": "Kelola Hari Libur",
                "admin": admin,
                "year": year,
                "month": month,
                "month_name": month_name,
                "holidays": holidays,
                "all_holidays": all_holidays,
                "generated_at": datetime.now(),
            },
        )
        
    except Exception as e:
        log.error(f"Failed to load holiday list: {e}")
        return templates.TemplateResponse(
            "portal_joki/admin/holiday.html",
            {
                "request": request,
                "title": "Kelola Hari Libur",
                "error": str(e),
                "year": date.today().year,
                "month": date.today().month,
                "month_name": get_month_name(date.today().month),
                "holidays": [],
                "all_holidays": [],
                "generated_at": datetime.now(),
            },
        )


# ==========================================================
# CREATE HOLIDAY (AJAX)
# ==========================================================
@router.post(
    "/create",
    name="portal_joki_admin_holiday_create",
)
async def holiday_create(
    request: Request,
    tanggal: str = Form(...),
    nama: str = Form(...),
    keterangan: Optional[str] = Form(None),
):
    """
    Create new holiday.
    """
    log.info(f"Create holiday: tanggal={tanggal}, nama={nama}")
    
    try:
        require_admin(request)
        
        # Parse date
        try:
            tanggal_date = datetime.strptime(tanggal, "%Y-%m-%d").date()
        except ValueError:
            return JSONResponse({
                "success": False,
                "error": "Format tanggal tidak valid. Gunakan YYYY-MM-DD.",
            }, status_code=400)
        
        # Validate
        if not nama or not nama.strip():
            return JSONResponse({
                "success": False,
                "error": "Nama hari libur wajib diisi.",
            }, status_code=400)
        
        # Create holiday
        result = PortalJokiHolidayService.create(
            tanggal=tanggal_date,
            nama=nama.strip(),
            keterangan=keterangan.strip() if keterangan else None,
        )
        
        if result.success:
            log.info(f"Holiday created: {result.data}")
            return JSONResponse({
                "success": True,
                "message": result.message,
                "data": result.data,
            })
        else:
            return JSONResponse({
                "success": False,
                "error": result.message,
            }, status_code=400)
        
    except Exception as e:
        log.error(f"Failed to create holiday: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# UPDATE HOLIDAY (AJAX)
# ==========================================================
@router.post(
    "/update",
    name="portal_joki_admin_holiday_update",
)
async def holiday_update(
    request: Request,
    holiday_id: int = Form(...),
    tanggal: str = Form(...),
    nama: str = Form(...),
    keterangan: Optional[str] = Form(None),
):
    """
    Update holiday.
    """
    log.info(f"Update holiday: ID={holiday_id}, tanggal={tanggal}, nama={nama}")
    
    try:
        require_admin(request)
        
        # Parse date
        try:
            tanggal_date = datetime.strptime(tanggal, "%Y-%m-%d").date()
        except ValueError:
            return JSONResponse({
                "success": False,
                "error": "Format tanggal tidak valid. Gunakan YYYY-MM-DD.",
            }, status_code=400)
        
        # Validate
        if not nama or not nama.strip():
            return JSONResponse({
                "success": False,
                "error": "Nama hari libur wajib diisi.",
            }, status_code=400)
        
        # Update holiday
        result = PortalJokiHolidayService.update(
            holiday_id=holiday_id,
            tanggal=tanggal_date,
            nama=nama.strip(),
            keterangan=keterangan.strip() if keterangan else None,
        )
        
        if result.success:
            log.info(f"Holiday updated: ID={holiday_id}")
            return JSONResponse({
                "success": True,
                "message": result.message,
                "data": result.data,
            })
        else:
            return JSONResponse({
                "success": False,
                "error": result.message,
            }, status_code=400)
        
    except Exception as e:
        log.error(f"Failed to update holiday: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# DELETE HOLIDAY (AJAX)
# ==========================================================
@router.post(
    "/delete",
    name="portal_joki_admin_holiday_delete",
)
async def holiday_delete(
    request: Request,
    holiday_id: int = Form(...),
):
    """
    Delete holiday.
    """
    log.info(f"Delete holiday: ID={holiday_id}")
    
    try:
        require_admin(request)
        
        result = PortalJokiHolidayService.delete(holiday_id)
        
        if result.success:
            log.info(f"Holiday deleted: ID={holiday_id}")
            return JSONResponse({
                "success": True,
                "message": result.message,
                "data": result.data,
            })
        else:
            return JSONResponse({
                "success": False,
                "error": result.message,
            }, status_code=400)
        
    except Exception as e:
        log.error(f"Failed to delete holiday: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# BULK DELETE HOLIDAYS (AJAX)
# ==========================================================
@router.post(
    "/bulk-delete",
    name="portal_joki_admin_holiday_bulk_delete",
)
async def holiday_bulk_delete(
    request: Request,
    holiday_ids: str = Form(...),  # Comma separated IDs
):
    """
    Bulk delete holidays.
    """
    log.info(f"Bulk delete holidays: {holiday_ids}")
    
    try:
        require_admin(request)
        
        # Parse IDs
        ids = [int(x.strip()) for x in holiday_ids.split(",") if x.strip()]
        
        if not ids:
            return JSONResponse({
                "success": False,
                "error": "Tidak ada ID yang dipilih.",
            }, status_code=400)
        
        result = PortalJokiHolidayService.delete_bulk(ids)
        
        if result.success:
            log.info(f"Holidays bulk deleted: {len(ids)} items")
            return JSONResponse({
                "success": True,
                "message": result.message,
                "data": result.data,
            })
        else:
            return JSONResponse({
                "success": False,
                "error": result.message,
                "errors": result.errors,
            }, status_code=400)
        
    except Exception as e:
        log.error(f"Failed to bulk delete holidays: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# HOLIDAY DETAIL (AJAX)
# ==========================================================
@router.get(
    "/detail",
    name="portal_joki_admin_holiday_detail",
)
async def holiday_detail(
    request: Request,
    holiday_id: int = Query(..., description="ID holiday"),
):
    """
    Get holiday detail as JSON.
    """
    log.info(f"Get holiday detail: ID={holiday_id}")
    
    try:
        require_admin(request)
        
        result = PortalJokiHolidayService.detail(holiday_id)
        
        if result.success:
            return JSONResponse({
                "success": True,
                "data": result.data,
            })
        else:
            return JSONResponse({
                "success": False,
                "error": result.message,
            }, status_code=404)
        
    except Exception as e:
        log.error(f"Failed to get holiday detail: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# UPCOMING HOLIDAYS (AJAX)
# ==========================================================
@router.get(
    "/upcoming",
    name="portal_joki_admin_holiday_upcoming",
)
async def holiday_upcoming(
    request: Request,
    days: int = Query(30, description="Jumlah hari ke depan"),
):
    """
    Get upcoming holidays as JSON.
    """
    log.info(f"Get upcoming holidays: days={days}")
    
    try:
        require_admin(request)
        
        result = PortalJokiHolidayService.upcoming(days)
        
        if result.success:
            return JSONResponse({
                "success": True,
                "data": result.data,
                "days": days,
            })
        else:
            return JSONResponse({
                "success": False,
                "error": result.message,
            }, status_code=400)
        
    except Exception as e:
        log.error(f"Failed to get upcoming holidays: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# YEARLY HOLIDAYS (AJAX)
# ==========================================================
@router.get(
    "/yearly",
    name="portal_joki_admin_holiday_yearly",
)
async def holiday_yearly(
    request: Request,
    year: int = Query(..., description="Tahun"),
):
    """
    Get yearly holidays as JSON.
    """
    log.info(f"Get yearly holidays: year={year}")
    
    try:
        require_admin(request)
        
        result = PortalJokiHolidayService.all(year=year)
        
        if result.success:
            data = []
            if result.data:
                if isinstance(result.data, dict):
                    data = result.data.get("data", [])
                elif isinstance(result.data, list):
                    data = result.data
            
            return JSONResponse({
                "success": True,
                "data": data,
                "year": year,
                "total": len(data),
            })
        else:
            return JSONResponse({
                "success": False,
                "error": result.message,
            }, status_code=400)
        
    except Exception as e:
        log.error(f"Failed to get yearly holidays: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# CHECK DATE (AJAX)
# ==========================================================
@router.get(
    "/check",
    name="portal_joki_admin_holiday_check",
)
async def holiday_check(
    request: Request,
    tanggal: str = Query(..., description="Tanggal (YYYY-MM-DD)"),
):
    """
    Check if date is holiday.
    """
    log.info(f"Check holiday: tanggal={tanggal}")
    
    try:
        require_admin(request)
        
        # Parse date
        try:
            tanggal_date = datetime.strptime(tanggal, "%Y-%m-%d").date()
        except ValueError:
            return JSONResponse({
                "success": False,
                "error": "Format tanggal tidak valid. Gunakan YYYY-MM-DD.",
            }, status_code=400)
        
        result = PortalJokiHolidayService.by_date(tanggal_date)
        
        return JSONResponse({
            "success": True,
            "is_holiday": result.success and result.data and result.data.get("is_holiday", False),
            "data": result.data if result.success else None,
        })
        
    except Exception as e:
        log.error(f"Failed to check holiday: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)