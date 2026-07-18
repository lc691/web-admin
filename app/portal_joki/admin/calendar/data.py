"""
Portal Joki - Admin Calendar Data
"""

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.dependencies.auth import require_admin
from app.portal_joki.services.calendar.calendar_service import (
    PortalJokiCalendarService,
)
from app.utils.logger import log

router = APIRouter()


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
    Get calendar data (AJAX).
    """
    log.info(
        f"Admin calendar data: year={year}, month={month}"
    )

    try:
        require_admin(request)

        result = PortalJokiCalendarService.month_admin(
            tahun=year,
            bulan=month,
        )

        return JSONResponse(
            {
                "success": True,
                "year": result.tahun,
                "month": result.bulan,
                "month_name": result.month_name,
                "calendar": result.calendar,
                "holidays": result.holidays,
                "stats": result.stats,
            }
        )

    except Exception as e:
        log.exception(
            "Failed to get admin calendar data"
        )

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )