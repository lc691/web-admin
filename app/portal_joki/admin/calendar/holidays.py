"""
Portal Joki - Admin Calendar Holidays
"""

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.dependencies.auth import require_admin
from app.portal_joki.services.calendar.holiday_service import (
    PortalJokiHolidayService,
)
from app.utils.logger import log

router = APIRouter()


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
    Get holidays (AJAX).
    """
    log.info(
        f"Admin calendar holidays: year={year}, month={month}"
    )

    try:
        require_admin(request)

        result = PortalJokiHolidayService.month(
            tahun=year,
            bulan=month,
        )

        holidays = result.data if result.data else []

        return JSONResponse(
            {
                "success": result.success,
                "year": year,
                "month": month,
                "data": holidays,
                "total": len(holidays),
            }
        )

    except Exception as e:
        log.exception(
            "Failed to get admin calendar holidays"
        )

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )