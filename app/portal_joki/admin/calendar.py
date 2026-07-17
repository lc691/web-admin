"""
Portal Joki - Admin Calendar Routes

Routes untuk halaman kalender admin portal joki.
"""

from datetime import date, datetime, timedelta
from calendar import monthrange
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse
from app.templates import templates

from app.dependencies.auth import require_admin
from app.portal_joki.services.calendar.calendar_service import (
    PortalJokiCalendarService,
)
from app.portal_joki.services.calendar.holiday_service import (
    PortalJokiHolidayService,
)
from app.utils.logger import log

# ==========================================================
# ROUTER & TEMPLATES
# ==========================================================
router = APIRouter(
    prefix="/admin/portal-joki/calendar",
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


def safe_get(data: Any, key: str, default=0):
    """Safe get from dict or return default."""
    if isinstance(data, dict):
        return data.get(key, default)
    return default


def build_calendar_data(
    year: int,
    month: int,
    calendar_data: List[Dict[str, Any]],
    holidays: List[Dict[str, Any]]
) -> List[List[Optional[Dict[str, Any]]]]:
    """
    Build calendar grid data.
    
    Args:
        year: Tahun
        month: Bulan
        calendar_data: Data dari service (list of dict)
        holidays: Data holiday (list of dict)
        
    Returns:
        list: Calendar grid dengan 6 minggu x 7 hari
    """
    # Get first day of month and total days
    first_day = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    
    # Get day of week for first day (0 = Monday, 6 = Sunday)
    # Python: 0 = Monday, 6 = Sunday
    # Kita mau: 0 = Sunday, 6 = Saturday
    start_weekday = first_day.weekday() + 1
    if start_weekday == 7:
        start_weekday = 0
    
    # Convert calendar data to dict by date
    calendar_dict = {}
    for day in calendar_data:
        # Handle both dict and other types
        if not isinstance(day, dict):
            continue
            
        tanggal = day.get("tanggal")
        if tanggal:
            # Convert to string date
            if hasattr(tanggal, "strftime"):
                date_str = tanggal.strftime("%Y-%m-%d")
            else:
                date_str = str(tanggal)
            calendar_dict[date_str] = day
    
    # Convert holidays to set
    holiday_set = set()
    for holiday in holidays:
        if not isinstance(holiday, dict):
            continue
            
        tanggal = holiday.get("tanggal")
        if tanggal:
            if hasattr(tanggal, "strftime"):
                date_str = tanggal.strftime("%Y-%m-%d")
            else:
                date_str = str(tanggal)
            holiday_set.add(date_str)
    
    # Build grid
    grid = []
    today = date.today()
    
    # First week: empty cells before first day
    week = []
    for _ in range(start_weekday):
        week.append(None)
    
    # Fill days
    for day_num in range(1, last_day + 1):
        current_date = date(year, month, day_num)
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Get tasks for this day
        day_data = calendar_dict.get(date_str, {})
        
        # Build day cell
        cell = {
            "day": day_num,
            "date": date_str,
            "is_today": current_date == today,
            "is_holiday": date_str in holiday_set,
            "total_tasks": safe_get(day_data, "total", 0),
            "pending": safe_get(day_data, "pending", 0),
            "upload": safe_get(day_data, "upload", 0),
            "revisi": safe_get(day_data, "revisi", 0),
            "selesai": safe_get(day_data, "selesai", 0),
            "tasks": [],  # We don't have task details in month view
        }
        
        week.append(cell)
        
        # Start new week
        if len(week) == 7:
            grid.append(week)
            week = []
    
    # Fill last week with empty cells
    if week:
        while len(week) < 7:
            week.append(None)
        grid.append(week)
    
    return grid


# ==========================================================
# CALENDAR PAGE
# ==========================================================
@router.get(
    "/",
    name="portal_joki_admin_calendar",
)
async def calendar_page(
    request: Request,
    year: Optional[int] = Query(None, description="Tahun"),
    month: Optional[int] = Query(None, description="Bulan"),
    today: bool = Query(False, description="Buka hari ini"),
):
    """
    Admin calendar page.
    """
    log.info(f"Admin calendar page: year={year}, month={month}, today={today}")
    
    try:
        admin = require_admin(request)
        
        # Get current date
        now = date.today()
        
        if today:
            year = now.year
            month = now.month
        else:
            if year is None:
                year = now.year
            if month is None:
                month = now.month
            
            # Validate month
            if month < 1 or month > 12:
                month = now.month
                year = now.year
        
        # Get calendar data
        result = PortalJokiCalendarService.month_admin(
            tahun=year,
            bulan=month,
        )
        
        # Get holidays
        holidays_result = PortalJokiHolidayService.month(
            tahun=year,
            bulan=month,
        )
        
        # Extract holidays data safely
        holidays_data = []
        if holidays_result.success and holidays_result.data:
            # Check if data is dict or list
            if isinstance(holidays_result.data, dict):
                holidays_data = holidays_result.data.get("data", [])
            elif isinstance(holidays_result.data, list):
                holidays_data = holidays_result.data
            else:
                holidays_data = []
        
        # Build calendar grid
        calendar_grid = build_calendar_data(
            year=year,
            month=month,
            calendar_data=result.calendar if result.calendar else [],
            holidays=holidays_data,
        )
        
        # Get month name
        month_name = get_month_name(month)
        
        return templates.TemplateResponse(
            "portal_joki/admin/calendar.html",
            {
                "request": request,
                "title": "Kalender Portal Joki",
                "admin": admin,
                "year": year,
                "month": month,
                "month_name": month_name,
                "calendar_data": calendar_grid,
                "holidays": holidays_data,
                "generated_at": datetime.now(),
            },
        )
        
    except Exception as e:
        log.error(f"Failed to load calendar page: {e}")
        import traceback
        traceback.print_exc()
        
        return templates.TemplateResponse(
            "portal_joki/admin/calendar.html",
            {
                "request": request,
                "title": "Kalender Portal Joki",
                "error": str(e),
                "year": date.today().year,
                "month": date.today().month,
                "month_name": get_month_name(date.today().month),
                "calendar_data": [],
                "holidays": [],
                "generated_at": datetime.now(),
            },
        )


# ==========================================================
# DAY DETAIL (AJAX)
# ==========================================================
@router.get(
    "/day",
    name="portal_joki_admin_calendar_day",
)
async def day_detail(
    request: Request,
    date_str: str = Query(..., description="Tanggal (YYYY-MM-DD)"),
):
    """
    Get day detail as JSON (for AJAX).
    """
    log.info(f"Admin calendar day detail: date={date_str}")
    
    try:
        require_admin(request)
        
        # Parse date
        try:
            tanggal = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return JSONResponse({
                "success": False,
                "error": "Format tanggal tidak valid. Gunakan YYYY-MM-DD.",
            }, status_code=400)
        
        # Get day data from admin view
        result = PortalJokiCalendarService.day_admin(
            tanggal=tanggal,
        )
        
        return JSONResponse({
            "success": True,
            "data": result.data if result.data else [],
            "tanggal": date_str,
            "total": len(result.data) if result.data else 0,
        })
        
    except Exception as e:
        log.error(f"Failed to get day detail: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# CALENDAR DATA (AJAX)
# ==========================================================
@router.get(
    "/data",
    name="portal_joki_admin_calendar_data",
)
async def calendar_data(
    request: Request,
    year: int = Query(..., description="Tahun"),
    month: int = Query(..., description="Bulan"),
):
    """
    Get calendar data as JSON (for AJAX).
    """
    log.info(f"Admin calendar data: year={year}, month={month}")
    
    try:
        require_admin(request)
        
        # Get calendar data
        result = PortalJokiCalendarService.month_admin(
            tahun=year,
            bulan=month,
        )
        
        # Get holidays
        holidays_result = PortalJokiHolidayService.month(
            tahun=year,
            bulan=month,
        )
        
        # Extract holidays data safely
        holidays_data = []
        if holidays_result.success and holidays_result.data:
            if isinstance(holidays_result.data, dict):
                holidays_data = holidays_result.data.get("data", [])
            elif isinstance(holidays_result.data, list):
                holidays_data = holidays_result.data
            else:
                holidays_data = []
        
        # Build calendar grid
        calendar_grid = build_calendar_data(
            year=year,
            month=month,
            calendar_data=result.calendar if result.calendar else [],
            holidays=holidays_data,
        )
        
        return JSONResponse({
            "success": True,
            "year": year,
            "month": month,
            "month_name": get_month_name(month),
            "calendar": calendar_grid,
            "holidays": holidays_data,
            "stats": result.stats if result.stats else {},
        })
        
    except Exception as e:
        log.error(f"Failed to get calendar data: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# MONTH STATS (AJAX)
# ==========================================================
@router.get(
    "/stats",
    name="portal_joki_admin_calendar_stats",
)
async def month_stats(
    request: Request,
    year: int = Query(..., description="Tahun"),
    month: int = Query(..., description="Bulan"),
):
    """
    Get month statistics as JSON.
    """
    log.info(f"Admin calendar stats: year={year}, month={month}")
    
    try:
        require_admin(request)
        
        stats = PortalJokiCalendarService.get_stats(
            tahun=year,
            bulan=month,
        )
        
        return JSONResponse({
            "success": True,
            "year": year,
            "month": month,
            "stats": stats or {},
        })
        
    except Exception as e:
        log.error(f"Failed to get calendar stats: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# HOLIDAY LIST (AJAX)
# ==========================================================
@router.get(
    "/holidays",
    name="portal_joki_admin_calendar_holidays",
)
async def holiday_list(
    request: Request,
    year: int = Query(..., description="Tahun"),
    month: int = Query(..., description="Bulan"),
):
    """
    Get holidays as JSON.
    """
    log.info(f"Admin calendar holidays: year={year}, month={month}")
    
    try:
        require_admin(request)
        
        result = PortalJokiHolidayService.month(
            tahun=year,
            bulan=month,
        )
        
        # Extract data safely
        data = []
        if result.success and result.data:
            if isinstance(result.data, dict):
                data = result.data.get("data", [])
            elif isinstance(result.data, list):
                data = result.data
            else:
                data = []
        
        return JSONResponse({
            "success": result.success,
            "data": data,
            "year": year,
            "month": month,
            "total": len(data),
        })
        
    except Exception as e:
        log.error(f"Failed to get holidays: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)


# ==========================================================
# WEEK DATA (AJAX)
# ==========================================================
@router.get(
    "/week",
    name="portal_joki_admin_calendar_week",
)
async def week_data(
    request: Request,
    date_str: str = Query(..., description="Tanggal referensi (YYYY-MM-DD)"),
):
    """
    Get week data as JSON.
    """
    log.info(f"Admin calendar week data: date={date_str}")
    
    try:
        require_admin(request)
        
        # Parse date
        try:
            tanggal = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return JSONResponse({
                "success": False,
                "error": "Format tanggal tidak valid. Gunakan YYYY-MM-DD.",
            }, status_code=400)
        
        # Get week data
        result = PortalJokiCalendarService.week_admin(
            tanggal=tanggal,
        )
        
        return JSONResponse({
            "success": True,
            "data": result or {},
        })
        
    except Exception as e:
        log.error(f"Failed to get week data: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
        }, status_code=500)