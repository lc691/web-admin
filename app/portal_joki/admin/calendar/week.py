"""
Portal Joki - Admin Calendar Week
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
    "/week",
    name="portal_joki_admin_calendar_week",
)
async def week_data(
    request: Request,
    date_str: str = Query(..., description="Tanggal referensi (YYYY-MM-DD)"),
):
    """
    Get calendar week data (AJAX).
    """
    log.info(
        f"Admin calendar week data: date={date_str}"
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

        result = PortalJokiCalendarService.week_admin(
            tanggal=tanggal,
        )

        return JSONResponse(
            {
                "success": True,
                "week": result,
            }
        )

    except Exception as e:
        log.exception(
            "Failed to get admin calendar week"
        )

        return JSONResponse(
            {
                "success": False,
                "error": str(e),
            },
            status_code=500,
        )