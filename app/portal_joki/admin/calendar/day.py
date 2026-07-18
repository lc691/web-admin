"""
Portal Joki - Admin Calendar Day
"""

from datetime import date

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.dependencies.auth import require_admin
from app.portal_joki.services.calendar.calendar_service import (
    PortalJokiCalendarService,
)
from app.utils.logger import log

router = APIRouter()


@router.get(
    "/day",
    name="portal_joki_admin_calendar_day",
)
async def day_detail(
    request: Request,
    date_str: str = Query(..., description="Tanggal (YYYY-MM-DD)"),
):
    """
    Get calendar day detail (AJAX).
    """
    log.info(
        f"Admin calendar day detail: date={date_str}"
    )

    try:
        require_admin(request)

        try:
            tanggal = date.fromisoformat(date_str)
        except ValueError:
            return JSONResponse(
                {
                    "success": False,
                    "error": "Format tanggal tidak valid. Gunakan YYYY-MM-DD.",
                },
                status_code=400,
            )

        result = PortalJokiCalendarService.day_admin(
            tanggal=tanggal,
        )

        return JSONResponse(
            {
                "success": True,
                "tanggal": result.tanggal.isoformat(),
                "data": result.data,
                "stats": result.stats,
            }
        )

    except Exception as e:
        log.exception(
            "Failed to get admin calendar day"
        )

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )