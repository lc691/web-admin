"""
Portal Joki - Admin Calendar Stats
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
    "/stats",
    name="portal_joki_admin_calendar_stats",
)
async def month_stats(
    request: Request,
    year: int = Query(..., description="Tahun"),
    month: int = Query(..., description="Bulan"),
):
    """
    Get calendar month statistics (AJAX).
    """
    log.info(
        f"Admin calendar stats: year={year}, month={month}"
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
                "stats": result.stats,
            }
        )

    except Exception as e:
        log.exception(
            "Failed to get admin calendar stats"
        )

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )